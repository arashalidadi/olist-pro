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

items = pd.read_csv('data/raw/olist_order_items_dataset.csv')
orders = pd.read_csv('data/raw/olist_orders_dataset.csv')
reviews = pd.read_csv('data/raw/olist_order_reviews_dataset.csv')
products = pd.read_csv('data/raw/olist_products_dataset.csv')
translation = pd.read_csv('data/raw/product_category_name_translation.csv')
customers = pd.read_csv('data/raw/olist_customers_dataset.csv')

# stage-2 cleaning rules
reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'])
reviews = (
    reviews.sort_values('review_creation_date')
    .drop_duplicates(subset='order_id', keep='last')
)
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])
orders['delivery_duration_days'] = (
    orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']
).dt.days
orders['delay_days'] = (
    orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']
).dt.days
products['product_category_name'] = products['product_category_name'].fillna('unknown')
products = products.merge(translation, on='product_category_name', how='left')
items = items.merge(products[['product_id', 'product_category_name_english']], on='product_id', how='left')

delivered = orders[orders['order_status'] == 'delivered']

print('=' * 70)
print('تحلیل ترکیبی سوم — قیمت محصول و رضایت مشتری')
print('=' * 70)
rv_items = items.merge(reviews[['order_id', 'review_score']], on='order_id', how='inner')
print('آیتم‌های دارای نظر:', f'{len(rv_items):,}')
corr = rv_items['price'].corr(rv_items['review_score'])
print('همبستگی قیمت و امتیاز نظر:', round(corr, 3))
print()
rv_items['price_band'] = pd.cut(
    rv_items['price'],
    bins=[0, 50, 100, 200, 500, 1000, np.inf],
    labels=['۰ تا ۵۰', '۵۰ تا ۱۰۰', '۱۰۰ تا ۲۰۰', '۲۰۰ تا ۵۰۰', '۵۰۰ تا ۱۰۰۰', 'بیش از ۱۰۰۰'],
)
by_band = rv_items.groupby('price_band', observed=True).agg(
    items=('price', 'size'),
    mean_score=('review_score', 'mean'),
    mean_price=('price', 'mean'),
)
print(by_band.round(2).to_string())

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].scatter(rv_items['price'], rv_items['review_score'], alpha=0.05, s=6, color='#4c72b0')
axes[0].set_title(fa('پراکندگی قیمت در برابر امتیاز نظر'), fontsize=12)
axes[0].set_xlabel(fa('قیمت (BRL)'))
axes[0].set_ylabel(fa('امتیاز'))
axes[0].set_xlim(0, 1000)
axes[0].grid(alpha=0.3)
bars = axes[1].bar([str(b) for b in by_band.index], by_band['mean_score'],
                   color=['#4c72b0', '#55a868', '#c44e52', '#8172b3', '#ccb974', '#64b5cd'])
axes[1].bar_label(bars, labels=[f'{v:.2f}' for v in by_band['mean_score']], fontsize=9)
axes[1].set_title(fa('میانگین امتیاز در بازه‌های قیمت'), fontsize=12)
axes[1].set_ylabel(fa('میانگین امتیاز'))
axes[1].set_ylim(3.5, 4.5)
plt.setp(axes[1].get_xticklabels(), rotation=25, ha='right', fontsize=8)
axes[1].grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/13_1_price_vs_score.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('تحلیل ترکیبی پنجم — تغییرات فروش دسته‌بندی‌ها در طول زمان')
print('=' * 70)
cat_month = (
    items[items['order_id'].isin(delivered['order_id'])]
    .merge(orders[['order_id', 'order_purchase_timestamp']], on='order_id', how='left')
    .assign(month=lambda d: d['order_purchase_timestamp'].dt.to_period('M'))
)
top6 = (
    cat_month.groupby('product_category_name_english')['price'].sum()
    .sort_values(ascending=False).head(6).index.tolist()
)
print('شش دسته برتر بر اساس کل فروش:', ', '.join(top6))
trend = (
    cat_month[cat_month['product_category_name_english'].isin(top6)]
    .pivot_table(index='month', columns='product_category_name_english',
                 values='price', aggfunc='sum', fill_value=0)
)
trend = trend[top6] / 1e3
print()
print('فروش ماهانه (هزار BRL):')
print(trend.round(0).to_string())

