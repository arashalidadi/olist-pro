import sys

import pandas as pd

#sys.stdout.reconfigure(encoding='utf-8')

DATE_COLS = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date',
]

df = pd.read_csv('data/raw/olist_orders_dataset.csv')
print('rows:', len(df))

print('\n--- datetime conversion ---')
print('before:')
print(df[DATE_COLS].dtypes.to_string())
for col in DATE_COLS:
    df[col] = pd.to_datetime(df[col], errors='coerce')
print('after:')
print(df[DATE_COLS].dtypes.to_string())
print('missing values after conversion:')
print(df[DATE_COLS].isna().sum().to_string())

print('\n--- delivered orders without delivery date ---')
mask = (df['order_status'] == 'delivered') & df['order_delivered_customer_date'].isna()
print('count:', int(mask.sum()))
df.loc[mask, 'order_delivered_customer_date'] = df.loc[mask, 'order_estimated_delivery_date']
remaining = ((df['order_status'] == 'delivered') & df['order_delivered_customer_date'].isna()).sum()
print('remaining after fix:', int(remaining))

print('\n--- derived columns ---')
df['order_year'] = df['order_purchase_timestamp'].dt.year
df['order_month'] = df['order_purchase_timestamp'].dt.month
df['order_day'] = df['order_purchase_timestamp'].dt.day
df['delivery_duration_days'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
df['delay_days'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days

delivered = df[df['order_status'] == 'delivered']
print('delivered orders:', len(delivered))
print('\ndelivery_duration_days stats:')
print(delivered['delivery_duration_days'].describe().to_string())
print('\ndelay_days stats:')
print(delivered['delay_days'].describe().to_string())
print('\ndelayed orders (delay_days > 0):', int((delivered['delay_days'] > 0).sum()))
print('on-time or early orders (delay_days <= 0):', int((delivered['delay_days'] <= 0).sum()))

print('\norders per year:')
print(delivered['order_year'].value_counts().sort_index().to_string())

print('\nfinal check: rows =', len(df), '| unique order_id =', df['order_id'].nunique())

df.to_csv('data/processed/olist_orders_cleaned.csv', index=False)
