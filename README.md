# سیستم گزارشات بندر امام — نسخه Vercel

داشبوردها اینجا فایل exe نیستند؛ هر کدام یک ماژول پایتونی (Flask Blueprint) داخل پوشه `dashboards/` است و با دکمه «اجرا» در تب جدید باز می‌شود (`/d/<نام‌داشبورد>/`).

## ساختار
```
app.py                  برنامه اصلی (لاگین + لیست داشبوردها)
dashboards/
  __init__.py           کشف خودکار داشبوردها
  sample_report.py      نمونه
requirements.txt
```

## افزودن داشبورد
یک فایل جدید در `dashboards/` بسازید (مثلاً `unitdash.py`):
```python
from flask import Blueprint
META = {"name": "unitdash", "description": "توضیح", "category": "عمومی", "icon": "📈", "allowed_users": ["user1"]}
bp = Blueprint("unitdash", __name__)

@bp.route("/")
def index():
    return "<h1>unitdash</h1>"
```
ادمین به همه داشبوردها دسترسی دارد؛ بقیه فقط به نام‌های `allowed_users`. کتابخانه‌های لازم را در `requirements.txt` اضافه کنید.

> فقط کدهایی که بشود به‌صورت وب‌اپ Flask/WSGI درآورد کار می‌کنند. برنامه‌های Tkinter/PyQt و Streamlit روی Vercel اجرا نمی‌شوند.

## کاربران و رمز
کاربران از متغیر محیطی `APP_USERS` (JSON با رمز sha256) خوانده می‌شوند. ساخت هش:
```
python -c "import hashlib;print(hashlib.sha256('رمز-شما'.encode()).hexdigest())"
```
نمونه مقدار `APP_USERS`:
```
{"admin":{"password_sha256":"<هش>","name":"مدیر سیستم","role":"admin"},"user1":{"password_sha256":"<هش>","name":"کاربر یک","role":"user"}}
```
متغیر دوم `SECRET_KEY` است: یک رشته‌ی تصادفی بلند (مثلاً خروجی `python -c "import secrets;print(secrets.token_hex(32))"`).
بدون این دو متغیر روی Vercel ورود ممکن نیست (عمداً رمز پیش‌فرض ندارد).

## اجرای محلی
```
pip install -r requirements.txt
python app.py        # ورود پیش‌فرض محلی: admin / admin123
```

## دیپلوی روی Vercel
**روش اول: CLI**
```
npm i -g vercel
vercel login
vercel            # پاسخ پیش‌فرض‌ها؛ فریم‌ورک Flask خودکار شناسایی می‌شود
vercel env add SECRET_KEY
vercel env add APP_USERS
vercel --prod     # لینک نهایی: https://<project>.vercel.app
```
**روش دوم: GitHub** — پوشه را در یک ریپو بگذارید، در vercel.com/new ایمپورت کنید، در Settings ← Environment Variables همان دو متغیر را اضافه و Redeploy بزنید.

## محدودیت‌ها
- فایل‌سیستم Vercel دائمی نیست: آمار اجرا بعد از cold start صفر می‌شود و افزودن/حذف کاربر و تغییر دسترسی از داخل پنل ممکن نیست (دکمه‌های ادمین در این نسخه مخفی‌اند). تغییرات را در فایل‌ها/متغیرها بدهید و دوباره دیپلوی کنید. برای ذخیره‌ی دائمی باید دیتابیس (مثلاً Neon/Upstash) وصل شود.
- پلن Hobby رایگان برای استفاده‌ی غیرتجاری است؛ برای سامانه‌ی سازمانی شرایط استفاده را بررسی کنید.
- لینک Vercel عمومی است؛ داده‌ی حساس را فقط پشت لاگین نگه دارید.
