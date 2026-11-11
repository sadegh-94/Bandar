"""
هر فایل .py در این پوشه (به‌جز فایل‌هایی که با _ شروع می‌شوند) یک داشبورد است و باید دو چیز داشته باشد:

    META = {"name": "...", "description": "...", "category": "عمومی", "icon": "📊", "allowed_users": ["user1"]}
    bp   = Blueprint(...)    # صفحه‌ی داشبورد؛ روی /d/<نام فایل>/ سرو می‌شود

ادمین به همه داشبوردها دسترسی دارد. بقیه فقط به داشبوردهایی که نامشان در allowed_users است.
"""
import importlib
import pkgutil

from flask import session, jsonify, redirect


def load_dashboards(app, can_access):
    found = {}
    for mod in pkgutil.iter_modules(__path__):
        if mod.name.startswith('_'):
            continue
        module = importlib.import_module(f'{__name__}.{mod.name}')
        meta, bp = getattr(module, 'META', None), getattr(module, 'bp', None)
        if meta is None or bp is None:
            print(f'[dashboards] {mod.name}: META یا bp تعریف نشده، نادیده گرفته شد')
            continue
        key = mod.name
        found[key] = meta

        def guard(key=key):
            if 'user' not in session:
                return redirect('/login')
            if not can_access(session['user'], key):
                return jsonify({'error': 'Access Denied'}), 403

        bp.before_request(guard)
        app.register_blueprint(bp, url_prefix=f'/d/{key}')
    return found
