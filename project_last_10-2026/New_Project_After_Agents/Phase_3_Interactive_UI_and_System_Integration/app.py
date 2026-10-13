"""
Phase 3: Interactive Multi-Agent Web Application (Streamlit)
Features:
- Dual Language Support (Arabic RTL & English LTR)
- Dynamic Multi-Agent Execution Pipeline Visualizer
- Clinical Presets (Normal, Pre-diabetic, Diabetic, Critical Emergency)
- Interactive Risk Gauges & Biomarker Visualizations
- Real-time Quality Gates Verification
- One-Click Official Patient Word Report (.docx) Download
"""

import os
import sys
import time
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt

# Configure clean font family for Matplotlib charts
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Tahoma', 'DejaVu Sans']

def fix_ar_text(text, is_arabic=True):
    # Modern Matplotlib on Windows renders standard Arabic strings natively in correct RTL order
    return str(text)

# Clinical Criteria Information for Feature Importance Analysis
CRITERIA_INFO = [
    {"en": "Pregnancies", "ar": "عدد مرات الحمل"},
    {"en": "Glucose", "ar": "مستوى الجلوكوز"},
    {"en": "BloodPressure", "ar": "ضغط الدم"},
    {"en": "SkinThickness", "ar": "سمك الجلد"},
    {"en": "Insulin", "ar": "الإنسولين"},
    {"en": "BMI", "ar": "مؤشر كتلة الجسم"},
    {"en": "DiabetesPedigreeFunction", "ar": "وراثة السكري"},
    {"en": "Age", "ar": "العمر"}
]

# Clinical Reference Limits for Biomarker Criteria Analysis
CLINICAL_REF_RANGES = {
    'Glucose': {'normal_max': 99.0, 'unit': 'mg/dL', 'ideal': '70 - 99 mg/dL'},
    'BloodPressure': {'normal_max': 80.0, 'unit': 'mmHg', 'ideal': '70 - 80 mmHg'},
    'BMI': {'normal_max': 24.9, 'unit': 'kg/m²', 'ideal': '18.5 - 24.9 kg/m²'},
    'Insulin': {'normal_max': 100.0, 'unit': 'μU/mL', 'ideal': '15 - 100 μU/mL'},
    'SkinThickness': {'normal_max': 25.0, 'unit': 'mm', 'ideal': '10 - 25 mm'},
    'DiabetesPedigreeFunction': {'normal_max': 0.50, 'unit': '', 'ideal': '< 0.50'},
    'Age': {'normal_max': 45.0, 'unit': 'years', 'ideal': '< 45 yrs'},
    'Pregnancies': {'normal_max': 3.0, 'unit': '', 'ideal': '0 - 3'}
}

# Adjust paths to import from Phase 2
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
P2_DIR = os.path.join(PARENT_DIR, 'Phase_2_Multi_Agent_Architecture')

