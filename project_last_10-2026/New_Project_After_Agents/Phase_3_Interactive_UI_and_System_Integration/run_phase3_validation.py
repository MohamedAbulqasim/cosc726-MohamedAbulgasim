"""
Phase 3 Validation Runner:
Tests UI integration components, patient report generators in Arabic and English,
and verifies Phase 3 Quality Gates (Gate 3.1 and Gate 3.2).
"""

import os
import sys
import json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
P2_DIR = os.path.join(PARENT_DIR, 'Phase_2_Multi_Agent_Architecture')

sys.path.append(P2_DIR)
sys.path.append(CURRENT_DIR)

from schemas import PatientInput
from agent_orchestrator import ClinicalAgentOrchestrator
from patient_report_generator import generate_patient_docx
from quality_gates import Phase3QualityGates

def run_validation():
    print("=" * 70)
    print("  PHASE 3: INTERACTIVE UI & SYSTEM INTEGRATION VERIFICATION")
    print("=" * 70)

    orchestrator = ClinicalAgentOrchestrator()

    # Step 1: Execute Pipeline on test patient
    print("\n[STEP 1] Executing Multi-Agent Pipeline for Test Patient...")
    patient = PatientInput(
        patient_id="VAL-P3-001",
        patient_name="المريض فحص المرحلة الثالثة / Phase 3 Test Patient",
        pregnancies=2,
        glucose=160.0,
        blood_pressure=84.0,
        skin_thickness=28.0,
        insulin=120.0,
        bmi=32.1,
        diabetes_pedigree=0.55,
        age=45
    )
    dossier = orchestrator.run_pipeline(patient)
    print(f" -> Pipeline Executed: Diagnosis={dossier.prediction.diagnosis_ar} | Prob={dossier.prediction.diabetes_probability}%")

    # Step 2: Test Arabic Report Generation
    print("\n[STEP 2] Testing Patient Arabic Word Report Generation (.docx)...")
    ar_report_path = os.path.join(CURRENT_DIR, "Test_Patient_Report_Arabic.docx")
    generate_patient_docx(dossier, output_path=ar_report_path, lang="ar")
    print(f" -> Generated Arabic Report: {ar_report_path}")

    # Step 3: Test English Report Generation
    print("\n[STEP 3] Testing Patient English Word Report Generation (.docx)...")
    en_report_path = os.path.join(CURRENT_DIR, "Test_Patient_Report_English.docx")
    generate_patient_docx(dossier, output_path=en_report_path, lang="en")
    print(f" -> Generated English Report: {en_report_path}")

    # Step 4: Verify Quality Gates
    print("\n" + "-" * 70)
    print("VERIFYING PHASE 3 QUALITY GATES")
    print("-" * 70)

    # Gate 3.1
    input_dict = patient.model_dump()
    gate_3_1 = Phase3QualityGates.verify_gate_3_1_input_validation(input_dict)
    print(f" -> {gate_3_1['gate_name']}: {'PASSED [OK]' if gate_3_1['passed'] else 'FAILED [X]'}")
    print(f"    Details: {gate_3_1['details']}")

    # Gate 3.2
    gate_3_2_ar = Phase3QualityGates.verify_gate_3_2_export_completeness(ar_report_path)
    gate_3_2_en = Phase3QualityGates.verify_gate_3_2_export_completeness(en_report_path)
    gate_3_2_passed = gate_3_2_ar['passed'] and gate_3_2_en['passed']
    print(f" -> {gate_3_2_ar['gate_name']}: {'PASSED [OK]' if gate_3_2_passed else 'FAILED [X]'}")
    print(f"    Details AR: {gate_3_2_ar['details']}")
    print(f"    Details EN: {gate_3_2_en['details']}")

    all_passed = gate_3_1['passed'] and gate_3_2_passed

    # Save Log
    log_data = {
        'gate_3_1': gate_3_1,
        'gate_3_2_arabic': gate_3_2_ar,
        'gate_3_2_english': gate_3_2_en,
        'all_gates_passed': all_passed
    }
    with open(os.path.join(CURRENT_DIR, "phase3_gates_log.json"), 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=4, ensure_ascii=False)

    print("\n" + "=" * 70)
    if all_passed:
        print(" [ALL GATES PASSED] Phase 3 UI & Reporting Verified!")
    else:
        print(" [GATE FAILURE] Phase 3 validation issues detected.")
    print("=" * 70)

    return all_passed

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
