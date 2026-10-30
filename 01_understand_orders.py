
import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)

df = pd.read_csv('data/raw/olist_orders_dataset.csv')
# ---------------------------------------------------------------
print('=' * 70)
print('شكل كلي جدول سفارش‌ها')
print('=' * 70)
print(f'تعداد سطر (سفارش):   {df.shape[0]:,}')
print(f'تعداد ستون:           {df.shape[1]}')

# ---------------------------------------------------------------
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

# ---------------------------------------------------------------
print()
print('=' * 70)
print('نمونه ۵ سطر اول')
print('=' * 70)
print(df.head().to_string())


# ---------------------------------------------------------------
print()
print('=' * 70)
print('توزيع وضعیت سفارش (order_status)')
print('=' * 70)
vc = df['order_status'].value_counts(dropna=False)
stat = pd.DataFrame({
    'تعداد': vc,
    'درصد': (vc / len(df) * 100).round(2)
})
print(stat.to_string())
