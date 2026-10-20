"""
Phase 4: Clinical Edge-Cases and Stress Testing Suite
Evaluates robustness of the multi-agent pipeline against extreme physiological inputs.
"""

import os
import sys
import pytest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
P2_DIR = os.path.join(PARENT_DIR, 'Phase_2_Multi_Agent_Architecture')

sys.path.append(P2_DIR)
from schemas import PatientInput
from agent_orchestrator import ClinicalAgentOrchestrator

@pytest.fixture
def orchestrator():
    return ClinicalAgentOrchestrator()

def test_extreme_hyperglycemia_and_obesity(orchestrator):
    """Stress test: Extreme glucose and morbid obesity."""
    patient = PatientInput(
        patient_id="EDGE-01",
        glucose=480.0,
        bmi=65.0,
        age=78,
        blood_pressure=180.0
    )
    dossier = orchestrator.run_pipeline(patient)
    assert dossier.prediction.prediction_label == 1
    assert dossier.prediction.diabetes_probability >= 60.0
    assert dossier.gatekeeper.emergency_alert_triggered is True
    assert dossier.triage.priority_tier == "Critical_Emergency"

def test_biological_zero_biomarkers_sanitization(orchestrator):
    """Stress test: Zero values in physiological measurements must be sanitized."""
    patient = PatientInput(
        patient_id="EDGE-02",
        glucose=0.0,
        blood_pressure=0.0,
        bmi=0.0,
        age=35
    )
    dossier = orchestrator.run_pipeline(patient)
    assert len(dossier.triage.zero_anomalies_detected) >= 3
    # Check sanitized features were replaced with biological defaults
    assert dossier.triage.sanitized_features['glucose'] > 0.0
    assert dossier.triage.sanitized_features['blood_pressure'] > 0.0
    assert dossier.triage.sanitized_features['bmi'] > 0.0
    assert dossier.overall_status == "CERTIFIED"

def test_healthy_young_athlete_baseline(orchestrator):
    """Test: Young healthy baseline with low glycemic markers."""
    patient = PatientInput(
        patient_id="EDGE-03",
        pregnancies=0,
        glucose=72.0,
        blood_pressure=68.0,
        bmi=19.2,
        diabetes_pedigree=0.15,
        age=21
    )
    dossier = orchestrator.run_pipeline(patient)
    assert dossier.prediction.prediction_label == 0
    assert dossier.prediction.diabetes_probability <= 25.0
    assert dossier.triage.priority_tier == "Routine"
    assert dossier.gatekeeper.emergency_alert_triggered is False

def test_high_multiparity_patient(orchestrator):
    """Test: High number of pregnancies (15)."""
    patient = PatientInput(
        patient_id="EDGE-04",
        pregnancies=15,
        glucose=145.0,
        bmi=33.0,
        age=52
    )
    dossier = orchestrator.run_pipeline(patient)
    assert dossier.prediction.diabetes_probability > 50.0
    assert dossier.overall_status == "CERTIFIED"
