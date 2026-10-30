import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 130)

df = pd.read_csv('data/raw/product_category_name_translation.csv')
products = pd.read_csv('data/raw/olist_products_dataset.csv')

print('=' * 70)
print('شكل كلي جدول ترجمه')
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
    'nunique': df.nunique(dropna=False),
})
info.index.name = 'column'
print(info.to_string())

print()
print('=' * 70)
print('نمونه ۱۰ سطر اول')
print('=' * 70)
print(df.head(10).to_string(index=False))

print()
print('=' * 70)
print('آزمون یکتایی ترجمه‌ها')
print('=' * 70)
print(f'نام پرتغالی یکتا:   {df["product_category_name"].nunique():,}')
print(f'نام انگلیسی یکتا:   {df["product_category_name_english"].nunique():,}')
print(f'سطر تکراری:         {df.duplicated().sum()}')

print()
print('=' * 70)
print('مقایسه با جدول محصولات — دسته‌بندی‌های ترجمه‌نشده')
print('=' * 70)
cats_products = set(products['product_category_name'].dropna().unique())
cats_translation = set(df['product_category_name'].dropna().unique())
print(f'دسته‌بندی جدول محصولات:   {len(cats_products)}')
print(f'دسته‌بندی جدول ترجمه:     {len(cats_translation)}')
print()
only_products = cats_products - cats_translation
only_translation = cats_translation - cats_products
print(f'دسته‌بندی‌های محصولات بدون ترجمه ({len(only_products)}):')
for c in sorted(only_products):
    n = (products['product_category_name'] == c).sum()
    print(f'  {c:40s} ({n} محصول)')
print()
print(f'ترجمه‌هایی که در محصولات استفاده نشده‌اند ({len(only_translation)}):')
for c in sorted(only_translation):
    print(f'  {c}')

print()
print('=' * 70)
print('بررسی موارد ترجمه‌نشده — از نظر املا')
print('=' * 70)
print('آیا این دسته‌بندی‌ها شبیه نسخه اصلاح‌شده‌شان هستند؟')
import difflib
for c in sorted(only_products):
    close = difflib.get_close_matches(c, cats_translation, n=2, cutoff=0.7)
    print(f'  {c:30s} -> نزدیک‌ترین ترجمه‌ها: {close}')
