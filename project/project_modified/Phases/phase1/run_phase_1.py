"""
phase_1_architecture_contracts/run_phase_1.py
Standalone test and verification runner for Phase 1: Architecture & Contracts.
Tests:
  1. ModelClient multi-model seam
  2. Pydantic contracts creation and JSON serialization
  3. Gate 1 (Parses), Gate 2 (Conforms), Gate 3 (Refers), Gate 4 (Coheres)
  4. Positive compliance testing (All 4 gates pass)
  5. Negative fault injection testing (Fault detection across all 4 gates)
"""

import sys
import os
import json

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phase_1_architecture_contracts.model_client import ModelClient, GenerationConfig
from phase_1_architecture_contracts.contracts import (
    CurriculumMetadata,
    WeeklyTopicDecomposition,
    LectureScript,
    LabAssignment,
    MCQQuestion,
    TrueFalseQuestion,
    WeeklyAssessmentBank,
    FullWeeklyModulePackage
)
from phase_1_architecture_contracts.validation_gates import ValidationGatesEngine

def run_tests():
    print("=" * 75)
    print("RUNNING PHASE 1 VERIFICATION: ARCHITECTURE, CONTRACTS & VALIDATION GATES")
    print("=" * 75)

    # 1. Test ModelClient Seam
    print("\n[TEST 1] Testing ModelClient Seam...")
    client = ModelClient(provider="mock")
    resp = client.generate("Generate assessment items for Week 1")
    assert resp.parsed_json is not None, "ModelClient failed to parse JSON in mock mode."
    assert "mcqs" in resp.parsed_json, "ModelClient mock response missing 'mcqs' key."
    print(f"  -> ModelClient Seam Verified: Provider={resp.provider}, Model={resp.model_name}")

    # 2. Test Pydantic Contracts
    print("\n[TEST 2] Testing Pydantic V2 Data Contracts...")
    meta = CurriculumMetadata(
        course_title="Autonomous Agentic Systems",
        target_weeks=4,
        target_total_hours=32.0,
        target_lecture_hours=16.0,
        target_lab_hours=16.0
    )
    assert meta.target_weeks == 4
    assert meta.target_total_hours == 32.0
    print("  -> CurriculumMetadata Contract Verified.")

    # 3. Construct Compliant Weekly Module Package
    print("\n[TEST 3] Testing Positive Conformance (All 4 Gates Expected to Pass)...")
    valid_citations = {"REF-W1-01", "REF-W1-02", "SYLLABUS-PARENT-1"}
    
    schedule = WeeklyTopicDecomposition(
        week_number=1,
        title="Multi-Agent Architectures & Tool Calling",
        lecture_hours=4.0,
        lab_hours=4.0,
        total_hours=8.0,
        lecture_topics=["Agentic Topologies", "Model-Harness-Agent Separation"],
        lab_tasks=["Building Deterministic Pydantic Tool Callers"],
        citation_ids=["REF-W1-01"]
    )

    lecture = LectureScript(
        week_number=1,
        delivery_script="Welcome to Week 1. In this module, we dissect agentic architectures and stateful harnesses.",
        discussion_prompts=["How does external memory mitigate token context limits?"],
        trainee_reading_summary="Students study the division of labor between next-token generators and deterministic code harnesses.",
        learning_outcomes=["Understand multi-agent message routing and tool schema contracts."]
    )

    lab = LabAssignment(
        week_number=1,
        assignment_title="Deterministic Tool Calling with Pydantic",
        student_starter_code="def run_tool():\n    # TODO: Implement tool logic\n    pass\n",
        student_debug_challenges=["Fix missing type hints in tool payload."],
        instructor_solution_code="def run_tool():\n    return 'success'\n\nassert run_tool() == 'success'\n",
        rubrics=["40% Schema validation", "60% Unit test pass"]
    )

    mcqs = [
        MCQQuestion(
            question_id=f"W1-MCQ-{i}",
            week_number=1,
            stem=f"What is the role of the Python harness in an agentic framework? (Item {i})",
            options=["A) Token prediction", "B) State management & gate enforcement", "C) Loss backpropagation", "D) Cloud hosting only"],
            correct_answer="B",
            rationale="The harness manages deterministic control flow while the LLM generates tokens.",
            citation_ref="REF-W1-01"
        ) for i in range(1, 6)
    ]

    tfs = [
        TrueFalseQuestion(
            question_id=f"W1-TF-{i}",
            week_number=1,
            statement=f"LLMs should compute contact hours mathematically rather than using Python. (Item {i})",
            is_true=False,
            rationale="Compute-in-code eliminates arithmetic hallucinations.",
            citation_ref="REF-W1-02"
        ) for i in range(1, 6)
    ]

    assessments = WeeklyAssessmentBank(week_number=1, mcqs=mcqs, true_false=tfs)

    package = FullWeeklyModulePackage(
        week_number=1,
        schedule=schedule,
        lecture=lecture,
        lab=lab,
        assessments=assessments
    )

    audit_result = ValidationGatesEngine.audit_full_package(
        pkg=package,
        valid_chunk_ids=valid_citations,
        target_course_hours=8.0,
        all_schedules=[schedule]
    )

    print(f"  Gate 1 (Parses):   Passed={audit_result.gate_1_parses.passed}, Score={audit_result.gate_1_parses.score}")
    print(f"  Gate 2 (Conforms): Passed={audit_result.gate_2_conforms.passed}, Score={audit_result.gate_2_conforms.score}")
    print(f"  Gate 3 (Refers):   Passed={audit_result.gate_3_refers.passed}, Score={audit_result.gate_3_refers.score}")
    print(f"  Gate 4 (Coheres):  Passed={audit_result.gate_4_coheres.passed}, Score={audit_result.gate_4_coheres.score}")
    print(f"  Overall Conformance: Passed={audit_result.all_passed}, Composite Score={audit_result.total_score}")
    
    assert audit_result.all_passed, f"Expected all 4 gates to pass, but failed: {audit_result.model_dump_json(indent=2)}"
    print("  -> Positive Conformance Check PASSED (100% Score)!")

    # 4. Negative Testing: Inject Faults to Ensure Gates Reject Defects
    print("\n[TEST 4] Testing Fault Injection (Verifying Defect Detection)...")
    
    # Fault 1: Gate 1 Fault (Invalid JSON format)
    g1_fault = ValidationGatesEngine.audit_gate_1_parses("{ broken json: missing quotes }")
    assert not g1_fault.passed, "Gate 1 failed to reject broken JSON!"
    print(f"  -> Gate 1 Defect Caught: {g1_fault.errors[0]}")

    # Fault 2: Gate 2 Fault (Quota violation: 4 MCQs instead of 5)
    bad_assessments = WeeklyAssessmentBank(week_number=1, mcqs=mcqs[:4], true_false=tfs)
    g2_fault = ValidationGatesEngine.audit_gate_2_conforms(bad_assessments, lab, lecture)
    assert not g2_fault.passed, "Gate 2 failed to catch MCQ quota violation!"
    print(f"  -> Gate 2 Defect Caught: {g2_fault.errors[0]}")

    # Fault 3: Gate 3 Fault (Ghost citation)
    ghost_mcq = mcqs[0].model_copy(update={"citation_ref": "REF-GHOST-UNKNOWN"})
    bad_assessments_ghost = WeeklyAssessmentBank(week_number=1, mcqs=[ghost_mcq] + mcqs[1:], true_false=tfs)
    g3_fault = ValidationGatesEngine.audit_gate_3_refers(bad_assessments_ghost, schedule, valid_citations)
    assert not g3_fault.passed, "Gate 3 failed to catch Ghost Citation!"
    print(f"  -> Gate 3 Defect Caught: {g3_fault.errors[0]}")

    # Fault 4: Gate 4 Fault (Hour mismatch & Syntax error)
    bad_schedule = schedule.model_copy(update={"lecture_hours": 3.0, "lab_hours": 4.0, "total_hours": 10.0})
    bad_lab = lab.model_copy(update={"instructor_solution_code": "def broken_code(:\n    pass"})
    g4_fault = ValidationGatesEngine.audit_gate_4_coheres(bad_schedule, bad_lab)
    assert not g4_fault.passed, "Gate 4 failed to catch math imbalance or syntax error!"
    print(f"  -> Gate 4 Defects Caught: {g4_fault.errors}")

    print("\n" + "=" * 75)
    print("ALL PHASE 1 ARCHITECTURAL TESTS AND VALIDATION GATES VERIFIED SUCCESSFULLY!")
    print("=" * 75)
    return True

if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
