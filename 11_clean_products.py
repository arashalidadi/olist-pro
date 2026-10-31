import sys

import pandas as pd

#sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/raw/olist_products_dataset.csv')
print('rows:', len(df))

print('\n--- missing categories ---')
missing_cat = df['product_category_name'].isna().sum()
print('products without category:', int(missing_cat))
df['product_category_name'] = df['product_category_name'].fillna('unknown')
print('categories after fix:', df['product_category_name'].isna().sum())

print('\n--- zero / missing physical dimensions ---')
dim_cols = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
print('before:')
print(df[dim_cols].isna().sum().to_string())
print('zeros:')
print((df[dim_cols] == 0).sum().to_string())

for col in dim_cols:
    median_val = df[col].median()
    df.loc[df[col].isna() | (df[col] == 0), col] = median_val

print('\nafter:')
print(df[dim_cols].isna().sum().to_string())
print('zeros:')
print((df[dim_cols] == 0).sum().to_string())

print('\nfinal check: rows =', len(df), '| unique product_id =', df['product_id'].nunique())

df.to_csv('data/processed/olist_products_cleaned.csv', index=False)
