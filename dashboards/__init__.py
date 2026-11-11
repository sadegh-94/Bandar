"""
هر فایل .py در این پوشه (به‌جز فایل‌هایی که با _ شروع می‌شوند) یک داشبورد است. نام فایل = کلید داشبورد = آدرس /d/<نام فایل>/

حداقل چیزی که لازم است:
    META = {"name": "...", "description": "...", "category": "عمومی", "icon": "📊", "allowed_users": ["user1"]}

و یکی از این دو:
    1) bp = Blueprint(...)                        -> وب‌اپ Flask ساده
    2) dash.Dash(..., server=server, url_base_pathname="/d/<نام فایل>/")   -> داشبورد Dash (خودش روی سرور مشترک ثبت می‌شود)

ادمین به همه داشبوردها دسترسی دارد؛ بقیه فقط به نام‌های allowed_users. کنترل دسترسی در app.py انجام می‌شود.
"""
import importlib
import pkgutil


def load_dashboards(app):
    found = {}
    for mod in pkgutil.iter_modules(__path__):
        if mod.name.startswith('_'):
            continue
        module = importlib.import_module(f'{__name__}.{mod.name}')
        meta = getattr(module, 'META', None)
        if meta is None:
            print(f'[dashboards] {mod.name}: META تعریف نشده، نادیده گرفته شد')
            continue
        found[mod.name] = meta
        bp = getattr(module, 'bp', None)
        if bp is not None:
            app.register_blueprint(bp, url_prefix=f'/d/{mod.name}')
    return found