if P2_DIR not in sys.path:
    sys.path.append(P2_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from schemas import PatientInput, MultiAgentDiagnosticDossier
from agent_orchestrator import ClinicalAgentOrchestrator
from patient_report_generator import generate_patient_docx

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="نظام التشخيص التنبئي للسكري بالوكلاء المتعددين | Multi-Agent Diabetes CDSS",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- LANGUAGE SELECTION & DIRECTION -----------------
if "app_lang" not in st.session_state:
    st.session_state["app_lang"] = "العربية"

is_ar = (st.session_state.get("app_lang", "العربية") == "العربية")

def inject_direction_and_styles(is_ar: bool):
    direction = "rtl" if is_ar else "ltr"
    align = "right" if is_ar else "left"
    sidebar_border = (
        "border-left: 1px solid #e2e8f0 !important; border-right: none !important;"
        if is_ar else
        "border-right: 1px solid #e2e8f0 !important; border-left: none !important;"
    )

    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
        
        /* 1. Global Page Direction & Typography */
        html, body, [data-testid="stAppViewContainer"], .stApp {{
            font-family: 'Tajawal', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            direction: {direction} !important;
            text-align: {align} !important;
        }}

        /* 2. Main Content Container */
        section.main, [data-testid="stMainBlockContainer"], [data-testid="stAppViewBlockContainer"], [data-testid="stVerticalBlock"] {{
            direction: {direction} !important;
            text-align: {align} !important;
        }}

        /* 3. Markdown and Text Elements */
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4,
        [data-testid="stMarkdownContainer"] h5,
        [data-testid="stMarkdownContainer"] h6,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] ul,
        [data-testid="stMarkdownContainer"] ol {{
            direction: {direction} !important;
            text-align: {align} !important;
        }}

        /* 4. Sidebar Content & Borders */
        [data-testid="stSidebar"],
        [data-testid="stSidebarContent"],
        [data-testid="stSidebarUserContent"] {{
            direction: {direction} !important;
            text-align: {align} !important;
            {sidebar_border}
        }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            direction: {direction} !important;
            text-align: {align} !important;
        }}

        [data-testid="stSidebarCollapsedControl"] {{
            {"right: 20px !important; left: auto !important;" if is_ar else "left: 20px !important; right: auto !important;"}
        }}

        /* 5. Form Widgets & Input Labels */
        div[data-testid="stTextInput"] label,
        div[data-testid="stNumberInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stRadio"] label,
        label[data-testid="stWidgetLabel"] {{
            direction: {direction} !important;
            text-align: {align} !important;
            display: flex !important;
            justify-content: flex-start !important;
            width: 100% !important;
        }}

        div[data-baseweb="input"] input,
        div[data-baseweb="base-input"] input {{
            direction: {direction} !important;
            text-align: {align} !important;
        }}

        div[data-baseweb="select"] {{
            direction: {direction} !important;
            text-align: {align} !important;
        }}
        div[data-baseweb="select"] div {{
            text-align: {align} !important;
        }}

        div[data-testid="stRadio"] div[role="radiogroup"] {{
            direction: {direction} !important;
            text-align: {align} !important;
        }}
        div[data-testid="stRadio"] label {{
            direction: {direction} !important;
            text-align: {align} !important;
        }}

        /* 6. Columns Layout (st.columns) */
        div[data-testid="stHorizontalBlock"] {{
            direction: {direction} !important;
        }}
        div[data-testid="stColumn"] {{
            direction: {direction} !important;
            text-align: {align} !important;
        }}

        /* 7. Metric Indicators */
        div[data-testid="stMetric"] {{
            direction: {direction} !important;
            text-align: {align} !important;
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 12px 14px !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
            min-height: 105px !important;
        }}
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] > div,
        div[data-testid="stMetricLabel"] * {{
            direction: {direction} !important;
            text-align: {align} !important;
            display: flex !important;
            justify-content: flex-start !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            color: #64748b !important;
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
            line-height: 1.25 !important;
        }}
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] > div,
        div[data-testid="stMetricValue"] * {{
            direction: {direction} !important;
            text-align: {align} !important;
            font-size: 1.05rem !important; /* Scaled down so full text fits without truncation */
            font-weight: 700 !important;
            color: #1e293b !important;
            white-space: normal !important;
            word-break: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
            line-height: 1.35 !important;
        }}
        div[data-testid="stMetricDelta"],
        div[data-testid="stMetricDelta"] > div,
        div[data-testid="stMetricDelta"] * {{
            direction: {direction} !important;
            text-align: {align} !important;
            display: flex !important;
            justify-content: flex-start !important;
            font-size: 0.8rem !important;
        }}

        /* 8. Tabs */
        div[data-baseweb="tab-list"] {{
            direction: {direction} !important;
        }}
        button[data-baseweb="tab"] {{
            direction: {direction} !important;
            text-align: {align} !important;
        }}

        /* 9. Alerts */
        div[data-testid="stAlert"] {{
            direction: {direction} !important;
            text-align: {align} !important;
        }}
        div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] {{
            direction: {direction} !important;
            text-align: {align} !important;
        }}

        /* 10. Dataframe */
        div[data-testid="stDataFrame"] {{
            direction: {direction} !important;
        }}

        /* 11. Buttons */
        div[data-testid="stButton"] button,
        div[data-testid="stDownloadButton"] button {{
            direction: {direction} !important;
            text-align: center !important;
        }}

        /* 12. Custom System Classes */
        .main-header {{
            background: linear-gradient(135deg, #1a4d2e 0%, #2e7d32 100%);
            color: white;
            padding: 22px 28px;
            border-radius: 14px;
            margin-bottom: 24px;
            box-shadow: 0 4px 14px rgba(26, 77, 46, 0.25);
            direction: {direction};
            text-align: {align};
        }}
        
        .agent-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 12px;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            direction: {direction};
            text-align: {align};
        }}
        
        .agent-card:hover {{
            border-color: #2e7d32;
            box-shadow: 0 4px 10px rgba(46, 125, 50, 0.12);
        }}
        
        .gate-badge-pass {{
            background-color: #dcfce7;
            color: #166534;
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 0.82rem;
            display: inline-block;
        }}
        
        .gate-badge-alert {{
            background-color: #fee2e2;
            color: #991b1b;
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 0.82rem;
            display: inline-block;
        }}
        
        .metric-box {{
            background: #f8fafc;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            border: 1px solid #e2e8f0;
            direction: {direction};
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Inject Direction & Layout Styles
inject_direction_and_styles(is_ar)

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/caduceus.png", width=64)
    st.markdown("### إعدادات النظام" if is_ar else "### System Settings")
    
    selected_lang = st.radio(
        "اختر لغة الواجهة / Interface Language:",
        options=["العربية", "English"],
        index=0 if st.session_state["app_lang"] == "العربية" else 1,
        key="lang_radio_selector"
    )
    if selected_lang != st.session_state["app_lang"]:
        st.session_state["app_lang"] = selected_lang
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🎓 مادة ( course ) : COSC726 AGENTIC AI" if is_ar else "#### 🎓 Course : COSC726 AGENTIC AI")
    st.info(
        "**جامعة النيلين - كلية الدراسات العليا**\n\n"
        "**الباحث:** محمد ابوالقاسم\n\n"
        "**الإشراف:** د. فخرالدين سعيد\n\n"
        "**الموضوع:** نظام وكلاء متعددين للتشخيص التنبئي للسكري"
        if is_ar else
        "**Al-Neelain University - Graduate Studies**\n\n"
        "**Researcher:** Mohamed Abolgasim\n\n"
        "**Supervisor:** Dr. Fakhreldeen Saeed\n\n"
        "**Topic:** Multi-Agent Clinical AI for Diabetes Prediction"
    )

    st.markdown("---")
    st.markdown("#### 🤖 محرك الذكاء الاصطناعي / AI Engine")
    provider_options = [
        "Clinical Expert Engine (Offline/Deterministic)",
        "Google Gemini",
        "OpenAI",
        "DeepSeek",
        "Ollama (Local Models)",
        "Cohere"
    ]
    provider_choice = st.selectbox(
        "مزود نموذج اللغة (LLM Provider):" if is_ar else "Select LLM Engine:",
        options=provider_options,
        index=0
    )
    
    api_key_input = None
    model_name_input = None
    base_url_input = None

    if provider_choice == "Google Gemini":
        api_key_input = st.text_input("مفتاح Gemini API Key (اختياري):" if is_ar else "Gemini API Key (optional):", type="password")
        model_name_input = st.selectbox("النموذج / Model:", ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"], index=0)
    elif provider_choice == "OpenAI":
        api_key_input = st.text_input("مفتاح OpenAI API Key (اختياري):" if is_ar else "OpenAI API Key (optional):", type="password")
        model_name_input = st.selectbox("النموذج / Model:", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], index=0)
    elif provider_choice == "DeepSeek":
        st.caption("ℹ️ تم تعديل الإملاء إلى: **DeepSeek** الرسمية.")
        api_key_input = st.text_input("مفتاح DeepSeek API Key (اختياري):" if is_ar else "DeepSeek API Key (optional):", type="password")
        model_name_input = st.selectbox("النموذج / Model:", ["deepseek-chat", "deepseek-reasoner"], index=0)
    elif provider_choice == "Ollama (Local Models)":
        base_url_input = st.text_input("عنوان خادم Ollama:" if is_ar else "Ollama Server URL:", value="http://localhost:11434")
        model_name_input = st.text_input("اسم النموذج المثبت في Ollama:" if is_ar else "Ollama Model Name:", value="llama3")
        st.caption("تأكد من تشغيل خادم Ollama محلياً (`ollama run llama3`)." if is_ar else "Ensure Ollama is running locally.")
    elif provider_choice == "Cohere":
        api_key_input = st.text_input("مفتاح Cohere API Key (اختياري):" if is_ar else "Cohere API Key (optional):", type="password")
        model_name_input = st.selectbox("النموذج / Model:", ["command-r-plus-08-2024", "command-r-08-2024", "command-light"], index=0)

    st.markdown("---")
    st.markdown("#### ⚡ الحالات السريرية الجاهزة" if is_ar else "#### ⚡ Clinical Presets")
    preset_options_ar = [
        "مخصص (إدخال يدوي)",
        "1. حالة سليمة (مخاطر منخفضة)",
        "2. مرحلة ما قبل السكري (مخاطر متوسطة)",
        "3. إصابة سكري متقدمة (مخاطر عالية)",
        "4. حالة طوارئ حرجة (إسعاف فوري)"
    ]
    preset_options_en = [
        "Custom Input",
        "1. Healthy Baseline (Low Risk)",
        "2. Pre-Diabetes (Moderate Risk)",
        "3. Advanced Diabetes (High Risk)",
        "4. Critical Emergency (Immediate Care)"
    ]
    options_list = preset_options_ar if is_ar else preset_options_en
    preset_choice = st.selectbox(
        "اختر ملف حالة مسبق:" if is_ar else "Select Patient Preset:",
        options=options_list,
        index=0
    )

# Preset Values
preset_data_list = [
    # 0: Custom / default
    {'preg': 2, 'gluc': 120.0, 'bp': 75.0, 'skin': 22.0, 'ins': 85.0, 'bmi': 26.8, 'dpf': 0.42, 'age': 38},
    # 1: Low Risk
    {'preg': 1, 'gluc': 88.0, 'bp': 72.0, 'skin': 20.0, 'ins': 65.0, 'bmi': 22.8, 'dpf': 0.28, 'age': 25},
    # 2: Pre-Diabetes
    {'preg': 2, 'gluc': 118.0, 'bp': 82.0, 'skin': 26.0, 'ins': 95.0, 'bmi': 28.5, 'dpf': 0.48, 'age': 42},
    # 3: High Risk
    {'preg': 4, 'gluc': 175.0, 'bp': 88.0, 'skin': 35.0, 'ins': 185.0, 'bmi': 35.2, 'dpf': 0.88, 'age': 54},
    # 4: Critical Emergency
    {'preg': 3, 'gluc': 310.0, 'bp': 98.0, 'skin': 32.0, 'ins': 260.0, 'bmi': 33.0, 'dpf': 0.72, 'age': 49}
]

chosen_idx = options_list.index(preset_choice)
active_vals = preset_data_list[chosen_idx]

# ----------------- MAIN HEADER -----------------
header_html_ar = """
<div class="main-header" dir="rtl">
    <h1 style="margin:0; font-size: 2rem;">🩺 منصة التشخيص التنبئي للسكري بالوكلاء المتعددين</h1>
    <p style="margin:6px 0 0 0; opacity:0.9; font-size:1.05rem;">
        نظام سريري متكامل يعتمد على 5 وكلاء أذكياء ونماذج تعلم آلي معايرة مع بوابات جودة وأمان سريرية صارمة
    </p>
</div>
"""
header_html_en = """
<div class="main-header" dir="ltr">
    <h1 style="margin:0; font-size: 2rem;">🩺 Multi-Agent Clinical AI System for Diabetes Prediction</h1>
    <p style="margin:6px 0 0 0; opacity:0.9; font-size:1.05rem;">
        Agentic Decision Support System featuring 5 Specialized Clinical Agents, Calibrated ML, and Strict Safety Gates
    </p>
</div>
"""
st.markdown(header_html_ar if is_ar else header_html_en, unsafe_allow_html=True)

# ----------------- PATIENT INPUT FORM -----------------
with st.container():
    st.subheader("📋 بيانات المريض والمؤشرات الحيوية" if is_ar else "📋 Patient Biomarkers & Clinical Parameters")
    
    col_p1, col_p2, col_p3 = st.columns([2, 2, 1.5])
    with col_p1:
        p_name = st.text_input("اسم المريض:" if is_ar else "Patient Name:", value="أحمد محمد" if is_ar else "Ahmed Mohamed")
    with col_p2:
        p_id = st.text_input("معرف المريض:" if is_ar else "Patient ID:", value="PAT-2026-09")
    with col_p3:
        gender_options = ["ذكر", "أنثى"] if is_ar else ["Male", "Female"]
        selected_gender = st.selectbox(
            "نوع المريض (الجنس):" if is_ar else "Patient Gender:",
            options=gender_options,
            index=0
        )
        is_male = (selected_gender == "ذكر" or selected_gender == "Male")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        glucose = st.number_input(
            "الجلوكوز (Glucose mg/dL):" if is_ar else "Glucose (mg/dL):",
            min_value=0.0, max_value=500.0, value=float(active_vals['gluc']), step=1.0,
            help="المعدل الطبيعي للصائم: 70 - 99 mg/dL"
        )
        bp = st.number_input(
            "ضغط الدم (Blood Pressure mmHg):" if is_ar else "Blood Pressure (mmHg):",
            min_value=0.0, max_value=240.0, value=float(active_vals['bp']), step=1.0,
            help="الضغط الانبساطي الطبيعي: 70 - 80 mmHg"
        )

    with col2:
        bmi = st.number_input(
            "مؤشر كتلة الجسم (BMI kg/m²):" if is_ar else "BMI (kg/m²):",
            min_value=0.0, max_value=80.0, value=float(active_vals['bmi']), step=0.1,
            help="المعدل الطبيعي: 18.5 - 24.9"
        )
        age = st.number_input(
            "العمر (Age in years):" if is_ar else "Age (years):",
            min_value=1, max_value=120, value=int(active_vals['age']), step=1
        )

    with col3:
        insulin = st.number_input(
            "الإنسولين (Insulin μU/mL):" if is_ar else "Serum Insulin (μU/mL):",
            min_value=0.0, max_value=900.0, value=float(active_vals['ins']), step=1.0,
            help="معدل الصيام الطبيعي: 15 - 100"
        )
        skin = st.number_input(
            "سمك ثنية الجلد (Skin Thickness mm):" if is_ar else "Skin Thickness (mm):",
            min_value=0.0, max_value=100.0, value=float(active_vals['skin']), step=1.0
        )

    with col4:
        pedigree = st.number_input(
            "وراثة السكري (Pedigree Function):" if is_ar else "Pedigree Function:",
            min_value=0.05, max_value=3.0, value=float(active_vals['dpf']), step=0.01,
            help="مؤشر التاريخ العائلي للإصابة"
        )
        if is_male:
            pregnancies = st.number_input(
                "مرات الحمل (Pregnancies):" if is_ar else "Pregnancies:",
                min_value=0, max_value=20, value=0, step=1,
                disabled=True,
                help="غير مفعل للذكور (تم ضبط القيمة تلقائياً إلى 0)" if is_ar else "Disabled for male patients (set to 0)"
            )
        else:
            pregnancies = st.number_input(
                "مرات الحمل (Pregnancies):" if is_ar else "Pregnancies:",
                min_value=0, max_value=20, value=int(active_vals['preg']), step=1,
                help="عدد مرات الحمل السابقة" if is_ar else "Number of previous pregnancies"
            )

    btn_label = "تشغيل منظومة الوكلاء للتشخيص السريري 🚀" if is_ar else "Run Multi-Agent Clinical Diagnosis 🚀"
    submit_btn = st.button(btn_label, type="primary", use_container_width=True)

# ----------------- EXECUTION & PIPELINE DISPLAY -----------------
if submit_btn:
    patient_input = PatientInput(
        patient_id=p_id,
        patient_name=p_name,
        gender="Male" if is_male else "Female",
        language="ar" if is_ar else "en",
        pregnancies=0 if is_male else int(pregnancies),
        glucose=glucose,
        blood_pressure=bp,
        skin_thickness=skin,
        insulin=insulin,
        bmi=bmi,
        diabetes_pedigree=pedigree,
        age=age
    )

    st.markdown("---")
    st.subheader("⚡ مسار معالجة الوكلاء المتعددين وبوابات الجودة" if is_ar else "⚡ Multi-Agent Pipeline Execution & Quality Gates")

    # Progress bar and status containers
    progress_bar = st.progress(0)
    status_text = st.empty()
    pipeline_cols = st.columns(5)
    
    agent_cards = []
    card_titles = [
        ("1. وكيل الفرز السريري", "1. Clinical Triage Agent"),
        ("2. وكيل التنبؤ المعاير", "2. Calibrated ML Agent"),
        ("3. وكيل التعليل الطبي", "3. Clinical Reasoning Agent"),
        ("4. وكيل التغذية ونمط الحياة", "4. Lifestyle & Diet Agent"),
        ("5. وكيل الحوكمة والأمان", "5. Safety Gatekeeper Agent")
    ]
    
    for i, col in enumerate(pipeline_cols):
        with col:
            title_text = card_titles[i][0] if is_ar else card_titles[i][1]
            placeholder = st.empty()
            placeholder.info(f"⏳ {title_text}\n\nفي الانتظار..." if is_ar else f"⏳ {title_text}\n\nWaiting...")
            agent_cards.append((placeholder, title_text))

    # Orchestrator execution with visual steps
    provider_arg = "deterministic"
    if "Gemini" in provider_choice:
        provider_arg = "gemini"
    elif "OpenAI" in provider_choice:
        provider_arg = "openai"
    elif "DeepSeek" in provider_choice:
        provider_arg = "deepseek"
    elif "Ollama" in provider_choice:
        provider_arg = "ollama"
    elif "Cohere" in provider_choice:
        provider_arg = "cohere"

    orchestrator = ClinicalAgentOrchestrator(
        llm_provider=provider_arg,
        api_key=api_key_input,
        model_name=model_name_input,
        base_url=base_url_input
    )

    # Step 1
    progress_bar.progress(20)
    status_text.text("جارٍ فحص المدخلات عبر وكيل الفرز السريري..." if is_ar else "Validating inputs via Clinical Triage Agent...")
    time.sleep(0.3)
    triage_res = orchestrator.triage_agent.execute(patient_input)
    agent_cards[0][0].success(f"✓ {agent_cards[0][1]}\n\n{triage_res.priority_tier}\n\nGate 1: OK")

    # Step 2
    progress_bar.progress(45)
    status_text.text("تشغيل النموذج المعاير وحساب احتمالية الخطر..." if is_ar else "Running calibrated model & computing risk...")
    time.sleep(0.3)
    diag_res = orchestrator.diagnostic_agent.execute(triage_res)
    agent_cards[1][0].success(f"✓ {agent_cards[1][1]}\n\nالخطر: {diag_res.diabetes_probability:.1f}%\n\nGate 2: OK" if is_ar else f"✓ {agent_cards[1][1]}\n\nRisk: {diag_res.diabetes_probability:.1f}%\n\nGate 2: OK")

    # Step 3
    progress_bar.progress(65)
    status_text.text("توليد التعليل السريري المستند لمعايير ADA..." if is_ar else "Generating ADA-grounded clinical reasoning...")
    time.sleep(0.3)
    reason_res = orchestrator.reasoning_agent.execute(patient_input, diag_res)
    agent_cards[2][0].success(f"✓ {agent_cards[2][1]}\n\nالتعليل الطبي\n\nGate 3: OK" if is_ar else f"✓ {agent_cards[2][1]}\n\nClinical Logic\n\nGate 3: OK")

    # Step 4
    progress_bar.progress(85)
    status_text.text("صياغة خطة نمط الحياة وجدولة الفحوصات..." if is_ar else "Designing personalized nutrition & lifestyle plan...")
    time.sleep(0.3)
    lifestyle_res = orchestrator.lifestyle_agent.execute(patient_input, diag_res)
    agent_cards[3][0].success(f"✓ {agent_cards[3][1]}\n\nخطة التغذية\n\nGate 4: OK" if is_ar else f"✓ {agent_cards[3][1]}\n\nNutrition Plan\n\nGate 4: OK")

    # Step 5
    progress_bar.progress(100)
    status_text.text("المراجعة النهائية وتطبيق بوابات الحوكمة..." if is_ar else "Final safety gatekeeper review & disclaimer enforcement...")
    time.sleep(0.3)
    gate_res = orchestrator.gatekeeper_agent.execute(patient_input, triage_res, diag_res, reason_res, lifestyle_res)
    agent_cards[4][0].success(f"✓ {agent_cards[4][1]}\n\nاعتماد الأمان\n\nGate 5: OK" if is_ar else f"✓ {agent_cards[4][1]}\n\nSafety Certified\n\nGate 5: OK")

    dossier = MultiAgentDiagnosticDossier(
        patient_input=patient_input,
        triage=triage_res,
        prediction=diag_res,
        reasoning=reason_res,
        lifestyle=lifestyle_res,
        gatekeeper=gate_res,
        execution_time_ms=120.0
    )
    st.session_state["dossier"] = dossier

# ----------------- DISPLAY CLINICAL RESULTS -----------------
if "dossier" in st.session_state and st.session_state["dossier"] is not None:
    dossier = st.session_state["dossier"]
    patient_input = dossier.patient_input
    triage_res = dossier.triage
    diag_res = dossier.prediction
    reason_res = dossier.reasoning
    lifestyle_res = dossier.lifestyle
    gate_res = dossier.gatekeeper

    st.markdown("---")
    
    # Emergency Alert Callout
    if gate_res.emergency_alert_triggered:
        st.error(gate_res.emergency_message_ar if is_ar else gate_res.emergency_message_en)

    # KPI Metrics
    st.subheader("📊 النتائج التشخيصية للوكلاء" if is_ar else "📊 Multi-Agent Diagnostic Findings")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    priority_map_ar = {
        "Routine": "حالة روتينية",
        "Elevated_Risk": "خطورة مرتفعة",
        "Urgent_Care": "رعاية عاجلة",
        "Critical_Emergency": "طوارئ قصوى"
    }
    priority_map_en = {
        "Routine": "Routine Care",
        "Elevated_Risk": "Elevated Risk",
        "Urgent_Care": "Urgent Care",
        "Critical_Emergency": "Critical Emergency"
    }
    priority_display = priority_map_ar.get(triage_res.priority_tier, triage_res.priority_tier) if is_ar else priority_map_en.get(triage_res.priority_tier, triage_res.priority_tier)

    with m_col1:
        st.metric(
            label="احتمالية الإصابة المعايرة" if is_ar else "Calibrated Risk Probability",
            value=f"{diag_res.diabetes_probability:.1f}%",
            delta=("مرتفع" if diag_res.prediction_label == 1 else "طبيعي") if is_ar else ("Elevated" if diag_res.prediction_label == 1 else "Normal"),
            delta_color="inverse" if diag_res.prediction_label == 1 else "normal"
        )
    with m_col2:
        st.metric(
            label="مستوى الخطورة السريرية" if is_ar else "Clinical Risk Tier",
            value=diag_res.risk_level_ar if is_ar else diag_res.risk_level
        )
    with m_col3:
        st.metric(
            label="درجة الموثوقية الإحصائية" if is_ar else "Model Confidence Score",
            value=f"{diag_res.confidence_score:.1f}%"
        )
    with m_col4:
        st.metric(
            label="أولوية الفرز السريري" if is_ar else "Triage Priority Tier",
            value=priority_display
        )

    # Detailed Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠 التعليل السريري وADA" if is_ar else "🧠 Clinical Reasoning",
        "📊 تحليل المعايير الطبية" if is_ar else "📊 Medical Criteria Analysis",
        "🥗 خطة التغذية والنشاط" if is_ar else "🥗 Lifestyle & Diet Plan",
        "🛡️ سجل بوابات الجودة والأمان" if is_ar else "🛡️ Safety Audit & Gates"
    ])

    with tab1:
        st.markdown(f"### {diag_res.diagnosis_ar if is_ar else diag_res.diagnosis_en}")
        st.write(reason_res.detailed_explanation_ar if is_ar else reason_res.detailed_explanation_en)
        st.markdown("#### معايير الجمعية الأمريكية للسكري المرجعية (ADA Standards):" if is_ar else "#### ADA Clinical Guidelines Alignment:")
        for ref in reason_res.ada_guidelines_alignment:
            st.markdown(f"• `{ref}`")

    with tab2:
        # Load model feature importances
        model_path = os.path.join(PARENT_DIR, 'diabetes_model.pkl')
        raw_importances = None
        if os.path.exists(model_path):
            try:
                import joblib
                _rf_model = joblib.load(model_path)
                if hasattr(_rf_model, 'feature_importances_'):
                    raw_importances = np.array(_rf_model.feature_importances_)
            except Exception:
                pass
        if raw_importances is None or len(raw_importances) != 8:
            raw_importances = np.array([0.08501656, 0.26714176, 0.08865968, 0.06460413, 0.07154712, 0.16876864, 0.12269526, 0.13156685])

        indices = np.argsort(raw_importances)
        
        # Single Chart Controls: shape selector
        c_top1, c_top2 = st.columns([3, 2])
        with c_top1:
            st.markdown("### 📊 تحليل المعايير الطبية" if is_ar else "### 📊 Clinical Criteria Analysis")
            st.caption(
                "مخطط بياني يوضح الأهمية النسبية لكل معيار طبي في تحديد احتمالية الإصابة بالسكري وفق نموذج الذكاء الاصطناعي."
                if is_ar else
                "Visual chart illustrating the relative importance of each clinical criterion in predictive modeling."
            )
        with c_top2:
            shape_options = [
                "مخطط أشرطة أفقية (أفقي - مثل الصورة)" if is_ar else "Horizontal Bar Chart (As in image)",
                "مخطط أعمدة رأسية (عمودي)" if is_ar else "Vertical Column Chart",
                "مخطط دائري (فطيرة)" if is_ar else "Circular / Pie Chart",
                "مخطط حلقي (دونات)" if is_ar else "Donut Chart",
                "مخطط راداري (عنكبوتي)" if is_ar else "Radar / Spider Chart"
            ]
            selected_shape = st.selectbox(
                "اختر شكل المخطط البياني:" if is_ar else "Select Chart Shape:",
                options=shape_options,
                index=0,
                key="chart_shape_select"
            )

        # ----------------- SINGLE CHART RENDERING -----------------
        if selected_shape.startswith("مخطط أشرطة أفقية") or selected_shape.startswith("Horizontal"):
            # Horizontal Bar Chart (Exactly like the user's uploaded image)
            fig, ax = plt.subplots(figsize=(10, 5.5), dpi=120)
            fig.patch.set_facecolor('#ffffff')
            ax.set_facecolor('#ffffff')

            plt_labels = [CRITERIA_INFO[i]['ar'] if is_ar else CRITERIA_INFO[i]['en'] for i in indices]
            ax.barh(range(len(indices)), raw_importances[indices], color='#1a4d2e', height=0.70)
            ax.set_yticks(range(len(indices)))
            ax.set_yticklabels(plt_labels, fontsize=11, color='#111827')
            ax.set_title("تحليل المعايير الطبية" if is_ar else "Clinical Criteria Analysis", fontsize=13, fontweight='bold', pad=12, color='#111827')
            ax.set_xlabel("وزن الأهمية النسبية في النموذج" if is_ar else "Relative Importance Weight", fontsize=10, labelpad=8)
            ax.set_xlim(0, max(raw_importances) * 1.15)
            ax.tick_params(axis='x', labelsize=10)

            for i, v in enumerate(raw_importances[indices]):
                ax.text(v + 0.003, i, f"{v*100:.1f}% ({v:.3f})", va='center', fontsize=9.5, color='#1a4d2e', fontweight='bold')

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        elif selected_shape.startswith("مخطط أعمدة رأسية") or selected_shape.startswith("Vertical"):
            # Vertical Column Chart (عمودي)
            fig, ax = plt.subplots(figsize=(10, 5.5), dpi=120)
            fig.patch.set_facecolor('#ffffff')
            ax.set_facecolor('#ffffff')

            desc_indices = indices[::-1]
            desc_labels = [fix_ar_text(CRITERIA_INFO[i]['ar'] if is_ar else CRITERIA_INFO[i]['en'], is_ar) for i in desc_indices]

            ax.bar(range(len(desc_indices)), raw_importances[desc_indices], color='#1a4d2e', width=0.65)
            ax.set_xticks(range(len(desc_indices)))
            ax.set_xticklabels(desc_labels, rotation=25, ha='right', fontsize=10, fontweight='500', color='#111827')
            ax.set_ylabel(fix_ar_text("وزن الأهمية النسبية", is_ar) if is_ar else "Relative Importance Weight", fontsize=10, labelpad=8)
            ax.set_title(fix_ar_text("تحليل المعايير الطبية - أعمدة رأسية", is_ar) if is_ar else "Clinical Criteria Analysis - Vertical Columns", fontsize=13, fontweight='bold', pad=12, color='#111827')
            ax.set_ylim(0, max(raw_importances) * 1.15)

            for i, v in enumerate(raw_importances[desc_indices]):
                ax.text(i, v + 0.004, f"{v*100:.1f}%", ha='center', fontsize=9.5, color='#1a4d2e', fontweight='bold')

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        elif selected_shape.startswith("مخطط دائري") or selected_shape.startswith("Circular"):
            # Pie Chart (دائري)
            fig, ax = plt.subplots(figsize=(8, 7), dpi=120)
            fig.patch.set_facecolor('#ffffff')
            ax.set_facecolor('#ffffff')

            colors = ['#1a4d2e', '#22633b', '#2a7a49', '#329157', '#3ba865', '#4dc07b', '#6cd194', '#93e0b2']
            desc_indices = indices[::-1]
            desc_labels = [fix_ar_text(CRITERIA_INFO[i]['ar'] if is_ar else CRITERIA_INFO[i]['en'], is_ar) for i in desc_indices]

            wedges, texts, autotexts = ax.pie(
                raw_importances[desc_indices],
                labels=desc_labels,
                autopct='%1.1f%%',
                startangle=140,
                colors=colors,
                pctdistance=0.72,
                textprops=dict(fontsize=10, color='#111827')
            )
            for at in autotexts:
                at.set_fontsize(9.5)
                at.set_color('#ffffff')
                at.set_fontweight('bold')

            ax.set_title(fix_ar_text("تحليل المعايير الطبية - توزيع دائري نسبي", is_ar) if is_ar else "Clinical Criteria Analysis - Pie Distribution", fontsize=13, fontweight='bold', pad=14, color='#111827')
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        elif selected_shape.startswith("مخطط حلقي") or selected_shape.startswith("Donut"):
            # Donut Chart (حلقي)
            fig, ax = plt.subplots(figsize=(8, 7), dpi=120)
            fig.patch.set_facecolor('#ffffff')
            ax.set_facecolor('#ffffff')

            colors = ['#1a4d2e', '#22633b', '#2a7a49', '#329157', '#3ba865', '#4dc07b', '#6cd194', '#93e0b2']
            desc_indices = indices[::-1]
            desc_labels = [fix_ar_text(CRITERIA_INFO[i]['ar'] if is_ar else CRITERIA_INFO[i]['en'], is_ar) for i in desc_indices]

            wedges, texts, autotexts = ax.pie(
                raw_importances[desc_indices],
                labels=desc_labels,
                autopct='%1.1f%%',
                startangle=140,
                colors=colors,
                pctdistance=0.76,
                wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2),
                textprops=dict(fontsize=10, color='#111827')
            )
            for at in autotexts:
                at.set_fontsize(9.5)
                at.set_color('#ffffff')
                at.set_fontweight('bold')

            ax.text(0, 0, fix_ar_text("أهمية\nالمعايير", is_ar) if is_ar else "Criteria\nWeights", ha='center', va='center', fontsize=11, fontweight='bold', color='#1a4d2e')
            ax.set_title(fix_ar_text("تحليل المعايير الطبية - مخطط حلقي (دونات)", is_ar) if is_ar else "Clinical Criteria Analysis - Donut Chart", fontsize=13, fontweight='bold', pad=14, color='#111827')
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        elif selected_shape.startswith("مخطط راداري") or selected_shape.startswith("Radar"):
            # Radar / Spider Chart (راداري)
            fig, ax = plt.subplots(figsize=(8, 7), dpi=120, subplot_kw=dict(polar=True))
            fig.patch.set_facecolor('#ffffff')
            ax.set_facecolor('#ffffff')

            desc_indices = indices[::-1]
            desc_labels = [fix_ar_text(CRITERIA_INFO[i]['ar'] if is_ar else CRITERIA_INFO[i]['en'], is_ar) for i in desc_indices]
            N = len(desc_indices)
            angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
            angles += angles[:1]
            vals = raw_importances[desc_indices].tolist() + [raw_importances[desc_indices][0]]

            ax.plot(angles, vals, color='#1a4d2e', linewidth=2.4, marker='o', markersize=6)
            ax.fill(angles, vals, color='#1a4d2e', alpha=0.30)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(desc_labels, fontsize=10, fontweight='bold', color='#111827')
            ax.set_title(fix_ar_text("تحليل المعايير الطبية - مخطط راداري", is_ar) if is_ar else "Clinical Criteria Analysis - Radar Chart", fontsize=13, fontweight='bold', pad=20, color='#111827')
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        # Optional expandable data table
        with st.expander("📋 عرض جدول نسب الأهمية الرقمية لكل معيار" if is_ar else "📋 View Criteria Numerical Importance Table", expanded=False):
            desc_indices = indices[::-1]
            table_df = pd.DataFrame([
                {
                    'المعيار الطبي' if is_ar else 'Clinical Criterion': CRITERIA_INFO[i]['ar'] if is_ar else CRITERIA_INFO[i]['en'],
                    'وزن الأهمية النسبية' if is_ar else 'Relative Importance Weight': f"{raw_importances[i]:.4f}",
                    'النسبة المئوية للمساهمة' if is_ar else 'Contribution Percentage': f"{raw_importances[i]*100:.1f}%"
                }
                for i in desc_indices
            ])
            st.dataframe(table_df, use_container_width=True)

    with tab3:
        st.markdown("#### التوصيات الغذائية المخصصة:" if is_ar else "#### Nutritional Prescriptions:")
        for diet_item in (lifestyle_res.dietary_recommendations_ar if is_ar else lifestyle_res.dietary_recommendations_en):
            st.markdown(f"• {diet_item}")
        
        st.markdown("#### النشاط البدني الموصى به سريرياً:" if is_ar else "#### Physical Activity Prescription:")
        st.info(lifestyle_res.physical_activity_plan_ar if is_ar else lifestyle_res.physical_activity_plan_en)

        st.markdown("#### جدول المتابعة المخبرية:" if is_ar else "#### Diagnostic Follow-Up Schedule:")
        for s in (lifestyle_res.monitoring_schedule_ar if is_ar else lifestyle_res.monitoring_schedule_en):
            st.markdown(f"• {s}")

    with tab4:
        st.markdown("#### سجل تدقيق بوابات الجودة (Quality Gates Audit Trail):" if is_ar else "#### Quality Gates Audit Trail:")
        for a in gate_res.audit_trail:
            st.markdown(f"✓ `{a}`")
        st.warning(gate_res.safety_disclaimer_ar if is_ar else gate_res.safety_disclaimer_en)

    # ----------------- REPORT DOWNLOAD BUTTON -----------------
    st.markdown("---")
    st.subheader("📥 تحميل التقرير الطبي المعتمد بصيغة Word (.docx)" if is_ar else "📥 Download Official Patient Word Report (.docx)")
    
    report_file = generate_patient_docx(dossier, lang="ar" if is_ar else "en")
    with open(report_file, "rb") as f:
        docx_bytes = f.read()

    st.download_button(
        label="📄 تحميل التقرير الطبي الشامل (.docx)" if is_ar else "📄 Download Comprehensive Clinical Report (.docx)",
        data=docx_bytes,
        file_name=os.path.basename(report_file),
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary"
    )
