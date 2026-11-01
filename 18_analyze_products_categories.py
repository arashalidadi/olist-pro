import os
import sys

import arabic_reshaper
import matplotlib.pyplot as plt
import pandas as pd
from bidi.algorithm import get_display

#sys.stdout.reconfigure(encoding='utf-8')

plt.rcParams['font.family'] = ['DejaVu Sans', 'Tahoma']


def fa(text):
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)[::-1]


os.makedirs('charts', exist_ok=True)

products = pd.read_csv('data/raw/olist_products_dataset.csv')
translation = pd.read_csv('data/raw/product_category_name_translation.csv')
items = pd.read_csv('data/raw/olist_order_items_dataset.csv')

products['product_category_name'] = products['product_category_name'].fillna('unknown')
dim_cols = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
for col in dim_cols:
    products.loc[products[col].isna() | (products[col] == 0), col] = products[col].median()

products = products.merge(translation, on='product_category_name', how='left')
extra = {
    'pc_gamer': 'pc_gaming',
    'portateis_cozinha_e_preparadores_de_alimentos': 'portable_kitchen_and_food_preparators',
}
mask = products['product_category_name_english'].isna() & products['product_category_name'].isin(extra)
products.loc[mask, 'product_category_name_english'] = products.loc[mask, 'product_category_name'].map(extra)
translated = set(products['product_category_name_english'].dropna()) == set(products['product_category_name'])
print('آیا همه دسته‌ها ترجمه دارند؟', translated, '(دسته‌ی unknown برچسب خود ماست و در جدول ترجمه نیست)')

items = items.merge(products[['product_id', 'product_category_name_english', 'product_weight_g',
                              'product_length_cm', 'product_height_cm', 'product_width_cm']],
                    on='product_id', how='left')
items['product_volume_cm3'] = (
    items['product_length_cm'] * items['product_height_cm'] * items['product_width_cm']
)

print()
print('=' * 70)
print('۷-۱. توزیع محصولات در دسته‌بندی‌ها (بر اساس آیتم‌های فروخته‌شده)')
print('=' * 70)
cat_sales = items.groupby('product_category_name_english').size().sort_values(ascending=False)
top10 = cat_sales.head(10)
bottom10 = cat_sales.sort_values().head(10)
share = (cat_sales / cat_sales.sum() * 100).round(2)
print('تعداد دسته‌بندی‌های فعال در فروش:', len(cat_sales))
print()
print('ده دسته پرتقاضا:')
print(pd.DataFrame({'تعداد آیتم': top10, 'درصد': share.head(10)}).to_string())
print()
print('ده دسته کم‌تقاضا:')
print(pd.DataFrame({'تعداد آیتم': bottom10}).to_string())
print()
print('سهم ۱۰ دسته اول از کل فروش:', round(share.head(10).sum(), 2), '%')

fig, ax = plt.subplots(figsize=(11, 5))
bars = ax.bar(top10.index, top10.values, color='#4c72b0')
ax.bar_label(bars, labels=[f'{p}%' for p in share.head(10).values], fontsize=9)
ax.set_title(fa('ده دسته‌بندی پرتقاضا بر اساس تعداد آیتم فروخته‌شده'), fontsize=13)
ax.set_ylabel(fa('تعداد آیتم'))
plt.setp(ax.get_xticklabels(), rotation=35, ha='right', fontsize=9)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/07_1_top_categories.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('۷-۲. تحلیل فیزیکی محصولات')
print('=' * 70)
phys = items.groupby('product_category_name_english').agg(
    items=('order_item_id', 'size'),
    mean_weight_g=('product_weight_g', 'mean'),
    mean_volume_cm3=('product_volume_cm3', 'mean'),
).sort_values('items', ascending=False)
print('میانگین وزن و حجم کل آیتم‌ها:')
print(items[['product_weight_g', 'product_volume_cm3']].describe().round(1).to_string())
print()
print('۵ دسته سنگین (میانگین وزن):')
print(phys.sort_values('mean_weight_g', ascending=False).head(5)
      [['items', 'mean_weight_g', 'mean_volume_cm3']].round(0).to_string())
print()
print('۵ دسته حجیم (میانگین حجم):')
print(phys.sort_values('mean_volume_cm3', ascending=False).head(5)
      [['items', 'mean_weight_g', 'mean_volume_cm3']].round(0).to_string())
print()
print('۵ دسته سبک‌ترین:')
print(phys.sort_values('mean_weight_g').head(5)
      [['items', 'mean_weight_g', 'mean_volume_cm3']].round(0).to_string())

fig, ax = plt.subplots(figsize=(11, 5))
heavy = phys.sort_values('mean_volume_cm3', ascending=False).head(10)
bars = ax.bar(heavy.index, heavy['mean_volume_cm3'], color='#dd8452')
ax.bar_label(bars, labels=[f'{int(v):,}' for v in heavy['mean_volume_cm3']], fontsize=8)
ax.set_title(fa('ده دسته حجیم‌تر بر اساس میانگین حجم محصول'), fontsize=13)
ax.set_ylabel(fa('میانگین حجم (سانتی‌متر مکعب)'))
plt.setp(ax.get_xticklabels(), rotation=35, ha='right', fontsize=9)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/07_2_heaviest_categories.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('۷-۳. ترکیب دسته‌بندی و ایالت فروشنده')
print('=' * 70)
sellers = pd.read_csv('data/raw/olist_sellers_dataset.csv')
orders = pd.read_csv('data/raw/olist_orders_dataset.csv')
full = items.merge(sellers[['seller_id', 'seller_state']], on='seller_id', how='left')
full = full[full['order_id'].isin(orders[orders['order_status'] == 'delivered']['order_id'])]

top8_cats = cat_sales.head(8).index
sub = full[full['product_category_name_english'].isin(top8_cats)]
pivot = pd.crosstab(sub['product_category_name_english'], sub['seller_state'], normalize='index') * 100
top_states = pivot.sum().sort_values(ascending=False).head(6).index
pivot = pivot[top_states].round(1)
print(pivot.to_string())

print()
print('سهم SP (سائوپائولو) در هر دسته:')
print(pivot['SP'].sort_values(ascending=False).to_string())

fig, ax = plt.subplots(figsize=(11, 5))
pivot.plot(kind='bar', stacked=True, ax=ax, colormap='tab20')
ax.set_title(fa('سهم ایالت‌های فروشنده در ۸ دسته پرتقاضا'), fontsize=13)
ax.set_ylabel(fa('درصد'))
plt.setp(ax.get_xticklabels(), rotation=35, ha='right', fontsize=9)
ax.legend(title='', fontsize=8, ncols=3)
fig.tight_layout()
fig.savefig('charts/07_3_category_state_mix.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('جمع‌بندی کسب‌وکاری')
print('=' * 70)
print('هسته‌ی فروش: ۱۰ دسته اول', round(share.head(10).sum(), 2), '٪ کل آیتم‌ها')
print('دسته‌های سنگین/حجیم بار لجستیک بالاتری دارند و در تحلیل ارسال بررسی می‌شوند')
