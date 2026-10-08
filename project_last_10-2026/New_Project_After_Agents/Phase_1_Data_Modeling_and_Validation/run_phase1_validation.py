"""
Phase 1 Validation Runner:
Executes the data pipeline, model training, and evaluates all Phase 1 Quality Gates.
"""

import os
import sys
import json
import joblib
import pandas as pd

from data_preprocessor import ClinicalDataPreprocessor, load_and_split_dataset
from train_calibrated_models import train_and_evaluate_models
from quality_gates import Phase1QualityGates

def run_validation():
    print("=" * 70)
    print("  PHASE 1: DATA MODELING, CALIBRATION & QUALITY GATES VERIFICATION")
    print("=" * 70)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "..", "diabetes_data.csv")

    # Step 1: Train & Evaluate Models
    print("\n[STEP 1] Training Candidate Models and Applying Probability Calibration...")
    metrics = train_and_evaluate_models(data_path, current_dir)

    # Step 2: Load generated artifacts
    model_path = os.path.join(current_dir, "calibrated_diabetes_model.pkl")
    prep_path = os.path.join(current_dir, "clinical_preprocessor.pkl")
    model = joblib.load(model_path)
    preprocessor = joblib.load(prep_path)
    raw_df = pd.read_csv(data_path)

    # Step 3: Verify Gate 1.1
    print("\n[STEP 2] Verifying Gate 1.1: Data Integrity & Biological Plausibility Gate...")
    gate_1_1 = Phase1QualityGates.verify_gate_1_1_data_integrity(preprocessor, raw_df)
    status_1_1 = "PASSED [OK]" if gate_1_1['passed'] else "FAILED [X]"
    print(f" -> {gate_1_1['gate_name']}: {status_1_1}")
    print(f"    Details: {gate_1_1['details']}")
    print(f"    Zero Biomarkers Caught: {gate_1_1['zero_counts_detected']}")

    # Step 4: Verify Gate 1.2
    print("\n[STEP 3] Verifying Gate 1.2: Model Performance & Calibration Gate...")
    gate_1_2 = Phase1QualityGates.verify_gate_1_2_model_performance(metrics, model, preprocessor, raw_df)
    status_1_2 = "PASSED [OK]" if gate_1_2['passed'] else "FAILED [X]"
    print(f" -> {gate_1_2['gate_name']}: {status_1_2}")
    print(f"    Details: {gate_1_2['details']}")

    # Save Gate Verification Log
    gate_results = {
        'gate_1_1': gate_1_1,
        'gate_1_2': gate_1_2,
        'all_gates_passed': gate_1_1['passed'] and gate_1_2['passed']
    }
    with open(os.path.join(current_dir, "phase1_gates_log.json"), 'w', encoding='utf-8') as f:
        json.dump(gate_results, f, indent=4, ensure_ascii=False)

    print("\n" + "=" * 70)
    if gate_results['all_gates_passed']:
        print(" [ALL GATES PASSED] Phase 1 is validated and certified for production handoff!")
    else:
        print(" [GATE FAILURE] Some quality gates failed. Review logs.")
    print("=" * 70)

    return gate_results['all_gates_passed']

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
