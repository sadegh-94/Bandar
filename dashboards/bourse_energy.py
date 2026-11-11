#!/usr/bin/env python
# coding: utf-8

# In[2]:


#!/usr/bin/env python
# coding: utf-8

# In[3]:


#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc, html, Input, Output, callback, State, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import threading
import webbrowser
import time
import sys
import os
import io
import traceback
import multiprocessing
from datetime import datetime
from core import server
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# تنظیمات اولیه


# =============================================================================

META = {
    'name': 'bourse_energy',
    'description': 'تحلیل عملکرد پتروشیمی بندرامام در بورس انرژی',
    'category': 'بورس انرژی',
    'icon': '📈',
    'allowed_users': [],
}

app = dash.Dash(__name__, server=server, url_base_pathname='/d/bourse_energy/')
app.title = "داشبورد تحلیلی پتروشیمی بندرامام در بورس انرژی"

# =============================================================================
# استایل CSS جدید با تم روشن و رنگ‌های زیبا
# =============================================================================

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            :root {
                --primary: #2f5fdb;
                --primary-dark: #1e3fa8;
                --primary-light: #eaf0fd;
                --success: #10b981;
                --success-light: #e7f9f1;
                --warning: #f59e0b;
                --warning-light: #fef5e7;
                --danger: #ef4444;
                --danger-light: #fdecec;
                --ink: #1f2937;
                --muted: #8792a2;
                --border: #eef1f6;
                --bg: #f3f5fa;
            }

            body {
                font-family: 'Vazir', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: var(--bg);
                margin: 0;
                padding: 0;
                direction: rtl;
                line-height: 1.6;
                color: var(--ink);
                min-height: 100vh;
            }

            .loading-container {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: linear-gradient(135deg, #2f5fdb 0%, #1e3fa8 100%);
                color: white;
                text-align: center;
                position: relative;
                overflow: hidden;
            }

            .loading-title {
                font-size: 2.4em;
                margin-bottom: 20px;
                font-weight: bold;
                text-shadow: 0 2px 10px rgba(0,0,0,0.2);
                color: white;
            }

            .loading-subtitle {
                font-size: 1.2em;
                margin-bottom: 40px;
                opacity: 0.9;
                color: white;
            }

            .progress-container {
                width: 500px;
                max-width: 85vw;
                height: 10px;
                background-color: rgba(255, 255, 255, 0.25);
                border-radius: 10px;
                margin: 30px 0;
                overflow: hidden;
                position: relative;
            }

            .progress-bar {
                height: 100%;
                background: #ffffff;
                border-radius: 10px;
                transition: width 0.5s ease;
                position: relative;
            }

            .dashboard-container {
                max-width: 1600px;
                margin: 0 auto;
                padding: 24px;
                font-family: 'Vazir', Tahoma, sans-serif;
            }

            /* ---------- Header ---------- */
            .header {
                background: transparent;
                padding: 4px 4px 20px 4px;
                margin-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                flex-wrap: wrap;
                gap: 16px;
            }

            .header-titles h1 {
                font-size: 1.7em;
                font-weight: bold;
                color: var(--ink);
                margin-bottom: 6px;
            }

            .header-titles p {
                color: var(--muted);
                font-size: 0.95em;
            }

            .header-actions {
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .header-chip {
                background: #ffffff;
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 10px 16px;
                display: flex;
                align-items: center;
                gap: 8px;
                color: var(--ink);
                font-size: 0.9em;
                box-shadow: 0 2px 8px rgba(20, 30, 60, 0.04);
            }

            .header-icon-btn {
                width: 42px;
                height: 42px;
                border-radius: 12px;
                background: #ffffff;
                border: 1px solid var(--border);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.1em;
                box-shadow: 0 2px 8px rgba(20, 30, 60, 0.04);
            }

            /* ---------- Insight banner ---------- */
            .insight-banner {
                background: linear-gradient(135deg, #2f5fdb 0%, #3f6fe0 100%);
                border-radius: 18px;
                padding: 22px 28px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 20px;
                margin-bottom: 24px;
                flex-wrap: wrap;
                color: white;
                box-shadow: 0 12px 28px rgba(47, 95, 219, 0.25);
            }

            .insight-banner-text {
                display: flex;
                align-items: flex-start;
                gap: 16px;
            }

            .insight-banner-icon {
                width: 44px;
                height: 44px;
                min-width: 44px;
                border-radius: 12px;
                background: rgba(255,255,255,0.18);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.3em;
            }

            .insight-banner-title {
                font-weight: bold;
                font-size: 1.05em;
                margin-bottom: 4px;
            }

            .insight-banner-desc {
                font-size: 0.92em;
                opacity: 0.92;
                max-width: 720px;
            }

            .insight-download-btn {
                background: #ffffff;
                color: var(--primary);
                border: none;
                padding: 12px 22px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 0.92em;
                cursor: pointer;
                white-space: nowrap;
                transition: all 0.2s ease;
            }

            .insight-download-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 18px rgba(0,0,0,0.15);
            }

            /* ---------- KPI cards ---------- */
            .grid-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 18px;
                margin-bottom: 24px;
            }

            .stat-card {
                background: #ffffff;
                color: var(--ink);
                padding: 20px;
                border-radius: 16px;
                box-shadow: 0 4px 16px rgba(20, 30, 60, 0.05);
                border: 1px solid var(--border);
                transition: all 0.25s ease;
                position: relative;
            }

            .stat-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 24px rgba(20, 30, 60, 0.1);
            }

            .stat-card-top {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 14px;
            }

            .stat-badge {
                font-size: 0.78em;
                font-weight: bold;
                padding: 4px 10px;
                border-radius: 20px;
                background: var(--primary-light);
                color: var(--primary);
            }

            .stat-badge.positive { background: var(--success-light); color: var(--success); }
            .stat-badge.negative { background: var(--danger-light); color: var(--danger); }
            .stat-badge.neutral  { background: var(--warning-light); color: var(--warning); }

            .stat-icon {
                width: 38px;
                height: 38px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.05em;
                background: var(--primary-light);
                color: var(--primary);
            }

            .stat-value {
                font-size: 1.9em;
                font-weight: bold;
                margin-bottom: 6px;
                color: var(--ink);
            }

            .stat-label {
                font-size: 0.88em;
                color: var(--muted);
                margin-bottom: 8px;
            }

            .stat-trend {
                font-size: 0.82em;
                padding: 4px 10px;
                background: var(--primary-light);
                color: var(--primary);
                border-radius: 20px;
                display: inline-block;
            }

            .company-highlight {
                border: 1px solid var(--primary);
                background: linear-gradient(180deg, #ffffff 0%, var(--primary-light) 260%);
            }

            /* ---------- Filters ---------- */
            .filter-card-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .filter-clear-btn {
                background: transparent;
                border: none;
                color: var(--primary);
                font-weight: bold;
                font-size: 0.88em;
                cursor: pointer;
            }

            .filter-row {
                display: flex;
                gap: 16px;
                margin-bottom: 4px;
                flex-wrap: wrap;
            }

            .filter-group {
                flex: 1;
                min-width: 190px;
            }

            .filter-label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: var(--ink);
                font-size: 0.9em;
            }

            .dropdown {
                width: 100%;
                font-size: 0.92em;
            }

            .Select-control, .dash-dropdown .Select-control {
                border-radius: 12px !important;
                border: 1px solid var(--border) !important;
                min-height: 44px !important;
            }

            /* ---------- Tabs ---------- */
            .tab-buttons {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }

            .tab-btn {
                padding: 11px 22px;
                text-align: center;
                background: #ffffff;
                border: 1px solid var(--border);
                color: var(--muted);
                cursor: pointer;
                border-radius: 24px;
                transition: all 0.2s ease;
                font-weight: bold;
                font-size: 0.92em;
            }

            .tab-btn.active {
                background: var(--primary);
                color: white;
                border-color: var(--primary);
                box-shadow: 0 6px 16px rgba(47, 95, 219, 0.28);
            }

            .tab-btn:hover:not(.active) {
                background: var(--primary-light);
                color: var(--primary);
            }

            /* ---------- Cards ---------- */
            .card {
                background: #ffffff;
                border-radius: 18px;
                box-shadow: 0 4px 16px rgba(20, 30, 60, 0.05);
                margin-bottom: 22px;
                overflow: hidden;
                border: 1px solid var(--border);
            }

            .card-header {
                background: transparent;
                color: var(--ink);
                padding: 20px 24px 8px 24px;
                font-size: 1.05em;
                font-weight: bold;
                border-bottom: none;
            }

            .card-subtitle {
                padding: 0 24px 12px 24px;
                color: var(--muted);
                font-size: 0.86em;
                margin-top: -6px;
            }

            .card-body {
                padding: 8px 24px 24px 24px;
                background: transparent;
            }

            /* ---------- Insight callouts under charts ---------- */
            .insight-card {
                background: var(--primary-light);
                border-radius: 14px;
                padding: 16px 20px;
                margin-bottom: 12px;
                border-right: 4px solid var(--primary);
            }

            .insight-title {
                font-size: 0.95em;
                font-weight: bold;
                color: var(--ink);
            }

            .callout {
                border-radius: 14px;
                padding: 16px 20px;
                text-align: center;
                font-weight: bold;
                font-size: 0.92em;
                margin-top: 16px;
            }

            .callout.success { background: var(--success-light); color: #0a7a56; }
            .callout.warning  { background: var(--warning-light); color: #a3660a; }
            .callout.danger   { background: var(--danger-light); color: #b03030; }
            .callout.info     { background: var(--primary-light); color: var(--primary-dark); }

            /* ---------- Table ---------- */
            .comparison-table {
                width: 100%;
                border-collapse: collapse;
                background: #ffffff;
                border-radius: 14px;
                overflow: hidden;
            }

            .comparison-table th {
                background: var(--primary);
                padding: 14px;
                text-align: center;
                color: white;
                font-weight: bold;
            }

            .comparison-table td {
                padding: 12px 14px;
                text-align: center;
                border-bottom: 1px solid var(--border);
                color: var(--ink);
            }

            .comparison-table tr:hover {
                background: var(--primary-light);
            }

            .step {
                margin: 10px 0;
                padding: 12px 15px;
                border-radius: 10px;
                background: rgba(255,255,255,0.15);
                transition: all 0.3s ease;
                color: white;
                border: 1px solid rgba(255,255,255,0.1);
            }

            .step.active {
                background: rgba(255,255,255,0.28);
                border-right: 4px solid #ffffff;
                color: white;
            }

            .progress-text {
                color: white;
                font-size: 1.1em;
                margin-top: 10px;
            }

            .trend-positive {
                color: var(--success);
                font-weight: bold;
            }

            .trend-negative {
                color: var(--danger);
                font-weight: bold;
            }

            .trend-neutral {
                color: var(--warning);
                font-weight: bold;
            }
        </style>
        <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/font-face.css" rel="stylesheet">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# =============================================================================
# تنظیمات پیشرفت
# =============================================================================

LOADING_STEPS = [
    "بارگذاری داده‌های پتروشیمی بندرامام...",
    "تحلیل عملکرد در بورس انرژی...",
    "محاسبه شاخص‌های رقابتی...",
    "بررسی ارتباط با بازار انرژی...",
    "تکمیل تحلیل‌های تخصصی..."
]

PROGRESS_INTERVAL = 400
PROGRESS_STEP = 2

# =============================================================================
# لی‌اوت اصلی متمرکز بر بندرامام
# =============================================================================

app.layout = html.Div([
    html.Div(id="loading-screen", children=[
        html.Div(className="loading-container", children=[
            html.H1("🏭 پتروشیمی بندرامام - تحلیل بورس انرژی", className="loading-title"),
            html.P("در حال تحلیل تخصصی عملکرد در بازار انرژی...", className="loading-subtitle"),
            
            html.Div(className="progress-container", children=[
                html.Div(id="progress-bar", className="progress-bar", style={'width': '0%'})
            ]),
            
            html.Div(id="progress-text", className="progress-text", children="0%"),
            
            html.Div(id="loading-steps", className="loading-steps", children=[
                html.Div(step, className="step", id=f"step-{i}") 
                for i, step in enumerate(LOADING_STEPS)
            ])
        ])
    ]),
    
    html.Div(id="dashboard-content", style={'display': 'none'}),
    
    dcc.Interval(
        id='progress-interval',
        interval=PROGRESS_INTERVAL,
        n_intervals=0,
        max_intervals=int(100/PROGRESS_STEP)
    ),
    
    dcc.Download(id="download-excel"),
    dcc.Store(id='data-store')
])

# =============================================================================
# 🔧 تحلیل تخصصی پتروشیمی بندرامام
# =============================================================================

def load_bandar_imam_analysis():
    """تحلیل تخصصی داده‌های پتروشیمی بندرامام در بورس انرژی"""
    # مسیر فایل داده: ۱) متغیر محیطی ENB_XLSX_PATH  ۲) data/enb.xlsx کنار پروژه  ۳) مسیر قدیمی درایو P
    _repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.environ.get('ENB_XLSX_PATH') or os.path.join(_repo_root, 'data', 'enb.xlsx')
    if not os.path.exists(excel_path) and os.path.exists(r'P:\Programs\Report Analyst\bours_energy_report\enb.xlsx'):
        excel_path = r'P:\Programs\Report Analyst\bours_energy_report\enb.xlsx'
    try:
        
        # خواندن داده‌ها
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"فایل داده (data/enb.xlsx) پیدا نشد؛ داده نمونه نمایش داده می‌شود.")
        
        en_bours = pd.read_excel(excel_path)
        en_bours.columns = en_bours.columns.str.strip()
        
        # بررسی وجود ستون‌های ضروری قبل از پردازش
        required_columns = ['تاریخ', 'عرضه کننده', 'زیرگروه', 'نرخ تبدیل ارز',
                             'متوسط قيمت معامله', 'حجم کل معامله شده بر حسب تن']
        missing_columns = [c for c in required_columns if c not in en_bours.columns]
        if missing_columns:
            raise KeyError(f"ستون‌های زیر در فایل enb.xlsx پیدا نشدند: {missing_columns}. "
                            f"ستون‌های موجود: {list(en_bours.columns)}")
        
        # حذف ردیف‌های ناقص که ستون‌های کلیدی (عرضه‌کننده/زیرگروه/تاریخ) در آن‌ها خالی است
        # این ردیف‌ها باعث خطای مقایسه نوع داده (float vs str) در مرتب‌سازی و گروه‌بندی می‌شوند
        rows_before = len(en_bours)
        en_bours = en_bours.dropna(subset=['عرضه کننده', 'زیرگروه', 'تاریخ']).copy()
        en_bours['عرضه کننده'] = en_bours['عرضه کننده'].astype(str).str.strip()
        en_bours['زیرگروه'] = en_bours['زیرگروه'].astype(str).str.strip()
        rows_dropped = rows_before - len(en_bours)
        if rows_dropped > 0:
            print(f"هشدار: {rows_dropped} ردیف به دلیل خالی بودن عرضه‌کننده/زیرگروه/تاریخ نادیده گرفته شد.")
        
        # پردازش تاریخ
        en_bours[['سال', 'ماه', 'روز']] = en_bours['تاریخ'].astype(str).str.split('/', expand=True)
        en_bours['سال'] = pd.to_numeric(en_bours['سال'], errors='coerce').fillna(0).astype(int)
        en_bours['ماه'] = pd.to_numeric(en_bours['ماه'], errors='coerce').fillna(0).astype(int)
        
        # جداسازی داده‌های بندرامام
        bandar_imam_data = en_bours[en_bours["عرضه کننده"] == "شرکت پتروشیمی بندرامام"].copy()
        
        if bandar_imam_data.empty:
            suppliers_found = sorted(en_bours['عرضه کننده'].dropna().astype(str).unique().tolist())
            raise ValueError(
                "هیچ ردیفی با عرضه‌کننده «شرکت پتروشیمی بندرامام» در فایل enb.xlsx پیدا نشد. "
                f"نام عرضه‌کننده‌های موجود در فایل: {suppliers_found[:15]}"
                + (" ..." if len(suppliers_found) > 15 else "")
            )
        
        list_bandar_en = bandar_imam_data["زیرگروه"].unique().tolist()
        
        # داده‌های کل بازار برای مقایسه
        market_data = en_bours[en_bours["زیرگروه"].isin(list_bandar_en)].copy()
        
        # محاسبات مالی
        for df in [bandar_imam_data, market_data]:
            df["nerkh"] = df.apply(
                lambda row: row["نرخ تبدیل ارز"] * row["متوسط قيمت معامله"] / 1000
                            if row["نرخ تبدیل ارز"] != 1
                            else row["نرخ تبدیل ارز"] * row["متوسط قيمت معامله"],
                axis=1
            )
            df["درآمد"] = df["nerkh"] * df["حجم کل معامله شده بر حسب تن"]
        
        # تحلیل‌های تخصصی
        analysis_results = calculate_bandar_imam_metrics(bandar_imam_data, market_data)
        analytical_indices = calculate_analytical_indices(bandar_imam_data, market_data)
        analysis_results.update(analytical_indices)
        
        return {
            'bandar_imam': bandar_imam_data,
            'market_data': market_data,
            'analysis': analysis_results,
            'available_years': [{'label': 'همه سال‌ها', 'value': 'all'}] + 
                             [{'label': str(year), 'value': year} 
                              for year in sorted(bandar_imam_data['سال'].dropna().unique().tolist())],
            'available_months': [{'label': 'همه ماه‌ها', 'value': 'all'}] + 
                               [{'label': str(month), 'value': month} 
                                for month in sorted(bandar_imam_data['ماه'].dropna().unique().tolist())],
            'products': sorted(bandar_imam_data['زیرگروه'].dropna().astype(str).unique().tolist()),
            'competitors': sorted(market_data[market_data['عرضه کننده'] != 'شرکت پتروشیمی بندرامام']['عرضه کننده'].dropna().astype(str).unique().tolist()),
            'is_sample_data': False,
            'load_error': None,
            'source_path': excel_path
        }
        
    except Exception as e:
        error_message = f"{type(e).__name__}: {e}"
        full_trace = traceback.format_exc()
        print(f"خطا در تحلیل داده‌های بندرامام: {error_message}")
        print(full_trace)
        
        # نوشتن خطا در فایل لاگ کنار برنامه تا حتی در نسخه exe بدون کنسول هم قابل مشاهده باشد
        try:
            log_path = os.path.join(base_path, 'error_log.txt')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n[{datetime.now()}] خطا در خواندن {excel_path}\n")
                f.write(full_trace)
                f.write("\n" + "=" * 60 + "\n")
        except Exception:
            pass
        
        sample = create_bandar_sample_data()
        sample['is_sample_data'] = True
        sample['load_error'] = error_message
        sample['source_path'] = excel_path
        return sample

def calculate_bandar_imam_metrics(bandar_data, market_data):
    """محاسبه متریک‌های تخصصی پتروشیمی بندرامام"""
    
    # شاخص‌های کلی
    total_revenue = bandar_data['درآمد'].sum()
    total_volume = bandar_data['حجم کل معامله شده بر حسب تن'].sum()
    market_share = (bandar_data['حجم کل معامله شده بر حسب تن'].sum() / 
                   market_data['حجم کل معامله شده بر حسب تن'].sum() * 100)
    
    # شاخص‌های ماه آخر
    try:
        latest_year = bandar_data['سال'].max()
        latest_month_data = bandar_data[bandar_data['سال'] == latest_year]
        latest_month = latest_month_data['ماه'].max()
        current_month_data = bandar_data[
            (bandar_data['سال'] == latest_year) & 
            (bandar_data['ماه'] == latest_month)
        ]
        
        # داده‌های ماه قبل و سال قبل برای مقایسه
        previous_month_data = bandar_data[
            (bandar_data['سال'] == latest_year) & 
            (bandar_data['ماه'] == latest_month - 1)
        ] if latest_month > 1 else pd.DataFrame()
        
        previous_year_data = bandar_data[
            (bandar_data['سال'] == latest_year - 1) & 
            (bandar_data['ماه'] == latest_month)
        ]
        
        # محاسبات ماه آخر
        current_month_revenue = current_month_data['درآمد'].sum()
        current_month_volume = current_month_data['حجم کل معامله شده بر حسب تن'].sum()
        
        # محاسبه سهم بازار ماه آخر
        current_month_market = market_data[
            (market_data['سال'] == latest_year) & 
            (market_data['ماه'] == latest_month)
        ]
        total_market_volume_current = current_month_market['حجم کل معامله شده بر حسب تن'].sum()
        market_share_current_month = (current_month_volume / total_market_volume_current * 100) if total_market_volume_current > 0 else 0
        
        # محاسبات ماه قبل
        previous_month_revenue = previous_month_data['درآمد'].sum() if not previous_month_data.empty else 0
        previous_month_volume = previous_month_data['حجم کل معامله شده بر حسب تن'].sum() if not previous_month_data.empty else 0
        
        # محاسبات سال قبل
        previous_year_revenue = previous_year_data['درآمد'].sum() if not previous_year_data.empty else 0
        previous_year_volume = previous_year_data['حجم کل معامله شده بر حسب تن'].sum() if not previous_year_data.empty else 0
        
        # محاسبه تغییرات درآمد
        revenue_change_prev_month = current_month_revenue - previous_month_revenue
        revenue_change_prev_month_percent = (revenue_change_prev_month / previous_month_revenue * 100) if previous_month_revenue > 0 else 0
        
        revenue_change_prev_year = current_month_revenue - previous_year_revenue
        revenue_change_prev_year_percent = (revenue_change_prev_year / previous_year_revenue * 100) if previous_year_revenue > 0 else 0
        
        # محاسبه تغییرات حجم
        volume_change_prev_month = current_month_volume - previous_month_volume
        volume_change_prev_month_percent = (volume_change_prev_month / previous_month_volume * 100) if previous_month_volume > 0 else 0
        
        volume_change_prev_year = current_month_volume - previous_year_volume
        volume_change_prev_year_percent = (volume_change_prev_year / previous_year_volume * 100) if previous_year_volume > 0 else 0
        
        # محاسبه سهم بازار ماه قبل و سال قبل
        previous_month_market = market_data[
            (market_data['سال'] == latest_year) & 
            (market_data['ماه'] == latest_month - 1)
        ] if latest_month > 1 else pd.DataFrame()
        
        previous_year_market = market_data[
            (market_data['سال'] == latest_year - 1) & 
            (market_data['ماه'] == latest_month)
        ]
        
        total_market_volume_prev_month = previous_month_market['حجم کل معامله شده بر حسب تن'].sum() if not previous_month_market.empty else 0
        total_market_volume_prev_year = previous_year_market['حجم کل معامله شده بر حسب تن'].sum() if not previous_year_market.empty else 0
        
        market_share_prev_month = (previous_month_volume / total_market_volume_prev_month * 100) if total_market_volume_prev_month > 0 else 0
        market_share_prev_year = (previous_year_volume / total_market_volume_prev_year * 100) if total_market_volume_prev_year > 0 else 0
        
        # محاسبه تغییرات سهم بازار
        market_share_change_prev_month = market_share_current_month - market_share_prev_month
        market_share_change_prev_month_percent = (market_share_change_prev_month / market_share_prev_month * 100) if market_share_prev_month > 0 else 0
        
        market_share_change_prev_year = market_share_current_month - market_share_prev_year
        market_share_change_prev_year_percent = (market_share_change_prev_year / market_share_prev_year * 100) if market_share_prev_year > 0 else 0
        
        # محاسبه تغییرات تعداد محصولات
        current_products = current_month_data['زیرگروه'].nunique()
        previous_month_products = previous_month_data['زیرگروه'].nunique() if not previous_month_data.empty else 0
        previous_year_products = previous_year_data['زیرگروه'].nunique() if not previous_year_data.empty else 0
        
        products_change_prev_month = current_products - previous_month_products
        products_change_prev_year = current_products - previous_year_products
        
        # ---- اختلاف قیمت با میانگین بازار (ماه آخر) ----
        bandar_avg_price_month = current_month_data['nerkh'].mean() if not current_month_data.empty else 0
        market_avg_price_month = current_month_market['nerkh'].mean() if not current_month_market.empty else 0
        price_gap_percent = ((bandar_avg_price_month - market_avg_price_month) / market_avg_price_month * 100) \
            if market_avg_price_month else 0
        
        # ---- محصولی با بیشترین اختلاف قیمت نسبت به بازار (ماه آخر) ----
        top_gap_product = ''
        top_gap_value = 0
        try:
            product_price_gap = {}
            for product in current_month_data['زیرگروه'].unique():
                b_price = current_month_data[current_month_data['زیرگروه'] == product]['nerkh'].mean()
                m_price = current_month_market[current_month_market['زیرگروه'] == product]['nerkh'].mean()
                if m_price and m_price > 0:
                    product_price_gap[product] = (b_price - m_price) / m_price * 100
            if product_price_gap:
                top_gap_product = max(product_price_gap, key=lambda k: abs(product_price_gap[k]))
                top_gap_value = product_price_gap[top_gap_product]
        except Exception:
            pass
        
        # ---- رتبه رقابتی بر اساس درآمد در ماه آخر ----
        total_suppliers = current_month_market['عرضه کننده'].nunique() if not current_month_market.empty else 0
        company_rank = total_suppliers
        try:
            supplier_revenue = current_month_market.groupby('عرضه کننده')['درآمد'].sum()
            supplier_rank = supplier_revenue.rank(ascending=False, method='min')
            if 'شرکت پتروشیمی بندرامام' in supplier_rank.index:
                company_rank = int(supplier_rank.loc['شرکت پتروشیمی بندرامام'])
        except Exception:
            pass
        
    except Exception as e:
        print(f"خطا در محاسبات ماه آخر: {e}")
        current_month_revenue = 0
        current_month_volume = 0
        market_share_current_month = 0
        revenue_change_prev_month = 0
        revenue_change_prev_month_percent = 0
        revenue_change_prev_year = 0
        revenue_change_prev_year_percent = 0
        volume_change_prev_month = 0
        volume_change_prev_month_percent = 0
        volume_change_prev_year = 0
        volume_change_prev_year_percent = 0
        market_share_change_prev_month = 0
        market_share_change_prev_month_percent = 0
        market_share_change_prev_year = 0
        market_share_change_prev_year_percent = 0
        current_products = 0
        products_change_prev_month = 0
        products_change_prev_year = 0
        price_gap_percent = 0
        top_gap_product = ''
        top_gap_value = 0
        total_suppliers = 0
        company_rank = 0
    
    # تحلیل محصولات
    product_performance = bandar_data.groupby('زیرگروه').agg({
        'درآمد': 'sum',
        'حجم کل معامله شده بر حسب تن': 'sum',
        'nerkh': 'mean'
    }).round(2)
    
    # تحلیل رقابتی
    competitive_analysis = market_data.groupby('عرضه کننده').agg({
        'درآمد': 'sum',
        'حجم کل معامله شده بر حسب تن': 'sum'
    }).sort_values('درآمد', ascending=False).head(10)
    
    # روند زمانی
    time_analysis = bandar_data.groupby(['سال', 'ماه']).agg({
        'درآمد': 'sum',
        'حجم کل معامله شده بر حسب تن': 'sum',
        'nerkh': 'mean'
    }).reset_index()
    
    # بینش‌های استراتژیک - با استفاده از داده‌های ماه آخر
    insights = generate_bandar_insights(bandar_data, market_data)
    
    return {
        'total_revenue': total_revenue,
        'total_volume': total_volume,
        'market_share': market_share,
        'market_share_current_month': market_share_current_month,
        'current_month_revenue': current_month_revenue,
        'current_month_volume': current_month_volume,
        'current_products': current_products,
        
        # تغییرات درآمد
        'revenue_change_prev_month': revenue_change_prev_month,
        'revenue_change_prev_month_percent': revenue_change_prev_month_percent,
        'revenue_change_prev_year': revenue_change_prev_year,
        'revenue_change_prev_year_percent': revenue_change_prev_year_percent,
        
        # تغییرات حجم
        'volume_change_prev_month': volume_change_prev_month,
        'volume_change_prev_month_percent': volume_change_prev_month_percent,
        'volume_change_prev_year': volume_change_prev_year,
        'volume_change_prev_year_percent': volume_change_prev_year_percent,
        
        # تغییرات سهم بازار
        'market_share_change_prev_month': market_share_change_prev_month,
        'market_share_change_prev_month_percent': market_share_change_prev_month_percent,
        'market_share_change_prev_year': market_share_change_prev_year,
        'market_share_change_prev_year_percent': market_share_change_prev_year_percent,
        
        # تغییرات تعداد محصولات
        'products_change_prev_month': products_change_prev_month,
        'products_change_prev_year': products_change_prev_year,
        
        # شاخص‌های تحلیلی مقایسه با بازار
        'price_gap_percent': price_gap_percent,
        'top_gap_product': top_gap_product,
        'top_gap_value': top_gap_value,
        'total_suppliers': total_suppliers,
        'company_rank': company_rank,
        
        'product_performance': product_performance.to_dict('index'),
        'competitive_analysis': competitive_analysis.to_dict('index'),
        'time_analysis': time_analysis.to_dict('records'),
        'insights': insights
    }


def calculate_analytical_indices(bandar_data, market_data):
    """
    محاسبه شاخص‌های تحلیلی مرکب (نه صرفاً عملیاتی) برای مقایسه بندرامام با بازار:
    - شاخص موقعیت رقابتی (ترکیبی از سهم بازار، رتبه و همسویی قیمت)
    - مومنتوم (شتاب) روند سهم بازار در طول زمان
    - شاخص تمرکز بازار HHI و جایگاه بندرامام در آن
    - شاخص تنوع سبد محصول بندرامام
    همه‌ی این شاخص‌ها از داده‌ی ورودی (که می‌تواند فیلترشده باشد) به‌صورت پویا محاسبه می‌شوند.
    """
    result = {
        'hhi_market': 0, 'market_concentration_label': 'نامشخص',
        'bandar_market_share_volume': 0, 'bandar_rank_by_share': 0,
        'total_suppliers_count': 0, 'share_percentile': 0,
        'price_gap_vs_competitors': 0, 'price_alignment_score': 0,
        'competitive_position_score': 0, 'share_momentum': 0,
        'product_diversification_score': 0, 'main_competitor': '—'
    }
    try:
        if bandar_data.empty or market_data.empty:
            return result
        
        supplier_volume = market_data.groupby('عرضه کننده')['حجم کل معامله شده بر حسب تن'].sum()
        total_volume = supplier_volume.sum()
        if total_volume <= 0:
            return result
        
        shares = supplier_volume / total_volume * 100
        hhi = float((shares ** 2).sum())
        
        if hhi < 1500:
            concentration_label = 'رقابتی'
        elif hhi < 2500:
            concentration_label = 'نسبتاً متمرکز'
        else:
            concentration_label = 'بسیار متمرکز'
        
        bandar_share = float(shares.get('شرکت پتروشیمی بندرامام', 0))
        total_suppliers = int(shares.shape[0])
        
        rank_by_share = shares.rank(ascending=False, method='min')
        bandar_rank = int(rank_by_share.get('شرکت پتروشیمی بندرامام', total_suppliers)) if total_suppliers else 0
        share_percentile = ((total_suppliers - bandar_rank + 1) / total_suppliers * 100) if total_suppliers else 0
        
        competitors_shares = shares.drop('شرکت پتروشیمی بندرامام', errors='ignore')
        main_competitor = competitors_shares.idxmax() if not competitors_shares.empty else '—'
        
        competitors_data = market_data[market_data['عرضه کننده'] != 'شرکت پتروشیمی بندرامام']
        bandar_avg_price = bandar_data['nerkh'].mean() if not bandar_data.empty else 0
        market_avg_price = competitors_data['nerkh'].mean() if not competitors_data.empty else 0
        price_gap = ((bandar_avg_price - market_avg_price) / market_avg_price * 100) if market_avg_price else 0
        price_alignment_score = max(0, 100 - abs(price_gap) * 2)
        
        rank_score = (100 - (bandar_rank - 1) / max(total_suppliers - 1, 1) * 100) if total_suppliers > 1 else 100
        competitive_position_score = round((share_percentile * 0.5) + (price_alignment_score * 0.3) + (rank_score * 0.2), 1)
        
        # مومنتوم سهم بازار: شیب خط روند سهم بازار ماهانه (واحد درصد در ماه)
        momentum = 0
        try:
            def _bandar_share(g):
                gv = g['حجم کل معامله شده بر حسب تن'].sum()
                if gv <= 0:
                    return 0
                bv = g[g['عرضه کننده'] == 'شرکت پتروشیمی بندرامام']['حجم کل معامله شده بر حسب تن'].sum()
                return bv / gv * 100
            
            monthly = market_data.groupby(['سال', 'ماه']).apply(_bandar_share).reset_index(name='share')
            monthly = monthly.sort_values(['سال', 'ماه'])
            if len(monthly) >= 2:
                x = np.arange(len(monthly))
                y = monthly['share'].values
                slope = np.polyfit(x, y, 1)[0]
                momentum = slope
        except Exception:
            momentum = 0
        
        # شاخص تنوع سبد محصول بندرامام (بر اساس درآمد، معکوس HHI داخلی)
        product_revenue = bandar_data.groupby('زیرگروه')['درآمد'].sum()
        total_rev = product_revenue.sum()
        diversification_score = 0
        if total_rev > 0:
            product_shares = product_revenue / total_rev * 100
            own_hhi = float((product_shares ** 2).sum())
            diversification_score = round(max(0, 100 - own_hhi / 100), 1)
        
        result.update({
            'hhi_market': round(hhi, 0),
            'market_concentration_label': concentration_label,
            'bandar_market_share_volume': round(bandar_share, 1),
            'bandar_rank_by_share': bandar_rank,
            'total_suppliers_count': total_suppliers,
            'share_percentile': round(share_percentile, 1),
            'price_gap_vs_competitors': round(price_gap, 1),
            'price_alignment_score': round(price_alignment_score, 1),
            'competitive_position_score': competitive_position_score,
            'share_momentum': round(momentum, 2),
            'product_diversification_score': diversification_score,
            'main_competitor': main_competitor
        })
    except Exception as e:
        print(f"خطا در محاسبه شاخص‌های تحلیلی: {e}")
    
    return result

def generate_bandar_insights(bandar_data, market_data):
    """تولید بینش‌های استراتژیک پیشرفته بر اساس ماه آخر"""
    insights = []
    
    try:
        # پیدا کردن آخرین ماه در داده‌ها
        latest_year = bandar_data['سال'].max()
        latest_month_data = bandar_data[bandar_data['سال'] == latest_year]
        latest_month = latest_month_data['ماه'].max()
        
        # فیلتر داده‌های ماه آخر
        current_month_data = bandar_data[
            (bandar_data['سال'] == latest_year) & 
            (bandar_data['ماه'] == latest_month)
        ]
        
        # داده‌های بازار در ماه آخر
        current_month_market = market_data[
            (market_data['سال'] == latest_year) & 
            (market_data['ماه'] == latest_month)
        ]
        
        # 1. سهم بازار در ماه آخر
        total_market_volume = current_month_market['حجم کل معامله شده بر حسب تن'].sum()
        bandar_volume = current_month_data['حجم کل معامله شده بر حسب تن'].sum()
        market_share = (bandar_volume / total_market_volume * 100) if total_market_volume > 0 else 0
        
        insights.append(f"🎯 سهم بازار ماه {latest_month}: {market_share:.1f}% از کل معاملات")
        
        # 2. محصول استراتژیک ماه
        if not current_month_data.empty:
            top_product = current_month_data.groupby('زیرگروه')['درآمد'].sum().idxmax()
            top_product_revenue = current_month_data.groupby('زیرگروه')['درآمد'].sum().max()
            insights.append(f"🏆 محصول استراتژیک ماه: {top_product} ({top_product_revenue:,.0f} میلیون ریال)")
        
        # 3. رقیب اصلی ماه
        if not current_month_market.empty:
            competitors = current_month_market[current_month_market['عرضه کننده'] != 'شرکت پتروشیمی بندرامام']
            if not competitors.empty:
                top_competitor = competitors.groupby('عرضه کننده')['درآمد'].sum().idxmax()
                top_competitor_revenue = competitors.groupby('عرضه کننده')['درآمد'].sum().max()
                insights.append(f"⚔️ رقیب اصلی ماه: {top_competitor} ({top_competitor_revenue:,.0f} میلیون ریال)")
        
        # 4. کارایی قیمت‌گذاری در ماه آخر
        bandar_avg_price = current_month_data['nerkh'].mean()
        market_avg_price = current_month_market['nerkh'].mean()
        price_ratio = (bandar_avg_price / market_avg_price * 100) if market_avg_price > 0 else 0
        
        if price_ratio > 105:
            insights.append("💎 قیمت‌گذاری: بالاتر از بازار (+{:.1f}%)".format(price_ratio-100))
        elif price_ratio < 95:
            insights.append("💰 قیمت‌گذاری: پایین‌تر از بازار ({:.1f}%)".format(price_ratio-100))
        else:
            insights.append("⚖️ قیمت‌گذاری: هم‌سطح با بازار")
        
        # 5. موقعیت رقابتی در ماه آخر
        competitors_count = current_month_market['عرضه کننده'].nunique() - 1
        insights.append(f"🎯 رقبا در ماه {latest_month}: {competitors_count} شرکت رقیب")
            
    except Exception as e:
        print(f"خطا در تولید بینش‌ها: {e}")
        insights = [
            "📊 در حال تحلیل داده‌های ماه آخر...",
            "🔄 محاسبه شاخص‌های عملکرد ماه جاری",
            "📈 بررسی روندهای بازار",
            "🏆 شناسایی محصول استراتژیک ماه",
            "⚔️ تحلیل رقبای اصلی ماه"
        ]
    
    # فقط ۵ بینش اول را برگردان
    return insights[:5]

def create_bandar_sample_data():
    """ایجاد داده‌های نمونه برای پتروشیمی بندرامام"""
    bandar_sample = pd.DataFrame({
        'تاریخ': ['1400/01/15', '1400/02/20', '1400/03/25', '1401/01/10', '1401/02/15'],
        'سال': [1400, 1400, 1400, 1401, 1401],
        'ماه': [1, 2, 3, 1, 2],
        'زیرگروه': ['پلی اتیلن سنگین', 'پلی پروپیلن', 'پلی اتیلن سبک', 'پلی اتیلن سنگین', 'پلی پروپیلن'],
        'عرضه کننده': ['شرکت پتروشیمی بندرامام'] * 5,
        'رینگ(بازار هدف)': ['داخلی', 'داخلی', 'بین الملل', 'داخلی', 'بین الملل'],
        'نرخ تبدیل ارز': [1, 1, 42000, 1, 42000],
        'متوسط قيمت معامله': [1500, 1800, 2000, 1600, 1900],
        'حجم عرضه بر حسب تن': [100, 120, 80, 110, 130],
        'تقاضا(بر حسب تن)': [150, 140, 90, 120, 150],
        'حجم کل معامله شده بر حسب تن': [90, 110, 75, 100, 120],
        'nerkh': [1500, 1800, 84000, 1600, 79800],
        'درآمد': [135000, 198000, 6300000, 160000, 9576000]
    })
    
    market_sample = pd.DataFrame({
        'تاریخ': ['1400/01/15', '1400/02/20', '1400/03/25'],
        'سال': [1400, 1400, 1400],
        'ماه': [1, 2, 3],
        'زیرگروه': ['پلی اتیلن سنگین', 'پلی پروپیلن', 'پلی اتیلن سبک'],
        'عرضه کننده': ['شرکت رقیب ۱', 'شرکت رقیب ۲', 'شرکت رقیب ۳'],
        'حجم کل معامله شده بر حسب تن': [200, 180, 160],
        'nerkh': [1550, 1850, 82000],
        'درآمد': [280000, 324000, 13440000]
    })
    
    analysis = calculate_bandar_imam_metrics(bandar_sample, market_sample)
    analysis.update(calculate_analytical_indices(bandar_sample, market_sample))
    
    return {
        'bandar_imam': bandar_sample,
        'market_data': market_sample,
        'analysis': analysis,
        'available_years': [{'label': 'همه سال‌ها', 'value': 'all'}, {'label': '1400', 'value': 1400}, {'label': '1401', 'value': 1401}],
        'available_months': [{'label': 'همه ماه‌ها', 'value': 'all'}] + [{'label': str(i), 'value': i} for i in range(1, 4)],
        'products': ['پلی اتیلن سنگین', 'پلی پروپیلن', 'پلی اتیلن سبک'],
        'competitors': ['شرکت رقیب ۱', 'شرکت رقیب ۲', 'شرکت رقیب ۳'],
        'is_sample_data': True,
        'load_error': None,
        'source_path': None
    }

# =============================================================================
# 🎨 ایجاد داشبورد تخصصی بندرامام
# =============================================================================

def get_trend_class(value):
    """تعیین کلاس CSS بر اساس مقدار تغییر"""
    if value > 0:
        return "trend-positive"
    elif value < 0:
        return "trend-negative"
    else:
        return "trend-neutral"

def format_trend_text(change_value, change_percent, is_percent=True):
    """فرمت‌دهی متن تغییرات"""
    if is_percent:
        return f"{change_value:+.1f}% ({change_percent:+.1f}%)"
    else:
        return f"{change_value:+,.0f} ({change_percent:+.1f}%)"

def build_headline_text(analysis):
    """ساخت متن پیشنهاد تحلیلی امروز بر اساس شاخص‌های تحلیلی مرکب (نه اعداد خام عملیاتی)"""
    score = analysis.get('competitive_position_score', 0)
    momentum = analysis.get('share_momentum', 0)
    hhi_label = analysis.get('market_concentration_label', 'نامشخص')
    main_competitor = analysis.get('main_competitor', '—')
    diversification = analysis.get('product_diversification_score', 0)
    gap = analysis.get('price_gap_vs_competitors', 0)

    if score >= 70:
        position_word = "قوی"
    elif score >= 45:
        position_word = "متوسط"
    else:
        position_word = "ضعیف"

    momentum_word = "روند صعودی" if momentum > 0.05 else ("روند نزولی" if momentum < -0.05 else "روند باثبات")
    gap_word = "بالاتر" if gap >= 0 else "پایین‌تر"

    text = (
        f"شاخص موقعیت رقابتی بندرامام در این دوره {score:.0f} از ۱۰۰ و در سطح {position_word} قرار دارد. "
        f"سهم بازار شرکت در حال حاضر {momentum_word} است (شتاب {momentum:+.2f} واحد درصد در ماه) و بازار به‌طور کلی "
        f"{hhi_label} است (رقیب اصلی: {main_competitor}). "
        f"قیمت‌گذاری بندرامام {abs(gap):.1f}% {gap_word} از رقبا و تنوع سبد محصول آن {diversification:.0f} از ۱۰۰ است."
    )
    return text


def create_bandar_imam_dashboard(data):
    """ایجاد رابط داشبورد تحلیلی پتروشیمی بندرامام"""
    analysis = data['analysis']
    
    position_score = analysis.get('competitive_position_score', 0)
    momentum = analysis.get('share_momentum', 0)
    hhi = analysis.get('hhi_market', 0)
    hhi_label = analysis.get('market_concentration_label', 'نامشخص')
    diversification = analysis.get('product_diversification_score', 0)
    
    competitor_options = [{'label': c, 'value': c} for c in data.get('competitors', [])]
    
    is_sample = data.get('is_sample_data', False)
    load_error = data.get('load_error')
    source_path = data.get('source_path')
    
    warning_banner = []
    if is_sample:
        warning_banner = [
            html.Div(style={
                'background': '#fdecec', 'border': '1px solid #f5b5b5', 'borderRadius': '14px',
                'padding': '16px 20px', 'marginBottom': '18px', 'color': '#b03030', 'fontWeight': 'bold'
            }, children=[
                html.Div("⚠️ توجه: این داشبورد در حال نمایش داده‌های نمونه (ساختگی) است، نه داده واقعی enb.xlsx"),
                html.Div(
                    f"مسیر مورد انتظار: {source_path}" + (f" | دلیل خطا: {load_error}" if load_error else ""),
                    style={'fontWeight': 'normal', 'fontSize': '0.85em', 'marginTop': '6px'}
                ),
                html.Div(
                    "برای رفع مشکل، مسیر فایل، اتصال درایو P و نام دقیق ستون‌ها را بررسی کنید. "
                    "جزئیات کامل خطا در فایل error_log.txt کنار برنامه ذخیره شده است.",
                    style={'fontWeight': 'normal', 'fontSize': '0.85em', 'marginTop': '4px'}
                )
            ])
        ]
    
    return html.Div(className="dashboard-container", children=[
        *warning_banner,
        # هدر
        html.Div(className="header", children=[
            html.Div(className="header-titles", children=[
                html.H1("داشبورد تحلیلی مقایسه‌ای بندرامام"),
                html.P("تحلیل موقعیت رقابتی، روند و ساختار بازار پتروشیمی بندرامام در برابر رقبا (به تفکیک ماه)")
            ]),
            html.Div(className="header-actions", children=[
                html.Div(className="header-icon-btn", children="🔔"),
                html.Div(className="header-chip", children=[
                    html.Span("📅"),
                    html.Span(id="header-period-text", children="آخرین دوره ثبت‌شده")
                ])
            ])
        ]),
        
        # پیشنهاد تحلیلی امروز
        html.Div(className="insight-banner", children=[
            html.Div(className="insight-banner-text", children=[
                html.Div(className="insight-banner-icon", children="💡"),
                html.Div(children=[
                    html.Div("پیشنهاد تحلیلی ماه", className="insight-banner-title"),
                    html.Div(build_headline_text(analysis), className="insight-banner-desc")
                ])
            ]),
            html.Button("دانلود گزارش تحلیلی", id="btn-download-report", className="insight-download-btn", n_clicks=0)
        ]),
        
        # شاخص‌های تحلیلی مرکب (KPI) - نه اعداد خام عملیاتی
        html.Div(className="grid-container", children=[
            # شاخص موقعیت رقابتی
            html.Div(className="stat-card company-highlight", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div(f"{position_score:.0f}/100", className=f"stat-badge {'positive' if position_score >= 60 else ('neutral' if position_score >= 40 else 'negative')}"),
                    html.Div("🧭", className="stat-icon")
                ]),
                html.Div(f"{position_score:.0f}", className="stat-value"),
                html.Div("شاخص موقعیت رقابتی بندرامام (از ۱۰۰)", className="stat-label")
            ]),
            
            # مومنتوم سهم بازار
            html.Div(className="stat-card", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div(f"{momentum:+.2f}", className=f"stat-badge {'positive' if momentum >= 0 else 'negative'}"),
                    html.Div("📈" if momentum >= 0 else "📉", className="stat-icon")
                ]),
                html.Div(f"{momentum:+.2f}", className="stat-value"),
                html.Div("مومنتوم سهم بازار (واحد درصد در ماه)", className="stat-label")
            ]),
            
            # شاخص تمرکز بازار
            html.Div(className="stat-card", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div(hhi_label, className="stat-badge neutral"),
                    html.Div("🧩", className="stat-icon")
                ]),
                html.Div(f"{hhi:.0f}", className="stat-value"),
                html.Div("شاخص تمرکز بازار HHI", className="stat-label")
            ]),
            
            # شاخص تنوع سبد محصول
            html.Div(className="stat-card", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div(f"{diversification:.0f}/100", className=f"stat-badge {'positive' if diversification >= 60 else 'neutral'}"),
                    html.Div("🧬", className="stat-icon")
                ]),
                html.Div(f"{diversification:.0f}", className="stat-value"),
                html.Div("شاخص تنوع سبد محصول بندرامام", className="stat-label")
            ])
        ]),
        
        # کارت فیلترها
        html.Div(className="card", children=[
            html.Div(className="filter-card-header", style={'padding': '20px 24px 4px 24px'}, children=[
                html.Div("🎛️ فیلترهای تحلیلی", className="card-header", style={'padding': '0'}),
                html.Button("پاک کردن فیلترها", id="btn-clear-filters", className="filter-clear-btn", n_clicks=0)
            ]),
            html.Div(className="card-body", children=[
                html.Div(className="filter-row", children=[
                    html.Div(className="filter-group", children=[
                        html.Label("سال:", className="filter-label"),
                        dcc.Dropdown(
                            id='year-dropdown',
                            options=data['available_years'],
                            value='all',
                            clearable=False,
                            className="dropdown"
                        )
                    ]),
                    html.Div(className="filter-group", children=[
                        html.Label("ماه:", className="filter-label"),
                        dcc.Dropdown(
                            id='month-dropdown',
                            options=data['available_months'],
                            value='all',
                            clearable=False,
                            className="dropdown"
                        )
                    ]),
                    html.Div(className="filter-group", children=[
                        html.Label("محصول (فقط برای گزارش مالی و روند):", className="filter-label"),
                        dcc.Dropdown(
                            id='product-dropdown',
                            options=[{'label': product, 'value': product} for product in data['products']],
                            value=data['products'][0] if data['products'] else '',
                            clearable=False,
                            className="dropdown"
                        )
                    ]),
                    html.Div(className="filter-group", children=[
                        html.Label("مقایسه با رقیب:", className="filter-label"),
                        dcc.Dropdown(
                            id='competitor-dropdown',
                            options=[{'label': 'مقایسه با ۵ رقیب برتر', 'value': 'top5'}] + competitor_options,
                            value='top5',
                            clearable=False,
                            className="dropdown"
                        )
                    ])
                ])
            ])
        ]),
        
        # تب‌های تحلیل تخصصی
        html.Div(className="tab-buttons", children=[
            html.Button("عملکرد محصولات", className="tab-btn active", id="tab-products"),
            html.Button("تحلیل رقابتی", className="tab-btn", id="tab-competitive"),
            html.Button("روند ماهانه بازار", className="tab-btn", id="tab-trends"),
            html.Button("گزارش مالی", className="tab-btn", id="tab-financial")
        ]),
        html.Div(id="bandar-tab-content", children=[
            # محتوای تب به صورت پویا بارگذاری می‌شود
        ]),
        
        dcc.Store(id='active-tab-store', data='tab-products'),
        dcc.Download(id="download-report-excel")
    ])

