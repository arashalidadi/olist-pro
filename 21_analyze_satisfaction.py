import os
import sys
import re

import arabic_reshaper
import matplotlib.pyplot as plt
import pandas as pd
from bidi.algorithm import get_display

sys.stdout.reconfigure(encoding='utf-8')

plt.rcParams['font.family'] = ['DejaVu Sans', 'Tahoma']


def fa(text):
    text = str(text)

    # تقسیم متن به بخش‌های فارسی و غیرفارسی
    parts = re.split(r'([\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+)', text)

    result = []

    for part in parts:
        if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', part):
            reshaped = arabic_reshaper.reshape(part)
            result.append(get_display(reshaped)[::-1])
        else:
            result.append(part)

    return ''.join(result)


os.makedirs('charts', exist_ok=True)

reviews = pd.read_csv('data/raw/olist_order_reviews_dataset.csv')
orders = pd.read_csv('data/raw/olist_orders_dataset.csv')
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
items = pd.read_csv('data/raw/olist_order_items_dataset.csv')
products = pd.read_csv('data/raw/olist_products_dataset.csv')
translation = pd.read_csv('data/raw/product_category_name_translation.csv')

# same cleaning logic as stage 2: keep latest review per order
reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'])
reviews = (
    reviews.sort_values('review_creation_date')
    .drop_duplicates(subset='order_id', keep='last')
)
print('نظرات پس از نگه‌داشتن آخرین نظر هر سفارش:', f'{len(reviews):,}')

products['product_category_name'] = products['product_category_name'].fillna('unknown')
products = products.merge(translation, on='product_category_name', how='left')
items = items.merge(products[['product_id', 'product_category_name_english']], on='product_id', how='left')

print()
print('=' * 70)
print('۱۰-۱. توزیع امتیازها')
print('=' * 70)
score_cnt = reviews['review_score'].value_counts().sort_index()
n_rev = len(reviews)
dist = pd.DataFrame({'تعداد نظر': score_cnt, 'درصد': (score_cnt / n_rev * 100).round(2)})
print(dist.to_string())
print()
mean_score = reviews['review_score'].mean().round(2)
pct_good = (reviews['review_score'] >= 4).mean() * 100
pct_bad = (reviews['review_score'] <= 2).mean() * 100
print('میانگین امتیاز:', mean_score)
print(f'درصد امتیاز ۴ یا ۵: {pct_good:.1f}٪')
print(f'درصد امتیاز ۱ یا ۲: {pct_bad:.1f}٪')

fig, ax = plt.subplots(figsize=(9, 5))
colors = ['#d62728', '#e8a838', '#bdbdbd', '#8fce8f', '#2ca02c']
bars = ax.bar(score_cnt.index, score_cnt.values, color=colors)
ax.bar_label(bars, labels=[f'{p}%' for p in (score_cnt / n_rev * 100).round(1).values], fontsize=10)
ax.set_title(fa('توزیع امتیازهای مشتریان'), fontsize=13)
ax.set_xlabel(fa('امتیاز'))
ax.set_ylabel(fa('تعداد نظر'))
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/10_1_score_distribution.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('۱۰-۲. رضایت به تفکیک دسته‌بندی محصول')
print('=' * 70)
rv = reviews.merge(items[['order_id', 'price', 'product_category_name_english']], on='order_id', how='inner')
by_cat = rv.groupby('product_category_name_english').agg(
    reviews=('review_score', 'size'),
    mean_score=('review_score', 'mean'),
)
by_cat = by_cat[by_cat['reviews'] >= 30]
print('دسته‌های با حداقل ۳۰ نظر:', len(by_cat))
print()
print('۱۰ دسته با بالاترین میانگین امتیاز:')
top10 = by_cat.sort_values('mean_score', ascending=False).head(10)
print(top10.round(2).to_string())
print()
print('۱۰ دسته با پایین‌ترین میانگین امتیاز:')
bottom10 = by_cat.sort_values('mean_score').head(10)
print(bottom10.round(2).to_string())

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
b = axes[0].barh(top10.index[::-1], top10['mean_score'][::-1], color='#2ca02c')
axes[0].bar_label(b, labels=[f'{v:.2f}' for v in top10['mean_score'][::-1]], fontsize=8)
axes[0].set_title(fa('۱۰ دسته با بالاترین امتیاز'), fontsize=12)
axes[0].set_xlim(1, 5)
axes[0].grid(axis='x', alpha=0.3)
plt.setp(axes[0].get_yticklabels(), fontsize=8)
b = axes[1].barh(bottom10.index[::-1], bottom10['mean_score'][::-1], color='#d62728')
axes[1].bar_label(b, labels=[f'{v:.2f}' for v in bottom10['mean_score'][::-1]], fontsize=8)
axes[1].set_title(fa('۱۰ دسته با پایین‌ترین امتیاز'), fontsize=12)
axes[1].set_xlim(1, 5)
axes[1].grid(axis='x', alpha=0.3)
plt.setp(axes[1].get_yticklabels(), fontsize=8)
fig.tight_layout()
fig.savefig('charts/10_2_category_scores.png', dpi=150)
plt.close(fig)