# persistence check: 2018 H1 vs 2017 H1 for each top category
h1_2017 = trend.loc['2017-01':'2017-06'].sum()
h1_2018 = trend.loc['2018-01':'2018-06'].sum()
growth = ((h1_2018 / h1_2017 - 1) * 100).round(1)
print()
print('رشد فروش نیمه‌ی اول ۲۰۱۸ نسبت به ۲۰۱۷ (٪):')
print(growth.sort_values(ascending=False).to_string())

fig, ax = plt.subplots(figsize=(12, 5.5))
x = [str(m) for m in trend.index]
colors = ['#4c72b0', '#55a868', '#c44e52', '#8172b3', '#ccb974', '#64b5cd']
for col, color in zip(top6, colors):
    ax.plot(x, trend[col], label=col, color=color, lw=1.6)
ax.set_title(fa('روند ماهانه فروش ۶ دسته برتر (هزار BRL)'), fontsize=13)
ax.set_ylabel(fa('فروش (هزار BRL)'))
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
ax.legend(fontsize=8, ncols=2)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('charts/13_2_category_trend.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('تحلیل ترکیبی دوم — موقعیت جغرافیایی و عملکرد تحویل')
print('=' * 70)
st = (
    delivered.merge(customers[['customer_id', 'customer_state']], on='customer_id', how='left')
    .groupby('customer_state').agg(
        orders=('order_id', 'size'),
        avg_duration=('delivery_duration_days', 'mean'),
        late_pct=('delay_days', lambda x: (x > 0).mean() * 100),
    )
)
st = st[st['orders'] >= 100].copy()
mean_dur = st['avg_duration'].mean()
mean_late = st['late_pct'].mean()
st['duration_vs_avg'] = np.where(st['avg_duration'] > mean_dur, 'کند', 'سریع')
st['late_vs_avg'] = np.where(st['late_pct'] > mean_late, 'دیرکرد بالا', 'دیرکرد کم')
quad = st.groupby(['duration_vs_avg', 'late_vs_avg']).agg(
    states=('orders', 'size'),
    orders=('orders', 'sum'),
)
print(f'میانگین مدت تحویل کل: {mean_dur:.1f} روز | میانگین درصد تأخیر: {mean_late:.1f}٪')
print()
print('ربع‌بندی ایالت‌ها:')
print(quad.to_string())
print()
worst = st[(st['avg_duration'] > mean_dur) & (st['late_pct'] > mean_late)].sort_values(
    'avg_duration', ascending=False)
print('ایالت‌های نامطلوب در هر دو شاخص (کند + دیرکرد بالا):')
print(worst.round(1).to_string())

fig, ax = plt.subplots(figsize=(11, 6))
ax.scatter(st['avg_duration'], st['late_pct'], s=st['orders'] / 15, alpha=0.6, color='#4c72b0')
ax.axvline(mean_dur, color='gray', ls='--', lw=1, label=f'avg duration = {mean_dur:.1f}')
ax.axhline(mean_late, color='gray', ls=':', lw=1, label=f'avg late = {mean_late:.1f}%')
for name, row in st.iterrows():
    if name in worst.index or row['orders'] > 3000:
        ax.annotate(name, (row['avg_duration'], row['late_pct']), fontsize=8)
ax.set_title(fa('جغرافیا در برابر عملکرد تحویل (اندازه نقطه = تعداد سفارش)'), fontsize=13)
ax.set_xlabel(fa('میانگین مدت تحویل (روز)'))
ax.set_ylabel(fa('درصد سفارش‌های دیرکرددار'))
ax.legend(fontsize=9)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('charts/13_3_geo_delivery.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('نتیجه‌گیری تحلیلی ترکیبی')
print('=' * 70)
print('قیمت با رضایت بی‌ارتباط است؛ رشد فروش دسته‌های برتر نیمه‌ی ۲۰۱۸ کند شده؛')
print('شمال‌شرق در هر دو شاخص تحویل (کندی + دیرکرد) رکورددار است.')
