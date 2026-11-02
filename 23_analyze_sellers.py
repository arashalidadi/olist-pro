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

sellers = pd.read_csv('data/raw/olist_sellers_dataset.csv')
items = pd.read_csv('data/raw/olist_order_items_dataset.csv')
orders = pd.read_csv('data/raw/olist_orders_dataset.csv')
reviews = pd.read_csv('data/raw/olist_order_reviews_dataset.csv')

reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'])
reviews = (
    reviews.sort_values('review_creation_date')
    .drop_duplicates(subset='order_id', keep='last')
)

# delivered orders only for revenue analysis
delivered_ids = orders[orders['order_status'] == 'delivered']['order_id']
ditems = items[items['order_id'].isin(delivered_ids)]

print('=' * 70)
print('۱۲-۱. تعداد و پراکندگی فروشندگان')
print('=' * 70)
n_sellers = sellers['seller_id'].nunique()
print('تعداد فروشندگان یکتا:', f'{n_sellers:,}')
state_sellers = sellers.groupby('seller_state')['seller_id'].nunique().sort_values(ascending=False)
top10_states = state_sellers.head(10)
state_pct = (state_sellers / n_sellers * 100).round(2)
print()
print('۱۰ ایالت با بیشترین فروشنده:')
print(pd.DataFrame({'فروشندگان': top10_states, 'درصد': state_pct.head(10)}).to_string())
print()
print('سهم SP از کل فروشندگان:', state_pct.get('SP'), '٪')

fig, ax = plt.subplots(figsize=(11, 5))
bars = ax.bar(top10_states.index, top10_states.values, color='#4c72b0')
ax.bar_label(bars, labels=[f'{p}%' for p in state_pct.head(10).values], fontsize=9)
ax.set_title(fa('۱۰ ایالت با بیشترین تعداد فروشنده'), fontsize=13)
ax.set_ylabel(fa('تعداد فروشنده'))
plt.setp(ax.get_xticklabels(), rotation=35, ha='right', fontsize=9)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/12_1_seller_states.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('۱۲-۲. تحلیل فروش فروشندگان')
print('=' * 70)
per_seller = ditems.groupby('seller_id').agg(
    items_sold=('order_item_id', 'size'),
    revenue=('price', 'sum'),
)
print('فروشندگان فعال در سفارش‌های تحویل‌شده:', f'{len(per_seller):,}')
print()
print('آمار مبلغ فروش هر فروشنده:')
print(per_seller['revenue'].describe()[['mean', '50%', 'max']].round(0).to_string())
print()
top10_rev = per_seller.sort_values('revenue', ascending=False).head(10)
print('۱۰ فروشنده برتر بر اساس مبلغ فروش:')
print(top10_rev.round(0).to_string())

total_revenue = per_seller['revenue'].sum()
top_share = top10_rev['revenue'].sum() / total_revenue * 100
print()
print(f'سهم ۱۰ فروشنده برتر از کل فروش: {top_share:.1f}٪')

fig, ax = plt.subplots(figsize=(11, 5))
bars = ax.bar(range(len(top10_rev)), top10_rev['revenue'] / 1e3, color='#4c72b0')
ax.bar_label(bars, labels=[f'{v/1e3:.0f}K' for v in top10_rev['revenue']], fontsize=8)
ax.set_xticks(range(len(top10_rev)))
ax.set_xticklabels(top10_rev.index, rotation=35, ha='right', fontsize=8)
ax.set_title(fa('۱۰ فروشنده برتر بر اساس مبلغ فروش'), fontsize=13)
ax.set_ylabel(fa('مبلغ فروش (هزار BRL)'))
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/12_2_top_sellers.png', dpi=150)
plt.close(fig)

# rank comparison: items vs revenue
per_seller['rank_revenue'] = per_seller['revenue'].rank(ascending=False)
per_seller['rank_items'] = per_seller['items_sold'].rank(ascending=False)
top10_items = per_seller.sort_values('items_sold', ascending=False).head(10)
overlap = set(top10_rev.index) & set(top10_items.index)
print()
print('تعداد مشترک در دو رتبه‌بندی (مبلغ vs تعداد اقلام):', len(overlap), 'از ۱۰')
print('رتبه بر اساس مبلغ برای ۱۰ پرفروشِ تعدادی:')
print(per_seller.loc[top10_items.index, ['items_sold', 'rank_revenue']].to_string())

print()
print('=' * 70)
print('۱۲-۳. فروش و رضایت مشتریان')
print('=' * 70)
rv_seller = items.merge(reviews[['order_id', 'review_score']], on='order_id', how='inner')
seller_reviews = rv_seller.groupby('seller_id').agg(
    n_reviews=('review_score', 'size'),
    mean_score=('review_score', 'mean'),
)
seller_stats = per_seller.join(seller_reviews, how='left')
qualified = seller_stats[seller_stats['n_reviews'] >= 50].copy()
print('فروشندگان با حداقل ۵۰ نظر:', f'{len(qualified):,}')
print()
overall_mean = reviews['review_score'].mean()
print('میانگین امتیاز کل:', round(overall_mean, 2))

risk = qualified[(qualified['revenue'] > qualified['revenue'].median())
                 & (qualified['mean_score'] < overall_mean)].sort_values('revenue', ascending=False)
print()
print('فروشندگان پرفروش (بالای میانه فروش) با امتیاز زیر میانگین کل:')
print(risk[['items_sold', 'revenue', 'n_reviews', 'mean_score']].head(10).round(2).to_string())

fig, ax = plt.subplots(figsize=(11, 6))
ax.scatter(qualified['revenue'] / 1e3, qualified['mean_score'], s=25, alpha=0.6, color='#4c72b0')
ax.axhline(overall_mean, color='gray', ls='--', lw=1, label=f'overall = {overall_mean}')
for _, row in risk.head(6).iterrows():
    ax.annotate(row.name[:12], (row['revenue'] / 1e3, row['mean_score']), fontsize=7)
ax.set_title(fa('فروش در برابر امتیاز رضایت فروشندگان (حداقل ۵۰ نظر)'), fontsize=13)
ax.set_xlabel(fa('مبلغ فروش (هزار BRL)'))
ax.set_ylabel(fa('میانگین امتیاز'))
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('charts/12_3_seller_revenue_score.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('جمع‌بندی کسب‌وکاری')
print('=' * 70)
print(f'فروش به ۱۰ فروشنده برتر: {top_share:.1f}٪ | فروشندگان پرمخاطره: {len(risk)}')
