import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

# Paths
BASE_DIR = r"d:\111\diabetes_predict\New_Project_After_Agents"
DOCS_DIR = os.path.join(BASE_DIR, "Documentation")
UI_DIR = os.path.join(BASE_DIR, "ui_screenshots")
ASSETS_DIR = os.path.join(BASE_DIR, "presentation_assets")
os.makedirs(DOCS_DIR, exist_ok=True)

# Import common styling utilities
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
from common_docx_styles import (
    PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, TEXT_COLOR, MUTED_COLOR,
    make_document_rtl, set_paragraph_direction, format_run_rtl,
    add_header_banner, add_heading_ar, add_heading_en,
    add_paragraph_ar, add_paragraph_en, add_callout_box, add_styled_table,
    apply_table_borders, set_cell_background, set_cell_margins
)

def add_footer(doc, text, rtl=False):
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0]
        p.text = ""
        set_paragraph_direction(p, rtl=rtl)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if rtl else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(text)
        r.font.size = Pt(8.5)
        r.font.color.rgb = MUTED_COLOR
        if rtl:
            format_run_rtl(r, "Traditional Arabic")
        else:
            r.font.name = "Calibri"

def add_figure_with_caption(doc, img_path, caption, rtl=False, width_in=6.0):
    """Safely adds an image with centered alignment and a styled italic caption."""
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(width_in))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        set_paragraph_direction(p_cap, rtl=rtl)
        r_cap = p_cap.add_run(caption)
        r_cap.font.size = Pt(9.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = MUTED_COLOR
        if rtl:
            format_run_rtl(r_cap, "Traditional Arabic")
        else:
            r_cap.font.name = "Calibri"
    else:
        print(f"Warning: Image not found: {img_path}")

def build_arabic_guide():
    doc = docx.Document()
    make_document_rtl(doc)
    
    # 1. Header Banner
    add_header_banner(
        doc,
        title_ar="الدليل التشغيلي والشرح المصور الشامل لمنظومة الوكلاء الأذكياء",
        title_en="Comprehensive Illustrated Operational Guide: Multi-Agent Clinical AI System",
        doc_type="الدليل الفني المصور / Illustrated Technical Manual",
        rtl=True,
        include_academic_meta=True
    )
    add_footer(doc, "جامعة النيلين - كلية الدراسات العليا | الدليل المصور لمنظومة الوكلاء الأذكياء", rtl=True)

    # 2. Section 1: Introduction & Architectural Shift
    add_heading_ar(doc, "1. المقدمة والتحول المعماري (Architectural Paradigm Shift)", level=1)
    add_paragraph_ar(doc, 
        "يمثل هذا المشروع نقلة معمارية ونوعية متقدمة في أبحاث ماجستير الذكاء الاصطناعي بجامعة النيلين لمساق COSC726 Agentic AI، "
        "حيث طور الباحث المشروع الأساسي الذي أنجزه في الفصل الدراسي السابق لمقرر 'تعلم الآلة (Machine Learning)' "
        "(والمحفوظ كاملاً في المجلد المستقل Old_Project_Before_Agents وكان يعتمد على مصنف منفرد صامت Random Forest وواجهة مكتبية محدودة Tkinter)، "
        "ونقله إلى منظومة وكلاء ذكاء اصطناعي سريرية متكاملة (Agentic AI Multi-Agent System) تعمل كفريق استشاري طبي متعدد التخصصات (Multidisciplinary Team - MDT). "
        "يقوم النظام بمحاكاة التشاور السريري الدقيق بين خمسة وكلاء متخصصين، مع تقديم التعليل الطبي المعمق المستند لمعايير الجمعية الأمريكية للسكري (ADA)، "
        "واعتراض الحالات الحرجة لحظياً، وتوليد خطط غذائية وحركية مخصصة وتقارير طبية رسمية مشفرة."
    )

    add_callout_box(
        doc,
        "الهدف الأساسي للمنظومة: معالجة ظاهرة 'الصندوق الأسود' في نماذج تعلم الآلة التقليدية، وتحويل التنبؤات الرقمية الجافة إلى استشارات طبية معللة سريرياً "
        "تلتزم بأعلى معايير الأمان والحوكمة والامتثال الإحصائي الصارم وفق إرشادات الجمعية الأمريكية للسكري.",
        title="الرؤية والهدف السريري",
        box_type="gate",
        rtl=True
    )

    # Comparison Table
    add_heading_ar(doc, "مقارنة معمارية دقيقة بين مشروع تعلم الآلة السابق والمشروع الوكيلي المطور حالياً:", level=2)
    comp_headers = ["المعيار / الخاصية", "مشروع مقرر تعلم الآلة - الفصل السابق (Old_Project_Before_Agents)", "مشروع مقرر الذكاء الاصطناعي الوكيل - الفصل الحالي (New_Project_After_Agents)"]
    comp_rows = [
        ["معمارية النظام", "سكريبت أحادي تقليدي (Single Script)", "منظومة وكلاء متعددين تفاعلية (5 Autonomous MDT Agents)"],
        ["واجهة المستخدم", "واجهة سطح مكتب كلاسيكية (Tkinter GUI)", "لوحة تحكم ويب سحابية عصرية (Streamlit) ثنائية اللغة"],
        ["نموذج الذكاء الاصطناعي", "Random Forest خام غير معاير إحصائياً", "نموذج معاير سريرياً (Isotonic Calibrated) بدقة 83.1% وAUC 0.852"],
        ["التعليل السريري", "غير موجود إطلاقاً (أرقام صامتة)", "محرك هجين متعدد المزودين (Gemini, OpenAI, DeepSeek, Ollama + ADA)"],
        ["بوابات الجودة والأمان", "لا توجد بوابات فحص أو مطابقة", "9 بوابات جودة سريرية صارمة تغطي المراحل الأربع بنسبة 100%"],
        ["نظام الطوارئ", "غير موجود", "اعتراض آلي فوري للحالات الحرجة (السكر >= 250 mg/dL) بإنذار أحمر عاجل"],
        ["تحليل المعايير الطبية", "رسم بياني ثابت أولي", "تبويب تفاعلي ديناميكي يدعم 5 أشكال بيانية وجدول أوزان مفصل"],
        ["التغذية ونمط الحياة", "غير متوفرة", "وكيل مخصص للوصفات الغذائية والنشاط البدني وجدول المتابعة"],
        ["تصدير التقارير", "ملفات PDF قديمة غير ديناميكية", "توليد تقارير وورد (.docx) طبية رسمية مشفرة ومطهرة من البيانات الأكاديمية"],
        ["الهوية المؤسسية", "اسم ونصوص عادية", "هوية بصرية متكاملة لجامعة النيلين مع شعار رسمي ودعم RTL كامل"]
    ]
    add_styled_table(doc, comp_headers, comp_rows, rtl=True)

    # 3. Section 2: Multi-Agent Architecture
    add_heading_ar(doc, "2. معمارية منظومة الوكلاء الخمسة المتكاملة (Multi-Agent Architecture)", level=1)
    add_paragraph_ar(doc, 
        "تتكون المنظومة المطورة من خط أنابيب تسلسلي مشروط يضم خمسة وكلاء متخصصين، يعمل كل منهم تحت مظلة عقد بيانات صارم (Pydantic Schema) "
        "وبوابة جودة مستقلة تفحص مخرجاته قبل تمريرها للوكيل التالي:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(ASSETS_DIR, "fig_multi_agent_architecture.png"),
        "شكل (1): المعمارية الهندسية الشاملة لمنظومة الوكلاء الخمسة المتعددين (MDT Multi-Agent Architecture)",
        rtl=True,
        width_in=6.2
    )

    agent_headers = ["الوكيل الذكي", "الدور التخصصي والمسؤولية", "بوابة الجودة المرتبطة (Quality Gate)"]
    agent_rows = [
        ["1. وكيل الفرز السريري (Triage Agent)", "التحقق من المعقولية الفسيولوجية للمدخلات، وتصفية الأصفار البيولوجية، وتحديد أولوية الحالة السريرية.", "Gate 1: فحص الحدود الفسيولوجية المسموحة ومنع القيم الشاذة."],
        ["2. وكيل التنبؤ المعاير (Predictive Agent)", "تطبيق نموذج الغابات العشوائية المعاير بـ Isotonic Regression لحساب احتمالية الخطر السريري الدقيقة.", "Gate 2: التأكد من دقة النموذج (AUC >= 0.80) وزمن استجابة < 100ms."],
        ["3. وكيل التعليل الطبي (Reasoning Agent)", "توليد تعليل طبي سريري مستند لمعايير الجمعية الأمريكية للسكري (ADA) عبر نماذج LLM والمحرك الحتمي.", "Gate 3: الاتساق الدلالي الطبي بين النسبة المحسوبة والشرح السريري."],
        ["4. وكيل التغذية ونمط الحياة (Lifestyle Agent)", "صياغة التوصيات الغذائية الدقيقة، وخطة النشاط البدني الموصى بها، وجدول المتابعة المخبرية الدورية.", "Gate 4: مواءمة الوصفة الحركية والغذائية مع مؤشر كتلة الجسم والعمر."],
        ["5. وكيل الحوكمة والأمان (Gatekeeper Agent)", "المراجعة النهائية للملف السريري، اعتراض الطوارئ القصوى، وإرفاق إخلاء المسؤولية الطبية والقانونية.", "Gate 5: اعتراض سكر الدم >= 250 وتأمين الاعتماد النهائي."]
    ]
    add_styled_table(doc, agent_headers, agent_rows, rtl=True)

    # 4. Section 3: Main Overview & Header
    add_heading_ar(doc, "3. الشاشة الرئيسية والهوية المؤسسية للواجهة (Application Header & Identity)", level=1)
    add_paragraph_ar(doc, 
        "تم تصميم الواجهة التفاعلية (Streamlit Dashboard) بهوية بصرية سريرية فائقة الاحترافية تعكس الانتماء الأكاديمي لجامعة النيلين. "
        "تحتوي الترويسة الرئيسية على شعار الجامعة الرسمي، وبطاقة تعريفية بالمساق والباحث والمشرف، بالإضافة إلى محول اللغة الفوري (العربية مع دعم RTL الكامل / الإنجليزية LTR)."
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "01_main_overview.png"),
        "شكل (2): الشاشة الرئيسية للوحة التحكم التفاعلية والهوية المؤسسية لجامعة النيلين",
        rtl=True,
        width_in=6.2
    )

    add_paragraph_ar(doc, 
        "المكونات البصرية للشاشة الرئيسية:\n"
        "• الشعار المؤسسي الرسمي لجامعة النيلين وكلية الدراسات العليا أعلى اليمين.\n"
        "• صندوق بيانات الاعتماد الأكاديمي: الباحث: محمد ابوالقاسم | الإشراف: د. فخرالدين سعيد | المساق: COSC726 AGENTIC AI (2026 م).\n"
        "• ترويسة النظام السريرية باللون الأخضر الطبي الغامق (#1a4d2e) توضح معمارية الوكلاء وبوابات الأمان."
    )

    # 5. Section 4: Sidebar Controls
    add_heading_ar(doc, "4. الشريط الجانبي وضوابط التحكم الفسيولوجية (Sidebar & Clinical Controls)", level=1)
    add_paragraph_ar(doc, 
        "يمثل الشريط الجانبي (Sidebar) مركز التحكم الرئيسي في النظام، ويتيح للطبيب أو الباحث إدخال المتغيرات وضبط محركات الذكاء الاصطناعي بدقة فائقة:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "02_sidebar_parameters.png"),
        "شكل (3): الشريط الجانبي متضمناً محدد محرك الذكاء الاصطناعي، الحالات المسبقة، ومدخلات المؤشرات الحيوية",
        rtl=True,
        width_in=3.8
    )

    add_paragraph_ar(doc, 
        "الوظائف التفصيلية للشريط الجانبي:\n"
        "1. محدد لغة الواجهة (Interface Language): التحويل الفوري بين العربية (RTL) والإنجليزية (LTR).\n"
        "2. محرك الذكاء الاصطناعي (LLM Provider): يتيح الاختيار بين Google Gemini, OpenAI, DeepSeek, Ollama, أو المحرك السريري الحتمي المعتمد على ADA والذي يعمل محلياً دون إنترنت.\n"
        "3. الإعدادات السريرية الجاهزة (Clinical Presets): تمكين الطبيب من تحميل حالات تجريبية نموذجية بنقرة واحدة:\n"
        "   - سليم (Normal) | مرحلة ما قبل السكري (Pre-diabetic) | مصاب بالسكري (Diabetic) | حالة طوارئ حرجة (Critical Emergency).\n"
        "4. التحديد الحيوي للجنس (Biological Sex): ميزة حصرية تقوم بالتعطيل التلقائي لخانة الحمل وتثبيتها على الصفر عند اختيار 'ذكر' لمنع الأخطاء السريرية المنطقية.\n"
        "5. حقول إدخال المؤشرات الحيوية الثمانية: الجلوكوز (mg/dL)، ضغط الدم (mmHg)، سمك الجلد (mm)، الإنسولين (μU/mL)، مؤشر كتلة الجسم (kg/m²)، وراثة السكري، العمر، وعدد مرات الحمل."
    )

    # 6. Section 5: Pipeline Visualizer & KPI Cards
    add_heading_ar(doc, "5. مسار معالجة الوكلاء المتعددين وبطاقات النتائج السريرية", level=1)
    add_paragraph_ar(doc, 
        "بمجرد النقر على زر 'تشغيل منظومة الوكلاء للتشخيص السريري 🚀'، يبدأ خط الأنابيب في التنفيذ المباشر، "
        "حيث يعرض شريط المتابعة الحية تقدم كل وكيل من الوكلاء الخمسة واجتياز بوابات الجودة تباعاً، تعلوها بطاقات النتائج التشخيصية الأساسية الأربعة:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "03_agent_pipeline_execution.png"),
        "شكل (4): شريط تتبع مسار معالجة الوكلاء المتعددين وبطاقات المؤشرات والنتائج السريرية العلوية",
        rtl=True,
        width_in=6.2
    )

    add_paragraph_ar(doc, 
        "شرح بطاقات المؤشرات التشخيصية العلوية:\n"
        "• احتمالية الإصابة المعايرة (Calibrated Probability): النسبة المئوية الدقيقة للإصابة المحسوبة عبر نموذج Isotonic Regression (مثل 16.0% طبيعي أو 88.5% مرتفع).\n"
        "• مستوى الخطورة السريرية (Clinical Risk Tier): التصنيف السريري المعتمد (خطورة منخفضة ضمن الحدود الآمنة، خطورة متوسطة، أو خطورة مرتفعة).\n"
        "• درجة الموثوقية الإحصائية (Model Confidence Score): تعكس مدى ثقة النموذج في التنبؤ استناداً لتوزيع العينات في فضاء الميزات (مثل 68.0% أو 92.4%).\n"
        "• أولوية الفرز السريري (Triage Priority Tier): تصنيف سرعة التعامل الطبي مع الحالة (حالة روتينية، حالة تحتاج متابعة، أو إنذار طارئ عاجل)."
    )

    # 7. Section 6: Tab 1 - Clinical Reasoning
    add_heading_ar(doc, "6. التبويب الأول: 🧠 التعليل السريري ومعايير ADA المرجعية", level=1)
    add_paragraph_ar(doc, 
        "يمثل هذا التبويب جوهر التحول إلى الذكاء الاصطناعي القائم على الوكلاء (Agentic AI)؛ حيث لا يكتفي النظام بتقديم رقم تنبؤي جاف، "
        "بل يقوم وكيل التعليل الطبي بصياغة سرد سريري متكامل ومبرهن فسيولوجياً، مع ربطه الصريح بإرشادات الجمعية الأمريكية للسكري (ADA):"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "04_tab1_clinical_reasoning.png"),
        "شكل (5): التبويب الأول - التشخيص المعتمد، السرد السريري المفصل، ومواءمة معايير الجمعية الأمريكية للسكري",
        rtl=True,
        width_in=6.2
    )

    add_paragraph_ar(doc, 
        "محتويات ووظائف التبويب الأول:\n"
        "1. عنوان التشخيص السريري المعتمد: مصاغ بدقة سريرية (مثل: 'الحالة سليمة من السكري حالياً' أو 'ارتفاع احتمالية الإصابة بالسكري').\n"
        "2. التفسير السريري التحليلي: شرح طبي فسيولوجي يربط بين قياس الجلوكوز ومؤشر كتلة الجسم والعوامل الوراثية.\n"
        "3. مواءمة معايير ADA المرجعية: توثيق رسمي للمرجعيات الطبية المعتمدة في التقييم مثل:\n"
        "   - `ADA Standards of Medical Care in Diabetes (Classification and Diagnosis)`\n"
        "   - `Screening for Diabetes in Asymptomatic Adults (BMI >= 25 kg/m² + Risk Factors)`\n"
        "   - `Criteria for Clinical Diagnosis: Fasting Plasma Glucose & Impaired Glucose Tolerance`"
    )

    # 8. Section 7: Tab 2 - Medical Criteria Analysis & Charts
    add_heading_ar(doc, "7. التبويب الثاني: 📊 تحليل المعايير الطبية والمخططات التفاعلية", level=1)
    add_paragraph_ar(doc, 
        "صُمم هذا التبويب لفك شفرة 'الصندوق الأسود' لخوارزمية التعلم الآلي، وتوضيح الأهمية النسبية ومساهمة كل مؤشر حيوي في التنبؤ النهائي. "
        "يتميز التبويب بمرونة فائقة تتيح للطبيب التبديل اللحظي بين خمسة أشكال بيانية متنوعة عبر قائمة منسدلة ديناميكية:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "05_tab2_criteria_bar_chart.png"),
        "شكل (6): التبويب الثاني داخل التطبيق - مخطط الأشرطة الأفقية باللون الأخضر السريري الكلاسيكي (#1a4d2e)",
        rtl=True,
        width_in=6.2
    )

    add_paragraph_ar(doc, "الأشكال البيانية الخمسة المتاحة في الواجهة:")

    # Add shapes figures
    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "shape_bar_horizontal_ar.png"),
        "شكل (7-أ): مخطط الأشرطة الأفقية - يوضح مساهمة المتغيرات بدقة من الجلوكوز (26.7%) وحتى سمك الجلد (6.5%)",
        rtl=True,
        width_in=5.5
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "shape_column_vertical_ar.png"),
        "شكل (7-ب): مخطط الأعمدة الرأسية - يتيح مقارنة فورية لارتفاع أوزان المعايير الطبية",
        rtl=True,
        width_in=5.5
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "shape_pie_ar.png"),
        "شكل (7-ج): مخطط التوزيع الدائري (فطيرة) - يوضح الحصة النسبية المئوية لكل معيار في النموذج",
        rtl=True,
        width_in=4.8
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "shape_donut_ar.png"),
        "شكل (7-د): مخطط التوزيع الحلقي (دونات) - تصميم عصري يعرض كتل الأهمية النسبية",
        rtl=True,
        width_in=4.8
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "shape_radar_ar.png"),
        "شكل (7-هـ): المخطط الراداري العنكبوتي متعدد المحاور - يوضح بصمة الأهمية الشعاعية الشاملة",
        rtl=True,
        width_in=4.8
    )

    # Table of weights
    add_paragraph_ar(doc, "جدول أوزان الأهمية النسبية الرقمية ومساهمة المعايير (متاح داخل صندوق قابل للطي بالواجهة):")
    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "06_tab2_criteria_weights_table.png"),
        "شكل (8): جدول أوزان الأهمية النسبية والنسب المئوية داخل القائمة المنسدلة في التبويب الثاني",
        rtl=True,
        width_in=6.0
    )

    crit_headers = ["المعيار الطبي السريري", "اسم المتغير بالإنجليزية", "وزن الأهمية النسبية في النموذج", "النسبة المئوية للمساهمة"]
    crit_rows = [
        ["مستوى الجلوكوز", "Glucose", "0.2671", "26.7%"],
        ["مؤشر كتلة الجسم", "BMI", "0.1688", "16.9%"],
        ["العمر", "Age", "0.1316", "13.2%"],
        ["وراثة السكري", "DiabetesPedigreeFunction", "0.1227", "12.3%"],
        ["ضغط الدم", "BloodPressure", "0.0887", "8.9%"],
        ["عدد مرات الحمل", "Pregnancies", "0.0850", "8.5%"],
        ["الإنسولين", "Insulin", "0.0715", "7.2%"],
        ["سمك الجلد", "SkinThickness", "0.0646", "6.5%"]
    ]
    add_styled_table(doc, crit_headers, crit_rows, rtl=True)

    # 9. Section 8: Tab 3 - Lifestyle & Diet Plan
    add_heading_ar(doc, "8. التبويب الثالث: 🥗 خطة التغذية ونمط الحياة والنشاط البدني", level=1)
    add_paragraph_ar(doc, 
        "ينقل هذا التبويب النظام من دائرة التشخيص النظري إلى ميدان التدخل العلاجي والوقائي الفعلي. "
        "يقوم وكيل نمط الحياة بصياغة برنامج سريري متكامل موائم لوزن المريض ومستوى خطورته وعمره:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "07_tab3_lifestyle_diet_plan.png"),
        "شكل (9): التبويب الثالث - التوصيات الغذائية، الوصفة الحركية، وجدول المتابعة المخبرية الدورية",
        rtl=True,
        width_in=6.2
    )

    add_paragraph_ar(doc, 
        "الأركان الثلاثة لخطة التغذية ونمط الحياة:\n"
        "1. التوصيات الغذائية المخصصة: الالتزام بحمية البحر الأبيض المتوسط، ضبط النشويات المعقدة، الامتناع عن الزيوت المهدرجة، وشرب 2-3 لتر ماء يومياً.\n"
        "2. النشاط البدني الموصى به سريرياً (معروض داخل صندوق أزرق مميز): 150 دقيقة أسبوعياً من النشاط الهوائي متوسط الشدة (المشي السريع، الهرولة، السباحة) مقسمة على 5 أيام مع جلستي مقاومة.\n"
        "3. جدول المتابعة المخبرية: فحص سنوي روتيني لسكر الدم الصائم والسكر التراكمي (HbA1c)، ومتابعة دورية لمؤشر كتلة الجسم وضغط الدم كل 6 أشهر."
    )

    # 10. Section 9: Tab 4 - Safety Audit Trail & Quality Gates
    add_heading_ar(doc, "9. التبويب الرابع: 🛡️ سجل تدقيق بوابات الجودة والأمان السريري", level=1)
    add_paragraph_ar(doc, 
        "يجسد هذا التبويب ميثاق الحوكمة والأمان الطبي المعتمد في المشروع. يوثق وكيل الحوكمة اجتياز كافة بوابات التحقق الخمس بصيغة مسار تدقيق رسمي (Audit Trail)، "
        "متبوعاً بصندوق تحذيري لإخلاء المسؤولية القانونية والطبية:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "08_tab4_safety_audit_trail.png"),
        "شكل (10): التبويب الرابع - سجل تدقيق بوابات الجودة (Quality Gates) وصندوق إخلاء المسؤولية الطبية",
        rtl=True,
        width_in=6.2
    )

    add_paragraph_ar(doc, 
        "سجل تدقيق بوابات الجودة الخمس (Audit Trail):\n"
        "• Gate 1 (Biological Plausibility): VERIFIED - تم التحقق من المعقولية الفسيولوجية لكافة المدخلات.\n"
        "• Gate 2 (Statistical Calibration): VERIFIED - تم التحقق من المعايرة الإحصائية ودقة الاحتمالية.\n"
        "• Gate 3 (Semantic Alignment): VERIFIED - تم التحقق من الاتساق الدلالي الطبي بين الرقم والشرح.\n"
        "• Gate 4 (Lifestyle Feasibility): VERIFIED - تم التحقق من ملاءمة الوصفة الحركية والغذائية.\n"
        "• Gate 5 (Emergency Triage): STABLE CLINICAL PROFILE - تم التحقق من استقرار الحالة وعدم وجود حالة طوارئ."
    )

    add_callout_box(
        doc,
        "إخلاء مسؤولية سريري وقانوني: هذا التقرير صادر عن نظام ذكاء اصطناعي متعدد الوكلاء كأداة دعم قرار سريري استرشادية، "
        "ولا يعد بديلاً عن الفحص الطبي المباشر أو التحاليل المخبرية المعتمدة (مثل HbA1c أو اختبار تحمل الجلوكوز OGTT). "
        "يرجى استشارة الطبيب المختص قبل اتخاذ أي قرارات علاجية أو دوائية.",
        title="إخلاء المسؤولية السريرية والقانونية المعتمد",
        box_type="warning",
        rtl=True
    )

    # 11. Section 10: Critical Emergency Interception
    add_heading_ar(doc, "10. نظام اعتراض الطوارئ السريرية الحرجة (Emergency Interception)", level=1)
    add_paragraph_ar(doc, 
        "زُوّدت المنظومة بحاجز أمان استباقي شديد الحساسية يعمل فورياً عند اكتشاف قراءات حرجة مهددة للحياة (مثل مستوى الجلوكوز >= 250 mg/dL). "
        "يقوم وكيل الحوكمة باعتراض التدفق الاعتيادي فوراً، وإطلاق إنذار أحمر عاجل باللون القرمزي (#b91c1c) ينبه إلى خطر الحماض الكيتوني السكري (DKA) أو متلازمة فرط الأسمولية (HHS)، "
        "مع توجيه عاجل لاستدعاء الإسعاف الطبي الفوري:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "10_critical_emergency_alert.png"),
        "شكل (11): إنذار الطوارئ السريرية الفوري باللون الأحمر عند تجاوز الجلوكوز 250 mg/dL داخل التطبيق",
        rtl=True,
        width_in=6.2
    )

    add_callout_box(
        doc,
        "🚨 إنذار سريري حرج: مستوى الجلوكوز بلغ 260 mg/dL (أعلى من عتبة الخطر 250 mg/dL)! "
        "تم تفعيل بروتوكول الطوارئ السريرية فوراً. يرجى التوجه إلى أقرب مركز طوارئ أو استدعاء الإسعاف الطبي فوراً لمنع الغيبوبة الكيتونية.",
        title="بروتوكول الطوارئ السريرية القصوى",
        box_type="alert",
        rtl=True
    )

    # 12. Section 11: Patient Word Report Generation
    add_heading_ar(doc, "11. قسم تحميل التقرير الطبي المعتمد بصيغة Word (.docx) للمريض", level=1)
    add_paragraph_ar(doc, 
        "يتيح النظام للطبيب والمريض تنزيل وثيقة سريرية رسمية شاملة بصيغة Microsoft Word بنقرة زر واحدة. "
        "تتميز هذه الوثيقة بتطبيق أعلى معايير أمن وسرية البيانات الطبية (Medical Confidentiality)، "
        "حيث تم تطهيرها بالكامل من أي بيانات أكاديمية (مثل أسماء الباحث والمشرف أو اسم المساق والجامعة) "
        "لتصدر كتقرير طبي سريري رسمي صرف موجه للمريض ومؤسسات الرعاية الصحية:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "09_report_download_button.png"),
        "شكل (12): قسم تحميل التقرير الطبي المعتمد بصيغة Word (.docx) للمريض داخل الواجهة التفاعلية",
        rtl=True,
        width_in=6.2
    )

    add_paragraph_ar(doc, 
        "مواصفات التقرير الطبي الشامل المولّد:\n"
        "• ترميز مشفر للمريض (Patient ID: PAT-2026-09) لضمان الخصوصية.\n"
        "• جدول المؤشرات الحيوية المفصل مع المقارنة بالمعدلات المرجعية الطبيعية.\n"
        "• تقييم المخاطر المعاير إحصائياً والتشخيص السريري الرسمي المعتمد.\n"
        "• الخطة العلاجية والوقائية الكاملة (التغذية، الرياضة، والجدول المخبري).\n"
        "• توقيع الطبيب وخاتم الاعتماد وإخلاء المسؤولية الطبية الصارم."
    )

    # 13. Section 12: English Interface Features
    add_heading_ar(doc, "12. استعراض ميزات الواجهة باللغة الإنجليزية (English Interface)", level=1)
    add_paragraph_ar(doc, 
        "يدعم النظام التبديل السلس والكامل للواجهة باللغة الإنجليزية (English LTR Interface)، "
        "حيث يتم إعادة ضبط اتجاه الصفحة والجداول والعناصر البيانية تلقائياً مع ترجمة سريرية دقيقة لكافة المصطلحات والتبويبات:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "11_english_dashboard_overview.png"),
        "شكل (13): نظرة عامة على لوحة التحكم باللغة الإنجليزية (English LTR Dashboard Overview)",
        rtl=True,
        width_in=6.2
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "12_english_tab2_criteria_analysis.png"),
        "شكل (14): تبويب تحليل المعايير الطبية باللغة الإنجليزية (Clinical Criteria Analysis Tab in English)",
        rtl=True,
        width_in=6.2
    )

    # 14. Section 13: Operational Guide & Troubleshooting
    add_heading_ar(doc, "13. دليل التشغيل السريع واستكشاف الأخطاء (Quick Start & Commands)", level=1)
    add_paragraph_ar(doc, "يمكن تشغيل النظام المطور وإدارته بسهولة فائقة عبر الطرق التالية:")

    add_paragraph_ar(doc, 
        "أولاً: التشغيل المباشر بنقرة واحدة (One-Click Launch):\n"
        "• بالنقر المزدوج على ملف: `run_new_project.bat` في المجلد الرئيسي للمشروع.\n"
        "• أو بالنقر المزدوج على: `run_web_app.bat` داخل مجلد `New_Project_After_Agents/`.\n\n"
        "ثانياً: التشغيل عبر سطر الأوامر (Command Line Interface):\n"
        "```bash\n"
        "cd New_Project_After_Agents\n"
        "streamlit run app.py\n"
        "```\n\n"
        "ثالثاً: إدارة النظام الشاملة عبر المتحكم المركزي (CLI Master Controller):\n"
        "```bash\n"
        "python run_system.py --ui                     # تشغيل الواجهة التفاعلية\n"
        "python run_system.py --phase all              # اختبار واجتياز كافة المراحل بنسبة 100%\n"
        "python run_system.py --presentation           # إعادة توليد عروض البوربوينت (عربي وإنجليزي)\n"
        "python run_system.py --generate-all-reports   # إعادة توليد كافة تقارير الوورد الرسمية العشرة\n"
        "```"
    )

    # Save Document
    out_file = os.path.join(DOCS_DIR, "New_Project_User_Guide_Arabic.docx")
    doc.save(out_file)
    print(f"Arabic User Guide successfully created: {out_file} ({os.path.getsize(out_file)} bytes)")
    return out_file

