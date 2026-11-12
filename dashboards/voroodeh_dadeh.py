#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8

import base64
import pandas as pd
import io
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import NullPool
from core import server
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import threading
import webbrowser
import time
import sys
import os
import io
import multiprocessing
from datetime import datetime

# =============================================================================
# تنظیمات اولیه
# =============================================================================

META = {
    'name': 'voroodeh_dadeh',
    'description': 'ورود داده‌ها (اکسل → پایگاه داده) و خروجی اکسل از جدول‌ها',
    'category': 'ورود داده',
    'icon': '🗂️',
    'allowed_users': [],
}

app = dash.Dash(__name__, server=server, url_base_pathname='/d/voroodeh_dadeh/')
# نمایش پیام خطای کال‌بک‌ها (مثلاً ۴۱۳/۵۰۴/۵۰۰) در گوشه صفحه، بدون فعال‌کردن حالت debug
app.enable_dev_tools(debug=False, dev_tools_ui=True, dev_tools_props_check=False,
                     dev_tools_hot_reload=False, dev_tools_serve_dev_bundles=False)
app.title = "سیستم ورود و خروجی اطلاعات"

# تنظیمات نوار پیشرفت
LOADING_STEPS = [
    "راه‌اندازی سیستم...",
    "بارگذاری رابط کاربری...",
    "آماده‌سازی فرم‌ها...",
    "اتصال به پایگاه داده...",
    "سیستم آماده استفاده!"
]

PROGRESS_INTERVAL = 400
PROGRESS_STEP = 2

