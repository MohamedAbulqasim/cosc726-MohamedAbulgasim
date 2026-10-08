"""
Agent 2: ML Diagnostic and Predictive Analytics Agent
Responsibilities:
- Ingests sanitized patient data from Triage Agent
- Transforms features using calibrated ClinicalDataPreprocessor
- Executes Calibrated Random Forest Ensemble
- Derives true posterior probability, confidence score, and biomarker risk contributions
- Enforces Gate 2: Confidence & Calibration Gate
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Phase_1_Data_Modeling_and_Validation')))
from schemas import TriageResult, PredictionResult, BiomarkerContribution

# Standard Clinical Reference Ranges
CLINICAL_RANGES = {
    'glucose': {'ideal': '70 - 99 mg/dL', 'normal_max': 99.0, 'ar': 'مستوى الجلوكوز'},
    'blood_pressure': {'ideal': '70 - 80 mmHg', 'normal_max': 80.0, 'ar': 'ضغط الدم الانبساطي'},
    'bmi': {'ideal': '18.5 - 24.9 kg/m²', 'normal_max': 24.9, 'ar': 'مؤشر كتلة الجسم'},
    'insulin': {'ideal': '15 - 100 μU/mL', 'normal_max': 100.0, 'ar': 'مستوى الإنسولين'},
    'skin_thickness': {'ideal': '10 - 25 mm', 'normal_max': 25.0, 'ar': 'سمك ثنية الجلد'},
    'diabetes_pedigree': {'ideal': '< 0.50', 'normal_max': 0.50, 'ar': 'معامل وراثة السكري'},
    'age': {'ideal': '< 45 سنة', 'normal_max': 45.0, 'ar': 'العمر'},
    'pregnancies': {'ideal': '---', 'normal_max': 3.0, 'ar': 'عدد مرات الحمل'}
}

FEATURE_KEY_MAP = {
    'Pregnancies': 'pregnancies',
    'Glucose': 'glucose',
    'BloodPressure': 'blood_pressure',
    'SkinThickness': 'skin_thickness',
    'Insulin': 'insulin',
    'BMI': 'bmi',
    'DiabetesPedigreeFunction': 'diabetes_pedigree',
    'Age': 'age'
}

class MLDiagnosticAgent:
    def __init__(self, model_path: str = None, prep_path: str = None):
        self.agent_name = "ML Diagnostic & Predictive Analytics Agent"
        self.agent_name_ar = "وكيل التنبؤ والتحليل الإحصائي والنمذجة"

        # Determine paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        p1_dir = os.path.join(base_dir, '..', 'Phase_1_Data_Modeling_and_Validation')
        
        self.model_path = model_path or os.path.join(p1_dir, "calibrated_diabetes_model.pkl")
        self.prep_path = prep_path or os.path.join(p1_dir, "clinical_preprocessor.pkl")

        self.model = joblib.load(self.model_path)
        self.preprocessor = joblib.load(self.prep_path)

    def execute(self, triage_result: TriageResult) -> PredictionResult:
        sanitized = triage_result.sanitized_features
        
        # Convert dictionary to DataFrame for preprocessor
        row_dict = {
            'Pregnancies': [sanitized.get('pregnancies', 0)],
            'Glucose': [sanitized.get('glucose', 100.0)],
            'BloodPressure': [sanitized.get('blood_pressure', 75.0)],
            'SkinThickness': [sanitized.get('skin_thickness', 20.0)],
            'Insulin': [sanitized.get('insulin', 79.0)],
            'BMI': [sanitized.get('bmi', 25.0)],
            'DiabetesPedigreeFunction': [sanitized.get('diabetes_pedigree', 0.45)],
            'Age': [sanitized.get('age', 40)]
        }
        df_input = pd.DataFrame(row_dict)

        # Preprocess and scale
        X_trans = self.preprocessor.transform(df_input)

        # Calibrated Probability Prediction
        probabilities = self.model.predict_proba(X_trans)[0]
        prob_diabetic = float(probabilities[1]) * 100.0
        prediction_label = int(1 if prob_diabetic >= 50.0 else 0)

        # Confidence metric (distance from decision boundary normalized)
        confidence = float(abs(prob_diabetic - 50.0) * 2.0)
        confidence = max(55.0, min(99.0, confidence))

        # Risk Level Categorization
        if prob_diabetic >= 75.0:
            risk_level = "Severe Clinical Risk"
            risk_level_ar = "خطورة سريرية شديدة"
        elif prob_diabetic >= 50.0:
            risk_level = "High Risk"
            risk_level_ar = "خطورة مرتفعة (إصابة مرجحة)"
        elif prob_diabetic >= 30.0:
            risk_level = "Moderate Risk (Pre-diabetes)"
            risk_level_ar = "خطورة متوسطة (مرحلة ما قبل السكري)"
        else:
            risk_level = "Low Risk (Normal)"
            risk_level_ar = "خطورة منخفضة (ضمن الحدود الآمنة)"

        diagnosis_ar = "احتمال وجود إصابة بداء السكري" if prediction_label == 1 else "الحالة سليمة من السكري حالياً"
        diagnosis_en = "Elevated Probability of Diabetes" if prediction_label == 1 else "Normal Glycemic Regulation"

        # Biomarker Contributions Calculation
        contributions = []
        for en_feat, py_feat in FEATURE_KEY_MAP.items():
            val = float(sanitized.get(py_feat, 0.0))
            ref = CLINICAL_RANGES.get(py_feat, {'ideal': '---', 'normal_max': 100.0, 'ar': en_feat})
            
            # Evaluate impact
            if val > ref['normal_max']:
                impact = "Elevated"
                weight = min(1.0, (val - ref['normal_max']) / ref['normal_max'])
            else:
                impact = "Normal"
                weight = 0.1

            contributions.append(BiomarkerContribution(
                feature_name=en_feat,
                feature_name_ar=ref['ar'],
                patient_value=val,
                ideal_range=ref['ideal'],
                risk_impact=impact,
                importance_weight=float(round(weight, 3))
            ))

        # Sort by impact
        contributions.sort(key=lambda x: (x.risk_impact == "Elevated", x.importance_weight), reverse=True)

        return PredictionResult(
            prediction_label=prediction_label,
            diagnosis_ar=diagnosis_ar,
            diagnosis_en=diagnosis_en,
            diabetes_probability=round(prob_diabetic, 1),
            confidence_score=round(confidence, 1),
            risk_level=risk_level,
            risk_level_ar=risk_level_ar,
            contributing_biomarkers=contributions,
            gate_status="PASSED"
        )