def build_english_guide():
    doc = docx.Document()
    
    # 1. Header Banner
    add_header_banner(
        doc,
        title_ar="الدليل التشغيلي والشرح المصور الشامل لمنظومة الوكلاء الأذكياء",
        title_en="Comprehensive Illustrated Operational Guide: Multi-Agent Clinical AI System",
        doc_type="Illustrated Technical Manual / Master's Thesis Project",
        rtl=False,
        include_academic_meta=True
    )
    add_footer(doc, "Al-Neelain University - Faculty of Graduate Studies | Multi-Agent Clinical AI System Guide", rtl=False)

    # 2. Section 1: Introduction & Architectural Shift
    add_heading_en(doc, "1. Introduction & Architectural Paradigm Shift", level=1)
    add_paragraph_en(doc, 
        "This project represents a major architectural milestone in Master's-level artificial intelligence research at Al-Neelain University for Course : COSC726 AGENTIC AI. "
        "The application represents the direct evolution of the student's prerequisite coursework project for the 'Machine Learning' module completed in the preceding semester "
        "(preserved in directory 'Old_Project_Before_Agents', comprising a basic desktop Tkinter GUI and an uncalibrated Random Forest classifier) "
        "into an enterprise-grade Agentic AI Clinical Decision Support System (CDSS) acting as a virtual Multidisciplinary Medical Team (MDT). "
        "The system orchestrates five autonomous specialist agents, delivers explainable clinical reasoning aligned with American Diabetes Association (ADA) standards, "
        "executes real-time emergency triage interception, produces customized nutrition and physical activity prescriptions, and generates official encrypted patient reports."
    )

    add_callout_box(
        doc,
        "Core Clinical Objective: Solving the medical 'black box' problem by transforming silent numeric probability outputs from classical ML into fully transparent, "
        "evidence-based clinical reasoning governed by strict statistical calibration and safety guardrails.",
        title="Clinical Vision and Research Objective",
        box_type="gate",
        rtl=False
    )

    # Comparison Table
    add_heading_en(doc, "Comprehensive Comparison: Machine Learning Project vs. Agentic AI System", level=2)
    comp_headers = ["Dimension / Feature", "Previous Semester ML Project (Old_Project_Before_Agents)", "Current COSC726 Agentic AI System (New_Project_After_Agents)"]
    comp_rows = [
        ["System Architecture", "Monolithic single script (Desktop GUI)", "Multi-Agent Clinical Architecture (5 Autonomous MDT Agents)"],
        ["User Interface", "Basic Tkinter desktop GUI", "Modern interactive bilingual Streamlit dashboard (Arabic RTL & English LTR)"],
        ["AI / ML Modeling", "Raw uncalibrated Random Forest model", "Isotonic Calibrated model (83.1% Accuracy, 0.852 ROC-AUC)"],
        ["Clinical Explainability", "Completely absent (Silent classification)", "Multi-provider hybrid reasoning engine (Gemini, OpenAI, DeepSeek, Ollama, ADA)"],
        ["Quality & Safety Gates", "None", "9 automated clinical Quality Gates across 4 development phases (100% Passed)"],
        ["Emergency Interception", "None", "Instant automated triage interception (Glucose >= 250 mg/dL) with critical red alert"],
        ["Biomarker Criteria Analysis", "Static basic bar chart", "Dynamic tab supporting 5 interactive chart shapes and detailed weights table"],
        ["Lifestyle & Nutrition", "None", "Autonomous agent generating diet prescriptions, exercise plans, and lab schedules"],
        ["Report Generation", "Static legacy PDF manuals", "Automated official Word (.docx) patient report download sanitized of academic metadata"],
        ["Institutional Identity", "Basic unbranded labels", "Full Al-Neelain University visual branding, official emblem, and academic badges"]
    ]
    add_styled_table(doc, comp_headers, comp_rows, rtl=False)

    # 3. Section 2: Multi-Agent Architecture
    add_heading_en(doc, "2. Integrated Five-Agent Clinical Architecture (MDT System)", level=1)
    add_paragraph_en(doc, 
        "The system pipeline is orchestrated as a deterministic sequential state machine comprising five autonomous clinical agents. "
        "Each agent operates under strict Pydantic schemas and is audited by dedicated Quality Gates before state transitions occur:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(ASSETS_DIR, "fig_multi_agent_architecture.png"),
        "Figure (1): Comprehensive Engineering Architecture of the Five-Agent Clinical Multidisciplinary Team (MDT)",
        rtl=False,
        width_in=6.2
    )

    agent_headers = ["Intelligent Agent", "Specialist Clinical Role & Function", "Associated Quality Gate"]
    agent_rows = [
        ["1. Clinical Triage Agent", "Validates biological plausibility, handles physiological zeros, and categorizes baseline triage priority.", "Gate 1: Verifies biological boundary compliance and rejects aberrant inputs."],
        ["2. Calibrated Predictive Agent", "Applies Isotonic Calibrated Random Forest to calculate true clinical probability and confidence score.", "Gate 2: Enforces ROC-AUC >= 0.80 and inference latency < 100ms."],
        ["3. Clinical Reasoning Agent", "Generates evidence-based physiological rationale aligned with ADA standards via LLM / ADA Engine.", "Gate 3: Enforces semantic alignment between statistical risk and clinical rationale."],
        ["4. Lifestyle & Nutrition Agent", "Formulates tailored dietary guidelines, physical activity prescriptions, and follow-up lab schedules.", "Gate 4: Verifies lifestyle feasibility matching patient BMI, age, and risk level."],
        ["5. Safety Gatekeeper Agent", "Conducts final dossier audit, triggers emergency alerts when indicated, and attaches medical disclaimers.", "Gate 5: Intercepts blood glucose >= 250 mg/dL and seals diagnostic dossier."]
    ]
    add_styled_table(doc, agent_headers, agent_rows, rtl=False)

    # 4. Section 3: Main Overview & Header
    add_heading_en(doc, "3. Application Header & Institutional Visual Identity", level=1)
    add_paragraph_en(doc, 
        "The Streamlit dashboard is styled with high-fidelity clinical branding reflecting Al-Neelain University's academic prestige. "
        "The header contains the official university seal, academic course and researcher metadata, and a real-time language switcher (Arabic RTL / English LTR):"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "11_english_dashboard_overview.png"),
        "Figure (2): Main Interactive Dashboard Overview in English LTR with Al-Neelain University Branding",
        rtl=False,
        width_in=6.2
    )

    add_paragraph_en(doc, 
        "Key Visual Header Components:\n"
        "• Official Al-Neelain University and Faculty of Graduate Studies emblem placed in the sidebar.\n"
        "• Academic Accreditation Badge: Researcher: Mohamed Abuelgasim | Supervisor: Dr. Fakhreldeen Saeed | Course: COSC726 AGENTIC AI (2026).\n"
        "• System Banner in clinical forest green (#1a4d2e) outlining the five-agent architecture and quality gates."
    )

    # 5. Section 4: Sidebar Controls
    add_heading_en(doc, "4. Sidebar Controls & Physiological Input Parameters", level=1)
    add_paragraph_en(doc, 
        "The sidebar serves as the central command console, allowing clinicians and researchers to configure AI reasoning engines and input patient parameters:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "02_sidebar_parameters.png"),
        "Figure (3): Sidebar Controls showing LLM Engine selection, Clinical Presets, and Biomarker Inputs",
        rtl=False,
        width_in=3.8
    )

    add_paragraph_en(doc, 
        "Detailed Sidebar Capabilities:\n"
        "1. Interface Language Selector: Seamless live toggling between Arabic (RTL) and English (LTR).\n"
        "2. LLM Engine Selector: Multi-provider flexibility supporting Google Gemini, OpenAI, DeepSeek, Ollama, and the Offline ADA Deterministic Engine.\n"
        "3. Clinical Presets: Instant one-click loading of benchmark clinical profiles:\n"
        "   - Normal Profile | Pre-diabetic Profile | Diabetic Profile | Critical Emergency Profile.\n"
        "4. Biological Sex Selector: Intelligent safety feature that automatically locks and zeros the 'Pregnancies' input when 'Male' is selected to eliminate logical clinical errors.\n"
        "5. 8 Clinical Biomarkers: Glucose (mg/dL), Blood Pressure (mmHg), Skin Thickness (mm), Insulin (μU/mL), BMI (kg/m²), Diabetes Pedigree Function, Age (years), and Pregnancies."
    )

    # 6. Section 5: Pipeline Visualizer & KPI Cards
    add_heading_en(doc, "5. Multi-Agent Execution Pipeline & Top KPI Diagnosis Cards", level=1)
    add_paragraph_en(doc, 
        "Clicking 'Run Multi-Agent Clinical Diagnosis 🚀' triggers the sequential execution pipeline. "
        "The visualizer dynamically highlights each agent's execution phase and quality gate validation status, followed by the four primary diagnostic KPI cards:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "03_agent_pipeline_execution.png"),
        "Figure (4): Multi-Agent Live Execution Pipeline Visualizer and Top Clinical KPI Cards",
        rtl=False,
        width_in=6.2
    )

    add_paragraph_en(doc, 
        "Detailed Description of Diagnostic Metric Cards:\n"
        "• Calibrated Risk Probability: The mathematically calibrated probability of diabetes generated via Isotonic Regression (e.g. 16.0% Normal or 88.5% Elevated).\n"
        "• Clinical Risk Tier: Stratified clinical classification (Low Risk / Normal, Moderate Risk, or High Clinical Risk).\n"
        "• Model Confidence Score: Empirical statistical confidence reflecting sample density and feature space positioning (e.g. 68.0% or 92.4%).\n"
        "• Triage Priority Tier: Clinical urgency indicator (Routine Care, Outpatient Follow-up, or Immediate Triage Alert)."
    )

    # 7. Section 6: Tab 1 - Clinical Reasoning
    add_heading_en(doc, "6. Tab 1: 🧠 Clinical Reasoning & ADA Reference Guidelines", level=1)
    add_paragraph_en(doc, 
        "Tab 1 delivers explainable AI transparency. Instead of unverified classifications, the Clinical Reasoning Agent constructs a structured clinical rationale "
        "explicitly linked to American Diabetes Association (ADA) clinical practice standards:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "04_tab1_clinical_reasoning.png"),
        "Figure (5): Tab 1 - Official Diagnosis, In-depth Physiological Rationale, and ADA Clinical Guidelines Alignment",
        rtl=False,
        width_in=6.2
    )

    add_paragraph_en(doc, 
        "Key Elements in Tab 1:\n"
        "1. Verified Diagnosis Title: Expressed with clinical precision (e.g. 'Status: Non-Diabetic / Normal Glucose Profile' or 'Elevated Diabetes Risk Profile').\n"
        "2. Comprehensive Physiological Explanation: Correlates plasma glucose, BMI, and age with metabolic homeostasis.\n"
        "3. ADA Guidelines Alignment: Explicit citations to recognized standards:\n"
        "   - `ADA Standards of Medical Care in Diabetes (Classification and Diagnosis)`\n"
        "   - `Screening for Diabetes in Asymptomatic Adults (BMI >= 25 kg/m² + Risk Factors)`\n"
        "   - `Criteria for Clinical Diagnosis: Fasting Plasma Glucose & Impaired Glucose Tolerance`"
    )

    # 8. Section 7: Tab 2 - Medical Criteria Analysis & Charts
    add_heading_en(doc, "7. Tab 2: 📊 Medical Criteria Analysis & Dynamic Visualizations", level=1)
    add_paragraph_en(doc, 
        "Tab 2 demystifies model decision-making by revealing the relative mathematical weight and contribution of each biomarker. "
        "Clinicians can dynamically toggle between five distinct chart formats via an intuitive dropdown menu:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "12_english_tab2_criteria_analysis.png"),
        "Figure (6): Tab 2 in English - Horizontal Bar Chart in Clinical Forest Green (#1a4d2e)",
        rtl=False,
        width_in=6.2
    )

    add_paragraph_en(doc, "The Five Available Chart Formats:")

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "shape_bar_horizontal_en.png"),
        "Figure (7-A): Horizontal Bar Chart - High-clarity view sorting features from Glucose (26.7%) to SkinThickness (6.5%)",
        rtl=False,
        width_in=5.5
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "shape_column_vertical_en.png"),
        "Figure (7-B): Vertical Column Chart - Providing clean vertical comparison across criteria",
        rtl=False,
        width_in=5.5
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "shape_pie_en.png"),
        "Figure (7-C): Circular Pie Chart - Depicting proportional relative weights",
        rtl=False,
        width_in=4.8
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "shape_donut_en.png"),
        "Figure (7-D): Donut Chart - Modern presentation of proportional weights",
        rtl=False,
        width_in=4.8
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "shape_radar_en.png"),
        "Figure (7-E): Radar / Spider Chart - Radial biomarker importance profile",
        rtl=False,
        width_in=4.8
    )

    add_paragraph_en(doc, "Relative Mathematical Weights and Contribution Breakdown (Available in collapsible expander table):")
    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "06_tab2_criteria_weights_table.png"),
        "Figure (8): Collapsible Numerical Data Table displaying exact Relative Weights and Contribution Percentages",
        rtl=False,
        width_in=6.0
    )

    crit_headers = ["Clinical Criterion", "Feature Identifier", "Model Importance Weight", "Contribution Percentage"]
    crit_rows = [
        ["Glucose Level", "Glucose", "0.2671", "26.7%"],
        ["Body Mass Index", "BMI", "0.1688", "16.9%"],
        ["Age", "Age", "0.1316", "13.2%"],
        ["Diabetes Pedigree Function", "DiabetesPedigreeFunction", "0.1227", "12.3%"],
        ["Blood Pressure", "BloodPressure", "0.0887", "8.9%"],
        ["Number of Pregnancies", "Pregnancies", "0.0850", "8.5%"],
        ["Serum Insulin", "Insulin", "0.0715", "7.2%"],
        ["Triceps Skin Thickness", "SkinThickness", "0.0646", "6.5%"]
    ]
    add_styled_table(doc, crit_headers, crit_rows, rtl=False)

    # 9. Section 8: Tab 3 - Lifestyle & Diet Plan
    add_heading_en(doc, "8. Tab 3: 🥗 Lifestyle, Nutrition & Physical Activity Prescription", level=1)
    add_paragraph_en(doc, 
        "Tab 3 translates predictive analytics into actionable preventative and therapeutic lifestyle interventions. "
        "The Lifestyle & Nutrition Agent personalizes dietary guidelines, exercise regimens, and diagnostic monitoring based on patient status:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "07_tab3_lifestyle_diet_plan.png"),
        "Figure (9): Tab 3 - Personalized Dietary Guidelines, Exercise Prescription, and Lab Follow-up Schedule",
        rtl=False,
        width_in=6.2
    )

    add_paragraph_en(doc, 
        "Key Pillars of Lifestyle Prescription:\n"
        "1. Dietary Prescriptions: Emphasizing Mediterranean-style nutritional patterns, controlling refined carbohydrates, eliminating trans-fats, and maintaining 2-3 liters of daily hydration.\n"
        "2. Clinical Physical Activity Prescription (Rendered in prominent blue container): 150 minutes per week of moderate-intensity aerobic exercise (brisk walking, jogging, swimming) across 5 days, supplemented with 2 resistance training sessions.\n"
        "3. Diagnostic Follow-up Schedule: Annual fasting blood glucose and HbA1c testing, with bi-annual BMI and blood pressure assessments."
    )

    # 10. Section 9: Tab 4 - Safety Audit Trail & Quality Gates
    add_heading_en(doc, "9. Tab 4: 🛡️ Safety Audit Trail & Quality Gates Verification", level=1)
    add_paragraph_en(doc, 
        "Tab 4 demonstrates regulatory compliance and governance. The Safety Gatekeeper Agent logs the validation outcome of all five quality gates, "
        "concluding with an official clinical and legal disclaimer:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "08_tab4_safety_audit_trail.png"),
        "Figure (10): Tab 4 - Quality Gates Audit Trail and Official Clinical Safety Disclaimer",
        rtl=False,
        width_in=6.2
    )

    add_paragraph_en(doc, 
        "The 5 Audited Quality Gates:\n"
        "• Gate 1 (Biological Plausibility): VERIFIED - Validated baseline inputs against physiological thresholds.\n"
        "• Gate 2 (Statistical Calibration): VERIFIED - Confirmed calibration accuracy and confidence bounds.\n"
        "• Gate 3 (Semantic Alignment): VERIFIED - Ensured semantic congruence between metrics and narrative.\n"
        "• Gate 4 (Lifestyle Feasibility): VERIFIED - Verified safety and feasibility of lifestyle prescriptions.\n"
        "• Gate 5 (Emergency Triage): STABLE CLINICAL PROFILE - Verified absence of acute decompensation."
    )

    add_callout_box(
        doc,
        "Clinical & Legal Disclaimer: This report is generated by a multi-agent artificial intelligence decision support system for guidance purposes only. "
        "It does not replace direct physician examination or certified laboratory diagnostics (e.g. HbA1c, OGTT). "
        "Consult a qualified healthcare provider prior to making clinical or pharmacological decisions.",
        title="Official Clinical & Legal Safety Disclaimer",
        box_type="warning",
        rtl=False
    )

    # 11. Section 10: Critical Emergency Interception
    add_heading_en(doc, "10. Critical Emergency Triage Interception System", level=1)
    add_paragraph_en(doc, 
        "The system incorporates an automated emergency tripwire mechanism triggered whenever acute, life-threatening hyperglycemia is detected (Glucose >= 250 mg/dL). "
        "The Safety Gatekeeper intercepts normal workflow, activates a high-priority red alert (#b91c1c), flags risks of Diabetic Ketoacidosis (DKA) or Hyperosmolar Hyperglycemic State (HHS), "
        "and instructs immediate emergency medical services contact:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "10_critical_emergency_alert.png"),
        "Figure (11): Real-time Critical Emergency Alert Banner triggered upon Glucose >= 250 mg/dL",
        rtl=False,
        width_in=6.2
    )

    add_callout_box(
        doc,
        "🚨 CRITICAL CLINICAL EMERGENCY: Plasma Glucose has reached 260 mg/dL (exceeding emergency threshold of 250 mg/dL). "
        "Emergency clinical protocol is active. Seek immediate emergency medical care or call an ambulance to prevent acute metabolic decompensation.",
        title="Acute Emergency Clinical Protocol Active",
        box_type="alert",
        rtl=False
    )

    # 12. Section 11: Patient Word Report Generation
    add_heading_en(doc, "11. Official Patient Clinical Report Download (.docx)", level=1)
    add_paragraph_en(doc, 
        "The dashboard enables one-click generation of comprehensive, print-ready Microsoft Word (.docx) clinical reports. "
        "To uphold medical privacy and clinical standards, patient reports are strictly sanitized of all academic metadata "
        "(author, supervisor, and course data are excluded), ensuring a purely professional medical document:"
    )

    add_figure_with_caption(
        doc,
        os.path.join(UI_DIR, "09_report_download_button.png"),
        "Figure (12): Official Patient Word Report (.docx) One-Click Download Section",
        rtl=False,
        width_in=6.2
    )

    add_paragraph_en(doc, 
        "Specifications of Generated Clinical Reports:\n"
        "• Encrypted Patient Identifier (e.g. PAT-2026-09) protecting privacy.\n"
        "• Tabular physiological metrics compared against clinical reference standards.\n"
        "• Statistical risk evaluation and verified clinical diagnosis.\n"
        "• Complete lifestyle, nutrition, and exercise prescription.\n"
        "• Physician signature line, certification seal, and mandatory safety disclaimer."
    )

    # 13. Section 12: Operational Guide & Commands
    add_heading_en(doc, "12. Quick Start & CLI Master Controller", level=1)
    add_paragraph_en(doc, "The upgraded project can be launched and verified using the following execution modes:")

    add_paragraph_en(doc, 
        "1. One-Click Batch Launchers:\n"
        "• Double-click `run_new_project.bat` in the root workspace.\n"
        "• Or double-click `run_web_app.bat` inside `New_Project_After_Agents/`.\n\n"
        "2. Direct Command Line (Streamlit):\n"
        "```bash\n"
        "cd New_Project_After_Agents\n"
        "streamlit run app.py\n"
        "```\n\n"
        "3. Master Controller Command Suite:\n"
        "```bash\n"
        "python run_system.py --ui                     # Launches interactive web dashboard\n"
        "python run_system.py --phase all              # Executes full test suite across all 4 phases (100% Passed)\n"
        "python run_system.py --presentation           # Re-generates bilingual master PowerPoint slide decks\n"
        "python run_system.py --generate-all-reports   # Re-generates all 10 official Word documentation reports\n"
        "```"
    )

    # Save Document
    out_file = os.path.join(DOCS_DIR, "New_Project_User_Guide_English.docx")
    doc.save(out_file)
    print(f"English User Guide successfully created: {out_file} ({os.path.getsize(out_file)} bytes)")
    return out_file

if __name__ == "__main__":
    ar_path = build_arabic_guide()
    en_path = build_english_guide()
    print("Both Illustrated User Guides Generated Successfully!")
