"""
Phase 2: Pydantic Data Contracts and Schemas for Multi-Agent Collaboration
Defines immutable data transfer objects between agents with strict typing and validation.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator

class PatientInput(BaseModel):
    patient_id: str = Field(default="PAT-001", description="Unique Patient Identifier")
    patient_name: str = Field(default="مريض تجريبي / Sample Patient", description="Patient full name")
    gender: str = Field(default="Female", description="Patient biological sex: Male or Female")
    language: str = Field(default="ar", description="Preferred output language ('ar' or 'en')")
    pregnancies: int = Field(ge=0, le=20, default=0, description="Number of pregnancies")
    glucose: float = Field(ge=0.0, le=500.0, default=120.0, description="Plasma glucose concentration (mg/dL)")
    blood_pressure: float = Field(ge=0.0, le=260.0, default=75.0, description="Diastolic blood pressure (mm Hg)")
    skin_thickness: float = Field(ge=0.0, le=100.0, default=20.0, description="Triceps skin fold thickness (mm)")
    insulin: float = Field(ge=0.0, le=900.0, default=80.0, description="2-Hour serum insulin (mu U/ml)")
    bmi: float = Field(ge=0.0, le=80.0, default=27.5, description="Body Mass Index (weight in kg/(height in m)^2)")
    diabetes_pedigree: float = Field(ge=0.05, le=3.0, default=0.45, description="Diabetes pedigree function score")
    age: int = Field(ge=1, le=120, default=38, description="Patient age in years")

class TriageResult(BaseModel):
    is_valid: bool = True
    priority_tier: str = Field(default="Routine", description="Routine, Elevated_Risk, Urgent_Care, or Critical_Emergency")
    zero_anomalies_detected: List[str] = Field(default_factory=list)
    clinical_flags: List[str] = Field(default_factory=list)
    sanitized_features: Dict[str, float] = Field(default_factory=dict)
    gate_status: str = "PASSED"
    validation_message: str = "Patient biomarkers verified within biological limits."

class BiomarkerContribution(BaseModel):
    feature_name: str
    feature_name_ar: str
    patient_value: float
    ideal_range: str
    risk_impact: str  # 'Elevated', 'Normal', 'Protective'
    importance_weight: float

class PredictionResult(BaseModel):
    prediction_label: int = Field(description="0: Non-Diabetic, 1: Diabetic")
    diagnosis_ar: str
    diagnosis_en: str
    diabetes_probability: float = Field(ge=0.0, le=100.0, description="Calibrated risk probability percentage")
    confidence_score: float = Field(ge=0.0, le=100.0)
    risk_level: str  # 'Low Risk', 'Moderate Risk', 'High Risk', 'Severe Clinical Risk'
    risk_level_ar: str
    contributing_biomarkers: List[BiomarkerContribution] = Field(default_factory=list)
    gate_status: str = "PASSED"

class ClinicalReasoningResult(BaseModel):
    summary_ar: str
    summary_en: str
    detailed_explanation_ar: str
    detailed_explanation_en: str
    ada_guidelines_alignment: List[str] = Field(default_factory=list)
    key_drivers_identified: List[str] = Field(default_factory=list)
    gate_status: str = "PASSED"

class LifestylePlanResult(BaseModel):
    dietary_recommendations_ar: List[str] = Field(default_factory=list)
    dietary_recommendations_en: List[str] = Field(default_factory=list)
    physical_activity_plan_ar: str
    physical_activity_plan_en: str
    monitoring_schedule_ar: List[str] = Field(default_factory=list)
    monitoring_schedule_en: List[str] = Field(default_factory=list)
    contraindications_cleared: bool = True
    gate_status: str = "PASSED"

class GatekeeperAuditResult(BaseModel):
    is_approved: bool = True
    emergency_alert_triggered: bool = False
    emergency_message_ar: Optional[str] = None
    emergency_message_en: Optional[str] = None
    safety_disclaimer_ar: str
    safety_disclaimer_en: str
    audit_trail: List[str] = Field(default_factory=list)
    gate_status: str = "PASSED"

class MultiAgentDiagnosticDossier(BaseModel):
    patient_input: PatientInput
    triage: TriageResult
    prediction: PredictionResult
    reasoning: ClinicalReasoningResult
    lifestyle: LifestylePlanResult
    gatekeeper: GatekeeperAuditResult
    execution_time_ms: float = 0.0
    overall_status: str = "CERTIFIED"