# =============================================================================
# منطق کنترل پیشرفت
# =============================================================================

dashboard_data = None

@app.callback(
    [Output('progress-bar', 'style'),
     Output('progress-text', 'children'),
     Output('loading-screen', 'style'),
     Output('dashboard-content', 'style'),
     Output('dashboard-content', 'children')] + 
    [Output(f'step-{i}', 'className') for i in range(len(LOADING_STEPS))],
    Input('progress-interval', 'n_intervals')
)
def update_progress(n):
    global dashboard_data
    
    progress = min(n * PROGRESS_STEP, 100)
    current_step = min(int(progress / (100/len(LOADING_STEPS))), len(LOADING_STEPS) - 1)
    
    step_classes = []
    for i in range(len(LOADING_STEPS)):
        if i <= current_step:
            step_classes.append("step active")
        else:
            step_classes.append("step")
    
    if progress < 100:
        return (
            {'width': f'{progress}%'},
            f"{progress}%",
            {'display': 'block'},
            {'display': 'none'},
            "",
            *step_classes
        )
    else:
        if dashboard_data is None:
            dashboard_data = load_bandar_imam_analysis()
        
        dashboard_content = create_bandar_imam_dashboard(dashboard_data)
        
        return (
            {'width': '100%'},
            "100% - آماده!",
            {'display': 'none'},
            {'display': 'block'},
            dashboard_content,
            *["step active"] * len(LOADING_STEPS)
        )

