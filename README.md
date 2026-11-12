# تحلیل فروش و رفتار مشتریان Olist

## ساختار فایل‌ها

- `project_requirements.md`: شرح پروژه
- `olist_analysis.ipynb`: تحلیل داده‌ها
- `olist_management_report.pdf`: گزارش مدیریتی
- `Olist-data/`: داده‌های خام
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

## نسخه‌های آزموده‌شده

نسخه‌های پایدار تا پایان 2026-10-30 بررسی شده‌اند. تحلیل در دو محیط مجزای Linux با داده‌های همین پروژه اجرا شده است:

| Python | pandas | NumPy | توضیح |
| --- | --- | --- | --- |
| 3.12.16 | 3.1.0 | 2.5.4 | ترکیب پیشنهادی با NumPy جدیدتر |
| 3.11.2 | 3.1.0 | 2.4.6 | ترکیب سازگار با Python 3.11 |

در هر دو محیط، `matplotlib==3.11.2`، `seaborn==0.13.2`، `packaging==26.3`، `arabic-reshaper==3.0.1` و `python-bidi==0.6.12` استفاده شده‌اند. برای اجرای نوت‌بوک نیز نسخه‌های `notebook==7.6.4`، `jupyterlab==4.6.5`، `ipython==9.18.0`، `ipykernel==7.4.0`، `nbclient==0.11.0`، `nbformat==5.11.1` و `matplotlib-inline==0.2.2` آزموده شده‌اند.

هر 47 سلول کد اجرا شد، هر 49 کنترل داخلی درست بود و خروجی‌های متنی، جدول‌ها و هر 33 نمودار با خروجی ذخیره‌شده یکسان بودند. این نتیجه به داده‌ها و محیط آزمون مربوط است؛ نسخه ریز Python، سیستم‌عامل، فونت‌ها و وابستگی‌های غیرمستقیم ممکن است متفاوت باشند. طبق [مشخصات NumPy 2.5.4 در PyPI](https://pypi.org/project/numpy/2.5.4/)، این نسخه به Python 3.12 یا جدیدتر نیاز دارد؛ برای Python 3.11 از نسخه 2.4.6 استفاده می‌شود.

## نصب و اجرا

در ریشه پروژه یک محیط مجازی **تازه** با Python 3.12 بسازید؛ اگر `.venv` از قبل وجود دارد، برای محیط جدید نام دیگری انتخاب کنید. در Linux یا macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

در Windows، برای نمونه در PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

برای Python 3.11، در فرمان ساخت محیط به‌جای `3.12` از `3.11` استفاده کنید. سپس، در محیط فعال‌شده و از ریشه پروژه:

```text
python -m pip install "pip==26.2.2"
python -m pip install --uploaded-prior-to 2026-10-31T00:00:00Z "notebook==7.6.4" "jupyterlab==4.6.5" "ipython==9.18.0" "ipykernel==7.4.0" "nbclient==0.11.0" "nbformat==5.11.1" "matplotlib-inline==0.2.2" "pandas==3.1.0" "numpy==2.5.4; python_version == '3.12'" "numpy==2.4.6; python_version == '3.11'" "matplotlib==3.11.2" "seaborn==0.13.2" "packaging==26.3" "arabic-reshaper==3.0.1" "python-bidi==0.6.12"
python -m pip check
python -m notebook olist_analysis.ipynb
```

این دستور برای بازتولید ترکیب آزموده‌شده است: نسخه‌های نام‌برده ثابت‌اند و فیلتر تاریخ از انتخاب بسته‌های منتشرشده پس از تاریخ بررسی جلوگیری می‌کند؛ با این حال همه وابستگی‌های غیرمستقیم یا فونت‌ها قفل نشده‌اند. برای استفاده از نسخه‌های جدیدتر، آن‌ها را در محیطی جداگانه نصب و کل تحلیل و خروجی‌ها را دوباره بررسی کنید.

در نوت‌بوک، در صورت وجود چند Kernel، محیط مجازی جدید را انتخاب کنید و همه سلول‌ها را به‌ترتیب با گزینه `Restart & Run All` اجرا کنید.

ممکن است در لاگ Jupyter هشدار ارتباط TCP بدون رمزنگاری میان Jupyter و Kernel دیده شود. این هشدار امنیتی خطای محاسباتی نیست؛ سرور را بدون تنظیم امنیت در شبکه عمومی قرار ندهید. در محیطی که CurveZMQ پشتیبانی می‌شود، برای فعال‌کردن رمزنگاری Kernel می‌توانید فرمان آخر را به‌شکل زیر اجرا کنید:

```text
python -m notebook --MappingKernelManager.transport_encryption=auto olist_analysis.ipynb
```
