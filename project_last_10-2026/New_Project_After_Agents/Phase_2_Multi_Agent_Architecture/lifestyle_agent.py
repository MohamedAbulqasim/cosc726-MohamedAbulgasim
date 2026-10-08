"""
Agent 4: Personalized Lifestyle and Nutrition Agent
Responsibilities:
- Formulate culturally tailored, low-glycemic dietary protocols
- Prescribe BMI and age-appropriate physical activity regimens
- Schedule personalized diagnostic lab follow-ups (HbA1c, fasting glucose)
- Enforce Gate 4: Lifestyle Feasibility and Contraindication Gate
"""

from typing import Dict, Any
from schemas import PatientInput, PredictionResult, LifestylePlanResult
from llm_engine import ClinicalLLMEngine

class LifestyleNutritionAgent:
    def __init__(self, llm_engine: ClinicalLLMEngine = None):
        self.agent_name = "Personalized Lifestyle & Nutrition Agent"
        self.agent_name_ar = "وكيل نمط الحياة والتغذية السريرية"
        self.llm = llm_engine or ClinicalLLMEngine()

    def execute(self, patient: PatientInput, prediction: PredictionResult) -> LifestylePlanResult:
        p_dict = patient.model_dump()
        prob = prediction.diabetes_probability

        plan_data = self.llm.generate_lifestyle_plan(p_dict, prob)

        # Gate 4: Contraindication Verification
        # If severe obesity or elderly, ensure strenuous cardio is contraindicated
        age = patient.age
        bmi = patient.bmi
        activity_plan = plan_data.get('physical_activity_plan_ar', '')
        
        safe = True
        if (bmi >= 35.0 or age >= 65) and "عالية الشدة" in activity_plan and "تجنب" not in activity_plan:
            safe = False

        gate_status = "PASSED" if safe else "FAILED_CONTRAINDICATION"

        return LifestylePlanResult(
            dietary_recommendations_ar=plan_data.get('dietary_recommendations_ar', []),
            dietary_recommendations_en=plan_data.get('dietary_recommendations_en', []),
            physical_activity_plan_ar=plan_data.get('physical_activity_plan_ar', ''),
            physical_activity_plan_en=plan_data.get('physical_activity_plan_en', ''),
            monitoring_schedule_ar=plan_data.get('monitoring_schedule_ar', []),
            monitoring_schedule_en=plan_data.get('monitoring_schedule_en', []),
            contraindications_cleared=safe,
            gate_status=gate_status
        )
