"""
Phase 4: Automated Clinical Quality Gates Verification Suite
Tests all gates across Phase 1, Phase 2, and Phase 3 without module name collision.
"""

import os
import sys
import importlib.util
import pytest
import pandas as pd
import joblib

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
P1_DIR = os.path.join(PARENT_DIR, 'Phase_1_Data_Modeling_and_Validation')
P2_DIR = os.path.join(PARENT_DIR, 'Phase_2_Multi_Agent_Architecture')
P3_DIR = os.path.join(PARENT_DIR, 'Phase_3_Interactive_UI_and_System_Integration')

if P2_DIR not in sys.path:
    sys.path.append(P2_DIR)
if P1_DIR not in sys.path:
    sys.path.append(P1_DIR)
if P3_DIR not in sys.path:
    sys.path.append(P3_DIR)

def load_module_from_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod

# Load phase-specific modules
qg1_mod = load_module_from_path("qg1", os.path.join(P1_DIR, "quality_gates.py"))
qg2_mod = load_module_from_path("qg2", os.path.join(P2_DIR, "quality_gates.py"))
qg3_mod = load_module_from_path("qg3", os.path.join(P3_DIR, "quality_gates.py"))

from agent_orchestrator import ClinicalAgentOrchestrator
from schemas import PatientInput

def test_gate_1_1_biological_integrity():
    preprocessor = joblib.load(os.path.join(P1_DIR, "clinical_preprocessor.pkl"))
    data_path = os.path.join(PARENT_DIR, "diabetes_data.csv")
    raw_df = pd.read_csv(data_path)
    res = qg1_mod.Phase1QualityGates.verify_gate_1_1_data_integrity(preprocessor, raw_df)
    assert res['passed'] is True
    assert res['zero_counts_detected']['Glucose'] > 0

def test_gate_1_2_model_performance():
    model = joblib.load(os.path.join(P1_DIR, "calibrated_diabetes_model.pkl"))
    preprocessor = joblib.load(os.path.join(P1_DIR, "clinical_preprocessor.pkl"))
    import json
    with open(os.path.join(P1_DIR, "model_metrics.json"), 'r') as f:
        metrics = json.load(f)
    sample_df = pd.read_csv(os.path.join(PARENT_DIR, "diabetes_data.csv")).head(5)
    res = qg1_mod.Phase1QualityGates.verify_gate_1_2_model_performance(metrics, model, preprocessor, sample_df)
    assert res['passed'] is True
    assert metrics['roc_auc'] >= 0.80
    assert metrics['accuracy'] >= 0.75

def test_gate_2_1_schema_contract():
    orchestrator = ClinicalAgentOrchestrator()
    patient = PatientInput(glucose=140.0, bmi=29.0, age=45)
    dossier = orchestrator.run_pipeline(patient)
    res = qg2_mod.Phase2QualityGates.verify_gate_2_1_schema_contract(dossier)
    assert res['passed'] is True

def test_gate_2_2_semantic_consistency():
    orchestrator = ClinicalAgentOrchestrator()
    patient = PatientInput(glucose=180.0, bmi=35.0, age=50)
    dossier = orchestrator.run_pipeline(patient)
    res = qg2_mod.Phase2QualityGates.verify_gate_2_2_semantic_consistency(dossier)
    assert res['passed'] is True

def test_gate_2_3_emergency_crisis_interception():
    orchestrator = ClinicalAgentOrchestrator()
    patient = PatientInput(glucose=310.0, bmi=32.0, age=40)
    dossier = orchestrator.run_pipeline(patient)
    res = qg2_mod.Phase2QualityGates.verify_gate_2_3_emergency_triage(dossier)
    assert res['passed'] is True
    assert dossier.gatekeeper.emergency_alert_triggered is True

def test_gate_3_2_export_report_completeness():
    from patient_report_generator import generate_patient_docx
    orchestrator = ClinicalAgentOrchestrator()
    patient = PatientInput(patient_id="TEST-G32", glucose=130.0)
    dossier = orchestrator.run_pipeline(patient)
    test_docx = os.path.join(CURRENT_DIR, "temp_gate_test.docx")
    generate_patient_docx(dossier, output_path=test_docx, lang="ar")
    res = qg3_mod.Phase3QualityGates.verify_gate_3_2_export_completeness(test_docx)
    assert res['passed'] is True
    if os.path.exists(test_docx):
        os.remove(test_docx)
