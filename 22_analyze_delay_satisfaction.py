import os
import sys

import arabic_reshaper
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bidi.algorithm import get_display

sys.stdout.reconfigure(encoding='utf-8')

plt.rcParams['font.family'] = ['DejaVu Sans', 'Tahoma']


def fa(text):
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)[::-1]


os.makedirs('charts', exist_ok=True)

orders = pd.read_csv('data/raw/olist_orders_dataset.csv')
reviews = pd.read_csv('data/raw/olist_order_reviews_dataset.csv')
items = pd.read_csv('data/raw/olist_order_items_dataset.csv')
products = pd.read_csv('data/raw/olist_products_dataset.csv')
translation = pd.read_csv('data/raw/product_category_name_translation.csv')

# same cleaning logic as stage 2
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])
orders['delay_days'] = (
    orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']
).dt.days

reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'])
reviews = (
    reviews.sort_values('review_creation_date')
    .drop_duplicates(subset='order_id', keep='last')
)

products['product_category_name'] = products['product_category_name'].fillna('unknown')
products = products.merge(translation, on='product_category_name', how='left')
items = items.merge(products[['product_id', 'product_category_name_english']], on='product_id', how='left')

# delivered orders with valid dates joined with latest review
delivered = orders[
    (orders['order_status'] == 'delivered')
    & orders['order_delivered_customer_date'].notna()
    & orders['order_estimated_delivery_date'].notna()
][['order_id', 'delay_days', 'order_purchase_timestamp']].copy()

df = delivered.merge(reviews[['order_id', 'review_score']], on='order_id', how='inner')
df = df.dropna(subset=['review_score'])
print('سفارش‌های تحویل‌شده با نظر:', f'{len(df):,}')

print()
print('=' * 70)
print('۱۱-۱. مقایسه سفارش‌های به‌موقع و دیرکرددار')
print('=' * 70)
df['group'] = np.where(df['delay_days'] > 0, 'late', 'on_time')
grp = df.groupby('group')['review_score'].agg(['mean', 'size'])
grp.index = [fa('دیرکرددار') if g == 'late' else fa('به موقع (شامل زودتر)') for g in grp.index]
print(grp.round(2).to_string())
print()
on_time = df.loc[df['group'] == 'on_time', 'review_score']
late = df.loc[df['group'] == 'late', 'review_score']
print(f'میانگین به‌موقع: {on_time.mean():.2f} ({len(on_time):,} سفارش)')
print(f'میانگین دیرکرددار: {late.mean():.2f} ({len(late):,} سفارش)')
print(f'اختلاف: {on_time.mean() - late.mean():.2f} امتیاز')

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(grp.index, grp['mean'], color=['#2ca02c', '#d62728'], width=0.5)
ax.bar_label(bars, labels=[f'{v:.2f}' for v in grp['mean']], fontsize=12)
for i, cnt in enumerate(grp['size']):
    ax.text(i, 0.15, f'n = {cnt:,}', ha='center', color='white', fontsize=10)
ax.set_title(fa('میانگین امتیاز: سفارش‌های به‌موقع در برابر دیرکرددار'), fontsize=13)
ax.set_ylabel(fa('میانگین امتیاز'))
ax.set_ylim(0, 5)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/11_1_ontime_vs_late.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('۱۱-۲. بررسی شدت تأخیر')
print('=' * 70)
bins = [0, 3, 7, np.inf]
labels = ['۱ تا ۳ روز', '۴ تا ۷ روز', 'بیش از ۷ روز']
late_df = df[df['group'] == 'late'].copy()
late_df['severity'] = pd.cut(late_df['delay_days'], bins=bins, labels=labels)
sev = late_df.groupby('severity', observed=True)['review_score'].agg(['mean', 'size'])
print(sev.round(2).to_string())

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar([str(i) for i in sev.index], sev['mean'], color=['#e8a838', '#e05c3a', '#d62728'])
ax.bar_label(bars, labels=[f'{v:.2f}' for v in sev['mean']], fontsize=11)
for i, cnt in enumerate(sev['size']):
    ax.text(i, 0.15, f'n = {cnt:,}', ha='center', color='white', fontsize=10)
ax.set_title(fa('میانگین امتیاز به تفکیک شدت تأخیر'), fontsize=13)
ax.set_ylabel(fa('میانگین امتیاز'))
ax.set_ylim(0, 5)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/11_2_severity.png', dpi=150)
plt.close(fig)

print()
print('توجه: گروه به‌موقع (شامل زودتر از موعد) =', f"{on_time.mean():.2f}", 'برای مقایسه')

print()
print('=' * 70)
print('۱۱-۳. بررسی تفاوت میان دسته‌بندی‌ها')
print('=' * 70)
cat_orders = (
    items[items['order_id'].isin(df['order_id'])]
    .dropna(subset=['product_category_name_english'])
    .groupby('order_id')['product_category_name_english']
    .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else None)
)
df_cat = df.merge(cat_orders.rename('category'), on='order_id', how='left')

big_cats = df_cat.groupby('category')['order_id'].size()
big_cats = big_cats[big_cats >= 1000].index
print('دسته‌های با حداقل ۱۰۰۰ سفارش:', len(big_cats))
print()
rows = []
for cat in big_cats:
    sub = df_cat[df_cat['category'] == cat]
    o = sub.loc[sub['group'] == 'on_time', 'review_score']
    l = sub.loc[sub['group'] == 'late', 'review_score']
    rows.append({
        'category': cat,
        'orders': len(sub),
        'on_time_mean': round(o.mean(), 2),
        'late_mean': round(l.mean(), 2) if len(l) > 0 else np.nan,
        'late_n': len(l),
        'gap': round(o.mean() - l.mean(), 2) if len(l) > 0 else np.nan,
        'late_pct': round(len(l) / len(sub) * 100, 1),
    })
cat_table = pd.DataFrame(rows).sort_values('gap', ascending=False)
print(cat_table.to_string(index=False))

fig, ax = plt.subplots(figsize=(11, 6))
y = np.arange(len(cat_table))
ax.barh(y + 0.2, cat_table['on_time_mean'], height=0.4, color='#2ca02c', label=fa('به موقع'))
ax.barh(y - 0.2, cat_table['late_mean'], height=0.4, color='#d62728', label=fa('دیرکرددار'))
ax.set_yticks(y)
ax.set_yticklabels(cat_table['category'], fontsize=8)
ax.set_xlim(1, 5)
ax.set_title(fa('امتیاز به‌موقع در برابر دیرکرد در دسته‌های بزرگ'), fontsize=13)
ax.set_xlabel(fa('میانگین امتیاز'))
ax.legend()
ax.grid(axis='x', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/11_3_category_gap.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('جمع‌بندی تحلیلی')
print('=' * 70)
print(f'اختلاف کل: {on_time.mean() - late.mean():.2f} امتیاز | n به‌موقع = {len(on_time):,} | n دیرکرد = {len(late):,}')
print('بیشترین شکاف:', cat_table.iloc[0]['category'], '| کمترین شکاف:', cat_table.iloc[-1]['category'])
