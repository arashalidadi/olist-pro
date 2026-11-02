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

# convert dates and compute delivery metrics (same logic as cleaning stage)
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])

orders['delivery_duration_days'] = (
    orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']
).dt.days
orders['delay_days'] = (
    orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']
).dt.days

# 9.1: delivered orders with valid dates
delivered = orders[
    (orders['order_status'] == 'delivered')
    & orders['order_purchase_timestamp'].notna()
    & orders['order_delivered_customer_date'].notna()
].copy()
print('سفارش‌های تحویل‌شده با تاریخ معتبر:', f'{len(delivered):,}')

dur = delivered['delivery_duration_days']
print()
print('=' * 70)
print('۹-۱. زمان تحویل (ثبت سفارش تا تحویل واقعی)')
print('=' * 70)
print(dur.describe()[['mean', '50%', 'min', 'max']].round(2).to_string())
print()
print('میانگین - میانه =', round(dur.mean() - dur.median(), 2), 'روز → توزیع راست‌کشیده (سفارش‌های بسیار کند کشیدگی ایجاد می‌کنند)')

fig, ax = plt.subplots(figsize=(11, 5))
ax.hist(dur.clip(0, 60), bins=60, color='#4c72b0', edgecolor='white')
ax.axvline(dur.mean(), color='#d62728', ls='--', lw=1.5, label=f"mean = {dur.mean():.1f}")
ax.axvline(dur.median(), color='#2ca02c', ls='--', lw=1.5, label=f"median = {dur.median():.1f}")
ax.set_title(fa('توزیع مدت زمان تحویل سفارش‌ها (تا ۶۰ روز)'), fontsize=13)
ax.set_xlabel(fa('روز از ثبت سفارش تا تحویل'))
ax.set_ylabel(fa('تعداد سفارش'))
ax.legend()
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/09_1_duration_hist.png', dpi=150)
plt.close(fig)

print()
p96 = (dur <= 20).mean() * 100
print(f'نسبت سفارش‌های تحویل‌شده تا ۲۰ روز: {p96:.1f}٪')
print('سفارش‌های بالای ۳۰ روز:', (dur > 30).sum())
print('طولانی‌ترین،', int(dur.max()), 'روز!')

print()
print('=' * 70)
print('۹-۲. تأخیر نسبت به تاریخ تخمینی')
print('=' * 70)
delivered['delay_status'] = np.where(
    delivered['delay_days'] < 0,
    'earlier',
    np.where(delivered['delay_days'] == 0, 'on_time', 'late'),
)
status_cnt = delivered['delay_status'].value_counts()
status_pct = (status_cnt / len(delivered) * 100).round(2)
for s, label in [('earlier', 'زودتر از موعد'), ('on_time', 'به موقع'), ('late', 'با تأخیر')]:
    print(f'{label}: {status_cnt.get(s, 0):,} ({status_pct.get(s, 0)}%)')
print()
late = delivered[delivered['delay_status'] == 'late']
print('میانگین روزهای تأخیر در سفارش‌های دیرکرددار:', round(late['delay_days'].mean(), 2))
print('تأخیر بیش از ۷ روز:', len(late[late['delay_days'] > 7]))

fig, ax = plt.subplots(figsize=(8, 5))
order_lbl = ['earlier', 'on_time', 'late']
colors = ['#55a868', '#7f7f7f', '#d62728']
vals = [status_cnt.get(s, 0) for s in order_lbl]
bars = ax.bar([fa(lbl) for lbl in ['زودتر از موعد', 'به موقع', 'با تأخیر']], vals, color=colors)
ax.bar_label(bars, labels=[f'{status_pct.get(s, 0)}%' for s in order_lbl], fontsize=10)
ax.set_title(fa('وضعیت تحویل نسبت به تاریخ تخمینی'), fontsize=13)
ax.set_ylabel(fa('تعداد سفارش'))
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/09_2_delay_status.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('۹-۳. عملکرد جغرافیایی و زمانی')
print('=' * 70)
state = delivered.merge(customers[['customer_id', 'customer_state']], on='customer_id', how='left')
by_state = state.groupby('customer_state').agg(
    orders=('order_id', 'size'),
    avg_duration=('delivery_duration_days', 'mean'),
    late_pct=('delay_days', lambda x: (x > 0).mean() * 100),
)
by_state = by_state[by_state['orders'] >= 100]
print('ایالت‌ها با حداقل ۱۰۰ سفارش — ۱۰ ایالت کندتر:')
slow10 = by_state.sort_values('avg_duration', ascending=False).head(10)
print(slow10.round(1).to_string())
print()
fast10 = by_state.sort_values('avg_duration').head(10)
print('۱۰ ایالت سریع‌تر برای مقایسه:')
print(fast10.round(1).to_string())

fig, ax = plt.subplots(figsize=(11, 5))
bars = ax.bar(slow10.index, slow10['avg_duration'], color='#d62728')
ax.bar_label(bars, labels=[f'{v:.1f}' for v in slow10['avg_duration']], fontsize=8)
ax.set_title(fa('۱۰ ایالت کندتر در تحویل (میانگین روز)'), fontsize=13)
ax.set_ylabel(fa('میانگین روزهای تحویل'))
plt.setp(ax.get_xticklabels(), rotation=35, ha='right', fontsize=9)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/09_3_slowest_states.png', dpi=150)
plt.close(fig)

print()
monthly = delivered.assign(
    month=delivered['order_purchase_timestamp'].dt.to_period('M'),
).groupby('month').agg(
    orders=('order_id', 'size'),
    avg_duration=('delivery_duration_days', 'mean'),
    late_pct=('delay_days', lambda x: (x > 0).mean() * 100),
)
print('روند ماهانه (میانگین مدت تحویل و درصد تأخیر):')
print(monthly.round(1).to_string())

fig, ax = plt.subplots(figsize=(12, 5))
x = [str(m) for m in monthly.index]
ax.plot(x, monthly['avg_duration'], color='#4c72b0', marker='o', label=fa('میانگین روزهای تحویل'))
ax2 = ax.twinx()
ax2.plot(x, monthly['late_pct'], color='#d62728', marker='s', label=fa('درصد تأخیر'))
ax.set_title(fa('روند ماهانه عملکرد ارسال'), fontsize=13)
ax.set_ylabel(fa('میانگین روزهای تحویل'))
ax2.set_ylabel(fa('درصد سفارش‌های دیرکرددار'))
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, fontsize=9)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('charts/09_4_monthly_trend.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('جمع‌بندی کسب‌وکاری')
print('=' * 70)
print('میانگین تحویل:', round(dur.mean(), 1), 'روز — تأخیر کل فقط', f"{status_pct.get('late', 0)}٪")
slow = slow10.index.tolist()
print('ایالت‌های کند:', ', '.join(slow))