# =============================================================================
# کالبک‌های تحلیل تخصصی
# =============================================================================

@app.callback(
    Output('active-tab-store', 'data'),
    [Input('tab-products', 'n_clicks'),
     Input('tab-competitive', 'n_clicks'),
     Input('tab-trends', 'n_clicks'),
     Input('tab-financial', 'n_clicks')],
    State('active-tab-store', 'data'),
    prevent_initial_call=True
)
def set_active_tab(btn1, btn2, btn3, btn4, current_tab):
    """ذخیره تب فعال هنگام کلیک روی دکمه‌های تب"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_tab
    return ctx.triggered[0]['prop_id'].split('.')[0]


@app.callback(
    [Output('bandar-tab-content', 'children'),
     Output('tab-products', 'className'),
     Output('tab-competitive', 'className'),
     Output('tab-trends', 'className'),
     Output('tab-financial', 'className')],
    [Input('active-tab-store', 'data'),
     Input('year-dropdown', 'value'),
     Input('month-dropdown', 'value'),
     Input('product-dropdown', 'value'),
     Input('competitor-dropdown', 'value')]
)
def update_bandar_tabs(tab_id, selected_year, selected_month, selected_product, selected_competitor):
    active_tab = tab_id or 'tab-products'
    
    if dashboard_data is None:
        return html.Div("در حال بارگذاری داده‌ها...", style={'textAlign': 'center', 'padding': '50px'}), "tab-btn", "tab-btn", "tab-btn", "tab-btn"
    
    bandar_data = dashboard_data['bandar_imam']
    market_data = dashboard_data['market_data']
    analysis = dashboard_data['analysis']
    
    # فیلتر کردن داده‌ها - در تب‌های «عملکرد محصولات» و «تحلیل رقابتی»، فیلتر محصول اعمال نمی‌شود
    # زیرا این دو تب باید کل سبد محصولات شرکت را در برابر بازار/رقبا ببینند
    if active_tab in ('tab-products', 'tab-competitive'):
        filtered_bandar = apply_bandar_filters(bandar_data, selected_year, selected_month, None)
    else:
        filtered_bandar = apply_bandar_filters(bandar_data, selected_year, selected_month, selected_product)
    
    if active_tab in ('tab-products', 'tab-competitive'):
        filtered_market = apply_bandar_filters(market_data, selected_year, selected_month, None)
    else:
        filtered_market = apply_bandar_filters(market_data, selected_year, selected_month, selected_product)
    
    # ایجاد کلاس‌های فعال برای تب‌ها
    tab_classes = []
    for tab in ['tab-products', 'tab-competitive', 'tab-trends', 'tab-financial']:
        if tab == active_tab:
            tab_classes.append("tab-btn active")
        else:
            tab_classes.append("tab-btn")
    
    if active_tab == 'tab-products':
        content = create_products_analysis(filtered_bandar, filtered_market, analysis)
    elif active_tab == 'tab-competitive':
        content = create_competitive_analysis(filtered_bandar, filtered_market, analysis, selected_competitor)
    elif active_tab == 'tab-trends':
        content = create_trends_analysis(filtered_bandar, filtered_market, analysis)
    elif active_tab == 'tab-financial':
        content = create_financial_analysis(filtered_bandar, analysis)
    else:
        content = create_products_analysis(filtered_bandar, filtered_market, analysis)
    
    return content, *tab_classes


@app.callback(
    [Output('year-dropdown', 'value'),
     Output('month-dropdown', 'value'),
     Output('product-dropdown', 'value'),
     Output('competitor-dropdown', 'value')],
    Input('btn-clear-filters', 'n_clicks'),
    prevent_initial_call=True
)
def clear_filters(n_clicks):
    """بازگرداندن همه فیلترها به حالت پیش‌فرض"""
    products = dashboard_data['products'] if dashboard_data else []
    default_product = products[0] if products else ''
    return 'all', 'all', default_product, 'top5'


@app.callback(
    Output('download-report-excel', 'data'),
    Input('btn-download-report', 'n_clicks'),
    prevent_initial_call=True
)
def download_analytical_report(n_clicks):
    """دانلود گزارش تحلیلی خلاصه به صورت اکسل"""
    if dashboard_data is None:
        return dash.no_update
    
    bandar_data = dashboard_data['bandar_imam']
    market_data = dashboard_data['market_data']
    
    summary = bandar_data.groupby('زیرگروه').agg({
        'درآمد': 'sum',
        'حجم کل معامله شده بر حسب تن': 'sum',
        'nerkh': 'mean'
    }).round(2).reset_index()
    summary.columns = ['محصول', 'درآمد (میلیون ریال)', 'حجم معاملات (تن)', 'میانگین قیمت']
    
    market_summary = market_data.groupby('عرضه کننده').agg({
        'درآمد': 'sum',
        'حجم کل معامله شده بر حسب تن': 'sum'
    }).sort_values('درآمد', ascending=False).round(2).reset_index()
    market_summary.columns = ['عرضه کننده', 'درآمد (میلیون ریال)', 'حجم معاملات (تن)']
    
    def write_excel(bytes_io):
        with pd.ExcelWriter(bytes_io, engine='xlsxwriter') as writer:
            summary.to_excel(writer, sheet_name='محصولات بندرامام', index=False)
            market_summary.to_excel(writer, sheet_name='مقایسه با بازار', index=False)
    
    return dcc.send_bytes(write_excel, "گزارش_تحلیلی_بندرامام.xlsx")

def apply_bandar_filters(data, year, month, product):
    """اعمال فیلترها بر روی داده‌های بندرامام"""
    filtered_data = data.copy()
    
    if year != 'all':
        filtered_data = filtered_data[filtered_data['سال'] == year]
    
    if month != 'all':
        filtered_data = filtered_data[filtered_data['ماه'] == month]
    
    if product:
        filtered_data = filtered_data[filtered_data['زیرگروه'] == product]
    
    return filtered_data

# پالت رنگی جدید برای نمودارها
# پالت رنگی هماهنگ با تم روشن داشبورد
COLOR_PALETTE = [
    '#2f5fdb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4',
    '#ec4899', '#84cc16', '#f97316', '#6366f1', '#14b8a6', '#a855f7'
]

def create_products_analysis(bandar_data, market_data, analysis):
    """
    پوزیشن‌یابی تحلیلی محصولات بندرامام در بازار (بدون فیلتر محصول - همیشه کل سبد).
    به‌جای نمودارهای عملیاتی ساده (سهم از درآمد/حجم)، یک ماتریس پوزیشن‌یابی
    (اختلاف قیمت در برابر سهم بازار هر محصول) و یک نمودار تجمیعی تنوع سبد ارائه می‌شود.
    همه‌ی اعداد و متن‌ها از داده ورودی محاسبه می‌شوند و ثابت نیستند.
    """
    try:
        if bandar_data.empty:
            return html.Div("داده‌ای برای تحلیل موجود نیست", style={'textAlign': 'center', 'padding': '50px'})
        
        total_company_revenue = bandar_data['درآمد'].sum()
        competitors_data = market_data[market_data['عرضه کننده'] != 'شرکت پتروشیمی بندرامام'] if not market_data.empty else market_data
        
        rows = []
        for product in sorted(bandar_data['زیرگروه'].dropna().astype(str).unique()):
            b_prod = bandar_data[bandar_data['زیرگروه'] == product]
            m_prod = market_data[market_data['زیرگروه'] == product] if not market_data.empty else b_prod.iloc[0:0]
            comp_prod = competitors_data[competitors_data['زیرگروه'] == product] if not competitors_data.empty else b_prod.iloc[0:0]
            
            b_revenue = b_prod['درآمد'].sum()
            b_volume = b_prod['حجم کل معامله شده بر حسب تن'].sum()
            m_volume = m_prod['حجم کل معامله شده بر حسب تن'].sum()
            product_market_share = (b_volume / m_volume * 100) if m_volume > 0 else 0
            
            b_price = b_prod['nerkh'].mean() if not b_prod.empty else 0
            comp_price = comp_prod['nerkh'].mean() if not comp_prod.empty else 0
            price_gap = ((b_price - comp_price) / comp_price * 100) if comp_price else 0
            
            revenue_share_of_company = (b_revenue / total_company_revenue * 100) if total_company_revenue else 0
            
            rows.append({
                'product': product,
                'price_gap': price_gap,
                'market_share': product_market_share,
                'revenue': b_revenue,
                'revenue_share_of_company': revenue_share_of_company
            })
        
        if not rows:
            return html.Div("داده‌ای برای تحلیل موجود نیست", style={'textAlign': 'center', 'padding': '50px'})
        
        avg_share = sum(r['market_share'] for r in rows) / len(rows)
        
        # ---------------- ماتریس پوزیشن‌یابی: اختلاف قیمت × سهم بازار ----------------
        def quadrant_of(r):
            if r['market_share'] >= avg_share and r['price_gap'] >= 0:
                return 'محصول پرچمدار (سهم بالا، قیمت پرمیوم)'
            elif r['market_share'] >= avg_share and r['price_gap'] < 0:
                return 'محصول حجم‌محور (سهم بالا، قیمت رقابتی)'
            elif r['market_share'] < avg_share and r['price_gap'] >= 0:
                return 'محصول تخصصی (سهم پایین، قیمت پرمیوم)'
            else:
                return 'محصول نیازمند بازنگری (سهم پایین، قیمت پایین)'
        
        for r in rows:
            r['quadrant'] = quadrant_of(r)
        
        quadrant_colors = {
            'محصول پرچمدار (سهم بالا، قیمت پرمیوم)': COLOR_PALETTE[1],
            'محصول حجم‌محور (سهم بالا، قیمت رقابتی)': COLOR_PALETTE[0],
            'محصول تخصصی (سهم پایین، قیمت پرمیوم)': COLOR_PALETTE[2],
            'محصول نیازمند بازنگری (سهم پایین، قیمت پایین)': COLOR_PALETTE[3]
        }
        
        fig_positioning = go.Figure()
        for quad, color in quadrant_colors.items():
            quad_rows = [r for r in rows if r['quadrant'] == quad]
            if not quad_rows:
                continue
            fig_positioning.add_trace(go.Scatter(
                x=[r['price_gap'] for r in quad_rows],
                y=[r['market_share'] for r in quad_rows],
                mode='markers+text',
                name=quad,
                text=[r['product'] for r in quad_rows],
                textposition='top center',
                marker=dict(
                    size=[max(18, min(60, r['revenue_share_of_company'])) for r in quad_rows],
                    color=color,
                    line=dict(width=1, color='white')
                )
            ))
        
        fig_positioning.add_vline(x=0, line_dash='dash', line_color='#c7ccd6')
        fig_positioning.add_hline(y=avg_share, line_dash='dash', line_color='#c7ccd6',
                                   annotation_text=f'میانگین سهم محصولات: {avg_share:.1f}%')
        fig_positioning.update_layout(
            title='🧭 ماتریس پوزیشن‌یابی محصولات (اختلاف قیمت با رقبا × سهم بازار محصول)',
            xaxis_title='اختلاف قیمت با رقبا (%)',
            yaxis_title='سهم بندرامام از بازار همان محصول (%)',
            template='plotly_white',
            height=460,
            font=dict(family='Vazir', size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="center", x=0.5)
        )
        
        # ---------------- ترکیب سبد بر اساس درآمد (Treemap) ----------------
        fig_treemap = px.treemap(
            rows,
            path=['quadrant', 'product'],
            values='revenue',
            color='price_gap',
            color_continuous_scale='RdYlGn',
            color_continuous_midpoint=0,
            title='🌳 ترکیب سبد محصولات بندرامام بر اساس درآمد و همسویی قیمت با رقبا'
        )
        fig_treemap.update_layout(
            template='plotly_white',
            height=460,
            font=dict(family='Vazir', size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=60, l=10, r=10, b=10)
        )
        
        # ---------------- کارت‌های تحلیلی پویا (بدون جدول) ----------------
        top_revenue_row = max(rows, key=lambda r: r['revenue'])
        best_position_row = max(rows, key=lambda r: (r['market_share'] - avg_share) + r['price_gap'])
        weakest_row = min(rows, key=lambda r: (r['market_share'] - avg_share) + r['price_gap'])
        flagship_count = sum(1 for r in rows if r['quadrant'] == 'محصول پرچمدار (سهم بالا، قیمت پرمیوم)')
        
        products_cards = [
            html.Div(className="stat-card company-highlight", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div(f"{top_revenue_row['revenue_share_of_company']:.1f}%", className="stat-badge positive"),
                    html.Div("💎", className="stat-icon")
                ]),
                html.Div(top_revenue_row['product'], className="stat-value", style={'fontSize': '1.15em'}),
                html.Div("محصول با بیشترین سهم از درآمد شرکت", className="stat-label")
            ]),
            html.Div(className="stat-card", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div(f"{best_position_row['price_gap']:+.1f}%", className="stat-badge positive"),
                    html.Div("🚀", className="stat-icon")
                ]),
                html.Div(best_position_row['product'], className="stat-value", style={'fontSize': '1.15em'}),
                html.Div("بهترین موقعیت رقابتی در بازار", className="stat-label")
            ]),
            html.Div(className="stat-card", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div(f"{weakest_row['price_gap']:+.1f}%", className="stat-badge negative"),
                    html.Div("⚠️", className="stat-icon")
                ]),
                html.Div(weakest_row['product'], className="stat-value", style={'fontSize': '1.15em'}),
                html.Div("محصول نیازمند بازنگری استراتژی", className="stat-label")
            ]),
            html.Div(className="stat-card", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div(f"{flagship_count}/{len(rows)}", className="stat-badge neutral"),
                    html.Div("🏳️", className="stat-icon")
                ]),
                html.Div(f"{flagship_count}", className="stat-value"),
                html.Div("تعداد محصولات پرچمدار در سبد", className="stat-label")
            ])
        ]
        
        callout_text = (
            f"از {len(rows)} محصول فعال بندرامام، {flagship_count} محصول در جایگاه «پرچمدار» (سهم بازار بالا و قیمت پرمیوم) قرار دارد. "
            f"محصول «{best_position_row['product']}» بهترین ترکیب سهم بازار و قیمت‌گذاری را دارد، در حالی که «{weakest_row['product']}» "
            f"بیشترین نیاز به بازنگری استراتژی قیمتی یا توزیع را دارد."
        )
        
        return html.Div([
            html.Div(className="grid-container", children=products_cards),
            html.Div(className="card", children=[
                html.Div(className="card-header", children="ماتریس پوزیشن‌یابی محصولات"),
                html.Div(className="card-subtitle", children="اندازه هر حباب متناسب با سهم آن محصول از درآمد کل شرکت است"),
                html.Div(className="card-body", children=[
                    dcc.Graph(figure=fig_positioning),
                    html.Div(className="callout info", children=callout_text)
                ])
            ]),
            html.Div(className="card", children=[
                html.Div(className="card-header", children="ترکیب سبد محصولات"),
                html.Div(className="card-subtitle", children="رنگ هر بخش نشان‌دهنده اختلاف قیمت آن محصول با رقبا است (سبز = گران‌تر، قرمز = ارزان‌تر)"),
                html.Div(className="card-body", children=[
                    dcc.Graph(figure=fig_treemap)
                ])
            ])
        ])
        
    except Exception as e:
        print(f"خطا در تحلیل محصولات: {e}")
        return html.Div("خطا در تحلیل محصولات")


def create_competitive_analysis(bandar_data, market_data, analysis, selected_competitor=None):
    """تحلیل رقابتی: مقایسه بندرامام با رقبای برتر یا یک رقیب انتخاب‌شده"""
    try:
        # محاسبه سهم بازار
        bandar_volume = bandar_data['حجم کل معامله شده بر حسب تن'].sum()
        bandar_revenue = bandar_data['درآمد'].sum()
        bandar_avg_price = bandar_data['nerkh'].mean() if not bandar_data.empty else 0
        market_volume = market_data['حجم کل معامله شده بر حسب تن'].sum()
        market_share = (bandar_volume / market_volume * 100) if market_volume > 0 else 0
        
        # تحلیل رقبا
        competitors = market_data[market_data['عرضه کننده'] != 'شرکت پتروشیمی بندرامام']
        top_competitors = competitors.groupby('عرضه کننده').agg({
            'درآمد': 'sum',
            'حجم کل معامله شده بر حسب تن': 'sum',
            'nerkh': 'mean'
        }).nlargest(5, 'درآمد').reset_index()
        
        use_specific = selected_competitor and selected_competitor != 'top5' and selected_competitor in competitors['عرضه کننده'].unique()
        
        if use_specific:
            comp_row = competitors[competitors['عرضه کننده'] == selected_competitor]
            companies = ['پتروشیمی بندرامام', selected_competitor]
            revenues = [bandar_revenue, comp_row['درآمد'].sum()]
            volumes = [bandar_volume, comp_row['حجم کل معامله شده بر حسب تن'].sum()]
            comp_avg_price = comp_row['nerkh'].mean() if not comp_row.empty else 0
            chart_title_suffix = f"در برابر {selected_competitor}"
        else:
            companies = ['پتروشیمی بندرامام'] + top_competitors['عرضه کننده'].tolist()[:4]
            revenues = [bandar_revenue] + top_competitors['درآمد'].tolist()[:4]
            volumes = [bandar_volume] + top_competitors['حجم کل معامله شده بر حسب تن'].tolist()[:4]
            comp_avg_price = top_competitors['nerkh'].mean() if not top_competitors.empty else 0
            chart_title_suffix = "با ۴ رقیب برتر"
        
        bar_colors = [COLOR_PALETTE[0] if c == 'پتروشیمی بندرامام' else COLOR_PALETTE[(i % (len(COLOR_PALETTE)-1)) + 1]
                      for i, c in enumerate(companies)]
        
        # نمودار مقایسه‌ای درآمد
        fig_revenue_comparison = go.Figure()
        fig_revenue_comparison.add_trace(go.Bar(
            name='درآمد (میلیون ریال)',
            x=companies,
            y=revenues,
            marker_color=bar_colors,
            text=revenues,
            texttemplate='%{text:,.0f}',
            textposition='auto',
        ))
        fig_revenue_comparison.update_layout(
            title=f'📊 مقایسه درآمد {chart_title_suffix}',
            template='plotly_white',
            height=380,
            font=dict(family='Vazir', size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        
        # نمودار مقایسه‌ای حجم معاملات
        fig_volume_comparison = go.Figure()
        fig_volume_comparison.add_trace(go.Bar(
            name='حجم معاملات (تن)',
            x=companies,
            y=volumes,
            marker_color=bar_colors,
            text=volumes,
            texttemplate='%{text:,.0f}',
            textposition='auto',
        ))
        fig_volume_comparison.update_layout(
            title=f'📦 مقایسه حجم معاملات {chart_title_suffix}',
            template='plotly_white',
            height=380,
            font=dict(family='Vazir', size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        
        # کارت‌های رقابتی
        price_gap_vs_comp = ((bandar_avg_price - comp_avg_price) / comp_avg_price * 100) if comp_avg_price else 0
        revenue_gap_vs_comp = ((bandar_revenue - revenues[1]) / revenues[1] * 100) if len(revenues) > 1 and revenues[1] else 0
        
        competitive_cards = [
            html.Div(className="stat-card", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div(f"{market_share:.1f}%", className="stat-badge positive"),
                    html.Div("📊", className="stat-icon")
                ]),
                html.Div(f"{market_share:.1f}%", className="stat-value"),
                html.Div("سهم بندرامام از بازار (دوره انتخابی)", className="stat-label")
            ]),
            html.Div(className="stat-card", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div(f"{revenue_gap_vs_comp:+.1f}%", className=f"stat-badge {'positive' if revenue_gap_vs_comp >= 0 else 'negative'}"),
                    html.Div("💰", className="stat-icon")
                ]),
                html.Div(f"{revenue_gap_vs_comp:+.1f}%", className="stat-value"),
                html.Div("اختلاف درآمد نسبت به " + (selected_competitor if use_specific else "میانگین رقبای برتر"), className="stat-label")
            ]),
            html.Div(className="stat-card", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div(f"{price_gap_vs_comp:+.1f}%", className=f"stat-badge {'positive' if price_gap_vs_comp >= 0 else 'negative'}"),
                    html.Div("🎯", className="stat-icon")
                ]),
                html.Div(f"{price_gap_vs_comp:+.1f}%", className="stat-value"),
                html.Div("اختلاف قیمت نسبت به " + (selected_competitor if use_specific else "میانگین رقبای برتر"), className="stat-label")
            ])
        ]
        
        if not top_competitors.empty and not use_specific:
            main_competitor = top_competitors.iloc[0]['عرضه کننده']
            main_competitor_revenue = top_competitors.iloc[0]['درآمد']
            competitive_cards.append(
                html.Div(className="stat-card", children=[
                    html.Div(className="stat-card-top", children=[
                        html.Div("۱", className="stat-badge neutral"),
                        html.Div("⚔️", className="stat-icon")
                    ]),
                    html.Div(main_competitor, className="stat-value", style={'fontSize': '1.2em'}),
                    html.Div(f"رقیب اصلی ({main_competitor_revenue:,.0f} میلیون ریال)", className="stat-label")
                ])
            )
        
        callout_class = "success" if revenue_gap_vs_comp >= 0 else "warning"
        callout_text = (
            f"در دوره انتخابی، درآمد بندرامام نسبت به {'رقیب ' + selected_competitor if use_specific else 'میانگین رقبای برتر'} "
            f"{revenue_gap_vs_comp:+.1f}% و قیمت‌گذاری آن {price_gap_vs_comp:+.1f}% تفاوت دارد."
        )
        
        # ---------------------------------------------------------------
        # بخش جداگانه: تحلیل رقابتی به تفکیک تک‌تک محصولات (بدون فیلتر محصول)
        # برای هر محصولی که بندرامام در آن فعالیت دارد، سهم بازار، اختلاف قیمت
        # و رقیب اصلی آن محصول به صورت پویا محاسبه می‌شود.
        # ---------------------------------------------------------------
        product_competitive_rows = []
        for product in sorted(bandar_data['زیرگروه'].dropna().astype(str).unique()):
            b_prod = bandar_data[bandar_data['زیرگروه'] == product]
            m_prod = market_data[market_data['زیرگروه'] == product]
            comp_prod = m_prod[m_prod['عرضه کننده'] != 'شرکت پتروشیمی بندرامام']
            
            b_vol = b_prod['حجم کل معامله شده بر حسب تن'].sum()
            m_vol = m_prod['حجم کل معامله شده بر حسب تن'].sum()
            product_share = (b_vol / m_vol * 100) if m_vol > 0 else 0
            
            b_price = b_prod['nerkh'].mean() if not b_prod.empty else 0
            comp_price = comp_prod['nerkh'].mean() if not comp_prod.empty else 0
            product_price_gap = ((b_price - comp_price) / comp_price * 100) if comp_price else 0
            
            if not comp_prod.empty:
                comp_rev_by_supplier = comp_prod.groupby('عرضه کننده')['درآمد'].sum()
                main_comp = comp_rev_by_supplier.idxmax()
            else:
                main_comp = '—'
            
            product_competitive_rows.append({
                'محصول': product,
                'سهم_بازار': round(product_share, 1),
                'اختلاف_قیمت': round(product_price_gap, 1),
                'رقیب_اصلی': main_comp
            })
        
        # نمودار حرارتی (Heatmap) اختلاف قیمت به تفکیک محصول - جایگزین تحلیلی جدول
        fig_price_heatmap = go.Figure()
        if product_competitive_rows:
            products_list = [r['محصول'] for r in product_competitive_rows]
            gaps_list = [r['اختلاف_قیمت'] for r in product_competitive_rows]
            hover_text = [
                f"{r['محصول']}<br>اختلاف قیمت: {r['اختلاف_قیمت']:+.1f}%<br>سهم بازار: {r['سهم_بازار']:.1f}%<br>رقیب اصلی: {r['رقیب_اصلی']}"
                for r in product_competitive_rows
            ]
            fig_price_heatmap.add_trace(go.Heatmap(
                z=[gaps_list],
                x=products_list,
                y=['اختلاف قیمت بندرامام با رقبا (%)'],
                colorscale='RdYlGn',
                zmid=0,
                text=[hover_text],
                hoverinfo='text',
                texttemplate='%{z:+.1f}%',
                showscale=True,
                colorbar=dict(title='%')
            ))
        fig_price_heatmap.update_layout(
            title='🌡️ نقشه حرارتی اختلاف قیمت بندرامام با رقبا به تفکیک محصول',
            template='plotly_white',
            height=280,
            font=dict(family='Vazir', size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        products_above = sum(1 for r in product_competitive_rows if r['اختلاف_قیمت'] > 0)
        products_below = sum(1 for r in product_competitive_rows if r['اختلاف_قیمت'] < 0)
        product_heatmap_callout = (
            f"از {len(product_competitive_rows)} محصول فعال، در {products_above} محصول قیمت بندرامام بالاتر از رقبا "
            f"و در {products_below} محصول پایین‌تر از رقبا بوده است."
        )
        
        return html.Div([
            html.Div(className="grid-container", children=competitive_cards),
            html.Div(className="grid-container", style={'gridTemplateColumns': 'repeat(auto-fit, minmax(380px, 1fr))'}, children=[
                html.Div(className="card", children=[
                    html.Div(className="card-header", children="مقایسه درآمد با رقبا"),
                    html.Div(className="card-subtitle", children="بر اساس فیلترهای انتخاب‌شده"),
                    html.Div(className="card-body", children=[
                        dcc.Graph(figure=fig_revenue_comparison)
                    ])
                ]),
                html.Div(className="card", children=[
                    html.Div(className="card-header", children="مقایسه حجم معاملات با رقبا"),
                    html.Div(className="card-subtitle", children="بر اساس فیلترهای انتخاب‌شده"),
                    html.Div(className="card-body", children=[
                        dcc.Graph(figure=fig_volume_comparison)
                    ])
                ])
            ]),
            html.Div(className=f"callout {callout_class}", children=callout_text),
            
            # بخش جداگانه: تحلیل رقابتی به تفکیک محصول (بدون جدول - نقشه حرارتی)
            html.Div(className="card", style={'marginTop': '10px'}, children=[
                html.Div(className="card-header", children="🧬 تحلیل رقابتی به تفکیک محصول"),
                html.Div(className="card-subtitle", children="بدون اعمال فیلتر محصول - همه محصولات فعال بندرامام به‌صورت جداگانه بررسی می‌شوند"),
                html.Div(className="card-body", children=[
                    dcc.Graph(figure=fig_price_heatmap),
                    html.Div(className="callout info", children=product_heatmap_callout)
                ])
            ])
        ])
        

    except Exception as e:
        print(f"خطا در تحلیل رقابتی: {e}")
        return html.Div("خطا در تحلیل رقابتی")

def create_trends_analysis(data, market_data, analysis):
    """تحلیل روندهای بازار با سهم بازار"""
    try:
        if data.empty:
            return html.Div("داده‌ای برای تحلیل موجود نیست", style={'textAlign': 'center', 'padding': '50px'})
        
        # محاسبه سهم بازار در زمان‌های مختلف
        trend_data = []
        for (year, month), group in data.groupby(['سال', 'ماه']):
            bandar_volume = group['حجم کل معامله شده بر حسب تن'].sum()
            bandar_revenue = group['درآمد'].sum()
            
            # داده‌های کل بازار برای این بازه زمانی
            market_period = market_data[
                (market_data['سال'] == year) & 
                (market_data['ماه'] == month)
            ]
            total_market_volume = market_period['حجم کل معامله شده بر حسب تن'].sum()
            total_market_revenue = market_period['درآمد'].sum()
            
            market_share_volume = (bandar_volume / total_market_volume * 100) if total_market_volume > 0 else 0
            market_share_revenue = (bandar_revenue / total_market_revenue * 100) if total_market_revenue > 0 else 0
            
            trend_data.append({
                'سال': year,
                'ماه': month,
                'تاریخ': f"{year}/{month}",
                'درآمد': bandar_revenue,
                'حجم کل معامله شده بر حسب تن': bandar_volume,
                'nerkh': group['nerkh'].mean(),
                'سهم بازار حجمی': market_share_volume,
                'سهم بازار ریالی': market_share_revenue
            })
        
        trend_df = pd.DataFrame(trend_data)
        
        # نمودار روند درآمد
        fig_revenue = px.line(
            trend_df,
            x='تاریخ',
            y='درآمد',
            title='📈 روند درآمدی پتروشیمی بندرامام',
            markers=True,
            color_discrete_sequence=[COLOR_PALETTE[0]]
        )
        fig_revenue.update_layout(
            template='plotly_white',
            height=300,
            font=dict(family='Vazir', size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        # نمودار روند حجم
        fig_volume = px.bar(
            trend_df,
            x='تاریخ',
            y='حجم کل معامله شده بر حسب تن',
            title='📊 روند حجم معاملات ماهانه',
            color='حجم کل معامله شده بر حسب تن',
            color_continuous_scale='Blues'
        )
        fig_volume.update_layout(
            template='plotly_white',
            height=300,
            font=dict(family='Vazir', size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        # نمودار روند سهم بازار حجمی
        fig_market_share_volume = px.line(
            trend_df,
            x='تاریخ',
            y='سهم بازار حجمی',
            title='🥧 روند سهم بازار (حجمی)',
            markers=True,
            color_discrete_sequence=[COLOR_PALETTE[2]]
        )
        fig_market_share_volume.update_layout(
            template='plotly_white',
            height=300,
            font=dict(family='Vazir', size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        # نمودار روند سهم بازار ریالی
        fig_market_share_revenue = px.line(
            trend_df,
            x='تاریخ',
            y='سهم بازار ریالی',
            title='💰 روند سهم بازار (ریالی)',
            markers=True,
            color_discrete_sequence=[COLOR_PALETTE[3]]
        )
        fig_market_share_revenue.update_layout(
            template='plotly_white',
            height=300,
            font=dict(family='Vazir', size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        return html.Div([
            html.Div(className="grid-container", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-header", children="روند درآمد"),
                    html.Div(className="card-body", children=[
                        dcc.Graph(figure=fig_revenue)
                    ])
                ]),
                html.Div(className="card", children=[
                    html.Div(className="card-header", children="روند حجم معاملات"),
                    html.Div(className="card-body", children=[
                        dcc.Graph(figure=fig_volume)
                    ])
                ])
            ]),
            html.Div(className="grid-container", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-header", children="روند سهم بازار (حجمی)"),
                    html.Div(className="card-body", children=[
                        dcc.Graph(figure=fig_market_share_volume)
                    ])
                ]),
                html.Div(className="card", children=[
                    html.Div(className="card-header", children="روند سهم بازار (ریالی)"),
                    html.Div(className="card-body", children=[
                        dcc.Graph(figure=fig_market_share_revenue)
                    ])
                ])
            ]),
            html.Div(className=f"callout {'success' if len(trend_df) > 1 and trend_df['سهم بازار حجمی'].iloc[-1] >= trend_df['سهم بازار حجمی'].iloc[0] else 'warning'}",
                      children=(
                          f"سهم بازار حجمی بندرامام از {trend_df['سهم بازار حجمی'].iloc[0]:.1f}% در ابتدای دوره "
                          f"به {trend_df['سهم بازار حجمی'].iloc[-1]:.1f}% در انتهای دوره رسیده است."
                      ) if len(trend_df) > 1 else "برای مشاهده روند، بازه زمانی بیشتری را انتخاب کنید."
            )
        ])
        
    except Exception as e:
        print(f"خطا در تحلیل روند: {e}")
        return html.Div("خطا در تحلیل روند")

def create_financial_analysis(data, analysis):
    """تحلیل مالی مبتنی بر داده - رشد ماهانه، تمرکز درآمد و نوسان قیمت"""
    try:
        if data.empty:
            return html.Div("داده‌ای برای تحلیل موجود نیست", style={'textAlign': 'center', 'padding': '50px'})
        
        # آمارهای مالی
        total_revenue = data['درآمد'].sum()
        avg_price = data['nerkh'].mean()
        total_volume = data['حجم کل معامله شده بر حسب تن'].sum()
        
        # روند ماهانه درآمد برای محاسبه رشد
        monthly_revenue = data.groupby(['سال', 'ماه'])['درآمد'].sum().reset_index().sort_values(['سال', 'ماه'])
        if len(monthly_revenue) > 1:
            first_rev = monthly_revenue['درآمد'].iloc[0]
            last_rev = monthly_revenue['درآمد'].iloc[-1]
            revenue_growth = ((last_rev - first_rev) / first_rev * 100) if first_rev else 0
        else:
            revenue_growth = 0
        
        # تمرکز درآمد بر روی محصول برتر
        product_revenue = data.groupby('زیرگروه')['درآمد'].sum()
        top_product_share = (product_revenue.max() / total_revenue * 100) if total_revenue and not product_revenue.empty else 0
        
        # نوسان قیمت (ضریب تغییرات)
        price_volatility = (data['nerkh'].std() / avg_price * 100) if avg_price else 0
        
        # کارت‌های مالی
        financial_cards = [
            html.Div(className="stat-card", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div("💰", className="stat-icon")
                ]),
                html.Div(f"{total_revenue:,.0f}", className="stat-value"),
                html.Div("درآمد کل دوره (میلیون ریال)", className="stat-label")
            ]),
            html.Div(className="stat-card", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div(f"{revenue_growth:+.1f}%", className=f"stat-badge {'positive' if revenue_growth >= 0 else 'negative'}"),
                    html.Div("📈", className="stat-icon")
                ]),
                html.Div(f"{revenue_growth:+.1f}%", className="stat-value"),
                html.Div("رشد درآمد از ابتدا تا انتهای دوره", className="stat-label")
            ]),
            html.Div(className="stat-card", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div(f"{top_product_share:.1f}%", className="stat-badge neutral"),
                    html.Div("🎯", className="stat-icon")
                ]),
                html.Div(f"{top_product_share:.1f}%", className="stat-value"),
                html.Div("تمرکز درآمد روی محصول برتر", className="stat-label")
            ]),
            html.Div(className="stat-card", children=[
                html.Div(className="stat-card-top", children=[
                    html.Div(f"{price_volatility:.1f}%", className=f"stat-badge {'negative' if price_volatility > 15 else 'neutral'}"),
                    html.Div("📉", className="stat-icon")
                ]),
                html.Div(f"{price_volatility:.1f}%", className="stat-value"),
                html.Div("نوسان قیمت (ضریب تغییرات)", className="stat-label")
            ])
        ]
        
        insights_text = []
        insights_text.append(
            f"درآمد شرکت در این دوره {'رشد' if revenue_growth >= 0 else 'کاهش'} "
            f"{abs(revenue_growth):.1f}% داشته است."
        )
        if top_product_share > 50:
            insights_text.append(f"بیش از نیمی از درآمد ({top_product_share:.1f}%) به یک محصول وابسته است که ریسک تمرکز را افزایش می‌دهد.")
        else:
            insights_text.append(f"سبد محصولات نسبتاً متنوع است و محصول برتر تنها {top_product_share:.1f}% از درآمد را تشکیل می‌دهد.")
        if price_volatility > 15:
            insights_text.append(f"نوسان قیمت در این دوره بالا بوده ({price_volatility:.1f}%) که می‌تواند ناشی از تغییرات نرخ ارز یا محصول باشد.")
        else:
            insights_text.append(f"قیمت‌گذاری در این دوره نسبتاً باثبات بوده است (نوسان {price_volatility:.1f}%).")
        
        return html.Div([
            html.Div(className="grid-container", children=financial_cards),
            html.Div(className="card", children=[
                html.Div(className="card-header", children="💎 خلاصه تحلیلی عملکرد مالی"),
                html.Div(className="card-body", children=[
                    html.Div(className="insight-card", children=[html.Div(t, className="insight-title")])
                    for t in insights_text
                ])
            ])
        ])
        
    except Exception as e:
        print(f"خطا در تحلیل مالی: {e}")
        return html.Div("خطا در تحلیل مالی")

# =============================================================================
# تنظیمات اجرا
# =============================================================================
