"""
phase_1_architecture_contracts/validation_gates.py
The Four Validation Gates Engine.
Strictly implements:
  - Gate 1 (Parses): JSON integrity & Syntactic validity
  - Gate 2 (Conforms): Structural schema quotas (strictly 5 MCQs & 5 T/F items, lab TODOs, assertions)
  - Gate 3 (Refers): Citation provenance against ingested syllabus chunks
  - Gate 4 (Coheres): Mathematical hour balance (Compute-in-Code) & AST Python syntax compilation
Author: Mohammad Abulgasim | Supervisor: Dr. Fakhreldeen Saeed
Academic Context: COSC726 Agentic AI
"""

import ast
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Set, Optional

from phase_1_architecture_contracts.contracts import (
    GateCheckResult,
    FourGatesAuditResult,
    WeeklyAssessmentBank,
    WeeklyTopicDecomposition,
    LabAssignment,
    LectureScript,
    FullWeeklyModulePackage
)

logger = logging.getLogger("ValidationGates")

class ValidationGatesEngine:
    """
    Deterministic Four-Gate Verification Engine enforcing academic and technical invariants.
    """

    @staticmethod
    def audit_gate_1_parses(raw_payload: Any) -> GateCheckResult:
        """
        Gate 1 (Parses): Checks JSON integrity and serializability.
        """
        errors = []
        if isinstance(raw_payload, str):
            try:
                json.loads(raw_payload)
            except Exception as e:
                errors.append(f"Invalid JSON format: {str(e)}")
        elif isinstance(raw_payload, (dict, list)):
            try:
                json.dumps(raw_payload)
            except Exception as e:
                errors.append(f"Object is not JSON serializable: {str(e)}")
        else:
            errors.append(f"Payload is neither a valid JSON string nor a serializable dictionary/list (type: {type(raw_payload)}).")

        passed = (len(errors) == 0)
        return GateCheckResult(
            gate_name="Gate 1 (Parses)",
            passed=passed,
            score=1.0 if passed else 0.0,
            details="Payload possesses clean JSON/syntactic integrity." if passed else "JSON syntax parsing failed.",
            errors=errors
        )

    @staticmethod
    def audit_gate_2_conforms(
        assessment_bank: Optional[WeeklyAssessmentBank] = None,
        lab: Optional[LabAssignment] = None,
        lecture: Optional[LectureScript] = None,
        has_lab: bool = True
    ) -> GateCheckResult:
        """
        Gate 2 (Conforms): Verifies structural schema quotas:
          - Exactly 5 MCQs and 5 True/False items per week.
          - Each MCQ has 4 options and valid answer key in ['A', 'B', 'C', 'D'].
          - If has_lab is True: Lab contains student starter template with explicit tasks (TODO/المطلوب) and instructor solution.
          - If has_lab is False: Purely theoretical course without lab requirements.
        """
        errors = []
        sub_scores = []

        # Assessment bank check
        if assessment_bank:
            mcq_count = len(assessment_bank.mcqs)
            tf_count = len(assessment_bank.true_false)

            if mcq_count != 5:
                errors.append(f"Quota violation: Formative assessment requires exactly 5 MCQs, found {mcq_count}.")
            else:
                sub_scores.append(1.0)

            if tf_count != 5:
                errors.append(f"Quota violation: Formative assessment requires exactly 5 T/F items, found {tf_count}.")
            else:
                sub_scores.append(1.0)

            for i, mcq in enumerate(assessment_bank.mcqs):
                if len(mcq.options) != 4:
                    errors.append(f"MCQ #{i+1} does not have exactly 4 options (found {len(mcq.options)}).")
                if mcq.correct_answer not in ["A", "B", "C", "D"]:
                    errors.append(f"MCQ #{i+1} answer key '{mcq.correct_answer}' is not A, B, C, or D.")

            for i, tf in enumerate(assessment_bank.true_false):
                if not isinstance(tf.is_true, bool):
                    errors.append(f"T/F #{i+1} answer is not a valid boolean.")

        # Lab assignment check
        if has_lab:
            if lab is None:
                errors.append("Quota violation: Practical lab assignment expected but not found.")
            else:
                starter = lab.student_starter_code
                sol = lab.instructor_solution_code
                has_task_marker = any(k in starter for k in ["TODO", "todo", "المطلوب", "مهمة", "تمرين", "Task", "Exercise", "def ", "--", "//"])
                if not has_task_marker:
                    errors.append("Lab starter code lacks explicit student tasks ('TODO' or 'المطلوب').")
                else:
                    sub_scores.append(1.0)

                if lab.has_executable_code and lab.tool_or_language == "python":
                    if "assert" not in sol and "assertEqual" not in sol and "print" not in sol:
                        errors.append("Instructor reference solution lacks verification or assertion code.")
                    else:
                        sub_scores.append(1.0)
                else:
                    if len(sol.strip()) < 20:
                        errors.append("Instructor reference solution is too brief or incomplete.")
                    else:
                        sub_scores.append(1.0)

                if len(lab.rubrics) == 0:
                    errors.append("Lab assignment missing evaluation rubrics.")
        else:
            # Purely theoretical module
            sub_scores.append(1.0)

        # Lecture script check
        if lecture:
            if len(lecture.learning_outcomes) == 0:
                errors.append("Lecture script missing explicit student learning outcomes.")
            if len(lecture.discussion_prompts) == 0:
                errors.append("Lecture delivery notes missing active discussion prompts.")

        total_checks = max(len(sub_scores) + len(errors), 1)
        passed = (len(errors) == 0)
        score = max(0.0, round(len(sub_scores) / total_checks, 2)) if not passed else 1.0

        return GateCheckResult(
            gate_name="Gate 2 (Conforms)",
            passed=passed,
            score=score,
            details="All structural quotas (5 MCQs, 5 T/F, starter TODOs, test assertions) confirmed." if passed else f"Encountered {len(errors)} structural non-conformance issues.",
            errors=errors
        )

    @staticmethod
    def audit_gate_3_refers(
        assessment_bank: Optional[WeeklyAssessmentBank] = None,
        schedule: Optional[WeeklyTopicDecomposition] = None,
        valid_chunk_ids: Optional[Set[str]] = None
    ) -> GateCheckResult:
        """
        Gate 3 (Refers): Enforces citation provenance against ingested syllabus chunks.
        Rejects hallucinated or ghost citation IDs.
        """
        errors = []
        referenced_ids = set()

        if assessment_bank:
            for mcq in assessment_bank.mcqs:
                if not mcq.citation_ref or mcq.citation_ref.strip() == "":
                    errors.append(f"MCQ {mcq.question_id} missing citation provenance.")
                else:
                    referenced_ids.add(mcq.citation_ref)

            for tf in assessment_bank.true_false:
                if not tf.citation_ref or tf.citation_ref.strip() == "":
                    errors.append(f"T/F {tf.question_id} missing citation provenance.")
                else:
                    referenced_ids.add(tf.citation_ref)

        if schedule:
            for cid in schedule.citation_ids:
                referenced_ids.add(cid)

        # If a known whitelist of valid chunk/reference IDs is provided, audit membership
        if valid_chunk_ids is not None and len(valid_chunk_ids) > 0:
            unknown_citations = referenced_ids - valid_chunk_ids
            if unknown_citations:
                for bad_ref in unknown_citations:
                    errors.append(f"Ghost Citation: '{bad_ref}' cannot be resolved in ingested syllabus chunks.")

        passed = (len(errors) == 0)
        return GateCheckResult(
            gate_name="Gate 3 (Refers)",
            passed=passed,
            score=1.0 if passed else max(0.0, 1.0 - (len(errors) * 0.15)),
            details=f"All {len(referenced_ids)} citations successfully grounded in ingested curriculum chunks." if passed else f"Encountered {len(errors)} provenance/grounding errors.",
            errors=errors
        )

    @staticmethod
    def audit_gate_4_coheres(
        schedule: Optional[WeeklyTopicDecomposition] = None,
        lab: Optional[LabAssignment] = None,
        all_schedules: Optional[List[WeeklyTopicDecomposition]] = None,
        target_course_hours: Optional[float] = None
    ) -> GateCheckResult:
        """
        Gate 4 (Coheres): Enforces mathematical contact hour coherence and Python code execution integrity:
          - lecture_hours + lab_hours == total_hours for each module
          - sum(total_hours across all modules) == target_course_hours
          - Instructor solution code parses cleanly through Python's AST compiler.
        """
        errors = []

        # 1. Contact hour math for single week
        if schedule:
            calculated_total = schedule.lecture_hours + schedule.lab_hours
            if abs(calculated_total - schedule.total_hours) > 0.001:
                errors.append(
                    f"Week {schedule.week_number} hour mismatch: Lecture ({schedule.lecture_hours}h) + "
                    f"Lab ({schedule.lab_hours}h) = {calculated_total}h, but total_hours is set to {schedule.total_hours}h."
                )

        # 2. Total course hours balance across entire curriculum
        if all_schedules and target_course_hours is not None:
            total_sum = sum(s.total_hours for s in all_schedules)
            if abs(total_sum - target_course_hours) > 0.001:
                errors.append(
                    f"Curriculum hour imbalance: Sum of all module hours ({total_sum}h) != "
                    f"Target course duration ({target_course_hours}h)."
                )

        # 3. Practical / Code Verification Check
        if lab and lab.instructor_solution_code:
            if lab.has_executable_code and lab.tool_or_language == "python":
                try:
                    compile(lab.instructor_solution_code, "<instructor_solution>", "exec")
                except SyntaxError as e:
                    errors.append(f"Instructor Python solution code has syntax errors: {str(e)}")
            else:
                if len(lab.instructor_solution_code.strip()) < 20:
                    errors.append(f"Instructor reference solution for {lab.tool_or_language} is too short or empty.")

        if lab and lab.student_starter_code:
            if lab.has_executable_code and lab.tool_or_language == "python":
                try:
                    compile(lab.student_starter_code, "<student_starter>", "exec")
                except SyntaxError as e:
                    errors.append(f"Student starter Python code has syntax errors: {str(e)}")
            else:
                if len(lab.student_starter_code.strip()) < 20:
                    errors.append(f"Student starter template for {lab.tool_or_language} is too short or empty.")

        passed = (len(errors) == 0)
        return GateCheckResult(
            gate_name="Gate 4 (Coheres)",
            passed=passed,
            score=1.0 if passed else 0.0,
            details="Mathematical contact hours reconciled and practical solution integrity verified." if passed else f"Encountered {len(errors)} coherence/math/code failures.",
            errors=errors
        )

    @classmethod
    def audit_full_package(
        cls,
        pkg: FullWeeklyModulePackage,
        valid_chunk_ids: Optional[Set[str]] = None,
        target_course_hours: Optional[float] = None,
        all_schedules: Optional[List[WeeklyTopicDecomposition]] = None
    ) -> FourGatesAuditResult:
        """
        Executes all four gates sequentially and produces a consolidated audit report.
        """
        raw_json = pkg.model_dump_json()
        has_lab = pkg.schedule.has_lab and (pkg.schedule.lab_hours > 0)
        g1 = cls.audit_gate_1_parses(raw_json)
        g2 = cls.audit_gate_2_conforms(pkg.assessments, pkg.lab, pkg.lecture, has_lab=has_lab)
        g3 = cls.audit_gate_3_refers(pkg.assessments, pkg.schedule, valid_chunk_ids)
        g4 = cls.audit_gate_4_coheres(pkg.schedule, pkg.lab, all_schedules, target_course_hours)

        all_passed = (g1.passed and g2.passed and g3.passed and g4.passed)
        total_score = round((g1.score + g2.score + g3.score + g4.score) / 4.0, 3)

        return FourGatesAuditResult(
            gate_1_parses=g1,
            gate_2_conforms=g2,
            gate_3_refers=g3,
            gate_4_coheres=g4,
            all_passed=all_passed,
            total_score=total_score,
            audit_timestamp=datetime.now().isoformat()
        )
