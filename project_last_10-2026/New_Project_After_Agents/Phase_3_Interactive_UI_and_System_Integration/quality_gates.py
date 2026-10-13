"""
Phase 3 Quality Gates:
- Gate 3.1: UI & Patient Input Validation Gate
- Gate 3.2: Export Completeness & Document Integrity Gate
"""

import os
import docx
from schemas import PatientInput

class Phase3QualityGates:
    @staticmethod
    def verify_gate_3_1_input_validation(input_dict: dict) -> dict:
        """Verifies UI input payload maps to PatientInput schema without errors."""
        issues = []
        try:
            p_obj = PatientInput(**input_dict)
            if p_obj.glucose < 0 or p_obj.age <= 0:
                issues.append("Patient parameters cannot be non-positive.")
        except Exception as e:
            issues.append(f"Input validation failure: {str(e)}")

        passed = len(issues) == 0
        return {
            'gate_name': 'Gate 3.1: UI & Patient Input Validation Gate',
            'passed': passed,
            'issues': issues,
            'details': "Interactive input safely captured, validated, and sanitized." if passed else str(issues)
        }

    @staticmethod
    def verify_gate_3_2_export_completeness(docx_path: str) -> dict:
        """Verifies that generated Word report exists, is readable, and non-empty."""
        issues = []
        if not os.path.exists(docx_path):
            issues.append(f"Report file not found: {docx_path}")
        else:
            file_size = os.path.getsize(docx_path)
            if file_size < 10240:  # Must be at least 10KB
                issues.append(f"Report file size {file_size} bytes is suspiciously small.")
            try:
                test_doc = docx.Document(docx_path)
                if len(test_doc.paragraphs) < 5:
                    issues.append("Document paragraphs count is insufficient.")
            except Exception as e:
                issues.append(f"Failed to read document with python-docx: {str(e)}")

        passed = len(issues) == 0
        return {
            'gate_name': 'Gate 3.2: Export Completeness & Document Integrity Gate',
            'passed': passed,
            'issues': issues,
            'details': f"Document verified: valid .docx format ({os.path.getsize(docx_path) if os.path.exists(docx_path) else 0} bytes)." if passed else str(issues)
        }
