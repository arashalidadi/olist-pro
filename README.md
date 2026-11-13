# تحلیل فروش و رفتار مشتریان Olist

## ساختار فایل‌ها

- `project_requirements.md`: شرح پروژه
- `olist_analysis.ipynb`: تحلیل داده‌ها
- `olist_management_report.pdf`: گزارش مدیریتی
- `Olist-data/`: داده‌های خام
- `requirements.txt`: کتابخانه‌های لازم برای اجرا
- `.gitignore`: فایل‌های نادیده‌گرفته‌شده در گیت

## داده‌ها

فایل‌های زیر با همین نام‌ها در پوشه `Olist-data/` قرار می‌گیرند:

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

## نصب و اجرا

برای اجرای نوت‌بوک به **Python 3.12 یا جدیدتر** نیاز است. در ریشه پروژه یک محیط مجازی بسازید؛ اگر `.venv` از قبل وجود دارد، برای محیط جدید نام دیگری انتخاب کنید.

در Linux یا macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

در Windows، برای نمونه در PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

اگر نسخه جدیدتری از Python نصب است، می‌توانید در فرمان ساخت محیط از همان نسخه استفاده کنید. سپس، در محیط فعال‌شده و از ریشه پروژه:

```bash
python -m pip install --upgrade pip
python -m pip install --upgrade -r requirements.txt
python -m notebook olist_analysis.ipynb
```

فایل `requirements.txt` حداقل نسخه کتابخانه‌ها را مشخص می‌کند؛ دستور بالا جدیدترین نسخه‌های پایدار سازگار را نصب یا ارتقا می‌دهد. بنابراین نسخه‌های نصب‌شده ممکن است در آینده تغییر کنند. برای ثبت دقیق نسخه‌های یک اجرا می‌توانید از `python -m pip freeze` استفاده کنید.

نوت‌بوک با Python 3.12.16، `pandas` 3.1.1 و `numpy` 2.5.4 اجرا شده است.

در نوت‌بوک، در صورت وجود چند Kernel، محیط مجازی ساخته‌شده را انتخاب کنید و همه سلول‌ها را به‌ترتیب با گزینه `Restart & Run All` اجرا کنید.
