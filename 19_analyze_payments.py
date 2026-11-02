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

payments = pd.read_csv('data/raw/olist_order_payments_dataset.csv')
orders = pd.read_csv('data/raw/olist_orders_dataset.csv')

# cleaning applied in stage 2: 2 zero-installment payments -> 1
payments.loc[payments['payment_installments'] == 0, 'payment_installments'] = 1

print('=' * 70)
print('۸-۱. بررسی روش‌های پرداخت')
print('=' * 70)
n_tx = len(payments)
n_orders = payments['order_id'].nunique()
print(f'کل رکوردهای پرداخت (تراکنش): {n_tx:,}')
print(f'سفارش‌های یکتا: {n_orders:,}')
print(f'سفارش‌های چندتراکنشی: {n_tx - n_orders:,}')

method_tx = payments.groupby('payment_type').size().sort_values(ascending=False)
share_tx = (method_tx / n_tx * 100).round(2)
method_sum = payments.groupby('payment_type')['payment_value'].sum().sort_values(ascending=False)
method_mean = payments.groupby('payment_type')['payment_value'].mean().round(1)
method_orders = payments.groupby('payment_type')['order_id'].nunique()

method_table = pd.DataFrame({
    'تعداد تراکنش': method_tx,
    'درصد تراکنش': share_tx,
    'تعداد سفارش': method_orders,
    'مجموع مبلغ': method_sum,
    'میانگین مبلغ': method_mean,
})
print(method_table.to_string())

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
bars = axes[0].bar(method_tx.index, method_tx.values, color='#4c72b0')
axes[0].bar_label(bars, labels=[f'{p}%' for p in share_tx.values], fontsize=9)
axes[0].set_title(fa('تعداد تراکنش و سهم هر روش پرداخت'), fontsize=13)
axes[0].set_ylabel(fa('تعداد تراکنش'))
axes[0].grid(axis='y', alpha=0.3)
plt.setp(axes[0].get_xticklabels(), rotation=25, ha='right', fontsize=9)

bars = axes[1].bar(method_sum.index, method_sum.values / 1e6, color='#55a868')
axes[1].bar_label(bars, labels=[f'{v/1e6:.1f}' for v in method_sum.values], fontsize=9)
axes[1].set_title(fa('مجموع مبلغ پرداخت هر روش (میلیون BRL)'), fontsize=13)
axes[1].set_ylabel(fa('مبلغ (میلیون BRL)'))
axes[1].grid(axis='y', alpha=0.3)
plt.setp(axes[1].get_xticklabels(), rotation=25, ha='right', fontsize=9)
fig.tight_layout()
fig.savefig('charts/08_1_payment_methods.png', dpi=150)
plt.close(fig)

print()
print('میانگین مبلغ به تفکیک روش:')
print(method_mean.sort_values(ascending=False).to_string())

fig, ax = plt.subplots(figsize=(9, 5))
mm = method_mean.sort_values(ascending=False)
bars = ax.bar(mm.index, mm.values, color='#dd8452')
ax.bar_label(bars, labels=[f'{v:,.0f}' for v in mm.values], fontsize=9)
ax.set_title(fa('میانگین مبلغ هر تراکنش به تفکیک روش پرداخت'), fontsize=13)
ax.set_ylabel(fa('میانگین مبلغ (BRL)'))
ax.grid(axis='y', alpha=0.3)
plt.setp(ax.get_xticklabels(), rotation=25, ha='right', fontsize=9)
fig.tight_layout()
fig.savefig('charts/08_2_avg_by_method.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('۸-۲. بررسی تعداد اقساط')
print('=' * 70)
inst = payments['payment_installments'].value_counts().sort_index()
print('توزیع تعداد اقساط:')
pd_inst = pd.DataFrame({'تعداد پرداخت': inst, 'درصد': (inst / n_tx * 100).round(2)})
print(pd_inst.to_string())
print()
print('پرداخت بدون قسط یا تک‌قسط (۰ یا ۱):', inst.get(1, 0), f'({inst.get(1, 0) / n_tx * 100:.1f}%)')
print('محبوب‌ترین تعداد اقساط:', inst.idxmax())

fig, ax = plt.subplots(figsize=(11, 5))
bars = ax.bar(inst.index, inst.values, color='#4c72b0')
ax.bar_label(bars, labels=[f'{p}%' for p in (inst / n_tx * 100).round(1).values], fontsize=8)
ax.set_title(fa('توزیع تعداد اقساط (هر ردیف پرداخت)'), fontsize=13)
ax.set_xlabel(fa('تعداد اقساط'))
ax.set_ylabel(fa('تعداد پرداخت'))
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/08_3_installments.png', dpi=150)
plt.close(fig)

print()
print('رابطه مبلغ پرداخت و تعداد اقساط (میانگین مبلغ در هر تعداد قسط):')
val_by_inst = payments.groupby('payment_installments')['payment_value']
val_table = pd.DataFrame({
    'میانگین مبلغ': val_by_inst.mean().round(1),
    'میانه': val_by_inst.median().round(1),
    'تعداد': val_by_inst.size(),
})
print(val_table.to_string())

fig, ax = plt.subplots(figsize=(11, 5))
grp = payments.groupby('payment_installments')['payment_value'].mean()
bars = ax.bar(grp.index, grp.values, color='#55a868')
ax.bar_label(bars, labels=[f'{v:,.0f}' for v in grp.values], fontsize=8)
ax.set_title(fa('میانگین مبلغ پرداخت به تفکیک تعداد اقساط'), fontsize=13)
ax.set_xlabel(fa('تعداد اقساط'))
ax.set_ylabel(fa('میانگین مبلغ (BRL)'))
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('charts/08_4_value_vs_installments.png', dpi=150)
plt.close(fig)

print()
print('الگوی اقساط به تفکیک روش (درصد سطر):')
inst_mix = pd.crosstab(payments['payment_type'], payments['payment_installments'], normalize='index') * 100
inst_mix = inst_mix.round(1)
print(inst_mix.to_string())

fig, ax = plt.subplots(figsize=(11, 4))
inst_mix.plot(kind='bar', stacked=True, ax=ax, colormap='tab20')
ax.set_title(fa('ترکیب تعداد اقساط در هر روش پرداخت'), fontsize=13)
ax.set_ylabel(fa('درصد'))
plt.setp(ax.get_xticklabels(), rotation=25, ha='right', fontsize=9)
ax.legend(title='', fontsize=8, ncols=6)
fig.tight_layout()
fig.savefig('charts/08_5_method_installment_mix.png', dpi=150)
plt.close(fig)

print()
print('=' * 70)
print('جمع‌بندی کسب‌وکاری')
print('=' * 70)
cc_share = share_tx.get('credit_card', 0)
print('سهم تراکنش credit_card:', cc_share, '٪')
print(' میانگین مبلغ اقساط ۱۰ به بالا:', round(val_table.loc[val_table.index >= 10, 'میانگین مبلغ'].mean(), 1))
