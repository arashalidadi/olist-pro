import sys

import pandas as pd

#sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/raw/olist_order_payments_dataset.csv')
print('rows:', len(df))

print('\n--- zero installments ---')
zero_inst = (df['payment_installments'] == 0).sum()
print('payments with zero installments:', int(zero_inst))
df.loc[df['payment_installments'] == 0, 'payment_installments'] = 1
print('zero installments after fix:', int((df['payment_installments'] == 0).sum()))

print('\n--- zero-value payments (kept, filtered in revenue analysis) ---')
zero_val = (df['payment_value'] == 0).sum()
print('payments with zero value:', int(zero_val))

print('\nfinal check: rows =', len(df), '| orders covered =', df['order_id'].nunique())

df.to_csv('data/processed/olist_payments_cleaned.csv', index=False)
