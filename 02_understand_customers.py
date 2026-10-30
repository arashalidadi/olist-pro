
import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)


# ---------------------------------------------------------------
df = pd.read_csv('data/raw/olist_customers_dataset.csv')

print('=' * 70)
print('شكل كلي جدول مشتریان')
print('=' * 70)
print(f'تعداد سطر:  {df.shape[0]:,}')
print(f'تعداد ستون: {df.shape[1]}')


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
print('آزمون کلیدی — شمارش یکتاها')
print('=' * 70)
print(f'تعداد سطر جدول:                      {len(df):,}')
print(f'تعداد customer_id یکتا:              {df["customer_id"].nunique():,}')
print(f'تعداد customer_unique_id یکتا:       {df["customer_unique_id"].nunique():,}')
print(f'تعداد customer_zip_code_prefix یکتا: {df["customer_zip_code_prefix"].nunique():,}')


# ---------------------------------------------------------------
print()
print('=' * 70)
print('اثبات چند-سفارشی بودن مشتریان واقعی')
print('=' * 70)
orders_per_customer = df['customer_unique_id'].value_counts()
print('توزیع تعداد سفارش به ازای هر مشتری واقعی:')
vc = orders_per_customer.value_counts().sort_index()
dist = pd.DataFrame({
    'تعداد سفارش': vc.index,
    'تعداد مشتریان': vc.values,
    'درصد مشتریان': (vc.values / len(orders_per_customer) * 100).round(2),
})
print(dist.head(10).to_string(index=False))
print()
print(f'میانگین سفارش هر مشتری واقعی: {orders_per_customer.mean():.4f}')
print(f'بیشترین سفارش یک مشتری:       {orders_per_customer.max()}')


# ---------------------------------------------------------------
print()
print('=' * 70)
print('توزیع مشتریان بر اساس ایالت (10 ایالت برتر)')
print('=' * 70)
vc_state = df['customer_state'].value_counts()
state_tbl = pd.DataFrame({
    'تعداد مشتری': vc_state,
    'درصد': (vc_state / len(df) * 100).round(2),
})
print(state_tbl.head(10).to_string())
print(f'\nتعداد کل ایالت‌های موجود: {df["customer_state"].nunique()}')


# ---------------------------------------------------------------
print()
print('=' * 70)
print('توزیع مشتریان بر اساس شهر (10 شهر برتر)')
print('=' * 70)
vc_city = df['customer_city'].value_counts()
city_tbl = pd.DataFrame({
    'تعداد مشتری': vc_city,
    'درصد': (vc_city / len(df) * 100).round(2),
})
print(city_tbl.head(10).to_string())
print(f'\nتعداد کل شهرهای موجود: {df["customer_city"].nunique()}')
