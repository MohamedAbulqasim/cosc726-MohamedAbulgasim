"""
Phase 2 Validation Runner:
Executes multi-agent orchestrator across representative patient clinical cohorts:
1. Normal Healthy Case (Low Risk)
2. Diabetic High Risk Case
3. Acute Emergency Case (Severe Hyperglycemia)
Evaluates Phase 2 Quality Gates (2.1, 2.2, 2.3).
"""

import os
import sys
import json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from schemas import PatientInput
from agent_orchestrator import ClinicalAgentOrchestrator
from quality_gates import Phase2QualityGates

def run_validation():
    print("=" * 70)
    print("  PHASE 2: MULTI-AGENT ARCHITECTURE & CLINICAL GATES VERIFICATION")
    print("=" * 70)

    orchestrator = ClinicalAgentOrchestrator()

    # Test Cohort 1: Normal Low Risk Patient
    print("\n[TEST CASE 1] Running Normal Low-Risk Patient...")
    patient_normal = PatientInput(
        patient_id="CASE-NORM-01",
        patient_name="حالة سليمة تجريبية / Healthy Profile",
        pregnancies=1,
        glucose=85.0,
        blood_pressure=70.0,
        skin_thickness=18.0,
        insulin=60.0,
        bmi=22.4,
        diabetes_pedigree=0.25,
        age=26
    )
    dossier_normal = orchestrator.run_pipeline(patient_normal)
    print(f" -> Predicted Label: {dossier_normal.prediction.prediction_label} | Prob: {dossier_normal.prediction.diabetes_probability}%")
    print(f" -> Priority Tier: {dossier_normal.triage.priority_tier} | Emergency Alert: {dossier_normal.gatekeeper.emergency_alert_triggered}")

    # Test Cohort 2: Diabetic High Risk Patient
    print("\n[TEST CASE 2] Running Diabetic High-Risk Patient...")
    patient_diabetic = PatientInput(
        patient_id="CASE-DIAB-02",
        patient_name="حالة إصابة سكري تجريبية / Diabetic Profile",
        pregnancies=4,
        glucose=178.0,
        blood_pressure=88.0,
        skin_thickness=32.0,
        insulin=180.0,
        bmi=34.8,
        diabetes_pedigree=0.85,
        age=52
    )
    dossier_diabetic = orchestrator.run_pipeline(patient_diabetic)
    print(f" -> Predicted Label: {dossier_diabetic.prediction.prediction_label} | Prob: {dossier_diabetic.prediction.diabetes_probability}%")
    print(f" -> Priority Tier: {dossier_diabetic.triage.priority_tier} | Risk Level: {dossier_diabetic.prediction.risk_level}")

    # Test Cohort 3: Critical Emergency Patient (Glucose = 320)
    print("\n[TEST CASE 3] Running Critical Emergency Patient (Glucose = 320 mg/dL)...")
    patient_emergency = PatientInput(
        patient_id="CASE-EMERG-03",
        patient_name="حالة طوارئ قصوى / Critical Emergency Profile",
        pregnancies=2,
        glucose=320.0,
        blood_pressure=95.0,
        skin_thickness=30.0,
        insulin=250.0,
        bmi=31.5,
        diabetes_pedigree=0.65,
        age=48
    )
    dossier_emergency = orchestrator.run_pipeline(patient_emergency)
    print(f" -> Priority Tier: {dossier_emergency.triage.priority_tier}")
    print(f" -> Emergency Alert: {dossier_emergency.gatekeeper.emergency_alert_triggered}")
    print(f" -> Message Preview: {dossier_emergency.gatekeeper.emergency_message_ar[:60]}...")

    # Quality Gates Verification
    print("\n" + "-" * 70)
    print("VERIFYING PHASE 2 QUALITY GATES")
    print("-" * 70)

    gate_2_1 = Phase2QualityGates.verify_gate_2_1_schema_contract(dossier_diabetic)
    print(f" -> {gate_2_1['gate_name']}: {'PASSED [OK]' if gate_2_1['passed'] else 'FAILED [X]'}")

    gate_2_2 = Phase2QualityGates.verify_gate_2_2_semantic_consistency(dossier_diabetic)
    print(f" -> {gate_2_2['gate_name']}: {'PASSED [OK]' if gate_2_2['passed'] else 'FAILED [X]'}")

    gate_2_3 = Phase2QualityGates.verify_gate_2_3_emergency_triage(dossier_emergency)
    print(f" -> {gate_2_3['gate_name']}: {'PASSED [OK]' if gate_2_3['passed'] else 'FAILED [X]'}")

    all_passed = gate_2_1['passed'] and gate_2_2['passed'] and gate_2_3['passed']

    # Save Log
    log_data = {
        'gate_2_1': gate_2_1,
        'gate_2_2': gate_2_2,
        'gate_2_3': gate_2_3,
        'cohort_execution_ms': {
            'normal': dossier_normal.execution_time_ms,
            'diabetic': dossier_diabetic.execution_time_ms,
            'emergency': dossier_emergency.execution_time_ms
        },
        'all_gates_passed': all_passed
    }
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phase2_gates_log.json")
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=4, ensure_ascii=False)

    print("\n" + "=" * 70)
    if all_passed:
        print(" [ALL GATES PASSED] Phase 2 Multi-Agent Architecture Verified!")
    else:
        print(" [GATE FAILURE] Phase 2 verification issues detected.")
    print("=" * 70)

    return all_passed

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
