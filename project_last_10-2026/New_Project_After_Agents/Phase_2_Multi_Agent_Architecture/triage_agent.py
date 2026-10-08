"""
Agent 1: Clinical Triage and Biological Validation Agent
Responsibilities:
- Validate input physiological boundaries
- Flag and sanitize biological zeros (fatal/anomalous measurements)
- Categorize patient into clinical triage priority tiers:
  * Routine
  * Elevated_Risk
  * Urgent_Care
  * Critical_Emergency
- Gate 1 Enforcer: Biological Plausibility Gate
"""

from typing import Dict, Any, Tuple
from schemas import PatientInput, TriageResult

# Established physiological human limits
PHYSIOLOGICAL_LIMITS = {
    'glucose': {'min': 40.0, 'max': 500.0, 'default': 100.0, 'name_ar': 'الجلوكوز'},
    'blood_pressure': {'min': 40.0, 'max': 240.0, 'default': 75.0, 'name_ar': 'ضغط الدم'},
    'bmi': {'min': 12.0, 'max': 75.0, 'default': 25.0, 'name_ar': 'مؤشر كتلة الجسم'},
    'insulin': {'min': 0.0, 'max': 900.0, 'default': 79.0, 'name_ar': 'الإنسولين'},
    'skin_thickness': {'min': 0.0, 'max': 99.0, 'default': 20.0, 'name_ar': 'سمك الجلد'},
    'age': {'min': 1, 'max': 120, 'default': 40, 'name_ar': 'العمر'},
    'pregnancies': {'min': 0, 'max': 20, 'default': 0, 'name_ar': 'مرات الحمل'},
    'diabetes_pedigree': {'min': 0.05, 'max': 2.8, 'default': 0.45, 'name_ar': 'وراثة السكري'}
}

class ClinicalTriageAgent:
    def __init__(self):
        self.agent_name = "Clinical Triage & Biological Validation Agent"
        self.agent_name_ar = "وكيل الفرز والتحقق السريري"

    def execute(self, patient: PatientInput) -> TriageResult:
        flags = []
        zero_anomalies = []
        sanitized = {}

        p_dict = patient.model_dump()

        # 1. Check for Biological Zeros
        for param in ['glucose', 'blood_pressure', 'bmi']:
            val = p_dict.get(param, 0.0)
            if val <= 0.0:
                zero_anomalies.append(param)
                default_val = PHYSIOLOGICAL_LIMITS[param]['default']
                sanitized[param] = default_val
                flags.append(f"تنبيه فسيولوجي: تم رصد قيمة صفرية غير منطقية للمتغير '{PHYSIOLOGICAL_LIMITS[param]['name_ar']}'. تم الاستبدال بالمرجع السريري {default_val}.")
            else:
                sanitized[param] = val

        for param in ['pregnancies', 'skin_thickness', 'insulin', 'diabetes_pedigree', 'age']:
            sanitized[param] = p_dict.get(param)

        # Biological Guardrail: Males cannot have pregnancies
        if p_dict.get('gender', 'Female') == 'Male' and sanitized.get('pregnancies', 0) > 0:
            flags.append("تنبيه بيولوجي: تم ضبط عدد مرات الحمل تلقائياً إلى 0 لأن جنس المريض ذكر.")
            sanitized['pregnancies'] = 0

        # 2. Check Range Boundaries
        for param, limits in PHYSIOLOGICAL_LIMITS.items():
            curr_val = sanitized[param]
            if curr_val < limits['min']:
                flags.append(f"القيمة {curr_val} أقل من الحد الأدنى المقبول سريرياً لـ {limits['name_ar']} ({limits['min']}).")
                sanitized[param] = limits['min']
            elif curr_val > limits['max']:
                flags.append(f"القيمة {curr_val} تتجاوز الحد الأقصى المعتاد لـ {limits['name_ar']} ({limits['max']}).")
                sanitized[param] = limits['max']

        # 3. Clinical Urgency Stratification (Triage Priority Tier)
        glucose_val = sanitized['glucose']
        bp_val = sanitized['blood_pressure']

        if glucose_val >= 250.0:
            priority = "Critical_Emergency"
            flags.append("حالة طوارئ قصوى: ارتفاع حرج في سكر الدم يتطلب تحويلاً فورياً للمستشفى!")
        elif glucose_val >= 180.0 or bp_val >= 160.0:
            priority = "Urgent_Care"
            flags.append("رعاية عاجلة: مستويات سكر أو ضغط مرتفعة تستدعي تدخلاً طبياً خلال 24 ساعة.")
        elif glucose_val >= 126.0 or sanitized['bmi'] >= 35.0:
            priority = "Elevated_Risk"
            flags.append("خطورة مرتفعة: مؤشرات تتوافق مع داء السكري أو السمنة المفرطة.")
        else:
            priority = "Routine"

        msg = "تم فحص المدخلات الحيوية وإجازتها بنجاح عبر بوابة الفرز السريري." if not zero_anomalies else "تمت تنقية وتصحيح القيم الصفرية بنجاح."

        return TriageResult(
            is_valid=True,
            priority_tier=priority,
            zero_anomalies_detected=zero_anomalies,
            clinical_flags=flags,
            sanitized_features=sanitized,
            gate_status="PASSED",
            validation_message=msg
        )
