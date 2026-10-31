import sys

import pandas as pd

#sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/raw/olist_order_reviews_dataset.csv')
print('rows:', len(df))
print('unique review_id:', df['review_id'].nunique())
print('unique order_id:', df['order_id'].nunique())

reviews_per_order = df.groupby('order_id')['review_id'].nunique()
print('orders with more than one review:', int((reviews_per_order > 1).sum()))
print('reviews per order distribution:', reviews_per_order.value_counts().to_dict())

df['review_creation_date'] = pd.to_datetime(df['review_creation_date'], errors='coerce')
df['review_answer_timestamp'] = pd.to_datetime(df['review_answer_timestamp'], errors='coerce')

df = df.sort_values(['order_id', 'review_creation_date', 'review_answer_timestamp'], kind='stable')
df = df.drop_duplicates('order_id', keep='last').reset_index(drop=True)

print('\nrows after keeping latest review per order:', len(df))
print('unique order_id after:', df['order_id'].nunique())

print('\nscore distribution after dedup:')
print(df['review_score'].value_counts().sort_index().to_string())
print('mean score:', round(df['review_score'].mean(), 2))

print('\nfinal check: rows =', len(df), '| unique order_id =', df['order_id'].nunique())

df.to_csv('data/processed/olist_reviews_cleaned.csv', index=False)
