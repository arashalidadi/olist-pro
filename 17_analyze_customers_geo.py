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

customers = pd.read_csv('data/raw/olist_customers_dataset.csv')

print('=' * 70)
print('۶-۱. تعداد مشتریان یکتا')
print('=' * 70)
print('تعداد سطر جدول (سفارش‌ها):', len(customers))
print('تعداد مشتریان یکتا:       ', customers['customer_unique_id'].nunique())
print('میانگین سفارش هر مشتری:   ', round(len(customers) / customers['customer_unique_id'].nunique(), 2))

print()
print('=' * 70)
print('۶-۲. مشتریان به تفکیک ایالت')
print('=' * 70)
state_customers = customers.groupby('customer_state')['customer_unique_id'].nunique().sort_values(ascending=False)
top10_states = state_customers.head(10)
state_share = (state_customers / state_customers.sum() * 100).round(2)
top5_share = state_share.head(5).sum()
state_table = pd.DataFrame({
    'تعداد مشتری': top10_states,
    'درصد': state_share.head(10),
    'درصد تجمعی': state_share.cumsum().head(10),
})
print(state_table.to_string())
print()
print('سهم ۵ ایالت اول از کل مشتریان:', round(top5_share, 2), '%')

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(top10_states.index, top10_states.values, color='#4c72b0')
ax.bar_label(bars, labels=[f'{p}%' for p in state_share.head(10).values], fontsize=9)
ax.set_title(fa('ده ایالت اول بر اساس تعداد مشتریان یکتا'), fontsize=13)
ax.set_xlabel(fa('ایالت'))
ax.set_ylabel(fa('تعداد مشتری'))
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/06_1_top_states.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('۶-۳. مشتریان به تفکیک شهر')
print('=' * 70)
city_customers = customers.groupby('customer_city')['customer_unique_id'].nunique().sort_values(ascending=False)
top10_cities = city_customers.head(10)
city_share = (city_customers / city_customers.sum() * 100).round(2)
city_table = pd.DataFrame({
    'تعداد مشتری': top10_cities,
    'درصد': city_share.head(10),
})
print(city_table.to_string())
print()
print('سهم ۱۰ شهر اول:', round(city_share.head(10).sum(), 2), '%')

fig, ax = plt.subplots(figsize=(11, 5))
bars = ax.bar(top10_cities.index, top10_cities.values, color='#55a868')
ax.bar_label(bars, labels=[f'{p}%' for p in city_share.head(10).values], fontsize=9)
ax.set_title(fa('ده شهر اول بر اساس تعداد مشتریان یکتا'), fontsize=13)
ax.set_xlabel(fa('شهر'))
ax.set_ylabel(fa('تعداد مشتری'))
plt.setp(ax.get_xticklabels(), rotation=30, ha='right', fontsize=9)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/06_2_top_cities.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('۶-۴. مقایسه مشتریان و سفارش‌ها در هر ایالت')
print('=' * 70)
orders_per_state = customers.groupby('customer_state').size()
compare = pd.DataFrame({
    'سفارش‌ها': orders_per_state,
    'مشتریان یکتا': state_customers,
})
compare['سفارش به ازای هر مشتری'] = (compare['سفارش‌ها'] / compare['مشتریان یکتا']).round(3)
compare = compare.sort_values('سفارش‌ها', ascending=False)
print(compare.head(10).to_string())
print()
print('نسبت سفارش به مشتری در کل دیتاست:', round(len(customers) / customers['customer_unique_id'].nunique(), 3))
print()
print('ایالت‌هایی که نسبت سفارش/مشتری بالاتر از میانگین کل دارند:')
above = compare[compare['سفارش به ازای هر مشتری'] > len(customers) / customers['customer_unique_id'].nunique()]
print(above[['سفارش‌ها', 'مشتریان یکتا', 'سفارش به ازای هر مشتری']].to_string())

top_states = compare.head(10)
x = range(len(top_states))
width = 0.38
fig, ax = plt.subplots(figsize=(12, 5))
ax.bar([i - width / 2 for i in x], top_states['سفارش‌ها'], width, label=fa('سفارش‌ها'), color='#4c72b0')
ax.bar([i + width / 2 for i in x], top_states['مشتریان یکتا'], width, label=fa('مشتریان یکتا'), color='#dd8452')
ax.set_xticks(list(x))
ax.set_xticklabels(top_states.index)
ax.set_title(fa('مقایسه سفارش‌ها و مشتریان یکتا در ده ایالت اول'), fontsize=13)
ax.set_xlabel(fa('ایالت'))
ax.set_ylabel(fa('تعداد'))
ax.legend()
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/06_3_customers_vs_orders.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('جمع‌بندی کسب‌وکاری')
print('=' * 70)
print('بازار به‌شدت متمرکز: ۵ ایالت اول', round(top5_share, 2), '٪ مشتریان را دارند')
print('سائوپائولو به‌تنهایی', round(city_share.iloc[0], 2), '٪ مشتریان')
