#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import threading
import webbrowser
import time
import sys
import os
import io
import multiprocessing
import math
import functools
from core import server


#if getattr(sys, 'frozen', False):
    # اگر از PyInstaller استفاده شده
    #base_path = sys._MEIPASS
    
    # تنظیم stdout/stderr برای PyInstaller
    #if sys.stdout is None:
        #sys.stdout = io.StringIO()
    #if sys.stderr is None:
        #sys.stderr = io.StringIO()
        
    # تنظیم multiprocessing برای PyInstaller
    #multiprocessing.freeze_support()
#else:
    #base_path = os.path.dirname(os.path.abspath(__file__))

pio.templates.default = "plotly_white"

# ایجاد اپلیکیشن Dash
META = {
    'name': 'holding_report',
    'description': 'تحلیل عملکرد مالی، تولید و فروش هلدینگ',
    'category': 'عمومی',
    'icon': '📊',
    'allowed_users': [],
}

app = dash.Dash(__name__, server=server, url_base_pathname='/d/holding_report/')

# مسیر فایل‌های داده: ۱) متغیر محیطی  ۲) data/holding_report/ در پروژه  ۳) مسیر قدیمی درایو P (فقط اجرای محلی)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _data_path(env_name, filename, old_path):
    p = os.environ.get(env_name) or os.path.join(_REPO_ROOT, 'data', 'holding_report', filename)
    if not os.path.exists(p) and os.path.exists(old_path):
        p = old_path
    return p


REPORT_XLSM = _data_path('HOLDING_REPORT_XLSM', 'report.xlsm', r'P:\Programs\Report Analyst\holding_report\report.xlsm')
DIM_XLSX = _data_path('HOLDING_DIM_XLSX', 'dim_p_h.xlsx', r'P:\Programs\Report Analyst\dim\dim_p_h.xlsx')
app.title = "تحلیل عملکرد بندر امام"

# تنظیمات نوار پیشرفت
LOADING_STEPS = [
    "اتصال به فایل Excel...",
    "بارگذاری داده ها ...",
    "پردازش اطلاعات ...",
    "ایجاد داشبورد ‌ ...",
    "تکمیل داشبورد مالی..."
]

PROGRESS_INTERVAL = 400  # میلی‌ثانیه
PROGRESS_STEP = 2       # درصد در هر مرحله


