# تحلیل فروش و رفتار مشتریان Olist

## ساختار فایل‌ها

- `olist_analysis.ipynb`: تحلیل داده‌ها
- `olist_management_report.pdf`: گزارش مدیریتی
- `data/raw/`: داده‌های خام
- `.gitignore`: فایل‌های نادیده‌گرفته‌شده در گیت

## داده‌ها

فایل‌های زیر با همین نام‌ها در پوشه `data/raw/` قرار می‌گیرند:

```text
olist_orders_dataset.csv
olist_customers_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
olist_geolocation_dataset.csv
product_category_name_translation.csv
```

## اجرا

فرمان‌های زیر از ریشه پروژه اجرا می‌شوند:

```bash
python -m pip install jupyter pandas numpy matplotlib seaborn packaging arabic-reshaper python-bidi
jupyter notebook olist_analysis.ipynb
```

در نوت‌بوک، همه سلول‌ها به‌ترتیب با گزینه `Restart & Run All` اجرا می‌شوند.
