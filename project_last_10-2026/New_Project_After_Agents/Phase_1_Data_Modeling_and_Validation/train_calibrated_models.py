"""
Phase 1: Multi-Model Training and Clinical Probability Calibration
Implements:
- Training of Random Forest, Gradient Boosting, and Logistic Regression
- Stratified 5-Fold Cross Validation
- Probability Calibration via CalibratedClassifierCV
- Comprehensive Clinical Metrics Evaluation (Accuracy, F1, ROC-AUC, Brier Score)
- Serialization of Calibrated Model and Metadata
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, brier_score_loss, confusion_matrix
)

from data_preprocessor import ClinicalDataPreprocessor, load_and_split_dataset

def train_and_evaluate_models(data_csv_path: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load and stratify split
    X_train, X_test, y_train, y_test, raw_df = load_and_split_dataset(data_csv_path)
    
    # 2. Preprocess data (Train only fitting)
    preprocessor = ClinicalDataPreprocessor()
    X_train_trans = preprocessor.fit_transform(X_train)
    X_test_trans = preprocessor.transform(X_test)

    # 3. Candidate Classifiers
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=150, max_depth=5, min_samples_split=3, random_state=10),
        'GradientBoosting': GradientBoostingClassifier(n_estimators=100, max_depth=3, learning_rate=0.06, random_state=10),
        'LogisticRegression': LogisticRegression(C=1.0, max_iter=500, random_state=10)
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=10)
    results = {}

    for name, model in models.items():
        cv_scores = cross_validate(
            model, X_train_trans, y_train, cv=cv,
            scoring=['accuracy', 'roc_auc', 'f1'],
            return_train_score=False
        )
        model.fit(X_train_trans, y_train)
        y_pred = model.predict(X_test_trans)
        y_prob = model.predict_proba(X_test_trans)[:, 1]

        results[name] = {
            'cv_mean_accuracy': float(np.mean(cv_scores['test_accuracy'])),
            'cv_mean_roc_auc': float(np.mean(cv_scores['test_roc_auc'])),
            'cv_mean_f1': float(np.mean(cv_scores['test_f1'])),
            'test_accuracy': float(accuracy_score(y_test, y_pred)),
            'test_precision': float(precision_score(y_test, y_pred, zero_division=0)),
            'test_recall': float(recall_score(y_test, y_pred)),
            'test_f1': float(f1_score(y_test, y_pred)),
            'test_roc_auc': float(roc_auc_score(y_test, y_prob)),
            'brier_score': float(brier_score_loss(y_test, y_prob))
        }

    # 4. Select Best Candidate (RandomForest) & Apply Probability Calibration
    base_best = RandomForestClassifier(n_estimators=180, max_depth=5, min_samples_split=3, random_state=10)
    calibrated_model = CalibratedClassifierCV(estimator=base_best, method='sigmoid', cv=5)
    calibrated_model.fit(X_train_trans, y_train)

    calib_pred = calibrated_model.predict(X_test_trans)
    calib_prob = calibrated_model.predict_proba(X_test_trans)[:, 1]

    cm = confusion_matrix(y_test, calib_pred).tolist()
    calibrated_metrics = {
        'model_name': 'Calibrated_Random_Forest_Ensemble',
        'accuracy': float(accuracy_score(y_test, calib_pred)),
        'precision': float(precision_score(y_test, calib_pred, zero_division=0)),
        'recall': float(recall_score(y_test, calib_pred)),
        'f1_score': float(f1_score(y_test, calib_pred)),
        'roc_auc': float(roc_auc_score(y_test, calib_prob)),
        'brier_score': float(brier_score_loss(y_test, calib_prob)),
        'confusion_matrix': cm,
        'model_comparisons': results
    }

    # 5. Extract Feature Importances from base trees in calibrated model
    base_best.fit(X_train_trans, y_train)
    feature_importances = dict(zip(preprocessor.all_feature_names, [float(x) for x in base_best.feature_importances_]))
    calibrated_metrics['feature_importances'] = feature_importances

    # 6. Save Artifacts
    model_path = os.path.join(output_dir, "calibrated_diabetes_model.pkl")
    prep_path = os.path.join(output_dir, "clinical_preprocessor.pkl")
    metrics_path = os.path.join(output_dir, "model_metrics.json")

    joblib.dump(calibrated_model, model_path)
    preprocessor.save(prep_path)
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(calibrated_metrics, f, indent=4, ensure_ascii=False)

    # Also save in root directory for easy access
    root_dir = os.path.abspath(os.path.join(output_dir, '..'))
    joblib.dump(calibrated_model, os.path.join(root_dir, "calibrated_diabetes_model.pkl"))
    preprocessor.save(os.path.join(root_dir, "clinical_preprocessor.pkl"))

    print(f"[SUCCESS] Calibrated Model Saved: {model_path}")
    print(f"[SUCCESS] Preprocessor Saved: {prep_path}")
    print(f"[SUCCESS] Metrics Saved: {metrics_path}")
    print(f"[METRICS] Accuracy: {calibrated_metrics['accuracy']:.4f} | ROC-AUC: {calibrated_metrics['roc_auc']:.4f} | Brier: {calibrated_metrics['brier_score']:.4f}")
    
    return calibrated_metrics

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "..", "diabetes_data.csv")
    train_and_evaluate_models(data_path, current_dir)
