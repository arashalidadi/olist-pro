import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)

df = pd.read_csv('data/raw/olist_order_payments_dataset.csv')

print('=' * 70)
print('شكل كلي جدول پرداخت‌ها')
print('=' * 70)
print(f'تعداد سطر:  {df.shape[0]:,}')
print(f'تعداد ستون: {df.shape[1]}')

print()
print('=' * 70)
print('ستون‌ها و نوع داده')
print('=' * 70)
info = pd.DataFrame({
    'dtype': df.dtypes.astype(str),
    'non_null': df.notna().sum(),
    'null': df.isna().sum(),
    'null_pct': (df.isna().mean() * 100).round(2),
    'nunique': df.nunique(dropna=False),
})
info.index.name = 'column'
print(info.to_string())

print()
print('=' * 70)
print('نمونه ۵ سطر اول')
print('=' * 70)
print(df.head().to_string())

print()
print('=' * 70)
print('آزمون کلیدی — آیا یک سفارش چند تراکنش دارد؟')
print('=' * 70)
print(f'تعداد سطر جدول:            {len(df):,}')
print(f'تعداد order_id یکتا:       {df["order_id"].nunique():,}')
print(f'تعداد سفارش چند-تراکنشی:  {(df.groupby("order_id").size() > 1).sum():,}')
print()
tx_per_order = df.groupby('order_id').size()
vc = tx_per_order.value_counts().sort_index()
dist = pd.DataFrame({
    'تعداد تراکنش': vc.index,
    'تعداد سفارش‌ها': vc.values,
    'درصد': (vc.values / len(tx_per_order) * 100).round(2),
})
print(dist.head(6).to_string(index=False))
print()
multi = df.groupby('order_id').filter(lambda x: len(x) > 1)
sample_id = multi['order_id'].iloc[0]
print(f'نمونه سفارش چند-تراکنشی ({sample_id}):')
print(df[df['order_id'] == sample_id].to_string(index=False))

print()
print('=' * 70)
print('روش‌های پرداخت')
print('=' * 70)
vc_pay = df['payment_type'].value_counts()
tbl = pd.DataFrame({
    'تعداد تراکنش': vc_pay,
    'درصد تراکنش': (vc_pay / len(df) * 100).round(2),
})
print(tbl.to_string())

print()
print('=' * 70)
print('مبلغ پرداختی به تفکیک روش')
print('=' * 70)
g = df.groupby('payment_type')['payment_value'].agg(['count', 'sum', 'mean', 'median'])
g.columns = ['تعداد تراکنش', 'مجموع مبلغ', 'میانگین مبلغ', 'میانه مبلغ']
g['سهم مبلغ از کل (%)'] = (df.groupby('payment_type')['payment_value'].sum() / df['payment_value'].sum() * 100).round(2)
print(g.round(2).to_string())


print()
print('=' * 70)
print('آمار توصیفی مبلغ پرداخت و اقساط')
print('=' * 70)
print(df[['payment_value', 'payment_installments', 'payment_sequential']].describe().round(2).to_string())

print()
print('=' * 70)
print('توزیع تعداد اقساط')
print('=' * 70)
vc_inst = df['payment_installments'].value_counts().sort_index()
tbl = pd.DataFrame({
    'تعداد اقساط': vc_inst.index,
    'تعداد تراکنش': vc_inst.values,
    'درصد': (vc_inst.values / len(df) * 100).round(2),
})
print(tbl.to_string(index=False))

print()
print('=' * 70)
print('بررسی مقادیر غیرعادی')
print('=' * 70)
print(f'پرداخت با مبلغ صفر:        {(df["payment_value"] == 0).sum():,}')
print(f'پرداخت با اقساط صفر:       {(df["payment_installments"] == 0).sum():,}')
print(f'بیشینه اقساط:               {df["payment_installments"].max()}')
print(f'بیشینه مبلغ:                {df["payment_value"].max():,.2f}')
zero_pay = df[df['payment_value'] == 0]
if len(zero_pay):
    print()
    print('نمونه پرداخت‌های صفر:')
    print(zero_pay.head().to_string(index=False))
