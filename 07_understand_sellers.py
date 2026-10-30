import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 130)

df = pd.read_csv('data/raw/olist_sellers_dataset.csv')

print('=' * 70)
print('شكل كلي جدول فروشندگان')
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
print('بررسی یکتایی و پوشش')
print('=' * 70)
print(f'تعداد سطر:                    {len(df):,}')
print(f'تعداد seller_id یکتا:         {df["seller_id"].nunique():,}')
print(f'کد پستی یکتا:                 {df["seller_zip_code_prefix"].nunique():,}')
print(f'تعداد شهر:                    {df["seller_city"].nunique():,}')
print(f'تعداد ایالت:                  {df["seller_state"].nunique():,}')

items = pd.read_csv('data/raw/olist_order_items_dataset.csv')
sellers_in_items = items['seller_id'].nunique()
missing = set(items['seller_id'].unique()) - set(df['seller_id'].unique())
print()
print(f'فروشندگانی که در جدول اقلام فروش داشته‌اند: {sellers_in_items:,}')
print(f'فروشندگان بدون هیچ فروش (این جدول):         {len(df) - sellers_in_items:,}')
print(f'فروشندگان اقلام که در جدول سellers نیستند:   {len(missing)}')

print()
print('=' * 70)
print('توزیع فروشندگان بر اساس ایالت')
print('=' * 70)
vc = df['seller_state'].value_counts()
tbl = pd.DataFrame({
    'تعداد فروشنده': vc,
    'درصد': (vc / len(df) * 100).round(2),
})
print(tbl.head(10).to_string())
print(f'... و {df["seller_state"].nunique() - 10} ایالت دیگر')

print()
print('=' * 70)
print('توزیع فروشندگان بر اساس شهر (10 شهر برتر)')
print('=' * 70)
vc_city = df['seller_city'].value_counts()
tbl = pd.DataFrame({
    'تعداد فروشنده': vc_city,
    'درصد': (vc_city / len(df) * 100).round(2),
})
print(tbl.head(10).to_string())