app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}te
        <style>
            body {
                font-family: 'Vazir', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
                margin: 0;
                padding: 0;
                
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
                height: 12px;
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                margin: 20px 0;
                overflow: hidden;
            }
            
            .progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #4CAF50, #45a049);
                border-radius: 6px;
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
            
            .dashboard-container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
                min-height: 100vh;
            }
            
            .dashboard-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                margin-bottom: 30px;
                text-align: center;
                color: white;
            }
            
            .dashboard-title {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: bold;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            
            .control-panel {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                margin-bottom: 40px;
            }
            
            .kpi-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .status-message {
                position: fixed;
                top: 20px;
                right: 20px;
                background: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                z-index: 1000;
                animation: slideIn 0.5s ease;
            }
            
            @keyframes slideIn {
                from { transform: translateX(100%); }
                to { transform: translateX(0); }
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


items = [
    'درآمدهای عملیاتی',
    'بهاي تمام شده درآمدهای عملیاتی',
    'سود ناخالص',
    'سود ( زیان ) عملیاتی',
    'هزينه هاي فروش، اداري و عمومي',
    'هزینه های مالی',
    'سود ( زیان ) خالص'
]

negative_items = [
    'بهاي تمام شده درآمدهای عملیاتی',
    'هزينه هاي فروش، اداري و عمومي',
    'هزینه های مالی'
]


icons = {
    'درآمدهای عملیاتی': '💼',
    'بهاي تمام شده درآمدهای عملیاتی': '🧾',
    'سود ناخالص': '📊',
    'هزينه هاي فروش، اداري و عمومي': '🏢',
    'هزینه های مالی': '💳',
    'سود ( زیان ) خالص': '💰',
    'سود پایه هر سهم': '📈',
    # آیتم‌های بهای تمام شده
    'مواد مستقیم مصرفي': '🏭',
    'دستمزد مستقیم': '👥',
    'سربار ساخت': '⚙️',
    'هزینه های جذب نشده در تولید': '📉',
    '( افزایش ) کاهش در موجودي کالای ساخته شده': '📦'
}


overhead_icons = {
    'دستمزد غیر مستقیم': '👤',
    'مواد غير مستقيم': '🧰',
    'تعميرات ونگهداري': '🔧',
    'آب مصرفي': '💧',
    'برق مصرفي': '⚡',
    'گاز مصرفي': '🔥',
    'کالا ، قطعات و ملزومات مصرفی': '📦'
}
icons.update(overhead_icons)
cost_items = [
    'مواد مستقیم مصرفي',
    'دستمزد مستقیم',
    'سربار ساخت',
    'هزینه های جذب نشده در تولید',
    '( افزایش ) کاهش در موجودي کالای ساخته شده'
]

negative_items.extend(cost_items)
overhead_items = [
    'دستمزد غیر مستقیم',
    'مواد غير مستقيم',
    'تعميرات ونگهداري',
    'آب مصرفي',
    'برق مصرفي',
    'گاز مصرفي',
    'کالا ، قطعات و ملزومات مصرفی'
]

negative_items.extend(overhead_items)



admin_items = [
    'هزینه حقوق و دستمزد کارکنان اداری و عمومی',
    'خدمات  پيمانكاري و تخصصی',
    'هزینه حمل',
    'حق العمل كاري وكميسيون فروش',
   'کمک به مراکز فرهنگی و ورزشی و بهداشتی (مسئولیت اجتماعی)','استهلاك دارائيها','کالا ، قطعات و ملزومات مصرفی'
]

admin_icons = {
    '': '💰',
    'هزینه های رفاهی': '🏥',
    'هزینه های آموزش': '📚',
    'هزینه های سفر': '✈️',
    'هزینه های ارتباطات': '📞',
    'هزینه های اداری': '📋',
    'هزینه های حمل و نقل': '🚚'
}
icons.update(admin_icons)


tolid_items = ['مقدار تولید']

negative_items.extend(admin_items)

def load_financial_data():
    """
    بارگذاری داده‌های مالی از فایل Excel
    """
    try:
        xls = pd.ExcelFile(REPORT_XLSM, engine='openpyxl')
        
        df = pd.read_excel(
            xls,
            skiprows=5,
            sheet_name='صورت سود (زیان)'
        ).fillna(0)
        
      
        df.rename(columns={df.columns[1]: "شرح"}, inplace=True)
        df.rename(columns={df.columns[2]: "عملکرد ماه"}, inplace=True)
        df.rename(columns={df.columns[3]: "بودجه ماه"}, inplace=True)
        df.rename(columns={df.columns[5]: "عملکرد سال قبل"}, inplace=True)
        df.rename(columns={df.columns[7]: " عملکرد تا ماه جاری"}, inplace=True)
        df.rename(columns={df.columns[8]: "  بودجه تا ماه جاری"}, inplace=True)
        df.rename(columns={df.columns[10]: "عملکرد تا سال قبل"}, inplace=True)
                
        dfff = pd.read_excel(
            xls,
            skiprows=4,
            sheet_name='ب ت ش کالای فروش رفته'
        ).fillna(0)
        dfff.rename(columns={dfff.columns[1]: "شرح"}, inplace=True)
        dfff.rename(columns={dfff.columns[2]: "عملکرد ماه"}, inplace=True)
        dfff.rename(columns={dfff.columns[3]: "بودجه ماه"}, inplace=True)
        dfff.rename(columns={dfff.columns[5]: "عملکرد سال قبل"}, inplace=True)
        dfff.rename(columns={dfff.columns[7]: " عملکرد تا ماه جاری"}, inplace=True)
        dfff.rename(columns={dfff.columns[8]: "  بودجه تا ماه جاری"}, inplace=True)
        dfff.rename(columns={dfff.columns[10]: "عملکرد تا سال قبل"}, inplace=True)


        dfftf = pd.read_excel(
            xls,
            skiprows=4,
            sheet_name='نقدینگی '
        ).fillna(0)
        dfftf.rename(columns={dfftf.columns[1]: "شرح"}, inplace=True)
        dfftf.rename(columns={dfftf.columns[3]: " برآورد کل سال جاری"}, inplace=True)
        dfkkkk = pd.read_excel(
            xls,
            skiprows=5,
            sheet_name='هزینه های سربار'
        ).fillna(0)

        dfkkkk.rename(columns={dfkkkk.columns[0]: "شرح"}, inplace=True)
        dfkkkk.rename(columns={dfkkkk.columns[1]: "عملکرد ماه"}, inplace=True)
        dfkkkk.rename(columns={dfkkkk.columns[2]: "بودجه ماه"}, inplace=True)
        dfkkkk.rename(columns={dfkkkk.columns[4]: "عملکرد سال قبل"}, inplace=True)
        dfkkkk.rename(columns={dfkkkk.columns[6]: " عملکرد تا ماه جاری"}, inplace=True)
        dfkkkk.rename(columns={dfkkkk.columns[7]: "  بودجه تا ماه جاری"}, inplace=True)
        dfkkkk.rename(columns={dfkkkk.columns[9]: "عملکرد تا سال قبل"}, inplace=True)

        dfkkkkkk = pd.read_excel(
        xls,
        skiprows=5,
        sheet_name='هزینه های عمومی و اداری'
        ).fillna(0)
        
        dfkkkkkk.rename(columns={dfkkkkkk.columns[0]: "شرح"}, inplace=True)
        dfkkkkkk.rename(columns={dfkkkkkk.columns[1]: "عملکرد ماه"}, inplace=True)
        dfkkkkkk.rename(columns={dfkkkkkk.columns[2]: "بودجه ماه"}, inplace=True)
        dfkkkkkk.rename(columns={dfkkkkkk.columns[4]: "عملکرد سال قبل"}, inplace=True)
        dfkkkkkk.rename(columns={dfkkkkkk.columns[6]: " عملکرد تا ماه جاری"}, inplace=True)
        dfkkkkkk.rename(columns={dfkkkkkk.columns[7]: "  بودجه تا ماه جاری"}, inplace=True)
        dfkkkkkk.rename(columns={dfkkkkkk.columns[9]: "عملکرد تا سال قبل"}, inplace=True)

        dfkkkkkker = pd.read_excel(
        xls,
        skiprows=7,
        sheet_name='فروش داخلی و صادراتی'
         ).fillna(0)

        dfkkkkkjjker = pd.read_excel(
        xls,
        skiprows=7,
        sheet_name='فروش داخلی و صادراتی'
        ).fillna(0)
        
        dim_p_h = pd.read_excel(
        DIM_XLSX,
        skiprows=0
        ).fillna(0)
        
        dfkkkkkjjker.rename(columns={dfkkkkkjjker.columns[2]: "شرح"}, inplace=True)
        
        # صادراتی
        saderati = dfkkkkkjjker.iloc[:,[2,21,24,25,28,29,32,51,54,55,58,59,62]]
        saderati["type"] = "صادراتی"
        saderati.rename(columns={
        saderati.columns[1]: "مقدار عملکرد ماه",
        saderati.columns[2]: "مبلغ عملکرد ماه", 
        saderati.columns[3]: "مقدار بودجه ای ماه",
        saderati.columns[4]: "مبلغ بودجه ای ماه",
        saderati.columns[5]: "مقدار ماه سال قبل",
        saderati.columns[6]: "مبلغ ماه سال قبل",
        saderati.columns[7]: "مقدار عملکرد تا ماه",
        saderati.columns[8]: "مبلغ عملکرد تا ماه",
        saderati.columns[9]: "مقدار بودجه ای تا ماه",
        saderati.columns[10]: "مبلغ بودجه ایتا ماه",
        saderati.columns[11]: "مقدار تا ماه سال قبل",
        saderati.columns[12]: "مبلغ تا ماه سال قبل"
        }, inplace=True)
        saderati_ad = saderati.merge(dim_p_h, how='inner', left_on=['شرح'], right_on=['محصولات یک'])
        
        # بورسی
        bours = dfkkkkkjjker.iloc[:,[2,3,5,6,8,9,11,33,35,36,38,39,41]]
        bours["type"] = "بورسی"
        bours.rename(columns={
        bours.columns[1]: "مقدار عملکرد ماه",
        bours.columns[2]: "مبلغ عملکرد ماه",
        bours.columns[3]: "مقدار بودجه ای ماه", 
        bours.columns[4]: "مبلغ بودجه ای ماه",
        bours.columns[5]: "مقدار ماه سال قبل",
        bours.columns[6]: "مبلغ ماه سال قبل",
        bours.columns[7]: "مقدار عملکرد تا ماه",
        bours.columns[8]: "مبلغ عملکرد تا ماه",
        bours.columns[9]: "مقدار بودجه ای تا ماه",
        bours.columns[10]: "مبلغ بودجه ایتا ماه",
        bours.columns[11]: "مقدار تا ماه سال قبل",
        bours.columns[12]: "مبلغ تا ماه سال قبل"
        }, inplace=True)
        bours_ad = bours.merge(dim_p_h, how='inner', left_on=['شرح'], right_on=['محصولات یک'])
        
        # بین مجتمعی
        beyn_mogtamai = dfkkkkkjjker.iloc[:,[2,12,14,15,17,18,20,42,44,45,47,48,50]]
        beyn_mogtamai["type"] = "بین مجتمعی"
        beyn_mogtamai.rename(columns={
        beyn_mogtamai.columns[1]: "مقدار عملکرد ماه",
        beyn_mogtamai.columns[2]: "مبلغ عملکرد ماه",
        beyn_mogtamai.columns[3]: "مقدار بودجه ای ماه",
        beyn_mogtamai.columns[4]: "مبلغ بودجه ای ماه",
        beyn_mogtamai.columns[5]: "مقدار ماه سال قبل",
        beyn_mogtamai.columns[6]: "مبلغ ماه سال قبل",
        beyn_mogtamai.columns[7]: "مقدار عملکرد تا ماه",
        beyn_mogtamai.columns[8]: "مبلغ عملکرد تا ماه",
        beyn_mogtamai.columns[9]: "مقدار بودجه ای تا ماه",
        beyn_mogtamai.columns[10]: "مبلغ بودجه ایتا ماه",
        beyn_mogtamai.columns[11]: "مقدار تا ماه سال قبل",
        beyn_mogtamai.columns[12]: "مبلغ تا ماه سال قبل"
        }, inplace=True)
        beyn_mogtamai_ad = beyn_mogtamai.merge(dim_p_h, how='inner', left_on=['شرح'], right_on=['محصولات یک'])
        
        sale_adju = pd.concat([saderati_ad, bours_ad, beyn_mogtamai_ad])
        
        
        khorak = pd.read_excel(
            xls,
            skiprows=7,
            sheet_name='نرخ خوراک'
        ).fillna(0)



        khorak["نام خوراک"]=khorak["Unnamed: 2"].astype(str)+ '  ' + khorak["Unnamed: 3"].astype(str)
        
        khorak.rename(columns={khorak.columns[14]: "نرخ عملکرد ماه"}, inplace=True)
        khorak.rename(columns={khorak.columns[15]: "مقدار عملکرد ماه"}, inplace=True)
        khorak.rename(columns={khorak.columns[17]: "مبلغ عملکرد ماه"}, inplace=True)
        khorak["نرخ عملکرد ماه"]= khorak["نرخ عملکرد ماه"]/1000000
        
        khorak.rename(columns={khorak.columns[26]: "نرخ بودجه ماه"}, inplace=True)
        khorak.rename(columns={khorak.columns[27]: "مقدار بودجه ماه"}, inplace=True)
        khorak.rename(columns={khorak.columns[29]: "مبلغ بودجه ماه"}, inplace=True)
        khorak["نرخ بودجه ماه"]=khorak["نرخ بودجه ماه"]/1000000
        
        khorak.rename(columns={khorak.columns[38]: "نرخ عملکرد ماه سال قبل"}, inplace=True)
        khorak.rename(columns={khorak.columns[39]: "مقدار عملکرد ماه سال قبل"}, inplace=True)
        khorak.rename(columns={khorak.columns[41]: "مبلغ عملکرد ماه سال قبل"}, inplace=True)
        khorak["نرخ عملکرد ماه سال قبل"]=khorak["نرخ عملکرد ماه سال قبل"]/1000000
        
        khorak.rename(columns={khorak.columns[50]: "نرخ تجمعی عملکرد ماه"}, inplace=True)
        khorak.rename(columns={khorak.columns[51]: "مقدار تجمعی عملکرد ماه"}, inplace=True)
        khorak.rename(columns={khorak.columns[53]: "مبلغ تجمعی عملکرد ماه"}, inplace=True)
        khorak["نرخ تجمعی عملکرد ماه"]=khorak["نرخ تجمعی عملکرد ماه"]/1000000

        
        khorak.rename(columns={khorak.columns[62]: "نرخ تجمعی بودجه ماه"}, inplace=True)
        khorak.rename(columns={khorak.columns[63]: "مقدار تجمعی بودجه ماه"}, inplace=True)
        khorak.rename(columns={khorak.columns[65]: "مبلغ تجمعی بودجه ماه"}, inplace=True)
        khorak["نرخ تجمعی بودجه ماه"]= khorak["نرخ تجمعی بودجه ماه"]/1000000

        
        khorak.rename(columns={khorak.columns[74]: "نرخ تجمعی عملکرد ماه سال قبل"}, inplace=True)
        khorak.rename(columns={khorak.columns[75]: "مقدار تجمعی عملکرد ماه سال قبل"}, inplace=True)
        khorak.rename(columns={khorak.columns[77]: "مبلغ تجمعی عملکرد ماه سال قبل"}, inplace=True)
        khorak["نرخ تجمعی عملکرد ماه سال قبل"]= khorak["نرخ تجمعی عملکرد ماه سال قبل"]/1000000


        khorak=khorak[(~khorak["نام خوراک"].str.contains("0"))]



        tolid_data = pd.read_excel(
        xls,
        skiprows=4,
        sheet_name='تولید محصولات'
        ).fillna(0)

        tolid_data.rename(columns={tolid_data.columns[2]: "نام محصول"}, inplace=True)
        tolid_data.rename(columns={tolid_data.columns[5]: "مقدار عملکرد ماه"}, inplace=True)
        tolid_data.rename(columns={tolid_data.columns[6]: "مقدار بودجه ماه"}, inplace=True)
        tolid_data.rename(columns={tolid_data.columns[8]: "مقدار عملکرد ماه سال قبل"}, inplace=True)
        tolid_data.rename(columns={tolid_data.columns[10]: "مقدار تجمعی عملکرد ماه"}, inplace=True)
        tolid_data.rename(columns={tolid_data.columns[11]: "مقدار تجمعی بودجه ماه"}, inplace=True)
        tolid_data.rename(columns={tolid_data.columns[13]: "مقدار تجمعی عملکرد ماه سال قبل"}, inplace=True)
        
        # Merge with dim data
        tolid_data = tolid_data.merge(dim_p_h, how='inner', left_on=['نام محصول'], right_on=['محصولات یک'])

        baha_and_sod = pd.read_excel(
        xls,
        skiprows=5,
        sheet_name='مقایسه فروش با بهای تمام'
        ).fillna(0)

        baha_and_sod.rename(columns={
            baha_and_sod.columns[2]: "محصولات دو",
            baha_and_sod.columns[4]: "بهای تمام شده دوره جاری",
            baha_and_sod.columns[5]: "سود دوره جاری", 
            baha_and_sod.columns[8]: "بهای تمام شده تا دوره جاری",
            baha_and_sod.columns[9]: "سود تا دوره جاری"
        }, inplace=True)
        baha_and_sod = baha_and_sod[baha_and_sod["محصولات دو"] != 0]

        froosh_kol = pd.read_excel(
            xls,
            skiprows=5,
            sheet_name='مقدار کل فروش'
        ).fillna(0)

        froosh_kol.rename(columns={
            froosh_kol.columns[2]: "محصولات سه",
            froosh_kol.columns[4]: "مقدار فروش ماه",
            froosh_kol.columns[9]: "مقدار فروش تا ماه"
        }, inplace=True)
        froosh_kol = froosh_kol[froosh_kol["محصولات سه"] != 0]

        # ادغام داده‌ها
        baha_and_sod_gg = baha_and_sod.merge(dim_p_h, how='inner', left_on=['محصولات دو'], right_on=['محصولات یک'])
        baha_and_sod_ggg = baha_and_sod_gg.merge(froosh_kol, how='inner', left_on=['محصولات دو'], right_on=['محصولات سه'])


        
        
        return df, dfff, dfftf, dfkkkk, dfkkkkkk,dfkkkkkker,sale_adju,khorak,tolid_data,baha_and_sod_ggg  
        
        
        
    except Exception as e:
        print(f"خطا در بارگذاری فایل: {e}")
        return None,None,None,None,None,None,None,None,None,None

# =============================================================================
# توابع کمکی
# =============================================================================

def money_iconify(value, currency='rial', exchange_rate=1):
    """فرمت عدد به ریال یا دلار"""
    if value == 0:
        return "—"
    
    # Convert from million rials to dollars if needed
    if currency == 'dollar':
        # Convert from million rials to dollars
        dollar_value = (value * 1) / exchange_rate
        # Format dollar values appropriately
        if abs(dollar_value) < 0.01:  # Very small values
            return "~0"
        elif abs(dollar_value) < 1:  # Values less than 1 dollar
            return f"${dollar_value:,.3f}"
        elif abs(dollar_value) < 1_000:  # Values less than 1000 dollars
            return f"${dollar_value:,.2f}"
        else:  # Values 1000 dollars and above
            return f"${dollar_value:,.0f}"
    else:
        # For rial, keep as million rials
        return f"{value:,.0f} میلیون ریال"

def get_column_names(data_type, df):
    """تعیین نام ستون‌های مناسب بر اساس نوع داده و ستون‌های موجود"""
    
    columns = df.columns.tolist()
    
    if data_type == 'current':
        current_col = "عملکرد ماه"
        
        # جستجو برای بودجه ماه جاری
        budget_col = None
        for col in columns:
            if 'بودجه' in str(col) and 'ماه' in str(col):
                budget_col = col
                break
        if not budget_col:
            for col in columns:
                if 'بودجه' in str(col) and len(str(col).split()) <= 3:
                    budget_col = col
                    break
        
        # جستجو برای عملکرد ماه سال قبل
        last_year_col = None
        for col in columns:
            if 'عملکرد' in str(col) and 'قبل' in str(col) and 'سال' in str(col):
                last_year_col = col
                break
        if not last_year_col:
            for col in columns:
                if '1403' in str(col) and len(str(col).split()) <= 4:
                    last_year_col = col
                    break
        
    else:  # cumulative
        # جستجو برای عملکرد تجمعی
        current_col = None
        for col in columns:
            if 'عملکرد' in str(col) and 'تا' in str(col) and 'جاری' in str(col):
                current_col = col
                break
        
        # جستجو برای بودجه تجمعی
        budget_col = None
        for col in columns:
            if 'بودجه' in str(col) and 'تا' in str(col) and 'جاری' in str(col):
                budget_col = col
                break
        
        # جستجو برای عملکرد تجمعی سال قبل
        last_year_col = None
        for col in columns:
            if 'عملکرد' in str(col) and 'تا' in str(col) and 'قبل' in str(col):
                last_year_col = col
                break
    
    return current_col, budget_col, last_year_col

def generate_card(item, threshold, source, data_type, df, currency="rial", current_exchange_rate=1, budget_exchange_rate=1, last_year_exchange_rate=1):
    """ساخت کارت KPI با نوار پیشرفت"""

    
    row = df[df['شرح'].astype(str).str.strip() == item.strip()]
    
    if not row.empty:
        # دریافت نام ستون‌های مناسب
        current_col, budget_col, last_year_col = get_column_names(data_type, df)
        
        # بررسی وجود ستون‌ها - مقادیر اصلی
        actual_original = row[current_col].values[0] if current_col and current_col in df.columns else 0
        budget_original = row[budget_col].values[0] if budget_col and budget_col in df.columns else 0
        last_year_original = row[last_year_col].values[0] if last_year_col and last_year_col in df.columns else 0
        
        # تبدیل به واحد مطلوب
        # تبدیل به واحد مطلوب با نرخ‌های جداگانه
        actual = convert_currency(actual_original, current_exchange_rate, currency)
        budget = convert_currency(budget_original, budget_exchange_rate, currency)
        last_year = convert_currency(last_year_original, last_year_exchange_rate, currency)

        if currency == 'dollar':
            actual = (actual_original / 1) / current_exchange_rate
            budget = (budget_original / 1) / budget_exchange_rate
            last_year = (last_year_original / 1) / last_year_exchange_rate
        else:
            actual = actual_original
            budget = budget_original
            last_year = last_year_original
        # انتخاب مرجع مقایسه
        base = budget if source == 'budget' else last_year
        base_label = "بودجه" if source == 'budget' else "سال قبل"
        
        
        
        
        # محاسبه انحراف با در نظر گیری نوع آیتم - از مقادیر تبدیل شده
        if base != 0:
            raw_deviation = ((actual - base) / base) * 100
            # برای آیتم‌های هزینه، انحراف مثبت یعنی بد و منفی یعنی خوب
            if item.strip() in negative_items:
                deviation = -raw_deviation  # معکوس کردن علامت
            else:
                deviation = raw_deviation
        else:
                deviation = 0
        
        # محاسبه درصد پیشرفت برای نوار - بر اساس منبع انتخاب شده
        if source == 'budget' and budget != 0:
           

            progress_percentage = (actual / budget) * 100
                
                 
            
            progress_label = f"پیشرفت نسبت به بودجه: {progress_percentage:.1f}%"
        elif source == 'last_year' and last_year != 0:
            progress_percentage = (actual / last_year) * 100
            progress_label = f"نسبت به سال قبل: {progress_percentage:.1f}%"
        else:
            progress_percentage = 0
            progress_label = "داده مرجع موجود نیست"
        
        progress_percentage = min(progress_percentage, 150)  # حداکثر 150%


        
        
        # انتخاب گرادینت و رنگ نوار بر اساس میزان انحراف
        if deviation >= threshold:
            gradient = 'linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%)'
            border = '3px solid #00C9FF'
            glow = '0 0 20px rgba(0, 201, 255, 0.5)'
            progress_color = '#00C9FF'
        elif deviation >= 0:
            gradient = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            border = '3px solid #667eea'
            glow = '0 0 20px rgba(102, 126, 234, 0.5)'
            progress_color = '#667eea'
        elif deviation >= -threshold:
            gradient = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
            border = '3px solid #f093fb'
            glow = '0 0 20px rgba(240, 147, 251, 0.5)'
            progress_color = '#f093fb'
        else:
            gradient = 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)'
            border = '3px solid #ff6b6b'
            glow = '0 0 20px rgba(255, 107, 107, 0.5)'
            progress_color = '#ff6b6b'
        
        icon = icons.get(item.strip(), '📎')
        
        # انتخاب آیکون بر اساس نوع آیتم و انحراف
        if item.strip() in negative_items:
            # برای هزینه‌ها: انحراف مثبت = کاهش هزینه = خوب
            arrow = '🚀' if deviation >= threshold else '⬆️' if deviation >= 0 else '⬇️' if deviation >= -threshold else '🔻'
        else:
            # برای درآمدها: انحراف مثبت = افزایش درآمد = خوب
            arrow = '🚀' if deviation >= threshold else '⬆️' if deviation >= 0 else '⬇️' if deviation >= -threshold else '🔻'
        
        # تعیین برچسب نوع داده
        data_label = "دوره فعلی" if data_type == 'current' else "تجمعی"
        
        return html.Div([
            html.Div([
                html.H4(f"{icon} {item}", style={
                    'textAlign': 'center', 
                    'color': '#fff', 
                    'margin': '0 0 10px 0',
                    'fontSize': '13px',
                    'fontWeight': 'bold'
                }),
                html.H2(f"{arrow} {deviation:.4f}%", style={
                    'textAlign': 'center', 
                    'color': '#fff', 
                    'margin': '0 0 10px 0',
                    'fontSize': '22px',
                    'fontWeight': 'bold',
                    'textShadow': '0 2px 4px rgba(0,0,0,0.3)'
                }),
                
                # نوار پیشرفت
                html.Div([
                    html.Div([
                        html.Div(style={
                            'width': f'{min(progress_percentage, 100)}%',
                            'height': '100%',
                            'backgroundColor': progress_color,
                            'borderRadius': '8px',
                            'transition': 'width 0.5s ease',
                            'boxShadow': f'0 0 10px {progress_color}'
                        })
                    ], style={
                        'width': '100%',
                        'height': '8px',
                        'backgroundColor': 'rgba(255,255,255,0.3)',
                        'borderRadius': '8px',
                        'overflow': 'hidden',
                        'margin': '10px 0'
                    }),
                    html.P(progress_label, style={
                        'textAlign': 'center',
                        'color': '#fff',
                        'fontSize': '9px',
                        'margin': '5px 0'
                    })
                ]),
                
                html.P(f"{data_label}: {money_iconify(actual, currency, 1)}", style={
                    'textAlign': 'center', 
                    'color': '#fff', 
                    'margin': '3px 0',
                    'fontSize': '10px'
                }),
                html.P(f"بودجه: {money_iconify(budget, currency, 1)}", style={
                    'textAlign': 'center', 
                    'color': '#fff', 
                    'margin': '3px 0',
                    'fontSize': '10px'
                }),
                html.P(f"سال قبل: {money_iconify(last_year, currency, 1)}", style={
                    'textAlign': 'center', 
                    'color': '#fff', 
                    'margin': '3px 0',
                    'fontSize': '10px'
                })
            ])
        ], style={
            'background': gradient,
            'borderRadius': '20px',
            'padding': '15px',
            'width': '200px',
            'height': '220px',
            'boxShadow': glow,
            'border': border,
            'transition': 'all 0.3s ease',
            'position': 'relative',
            'overflow': 'hidden'
        })
    
    return html.Div([
        html.H4(f"❓ {item}", style={'textAlign': 'center', 'color': '#fff'}),
        html.H3("⛔ داده موجود نیست", style={'textAlign': 'center', 'color': '#fff'}),
        html.P("عملکرد: —", style={'textAlign': 'center', 'color': '#fff'}),
        html.P("بودجه: —", style={'textAlign': 'center', 'color': '#fff'}),
        html.P("سال قبل: —", style={'textAlign': 'center', 'color': '#fff'})
    ], style={
        'background': 'linear-gradient(135deg, #808B96, #566573)',
        'borderRadius': '20px',
        'padding': '15px',
        'width': '200px',
        'height': '220px',
        'boxShadow': '0 0 15px rgba(0,0,0,0.3)'
    })
# =============================================================================
# لی‌اوت اصلی
# =============================================================================

app.layout = html.Div([
    # پیام وضعیت
    html.Div(id="status-message", style={'display': 'none'}),
    
    # صفحه بارگذاری
    html.Div(id="loading-screen", children=[
        html.Div(className="loading-container", children=[
            html.H1("📊 گزارش عملکرد مالی پتروشیمی بندر امام  ", className="loading-title"),
            html.P("در حال بارگذاری اطلاعات ...", className="loading-subtitle"),
            
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
    
    # محتوای داشبورد
    html.Div(id="dashboard-content", style={'display': 'none'}),
    
    # تایمر پیشرفت
    dcc.Interval(
        id='progress-interval',
        interval=PROGRESS_INTERVAL,
        n_intervals=0,
        max_intervals=int(100/PROGRESS_STEP)
    )
])

# =============================================================================
# =============================================================================

financial_data = None
cost_data = None
cash_data = None  #  
overhead_data = None
admin_data = None  # 
sales_data = None
sales_detail_data = None  # در بالای فایل با سایر متغیرهای global
khorak_data = None
tolid_data = None
sood_data=None

_LOAD_LOCK = threading.Lock()
_LOAD_ATTEMPTED = False


def ensure_loaded():
    """داده‌ها را در صورت نبود (مثلاً instance جدید در Vercel) یک‌بار از فایل می‌خواند."""
    global financial_data, cost_data, cash_data, overhead_data, admin_data, sales_data, sales_detail_data, khorak_data, tolid_data, sood_data, _LOAD_ATTEMPTED
    if financial_data is not None or _LOAD_ATTEMPTED:
        return
    with _LOAD_LOCK:
        if financial_data is not None or _LOAD_ATTEMPTED:
            return
        (financial_data, cost_data, cash_data, overhead_data, admin_data, sales_data,
         sales_detail_data, khorak_data, tolid_data, sood_data) = load_financial_data()
        _LOAD_ATTEMPTED = True


def data_callback(*cb_args, **cb_kwargs):
    """مثل app.callback، ولی قبل از اجرای تابع مطمئن می‌شود داده‌ها در این instance بارگذاری شده‌اند."""
    register = app.callback(*cb_args, **cb_kwargs)

    def wrap(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            ensure_loaded()
            return func(*args, **kwargs)
        return register(inner)
    return wrap

# =============================================================================
# کال‌بک‌ها
# =============================================================================

def calculate_exchange_rates(sales_data):
    """محاسبه نرخ تسعیر از داده‌های فروش"""
    exchange_rates = {}
    
    # بررسی ستون‌های موجود
    
    
    try:
        budget_current_rial = sales_data.iloc[:, 28]  # ستون 29 (ریال)
        budget_current_dollar = sales_data.iloc[:, 27]  # ستون 28 (دلار)
        
        month_current_rial = sales_data.iloc[:, 24]   # ستون 25 (ریال)
        month_current_dollar = sales_data.iloc[:, 23]   # ستون 24 (دلار)
        
        month_lastyear_rial = sales_data.iloc[:, 32]  # ستون 30 (ریال)
        month_lastyear_dollar = sales_data.iloc[:, 31]  # ستون 29 (دلار)
        
        budget_tajomi_rial = sales_data.iloc[:, 58]    # ستون 59 (ریال)
        budget_tajomi_dollar = sales_data.iloc[:, 57]    # ستون 58 (دلار)
        
        month_tajomi_rial = sales_data.iloc[:, 54]     # ستون 55 (ریال)
        month_tajomi_dollar = sales_data.iloc[:, 53]     # ستون 54 (دلار)
        
        month_lastyear_tajmoii_rial = sales_data.iloc[:, 62]   # ستون 63 (ریال)
        month_lastyear_tajmoii_dollar = sales_data.iloc[:, 61]   # ستون 62 (دلار)
        
    except Exception as e:
        print(f"خطا در انتخاب ستون‌ها: {e}")
        return {'budget_current': 1, 'month_current': 1, 'month_lastyear': 1, 
                'budget_tajomi': 1, 'month_tajomi': 1, 'month_lastyear_tajmoii': 1}
    
    def calculate_rate(rial_series, dollar_series, section_name):
        valid_rates = []
        
        for idx in range(len(rial_series)):
            try:
                rial_val = float(rial_series.iloc[idx]) if pd.notna(rial_series.iloc[idx]) else 0
                dollar_val = float(dollar_series.iloc[idx]) if pd.notna(dollar_series.iloc[idx]) else 0
                
                if dollar_val > 0 and rial_val > 0:
                    rate = rial_val / dollar_val
                    if 100 <= rate <= 10000:  # فیلتر نرخ‌های غیرمعقول
                        valid_rates.append(rate)
                        
                        
            except Exception as e:
                continue
        
        if valid_rates:
            final_rate = valid_rates[0]  # یا sum(valid_rates) / len(valid_rates) برای میانگین
            
            return final_rate
        else:
            
            return 1  # نرخ پیش‌فرض
    
    exchange_rates['budget_current'] = calculate_rate(budget_current_rial, budget_current_dollar, 'budget_current')
    exchange_rates['month_current'] = calculate_rate(month_current_rial, month_current_dollar, 'month_current')
    exchange_rates['month_lastyear'] = calculate_rate(month_lastyear_rial, month_lastyear_dollar, 'month_lastyear')
    exchange_rates['budget_tajomi'] = calculate_rate(budget_tajomi_rial, budget_tajomi_dollar, 'budget_tajomi')
    exchange_rates['month_tajomi'] = calculate_rate(month_tajomi_rial, month_tajomi_dollar, 'month_tajomi')
    exchange_rates['month_lastyear_tajmoii'] = calculate_rate(month_lastyear_tajmoii_rial, month_lastyear_tajmoii_dollar, 'month_lastyear_tajmoii')
    
    return exchange_rates

def convert_currency(value, exchange_rate, target_currency='rial'):
    if target_currency == 'dollar' and exchange_rate != 0:
        # Convert from million rials to thousand dollars
        return (value * 1) / exchange_rate
    return value
def create_cost_pie_chart(data_type, cost_data, currency='rial', exchange_rate=1):
    """ایجاد نمودار پای برای اجزای بهای تمام شده با تبدیل ارز"""
    pie_items = [
        'مواد مستقیم مصرفي',
        'دستمزد مستقیم', 
        'سربار ساخت'
    ]
    
    pie_data = []
    pie_labels = []
    currency_label = "دلار" if currency == 'dollar' else "میلیون ریال"
    
    for item in pie_items:
        row = cost_data[cost_data['شرح'].astype(str).str.strip() == item.strip()]
        if not row.empty:
            current_col, _, _ = get_column_names(data_type, cost_data)
            value = row[current_col].values[0] if current_col and current_col in cost_data.columns else 0
            if value > 0:
                if currency == 'dollar':
                    converted_value = (value / 1_000) / exchange_rate
                else:
                    converted_value = value
                #converted_value = convert_currency(value, exchange_rate, currency)
                pie_data.append(converted_value)
                pie_labels.append(item)
    
    colors = ['#FF6B9D', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    pie_fig = go.Figure(data=[go.Pie(
        labels=pie_labels,
        values=pie_data,
        marker=dict(colors=colors[:len(pie_data)]),
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>%{value:,.0f}',
        hovertemplate=f'<b>%{{label}}</b><br>مبلغ: %{{value:,.0f}} {currency_label}<br>درصد: %{{percent}}<extra></extra>',
        hole=0.4
    )])
    
    pie_fig.update_layout(
        title=f"ترکیب اجزای بهای تمام شده ({currency_label})",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    return pie_fig

def create_overhead_pie_chart(data_type, overhead_data, currency='rial', exchange_rate=1):
    """ایجاد نمودار پای برای اجزای هزینه‌های سربار با تبدیل ارز"""
    pie_items = [
        'دستمزد غیر مستقیم',
        'مواد غير مستقيم', 
        'تعميرات ونگهداري',
        'گاز مصرفي'
    ]
    
    pie_data = []
    pie_labels = []
    currency_label = "دلار" if currency == 'dollar' else "میلیون ریال"
    
    for item in pie_items:
        row = overhead_data[overhead_data['شرح'].astype(str).str.strip() == item.strip()]
        if not row.empty:
            current_col, _, _ = get_column_names(data_type, overhead_data)
            value = row[current_col].values[0] if current_col and current_col in overhead_data.columns else 0
            if value > 0:
                if currency == 'dollar':
                    converted_value = (value / 1000) / exchange_rate
                else:
                    converted_value = value
                #converted_value = convert_currency(value, exchange_rate, currency)
                pie_data.append(converted_value)
                pie_labels.append(item)
    
    colors = ['#FF9500', '#FF6B9D', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFA07A']
    
    pie_fig = go.Figure(data=[go.Pie(
        labels=pie_labels,
        values=pie_data,
        marker=dict(colors=colors[:len(pie_data)]),
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>%{value:,.0f}',
        hovertemplate=f'<b>%{{label}}</b><br>مبلغ: %{{value:,.0f}} {currency_label}<br>درصد: %{{percent}}<extra></extra>',
        hole=0.4
    )])
    
    pie_fig.update_layout(
        title=f"ترکیب هزینه‌های سربار ({currency_label})",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    return pie_fig



def create_cash_flow_infographic(cash_data, currency='rial', exchange_rate=1):
    """ایجاد کارت‌های پیشرفت اینفوگرافیکی برای نقدینگی با تبدیل ارز"""
    
    cash_items = [
        'پرداختی بابت خوراک',
        'پرداختی به هلدینگ', 
        'سود سهام',
        'بازپرداخت تسهیلات',
        'بازپرداخت بدهی',
        'پرداخت بابت پروژه‌هاي سرمايه‌ايي',
        'سرويس هاي جانبي و يوتيليتي',
        'سود سهام پرداختني',
        'درآمد حاصل ازفروش و دریافتنی های تجاری',
        'هزينه هاي حقوق و دستمزد'
    ]
    
    circles_data = []
    currency_label = "دلار" if currency == 'dollar' else "میلیون ریال"
    
    for i, item in enumerate(cash_items):
        matching_rows = cash_data[
            cash_data['شرح'].astype(str).str.contains(item, case=False, na=False)
        ]
        
        if not matching_rows.empty:
            row = matching_rows.iloc[0]
            
            ytd_value = 0
            forecast_value = 0
            
            for col in cash_data.columns:
                col_str = str(col)
                if 'ابتدای سال' in col_str or 'تا ماه' in col_str:
                    try:
                        ytd_value = float(row[col]) if pd.notna(row[col]) else 0
                    except:
                        ytd_value = 0
                elif 'جاری' in col_str and ('برآورد' in col_str or 'کل سال' in col_str):
                    try:
                        forecast_value = float(row[col]) if pd.notna(row[col]) else 0
                    except:
                        forecast_value = 0
            
            ytd_converted = convert_currency(ytd_value, exchange_rate, currency)
            forecast_converted = convert_currency(forecast_value, exchange_rate, currency)
            
            if forecast_value != 0:
                progress_percent = min((ytd_value / forecast_value * 100), 100)
            else:
                progress_percent = 0
            
            if progress_percent > 0:
                circles_data.append({
                    'title': row['شرح'],
                    'progress': progress_percent,
                    'ytd': ytd_converted,
                    'forecast': forecast_converted
                })
    
    if not circles_data:
        return html.Div([
            html.H3("📊 داده‌های نقدینگی موجود نیست", 
                   style={'textAlign': 'center', 'color': '#6B7280', 'marginTop': '50px'})
        ])
    
    def create_donut_card(item_data):
        progress = item_data['progress']
        if progress >= 90:
            color = '#10B981'
        elif progress >= 70:
            color = '#F59E0B'
        elif progress >= 50:
            color = '#EF4444'
        elif progress >= 30:
            color = '#8B5CF6'
        else:
            color = '#6B7280'
        
        fig = go.Figure(data=[go.Pie(
            values=[progress, 100 - progress],
            hole=0.7,
            marker=dict(
                colors=[color, '#E5E7EB'],
                line=dict(color='white', width=3)
            ),
            showlegend=False,
            hovertemplate=f"<b>{item_data['title']}</b><br>" +
                         f"{progress:.1f}%<br>" +
                         f"تا کنون: {item_data['ytd']:,.0f} {currency_label}<br>" +
                         f"پیش‌بینی: {item_data['forecast']:,.0f} {currency_label}<extra></extra>",
            textinfo='none',
            rotation=90
        )])
        
        fig.add_annotation(
            text=f"<b>{progress:.0f}%</b>",
            x=0.5, y=0.5,
            font=dict(size=24, color=color, family="Vazir"),
            showarrow=False
        )
        
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            height=200,
            width=200
        )
        
        short_title = item_data['title'][:30] + '...' if len(item_data['title']) > 30 else item_data['title']
        
        return html.Div([
            html.H4(short_title, style={
                'textAlign': 'center',
                'color': '#2c3e50',
                'margin': '0 0 10px 0',
                'fontSize': '14px',
                'fontWeight': 'bold'
            }),
            
            dcc.Graph(
                figure=fig,
                config={'displayModeBar': False},
                style={'height': '200px'}
            ),
            
            html.Div([
                html.P(f"تا کنون: {item_data['ytd']:,.0f} {currency_label}", style={
                    'color': '#34495e',
                    'fontSize': '12px',
                    'margin': '5px 0',
                    'textAlign': 'center'
                }),
                html.P(f"پیش‌بینی: {item_data['forecast']:,.0f} {currency_label}", style={
                    'color': '#34495e',
                    'fontSize': '12px',
                    'margin': '5px 0',
                    'textAlign': 'center'
                })
            ])
            
        ], style={
            'background': 'white',
            'borderRadius': '15px',
            'padding': '20px',
            'width': '250px',
            'height': '320px',
            'boxShadow': '0 4px 20px rgba(0,0,0,0.1)',
            'border': f'2px solid {color}',
            'transition': 'all 0.3s ease',
            'margin': '10px'
        })
    
    cards = [create_donut_card(item) for item in circles_data[:8]]
    
    return html.Div([
        html.H4(f"💰 جریان نقدی ({currency_label})", style={
            'textAlign': 'center',
            'color': '#34495e',
            'marginBottom': '20px'
        }),
        html.Div(cards, style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'justifyContent': 'center',
            'gap': '15px',
            'maxWidth': '1200px',
            'margin': '0 auto'
        })
    ])



def create_overhead_pie_chart(data_type, overhead_data, currency='rial', exchange_rate=1):
    """ایجاد نمودار پای برای اجزای هزینه‌های سربار با تبدیل ارز"""
    pie_items = [
        'دستمزد غیر مستقیم',
        'مواد غير مستقيم', 
        'تعميرات ونگهداري',
        'گاز مصرفي'
    ]
    
    pie_data = []
    pie_labels = []
    currency_label = " هزار دلار" if currency == 'dollar' else "میلیون ریال"
    
    for item in pie_items:
        row = overhead_data[overhead_data['شرح'].astype(str).str.strip() == item.strip()]
        if not row.empty:
            current_col, _, _ = get_column_names(data_type, overhead_data)
            value = row[current_col].values[0] if current_col and current_col in overhead_data.columns else 0
            if value > 0:
                if currency == 'dollar':
                    converted_value = (value / 1_000) / exchange_rate
                else:
                    converted_value = value
                #converted_value = convert_currency(value, exchange_rate, currency)
                pie_data.append(converted_value)
                pie_labels.append(item)
    
    colors = ['#FF9500', '#FF6B9D', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFA07A']
    
    pie_fig = go.Figure(data=[go.Pie(
        labels=pie_labels,
        values=pie_data,
        marker=dict(colors=colors[:len(pie_data)]),
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>%{value:,.0f}',
        hovertemplate=f'<b>%{{label}}</b><br>مبلغ: %{{value:,.0f}} {currency_label}<br>درصد: %{{percent}}<extra></extra>',
        hole=0.4
    )])
    
    pie_fig.update_layout(
        title=f"ترکیب هزینه‌های سربار ({currency_label})",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    return pie_fig



def create_admin_pie_chart(data_type, admin_data, currency='rial', exchange_rate=1):
    """ایجاد نمودار پای برای اجزای هزینه‌های عمومی و اداری با تبدیل ارز"""
    pie_items = [
        'هزینه حقوق و دستمزد کارکنان اداری و عمومی',
        'خدمات  پيمانكاري و تخصصی',
        'هزینه حمل',
        'حق العمل كاري وكميسيون فروش',
        'کمک به مراکز فرهنگی و ورزشی و بهداشتی (مسئولیت اجتماعی)',
        'استهلاك دارائيها',
        'کالا ، قطعات و ملزومات مصرفی'
    ]
    
    pie_data = []
    pie_labels = []
    currency_label = "هزار دلار" if currency == 'dollar' else "میلیون ریال"
    
    for item in pie_items:
        row = admin_data[admin_data['شرح'].astype(str).str.strip() == item.strip()]
        if not row.empty:
            current_col, _, _ = get_column_names(data_type, admin_data)
            value = row[current_col].values[0] if current_col and current_col in admin_data.columns else 0
            if value > 0:
                if currency == 'dollar':
                    converted_value = (value / 1_000) / exchange_rate
                else:
                    converted_value = value
                #converted_value = convert_currency(value, exchange_rate, currency)
                pie_data.append(converted_value)
                pie_labels.append(item)
    
    colors = ['#FF9500', '#FF6B9D', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFA07A', '#98D8E8']
    
    pie_fig = go.Figure(data=[go.Pie(
        labels=pie_labels,
        values=pie_data,
        marker=dict(colors=colors[:len(pie_data)]),
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>%{value:,.0f}',
        hovertemplate=f'<b>%{{label}}</b><br>مبلغ: %{{value:,.0f}} {currency_label}<br>درصد: %{{percent}}<extra></extra>',
        hole=0.4
    )])
    
    pie_fig.update_layout(
        title=f"ترکیب هزینه‌های عمومی و اداری ({currency_label})",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    return pie_fig


def generate_sales_kpi_cards(selected_complex, selected_unit, data_type, source, currency, exchange_rates,threshold):
    global sales_detail_data
    
    if sales_detail_data is None:
        return []
    
    # تعیین نرخ‌های مبادله بر اساس نوع داده
    if data_type == 'current':
        actual_exchange_rate = exchange_rates.get('month_current', 1)
        budget_exchange_rate = exchange_rates.get('budget_current', 1)
        last_year_exchange_rate = exchange_rates.get('month_lastyear', 1)
    else:  # cumulative
        actual_exchange_rate = exchange_rates.get('month_tajomi', 1)
        budget_exchange_rate = exchange_rates.get('budget_tajomi', 1)
        last_year_exchange_rate = exchange_rates.get('month_lastyear_tajmoii', 1)
    
    # فیلتر کردن داده‌ها
    filtered_data = sales_detail_data.copy()
    if selected_complex != 'کل شرکت':
        filtered_data = filtered_data[filtered_data['مجتمع'] == selected_complex]
    if selected_unit != 'کل واحدها':
        filtered_data = filtered_data[filtered_data['واحد'] == selected_unit]
    
    # تعیین ستون‌ها بر اساس نوع داده
    if data_type == 'current':
        qty_actual_col = 'مقدار عملکرد ماه'
        amt_actual_col = 'مبلغ عملکرد ماه'
        qty_budget_col = 'مقدار بودجه ای ماه'
        amt_budget_col = 'مبلغ بودجه ای ماه'
        qty_last_year_col = 'مقدار ماه سال قبل'
        amt_last_year_col = 'مبلغ ماه سال قبل'
    else:  # cumulative
        qty_actual_col = 'مقدار عملکرد تا ماه'
        amt_actual_col = 'مبلغ عملکرد تا ماه'
        qty_budget_col = 'مقدار بودجه ای تا ماه'
        amt_budget_col = 'مبلغ بودجه ایتا ماه'
        qty_last_year_col = 'مقدار تا ماه سال قبل'
        amt_last_year_col = 'مبلغ تا ماه سال قبل'
    
    # تجمیع داده‌ها
    agg_data = {
        'qty_actual': filtered_data[qty_actual_col].sum(),
        'amt_actual': filtered_data[amt_actual_col].sum(),
        'qty_budget': filtered_data[qty_budget_col].sum(),
        'amt_budget': filtered_data[amt_budget_col].sum(),
        'qty_last_year': filtered_data[qty_last_year_col].sum(),
        'amt_last_year': filtered_data[amt_last_year_col].sum()
    }
    
    # تبدیل ارز در صورت نیاز
    if currency == 'dollar':
        agg_data['amt_actual'] /= actual_exchange_rate/1000
        agg_data['amt_budget'] /= budget_exchange_rate/1000
        agg_data['amt_last_year'] /= last_year_exchange_rate/1000
    
    # محاسبه نرخ‌ها
    current_rate = agg_data['amt_actual'] / agg_data['qty_actual'] if agg_data['qty_actual'] > 0 else 0
    budget_rate = agg_data['amt_budget'] / agg_data['qty_budget'] if agg_data['qty_budget'] > 0 else 0
    last_year_rate = agg_data['amt_last_year'] / agg_data['qty_last_year'] if agg_data['qty_last_year'] > 0 else 0
    
    # ایجاد کارت‌های KPI
    cards = []
    
    # کارت مقدار فروش
    cards.append(create_sales_kpi_card(
        "مقدار فروش", 
        agg_data['qty_actual'],
        agg_data['qty_budget'],
        agg_data['qty_last_year'],
        "تن", source,threshold
    ))
    
    # کارت مبلغ فروش
    currency_symbol = "$" if currency == 'dollar' else "میلیون ریال"
    cards.append(create_sales_kpi_card(
        "مبلغ فروش",
        agg_data['amt_actual'],
        agg_data['amt_budget'],
        agg_data['amt_last_year'],
        currency_symbol, source,threshold #True,
    ))
    
    # کارت نرخ فروش
    rate_unit = f"{currency_symbol} به ازای هر تن"
    cards.append(create_sales_kpi_card(
        "نرخ فروش",
        current_rate,
        budget_rate,
        last_year_rate,
        rate_unit, source,threshold #True,
    ))
    
    return cards



def create_sales_kpi_card(title, actual, budget, last_year, unit, source, threshold, is_currency=False):
    """ایجاد کارت KPI برای فروش با جزئیات کامل"""
    base = budget if source == 'budget' else last_year
    base_label = "بودجه" if source == 'budget' else "سال قبل"
    
    if base != 0:
        deviation = ((actual - base) / base) * 100
    else:
        deviation = 0
    
    # محاسبه درصد پیشرفت برای نوار
    if source == 'budget' and budget != 0:
        progress_percentage = (actual / budget) * 100
        progress_label = f"پیشرفت نسبت به بودجه: {progress_percentage:.1f}%"
    elif source == 'last_year' and last_year != 0:
        progress_percentage = (actual / last_year) * 100
        progress_label = f"نسبت به سال قبل: {progress_percentage:.1f}%"
    else:
        progress_percentage = 0
        progress_label = "داده مرجع موجود نیست"
    
    progress_percentage = min(progress_percentage, 150)  # حداکثر 150%
    
    # انتخاب گرادینت و رنگ نوار بر اساس میزان انحراف و threshold
    if deviation >= threshold:
        gradient = 'linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%)'
        progress_color = '#00C9FF'
        arrow = '🚀'
    elif deviation >= 0:
        gradient = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        progress_color = '#667eea'
        arrow = '⬆️'
    elif deviation >= -threshold:
        gradient = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
        progress_color = '#f093fb'
        arrow = '⬇️'
    else:
        gradient = 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)'
        progress_color = '#ff6b6b'
        arrow = '🔻'
    
    # فرمت کردن مقادیر
    def format_value(value):
        if is_currency:
            if currency == 'dollar':
                # Format dollar values appropriately
                if abs(value) < 0.01:  # Very small values
                    return "~0"
                elif abs(value) <= 1:  # Values less than 1000 dollars
                    return f"{value:,.3f}"
                else:  # Values 1000 dollars and above
                    return f"{value:,.0f}"
            else:
                if abs(value) >= 1_000_000_000:
                    return f"{value/1_000_000_000:,.5f} میلیارد"
                elif abs(value) >= 1_000_000:
                    return f"{value/1_000_000:,.5f} میلیون"
                else:
                    return f"{value:,.0f}"
        else:
            if abs(value) >= 1_000_000:
                return f"{value/1_000_000:,.1f} میلیون"
            elif abs(value) >= 1_000:
                return f"{value/1_000:,.1f} هزار"
            else:
                return f"{value:,.0f}"
    
    return html.Div([
        html.Div([
            html.H4(f"📊 {title}", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '0 0 10px 0',
                'fontSize': '13px',
                'fontWeight': 'bold'
            }),
            html.H2(f"{arrow} {deviation:.1f}%", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '0 0 10px 0',
                'fontSize': '22px',
                'fontWeight': 'bold',
                'textShadow': '0 2px 4px rgba(0,0,0,0.3)'
            }),
            
            # نوار پیشرفت
            html.Div([
                html.Div([
                    html.Div(style={
                        'width': f'{min(progress_percentage, 100)}%',
                        'height': '100%',
                        'backgroundColor': progress_color,
                        'borderRadius': '8px',
                        'transition': 'width 0.5s ease',
                        'boxShadow': f'0 0 10px {progress_color}'
                    })
                ], style={
                    'width': '100%',
                    'height': '8px',
                    'backgroundColor': 'rgba(255,255,255,0.3)',
                    'borderRadius': '8px',
                    'overflow': 'hidden',
                    'margin': '10px 0'
                }),
                html.P(progress_label, style={
                    'textAlign': 'center',
                    'color': '#fff',
                    'fontSize': '9px',
                    'margin': '5px 0'
                })
            ]),
            
            html.P(f"عملکرد: {format_value(actual)} {unit}", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '3px 0',
                'fontSize': '10px'
            }),
            html.P(f"بودجه: {format_value(budget)} {unit}", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '3px 0',
                'fontSize': '10px'
            }),
            html.P(f"سال قبل: {format_value(last_year)} {unit}", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '3px 0',
                'fontSize': '10px'
            })
        ])
    ], style={
        'background': gradient,
        'borderRadius': '20px',
        'padding': '15px',
        'width': '200px',
        'height': '220px',
        'boxShadow': '0 0 15px rgba(0,0,0,0.3)',
        'border': '2px solid ' + progress_color,
        'transition': 'all 0.3s ease',
        'position': 'relative',
        'overflow': 'hidden'
    })


def create_sales_charts(selected_complex, selected_unit, data_type, deviation_type, 
                       currency, threshold, source, exchange_rates, grouping):
    """ایجاد نمودارهای فروش با قابلیت گروه‌بندی"""
    global sales_detail_data
    
    # تعیین نرخ‌های مبادله
    if data_type == 'current':
        actual_exchange_rate = exchange_rates.get('month_current', 1)
        budget_exchange_rate = exchange_rates.get('budget_current', 1)
        last_year_exchange_rate = exchange_rates.get('month_lastyear', 1)
    else:
        actual_exchange_rate = exchange_rates.get('month_tajomi', 1)
        budget_exchange_rate = exchange_rates.get('budget_tajomi', 1)
        last_year_exchange_rate = exchange_rates.get('month_lastyear_tajmoii', 1)
    
    # فیلتر کردن داده‌ها
    filtered_data = sales_detail_data.copy()
    if selected_complex != 'کل شرکت':
        filtered_data = filtered_data[filtered_data['مجتمع'] == selected_complex]
    if selected_unit != 'کل واحدها':
        filtered_data = filtered_data[filtered_data['واحد'] == selected_unit]
    
    # تعیین ستون‌ها
    if data_type == 'current':
        qty_actual_col = 'مقدار عملکرد ماه'
        amt_actual_col = 'مبلغ عملکرد ماه'
        qty_budget_col = 'مقدار بودجه ای ماه'
        amt_budget_col = 'مبلغ بودجه ای ماه'
        qty_last_year_col = 'مقدار ماه سال قبل'
        amt_last_year_col = 'مبلغ ماه سال قبل'
    else:
        qty_actual_col = 'مقدار عملکرد تا ماه'
        amt_actual_col = 'مبلغ عملکرد تا ماه'
        qty_budget_col = 'مقدار بودجه ای تا ماه'
        amt_budget_col = 'مبلغ بودجه ایتا ماه'
        qty_last_year_col = 'مقدار تا ماه سال قبل'
        amt_last_year_col = 'مبلغ تا ماه سال قبل'
    
    # تعیین ستون گروه‌بندی
    group_column = 'type' if grouping == 'sales_type' else 'محصولات'
    
    # تجمیع بر اساس گروه انتخاب شده
    chart_data = []
    for group_value in filtered_data[group_column].unique():
        group_data = filtered_data[filtered_data[group_column] == group_value]
        
        if deviation_type == 'quantity':
            actual = group_data[qty_actual_col].sum()
            budget = group_data[qty_budget_col].sum()
            last_year = group_data[qty_last_year_col].sum()
            unit = "تن"
        elif deviation_type == 'amount':
            actual = group_data[amt_actual_col].sum()
            budget = group_data[amt_budget_col].sum()
            last_year = group_data[amt_last_year_col].sum()
            
            if currency == 'dollar':
                actual /= actual_exchange_rate
                budget /= budget_exchange_rate
                last_year /= last_year_exchange_rate
                
            unit = "دلار" if currency == 'dollar' else "میلیون ریال"
        else:  # rate
            actual_qty = group_data[qty_actual_col].sum()
            actual_amt = group_data[amt_actual_col].sum()
            actual = actual_amt / actual_qty if actual_qty > 0 else 0
            
            budget_qty = group_data[qty_budget_col].sum()
            budget_amt = group_data[amt_budget_col].sum()
            budget = budget_amt / budget_qty if budget_qty > 0 else 0
            
            ly_qty = group_data[qty_last_year_col].sum()
            ly_amt = group_data[amt_last_year_col].sum()
            last_year = ly_amt / ly_qty if ly_qty > 0 else 0
            
            if currency == 'dollar':
                actual /= actual_exchange_rate
                budget /= budget_exchange_rate
                last_year /= last_year_exchange_rate
                
            unit = "به ازای هر تن"
        
        base = budget if source == 'budget' else last_year
        if base != 0:
            deviation = ((actual - base) / base) * 100
        else:
            deviation = 0
        
        chart_data.append({
            'group': group_value,
            'deviation': deviation,
            'actual': actual,
            'budget': budget,
            'last_year': last_year,
            'unit': unit
        })
    
    # نمودار انحراف
    deviation_fig = go.Figure()
    colors = []
    for data in chart_data:
        d = data['deviation']
        if d >= threshold:
            colors.append('#00C9FF')
        elif d >= 0:
            colors.append('#667eea')
        elif d >= -threshold:
            colors.append('#f093fb')
        else:
            colors.append('#ff6b6b')
    
    deviation_fig.add_trace(go.Bar(
        x=[data['deviation'] for data in chart_data],
        y=[data['group'] for data in chart_data],
        orientation='h',
        marker_color=colors,
        text=[f"{data['deviation']:.1f}%" for data in chart_data],
        textposition='auto',
        name=f'انحراف {deviation_type}'
    ))
    
    deviation_fig.add_vline(x=threshold, line_dash="dash", line_color="green", 
                           annotation_text=f"حد مطلوب +{threshold}%")
    deviation_fig.add_vline(x=-threshold, line_dash="dash", line_color="red", 
                           annotation_text=f"حد هشدار -{threshold}%")
    
    deviation_fig.update_layout(
        title=f"انحراف {deviation_type} فروش نسبت به {'بودجه' if source == 'budget' else 'سال قبل'}",
        xaxis_title="درصد انحراف",
        font=dict(family="Vazir", size=12),
        plot_bgcolor='rgba(248,249,250,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=800
    )
    
    # نمودار مقایسه
    comparison_fig = go.Figure()
    groups_list = [data['group'] for data in chart_data]
    actual_values = [data['actual'] for data in chart_data]
    budget_values = [data['budget'] for data in chart_data]
    last_year_values = [data['last_year'] for data in chart_data]
    unit = chart_data[0]['unit'] if chart_data else ""
    
    comparison_fig.add_trace(go.Bar(
        name='عملکرد فعلی',
        x=groups_list,
        y=actual_values,
        marker_color='#667eea'
    ))
    
    comparison_fig.add_trace(go.Bar(
        name='بودجه',
        x=groups_list,
        y=budget_values,
        marker_color='#00C9FF'
    ))
    
    comparison_fig.add_trace(go.Bar(
        name='سال قبل',
        x=groups_list,
        y=last_year_values,
        marker_color='#f093fb'
    ))
    
    comparison_fig.update_layout(
        title=f"مقایسه {deviation_type} فروش ({unit})",
        xaxis_title="گروه" if grouping == 'products' else "نوع فروش",
        yaxis_title=f"مقدار ({unit})",
        barmode='group',
        font=dict(family="Vazir", size=12),
        plot_bgcolor='rgba(248,249,250,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return deviation_fig, comparison_fig

def create_sales_pie_chart(data, chart_type, data_type, currency='rial'):
    """ایجاد نمودار پای برای فروش"""
    if chart_type == 'quantity':
        value_col = 'مقدار عملکرد ماه' if data_type == 'current' else 'مقدار عملکرد تا ماه'
        title = "سهم از مقدار (تن)"
    else:
        value_col = 'مبلغ عملکرد ماه' if data_type == 'current' else 'مبلغ عملکرد تا ماه'
        title = f"سهم از مبلغ ({'دلار' if currency == 'dollar' else 'میلیون ریال'})"
    
    pie_data = data.groupby('type')[value_col].sum().reset_index()
    
    fig = go.Figure(data=[go.Pie(
        labels=pie_data['type'],
        values=pie_data[value_col],
        hole=0.4
    )])
    
    fig.update_layout(
        title=title,
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig

def create_sales_pie_charts(selected_complex, selected_unit, data_type, currency, grouping,exchange_rates):
    """ایجاد نمودارهای پای برای فروش"""
    global sales_detail_data
    
    # تعیین ستون‌ها
    if data_type == 'current':
        qty_col = 'مقدار عملکرد ماه'
        amt_col = 'مبلغ عملکرد ماه'
    else:
        qty_col = 'مقدار عملکرد تا ماه'
        amt_col = 'مبلغ عملکرد تا ماه'


    
    
    
    # فیلتر کردن داده‌ها
    filtered_data = sales_detail_data.copy()
    if selected_complex != 'کل شرکت':
        filtered_data = filtered_data[filtered_data['مجتمع'] == selected_complex]
    if selected_unit != 'کل واحدها':
        filtered_data = filtered_data[filtered_data['واحد'] == selected_unit]
    
    # تعیین ستون گروه‌بندی
    group_column = 'type' if grouping == 'sales_type' else 'محصولات'

    
    # نمودار سهم از مقدار
    quantity_data = filtered_data.groupby(group_column)[qty_col].sum().reset_index()

    total_qty = quantity_data[qty_col].sum()
    quantity_data['سهم'] = quantity_data[qty_col] / total_qty * 100
    
    # جدا کردن موارد با سهم کمتر از ۲٪
    main_quantity = quantity_data[quantity_data['سهم'] >= 2]
    other_quantity = quantity_data[quantity_data['سهم'] < 2]
    other_sum = other_quantity[qty_col].sum()
    
    # اضافه کردن دسته "سایر" اگر موردی وجود دارد
    if not other_quantity.empty:
        main_quantity = pd.concat([main_quantity, pd.DataFrame({
            group_column: ['سایر'],
            qty_col: [other_sum],
            'سهم': [other_sum / total_qty * 100]
        })], ignore_index=True)


    
    colors = ['#FF9500', '#FF6B9D', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFA07A', '#98D8E8']
    quantity_pie = go.Figure(data=[go.Pie(
        labels=main_quantity[group_column],
        values=main_quantity[qty_col],
        hole=0.4,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>مقدار: %{value:,.0f} تن<br>درصد: %{percent}<extra></extra>',
        marker=dict(colors=colors[:len(main_quantity)])
    )])
    
    quantity_pie.update_layout(
        title="سهم از مقدار فروش (تن)",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    # نمودار سهم از مبلغ  
    currency_label = "دلار" if currency == 'dollar' else "میلیون ریال"
    amount_data = filtered_data.groupby(group_column)[amt_col].sum().reset_index()
    total_amnt = amount_data[amt_col].sum()
    amount_data['سهم'] = amount_data[amt_col] / total_amnt * 100
    
    # جدا کردن موارد با سهم کمتر از ۲٪
    main_amount = amount_data[amount_data['سهم'] >= 2]
    other_amount = amount_data[amount_data['سهم'] < 2]
    other_sum = other_amount[amt_col].sum()
    
    # اضافه کردن دسته "سایر" اگر موردی وجود دارد
    if not other_quantity.empty:
        main_amount = pd.concat([main_amount, pd.DataFrame({
            group_column: ['سایر'],
            amt_col: [other_sum],
            'سهم': [other_sum / total_amnt * 100]
        })], ignore_index=True)

    
    if currency == 'dollar':
        # تعیین نرخ تبادل مناسب بر اساس نوع داده (دوره جاری یا تجمعی)
        if data_type == 'current':
            exchange_rate = exchange_rates.get('month_current', 1)
        else:
            exchange_rate = exchange_rates.get('month_tajomi', 1)
        main_amount[amt_col] = main_amount[amt_col] / exchange_rate
    
    
    colors = ['#FF9500', '#FF6B9D', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFA07A', '#98D8E8']
    
    amount_pie = go.Figure(data=[go.Pie(
        labels=main_amount[group_column],
        values=main_amount[amt_col],
        hole=0.4,
        textinfo='label+percent',
        hovertemplate=f'<b>%{{label}}</b><br>مبلغ: %{{value:,.0f}} {currency_label}<br>درصد: %{{percent}}<extra></extra>',
        marker=dict(colors=colors[:len(main_amount)]),
        
    )])
    
    amount_pie.update_layout(
        title=f"سهم از مبلغ فروش ({currency_label})",
        font=dict(family="Vazir", size=9),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return html.Div([
        html.Div([
            html.H4("🥧 سهم از مقدار", style={'textAlign': 'center', 'color': '#34495e'}),
            dcc.Graph(figure=quantity_pie)
        ], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            html.H4("🥧 سهم از مبلغ", style={'textAlign': 'center', 'color': '#34495e'}),
            dcc.Graph(figure=amount_pie)
        ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '4%'})
    ])






def generate_khorak_kpi_cards(data_type, source, currency, threshold,exchange_rate=1):
    global khorak_data
    if khorak_data is None:
        return []


    # تعیین نرخ‌های مبادله بر اساس نوع داده
    
    
    
    if data_type == 'current':
        actual_exchange_rate = exchange_rate.get('month_current', 1)
        budget_exchange_rate = exchange_rate.get('budget_current', 1)
        last_year_exchange_rate = exchange_rate.get('month_lastyear', 1)
    else:
        actual_exchange_rate = exchange_rate.get('month_tajomi', 1)
        budget_exchange_rate = exchange_rate.get('budget_tajomi', 1)
        last_year_exchange_rate = exchange_rate.get('month_lastyear_tajmoii', 1)

    cards = [
        create_khorak_kpi_card("مقدار خوراک", data_type, source, currency, threshold, 'quantity', 
                              actual_exchange_rate, budget_exchange_rate, last_year_exchange_rate),
        create_khorak_kpi_card("نرخ خوراک", data_type, source, currency, threshold, 'rate', 
                              actual_exchange_rate, budget_exchange_rate, last_year_exchange_rate),
        create_khorak_kpi_card("مبلغ خوراک", data_type, source, currency, threshold, 'amount', 
                              actual_exchange_rate, budget_exchange_rate, last_year_exchange_rate)
    ]
    
    return cards








    # تعیین ستون‌ها بر اساس نوع داده
def create_khorak_kpi_card(title, data_type, source, currency, threshold, value_type, actual_exchange_rate, budget_exchange_rate, last_year_exchange_rate, is_currency=False):
    global khorak_data
    
    # تعیین پیشوند بر اساس نوع داده
    prefix = "" if data_type == 'current' else "تجمعی "
    
    # تعیین ستون‌های مقدار و مبلغ
    if data_type == 'current':
        qty_actual_col = "مقدار عملکرد ماه"
        amt_actual_col = "مبلغ عملکرد ماه"
        qty_budget_col = "مقدار بودجه ماه"
        amt_budget_col = "مبلغ بودجه ماه"
        qty_last_year_col = "مقدار عملکرد ماه سال قبل"
        amt_last_year_col = "مبلغ عملکرد ماه سال قبل"
    else:
        qty_actual_col = "مقدار تجمعی عملکرد ماه"
        amt_actual_col = "مبلغ تجمعی عملکرد ماه"
        qty_budget_col = "مقدار تجمعی بودجه ماه"
        amt_budget_col = "مبلغ تجمعی بودجه ماه"
        qty_last_year_col = "مقدار تجمعی عملکرد ماه سال قبل"
        amt_last_year_col = "مبلغ تجمعی عملکرد ماه سال قبل"
    
    # محاسبه مجموع مقادیر و مبالغ
    total_qty_actual = khorak_data[qty_actual_col].sum()
    total_amt_actual = khorak_data[amt_actual_col].sum()
    total_qty_budget = khorak_data[qty_budget_col].sum()
    total_amt_budget = khorak_data[amt_budget_col].sum()
    total_qty_last_year = khorak_data[qty_last_year_col].sum()
    total_amt_last_year = khorak_data[amt_last_year_col].sum()
    
    # محاسبه نرخ‌ها
    actual_rate = total_amt_actual / total_qty_actual if total_qty_actual > 0 else 0
    budget_rate = total_amt_budget / total_qty_budget if total_qty_budget > 0 else 0
    last_year_rate = total_amt_last_year / total_qty_last_year if total_qty_last_year > 0 else 0
    
    # انتخاب مقادیر بر اساس نوع value_type
    if value_type == 'quantity':
        actual = total_qty_actual
        budget = total_qty_budget
        last_year = total_qty_last_year
        unit = "تن"
        is_currency = False
    elif value_type == 'rate':
        actual = actual_rate
        budget = budget_rate
        last_year = last_year_rate
        unit = "میلیون ریال" if currency == 'rial' else "هزار دلار"
        is_currency = True
    else:  # amount
        actual = total_amt_actual
        budget = total_amt_budget
        last_year = total_amt_last_year
        unit = "میلیون ریال" if currency == 'rial' else " دلار"
        is_currency = True
    
    # تبدیل ارز در صورت نیاز
    if is_currency and currency == 'dollar':
        actual = convert_currency(actual, actual_exchange_rate, currency)
        budget = convert_currency(budget, budget_exchange_rate, currency)
        last_year = convert_currency(last_year, last_year_exchange_rate, currency)

    
    # محاسبه انحراف
    base = budget if source == 'budget' else last_year
    if base != 0:
        deviation = ((actual - base) / base) * 100
    else:
        deviation = 0
    
    # محاسبه درصد پیشرفت
    if source == 'budget' and budget != 0:
        progress_percentage = (actual / budget) * 100
        progress_label = f"پیشرفت نسبت به بودجه: {progress_percentage:.1f}%"
    elif source == 'last_year' and last_year != 0:
        progress_percentage = (actual / last_year) * 100
        progress_label = f"نسبت به سال قبل: {progress_percentage:.1f}%"
    else:
        progress_percentage = 0
        progress_label = "داده مرجع موجود نیست"
    
    # انتخاب رنگ بر اساس انحراف
    if deviation >= threshold:
        gradient = 'linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%)'
        progress_color = '#00C9FF'
        arrow = '🚀'
    elif deviation >= 0:
        gradient = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        progress_color = '#667eea'
        arrow = '⬆️'
    elif deviation >= -threshold:
        gradient = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
        progress_color = '#f093fb'
        arrow = '⬇️'
    else:
        gradient = 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)'
        progress_color = '#ff6b6b'
        arrow = '🔻'
    
    # فرمت اعداد
    def format_value(value):
        if is_currency:
            if currency == 'dollar':
                # Format dollar values appropriately
                if abs(value) < 0.01:  # Very small values
                    return "~0"
                elif abs(value) < 1:  # Values less than 1000 dollars
                    return f"{value:,.3f}"
                else:  # Values 1000 dollars and above
                    return f"{value:,.0f}"
            else:
                if abs(value) >= 1_000_000_000:
                    return f"{value/1_000_000_000:,.1f} میلیارد"
                elif abs(value) >= 1_000_000:
                    return f"{value/1_000_000:,.1f} میلیون"
                else:
                    return f"{value:,.0f}"
        else:
            if abs(value) >= 1_000_000:
                return f"{value/1_000_000:,.1f} میلیون"
            elif abs(value) >= 1_000:
                return f"{value/1_000:,.1f} هزار"
            else:
                return f"{value:,.0f}"
        
    
    return html.Div([
        html.Div([
            html.H4(f"🍽️ {title}", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '0 0 10px 0',
                'fontSize': '13px',
                'fontWeight': 'bold'
            }),
            html.H2(f"{arrow} {deviation:.1f}%", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '0 0 10px 0',
                'fontSize': '22px',
                'fontWeight': 'bold',
                'textShadow': '0 2px 4px rgba(0,0,0,0.3)'
            }),
            
            # نوار پیشرفت
            html.Div([
                html.Div([
                    html.Div(style={
                        'width': f'{min(progress_percentage, 100)}%',
                        'height': '100%',
                        'backgroundColor': progress_color,
                        'borderRadius': '8px',
                        'transition': 'width 0.5s ease',
                        'boxShadow': f'0 0 10px {progress_color}'
                    })
                ], style={
                    'width': '100%',
                    'height': '8px',
                    'backgroundColor': 'rgba(255,255,255,0.3)',
                    'borderRadius': '8px',
                    'overflow': 'hidden',
                    'margin': '10px 0'
                }),
                html.P(progress_label, style={
                    'textAlign': 'center',
                    'color': '#fff',
                    'fontSize': '9px',
                    'margin': '5px 0'
                })
            ]),
            
            html.P(f"عملکرد: {format_value(actual)} {unit}", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '3px 0',
                'fontSize': '10px'
            }),
            html.P(f"بودجه: {format_value(budget)} {unit}", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '3px 0',
                'fontSize': '10px'
            }),
            html.P(f"سال قبل: {format_value(last_year)} {unit}", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '3px 0',
                'fontSize': '10px'
            })
        ])
    ], style={
        'background': gradient,
        'borderRadius': '20px',
        'padding': '15px',
        'width': '200px',
        'height': '220px',
        'boxShadow': '0 0 15px rgba(0,0,0,0.3)',
        'border': '2px solid ' + progress_color,
        'transition': 'all 0.3s ease',
        'position': 'relative',
        'overflow': 'hidden'
    })




def create_khorak_charts(data_type, deviation_type1, source, threshold, currency, exchange_rates):
    global khorak_data
    
    # تعیین نرخ‌های مبادله بر اساس نوع داده
    if data_type == 'current':
        actual_exchange_rate = exchange_rates.get('month_current', 1)
        budget_exchange_rate = exchange_rates.get('budget_current', 1)
        last_year_exchange_rate = exchange_rates.get('month_lastyear', 1)
    else:
        actual_exchange_rate = exchange_rates.get('month_tajomi', 1)
        budget_exchange_rate = exchange_rates.get('budget_tajomi', 1)
        last_year_exchange_rate = exchange_rates.get('month_lastyear_tajmoii', 1)
    
    # تعیین ستون‌ها بر اساس نوع داده
    if data_type == 'current':
        prefix = ""
    else:
        prefix = "تجمعی "
    
    # تعیین ستون‌های انحراف
    if deviation_type1 == 'quantity':
        actual_col = f"مقدار {prefix}عملکرد ماه"



        
        budget_col = f"مقدار {prefix}بودجه ماه"
        last_year_col = f"مقدار {prefix}عملکرد ماه سال قبل"
        unit = "تن"
        is_currency = False
    elif deviation_type1 == 'rate':
        actual_col = f"نرخ {prefix}عملکرد ماه"
        budget_col = f"نرخ {prefix}بودجه ماه"
        last_year_col = f"نرخ {prefix}عملکرد ماه سال قبل"
        unit = "میلیون ریال" if currency == 'rial' else "دلار"
        is_currency = True
    else:  # amount
        actual_col = f"مبلغ {prefix}عملکرد ماه"
        budget_col = f"مبلغ {prefix}بودجه ماه"
        last_year_col = f"مبلغ {prefix}عملکرد ماه سال قبل"
        unit = "میلیون ریال" if currency == 'rial' else "دلار"
        is_currency = True
    
    # محاسبه انحراف برای هر خوراک
    chart_data = []
    for idx, row in khorak_data.iterrows():
        name = row['نام خوراک']
        actual = row[actual_col]
        budget = row[budget_col]
        last_year = row[last_year_col]
        
        # تبدیل ارز در صورت نیاز
        if is_currency and currency == 'dollar':
            actual = convert_currency(actual, actual_exchange_rate, currency)
            budget = convert_currency(budget, budget_exchange_rate, currency)
            last_year = convert_currency(last_year, last_year_exchange_rate, currency)
        
        base = budget if source == 'budget' else last_year
        if base != 0:
            deviation = ((actual - base) / base) * 100
        else:
            deviation = 0
        
        chart_data.append({
            'name': name,
            'deviation': deviation,
            'actual': actual,
            'budget': budget,
            'last_year': last_year,
            'unit': unit
        })
    # نمودار انحراف
    deviation_fig = go.Figure()
    colors = []
    for data in chart_data:
        d = data['deviation']
        if d >= threshold:
            colors.append('#00C9FF')
        elif d >= 0:
            colors.append('#667eea')
        elif d >= -threshold:
            colors.append('#f093fb')
        else:
            colors.append('#ff6b6b')
    
    deviation_fig.add_trace(go.Bar(
        x=[data['deviation'] for data in chart_data],
        y=[data['name'] for data in chart_data],
        orientation='h',
        marker_color=colors,
        text=[f"{data['deviation']:.1f}%" for data in chart_data],
        textposition='auto',
        name='انحراف'
    ))
    
    deviation_fig.add_vline(x=threshold, line_dash="dash", line_color="green", 
                           annotation_text=f"حد مطلوب +{threshold}%")
    deviation_fig.add_vline(x=-threshold, line_dash="dash", line_color="red", 
                           annotation_text=f"حد هشدار -{threshold}%")
    
    deviation_fig.update_layout(
        title=f"انحراف {deviation_type1} خوراک نسبت به {'بودجه' if source == 'budget' else 'سال قبل'}",
        xaxis_title="درصد انحراف",
        font=dict(family="Vazir", size=12),
        plot_bgcolor='rgba(248,249,250,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=800
    )
    
    # نمودار مقایسه
    comparison_fig = go.Figure()
    names = [data['name'] for data in chart_data]
    actual_values = [data['actual'] for data in chart_data]
    budget_values = [data['budget'] for data in chart_data]
    last_year_values = [data['last_year'] for data in chart_data]
    
    comparison_fig.add_trace(go.Bar(
        name='عملکرد فعلی',
        x=names,
        y=actual_values,
        marker_color='#667eea'
    ))
    comparison_fig.add_trace(go.Bar(
        name='بودجه',
        x=names,
        y=budget_values,
        marker_color='#00C9FF'
    ))
    comparison_fig.add_trace(go.Bar(
        name='سال قبل',
        x=names,
        y=last_year_values,
        marker_color='#f093fb'
    ))
    
    comparison_fig.update_layout(
        title=f"مقایسه {deviation_type1} خوراک ({unit})",
        barmode='group',
        font=dict(family="Vazir", size=12),
        plot_bgcolor='rgba(248,249,250,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=800,
        xaxis_tickangle=-45
    )
    
    return deviation_fig, comparison_fig





def create_khorak_pie_chart(data_type, currency, threshold_percent=5, exchange_rates=None):
    global khorak_data
    if khorak_data is None or khorak_data.empty:
        fig = go.Figure()
        fig.add_annotation(text="داده‌ای موجود نیست", showarrow=False)
        return fig
    
    # تعیین نرخ مبادله مناسب
    if data_type == 'current':
        exchange_rate = exchange_rates.get('month_current', 1) if exchange_rates else 1
    else:
        exchange_rate = exchange_rates.get('month_tajomi', 1) if exchange_rates else 1
    
    # تعیین ستون مبلغ با توجه به نوع داده
    if data_type == 'current':
        amt_col = "مبلغ عملکرد ماه"
    else:
        amt_col = "مبلغ تجمعی عملکرد ماه"
    
    # کپی داده‌ها برای جلوگیری از تغییر داده اصلی
    khorak = khorak_data.copy()
    
    # تبدیل ارز در صورت نیاز
    if currency == 'dollar':
        khorak[amt_col] = khorak[amt_col].apply(lambda x: convert_currency(x, exchange_rate, currency))
    
    # محاسبه سهم هر خوراک از کل مبلغ (با استفاده از مقادیر مثبت)
    total = khorak[amt_col].abs().sum()
    
    # محاسبه سهم و فیلتر کردن مقادیر منفی
    khorak['سهم'] = khorak[amt_col].abs() / total * 100
    main_khorak = khorak[khorak['سهم'] > 0]  # حذف موارد با سهم صفر یا منفی

    # گروه‌بندی خوراک‌ها
    #main_khorak = khorak[khorak['سهم'] >= threshold_percent]
    #other_khorak = khorak[khorak['سهم'] < threshold_percent]
    #other_sum = other_khorak[amt_col].abs().sum()

    # آماده‌سازی داده‌ها برای نمودار
    pie_data = main_khorak[['نام خوراک', amt_col]].copy()
    
    #if other_sum > 0:
        #pie_data = pie_data.append({
            #'نام خوراک': 'سایر خوراک‌ها', 
            #amt_col: other_sum
        #}, ignore_index=True)

    # ایجاد نمودار پای
    
    colors = ['#FF9500', '#FF6B9D', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFA07A', '#98D8E8']
    
    fig = go.Figure(data=[go.Pie(
        labels=pie_data['نام خوراک'],
        values=pie_data[amt_col].abs(),  # استفاده از مقادیر مطلق
        hole=0.4,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>سهم: %{percent}<br>مبلغ: %{value:,.0f}<extra></extra>',
        marker=dict(colors=colors[:len(pie_data)]),
        #marker=dict(colors=px.colors.qualitative.Pastel)
    )])

    currency_label = "دلار" if currency == 'dollar' else "میلیون ریال"
    fig.update_layout(
        title=f"سهم خوراک‌ها از کل مبلغ ({currency_label})",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left",
            x=0.5
        )
    )
    
    return fig








def create_sales_unit_complex_pie_charts(selected_complex, selected_unit, data_type, currency, exchange_rates):
    """ایجاد نمودارهای پای برای سهم واحدها و مجتمع‌ها از فروش"""
    global sales_detail_data
    
    # تعیین ستون‌ها
    if data_type == 'current':
        qty_col = 'مقدار عملکرد ماه'
        amt_col = 'مبلغ عملکرد ماه'
    else:
        qty_col = 'مقدار عملکرد تا ماه'
        amt_col = 'مبلغ عملکرد تا ماه'
    
    # فیلتر کردن داده‌ها
    filtered_data = sales_detail_data.copy()
    if selected_complex != 'کل شرکت':
        filtered_data = filtered_data[filtered_data['مجتمع'] == selected_complex]
    if selected_unit != 'کل واحدها':
        filtered_data = filtered_data[filtered_data['واحد'] == selected_unit]
    
    currency_label = "دلار" if currency == 'dollar' else "میلیون ریال"
    
    # تابع کمکی برای گروه‌بندی موارد با سهم کم
    def group_small_categories(data, category_col, value_col, threshold=2):
        total = data[value_col].sum()
        if total == 0:
            return data
        
        data = data.copy()
        data['سهم'] = data[value_col] / total * 100
        
        main_categories = data[data['سهم'] >= threshold]
        small_categories = data[data['سهم'] < threshold]
        
        if len(small_categories) > 0:
            other_sum = small_categories[value_col].sum()
            other_row = pd.DataFrame({
                category_col: ['سایر'],
                value_col: [other_sum],
                'سهم': [other_sum / total * 100]
            })
            main_categories = pd.concat([main_categories, other_row], ignore_index=True)
        
        return main_categories
    
    # نمودار سهم واحدها از مقدار
    unit_qty_data = filtered_data.groupby('واحد')[qty_col].sum().reset_index()
    unit_qty_data = group_small_categories(unit_qty_data, 'واحد', qty_col)
    colors = ['#FF9500', '#FF6B9D', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFA07A', '#98D8E8']
    unit_qty_pie = go.Figure(data=[go.Pie(
        labels=unit_qty_data['واحد'],
        values=unit_qty_data[qty_col],
        hole=0.4,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>مقدار: %{value:,.0f} تن<br>درصد: %{percent}<extra></extra>',
        marker=dict(colors=colors[:len(unit_qty_data)])
    )])
    unit_qty_pie.update_layout(
        title="سهم واحدها از مقدار فروش (تن)",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    # نمودار سهم واحدها از مبلغ
    unit_amt_data = filtered_data.groupby('واحد')[amt_col].sum().reset_index()
    if currency == 'dollar':
        exchange_rate = exchange_rates.get('month_current', 1) if data_type == 'current' else exchange_rates.get('month_tajomi', 1)
        unit_amt_data[amt_col] = unit_amt_data[amt_col] / exchange_rate
    unit_amt_data = group_small_categories(unit_amt_data, 'واحد', amt_col)
    unit_amt_pie = go.Figure(data=[go.Pie(
        labels=unit_amt_data['واحد'],
        values=unit_amt_data[amt_col],
        hole=0.4,
        textinfo='label+percent',
        hovertemplate=f'<b>%{{label}}</b><br>مبلغ: %{{value:,.0f}} {currency_label}<br>درصد: %{{percent}}<extra></extra>',
        marker=dict(colors=colors[:len(unit_amt_data)])
    )])
    unit_amt_pie.update_layout(
        title=f"سهم واحدها از مبلغ فروش ({currency_label})",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    # نمودار سهم مجتمع‌ها از مقدار (همیشه کل داده‌ها)
    complex_qty_data = sales_detail_data.groupby('مجتمع')[qty_col].sum().reset_index()
    complex_qty_data = group_small_categories(complex_qty_data, 'مجتمع', qty_col)
    complex_qty_pie = go.Figure(data=[go.Pie(
        labels=complex_qty_data['مجتمع'],
        values=complex_qty_data[qty_col],
        hole=0.4,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>مقدار: %{value:,.0f} تن<br>درصد: %{percent}<extra></extra>',
        marker=dict(colors=colors[:len(complex_qty_data)])
    )])
    complex_qty_pie.update_layout(
        title="سهم مجتمع‌ها از مقدار فروش (تن)",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    # نمودار سهم مجتمع‌ها از مبلغ (همیشه کل داده‌ها)
    complex_amt_data = sales_detail_data.groupby('مجتمع')[amt_col].sum().reset_index()
    if currency == 'dollar':
        exchange_rate = exchange_rates.get('month_current', 1) if data_type == 'current' else exchange_rates.get('month_tajomi', 1)
        complex_amt_data[amt_col] = complex_amt_data[amt_col] / exchange_rate
    complex_amt_data = group_small_categories(complex_amt_data, 'مجتمع', amt_col)
    complex_amt_pie = go.Figure(data=[go.Pie(
        labels=complex_amt_data['مجتمع'],
        values=complex_amt_data[amt_col],
        hole=0.4,
        textinfo='label+percent',
        hovertemplate=f'<b>%{{label}}</b><br>مبلغ: %{{value:,.0f}} {currency_label}<br>درصد: %{{percent}}<extra></extra>',
        marker=dict(colors=colors[:len(complex_amt_data)])
    )])
    complex_amt_pie.update_layout(
        title=f"سهم مجتمع‌ها از مبلغ فروش ({currency_label})",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return html.Div([
        html.H4("🥧 سهم واحدها و مجتمع‌ها از فروش", style={'textAlign': 'center', 'color': '#34495e', 'marginBottom': '20px'}),
        
        html.Div([
            html.Div([
                dcc.Graph(figure=unit_qty_pie)
            ], style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                dcc.Graph(figure=unit_amt_pie)
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '4%'})
        ], style={'marginBottom': '30px'}),
        
        html.Div([
            html.Div([
                dcc.Graph(figure=complex_qty_pie)
            ], style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                dcc.Graph(figure=complex_amt_pie)
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '4%'})
        ])
    ])







def create_khorak_pie_charts(data_type, currency, threshold_percent=5, exchange_rates=None):
    global khorak_data
    if khorak_data is None or khorak_data.empty:
        fig_qty = go.Figure()
        fig_qty.add_annotation(text="داده‌ای موجود نیست", showarrow=False)
        fig_amt = go.Figure()
        fig_amt.add_annotation(text="داده‌ای موجود نیست", showarrow=False)
        return fig_qty, fig_amt

    # تعیین نرخ مبادله مناسب
    if data_type == 'current':
        exchange_rate = exchange_rates.get('month_current', 1) if exchange_rates else 1
        qty_col = "مقدار عملکرد ماه"
        amt_col = "مبلغ عملکرد ماه"
    else:
        exchange_rate = exchange_rates.get('month_tajomi', 1) if exchange_rates else 1
        qty_col = "مقدار تجمعی عملکرد ماه"
        amt_col = "مبلغ تجمعی عملکرد ماه"

    # کپی داده‌ها
    khorak = khorak_data.copy()
    total_qty = khorak[qty_col].sum()
    khorak['سهم'] = khorak[qty_col] / total_qty * 100
    
    # جدا کردن موارد با سهم کمتر از ۲٪
    main_khorak = khorak[khorak['سهم'] >= 2]
    other_khorak = khorak[khorak['سهم'] < 2]
    other_sum = other_khorak[qty_col].sum()
    
    if not other_khorak.empty:
        main_khorak = pd.concat([main_khorak, pd.DataFrame({
            'نام خوراک': ['سایر'],
            qty_col: [other_sum],
            'سهم': [other_sum / total_qty * 100]
        })], ignore_index=True)
    colors = ['#FF9500', '#FF6B9D', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFA07A', '#98D8E8']
    # ایجاد نمودار با داده‌های گروه‌بندی شده
    qty_pie = go.Figure(data=[go.Pie(
        labels=main_khorak['نام خوراک'],
        values=main_khorak[qty_col],
        hole=0.4,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>مقدار: %{value:,.0f} تن<br>درصد: %{percent}<extra></extra>',
        marker=dict(colors=colors[:len(main_khorak)])
    )])
    # تبدیل ارز در صورت نیاز
    if currency == 'dollar':
        main_khorak[amt_col] = khorak[amt_col].apply(lambda x: convert_currency(x, exchange_rate, currency))
    colors = ['#FF9500', '#FF6B9D', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFA07A', '#98D8E8']
    # نمودار پای برای مقدار
    

    
    qty_pie.update_layout(
        title="سهم از مقدار خوراک (تن)",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    

    khorak_we = khorak_data.copy()
    total_amn = khorak_we[amt_col].sum()
    khorak_we['سهم'] = khorak_we[amt_col] / total_amn * 100
    
    # جدا کردن موارد با سهم کمتر از ۲٪
    main_khorak_am = khorak_we[khorak_we['سهم'] >= 2]
    other_khorak_am = khorak_we[khorak_we['سهم'] < 2]
    other_sum_we = other_khorak_am[amt_col].sum()
    
    if not other_khorak.empty:
        main_khorak_am = pd.concat([main_khorak_am, pd.DataFrame({
            'نام خوراک': ['سایر'],
            amt_col: [other_sum_we],
            'سهم': [other_sum_we / total_amn * 100]
        })], ignore_index=True)
    if currency == 'dollar':
        main_khorak_am[amt_col] = main_khorak_am[amt_col].apply(lambda x: convert_currency(x, exchange_rate, currency))
    # نمودار پای برای مبلغ
    currency_label = "دلار" if currency == 'dollar' else "میلیون ریال"
    amt_pie = go.Figure(data=[go.Pie(
        labels=main_khorak_am['نام خوراک'],
        values=main_khorak_am[amt_col],
        hole=0.4,
        textinfo='label+percent',
        hovertemplate=f'<b>%{{label}}</b><br>مبلغ: %{{value:,.0f}} {currency_label}<br>درصد: %{{percent}}<extra></extra>',
         #marker=dict(  # اضافه شدن این بخش
            #colors=px.colors.qualitative.Plotly,
            #line=dict(color='#000000', width=1),
             marker=dict(colors=colors[:len(main_khorak)])

        
    )])
    
    amt_pie.update_layout(
        title=f"سهم از مبلغ خوراک ({currency_label})",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    return qty_pie, amt_pie






def generate_production_kpi_cards(selected_complex, selected_unit, data_type, source, threshold):
    global tolid_data
    
    if tolid_data is None:
        return []
    
    # Filter data
    filtered_data = tolid_data.copy()
    if selected_complex != 'کل شرکت':
        filtered_data = filtered_data[filtered_data['مجتمع'] == selected_complex]
    if selected_unit != 'کل واحدها':
        filtered_data = filtered_data[filtered_data['واحد'] == selected_unit]
    
    # Determine columns based on data type
    if data_type == 'current':
        actual_col = 'مقدار عملکرد ماه'
        budget_col = 'مقدار بودجه ماه'
        last_year_col = 'مقدار عملکرد ماه سال قبل'
    else:
        actual_col = 'مقدار تجمعی عملکرد ماه'
        budget_col = 'مقدار تجمعی بودجه ماه'
        last_year_col = 'مقدار تجمعی عملکرد ماه سال قبل'
    
    # Aggregate data
    agg_data = {
        'actual': filtered_data[actual_col].sum(),
        'budget': filtered_data[budget_col].sum(),
        'last_year': filtered_data[last_year_col].sum()
    }
    
    # Create KPI card
    return [create_production_kpi_card(
        "مقدار تولید",
        agg_data['actual'],
        agg_data['budget'],
        agg_data['last_year'],
        "تن", source, threshold
    )]

def create_production_kpi_card(title, actual, budget, last_year, unit, source, threshold):
    base = budget if source == 'budget' else last_year
    base_label = "بودجه" if source == 'budget' else "سال قبل"
    
    if base != 0:
        deviation = ((actual - base) / base) * 100
    else:
        deviation = 0
    
    # Calculate progress percentage
    if source == 'budget' and budget != 0:
        progress_percentage = (actual / budget) * 100
        progress_label = f"پیشرفت نسبت به بودجه: {progress_percentage:.1f}%"
    elif source == 'last_year' and last_year != 0:
        progress_percentage = (actual / last_year) * 100
        progress_label = f"نسبت به سال قبل: {progress_percentage:.1f}%"
    else:
        progress_percentage = 0
        progress_label = "داده مرجع موجود نیست"
    
    progress_percentage = min(progress_percentage, 150)
    
    # Select gradient and color based on deviation
    if deviation >= threshold:
        gradient = 'linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%)'
        progress_color = '#00C9FF'
        arrow = '🚀'
    elif deviation >= 0:
        gradient = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        progress_color = '#667eea'
        arrow = '⬆️'
    elif deviation >= -threshold:
        gradient = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
        progress_color = '#f093fb'
        arrow = '⬇️'
    else:
        gradient = 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)'
        progress_color = '#ff6b6b'
        arrow = '🔻'
    
    # Format values
    def format_value(value):
        if abs(value) >= 1_000_000:
            return f"{value/1_000_000:,.1f} میلیون"
        elif abs(value) >= 1_000:
            return f"{value/1_000:,.1f} هزار"
        else:
            return f"{value:,.0f}"
    
    return html.Div([
        html.Div([
            html.H4(f"🏭 {title}", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '0 0 10px 0',
                'fontSize': '13px',
                'fontWeight': 'bold'
            }),
            html.H2(f"{arrow} {deviation:.1f}%", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '0 0 10px 0',
                'fontSize': '22px',
                'fontWeight': 'bold',
                'textShadow': '0 2px 4px rgba(0,0,0,0.3)'
            }),
            
            # Progress bar
            html.Div([
                html.Div([
                    html.Div(style={
                        'width': f'{min(progress_percentage, 100)}%',
                        'height': '100%',
                        'backgroundColor': progress_color,
                        'borderRadius': '8px',
                        'transition': 'width 0.5s ease',
                        'boxShadow': f'0 0 10px {progress_color}'
                    })
                ], style={
                    'width': '100%',
                    'height': '8px',
                    'backgroundColor': 'rgba(255,255,255,0.3)',
                    'borderRadius': '8px',
                    'overflow': 'hidden',
                    'margin': '10px 0'
                }),
                html.P(progress_label, style={
                    'textAlign': 'center',
                    'color': '#fff',
                    'fontSize': '9px',
                    'margin': '5px 0'
                })
            ]),
            
            html.P(f"عملکرد: {format_value(actual)} {unit}", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '3px 0',
                'fontSize': '10px'
            }),
            html.P(f"بودجه: {format_value(budget)} {unit}", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '3px 0',
                'fontSize': '10px'
            }),
            html.P(f"سال قبل: {format_value(last_year)} {unit}", style={
                'textAlign': 'center', 
                'color': '#fff', 
                'margin': '3px 0',
                'fontSize': '10px'
            })
        ])
    ], style={
        'background': gradient,
        'borderRadius': '20px',
        'padding': '15px',
        'width': '200px',
        'height': '220px',
        'boxShadow': '0 0 15px rgba(0,0,0,0.3)',
        'border': '2px solid ' + progress_color,
        'transition': 'all 0.3s ease',
        'position': 'relative',
        'overflow': 'hidden'
    })




def create_production_charts(selected_complex, selected_unit, data_type, threshold, source):
    global tolid_data
    
    # Filter data
    filtered_data = tolid_data.copy()
    if selected_complex != 'کل شرکت':
        filtered_data = filtered_data[filtered_data['مجتمع'] == selected_complex]
    if selected_unit != 'کل واحدها':
        filtered_data = filtered_data[filtered_data['واحد'] == selected_unit]
    
    # Determine columns
    if data_type == 'current':
        actual_col = 'مقدار عملکرد ماه'
        budget_col = 'مقدار بودجه ماه'
        last_year_col = 'مقدار عملکرد ماه سال قبل'
    else:
        actual_col = 'مقدار تجمعی عملکرد ماه'
        budget_col = 'مقدار تجمعی بودجه ماه'
        last_year_col = 'مقدار تجمعی عملکرد ماه سال قبل'
    
    # Group by product
    chart_data = []
    for product in filtered_data['نام محصول'].unique():
        product_data = filtered_data[filtered_data['نام محصول'] == product]
        
        actual = product_data[actual_col].sum()
        budget = product_data[budget_col].sum()
        last_year = product_data[last_year_col].sum()
        
        base = budget if source == 'budget' else last_year
        if base != 0:
            deviation = ((actual - base) / base) * 100
        else:
            deviation = 0
        
        chart_data.append({
            'product': product,
            'deviation': deviation,
            'actual': actual,
            'budget': budget,
            'last_year': last_year
        })
    
    # Deviation chart
    deviation_fig = go.Figure()
    colors = []
    for data in chart_data:
        d = data['deviation']
        if d >= threshold:
            colors.append('#00C9FF')
        elif d >= 0:
            colors.append('#667eea')
        elif d >= -threshold:
            colors.append('#f093fb')
        else:
            colors.append('#ff6b6b')
    
    deviation_fig.add_trace(go.Bar(
        x=[data['deviation'] for data in chart_data],
        y=[data['product'] for data in chart_data],
        orientation='h',
        marker_color=colors,
        text=[f"{data['deviation']:.1f}%" for data in chart_data],
        textposition='auto',
        name='انحراف تولید'
    ))
    
    deviation_fig.add_vline(x=threshold, line_dash="dash", line_color="green", 
                           annotation_text=f"حد مطلوب +{threshold}%")
    deviation_fig.add_vline(x=-threshold, line_dash="dash", line_color="red", 
                           annotation_text=f"حد هشدار -{threshold}%")
    
    deviation_fig.update_layout(
        title=f"انحراف تولید نسبت به {'بودجه' if source == 'budget' else 'سال قبل'}",
        xaxis_title="درصد انحراف",
        font=dict(family="Vazir", size=12),
        plot_bgcolor='rgba(248,249,250,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=800
    )
    
    # Comparison chart
    comparison_fig = go.Figure()
    products = [data['product'] for data in chart_data]
    actual_values = [data['actual'] for data in chart_data]
    budget_values = [data['budget'] for data in chart_data]
    last_year_values = [data['last_year'] for data in chart_data]
    
    comparison_fig.add_trace(go.Bar(
        name='عملکرد فعلی',
        x=products,
        y=actual_values,
        marker_color='#667eea'
    ))
    
    comparison_fig.add_trace(go.Bar(
        name='بودجه',
        x=products,
        y=budget_values,
        marker_color='#00C9FF'
    ))
    
    comparison_fig.add_trace(go.Bar(
        name='سال قبل',
        x=products,
        y=last_year_values,
        marker_color='#f093fb'
    ))
    
    comparison_fig.update_layout(
        title=f"مقایسه تولید (تن)",
        xaxis_title="محصولات",
        yaxis_title="مقدار (تن)",
        barmode='group',
        font=dict(family="Vazir", size=12),
        plot_bgcolor='rgba(248,249,250,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=800
        ,
        xaxis_tickangle=-45
    )
    
    return deviation_fig, comparison_fig



def create_production_pie_charts(selected_complex, selected_unit, data_type):
    global tolid_data
    
    # Determine column
    if data_type == 'current':
        qty_col = 'مقدار عملکرد ماه'
    else:
        qty_col = 'مقدار تجمعی عملکرد ماه'
    
    # Filter data
    filtered_data = tolid_data.copy()
    if selected_complex != 'کل شرکت':
        filtered_data = filtered_data[filtered_data['مجتمع'] == selected_complex]
    if selected_unit != 'کل واحدها':
        filtered_data = filtered_data[filtered_data['واحد'] == selected_unit]
    
    # Group by product
    product_data = filtered_data.groupby('نام محصول')[qty_col].sum().reset_index()
    
    # Group small categories
    total = product_data[qty_col].sum()
    product_data['سهم'] = product_data[qty_col] / total * 100
    
    main_products = product_data[product_data['سهم'] >= 2]
    other_products = product_data[product_data['سهم'] < 2]
    other_sum = other_products[qty_col].sum()
    
    if not other_products.empty:
        main_products = pd.concat([main_products, pd.DataFrame({
            'نام محصول': ['سایر'],
            qty_col: [other_sum],
            'سهم': [other_sum / total * 100]
        })], ignore_index=True)
    
    # Create pie chart
    colors = ['#FF9500', '#FF6B9D', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFA07A', '#98D8E8']
    pie_fig = go.Figure(data=[go.Pie(
        labels=main_products['نام محصول'],
        values=main_products[qty_col],
        hole=0.4,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>مقدار: %{value:,.0f} تن<br>درصد: %{percent}<extra></extra>',
        marker=dict(colors=colors[:len(main_products)])
    )])
    
    pie_fig.update_layout(
        title="سهم محصولات از تولید (تن)",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return html.Div([
        html.H4("🥧 سهم محصولات از تولید", style={'textAlign': 'center', 'color': '#34495e'}),
        dcc.Graph(figure=pie_fig)
    ])

def create_production_unit_complex_pie_charts(selected_complex, selected_unit, data_type):
    global tolid_data
    
    # Determine column
    if data_type == 'current':
        qty_col = 'مقدار عملکرد ماه'
    else:
        qty_col = 'مقدار تجمعی عملکرد ماه'
    
    # Filter data
    filtered_data = tolid_data.copy()
    if selected_complex != 'کل شرکت':
        filtered_data = filtered_data[filtered_data['مجتمع'] == selected_complex]
    if selected_unit != 'کل واحدها':
        filtered_data = filtered_data[filtered_data['واحد'] == selected_unit]
    
    # Helper function to group small categories
    def group_small_categories(data, category_col, value_col, threshold=2):
        total = data[value_col].sum()
        if total == 0:
            return data
        
        data = data.copy()
        data['سهم'] = data[value_col] / total * 100
        
        main_categories = data[data['سهم'] >= threshold]
        small_categories = data[data['سهم'] < threshold]
        
        if len(small_categories) > 0:
            other_sum = small_categories[value_col].sum()
            other_row = pd.DataFrame({
                category_col: ['سایر'],
                value_col: [other_sum],
                'سهم': [other_sum / total * 100]
            })
            main_categories = pd.concat([main_categories, other_row], ignore_index=True)
        
        return main_categories
    
    # Unit share chart
    unit_data = filtered_data.groupby('واحد')[qty_col].sum().reset_index()
    unit_data = group_small_categories(unit_data, 'واحد', qty_col)
    
    colors = ['#FF9500', '#FF6B9D', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFA07A', '#98D8E8']
    unit_pie = go.Figure(data=[go.Pie(
        labels=unit_data['واحد'],
        values=unit_data[qty_col],
        hole=0.4,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>مقدار: %{value:,.0f} تن<br>درصد: %{percent}<extra></extra>',
        marker=dict(colors=colors[:len(unit_data)])
    )])
    
    unit_pie.update_layout(
        title="سهم واحدها از تولید (تن)",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    # Complex share chart (always all data)
    complex_data = tolid_data.groupby('مجتمع')[qty_col].sum().reset_index()
    complex_data = group_small_categories(complex_data, 'مجتمع', qty_col)
    
    complex_pie = go.Figure(data=[go.Pie(
        labels=complex_data['مجتمع'],
        values=complex_data[qty_col],
        hole=0.4,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>مقدار: %{value:,.0f} تن<br>درصد: %{percent}<extra></extra>',
        marker=dict(colors=colors[:len(complex_data)])
    )])
    
    complex_pie.update_layout(
        title="سهم مجتمع‌ها از تولید (تن)",
        font=dict(family="Vazir", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return html.Div([
        html.H4("🥧 سهم واحدها و مجتمع‌ها از تولید", style={'textAlign': 'center', 'color': '#34495e', 'marginBottom': '20px'}),
        
        html.Div([
            html.Div([
                dcc.Graph(figure=unit_pie)
            ], style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                dcc.Graph(figure=complex_pie)
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '4%'})
        ])
    ])





def create_profit_cost_pie_charts(data_type, currency, exchange_rate):
    global sood_data
    if sood_data is None:
        return html.Div("❌ داده‌های سود و بهای تمام شده موجود نیست", 
                      style={'textAlign': 'center', 'color': 'red', 'padding': '20px'})
    
    # انتخاب ستون‌ها بر اساس نوع داده
    if data_type == 'current':
        cost_col = 'بهای تمام شده دوره جاری'
        profit_col = 'سود دوره جاری'
    else:
        cost_col = 'بهای تمام شده تا دوره جاری'
        profit_col = 'سود تا دوره جاری'
    
    # کپی داده‌ها برای جلوگیری از تغییر داده اصلی
    data = sood_data.copy()
    
    # تبدیل ارز در صورت نیاز
    if currency == 'dollar':
        data[cost_col] = data[cost_col] / exchange_rate
        data[profit_col] = data[profit_col] / exchange_rate
    
    currency_label = "دلار" if currency == 'dollar' else "میلیون ریال"
    
    # تابع کمکی برای ایجاد نمودار پای با گروه‌بندی موارد کوچک
    def create_pie_with_grouping(grouped_data, title, threshold=2):
        # محاسبه مجموع و سهم
        total = grouped_data.sum()
        if total == 0:
            fig = go.Figure()
            fig.add_annotation(text="داده‌ای موجود نیست", showarrow=False)
            return fig
        
        # تبدیل به DataFrame برای راحتی کار
        df = grouped_data.reset_index()
        df.columns = ['نام', 'مقدار']  # نام ستون‌ها را مشخص می‌کنیم
        df['سهم'] = df['مقدار'] / total * 100
        
        # جدا کردن موارد با سهم کمتر از آستانه
        main_data = df[df['سهم'] >= threshold].copy()
        other_data = df[df['سهم'] < threshold]
        
        # اضافه کردن دسته "سایر" اگر موردی وجود دارد
        if not other_data.empty:
            other_sum = other_data['مقدار'].sum()
            other_row = pd.DataFrame({
                'نام': ['سایر'],
                'مقدار': [other_sum],
                'سهم': [other_sum / total * 100]
            })
            main_data = pd.concat([main_data, other_row], ignore_index=True)
        
        # ایجاد نمودار پای
        colors = ['#FF9500', '#FF6B9D', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFA07A', '#98D8E8']
        
        fig = go.Figure(data=[go.Pie(
            labels=main_data['نام'],  # استفاده از نام‌های واقعی
            values=main_data['مقدار'],
            hole=0.4,
            textinfo='label+percent',
            hovertemplate=f'<b>%{{label}}</b><br>مبلغ: %{{value:,.0f}} {currency_label}<br>درصد: %{{percent}}<extra></extra>',
            marker=dict(colors=colors[:len(main_data)]),
        )])
        
        fig.update_layout(
            title=title,
            font=dict(family="Vazir", size=12),
            paper_bgcolor='rgba(0,0,0,0)',
            height=400,
            showlegend=False,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            )
        )
        
        return fig
    
    # نمودار سهم محصولات از سود
    product_profit = data.groupby('محصولات دو')[profit_col].sum()
    product_profit_pie = create_pie_with_grouping(
        product_profit, 
        f"سهم محصولات از سود ({currency_label})"
    )
    
    # نمودار سهم محصولات از بهای تمام شده
    product_cost = data.groupby('محصولات دو')[cost_col].sum()
    product_cost_pie = create_pie_with_grouping(
        product_cost, 
        f"سهم محصولات از بهای تمام شده ({currency_label})"
    )
    
    # نمودار سهم واحدها از سود
    unit_profit = data.groupby('واحد')[profit_col].sum()
    unit_profit_pie = create_pie_with_grouping(
        unit_profit, 
        f"سهم واحدها از سود ({currency_label})"
    )
    
    # نمودار سهم مجتمع‌ها از سود
    complex_profit = data.groupby('مجتمع')[profit_col].sum()
    complex_profit_pie = create_pie_with_grouping(
        complex_profit, 
        f"سهم مجتمع‌ها از سود ({currency_label})"
    )
    
    return html.Div([
        html.Div([
            html.Div([
                dcc.Graph(figure=product_profit_pie)
            ], style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                dcc.Graph(figure=product_cost_pie)
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '4%'})
        ], style={'marginBottom': '30px'}),
        
        html.Div([
            html.Div([
                dcc.Graph(figure=unit_profit_pie)
            ], style={'width': '48%', 'display': 'inline-block'}),
            html.Div([
                dcc.Graph(figure=complex_profit_pie)
            ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '4%'})
        ])
    ])
















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
    global financial_data,cost_data,cash_data ,overhead_data,admin_data,sales_data,sale_adju,sales_detail_data,khorak_data,tolid_data,sood_data 
    
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
            "",
            *step_classes
        )
    else:
        ensure_loaded()

        
        if financial_data is None or cost_data is None:
            dashboard_content = html.Div([
                html.H1("❌ خطا در بارگذاری فایل Excel", style={'textAlign': 'center', 'color': 'red'}),
                html.P("فایل داده (data/holding_report/report.xlsm و dim_p_h.xlsx) پیدا نشد یا خوانده نشد.", style={'textAlign': 'center'})
            ])
        else:
            dashboard_content = create_dashboard_layout()
        
        return (
            {'width': '100%'},
            "100% - آماده!",
            {'display': 'none'},
            {'display': 'block'},
            dashboard_content,
            *["step active"] * len(LOADING_STEPS)
        )






def create_dashboard_layout():
    """ایجاد لی‌اوت اصلی داشبورد"""
    return html.Div(className="dashboard-container", children=[
        # هدر داشبورد
        html.Div(className="dashboard-header", children=[
            html.H1("📊  تحلیل عملکرد پتروشیمی بندر امام ", className="dashboard-title"),
            html.P("تحلیل مالی", style={
                'fontSize': '1.2em',
                'margin': '0',
                'opacity': '0.9'
            })
        ]),
        
        # پنل کنترل
        html.Div([
            html.H3("🎛️ پنل کنترل", style={
                'textAlign': 'center', 
                'color': '#2c3e50',
                'marginBottom': '20px'
            }),
            html.Div([
                html.Label("📋 نوع گزارش:", style={'fontWeight': 'bold', 'color': '#34495e'}),
                dcc.RadioItems(
                    id='report-type-radio',
                    options=[
                        {'label': '💼 صورت سود و زیان', 'value': 'profit_loss'},
                        {'label': '🏭 بهای تمام شده', 'value': 'cost_analysis'},
                         {'label': '⚙️ هزینه های سربار', 'value': 'overhead_analysis'},
                        {'label': '🏢 هزینه های عمومی و اداری', 'value': 'admin_analysis'},
                        {'label': '📊 فروش', 'value': 'sales_analysis'},
                        {'label': '🛢️ خوراک', 'value': 'khorak_analysis'},
                        {'label': '🏭 تولید', 'value': 'production_analysis'}
                        
                    ],
                    value='profit_loss',
                    labelStyle={'display': 'block', 'marginBottom': '10px', 'fontSize': '14px'},
                    style={'marginBottom': '20px'}
                )
            ], style={'marginBottom': '25px'}),
            # کنترل نوع داده
            html.Div([
                html.Label("📈 نوع داده:", style={'fontWeight': 'bold', 'color': '#34495e'}),
                dcc.RadioItems(
                    id='data-type-radio',
                    options=[
                        {'label': '📊 دوره فعلی', 'value': 'current'},
                        {'label': '📈 تجمعی', 'value': 'cumulative'}
                        
                    ],
                    value='current',
                    labelStyle={'display': 'block', 'marginBottom': '10px', 'fontSize': '14px'},
                    style={'marginBottom': '20px'}
                )
            ], style={'marginBottom': '25px'}),
            
            # کنترل منبع مقایسه
            html.Div([
                html.Label("🎯 منبع مقایسه:", style={'fontWeight': 'bold', 'color': '#34495e'}),
                dcc.RadioItems(
                    id='comparison-source-radio',
                    options=[
                        {'label': '📊 بودجه', 'value': 'budget'},
                        {'label': '📆 سال قبل', 'value': 'last_year'}
                    ],
                    value='budget',
                    labelStyle={'display': 'block', 'marginBottom': '10px', 'fontSize': '14px'},
                    style={'marginBottom': '20px'}
                )
            ], style={'marginBottom': '25px'}),

            html.Div([
            html.Label("💱 واحد پولی:", style={'fontWeight': 'bold', 'color': '#34495e'}),
            dcc.RadioItems(
                id='currency-radio',
                options=[
                    {'label': '💰 ریال', 'value': 'rial'},
                    {'label': '💵 دلار', 'value': 'dollar'}
                ],
                value='rial',
                labelStyle={'display': 'block', 'marginBottom': '10px', 'fontSize': '14px'},
                style={'marginBottom': '20px'}
            )
            ], id='currency-container', style={'display': 'block', 'marginBottom': '25px'}),




             html.Div([
                html.Label("🏭 انتخاب مجتمع:", style={'fontWeight': 'bold', 'color': '#34495e'}),
                dcc.Dropdown(
                    id='complex-dropdown',
                    options=[],
                    value='کل شرکت',
                    style={'marginBottom': '20px'}
                )
            ], id='complex-dropdown-container', style={'display': 'none', 'marginBottom': '25px'}),
            
            # دراپ داون واحد
            html.Div([
                html.Label("🏭 انتخاب واحد:", style={'fontWeight': 'bold', 'color': '#34495e'}),
                dcc.Dropdown(
                    id='unit-dropdown', 
                    options=[],
                    value='کل واحدها',
                    style={'marginBottom': '20px'}
                )
            ], id='unit-dropdown-container', style={'display': 'none', 'marginBottom': '25px'}),


            html.Div([
            html.Label("📈 نوع انحراف:", style={'fontWeight': 'bold', 'color': '#34495e'}),
            dcc.RadioItems(
                id='deviation-type-radio',
                options=[
                    {'label': '💰 انحراف مبلغ', 'value': 'amount'},
                    {'label': '📦 انحراف مقدار', 'value': 'quantity'},
                    {'label': '📊 انحراف نرخ', 'value': 'rate'}
                ],
                value='amount',
                labelStyle={'display': 'block', 'marginBottom': '10px', 'fontSize': '14px'},
                style={'marginBottom': '20px'}
            )
        ], id='deviation-type-container', style={'display': 'none', 'marginBottom': '25px'}),


            html.Div([
                html.Label("📊 طبقه‌بندی نمودارها:", style={'fontWeight': 'bold', 'color': '#34495e'}),
                dcc.RadioItems(
                    id='sales-grouping-radio',
                    options=[
                        {'label': '📦 نوع فروش', 'value': 'sales_type'},
                        {'label': '🏷️ محصولات', 'value': 'products'}
                    ],
                    value='sales_type',
                    labelStyle={'display': 'block', 'marginBottom': '10px', 'fontSize': '14px'},
                    style={'marginBottom': '20px'}
                )
            ], id='sales-grouping-container', style={'display': 'none', 'marginBottom': '25px'}),

            html.Div([
            html.Label("📈 نوع انحراف خوراک:", style={'fontWeight': 'bold', 'color': '#34495e'}),
            dcc.RadioItems(
                id='khorak-deviation-type-radio',
                options=[
                    {'label': '📦 انحراف مقدار', 'value': 'quantity'},
                    {'label': '📊 انحراف نرخ', 'value': 'rate'},
                    {'label': '💰 انحراف مبلغ', 'value': 'amount'}
                ],
                value='amount',
                labelStyle={'display': 'block', 'marginBottom': '10px', 'fontSize': '14px'},
                style={'marginBottom': '20px'}
            )
          ], id='khorak-deviation-type-container', style={'display': 'none', 'marginBottom': '25px'}),
                    
                                        
            # اسلایدر سطح هشدار
            html.Div([
                html.Label("🚨 سطح هشدار (%)", style={'fontWeight': 'bold', 'color': '#34495e'}),
                dcc.Slider(
                    id='alert-threshold-slider',
                    min=5, max=50, step=5, value=15,
                    marks={i: {'label': f'{i}%', 'style': {'color': '#2c3e50'}} for i in range(5, 55, 10)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ]),
            html.Div([
                html.Button(
                    "❌ خروج از برنامه", 
                    id='exit-button',
                    n_clicks=0,
                    style={
                        'backgroundColor': '#e74c3c',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '10px',
                        'padding': '12px 24px',
                        'fontSize': '14px',
                        'fontWeight': 'bold',
                        'cursor': 'pointer',
                        'width': '100%',
                        'marginTop': '20px',
                        'transition': 'all 0.3s ease'
                    }
                )
            ], style={'marginTop': '25px'}),
            ], 
                 
                 className="control-panel", style={
                'width': '400px', 
                'margin': '0 auto 40px auto'
            }),
        
                
        # بخش کارت‌های KPI
        html.Div(id='kpi-container', className="kpi-container"),# بخش نمودارها
        html.Div([
            html.H3("📈 نمودارهای تحلیلی", style={
                'textAlign': 'center', 
                'color': '#2c3e50',
                'marginBottom': '20px'
            }),
            
            html.Div([
                html.H4("📊 نمودار انحراف عملکرد", style={'textAlign': 'center', 'color': '#34495e'}),
                dcc.Graph(id='deviation-chart')
            ], style={
                'backgroundColor': 'white',
                'borderRadius': '15px',
                'padding': '20px',
                'marginBottom': '20px',
                'boxShadow': '0 4px 20px rgba(0,0,0,0.1)'
            }),
            
            # نمودار مقایسه ستونی
            html.Div([
                html.H4("📊 مقایسه ستونی", style={'textAlign': 'center', 'color': '#34495e'}),
                dcc.Graph(id='comparison-chart')
            ], style={
                'backgroundColor': 'white',
                'borderRadius': '15px',
                'padding': '20px',
                'marginBottom': '30px',
                'boxShadow': '0 4px 20px rgba(0,0,0,0.1)'
            })
        ]),
            
       html.Div(id='third-chart-container', style={
    'backgroundColor': 'white',
    'borderRadius': '15px',
    'padding': '20px', 
    'marginBottom': '20px',
    'boxShadow': '0 4px 20px rgba(0,0,0,0.1)'
})

    
      
    ])

@data_callback(
    Output('kpi-container', 'children'),
    [
        Input('alert-threshold-slider', 'value'),
        Input('comparison-source-radio', 'value'),
        Input('data-type-radio', 'value'),
        Input('report-type-radio', 'value'),
        Input('currency-radio', 'value'),
        Input('complex-dropdown', 'value'),
        Input('unit-dropdown', 'value')
    ]
)
def update_kpi_cards(threshold, source, data_type, report_type, currency,selected_complex, selected_unit):
    global financial_data, cost_data, overhead_data, admin_data, sales_data,sales_detail_data,tolid_data
    exchange_rates = {}
    if sales_data is not None:
        exchange_rates = calculate_exchange_rates(sales_data)
    if data_type == 'current':
        current_exchange_rate = exchange_rates.get('month_current', 1)
        budget_exchange_rate = exchange_rates.get('budget_current', 1)
        last_year_exchange_rate = exchange_rates.get('month_lastyear', 1)
    else:  # cumulative
        current_exchange_rate = exchange_rates.get('month_tajomi', 1)
        budget_exchange_rate = exchange_rates.get('budget_tajomi', 1)
        last_year_exchange_rate = exchange_rates.get('month_lastyear_tajmoii', 1)
    if report_type == 'cost_analysis':
        if cost_data is None:
            return [html.Div("❌ داده‌های بهای تمام شده موجود نیست", style={'textAlign': 'center', 'color': 'red'})]
        selected_data = cost_data
        selected_items = cost_items
    elif report_type == 'overhead_analysis':
        if overhead_data is None:
             return [html.Div("❌ داده‌های هزینه‌های سربار موجود نیست", style={'textAlign': 'center', 'color': 'red'})]
        selected_data = overhead_data
        selected_items = overhead_items
    elif report_type == 'admin_analysis':
        if admin_data is None:
            return [html.Div("❌ داده‌های هزینه‌های عمومی و اداری موجود نیست", style={'textAlign': 'center', 'color': 'red'})]
        selected_data = admin_data
        selected_items = admin_items
    
   
    elif report_type == 'sales_analysis':
        if sales_detail_data is None:
             return [html.Div("❌ داده‌های فروش موجود نیست", style={'textAlign': 'center', 'color': 'red'})]
        return generate_sales_kpi_cards(
        selected_complex or 'کل شرکت',
        selected_unit or 'کل واحدها',
        data_type, source, currency, exchange_rates,threshold
    )

    elif report_type == 'khorak_analysis':
        if khorak_data is None:
            return [html.Div("❌ داده‌های خوراک موجود نیست", style={'textAlign': 'center', 'color': 'red'})]
        return generate_khorak_kpi_cards(data_type, source, currency, threshold,exchange_rates)




    elif report_type == 'production_analysis':
        if tolid_data is None:
            return [html.Div("❌ داده‌های تولید موجود نیست", style={'textAlign': 'center', 'color': 'red'})]
        
        return generate_production_kpi_cards(
            selected_complex or 'کل شرکت',
            selected_unit or 'کل واحدها',
            data_type, source, threshold
        )
    else:
        if financial_data is None:
                return [html.Div("❌ داده‌های مالی موجود نیست", style={'textAlign': 'center', 'color': 'red'})]
        selected_data = financial_data
        selected_items = items

    cards = [generate_card(item, threshold, source, data_type, selected_data, currency, 
                      current_exchange_rate, budget_exchange_rate, last_year_exchange_rate) 
          for item in selected_items]
    return cards   
    
    
    


@data_callback(
    [Output('deviation-chart', 'figure'),
     Output('comparison-chart', 'figure'),
     Output('third-chart-container', 'children')],
    [
        Input('alert-threshold-slider', 'value'),
        Input('comparison-source-radio', 'value'),
        Input('data-type-radio', 'value'),
        Input('report-type-radio', 'value'),
        Input('currency-radio', 'value'),
        Input('complex-dropdown', 'value'),
        Input('unit-dropdown', 'value'),
        Input('deviation-type-radio', 'value'),
        Input('sales-grouping-radio', 'value'),
         Input('khorak-deviation-type-radio', 'value')
        
    ]

)

def update_charts(threshold, source, data_type, report_type, currency, selected_complex, selected_unit, deviation_type,grouping,deviation_type1):
    global financial_data, cost_data, cash_data, overhead_data, admin_data, sales_data,tolid_data,sood_data    
    exchange_rates = {}
    if sales_data is not None:
        exchange_rates = calculate_exchange_rates(sales_data)
    
    if data_type == 'current':
        current_exchange_rate = exchange_rates.get('month_current', 1)
        budget_exchange_rate = exchange_rates.get('budget_current', 1)
        last_year_exchange_rate = exchange_rates.get('month_lastyear', 1)
    else:  # cumulative
        current_exchange_rate = exchange_rates.get('month_tajomi', 1)
        budget_exchange_rate = exchange_rates.get('budget_tajomi', 1)
        last_year_exchange_rate = exchange_rates.get('month_lastyear_tajmoii', 1)
        
    if report_type == 'cost_analysis':
        if cost_data is None:
            empty_fig = go.Figure()
            empty_fig.update_layout(title="داده‌های بهای تمام شده موجود نیست")
            return empty_fig, empty_fig, empty_fig
        selected_data = cost_data
        selected_items = cost_items
    elif report_type == 'overhead_analysis':
        if overhead_data is None:
            empty_fig = go.Figure()
            empty_fig.update_layout(title="داده‌های هزینه‌های سربار موجود نیست")
            return empty_fig, empty_fig, empty_fig
        selected_data = overhead_data
        selected_items = overhead_items  
    elif report_type == 'admin_analysis':
        if admin_data is None:
            empty_fig = go.Figure()
            empty_fig.update_layout(title="داده‌های هزینه‌های عمومی و اداری موجود نیست")
            return empty_fig, empty_fig, empty_fig
        selected_data = admin_data
        selected_items = admin_items



    # در بخش مربوط به sales_analysis در تابع update_charts:
    elif report_type == 'sales_analysis':
        if sales_detail_data is None:
            empty_fig = go.Figure()
            empty_fig.update_layout(title="داده‌های فروش موجود نیست")
            return empty_fig, empty_fig, html.Div("داده‌های فروش موجود نیست")
        
        # ایجاد نمودارهای فروش
        deviation_fig, comparison_fig = create_sales_charts(
            selected_complex or 'کل شرکت', 
            selected_unit or 'کل واحدها',
            data_type, deviation_type, currency, threshold, source, exchange_rates, grouping
        )
        
        # ایجاد نمودارهای پای
        pie_charts = create_sales_pie_charts(
            selected_complex or 'کل شرکت',
            selected_unit or 'کل واحدها', 
            data_type, currency, grouping, exchange_rates
        )
        
        # ایجاد نمودارهای پای جدید برای واحدها و مجتمع‌ها
        unit_complex_pie_charts = create_sales_unit_complex_pie_charts(
            selected_complex or 'کل شرکت',
            selected_unit or 'کل واحدها',
            data_type, currency, exchange_rates
            
        )
        
        # ترکیب همه نمودارها در یک container
        combined_charts = html.Div([
            pie_charts,
            html.Hr(style={'margin': '30px 0', 'borderColor': '#e0e0e0'}),
            unit_complex_pie_charts
        ])
        
        return deviation_fig, comparison_fig, combined_charts
            
           


    elif report_type == 'khorak_analysis':
        if khorak_data is None:
            empty_fig = go.Figure()
            empty_fig.update_layout(title="داده‌های خوراک موجود نیست")
            return empty_fig, empty_fig, html.Div("داده‌های خوراک موجود نیست")
        
        # ایجاد نمودارهای انحراف و مقایسه
        deviation_fig, comparison_fig = create_khorak_charts(
            data_type, deviation_type1, source, threshold, currency, exchange_rates
        )
        
        # ایجاد نمودارهای پای برای مقدار و مبلغ خوراک
        qty_pie, amt_pie = create_khorak_pie_charts(data_type, currency, threshold, exchange_rates)
        
        return deviation_fig, comparison_fig, html.Div([
            html.Div([
                html.Div([
                    html.H4("🥧 سهم از مقدار خوراک", style={'textAlign': 'center', 'color': '#34495e'}),
                    dcc.Graph(figure=qty_pie)
                ], style={'width': '48%', 'display': 'inline-block'}),
                html.Div([
                    html.H4("🥧 سهم از مبلغ خوراک", style={'textAlign': 'center', 'color': '#34495e'}),
                    dcc.Graph(figure=amt_pie)
                ], style={'width': '48%', 'display': 'inline-block', 'margin-left': '4%'})
            ])
        ])
    
    elif report_type == 'production_analysis':
        if tolid_data is None:
            empty_fig = go.Figure()
            empty_fig.update_layout(title="داده‌های تولید موجود نیست")
            return empty_fig, empty_fig, html.Div("داده‌های تولید موجود نیست")
        
        # Create production charts
        deviation_fig, comparison_fig = create_production_charts(
            selected_complex or 'کل شرکت', 
            selected_unit or 'کل واحدها',
            data_type, threshold, source
        )
        
        # Create pie charts
        pie_charts = create_production_pie_charts(
            selected_complex or 'کل شرکت',
            selected_unit or 'کل واحدها', 
            data_type
        )
        
        # Create unit and complex pie charts
        unit_complex_pie_charts = create_production_unit_complex_pie_charts(
            selected_complex or 'کل شرکت',
            selected_unit or 'کل واحدها',
            data_type
        )
        
        # Combine all charts
        combined_charts = html.Div([
            pie_charts,
            html.Hr(style={'margin': '30px 0', 'borderColor': '#e0e0e0'}),
            unit_complex_pie_charts
        ])
        
        return deviation_fig, comparison_fig, combined_charts

    
    
    else:
        if financial_data is None:
            empty_fig = go.Figure()
            empty_fig.update_layout(title="داده‌ای برای نمایش موجود نیست")
            return empty_fig, empty_fig, empty_fig
        selected_data = financial_data
        selected_items = items
    
    chart_data = []
    for item in selected_items:
        row = selected_data[selected_data['شرح'].astype(str).str.strip() == item.strip()]
        if not row.empty:
            current_col, budget_col, last_year_col = get_column_names(data_type, selected_data)
            
            actual = row[current_col].values[0] if current_col and current_col in selected_data.columns else 0
            budget = row[budget_col].values[0] if budget_col and budget_col in selected_data.columns else 0
            last_year = row[last_year_col].values[0] if last_year_col and last_year_col in selected_data.columns else 0
            
            actual_converted = convert_currency(actual, current_exchange_rate, currency)
            budget_converted = convert_currency(budget, budget_exchange_rate, currency)
            last_year_converted = convert_currency(last_year, last_year_exchange_rate, currency)
            base_converted = budget_converted if source == 'budget' else last_year_converted
            if base_converted != 0:
                raw_deviation = ((actual_converted - base_converted) / base_converted) * 100
                if item.strip() in negative_items:
                    deviation = -raw_deviation
                else:
                    deviation = raw_deviation
            else:
                deviation = 0
            
            chart_data.append({
                'item': item,
                'deviation': deviation,
                'actual': actual_converted,
                'budget': budget_converted,
                'last_year': last_year_converted
            })
    deviation_fig = go.Figure()
    
    colors = []
    for d in [data['deviation'] for data in chart_data]:
        if d >= threshold:
            colors.append('#00C9FF')
        elif d >= 0:
            colors.append('#667eea')
        elif d >= -threshold:
            colors.append('#f093fb')
        else:
            colors.append('#ff6b6b')
    
    deviation_fig.add_trace(go.Bar(
        x=[data['deviation'] for data in chart_data],
        y=[data['item'] for data in chart_data],
        orientation='h',
        marker_color=colors,
        text=[f"{data['deviation']:.1f}%" for data in chart_data],
        textposition='auto',
        name='انحراف عملکرد'
    ))
    
    deviation_fig.add_vline(x=threshold, line_dash="dash", line_color="green", 
                           annotation_text=f"حد مطلوب +{threshold}%")
    deviation_fig.add_vline(x=-threshold, line_dash="dash", line_color="red", 
                           annotation_text=f"حد هشدار -{threshold}%")
    
    deviation_fig.update_layout(
        title=f"انحراف عملکرد نسبت به {'بودجه' if source == 'budget' else 'سال قبل'}",
        xaxis_title="درصد انحراف",
        font=dict(family="Vazir", size=12),
        plot_bgcolor='rgba(248,249,250,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=600,
        showlegend=False
    )
    
    comparison_fig = go.Figure()
    
    currency_label = "دلار" if currency == 'dollar' else "میلیون ریال"
    
    items_list = [data['item'] for data in chart_data]
    actual_values = [data['actual'] for data in chart_data]
    budget_values = [data['budget'] for data in chart_data]
    last_year_values = [data['last_year'] for data in chart_data]
    
    comparison_fig.add_trace(go.Bar(
        name='عملکرد فعلی',
        x=items_list,
        y=actual_values,
        marker_color='#667eea',
        hovertemplate=f'عملکرد فعلی: %{{y:,.0f}} {currency_label}<extra></extra>'
    ))
    
    comparison_fig.add_trace(go.Bar(
        name='بودجه',
        x=items_list,
        y=budget_values,
        marker_color='#00C9FF',
        hovertemplate=f'بودجه: %{{y:,.0f}} {currency_label}<extra></extra>'
    ))
    
    comparison_fig.add_trace(go.Bar(
        name='سال قبل',
        x=items_list,
        y=last_year_values,
        marker_color='#f093fb',
        hovertemplate=f'سال قبل: %{{y:,.0f}} {currency_label}<extra></extra>'
    ))
    
    comparison_fig.update_layout(
        title=f"مقایسه عملکرد فعلی با بودجه و سال قبل ({currency_label})",
        xaxis_title="آیتم‌های مالی",
        yaxis_title=f"مبلغ ({currency_label})",
        barmode='group',
        font=dict(family="Vazir", size=12),
        plot_bgcolor='rgba(248,249,250,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=800,
        xaxis={'tickangle': -45}
    )
    
    if report_type == 'cost_analysis':
        pie_fig = pie_fig = create_cost_pie_chart(data_type, selected_data, currency, current_exchange_rate)
        third_chart_content = [
            html.H4(f"🥧 ترکیب اجزای بهای تمام شده ({currency_label})", 
                   style={'textAlign': 'center', 'color': '#34495e'}),
            dcc.Graph(figure=pie_fig, config={'displayModeBar': False})
        ]
    elif report_type == 'overhead_analysis':
        pie_fig = create_overhead_pie_chart(data_type, selected_data, currency, current_exchange_rate)

        third_chart_content = [
            html.H4(f"🥧 ترکیب هزینه‌های سربار ({currency_label})", 
                   style={'textAlign': 'center', 'color': '#34495e'}),
            dcc.Graph(figure=pie_fig, config={'displayModeBar': False})
        ]
    elif report_type == 'admin_analysis':
        pie_fig = create_admin_pie_chart(data_type, selected_data, currency, current_exchange_rate)

        third_chart_content = [
            html.H4(f"🥧 ترکیب هزینه‌های عمومی و اداری ({currency_label})", 
                   style={'textAlign': 'center', 'color': '#34495e'}),
            dcc.Graph(figure=pie_fig, config={'displayModeBar': False})
        ]
    
    
    
    elif report_type == 'khorak_analysis':
        if khorak_data is None:
            empty_fig = go.Figure()
            empty_fig.update_layout(title="داده‌های خوراک موجود نیست")
            return empty_fig, empty_fig, html.Div("داده‌های خوراک موجود نیست")

        
        # ایجاد نمودارهای انحراف و مقایسه
        deviation_fig, comparison_fig = create_khorak_charts(data_type, deviation_type1, source, threshold, currency,exchange_rates)
        
        # ایجاد نمودار پای
        pie_fig = create_khorak_pie_chart(data_type, currency, threshold,exchange_rates)
        
        return deviation_fig, comparison_fig, html.Div([
            html.H4("🥧 سهم خوراک‌ها", style={'textAlign': 'center', 'color': '#34495e'}),
            dcc.Graph(figure=pie_fig)
        ])
    
    elif report_type == 'profit_loss':
        # محاسبه نرخ ارز
        exchange_rate = current_exchange_rate if data_type == 'current' else budget_exchange_rate
        
        # ایجاد نمودارهای سود و بهای تمام شده
        third_chart_content = create_profit_cost_pie_charts(data_type, currency, exchange_rate)
    
    
    
    else:  # صورت سود و زیان
        if cash_data is not None:
            third_chart_content = create_cash_flow_infographic(cash_data, currency, current_exchange_rate)
        else:
            third_chart_content = html.Div([
                html.H4("❌ داده‌های نقدینگی موجود نیست", 
                       style={'textAlign': 'center', 'color': '#e74c3c'})
            ])
    
    return deviation_fig, comparison_fig, third_chart_content




#@app.callback(
    #[Output('complex-dropdown-container', 'style'),
     #Output('unit-dropdown-container', 'style'),
     #Output('deviation-type-container', 'style'),
     #Output('sales-grouping-container', 'style')],
    #[Input('report-type-radio', 'value')]
#)
#def toggle_sales_controls(report_type):
    #if report_type == 'sales_analysis':
        #return {'display': 'block', 'marginBottom': '25px'}, {'display': 'block', 'marginBottom': '25px'}, {'display': 'block', 'marginBottom': '25px'},{'display': 'block', 'marginBottom': '25px'} 
    #else:
        #return {'display': 'none'}, {'display': 'none'}, {'display': 'none'},{'display': 'none'}

# 6. کال‌بک برای پر کردن دراپ داون مجتمع:
@data_callback(
    Output('complex-dropdown', 'options'),
    [Input('report-type-radio', 'value')]
)
def update_complex_dropdown(report_type):
    global sales_detail_data
    if (report_type == 'sales_analysis' and sales_detail_data is not None) or report_type == 'production_analysis':
        complexes = ['کل شرکت'] + list(sales_detail_data['مجتمع'].unique())
        return [{'label': complex_name, 'value': complex_name} for complex_name in complexes]
    return []   
    

# 7. کال‌بک برای پر کردن دراپ داون واحد بر اساس مجتمع انتخاب شده:
@data_callback(
    Output('unit-dropdown', 'options'),
    [Input('complex-dropdown', 'value')]
)
def update_unit_dropdown(selected_complex):
    global sales_detail_data
    if sales_detail_data is not None and selected_complex:
        if selected_complex == 'کل شرکت':
            units = ['کل واحدها'] + list(sales_detail_data['واحد'].unique())
        else:
            filtered_data = sales_detail_data[sales_detail_data['مجتمع'] == selected_complex]
            units = ['کل واحدها'] + list(filtered_data['واحد'].unique())
        return [{'label': unit, 'value': unit} for unit in units]
    return []





@data_callback(
    [Output('complex-dropdown-container', 'style'),
     Output('unit-dropdown-container', 'style'),
     Output('deviation-type-container', 'style'),
     Output('sales-grouping-container', 'style'),
     Output('khorak-deviation-type-container', 'style')],  # خروجی جدید برای کنترل نوع انحراف خوراک
    [Input('report-type-radio', 'value')]
)
def toggle_controls(report_type):
    if report_type == 'sales_analysis':
        return {'display': 'block'}, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}, {'display': 'none'}
    elif report_type == 'khorak_analysis':
        return {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'block'}
    elif report_type == 'production_analysis':
        return {'display': 'block'}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
    
    else:
        return {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}




@data_callback(
    Output('currency-container', 'style'),
    [Input('report-type-radio', 'value')]
)
def toggle_currency_control(report_type):
    if report_type == 'production_analysis':
        return {'display': 'none', 'marginBottom': '25px'}
    else:
        return {'display': 'block', 'marginBottom': '25px'}








@app.callback(
    Output('status-message', 'children'),
    Input('exit-button', 'n_clicks'),
    prevent_initial_call=True
)
def handle_exit(n_clicks):
    if n_clicks > 0:
        # نمایش پیام خروج
        return html.Div([
            "✅ برای خروج، صفحه را ببندید یا از سیستم خارج شوید."
        ], style={
            'position': 'fixed',
            'top': '50%',
            'left': '50%',
            'transform': 'translate(-50%, -50%)',
            'backgroundColor': '#2ecc71',
            'color': 'white',
            'padding': '20px 40px',
            'borderRadius': '10px',
            'fontSize': '16px',
            'fontWeight': 'bold',
            'zIndex': '9999',
            'textAlign': 'center',
            'boxShadow': '0 4px 20px rgba(0,0,0,0.3)'
        })
    return ""
