import hashlib
import hmac
import json
import os
import time
from datetime import datetime

from flask import Flask, render_template_string, jsonify, request, session, redirect, url_for

from dashboards import load_dashboards

app = Flask(__name__)

IS_VERCEL = bool(os.environ.get('VERCEL'))
_secret = os.environ.get('SECRET_KEY')
if not _secret:
    if IS_VERCEL:
        raise RuntimeError('متغیر محیطی SECRET_KEY روی Vercel تنظیم نشده است')
    _secret = 'dev-only-secret'
app.secret_key = _secret
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=IS_VERCEL)

DASHBOARDS = load_dashboards(app, lambda u, k: user_can_access_dashboard(u, k))  # {key: META} + ثبت Blueprint هر داشبورد در /d/<key>/


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    """کاربران از متغیر محیطی APP_USERS خوانده می‌شوند (JSON با رمز sha256)."""
    raw = os.environ.get('APP_USERS')
    if raw:
        try:
            return json.loads(raw)
        except ValueError:
            return {}
    if IS_VERCEL:
        return {}
    # فقط برای اجرای محلی
    return {'admin': {'password_sha256': hash_password('admin123'), 'name': 'مدیر سیستم', 'role': 'admin'}}


# آمار اجرا: فقط در حافظه + /tmp (در Vercel دائمی نیست و با cold start صفر می‌شود)
STATS_FILE = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'dashboard_stats.json')
_stats = None


def load_stats():
    global _stats
    if _stats is None:
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                _stats = json.load(f)
        except Exception:
            _stats = {}
    return _stats


def save_stats():
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(_stats or {}, f, ensure_ascii=False)
    except Exception:
        pass


def user_can_access_dashboard(username, key):
    user = load_users().get(username)
    meta = DASHBOARDS.get(key)
    if not user or not meta:
        return False
    return user.get('role') == 'admin' or username in meta.get('allowed_users', [])


LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سیستم گزارشات بندر امام</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root{
            --primary:#6C5CE7;
            --primary-dark:#4B3FCF;
            --ink:#1F2333;
            --muted:#8A8FA3;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            display: flex;
            background: #ffffff;
        }
        .login-page { display: flex; width: 100%; min-height: 100vh; }
        .brand-panel {
            position: relative;
            flex: 1 1 46%;
            min-width: 320px;
            overflow: hidden;
            background: linear-gradient(160deg, #241E4E 0%, #4B3FCF 55%, #7C6CF0 100%);
            color: #fff;
            padding: 48px 56px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .brand-panel::before, .brand-panel::after {
            content: '';
            position: absolute;
            border-radius: 50%;
            background: rgba(255,255,255,0.06);
        }
        .brand-panel::before { width: 420px; height: 420px; top: -160px; right: -140px; }
        .brand-panel::after { width: 300px; height: 300px; bottom: -120px; left: -80px; background: rgba(255,255,255,0.05); }
        .brand-logo { display:flex; align-items:center; gap:10px; font-size:1.1em; font-weight:bold; position:relative; z-index:1; }
        .brand-logo .logo-box {
            width:38px; height:38px; border-radius:10px; background:#fff; color:var(--primary);
            display:flex; align-items:center; justify-content:center; font-size:1.1em;
        }
        .mock-card {
            position: relative; z-index: 1;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 18px;
            padding: 22px;
            max-width: 420px;
            margin: 30px 0;
            backdrop-filter: blur(4px);
        }
        .mock-dots { display:flex; gap:6px; margin-bottom:16px; }
        .mock-dots span { width:7px; height:7px; border-radius:50%; background:rgba(255,255,255,0.5); display:inline-block; }
        .mock-bar-top { height:8px; border-radius:6px; background:rgba(255,255,255,0.25); width:60%; margin-bottom:18px; }
        .mock-tiles { display:flex; gap:10px; margin-bottom:20px; }
        .mock-tile { flex:1; height:46px; border-radius:10px; background:rgba(255,255,255,0.85); }
        .mock-tile:nth-child(1){ background:#a29bfe; }
        .mock-tile:nth-child(2){ background:#55efc4; }
        .mock-tile:nth-child(3){ background:#a29bfe; }
        .mock-chart { display:flex; align-items:flex-end; gap:8px; height:70px; }
        .mock-chart span { flex:1; border-radius:5px 5px 0 0; background:rgba(255,255,255,0.5); }
        .mock-chart span.hl { background:#55efc4; }
        .brand-copy { position: relative; z-index: 1; }
        .brand-copy h2 { font-size: 1.8em; line-height:1.5; margin-bottom: 14px; }
        .brand-copy p { color: rgba(255,255,255,0.85); line-height:1.8; max-width: 420px; }
        .brand-footer {
            position: relative; z-index: 1;
            display:flex; color: rgba(255,255,255,0.6); font-size:0.8em;
        }
        .form-panel {
            flex: 1 1 54%;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px 24px;
            background:#fff;
        }
        .form-card { width: 100%; max-width: 420px; }
        .form-card h1 { color: var(--ink); font-size: 1.9em; margin-bottom: 10px; }
        .form-card > p { color: var(--muted); margin-bottom: 28px; line-height:1.6; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; color: var(--ink); font-weight: 600; margin-bottom: 8px; font-size: 0.92em; }
        .input-wrap { position: relative; }
        .input-wrap .icon {
            position: absolute; top: 50%; right: 14px; transform: translateY(-50%);
            color: var(--muted); font-size: 1em; pointer-events:none;
        }
        .form-group input {
            width: 100%;
            padding: 13px 44px 13px 15px;
            border: 1.5px solid #E7E8F0;
            background:#FAFAFD;
            border-radius: 12px;
            font-size: 0.95em;
            transition: border-color 0.2s, background 0.2s;
            font-family: inherit;
        }
        .form-group input::placeholder { color: #B7BAC9; }
        .form-group input:focus { outline: none; border-color: var(--primary); background:#fff; }
        .form-row {
            display:flex; justify-content:space-between; align-items:center;
            margin-bottom: 22px; font-size: 0.88em;
        }
        .remember { display:flex; align-items:center; gap:6px; color:#5B5F73; }
        .form-row a { color: var(--primary); text-decoration:none; font-weight:600; }
        .form-row a:hover { text-decoration:underline; }
        .login-button {
            width: 100%;
            padding: 15px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.02em;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.25s, transform 0.15s;
            font-family: inherit;
        }
        .login-button:hover { background: var(--primary-dark); }
        .login-button:active { transform: scale(0.99); }
        .secure-note { text-align:center; color: var(--muted); font-size:0.82em; margin-top: 22px; }
        .error-message {
            background: #FDECEC;
            color: #C0392B;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 0.9em;
            display: none;
        }
        .error-message.show { display: block; animation: shake 0.4s; }
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-8px); }
            75% { transform: translateX(8px); }
        }
        .default-creds {
            margin-top: 18px;
            padding: 14px;
            background: #F7F7FB;
            border-radius: 10px;
            text-align: center;
            font-size: 0.85em;
            color: var(--muted);
        }
        .default-creds strong { color: var(--ink); }
        .users-list { margin-top: 8px; text-align: right; }
        @media (max-width: 900px) {
            .brand-panel { display: none; }
            .form-panel { flex: 1 1 100%; }
        }
    </style>
</head>
<body>
    <div class="login-page">
        <div class="brand-panel">
            <div class="brand-logo"><span class="logo-box">📈</span><span>سیستم گزارشات بندر امام</span></div>
            <div class="mock-card">
                <div class="mock-dots"><span></span><span></span><span></span></div>
                <div class="mock-bar-top"></div>
                <div class="mock-tiles">
                    <div class="mock-tile"></div>
                    <div class="mock-tile"></div>
                    <div class="mock-tile"></div>
                </div>
                <div class="mock-chart">
                    <span style="height:35%"></span>
                    <span style="height:55%"></span>
                    <span style="height:30%"></span>
                    <span style="height:70%"></span>
                    <span class="hl" style="height:95%"></span>
                    <span style="height:50%"></span>
                </div>
            </div>
            <div class="brand-copy">
                <h2>تصمیم‌های بهتر، با یک نگاه روشن</h2>
                <p>همه داشبوردها، گزارش‌ها و دسترسی‌های سازمان را در یک فضای امن و یکپارچه مدیریت کنید.</p>
            </div>
            <div class="brand-footer">
                <span>نسخه ۲.۴.۰</span>
            </div>
        </div>
        <div class="form-panel">
            <div class="form-card">
                <h1>خوش آمدید</h1>
                <p>برای ورود به پنل مدیریت، اطلاعات خود را وارد کنید.</p>
                <div class="error-message" id="errorMessage"></div>
                <form id="loginForm" onsubmit="return handleLogin(event)">
                    <div class="form-group">
                        <label for="username">نام کاربری یا ایمیل</label>
                        <div class="input-wrap">
                            <input type="text" id="username" name="username" placeholder="example@company.ir" required autofocus>
                            <span class="icon">👤</span>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="password">رمز عبور</label>
                        <div class="input-wrap">
                            <input type="password" id="password" name="password" placeholder="رمز عبور خود را وارد کنید" required>
                            <span class="icon">🔒</span>
                        </div>
                    </div>
                    <div class="form-row">
                        <label class="remember"><input type="checkbox" id="rememberMe"> مرا به خاطر بسپار</label>
                        <a href="#" onclick="return false;">رمز عبور را فراموش کرده‌اید؟</a>
                    </div>
                    <button type="submit" class="login-button">ورود به سامانه</button>
                </form>
            </div>
        </div>
    </div>
    <script>
        async function handleLogin(event) {
            event.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorDiv = document.getElementById('errorMessage');
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                const result = await response.json();
                if (result.success) {
                    window.location.href = '/';
                } else {
                    errorDiv.textContent = result.error || 'نام کاربری یا رمز عبور اشتباه است';
                    errorDiv.classList.add('show');
                    setTimeout(() => errorDiv.classList.remove('show'), 3000);
                }
            } catch (error) {
                errorDiv.textContent = 'خطا در برقراری ارتباط';
                errorDiv.classList.add('show');
            }
            return false;
        }
    </script>
</body>
</html>
'''

MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مدیریت داشبوردها</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root{
            --primary:#6C5CE7;
            --primary-dark:#4B3FCF;
            --ink:#1F2333;
            --muted:#8A8FA3;
            --border:#EDEEF3;
            --bg:#F7F7FB;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg);
            min-height: 100vh;
            padding: 24px;
            color: var(--ink);
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: white;
            border-radius: 16px;
            padding: 16px 26px;
            margin-bottom: 24px;
            border: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }
        .header-right { display: flex; align-items: center; gap: 22px; }
        .header-brand { display: flex; align-items: center; gap: 12px; }
        .app-icon {
            width: 42px; height: 42px; border-radius: 12px;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: #fff; display:flex; align-items:center; justify-content:center; font-size:1.2em;
        }
        .app-title { font-size: 1.15em; font-weight: bold; color: var(--ink); }
        .app-status { display:flex; align-items:center; gap:6px; color:#2ECC71; font-size:0.82em; margin-top:2px; }
        .app-status .dot { width:7px; height:7px; border-radius:50%; background:#2ECC71; display:inline-block; }
        .header-user { display: flex; align-items: center; gap: 10px; padding-right: 18px; border-right: 1px solid var(--border); }
        .avatar {
            width: 38px; height: 38px; border-radius: 50%;
            background: #EDEAFB; color: var(--primary);
            display:flex; align-items:center; justify-content:center; font-weight:bold;
        }
        .user-name { color: var(--ink); font-weight: bold; font-size: 0.92em; }
        .user-role { color: var(--muted); font-size: 0.8em; }
        .header-actions { display: flex; gap: 10px; }
        .btn {
            padding: 10px 18px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9em;
            transition: all 0.2s;
            font-family: inherit;
            border: 1px solid transparent;
            display: inline-flex; align-items: center; gap: 6px;
        }
        .btn-primary { background: var(--primary); color: #fff; }
        .btn-primary:hover { background: var(--primary-dark); }
        .btn-outline { background: #fff; color: var(--ink); border-color: var(--border); }
        .btn-outline:hover { background: #F5F5FA; }
        .btn-outline-danger { background: #fff; color: #EB5757; border-color: var(--border); }
        .btn-outline-danger:hover { background: #FDECEC; }
        .manage-button, .logout-button { padding: 10px 18px; border-radius: 10px; cursor: pointer; font-weight: 600; font-size: 0.9em; border: 1px solid var(--border); font-family: inherit; }
        .page-heading { margin-bottom: 22px; }
        .page-heading h2 { font-size: 1.5em; color: var(--ink); margin-bottom: 6px; }
        .page-heading p { color: var(--muted); font-size: 0.92em; }
        .search-bar {
            background: #fff; border: 1px solid var(--border); border-radius: 12px;
            padding: 13px 18px; margin-bottom: 26px; display:flex; align-items:center; gap:10px;
        }
        .search-bar span { color: var(--muted); }
        .search-bar input {
            border: none; outline: none; flex: 1; font-size: 0.95em; font-family: inherit; background: transparent; color: var(--ink);
        }
        .section-title { font-size: 1.05em; font-weight: bold; color: var(--ink); margin: 8px 0 14px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 18px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #fff; border: 1px solid var(--border); border-radius: 16px;
            padding: 20px 22px; display: flex; align-items: flex-start; justify-content: space-between;
        }
        .stat-text { text-align: right; }
        .stat-value { font-size: 2em; font-weight: bold; color: var(--ink); }
        .stat-label { color: var(--muted); font-size: 0.85em; margin-top: 4px; }
        .stat-icon {
            width: 46px; height: 46px; border-radius: 12px; flex-shrink:0;
            display:flex; align-items:center; justify-content:center; font-size: 1.3em;
        }
        .stat-icon.orange { background: #FDECD3; }
        .stat-icon.green { background: #DCF5E7; }
        .stat-icon.purple { background: #EDEAFB; }
        .filter-row { display:flex; align-items:center; gap:8px; color: var(--muted); font-size:0.9em; margin-bottom: 16px; }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
        }
        .dashboard-card {
            background: white;
            border-radius: 16px;
            padding: 22px;
            border: 1px solid var(--border);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            position: relative;
        }
        .dashboard-card:hover { transform: translateY(-3px); box-shadow: 0 12px 24px rgba(31,35,51,0.08); }
        .card-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 14px;
        }
        .card-badges { display: flex; gap: 8px; }
        .badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75em; font-weight: 600; }
        .badge-run { background: #DCF5E7; color: #1E9E5A; }
        .badge-cat { background: #F1F1F6; color: var(--muted); }
        .card-icon {
            width: 42px; height: 42px; border-radius: 10px; background: #EDEAFB; color: var(--primary);
            display:flex; align-items:center; justify-content:center; font-size:1.15em; flex-shrink:0;
        }
        .dashboard-title { font-size: 1.15em; color: var(--ink); font-weight: bold; margin-bottom: 8px; }
        .dashboard-description { color: var(--muted); margin-bottom: 16px; line-height: 1.6; font-size: 0.9em; }
        .card-divider { border: none; border-top: 1px solid var(--border); margin-bottom: 14px; }
        .card-footer { display:flex; justify-content: space-between; align-items: center; gap: 10px; }
        .card-link { color: var(--primary); text-decoration:none; font-size: 0.85em; font-weight: 600; }
        .card-link:hover { text-decoration: underline; }
        .last-run { color: var(--muted); font-size: 0.78em; margin-top: 4px; }
        .footer-meta { text-align: right; }
        .launch-button {
            padding: 10px 20px;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 0.9em;
            font-weight: bold;
            cursor: pointer;
            transition: filter 0.2s;
            white-space: nowrap;
            font-family: inherit;
        }
        .launch-button:hover { filter: brightness(0.92); }
        .launch-button:disabled { background: #ccc !important; cursor: not-allowed; }
        .launch-button.accent-purple { background: #6C5CE7; }
        .launch-button.accent-cyan { background: #00B8D9; }
        .launch-button.accent-green { background: #2ECC71; }
        .launch-button.accent-orange { background: #F5A623; }
        .launch-button.running {
            background: #EB5757 !important;
        }
        .no-access { opacity: 0.6; }
        .no-access-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 16px;
            background: rgba(255,255,255,0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #EB5757;
            font-weight: bold;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 28px;
            border-radius: 16px;
            width: 90%;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            border: 1px solid var(--border);
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .modal-header h2 { color: var(--ink); font-size: 1.2em; }
        .close-modal { font-size: 1.6em; cursor: pointer; color: var(--muted); line-height: 1; }
        .close-modal:hover { color: var(--ink); }
        .dashboard-item {
            background: var(--bg);
            padding: 18px;
            border-radius: 12px;
            margin-bottom: 14px;
            border: 1px solid var(--border);
        }
        .permission-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        .save-button {
            background: var(--primary);
            color: white;
            padding: 12px 28px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 18px;
            font-family: inherit;
        }
        .save-button:hover { background: var(--primary-dark); }
        .add-user-section {
            background: #EEF1FF;
            padding: 18px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .add-user-form {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        .add-user-form input {
            padding: 10px;
            border: 1.5px solid var(--border);
            border-radius: 8px;
            font-family: inherit;
        }
        .add-user-btn {
            background: var(--primary);
            color: white;
            padding: 8px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            font-family: inherit;
        }
        .add-user-btn:hover { background: var(--primary-dark); }
        .users-management {
            background: #FEF6EA;
            padding: 18px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .user-item {
            background: white;
            padding: 14px;
            border-radius: 10px;
            margin-top: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid var(--border);
        }
        .delete-user-btn {
            background: #fff;
            color: #EB5757;
            border: 1px solid var(--border);
            padding: 5px 15px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9em;
            font-family: inherit;
        }
        .delete-user-btn:hover { background: #FDECEC; }
        .status-message {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            padding: 14px 28px;
            border-radius: 10px;
            color: white;
            font-weight: bold;
            z-index: 1001;
            display: none;
        }
        .status-success { background: #2ECC71; }
        .status-error { background: #EB5757; }
        .edit-fields { display: grid; gap: 14px; margin-bottom: 14px; }
        .edit-fields label { display: block; font-weight: 600; margin-bottom: 5px; color: var(--ink); font-size: 0.9em; }
        .edit-fields input, .edit-fields textarea {
            width: 100%;
            padding: 10px;
            border: 1.5px solid var(--border);
            border-radius: 8px;
            font-family: inherit;
        }
        .edit-fields textarea { min-height: 80px; resize: vertical; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-right">
                <div class="header-brand">
                    <div class="app-icon">⊞</div>
                    <div>
                        <div class="app-title">مدیریت داشبوردها</div>
                        <div class="app-status"><span class="dot"></span>آنلاین</div>
                    </div>
                </div>
                <div class="header-user">
                    <div class="avatar">{{ user_name[0] if user_name else 'K' }}</div>
                    <div>
                        <div class="user-name">{{ user_name }}</div>
                        <div class="user-role">{{ user_role }}</div>
                    </div>
                </div>
            </div>
            <div class="header-actions">
                {% if is_admin %}
                <button class="btn btn-primary" onclick="openUploadModal()">➕ داشبورد جدید</button>
                <button class="btn btn-outline" onclick="openManageModal()">مدیریت دسترسی</button>
                {% endif %}
                <button class="btn btn-outline-danger" onclick="logout()">خروج</button>
            </div>
        </div>

        <div class="page-heading">
            <h2>نمای کلی</h2>
            <p>مدیریت و اجرای سریع داشبوردهای سازمان</p>
        </div>

        <div class="search-bar">
            <span>🔍</span>
            <input type="text" id="dashboardSearch" placeholder="جستجو در داشبوردها..." oninput="renderDashboards()">
        </div>

        <div class="section-title">آمار کلی</div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-text">
                    <div class="stat-value" id="totalRuns">0</div>
                    <div class="stat-label">مجموع اجراها</div>
                </div>
                <div class="stat-icon orange">▶️</div>
            </div>
            <div class="stat-card">
                <div class="stat-text">
                    <div class="stat-value" id="accessibleDashboards">0</div>
                    <div class="stat-label">داشبوردهای قابل دسترس</div>
                </div>
                <div class="stat-icon green">🛡️</div>
            </div>
            <div class="stat-card">
                <div class="stat-text">
                    <div class="stat-value" id="totalDashboards">0</div>
                    <div class="stat-label">مجموع داشبوردها</div>
                </div>
                <div class="stat-icon purple">⊞</div>
            </div>
        </div>

        <div class="filter-row"><span>▽</span><span>همه داشبوردها</span></div>
        <div class="section-title">داشبوردهای شما</div>
        <div id="dashboardsArea"></div>
    </div>
    <div id="manageModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>⚙️ مدیریت دسترسی</h2>
                <span class="close-modal" onclick="closeManageModal()">&times;</span>
            </div>
            <div id="manageContent"></div>
            <button class="save-button" onclick="savePermissions()">💾 ذخیره</button>
        </div>
    </div>
    
    <div id="uploadModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>➕ افزودن داشبورد جدید</h2>
                <span class="close-modal" onclick="closeUploadModal()">&times;</span>
            </div>
            <div style="padding:20px">
                <div class="edit-fields">
                    <div>
                        <label>📁 انتخاب فایل EXE:</label>
                        <input type="file" id="dashboardFile" accept=".exe" style="width:100%;padding:10px;border:2px dashed #ddd;border-radius:8px">
                    </div>
                    <div>
                        <label>📝 عنوان داشبورد:</label>
                        <input type="text" id="uploadTitle" placeholder="مثال: داشبورد فروش ماهانه">
                    </div>
                    <div>
                        <label>📄 توضیحات:</label>
                        <textarea id="uploadDescription" placeholder="توضیحات کامل درباره این داشبورد..."></textarea>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
                        <div>
                            <label>📁 دسته‌بندی:</label>
                            <input type="text" id="uploadCategory" placeholder="عمومی" value="عمومی">
                        </div>
                        <div>
                            <label>🎨 آیکون (ایموجی):</label>
                            <input type="text" id="uploadIcon" placeholder="📊" value="📊" maxlength="2">
                        </div>
                    </div>
                </div>
                <button class="save-button" onclick="uploadDashboard()" style="width:100%;margin-top:20px">
                    📤 آپلود و رمزنگاری
                </button>
                <div id="uploadProgress" style="display:none;margin-top:15px;padding:15px;background:#e3f2fd;border-radius:8px;text-align:center">
                    <div style="font-weight:bold;margin-bottom:10px">در حال آپلود...</div>
                    <div style="background:#ddd;height:8px;border-radius:4px;overflow:hidden">
                        <div id="progressBar" style="background:#2196f3;height:100%;width:0%;transition:width 0.3s"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="status-message" id="statusMessage"></div>
    <script>
        let dashboards={},stats={},users={};
        const runningDashboards = new Set();
        
        async function loadData(){
            try{
                const r=await fetch('/api/dashboards');
                const d=await r.json();
                dashboards=d.dashboards;
                stats=d.stats;
                
                renderDashboards();
            }catch(e){showStatus('خطا در بارگذاری','error');}
        }
        const FA_DIGITS=['۰','۱','۲','۳','۴','۵','۶','۷','۸','۹'];
        function toFa(n){ return String(n).replace(/[0-9]/g,d=>FA_DIGITS[d]); }
        const ACCENTS=['accent-purple','accent-cyan','accent-green','accent-orange'];

        function renderDashboards(){
            const area=document.getElementById('dashboardsArea');
            const searchEl=document.getElementById('dashboardSearch');
            const q=(searchEl?searchEl.value:'').trim().toLowerCase();
            const entries=Object.entries(dashboards).filter(([key,dash])=>{
                if(!q) return true;
                return (dash.name||'').toLowerCase().includes(q) || (dash.description||'').toLowerCase().includes(q) || (dash.category||'').toLowerCase().includes(q);
            });

            let totalRuns=0,accessibleCount=0;
            for(const[key,dash]of Object.entries(dashboards)){
                const st=stats[key]||{count:0,last_run:null};
                totalRuns+=st.count;
                if(dash.has_access)accessibleCount++;
            }

            if(Object.keys(dashboards).length===0){
                area.innerHTML='<div style="background:white;border:1px solid var(--border);border-radius:16px;padding:60px;text-align:center;"><div style="font-size:5em">📂</div><h2>هیچ داشبوردی یافت نشد</h2><p style="color:var(--muted);margin-top:15px">ماژول داشبورد را در پوشه <strong>dashboards</strong> اضافه کنید</p></div>';
            }else if(entries.length===0){
                area.innerHTML='<div style="background:white;border:1px solid var(--border);border-radius:16px;padding:60px;text-align:center;"><div style="font-size:4em">🔍</div><h2>نتیجه‌ای یافت نشد</h2><p style="color:var(--muted);margin-top:15px">عبارت جستجوی دیگری را امتحان کنید</p></div>';
            }else{
                let html='<div class="dashboard-grid">';
                let i=0;
                for(const[key,dash]of entries){
                    const st=stats[key]||{count:0,last_run:null};
                    const hasAccess=dash.has_access;
                    const accent=ACCENTS[i%ACCENTS.length]; i++;
                    html+=`<div class="dashboard-card ${hasAccess?'':'no-access'}">
                        ${!hasAccess?'<div class="no-access-overlay">🔒 دسترسی محدود</div>':''}
                        <div class="card-top">
                            <div class="card-badges">
                                <span class="badge badge-run">${toFa(st.count)} بار</span>
                                <span class="badge badge-cat">${dash.category||'عمومی'}</span>
                            </div>
                            <div class="card-icon">${dash.icon||'📊'}</div>
                        </div>
                        <div class="dashboard-title">${dash.name}</div>
                        <div class="dashboard-description">${dash.description}</div>
                        <hr class="card-divider">
                        <div class="card-footer">
                            <div class="footer-meta">
                                ${dash.link?`<a href="${dash.link}" target="_blank" class="card-link">🔗 لینک مرتبط</a>`:'<span class="card-link" style="color:var(--muted)">بدون لینک</span>'}
                                <div class="last-run">آخرین اجرا: ${st.last_run?toFa(st.last_run):'هنوز اجرا نشده'}</div>
                            </div>
                            <button class="launch-button ${accent}" ${hasAccess?`onclick="launchDashboard('${key}')"`:'disabled'}>
                                ${hasAccess?'اجرا →':'🔒 دسترسی ندارید'}
                            </button>
                        </div>
                    </div>`;
                }
                html+='</div>';
                area.innerHTML=html;
            }
            document.getElementById('totalDashboards').textContent=toFa(Object.keys(dashboards).length);
            document.getElementById('accessibleDashboards').textContent=toFa(accessibleCount);
            document.getElementById('totalRuns').textContent=toFa(totalRuns);
        }
        async function launchDashboard(key){
            const w=window.open('about:blank','_blank');
            try{
                const r=await fetch('/api/launch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({dashboard_id:key})});
                const res=await r.json();
                if(res.success){
                    if(w){w.location.href=res.url;}else{window.location.href=res.url;}
                    setTimeout(()=>loadData(),500);
                }else{
                    if(w)w.close();
                    showStatus('خطا: '+res.error,'error');
                }
            }catch(e){
                if(w)w.close();
                showStatus('خطا در اجرا','error');
            }
        }
        
        async function stopDashboard(key){
            if(!confirm('آیا از توقف این داشبورد اطمینان دارید؟'))return;
            const btn=event.target;
            btn.disabled=true;
            btn.textContent='⏳ در حال توقف...';
            try{
                const r=await fetch('/api/stop',{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({dashboard_id:key})
                });
                const res=await r.json();
                if(res.success){
                    runningDashboards.delete(key);
                    btn.textContent='▶️ اجرا';
                    btn.classList.remove('running');
                    btn.disabled=false;
                    showStatus('✅ داشبورد با موفقیت متوقف شد','success');
                    setTimeout(()=>loadData(),500);
                }else{
                    showStatus('❌ خطا: '+res.error,'error');
                    btn.disabled=false;
                    btn.textContent='⏹️ توقف';
                }
            }catch(e){
                showStatus('❌ خطا در توقف','error');
                btn.disabled=false;
                btn.textContent='⏹️ توقف';
            }
        }
        async function openManageModal(){
            document.getElementById('manageModal').style.display='block';
            try{
                const r=await fetch('/api/manage/permissions');
                const d=await r.json();
                users=d.users;
                dashboards=d.dashboards;
                renderManageContent();
            }catch(e){showStatus('خطا','error');}
        }
        function closeManageModal(){
            document.getElementById('manageModal').style.display='none';
        }
        
        function openUploadModal(){
            document.getElementById('uploadModal').style.display='block';
        }
        
        function closeUploadModal(){
            document.getElementById('uploadModal').style.display='none';
            document.getElementById('dashboardFile').value='';
            document.getElementById('uploadTitle').value='';
            document.getElementById('uploadDescription').value='';
            document.getElementById('uploadCategory').value='عمومی';
            document.getElementById('uploadIcon').value='📊';
            document.getElementById('uploadProgress').style.display='none';
        }
        
        async function uploadDashboard(){
            const fileInput=document.getElementById('dashboardFile');
            const title=document.getElementById('uploadTitle').value.trim();
            const description=document.getElementById('uploadDescription').value.trim();
            const category=document.getElementById('uploadCategory').value.trim();
            const icon=document.getElementById('uploadIcon').value.trim();
            
            if(!fileInput.files[0]){
                showStatus('❌ لطفا یک فایل EXE انتخاب کنید','error');
                return;
            }
            
            if(!title){
                showStatus('❌ لطفا عنوان داشبورد را وارد کنید','error');
                return;
            }
            
            const file=fileInput.files[0];
            if(!file.name.endsWith('.exe')){
                showStatus('❌ فقط فایل‌های EXE مجاز هستند','error');
                return;
            }
            
            const formData=new FormData();
            formData.append('file',file);
            formData.append('title',title);
            formData.append('description',description);
            formData.append('category',category);
            formData.append('icon',icon);
            
            document.getElementById('uploadProgress').style.display='block';
            document.getElementById('progressBar').style.width='30%';
            
            try{
                const r=await fetch('/api/upload-dashboard',{
                    method:'POST',
                    body:formData
                });
                
                document.getElementById('progressBar').style.width='70%';
                const res=await r.json();
                document.getElementById('progressBar').style.width='100%';
                
                if(res.success){
                    showStatus('✅ داشبورد با موفقیت اضافه و رمزنگاری شد!','success');
                    closeUploadModal();
                    setTimeout(()=>loadData(),1000);
                }else{
                    showStatus('❌ '+res.error,'error');
                    document.getElementById('uploadProgress').style.display='none';
                }
            }catch(e){
                showStatus('❌ خطا در آپلود فایل','error');
                document.getElementById('uploadProgress').style.display='none';
            }
        }
        function renderManageContent(){
            let html='';
            html+=`<div class="add-user-section">
                <h3>➕ افزودن کاربر جدید</h3>
                <div class="add-user-form">
                    <input type="text" id="newUsername" placeholder="نام کاربری (انگلیسی)">
                    <input type="password" id="newPassword" placeholder="رمز عبور">
                    <input type="text" id="newName" placeholder="نام نمایشی (فارسی)">
                    <button class="add-user-btn" onclick="addNewUser()">افزودن کاربر</button>
                </div>
            </div>`;
            html+=`<div class="users-management">
                <h3>👥 کاربران موجود</h3>`;
            for(const[username,user]of Object.entries(users)){
                if(user.role!=='admin'){
                    html+=`<div class="user-item">
                        <div><strong>${user.name}</strong> (${username})</div>
                        <button class="delete-user-btn" onclick="deleteUser('${username}')">🗑️ حذف</button>
                    </div>`;
                }
            }
            html+=`</div>`;
            for(const[key,dash]of Object.entries(dashboards)){
                html+=`<div class="dashboard-item">
                    <h3>${dash.icon||'📊'} ${dash.name}</h3>
                    <div class="edit-fields">
                        <div>
                            <label>عنوان نمایشی:</label>
                            <input type="text" value="${dash.title||dash.name}" id="title_${key}" placeholder="عنوان داشبورد">
                        </div>
                        <div>
                            <label>توضیحات:</label>
                            <textarea id="desc_${key}" placeholder="توضیحات کامل درباره این داشبورد">${dash.description||''}</textarea>
                        </div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
                            <div>
                                <label>دسته‌بندی:</label>
                                <input type="text" value="${dash.category||'عمومی'}" id="category_${key}">
                            </div>
                            <div>
                                <label>آیکون:</label>
                                <input type="text" value="${dash.icon||'📊'}" id="icon_${key}" style="width:100%">
                            </div>
                        </div>
                        <div>
                            <label>🔗 لینک مرتبط (اختیاری):</label>
                            <input type="url" value="${dash.link||''}" id="link_${key}" placeholder="https://example.com/docs">
                        </div>
                    </div>
                    <div><strong>کاربران مجاز:</strong>
                        <div class="permission-grid">`;
                for(const[username,user]of Object.entries(users)){
                    if(user.role!=='admin'){
                        const isAllowed=dash.allowed_users.includes(username);
                        html+=`<label style="display:flex;align-items:center;gap:5px">
                            <input type="checkbox" data-dashboard="${key}" data-user="${username}" ${isAllowed?'checked':''}>
                            <span>${user.name}</span>
                        </label>`;
                    }
                }
                html+=`</div></div>
                    <div style="margin-top:15px;text-align:left">
                        <button class="delete-user-btn" onclick="deleteDashboard('${key}')" style="background:#f44336">
                            🗑️ حذف این داشبورد
                        </button>
                    </div>
                </div>`;
            }
            document.getElementById('manageContent').innerHTML=html;
        }
        async function savePermissions(){
            const permissions={},categories={},icons={},titles={},descriptions={},links={};
            for(const[key,dash]of Object.entries(dashboards)){
                permissions[key]=[];
                const titleInput=document.getElementById(`title_${key}`);
                const descInput=document.getElementById(`desc_${key}`);
                const catInput=document.getElementById(`category_${key}`);
                const iconInput=document.getElementById(`icon_${key}`);
                const linkInput=document.getElementById(`link_${key}`);
                if(titleInput)titles[key]=titleInput.value;
                if(descInput)descriptions[key]=descInput.value;
                if(catInput)categories[key]=catInput.value;
                if(iconInput)icons[key]=iconInput.value;
                if(linkInput)links[key]=linkInput.value;
                const checkboxes=document.querySelectorAll(`input[data-dashboard="${key}"]`);
                checkboxes.forEach(cb=>{
                    if(cb.checked)permissions[key].push(cb.dataset.user);
                });
            }
            try{
                const r=await fetch('/api/manage/permissions',{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({permissions,categories,icons,titles,descriptions,links})
                });
                const res=await r.json();
                if(res.success){
                    showStatus('تغییرات ذخیره شد! ✅','success');
                    closeManageModal();
                    loadData();
                }else{
                    showStatus('خطا در ذخیره','error');
                }
           }catch(e){showStatus('خطا','error');}
        }
        
        async function addNewUser(){
            const username=document.getElementById('newUsername').value.trim();
            const password=document.getElementById('newPassword').value;
            const name=document.getElementById('newName').value.trim();
            
            if(!username || !password || !name){
                showStatus('❌ لطفا تمام فیلدها را پر کنید','error');
                return;
            }
            
            if(!/^[a-zA-Z0-9_]+$/.test(username)){
                showStatus('❌ نام کاربری فقط باید شامل حروف انگلیسی، اعداد و _ باشد','error');
                return;
            }
            
            try{
                const r=await fetch('/api/manage/users',{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({action:'add',username,password,name})
                });
                const res=await r.json();
                if(res.success){
                    showStatus('✅ کاربر با موفقیت اضافه شد!','success');
                    document.getElementById('newUsername').value='';
                    document.getElementById('newPassword').value='';
                    document.getElementById('newName').value='';
                    openManageModal();
                }else{
                    showStatus('❌ '+res.error,'error');
                }
            }catch(e){showStatus('❌ خطا در افزودن کاربر','error');}
        }
        
        async function deleteUser(username){
            if(!confirm(`آیا از حذف کاربر "${username}" اطمینان دارید؟`))return;
            
            try{
                const r=await fetch('/api/manage/users',{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({action:'delete',username})
                });
                const res=await r.json();
                if(res.success){
                    showStatus('✅ کاربر با موفقیت حذف شد!','success');
                    openManageModal();
                }else{
                    showStatus('❌ '+res.error,'error');
                }
           }catch(e){showStatus('❌ خطا در حذف کاربر','error');}
        }
        
        async function deleteDashboard(key){
            const dashName = dashboards[key]?.name || key;
            if(!confirm(`⚠️ آیا از حذف داشبورد "${dashName}" اطمینان دارید؟\n\nاین عملیات قابل بازگشت نیست!`))return;
            
            try{
                const r=await fetch('/api/manage/dashboards',{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({action:'delete',dashboard_id:key})
                });
                const res=await r.json();
                if(res.success){
                    showStatus('✅ داشبورد با موفقیت حذف شد!','success');
                    closeManageModal();
                    loadData();
                }else{
                    showStatus('❌ '+res.error,'error');
                }
            }catch(e){showStatus('❌ خطا در حذف داشبورد','error');}
        }
        async function logout(){
            await fetch('/api/logout',{method:'POST'});
            window.location.href='/login';
        }
        function showStatus(msg,type){
            const div=document.getElementById('statusMessage');
            div.textContent=msg;
            div.className=`status-message status-${type}`;
            div.style.display='block';
            setTimeout(()=>div.style.display='none',3000);
        }
        window.onclick=function(e){
            const manageModal=document.getElementById('manageModal');
            const uploadModal=document.getElementById('uploadModal');
            if(e.target==manageModal)closeManageModal();
            if(e.target==uploadModal)closeUploadModal();
        }
        loadData();
        setInterval(loadData,30000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    user = load_users().get(username)
    if not user:
        session.pop('user', None)
        return redirect(url_for('login'))
    user_role = 'مدیر سیستم' if user.get('role') == 'admin' else 'کاربر'
    # مدیریت کاربران/دسترسی‌ها در این نسخه از طریق فایل‌ها و متغیرهای محیطی انجام می‌شود
    return render_template_string(MAIN_TEMPLATE, user_name=user.get('name', username), user_role=user_role,
                                  username=username, is_admin=False)


@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('index'))
    return render_template_string(LOGIN_TEMPLATE)


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', ''))
    user = load_users().get(username)
    if user and hmac.compare_digest(user.get('password_sha256', ''), hash_password(password)):
        session['user'] = username
        return jsonify({'success': True})
    time.sleep(0.5)
    return jsonify({'success': False, 'error': 'نام کاربری یا رمز عبور اشتباه است'}), 401


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({'success': True})


@app.route('/api/dashboards')
def get_dashboards():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    username = session['user']
    out = {}
    for key, meta in DASHBOARDS.items():
        out[key] = {'name': meta['name'], 'description': meta.get('description', ''),
                    'category': meta.get('category', 'عمومی'), 'icon': meta.get('icon', '📊'),
                    'link': '', 'has_access': user_can_access_dashboard(username, key)}
    return jsonify({'dashboards': out, 'stats': load_stats()})


@app.route('/api/launch', methods=['POST'])
def launch_dashboard():
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    key = (request.get_json(silent=True) or {}).get('dashboard_id')
    if key not in DASHBOARDS:
        return jsonify({'success': False, 'error': 'داشبورد یافت نشد'}), 404
    if not user_can_access_dashboard(session['user'], key):
        return jsonify({'success': False, 'error': 'شما به این داشبورد دسترسی ندارید'}), 403
    stats = load_stats()
    entry = stats.setdefault(key, {'count': 0, 'last_run': None})
    entry['count'] += 1
    entry['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_stats()
    return jsonify({'success': True, 'url': f'/d/{key}/'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
