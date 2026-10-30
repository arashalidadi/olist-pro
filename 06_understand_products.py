import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 130)

df = pd.read_csv('data/raw/olist_products_dataset.csv')

print('=' * 70)
print('شكل كلي جدول محصولات')
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
print('بررسی دسته‌بندی محصولات')
print('=' * 70)
n_null_cat = df['product_category_name'].isna().sum()
print(f'تعداد دسته‌بندی‌های یکتا (پرتغالی): {df["product_category_name"].nunique()}')
print(f'محصولات بدون دسته‌بندی:            {n_null_cat:,} ({n_null_cat / len(df) * 100:.2f}%)')
print()
vc_cat = df['product_category_name'].value_counts()
print('۱۰ دسته‌بندی پرمحصول:')
print(vc_cat.head(10).to_string())
print()
print('۵ دسته‌بندی کم‌محصول:')
print(vc_cat.tail(5).to_string())
print()
one_off = (vc_cat == 1).sum()
print(f'دسته‌بندی‌هایی که فقط ۱ محصول دارند: {one_off}')

print()
print('=' * 70)
print('بررسی مقادیر گمشده ستون‌های ویژگی')
print('=' * 70)
print('ستون‌های ابعاد و وزن — آیا خالی‌ها با هم ربط دارند؟')
dim_cols = ['product_name_lenght', 'product_description_lenght',
            'product_photos_qty', 'product_weight_g',
            'product_length_cm', 'product_height_cm', 'product_width_cm']
all_null = df[dim_cols].isna().all(axis=1).sum()
any_null = df[dim_cols].isna().any(axis=1).sum()
print(f'محصولاتی که همه این ۷ ستون خالی دارند: {all_null:,}')
print(f'محصولاتی که حداقل یکی خالی دارند:     {any_null:,}')
print()
print('درصد خالی هر ستون:')
for c in dim_cols:
    print(f'  {c:32s} {df[c].isna().mean() * 100:6.2f}%')

print()
print('=' * 70)
print('آمار توصیفی ستون‌های عددی')
print('=' * 70)
num_cols = ['product_name_lenght', 'product_description_lenght',
            'product_photos_qty', 'product_weight_g',
            'product_length_cm', 'product_height_cm', 'product_width_cm']
print(df[num_cols].describe().round(2).to_string())

print()
print('=' * 70)
print('بررسی مقادیر غیرعادی')
print('=' * 70)
print(f'وزن صفر:                    {(df["product_weight_g"] == 0).sum()}')
print(f'وزن بالای ۳۰ کیلوگرم:       {(df["product_weight_g"] > 30000).sum()}')
print(f'بیشینه وزن (گرم):            {df["product_weight_g"].max():,.0f}')
print(f'طول صفر:                    {(df["product_length_cm"] == 0).sum()}')
print(f'عرض صفر:                    {(df["product_width_cm"] == 0).sum()}')
print(f'ارتفاع صفر:                 {(df["product_height_cm"] == 0).sum()}')
print(f'طول عنوان صفر:              {(df["product_name_lenght"] == 0).sum()}')
