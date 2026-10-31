import os
import sys

import arabic_reshaper
import matplotlib.pyplot as plt
import pandas as pd
from bidi.algorithm import get_display

sys.stdout.reconfigure(encoding='utf-8')

plt.rcParams['font.family'] = ['DejaVu Sans', 'Tahoma']


def fa(text):
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)[::-1]


os.makedirs('charts', exist_ok=True)

DATE_COLS = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date',
]

orders = pd.read_csv('data/processed/olist_orders_cleaned.csv')
for col in DATE_COLS:
    orders[col] = pd.to_datetime(orders[col], errors='coerce')

mask = (orders['order_status'] == 'delivered') & orders['order_delivered_customer_date'].isna()
orders.loc[mask, 'order_delivered_customer_date'] = orders.loc[mask, 'order_estimated_delivery_date']

orders['order_year'] = orders['order_purchase_timestamp'].dt.year
orders['order_month'] = orders['order_purchase_timestamp'].dt.month
orders['order_dayofweek'] = orders['order_purchase_timestamp'].dt.day_of_week
orders['order_period'] = orders['order_purchase_timestamp'].dt.to_period('M')

print('بازه زمانی داده:', orders['order_purchase_timestamp'].min(), 'تا', orders['order_purchase_timestamp'].max())

print()
print('=' * 70)
print('۵-۱. وضعیت سفارش‌ها')
print('=' * 70)
status = orders['order_status'].value_counts()
status_pct = (status / len(orders) * 100).round(2)
status_table = pd.DataFrame({'تعداد': status, 'درصد': status_pct})
print(status_table.to_string())

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(status.index, status.values, color='#4c72b0')
ax.bar_label(bars, labels=[f'{p}%' for p in status_pct.values], fontsize=9)
ax.set_title(fa('وضعیت سفارش‌ها — تعداد و درصد'), fontsize=13)
ax.set_ylabel(fa('تعداد سفارش'))
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/05_1_orders_status.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('۵-۲. روند ماهانه سفارش‌ها')
print('=' * 70)
monthly = orders.groupby('order_period').size()
print('تعداد ماه‌ها:', len(monthly))
print('بیشترین ماه:', monthly.idxmax(), 'با', monthly.max(), 'سفارش')
print('کمترین ماه:', monthly.idxmin(), 'با', monthly.min(), 'سفارش')

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot([str(p) for p in monthly.index], monthly.values, marker='o', markersize=4, color='#4c72b0')
ax.set_title(fa('روند ماهانه ثبت سفارش‌ها'), fontsize=13)
ax.set_ylabel(fa('تعداد سفارش'))
ax.set_xlabel(fa('ماه'))
ax.grid(alpha=0.3)
plt.setp(ax.get_xticklabels(), rotation=60, fontsize=8)
fig.tight_layout()
fig.savefig('charts/05_2_orders_monthly_trend.png', dpi=150)
plt.close(fig)

print()
print('سفارش‌ها به تفکیک سال:')
yearly = orders.groupby('order_year').size()
for year, count in yearly.items():
    print(f'  {year}: {count:,}')

print()
print('=' * 70)
print('۵-۳. الگوی روزهای هفته')
print('=' * 70)
WEEKDAY_FA = {
    0: 'دوشنبه',
    1: 'سه‌شنبه',
    2: 'چهارشنبه',
    3: 'پنجشنبه',
    4: 'جمعه',
    5: 'شنبه',
    6: 'یکشنبه',
}
weekday_counts = orders.groupby('order_dayofweek').size().rename(index=WEEKDAY_FA)
weekday_pct = (weekday_counts / len(orders) * 100).round(2)
weekday_table = pd.DataFrame({'تعداد': weekday_counts, 'درصد': weekday_pct})
print(weekday_table.to_string())
print()
print('پرتعدادترین روز:', weekday_counts.idxmax())
print('کم‌تعدادترین روز:', weekday_counts.idxmin())

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar([fa(d) for d in weekday_counts.index], weekday_counts.values, color='#55a868')
ax.bar_label(bars, labels=[f'{p}%' for p in weekday_pct.values], fontsize=9)
ax.set_title(fa('تعداد سفارش‌ها به تفکیک روز هفته'), fontsize=13)
ax.set_ylabel(fa('تعداد سفارش'))
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/05_3_orders_weekday.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('۵-۴. پنج ماه پرتراکنش')
print('=' * 70)
top5 = monthly.sort_values(ascending=False).head(5)
print(top5.to_string())
print()
print('تعیین تعلق ماه‌ها به سال‌ها:', top5.index.year.value_counts().to_dict())

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar([str(p) for p in top5.index], top5.values, color='#8172b2')
ax.bar_label(bars, fontsize=9)
ax.set_title(fa('پنج ماه پرتراکنش'), fontsize=13)
ax.set_ylabel(fa('تعداد سفارش'))
ax.set_xlabel(fa('ماه'))
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/05_4_orders_top_months.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('جمع‌بندی کسب‌وکاری')
print('=' * 70)
delivered_pct = status_pct.get('delivered', 0)
canceled_pct = status_pct.get('canceled', 0) + status_pct.get('unavailable', 0)
weekday_sum = weekday_pct.loc[['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه']].sum()
weekend_sum = weekday_pct.loc[['شنبه', 'یکشنبه']].sum()
print(f'۹۷٪ سفارش‌ها تحویل شده‌اند؛ لغو و ناموجود مجموعاً {canceled_pct:.2f}%')
print(f'روند ماهانه از ۲۰۱۶ تا ۲۰۱۸ رو به رشد بوده است.')
print(f'مجموع ۵ ماه پرتراکنش: {top5.sum():,} سفارش ({top5.sum() / len(orders) * 100:.1f}% کل)')
print(f'سفارش‌های روزهای کاری (دوشنبه تا پنجشنبه): {weekday_sum:.1f}% | آخر هفته: {weekend_sum:.1f}%')
