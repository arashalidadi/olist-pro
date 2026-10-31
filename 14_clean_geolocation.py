import sys
import pandas as pd
import os

#sys.stdout.reconfigure(encoding='utf-8')

# os.makedirs('data/processed', exist_ok=True)

df = pd.read_csv('data/raw/olist_geolocation_dataset.csv')

print('=' * 70)
print('پاک‌سازی جدول جغرافیا')
print('=' * 70)

initial_len = len(df)
df = df.drop_duplicates()
print(f'حذف سطرهای کاملاً تکراری: {initial_len - len(df)} سطر حذف شد.')


bad_coords = (
    (df['geolocation_lat'] < -40) | (df['geolocation_lat'] > 10) |
    (df['geolocation_lng'] < -80) | (df['geolocation_lng'] > -30)
)
print(f'حذف مختصات غیرعادی (خارج از برزیل): {bad_coords.sum()} سطر حذف شد.')
df = df[~bad_coords]


df.to_csv('data/processed/olist_geolocation_cleaned.csv', index=False)