# =============================================================================
# استایل CSS
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
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
                direction: rtl;
            }
            
            .loading-container {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
            }
            
            .loading-title {
                font-size: 2.5em;
                margin-bottom: 20px;
                font-weight: 300;
            }
            
            .loading-subtitle {
                font-size: 1.2em;
                margin-bottom: 40px;
                opacity: 0.8;
            }
            
            .progress-container {
                width: 400px;
                height: 10px;
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                margin: 20px 0;
                overflow: hidden;
            }
            
            .progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #4CAF50, #45a049);
                border-radius: 5px;
                transition: width 0.5s ease;
                position: relative;
            }
            
            .progress-bar::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
                animation: shimmer 2s infinite;
            }
            
            @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }
            
            .progress-text {
                font-size: 1.3em;
                margin-top: 15px;
                font-weight: 500;
            }
            
            .loading-steps {
                margin-top: 30px;
                text-align: center;
            }
            
            .step {
                opacity: 0.6;
                margin: 8px 0;
                font-size: 1.1em;
                transition: opacity 0.3s ease;
            }
            
            .step.active {
                opacity: 1;
                font-weight: 500;
                color: #4CAF50;
            }
            
            .main-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .form-container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            
            .form-title {
                color: #333;
                font-size: 2em;
                margin-bottom: 20px;
                font-weight: 300;
                text-align: center;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            .form-label {
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                color: #555;
            }
            
            .preview-container {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-top: 20px;
            }
            
            .message-success {
                background: #4CAF50;
                color: white;
                padding: 12px 20px;
                border-radius: 5px;
                margin: 10px 0;
            }
            
            .message-error {
                background: #f44336;
                color: white;
                padding: 12px 20px;
                border-radius: 5px;
                margin: 10px 0;
            }
            
            .message-info {
                background: #2196F3;
                color: white;
                padding: 12px 20px;
                border-radius: 5px;
                margin: 10px 0;
            }
            
            .tab-container {
                margin-bottom: 20px;
            }
            
            .tab-buttons {
                display: flex;
                border-bottom: 2px solid #e0e0e0;
                margin-bottom: 20px;
            }
            
            .tab-button {
                padding: 12px 24px;
                background: none;
                border: none;
                cursor: pointer;
                font-size: 16px;
                border-bottom: 3px solid transparent;
                transition: all 0.3s ease;
            }
            
            .tab-button.active {
                border-bottom: 3px solid #2196F3;
                color: #2196F3;
                font-weight: 500;
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
            }
            
            .button-group {
                display: flex;
                gap: 10px;
                margin-top: 20px;
            }
            
            .btn {
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                transition: background 0.3s ease;
                flex: 1;
            }
            
            .btn-primary {
                background: #2196F3;
                color: white;
            }
            
            .btn-success {
                background: #4CAF50;
                color: white;
            }
            
            .btn-warning {
                background: #FF9800;
                color: white;
            }
            
            .btn-danger {
                background: #f44336;
                color: white;
            }
            
            .btn:hover {
                opacity: 0.9;
            }
        </style>
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
# تابع تمیزکاری داده‌ها
# =============================================================================

def clean_data(df, data_type, selected_month, selected_year, sheet_name=None):
    if data_type == "cost_book":
        back = df.index[df['عوامل هزينه'] == "محصول"].tolist()[0]
        forward = df.index[(df['واحد'] == "جمع") | (df['مقدار'] == "جمع")].tolist()[0]
        df = df.iloc[back+1:forward]
        df["month"] = selected_month
        df["year"] = selected_year
     
    if data_type == "sales":
        df.rename(columns={'Unnamed: 1': '2'}, inplace=True)
        
        s_dakheli_b=df.iloc[0:37,[1,3,4,5]]
        s_dakheli_b.rename(columns={'2': "2",'مقدار(تن)':'q' ,'نرخ (ريال)':'rate' ,'مبلغ (ريال)':'price' }, inplace=True)
        s_dakheli_b['type_s']="داخلی"  
        s_dakheli_b['type_s_s']="بین مجتمعی"
        
        s_dakheli_bo=df.iloc[0:37,[1,7,8,9]]
        s_dakheli_bo.rename(columns={'2': "2",'مقدار(تن).1':'q' ,'نرخ (ريال).1':'rate' ,'مبلغ (ريال).1':'price' }, inplace=True)
        s_dakheli_bo['type_s']="داخلی"  
        s_dakheli_bo['type_s_s']="بورسی"
        
        s_dakheli_bot=df.iloc[0:37,[1,11,12,13]]
        s_dakheli_bot.rename(columns={'2': "2",'مقدار(تن).2':'q' ,'نرخ (ريال).2':'rate' ,'مبلغ (ريال).2':'price' }, inplace=True)
        s_dakheli_bot['type_s']="داخلی"  
        s_dakheli_bot['type_s_s']="سایر"
        
        s_saderati_tank=df.iloc[0:37,[1,19,23,24]]
        s_saderati_tank.rename(columns={'2': "2",'مقدار(تن).4':'q' ,'نرخ (ريال).3':'rate' ,'مبلغ (ريال).4':'price' }, inplace=True)
        s_saderati_tank['type_s']="صادراتی"  
        s_saderati_tank['type_s_s']="تانکر"
        
        s_saderati_keshti=df.iloc[0:37,[1,26,30,31]]
        s_saderati_keshti.rename(columns={'2': "2",'مقدار(تن).5':'q' ,'نرخ (ريال).4':'rate' ,'مبلغ (ريال).5':'price' }, inplace=True)
        s_saderati_keshti['type_s']="صادراتی"  
        s_saderati_keshti['type_s_s']="کشتی"
        
        df=pd.concat([s_dakheli_b,s_dakheli_bo,s_saderati_tank,s_saderati_keshti])
        df["month"] = selected_month
        df["year"] = selected_year
        
    if data_type == "production":
        df["unit"] = df["نام واحد"].ffill()
        
        ghabl_aza = df.index[(df['محصولات'] == "گاز سوخت وضايعات") & (df["unit"] == "MTBE")].tolist()[0]
        df = df.iloc[:ghabl_aza+1]
        
        replacements = {
            ("گاز سوخت وضايعات", "MTBE"): "گاز سوخت وضايعات MTBE",
            ("گاز سوخت", "NF"): "گاز سوخت وضايعات NF",
            ("گاز سوخت وضايعات", "OL"): "گاز سوخت وضايعات OL",
            ("گاز سوخت وضايعات", "AR"): "گاز سوخت وضايعات AR",
            ("ضايعات و نامرغوب ", "LD"): "ضايعات و نامرغوب LD",
            ("ضايعات و نامرغوب ", "HD"): "ضايعات و نامرغوب HD",
            ("ضايعات و نامرغوب ", "PVC"): "ضايعات و نامرغوب PVC"
        }
        
        for (product, unit), new_name in replacements.items():
            df.loc[(df["محصولات"] == product) & (df["unit"] == unit), "محصولات"] = new_name
        
        total_balancet = df.iloc[:ghabl_aza+1, [1,4,5,-1] ]
        df = total_balancet.iloc[1:]
        df.rename(columns={'محصولات': 'product', 'توليد دوره': 'tolid'}, inplace=True)
        df["month"] = selected_month
        df["year"] = selected_year
        
    if data_type == "internal_consumption":   
        df["واحد"]=df["نام واحد"].ffill()
        ghabl_aza=df.index[(df['محصولات']=="گاز سوخت وضايعات")&(df["واحد"]=="MTBE")].tolist()[0]
        
        df=df.iloc[:ghabl_aza+1 ]
        df_33=df.iloc[1:,1:27]
        
        data=df_33.columns[6:28]
        
        df = pd.melt(df_33, id_vars=['محصولات'], value_vars=data)
        df["month"] = selected_month
        df["year"] = selected_year
        
    if data_type == "external_consumption":
        ghabl_az=df.index[df['شرح خوراك / محصول']=="جمع"].tolist()[0]
        total_balance1=df.iloc[:ghabl_az ,0:21]
        data=total_balance1.columns[5:23]
        df=pd.melt(total_balance1, id_vars=['شرح خوراك / محصول'], value_vars=data)
        df["month"] = selected_month
        df["year"] = selected_year
        
    if data_type == "energy_consumption":
        # تمیزکاری جدید برای انرژی
        # نامگذاری ستون محصول
        if 'Unnamed: 1' in df.columns:
            df.rename(columns={'Unnamed: 1': 'product'}, inplace=True)
        
        # پیدا کردن ستون جمع و نگه داشتن فقط ستون‌های قبل از آن
        total_indicators = ["جمع "]
        total_position = None
        
        for indicator in total_indicators:
            if indicator in df.columns:
                total_position = df.columns.get_loc(indicator)
                break
        
        if total_position is not None:
            # نگه داشتن فقط ستون‌های قبل از ستون جمع
            df = df.iloc[:, :total_position]
        
        # جایگزینی ستون‌های محاسباتی
        if all(col in df.columns for col in ['BD', 'SR']):
            bd_position = df.columns.get_loc('BD')
            df["BD/SR"] = df["BD"] + df["SR"]
            df = df.drop(['BD', 'SR'], axis=1)
            bd_sr_col = df.pop("BD/SR")
            df.insert(bd_position, "BD/SR", bd_sr_col)
        
        if all(col in df.columns for col in ['NF1&2', 'NF3']):
            nf_position = df.columns.get_loc('NF1&2')
            df["NF"] = df["NF1&2"] + df["NF3"]
            df = df.drop(['NF1&2', 'NF3'], axis=1)
            nf_col = df.pop("NF")
            df.insert(nf_position, "NF", nf_col)
        
        # توقف ردیف‌ها در اولین مقدار NaN در ستون محصول
        if 'product' in df.columns:
            na_mask = df['product'].isna()
            if na_mask.any():
                first_na_index = na_mask.idxmax()
                df = df.iloc[0:first_na_index]
        
        # تبدیل به فرمت long
        if 'product' in df.columns:
            value_columns = [col for col in df.columns if col != 'product']
            df = pd.melt(df, id_vars=['product'], value_vars=value_columns, 
                        var_name='variable', value_name='value')
        
        
        df = df[df['variable'] != 'شرح']
        df["month"] = selected_month
        df["year"] = selected_year
        
    if data_type == "cost_sheets":
        df=df.iloc[1:,[2,4,5,6,7]]
        df.rename(columns={'Unnamed: 2': 'product'}, inplace=True)
        df.columns.values[1]='sale'
        
        df["month"] = selected_month
        df["year"] = selected_year
        
    if data_type == "zayeat_sheets":
        df["واحد"]=df.واحد.ffill()
        df=df.iloc[:17]
        df["month"] = selected_month
        df["year"] = selected_year
        
    if data_type == "production_plan":   
        df=df.iloc[0:,[3,4,5,6,7,8,9,10,11,12,13]]
        df=df.fillna(0)
        df["month"] = selected_month
        df["year"] = selected_year
        
    if data_type == "chemicals": 
        dic_replace34={
            "30621":"LD",
            "30622":"HD",
            "30624":"PVC",
            "30625":"BD",
            "30626":"SR",
        }
        dic_replace={
           "87":"روغن",
           "89":"مواد شیمیایی"
        }
        df=df[(df['تفصیلی']>30620000)&(df['تفصیلی']<30629999)]
        df["oil/shim"]=df["کدکالا"].astype(str).str[:2].replace(dic_replace)
        df["unit"]=df["تفصیلی"].astype(str).str[:5].replace(dic_replace34)
        df=df[["میانگین نرخ","کدکالا","مقدار واقعی","واحد سنجش","شرح","oil/shim","unit" ]]

        df["month"] = selected_month
        df["year"] = selected_year
        
    if data_type == "analys": 
        df=df[["Comp (%Wt)","Average % wt"]]  
        df["month"] = selected_month
        df["year"] = selected_year
         
    if data_type == "nerkh": 
        df=df.iloc[:,[1,2,0,3]]
        df.round()
        df["month"] = selected_month
        df["year"] = selected_year
         
    return df

# =============================================================================
# توابع جدید برای خروجی اکسل
# =============================================================================

def _make_engine():
    """DATABASE_URL (مثلاً Postgres در Neon) → دائمی؛ محلی: فایل SQLite؛ روی Vercel بدون DATABASE_URL: غیرفعال."""
    url = os.environ.get('DATABASE_URL')
    if url:
        if url.startswith('postgres://'):
            url = 'postgresql://' + url[len('postgres://'):]
        if url.startswith('postgresql://'):
            url = 'postgresql+psycopg2://' + url[len('postgresql://'):]
        return create_engine(url, poolclass=NullPool)
    if os.environ.get('VERCEL'):
        return None  # فایل‌سیستم Vercel دائمی نیست؛ ذخیره نمی‌کنیم تا داده بی‌صدا از بین نرود
    path = os.environ.get('SQLITE_PATH') or r'P:\Programs\Report Analyst\ss\my_database.db'
    return create_engine(f'sqlite:///{path}', poolclass=NullPool)

ENGINE = _make_engine()
NO_DB_MESSAGE = "⚠️ پایگاه داده دائمی تنظیم نشده است (متغیر DATABASE_URL). ذخیره‌سازی انجام نشد."


def _quote(name):
    return ENGINE.dialect.identifier_preparer.quote(name)


def get_table_names():
    """دریافت لیست تمام جدول‌های موجود در دیتابیس"""
    try:
        if ENGINE is None:
            return []
        return inspect(ENGINE).get_table_names()
    except Exception as e:
        print(f"خطا در دریافت لیست جدول‌ها: {e}")
        return []


def get_table_data(table_name, month=None, year=None):
    """دریافت داده‌های یک جدول خاص با امکان فیلتر بر اساس ماه و سال"""
    try:
        if ENGINE is None or table_name not in get_table_names():
            return pd.DataFrame()
        quoted = _quote(table_name)
        with ENGINE.connect() as conn:
            if month and year:
                columns = [c['name'] for c in inspect(conn).get_columns(table_name)]
                if 'month' in columns and 'year' in columns:
                    return pd.read_sql_query(text(f"SELECT * FROM {quoted} WHERE month = :m AND year = :y"),
                                             conn, params={'m': month, 'y': year})
            return pd.read_sql_query(text(f"SELECT * FROM {quoted}"), conn)
    except Exception as e:
        print(f"خطا در دریافت داده‌های جدول {table_name}: {e}")
        return pd.DataFrame()


def save_to_db(final_df, table_name, storage_method, month, year):
    quoted = _quote(table_name)
    with ENGINE.begin() as conn:
        if storage_method == "force_create":
            conn.execute(text(f"DROP TABLE IF EXISTS {quoted}"))
            final_df.to_sql(table_name, conn, if_exists="replace", index=False, chunksize=1000)
        elif storage_method == "create":
            if table_name not in inspect(conn).get_table_names():
                final_df.to_sql(table_name, conn, if_exists="replace", index=False, chunksize=1000)
        elif storage_method == "append":
            final_df.to_sql(table_name, conn, if_exists="append", index=False, chunksize=1000)
        elif storage_method == "replace":
            conn.execute(text(f"DELETE FROM {quoted} WHERE month = :m AND year = :y"), {"m": month, "y": year})
            final_df.to_sql(table_name, conn, if_exists="append", index=False, chunksize=1000)


def export_to_excel(table_names, selected_tables, month=None, year=None):
    """ایجاد فایل اکسل از جدول‌های انتخاب شده"""
    try:
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for table_name in selected_tables:
                if table_name in table_names:
                    df = get_table_data(table_name, month, year)
                    if not df.empty:
                        # نام شیت را کوتاه می‌کنیم (حداکثر 31 کاراکتر برای اکسل)
                        sheet_name = table_name.replace('_data', '')[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        output.seek(0)
        return output
    except Exception as e:
        print(f"خطا در ایجاد فایل اکسل: {e}")
        return None

# =============================================================================
# لی‌اوت اصلی
# =============================================================================

app.layout = html.Div([
    # صفحه بارگذاری
    html.Div(id="loading-screen", children=[
        html.Div(className="loading-container", children=[
            html.H1("سیستم ورود و خروجی اطلاعات", className="loading-title"),
            html.P("در حال راه‌اندازی سیستم...", className="loading-subtitle"),
            
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
    
    # محتوای اصلی
    html.Div(id="main-content", style={'display': 'none'}, children=[
        html.Div(className="main-container", children=[
            # تب‌ها
            html.Div(className="tab-container", children=[
                html.Div(className="tab-buttons", children=[
                    html.Button("ورود اطلاعات", id="tab-input-btn", className="tab-button active"),
                    html.Button("خروجی اکسل", id="tab-export-btn", className="tab-button")
                ]),
                
                # تب ورود اطلاعات
                html.Div(id="tab-input", className="tab-content active", children=[
                    html.Div(className="form-container", children=[
                        html.H1("سیستم ورود اطلاعات", className="form-title"),
                        
                        html.Div(className="form-group", children=[
                            html.Label("نوع داده:", className="form-label"),
                            dcc.Dropdown(
                                id='data-type-dropdown',
                                options=[
                                    {'label': 'دفترچه بهای تمام شده', 'value': 'cost_book'},
                                    {'label': 'فروش', 'value': 'sales'},
                                    {'label': 'تولید', 'value': 'production'},
                                    {'label': 'مصرف داخلی', 'value': 'internal_consumption'},
                                    {'label': 'مصرف خارجی', 'value': 'external_consumption'},
                                    {'label': 'مصرف انرژی', 'value': 'energy_consumption'},
                                    {'label': 'شیت ها', 'value': 'cost_sheets'},
                                    {'label': 'ضایعات', 'value': 'zayeat_sheets'},
                                    {'label': 'برنامه تولید', 'value': 'production_plan'},
                                    {'label': 'مواد شیمیایی', 'value': 'chemicals'},
                                    {'label': 'انالیز خوراک مناطق', 'value': 'analys'},
                                    {'label': 'نرخ ها', 'value': 'nerkh'},
                                    {'label': 'سایر', 'value': 'other'}
                                ],
                                value='cost_book',
                                style={'width': '100%'}
                            )
                        ]),
                        
                        html.Div(className="form-group", children=[
                            html.Label("ماه:", className="form-label"),
                            dcc.Dropdown(
                                id='month-dropdown',
                                options=[{'label': str(i), 'value': str(i)} for i in range(1, 13)],
                                value='1',
                                style={'width': '100%'}
                            )
                        ]),
                        
                        html.Div(className="form-group", children=[
                            html.Label("سال:", className="form-label"),
                            dcc.Dropdown(
                                id='year-dropdown',
                                options=[{'label': str(i), 'value': str(i)} for i in range(1370, 1500)],
                                value='1403',
                                style={'width': '100%'}
                            )
                        ]),
                        
                        html.Div(id='sheet-name-container', className="form-group", children=[
                            html.Label("نام شیت:", className="form-label"),
                            dcc.Input(id='sheet-name', type='text', value='', style={'width': '100%'})
                        ]),
                        
                        html.Div(className="form-group", children=[
                            dcc.Upload(
                                id='upload-data',
                                children=html.Button("بارگذاری فایل(های) اکسل", style={
                                    'width': '100%', 
                                    'padding': '12px',
                                    'background': '#4CAF50',
                                    'color': 'white',
                                    'border': 'none',
                                    'borderRadius': '5px',
                                    'cursor': 'pointer',
                                    'fontSize': '16px'
                                }),
                                multiple=True
                            )
                        ]),
                        
                        html.Div(className="form-group", children=[
                            html.Label("روش ذخیره‌سازی:", className="form-label"),
                            dcc.RadioItems(
                                id='storage-method',
                                options=[
                                    {'label': 'ایجاد جدول جدید', 'value': 'create'},
                                    {'label': 'جایگزینی جدول موجود', 'value': 'replace'},
                                    {'label': 'اضافه کردن به جدول موجود', 'value': 'append'},
                                    {'label': 'ایجاد دوباره (Force Create)', 'value': 'force_create'}
                                ],
                                value='create',
                                labelStyle={'display': 'block', 'margin': '5px 0'}
                            )
                        ]),
                        
                        html.Div(className="button-group", children=[
                            html.Button('ذخیره‌سازی داده‌ها', id='save-button', n_clicks=0, className='btn btn-primary'),
                        ]),
                        
                        html.Div(id="output-message"),
                        
                        html.Hr(),
                        
                        html.Div(id='data-preview')
                    ])
                ]),
                
                # تب خروجی اکسل
                html.Div(id="tab-export", className="tab-content", children=[
                    html.Div(className="form-container", children=[
                        html.H1("خروجی اکسل از دیتابیس", className="form-title"),
                        
                        html.Div(className="form-group", children=[
                            html.Label("جدول‌های موجود در دیتابیس:", className="form-label"),
                            dcc.Checklist(
                                id='table-checklist',
                                options=[],
                                value=[],
                                labelStyle={'display': 'block', 'margin': '5px 0'}
                            )
                        ]),
                        
                        html.Div(className="form-group", children=[
                            html.Label("فیلتر بر اساس ماه (اختیاری):", className="form-label"),
                            dcc.Dropdown(
                                id='export-month-dropdown',
                                options=[{'label': str(i), 'value': str(i)} for i in range(1, 13)],
                                value=None,
                                style={'width': '100%'}
                            )
                        ]),
                        
                        html.Div(className="form-group", children=[
                            html.Label("فیلتر بر اساس سال (اختیاری):", className="form-label"),
                            dcc.Dropdown(
                                id='export-year-dropdown',
                                options=[{'label': str(i), 'value': str(i)} for i in range(1370, 1500)],
                                value=None,
                                style={'width': '100%'}
                            )
                        ]),
                        
                        html.Div(className="button-group", children=[
                            html.Button('بارگذاری مجدد جدول‌ها', id='reload-tables-btn', n_clicks=0, className='btn btn-warning'),
                            html.Button('انتخاب همه', id='select-all-btn', n_clicks=0, className='btn btn-primary'),
                            html.Button('لغو انتخاب همه', id='deselect-all-btn', n_clicks=0, className='btn btn-primary'),
                        ]),
                        
                        html.Div(className="button-group", children=[
                            html.Button('خروجی اکسل از جدول‌های انتخاب شده', id='export-excel-btn', n_clicks=0, className='btn btn-success'),
                        ]),
                        
                        html.Div(id="export-message"),
                        
                        html.Div(id="export-preview")
                    ])
                ])
            ])
        ])
    ]),
    
    # کامپوننت‌های مخفی برای دانلود
    dcc.Download(id="download-excel"),
    
    # تایمر پیشرفت
    dcc.Interval(
        id='progress-interval',
        interval=PROGRESS_INTERVAL,
        n_intervals=0,
        max_intervals=int(100/PROGRESS_STEP)
    )
])

# =============================================================================
# کنترل نوار پیشرفت
# =============================================================================

@app.callback(
    [Output('progress-bar', 'style'),
     Output('progress-text', 'children'),
     Output('loading-screen', 'style'),
     Output('main-content', 'style')] + 
    [Output(f'step-{i}', 'className') for i in range(len(LOADING_STEPS))],
    Input('progress-interval', 'n_intervals')
)
def update_progress(n):
    progress = min(n * PROGRESS_STEP, 100)
    current_step = min(int(progress / (100/len(LOADING_STEPS))), len(LOADING_STEPS) - 1)
    
    # تنظیم مراحل
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
            *step_classes
        )
    else:
        return (
            {'width': '100%'},
            "100% - آماده!",
            {'display': 'none'},
            {'display': 'block'},
            *["step active"] * len(LOADING_STEPS)
        )

# =============================================================================
# کنترل تب‌ها
# =============================================================================

@app.callback(
    [Output('tab-input', 'className'),
     Output('tab-export', 'className'),
     Output('tab-input-btn', 'className'),
     Output('tab-export-btn', 'className')],
    [Input('tab-input-btn', 'n_clicks'),
     Input('tab-export-btn', 'n_clicks')]
)
def switch_tab(input_clicks, export_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "tab-content active", "tab-content", "tab-button active", "tab-button"
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'tab-input-btn':
        return "tab-content active", "tab-content", "tab-button active", "tab-button"
    elif button_id == 'tab-export-btn':
        return "tab-content", "tab-content active", "tab-button", "tab-button active"
    
    return "tab-content active", "tab-content", "tab-button active", "tab-button"

# =============================================================================
# کنترل فرم ورود اطلاعات
# =============================================================================

# نمایش فیلد sheet-name فقط برای حالت‌هایی غیر از cost_book
@app.callback(
    Output('sheet-name-container', 'style'),
    Input('data-type-dropdown', 'value')
)
def toggle_sheet_input(data_type):
    return {'display': 'none'} if data_type == 'cost_book' else {'display': 'block'}

# پردازش فایل‌ها و ذخیره در دیتابیس + نمایش پیش‌نمایش
@app.callback(
    [Output("output-message", "children"),
     Output("data-preview", "children")],
    Input("save-button", "n_clicks"),
    State("upload-data", "contents"),
    State("sheet-name", "value"),
    State("month-dropdown", "value"),
    State("year-dropdown", "value"),
    State("data-type-dropdown", "value"),
    State("storage-method", "value")
)
def process_file(n_clicks, file_contents, sheet_name, selected_month, selected_year, data_type, storage_method):
    if n_clicks == 0 or not file_contents:
        return "", ""

    if data_type != "cost_book" and not sheet_name:
        return html.Div("لطفاً نام شیت را وارد کنید.", className="message-error"), ""

    try:
        dfs = []

        for file_content in file_contents:
            content_type, content_string = file_content.split(',')
            decoded = base64.b64decode(content_string)

            if data_type == "cost_book":
                df = pd.read_excel(io.BytesIO(decoded), skiprows=1, skipfooter=0)
            else:
                if data_type == "sales":
                    skiprows=1
                    skipfooter=0
                if data_type == "production":
                    skiprows=3
                    skipfooter=0
                if data_type == "internal_consumption": 
                    skiprows=3
                    skipfooter=0
                if data_type == "external_consumption": 
                    skiprows=3
                    skipfooter=0  
                    
                if data_type == "energy_consumption":
                    skiprows=3
                    skipfooter=0  
                    
                if data_type == "cost_sheets": 
                    skiprows=9
                    skipfooter=7 
                if data_type == "zayeat_sheets": 
                    skiprows=1
                    skipfooter=0
                if data_type == "production_plan": 
                    skiprows=1
                    skipfooter=0
                if data_type == "chemicals": 
                    skiprows=1
                    skipfooter=0
                if data_type == "analys": 
                    skiprows=6
                    skipfooter=1
                if data_type == "nerkh": 
                    skiprows=0
                    skipfooter=0
                    
                df = pd.read_excel(io.BytesIO(decoded), sheet_name=sheet_name,skiprows=skiprows,skipfooter=skipfooter, engine='openpyxl')

            df = clean_data(df, data_type, selected_month, selected_year, sheet_name)
            dfs.append(df)

        if dfs:
            final_df = pd.concat(dfs, ignore_index=True)
            table_name = f"{data_type}_data"

            if ENGINE is None:
                return html.Div(NO_DB_MESSAGE, className="message-error"), ""
            save_to_db(final_df, table_name, storage_method, selected_month, selected_year)

            preview_table = dash_table.DataTable(
                data=final_df.head(10).to_dict('records'),
                columns=[{"name": i, "id": i} for i in final_df.columns],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'right',
                    'fontFamily': 'Segoe UI',
                    'padding': '10px'
                },
                style_header={
                    'backgroundColor': '#f5f5f5',
                    'fontWeight': 'bold'
                }
            )

            return html.Div(
                f"داده‌های '{data_type}' برای ماه {selected_month} و سال {selected_year} ذخیره شدند!", 
                className="message-success"
            ), preview_table

        else:
            return html.Div("هیچ داده‌ای برای ذخیره یافت نشد.", className="message-error"), ""

    except Exception as e:
        return html.Div(f"خطا در پردازش فایل‌ها: {str(e)}", className="message-error"), ""

# =============================================================================
# کنترل خروجی اکسل
# =============================================================================

@app.callback(
    Output('table-checklist', 'options'),
    Input('reload-tables-btn', 'n_clicks')
)
def load_table_options(n_clicks):
    tables = get_table_names()
    options = [{'label': table, 'value': table} for table in tables]
    return options

@app.callback(
    Output('table-checklist', 'value'),
    [Input('select-all-btn', 'n_clicks'),
     Input('deselect-all-btn', 'n_clicks')],
    State('table-checklist', 'options')
)
def select_deselect_all(select_clicks, deselect_clicks, options):
    ctx = dash.callback_context
    if not ctx.triggered:
        return []
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'select-all-btn':
        return [option['value'] for option in options]
    elif button_id == 'deselect-all-btn':
        return []
    
    return []

@app.callback(
    [Output("export-message", "children"),
     Output("download-excel", "data")],
    Input("export-excel-btn", "n_clicks"),
    [State('table-checklist', 'value'),
     State('export-month-dropdown', 'value'),
     State('export-year-dropdown', 'value')]
)
def export_data(n_clicks, selected_tables, month, year):
    if n_clicks == 0:
        return "", None
    
    if not selected_tables:
        return html.Div("لطفاً حداقل یک جدول را انتخاب کنید.", className="message-error"), None
    
    try:
        table_names = get_table_names()
        excel_file = export_to_excel(table_names, selected_tables, month, year)
        
        if excel_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_export_{timestamp}.xlsx"
            
            message = html.Div(
                f"فایل اکسل با موفقیت ایجاد شد! {len(selected_tables)} جدول در فایل ذخیره شد.",
                className="message-success"
            )
            
            return message, dcc.send_bytes(excel_file.read(), filename=filename)
        else:
            return html.Div("خطا در ایجاد فایل اکسل.", className="message-error"), None
            
    except Exception as e:
        return html.Div(f"خطا در ایجاد خروجی: {str(e)}", className="message-error"), None

# =============================================================================
# تنظیمات اجرا
# =============================================================================
