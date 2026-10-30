import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 130)

df = pd.read_csv('data/raw/olist_geolocation_dataset.csv')

print('=' * 70)
print('شكل كلي جدول جغرافیا')
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
print('آزمون کلیدی — آیا هر کد پستی یک مختصات دارد؟')
print('=' * 70)
print(f'تعداد سطر:                       {len(df):,}')
print(f'تعداد کد پستی یکتا:              {df["geolocation_zip_code_prefix"].nunique():,}')
print(f'تعداد سطر کاملاً تکراری:         {df.duplicated().sum():,}')
print(f'تعداد سطر تکراری فقط با مختصات: {df.duplicated(subset=["geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng"]).sum():,}')
print()
coords_per_zip = df.groupby('geolocation_zip_code_prefix').size()
vc = coords_per_zip.value_counts().sort_index()
dist = pd.DataFrame({
    'تعداد مختصات': vc.index,
    'تعداد کد پستی': vc.values,
})
print('توزیع تعداد مختصات به ازای هر کد پستی (۱۰ ردیف اول):')
print(dist.head(10).to_string(index=False))
print()
print(f'میانگین مختصات هر کد پستی: {coords_per_zip.mean():.2f}')
print(f'بیشترین مختصات برای یک کد پستی: {coords_per_zip.max()}')

print()
print('=' * 70)
print('بررسی یک کد پستی با چند مختصات (نمونه واقعی)')
print('=' * 70)
sample_zip = coords_per_zip.idxmax()
print(f'کد پستی {sample_zip} با {coords_per_zip.max()} مختصات:')
print(df[df['geolocation_zip_code_prefix'] == sample_zip].head(8).to_string(index=False))
print()
span = df[df['geolocation_zip_code_prefix'] == sample_zip]
print(f'گستره عرض جغرافیایی: {span["geolocation_lat"].max() - span["geolocation_lat"].min():.4f} درجه')
print(f'گستره طول جغرافیایی: {span["geolocation_lng"].max() - span["geolocation_lng"].min():.4f} درجه')

print()
print('=' * 70)
print('بررسی محدوده مختصات — آیا منطقی است؟')
print('=' * 70)
print(df[['geolocation_lat', 'geolocation_lng']].describe().round(4).to_string())
print()
print('برزیل تقریباً بین عرض  -34 تا +6 و طول  -74 تا -34 قرار دارد')
bad_lat = ((df['geolocation_lat'] < -40) | (df['geolocation_lat'] > 10)).sum()
bad_lng = ((df['geolocation_lng'] < -80) | (df['geolocation_lng'] > -30)).sum()
print(f'مختصات با عرض خارج از محدوده برزیل: {bad_lat:,}')
print(f'مختصات با طول خارج از محدوده برزیل: {bad_lng:,}')
