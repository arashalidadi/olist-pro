import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)

df = pd.read_csv('data/raw/olist_order_items_dataset.csv')

print('=' * 70)
print('شكل كلي جدول اقلام سفارش')
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
print('آزمون رابطه سفارش و قلم')
print('=' * 70)
print(f'تعداد سطر جدول:                     {len(df):,}')
print(f'تعداد order_id یکتا:                {df["order_id"].nunique():,}')
print(f'تعداد order_item_id یکتا:           {df["order_item_id"].nunique():,}')
print(f'تعداد product_id یکتا:              {df["product_id"].nunique():,}')
print(f'تعداد seller_id یکتا:               {df["seller_id"].nunique():,}')
print()
items_per_order = df.groupby('order_id').size()
print('توزیع تعداد اقلام به ازای هر سفارش:')
vc = items_per_order.value_counts().sort_index()
dist = pd.DataFrame({
    'تعداد اقلام': vc.index,
    'تعداد سفارش‌ها': vc.values,
    'درصد سفارش‌ها': (vc.values / len(items_per_order) * 100).round(2),
})
print(dist.head(10).to_string(index=False))
print(f'\nمیانگین اقلام هر سفارش: {items_per_order.mean():.4f}')
print(f'بیشترین اقلام یک سفارش: {items_per_order.max()}')

print()
print('=' * 70)
print('بررسی ترکیب (order_id, order_item_id) به عنوان کلید یکتا')
print('=' * 70)
dup = df.duplicated(subset=['order_id', 'order_item_id']).sum()
print(f'تعداد سطرهای تکراری با کلید (order_id, order_item_id): {dup:,}')

print()
print('=' * 70)
print('آمار توصیفی ستون‌های عددی')
print('=' * 70)
print(df[['price', 'freight_value']].describe().round(2).to_string())

print()
print('=' * 70)
print('بررسی مقادیر غیرعادی')
print('=' * 70)
print(f'سفارش‌هایی با قیمت صفر:        {(df["price"] == 0).sum()}')
print(f'سفارش‌هایی با حمل صفر:         {(df["freight_value"] == 0).sum()}')
print(f'بیشینه قیمت:                   {df["price"].max():,.2f}')
print(f'بیشینه هزینه حمل:              {df["freight_value"].max():,.2f}')
q99_price = df['price'].quantile(0.99)
q99_freight = df['freight_value'].quantile(0.99)
print(f'صدک ۹۹ قیمت:                   {q99_price:,.2f}')
print(f'صدک ۹۹ حمل:                    {q99_freight:,.2f}')
print(f'تعداد اقلام با قیمت بالای صدک ۹۹: {(df["price"] > q99_price).sum():,}')

print()
print('=' * 70)
print('بازه زمانی ثبت اقلام (shipping_limit_date)')
print('=' * 70)
shipping = pd.to_datetime(df['shipping_limit_date'])
print(f'از: {shipping.min()}')
print(f'تا: {shipping.max()}')