small_in_top = top10[top10['reviews'] < 100]
small_in_bottom = bottom10[bottom10['reviews'] < 100]
print()
print('دسته‌های کم‌نظر (زیر ۱۰۰) در برترین‌ها:', ', '.join(small_in_top.index) or '—')
print('دسته‌های کم‌نظر (زیر ۱۰۰) در ضعیف‌ترین‌ها:', ', '.join(small_in_bottom.index) or '—')

print()
print('=' * 70)
print('۱۰-۳. تغییرات رضایت در طول زمان')
print('=' * 70)
rv_time = reviews.merge(orders[['order_id', 'order_purchase_timestamp']], on='order_id', how='left')
monthly_score = rv_time.assign(
    month=rv_time['order_purchase_timestamp'].dt.to_period('M'),
).groupby('month')['review_score'].agg(['mean', 'size'])
print(monthly_score.round(2).to_string())

fig, ax = plt.subplots(figsize=(12, 5))
x = [str(m) for m in monthly_score.index]
ax.plot(x, monthly_score['mean'], color='#4c72b0', marker='o')
ax.axhline(mean_score, color='gray', ls='--', lw=1, label=f'overall = {mean_score}')
ax.set_title(fa('روند ماهانه میانگین امتیاز مشتریان'), fontsize=13)
ax.set_ylabel(fa('میانگین امتیاز'))
ax.set_ylim(3.5, 4.6)
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('charts/10_3_score_trend.png', dpi=150)
plt.close(fig)

print()
print('مقایسه فروش و امتیاز دسته‌بندی‌ها (حداقل ۳۰ نظر):')
revenue = (
    items[items['order_id'].isin(orders[orders['order_status'] == 'delivered']['order_id'])]
    .groupby('product_category_name_english')['price'].sum()
)
cat_mix = by_cat.assign(revenue=revenue)
cat_mix = cat_mix.dropna()
cat_mix['revenue_m'] = (cat_mix['revenue'] / 1e6).round(2)
overall_mean = reviews['review_score'].mean()
weak = cat_mix[(cat_mix['revenue'] > cat_mix['revenue'].median())
               & (cat_mix['mean_score'] < overall_mean)].sort_values('revenue', ascending=False)
print('دسته‌های پرفروش با امتیاز زیر میانگین کل:')
print(weak[['reviews', 'mean_score', 'revenue_m']].round(2).head(10).to_string())

fig, ax = plt.subplots(figsize=(11, 6))
ax.scatter(cat_mix['revenue_m'], cat_mix['mean_score'], s=30, alpha=0.6, color='#4c72b0')
ax.axhline(overall_mean, color='gray', ls='--', lw=1, label=f'overall = {overall_mean}')
ax.axvline(cat_mix['revenue'].median() / 1e6, color='gray', ls=':', lw=1)
for _, row in weak.head(6).iterrows():
    ax.annotate(row.name, (row['revenue_m'], row['mean_score']), fontsize=7)
ax.set_title(fa('فروش در برابر امتیاز رضایت (دسته‌بندی‌ها)'), fontsize=13)
ax.set_xlabel(fa('مبلغ فروش (میلیون BRL)'))
ax.set_ylabel(fa('میانگین امتیاز'))
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('charts/10_4_revenue_vs_score.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('جمع‌بندی کسب‌وکاری')
print('=' * 70)
print('میانگین کل:', mean_score, '| خوب (۴-۵):', f'{pct_good:.1f}٪', '| بد (۱-۲):', f'{pct_bad:.1f}٪')
print('ضعیف‌های پرفروش:', ', '.join(weak.head(6).index.tolist()))
