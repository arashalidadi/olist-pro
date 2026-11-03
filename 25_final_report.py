import os
import sys

import arabic_reshaper
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bidi.algorithm import get_display

#sys.stdout.reconfigure(encoding='utf-8')

plt.rcParams['font.family'] = ['DejaVu Sans', 'Tahoma']


def fa(text):
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)[::-1]


os.makedirs('charts', exist_ok=True)

orders = pd.read_csv('data/raw/olist_orders_dataset.csv')
customers = pd.read_csv('data/raw/olist_customers_dataset.csv')
items = pd.read_csv('data/raw/olist_order_items_dataset.csv')
payments = pd.read_csv('data/raw/olist_order_payments_dataset.csv')
reviews = pd.read_csv('data/raw/olist_order_reviews_dataset.csv')

# stage-2 cleaning rules (same as notebook)
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])
orders['delivery_duration_days'] = (
    orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']
).dt.days
orders['delay_days'] = (
    orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']
).dt.days
reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'])
reviews = reviews.sort_values('review_creation_date').drop_duplicates('order_id', keep='last')
payments.loc[payments['payment_installments'] == 0, 'payment_installments'] = 1

delivered = orders[orders['order_status'] == 'delivered']

print('=' * 70)
print('گزارش نهایی مدیریت — شاخص‌های کلیدی و نمودارهای شاهد')
print('=' * 70)

# KPIs
n_orders_total = len(orders)
n_delivered = len(delivered)
n_customers = customers['customer_unique_id'].nunique()
total_revenue = items[items['order_id'].isin(delivered_ids)]['price'].sum() \
    if (delivered_ids := orders[orders['order_status'] == 'delivered']['order_id']) is not None else 0
mean_score = reviews['review_score'].mean()
late_pct = (delivered['delay_days'] > 0).mean() * 100
mean_delivery = delivered['delivery_duration_days'].mean()
cc_share = (payments['payment_type'] == 'credit_card').mean() * 100

print(f'سفارش‌ها: {n_orders_total:,} | تحویل‌شده: {n_delivered:,} ({n_delivered / n_orders_total * 100:.1f}٪)')
print(f'مشتریان یکتا: {n_customers:,} | درآمد تحویل‌شده: {total_revenue / 1e6:.1f}M BRL')
print(f'میانگین امتیاز: {mean_score:.2f} | تأخیر: {late_pct:.1f}٪ | میانگین تحویل: {mean_delivery:.1f} روز')
print(f'سهم کارت اعتباری: {cc_share:.1f}٪ تراکنش‌ها')

# --- Finding 1 chart: monthly orders trend ---
monthly_orders = (
    orders.assign(month=orders['order_purchase_timestamp'].dt.to_period('M'))
    .groupby('month')['order_id'].nunique()
)
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot([str(m) for m in monthly_orders.index], monthly_orders.values,
        color='#4c72b0', marker='o', ms=3)
ax.set_title(fa('یافته ۱: رشد پایدار سفارش‌ها با اوج Black Friday'), fontsize=12)
ax.set_ylabel(fa('سفارش‌های ماهانه'))
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=7)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('charts/14_1_orders_trend.png', dpi=150)
plt.close(fig)
peak = monthly_orders.idxmax()
print(f'\nیافته ۱ — روندها: اوج سفارش ماهانه {peak} با {monthly_orders.max():,} سفارش (Black Friday)')

# --- Finding 2 chart: top 10 categories ---
products = pd.read_csv('data/raw/olist_products_dataset.csv')
translation = pd.read_csv('data/raw/product_category_name_translation.csv')
products['product_category_name'] = products['product_category_name'].fillna('unknown')
products = products.merge(translation, on='product_category_name', how='left')
it = items.merge(products[['product_id', 'product_category_name_english']], on='product_id', how='left')
cat_sales = it.groupby('product_category_name_english').size().sort_values(ascending=False)
top10_share = cat_sales.head(10).sum() / cat_sales.sum() * 100
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.bar(cat_sales.head(10).index, cat_sales.head(10).values, color='#4c72b0')
ax.set_title(fa('یافته ۲: ده دسته اول ۶۴.۵٪ فروش'), fontsize=12)
plt.setp(ax.get_xticklabels(), rotation=35, ha='right', fontsize=8)
ax.set_ylabel(fa('تعداد آیتم'))
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/14_2_categories.png', dpi=150)
plt.close(fig)
print(f'یافته ۲ — محصولات: ۱۰ دسته اول {top10_share:.1f}٪ کل آیتم‌ها')

# --- Finding 3 chart: customers by state ---
state_cust = customers.groupby('customer_state')['customer_unique_id'].nunique().sort_values(ascending=False)
top5_share = state_cust.head(5).sum() / state_cust.sum() * 100
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.bar(state_cust.head(10).index, state_cust.head(10).values, color='#55a868')
ax.set_title(fa('یافته ۳: تمرکز جغرافیایی — پنج ایالت اول ۷۷٪ مشتریان'), fontsize=12)
plt.setp(ax.get_xticklabels(), rotation=35, ha='right', fontsize=8)
ax.set_ylabel(fa('مشتریان یکتا'))
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/14_3_geo.png', dpi=150)
plt.close(fig)
print(f'یافته ۳ — مشتریان: ۵ ایالت اول {top5_share:.1f}٪ مشتریان')

# --- Finding 4 chart: delivery status ---
late_pct_by_status = [
    (delivered['delay_days'] < 0).mean() * 100,
    (delivered['delay_days'] == 0).mean() * 100,
    (delivered['delay_days'] > 0).mean() * 100,
]
fig, ax = plt.subplots(figsize=(8, 4.5))
bars = ax.bar([fa('زودتر از موعد'), fa('به موقع'), fa('با تأخیر')], late_pct_by_status,
              color=['#55a868', '#7f7f7f', '#d62728'])
ax.bar_label(bars, labels=[f'{v:.1f}%' for v in late_pct_by_status], fontsize=10)
ax.set_title(fa('یافته ۴: ۹۱.۹٪ زودتر از موعد تحویل می‌شوند'), fontsize=12)
ax.set_ylabel(fa('درصد سفارش‌ها'))
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/14_4_delivery.png', dpi=150)
plt.close(fig)
print(f'یافته ۴ — تحویل: زودتر {late_pct_by_status[0]:.1f}٪ | تأخیر {late_pct_by_status[2]:.1f}٪')

# --- Finding 5 chart: delay vs satisfaction ---
df = delivered[['order_id', 'delay_days']].merge(
    reviews[['order_id', 'review_score']], on='order_id', how='inner')
grp = df.assign(group=np.where(df['delay_days'] > 0, 'late', 'on_time')).groupby('group')['review_score'].mean()
fig, ax = plt.subplots(figsize=(8, 4.5))
bars = ax.bar([fa('به موقع (شامل زودتر)'), fa('دیرکرددار')], [grp['on_time'], grp['late']],
              color=['#2ca02c', '#d62728'])
ax.bar_label(bars, labels=[f'{grp["on_time"]:.2f}', f'{grp["late"]:.2f}'], fontsize=11)
ax.set_title(fa('یافته ۵: تأخیر، رضایت را نصف می‌کند'), fontsize=12)
ax.set_ylabel(fa('میانگین امتیاز'))
ax.set_ylim(0, 5)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/14_5_delay_satisfaction.png', dpi=150)
plt.close(fig)
print(f'یافته ۵ — رضایت: به‌موقع {grp["on_time"]:.2f} در برابر دیرکرد {grp["late"]:.2f}')
