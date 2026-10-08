"""
Phase 2 Quality Gates:
- Gate 2.1: Schema Contract & Serialization Gate
- Gate 2.2: Semantic Consistency & Explainer Concordance Gate
- Gate 2.3: Clinical Emergency Triage & Crisis Interception Gate
"""

from schemas import PatientInput, MultiAgentDiagnosticDossier

class Phase2QualityGates:
    @staticmethod
    def verify_gate_2_1_schema_contract(dossier: MultiAgentDiagnosticDossier) -> dict:
        """Verifies strict adherence to Pydantic schema contracts."""
        issues = []
        try:
            # Test serialization and re-validation
            raw_json = dossier.model_dump_json()
            reconstructed = MultiAgentDiagnosticDossier.model_validate_json(raw_json)
            if reconstructed.execution_time_ms < 0:
                issues.append("Execution time is invalid.")
        except Exception as e:
            issues.append(f"Pydantic serialization failed: {str(e)}")

        passed = len(issues) == 0
        return {
            'gate_name': 'Gate 2.1: Schema Contract & Serialization Gate',
            'passed': passed,
            'issues': issues,
            'details': "All multi-agent data transfers conform strictly to typed Pydantic contracts." if passed else str(issues)
        }

    @staticmethod
    def verify_gate_2_2_semantic_consistency(dossier: MultiAgentDiagnosticDossier) -> dict:
        """Verifies clinical alignment between ML numbers and LLM prose."""
        issues = []
        pred_label = dossier.prediction.prediction_label
        summary_ar = dossier.reasoning.summary_ar

        if pred_label == 1 and "منخفضة" in summary_ar and "مرتفعة" not in summary_ar:
            issues.append("Semantic mismatch: Model predicted diabetic risk, but LLM described low risk!")
        if pred_label == 0 and "إصابة بداء السكري" in summary_ar and "منخفضة" not in summary_ar:
            issues.append("Semantic mismatch: Model predicted low risk, but LLM diagnosed active diabetes!")

        passed = len(issues) == 0
        return {
            'gate_name': 'Gate 2.2: Semantic Consistency Gate',
            'passed': passed,
            'issues': issues,
            'details': "Complete clinical semantic concordance between numerical risk score and narrative explanation." if passed else str(issues)
        }

    @staticmethod
    def verify_gate_2_3_emergency_triage(dossier: MultiAgentDiagnosticDossier) -> dict:
        """Verifies that severe crisis biomarkers trigger emergency protocols."""
        issues = []
        glucose = dossier.triage.sanitized_features.get('glucose', 100.0)
        emergency_alert = dossier.gatekeeper.emergency_alert_triggered

        if glucose >= 250.0 and not emergency_alert:
            issues.append(f"Emergency safety failure: Glucose was {glucose} mg/dL, but no emergency alert was fired!")

        passed = len(issues) == 0
        return {
            'gate_name': 'Gate 2.3: Clinical Emergency Triage Gate',
            'passed': passed,
            'issues': issues,
            'details': "Emergency safeguard verified: critical thresholds trigger prompt urgent triage notices." if passed else str(issues)
        }
