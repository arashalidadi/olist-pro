import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)

df = pd.read_csv('data/raw/olist_order_reviews_dataset.csv')

print('=' * 70)
print('شكل كلي جدول نظرات')
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
print('نمونه ۵ سطر اول (حذف متن طولانی)')
print('=' * 70)
print(df.drop(columns=['review_comment_message']).head().to_string())

print()
print('=' * 70)
print('آزمون کلیدی — یک نظر یا چند نظر برای هر سفارش؟')
print('=' * 70)
print(f'تعداد سطر جدول:              {len(df):,}')
print(f'تعداد order_id یکتا:         {df["order_id"].nunique():,}')
print(f'تعداد review_id یکتا:        {df["review_id"].nunique():,}')
print()
rev_per_order = df.groupby('order_id').size()
vc = rev_per_order.value_counts().sort_index()
dist = pd.DataFrame({
    'تعداد نظر': vc.index,
    'تعداد سفارش‌ها': vc.values,
    'درصد': (vc.values / len(rev_per_order) * 100).round(2),
})
print(dist.head(6).to_string(index=False))
print()
dup_rev = df['review_id'].duplicated().sum()
print(f'تعداد review_id تکراری: {dup_rev:,}')

print()
print('=' * 70)
print('توزیع امتیازها (review_score)')
print('=' * 70)
vc_score = df['review_score'].value_counts().sort_index()
tbl = pd.DataFrame({
    'امتیاز': vc_score.index,
    'تعداد': vc_score.values,
    'درصد': (vc_score.values / len(df) * 100).round(2),
})
print(tbl.to_string(index=False))
print()
print(f'میانگین امتیاز کل:   {df["review_score"].mean():.4f}')
print(f'میانه امتیاز کل:     {df["review_score"].median()}')
print(f'انحراف معیار:        {df["review_score"].std():.4f}')
pct_pos = df['review_score'].isin([4, 5]).mean() * 100
pct_neg = df['review_score'].isin([1, 2]).mean() * 100
print(f'درصد رضایت (۴ یا ۵): {pct_pos:.2f}%')
print(f'درصد نارضایتی (۱ یا ۲): {pct_neg:.2f}%')

print()
print('=' * 70)
print('ستون‌های متنی و تاریخی')
print('=' * 70)
has_msg = df['review_comment_message'].notna().sum()
print(f'نظرات با متن:   {has_msg:,} ({has_msg / len(df) * 100:.2f}%)')
print(f'نظرات بدون متن: {len(df) - has_msg:,}')
has_title = df['review_comment_title'].notna().sum()
print(f'نظرات با عنوان: {has_title:,} ({has_title / len(df) * 100:.2f}%)')
print()
answer_dt = pd.to_datetime(df['review_answer_timestamp'])
create_dt = pd.to_datetime(df['review_creation_date'])
print(f'بازه ثبت نظر:          از {create_dt.min()} تا {create_dt.max()}')
print(f'بازه پاسخ به نظر:      از {answer_dt.min()} تا {answer_dt.max()}')
print()
print('نمونه متن‌های نظرات (۵ مورد اول):')
for i, t in enumerate(df['review_comment_message'].dropna().head(5), 1):
    txt = str(t).replace('\n', ' ')[:100]
    print(f'  {i}. {txt}')
