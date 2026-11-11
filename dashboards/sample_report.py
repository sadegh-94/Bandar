"""نمونه داشبورد. کد داشبوردهای خودتان را به همین شکل (Blueprint + META) اینجا اضافه کنید."""
from flask import Blueprint, render_template_string

META = {
    'name': 'sample_report',
    'description': 'نمونه گزارش برای تست دیپلوی',
    'category': 'عمومی',
    'icon': '📈',
    'allowed_users': [],
}

bp = Blueprint('sample_report', __name__)

PAGE = '''<!DOCTYPE html><html dir="rtl" lang="fa"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>نمونه گزارش</title>
<style>body{font-family:Tahoma,sans-serif;background:#F7F7FB;margin:0;padding:24px;color:#1F2333}
.card{background:#fff;border:1px solid #EDEEF3;border-radius:16px;padding:24px;max-width:720px;margin:0 auto}
a{color:#6C5CE7}</style></head><body><div class="card">
<h2>نمونه گزارش</h2><p>این صفحه یک داشبورد پایتونی ساده است.</p>
<svg viewBox="0 0 300 120" width="100%"><g fill="#6C5CE7">
{% for v in data %}<rect x="{{ loop.index0*45+10 }}" y="{{ 110-v }}" width="30" height="{{ v }}" rx="4"/>{% endfor %}
</g></svg><p><a href="/">← بازگشت</a></p></div></body></html>'''


@bp.route('/')
def index():
    return render_template_string(PAGE, data=[40, 65, 50, 90, 75, 100])
