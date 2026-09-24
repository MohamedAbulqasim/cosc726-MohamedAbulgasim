"""
phase_1_architecture_contracts/contracts.py
Comprehensive Pydantic V2 Data Contracts for Autonomous Agentic Course Preparation.
Author: Mohammad Abulgasim | Supervisor: Dr. Fakhreldeen Saeed
Academic Context: COSC726 Agentic AI
"""

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field, field_validator

class CurriculumMetadata(BaseModel):
    course_title: str = Field(..., description="Full course title")
    course_code: Optional[str] = Field(default="COSC726", description="Course catalog code")
    academic_term: Optional[str] = Field(default="Fall 2026", description="Academic term / semester")
    target_weeks: int = Field(..., ge=1, le=52, description="Total instructional weeks")
    target_total_hours: float = Field(..., gt=0, description="Total contact hours")
    target_lecture_hours: float = Field(..., ge=0, description="Planned total lecture hours")
    target_lab_hours: float = Field(..., ge=0, description="Planned total practical lab hours")
    language: str = Field(default="en", description="Course language code ('en' or 'ar')")
    has_lab: bool = Field(default=True, description="True if course includes practical/lab component")
    practical_domain: str = Field(default="python", description="Practical domain/tool (e.g. python, sql, bash, cpp, web, case_study)")

    @field_validator("target_total_hours")
    def validate_total_hours(cls, v, info):
        return v

class SyllabusChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier, e.g. PARENT-01 or CHILD-01-03")
    parent_id: Optional[str] = Field(default=None, description="Parent container ID if this is a child chunk")
    chunk_type: Literal["parent", "child", "standalone"] = Field(default="standalone")
    text: str = Field(..., min_length=10, description="Text segment payload")
    section_name: str = Field(default="General", description="Syllabus section header")
    page_number: int = Field(default=1, ge=1, description="Source PDF page number")
    char_length: int = Field(default=0, description="Character count")

class WeeklyTopicDecomposition(BaseModel):
    week_number: int = Field(..., ge=1, description="Week index (1-based)")
    title: str = Field(..., min_length=3, description="Week module theme/topic title")
    lecture_hours: float = Field(..., ge=0, description="Allocated lecture contact hours")
    lab_hours: float = Field(..., ge=0, description="Allocated lab contact hours")
    total_hours: float = Field(..., ge=0, description="Total contact hours for this week")
    has_lab: bool = Field(default=True, description="Whether this week has a practical lab component")
    lecture_topics: List[str] = Field(default_factory=list, description="Subtopics covered in lectures")
    lab_tasks: List[str] = Field(default_factory=list, description="Practical laboratory exercises")
    citation_ids: List[str] = Field(default_factory=list, description="Referenced syllabus chunk or citation IDs")

class LectureScript(BaseModel):
    week_number: int = Field(..., ge=1)
    delivery_script: str = Field(..., min_length=50, description="Detailed lecture script for instructor")
    discussion_prompts: List[str] = Field(default_factory=list, description="Interactive discussion starters")
    trainee_reading_summary: str = Field(..., min_length=30, description="Concise reading synthesis for student kit")
    learning_outcomes: List[str] = Field(..., min_length=1, description="Concrete weekly student learning outcomes")

class LabAssignment(BaseModel):
    week_number: int = Field(..., ge=1)
    assignment_title: str = Field(..., min_length=5)
    student_starter_code: str = Field(..., min_length=20, description="Starter template with explicit TODO tasks")
    student_debug_challenges: List[str] = Field(default_factory=list, description="Hands-on debugging problems or practical challenges")
    instructor_solution_code: str = Field(..., min_length=20, description="Complete solution code or reference model solution")
    rubrics: List[str] = Field(default_factory=list, description="Grading criteria and point allocations")
    tool_or_language: str = Field(default="python", description="Practical tool/language (python, sql, bash, cpp, web, case_study)")
    has_executable_code: bool = Field(default=True, description="True if involves executable code, False for conceptual case studies")

class MCQQuestion(BaseModel):
    question_id: str = Field(..., description="Unique question identifier, e.g. W1-MCQ-1")
    week_number: int = Field(..., ge=1)
    stem: str = Field(..., min_length=10, description="Multiple choice question text")
    options: List[str] = Field(..., min_length=4, max_length=4, description="Four options A, B, C, D")
    correct_answer: str = Field(..., pattern=r"^[A-D]$", description="Correct answer letter (A, B, C, or D)")
    rationale: str = Field(..., min_length=10, description="Pedagogical explanation of why this answer is correct")
    citation_ref: str = Field(..., min_length=2, description="Evidence citation provenance referencing syllabus chunk or REF")

class TrueFalseQuestion(BaseModel):
    question_id: str = Field(..., description="Unique question identifier, e.g. W1-TF-1")
    week_number: int = Field(..., ge=1)
    statement: str = Field(..., min_length=10, description="True or False statement")
    is_true: bool = Field(..., description="Boolean ground truth value")
    rationale: str = Field(..., min_length=10, description="Pedagogical explanation and justification")
    citation_ref: str = Field(..., min_length=2, description="Evidence citation provenance referencing syllabus chunk or REF")

class WeeklyAssessmentBank(BaseModel):
    week_number: int = Field(..., ge=1)
    mcqs: List[MCQQuestion] = Field(..., description="Formative Multiple Choice Questions (strictly 5 items)")
    true_false: List[TrueFalseQuestion] = Field(..., description="Formative True/False Questions (strictly 5 items)")

class GateCheckResult(BaseModel):
    gate_name: str = Field(..., description="Name of the gate, e.g. Gate 1 (Parses)")
    passed: bool = Field(..., description="True if gate criteria fully satisfied")
    score: float = Field(..., ge=0.0, le=1.0, description="Conformance score from 0.0 to 1.0")
    details: str = Field(..., description="Human-readable explanation of audit findings")
    errors: List[str] = Field(default_factory=list, description="Specific error details if any")

class FourGatesAuditResult(BaseModel):
    gate_1_parses: GateCheckResult
    gate_2_conforms: GateCheckResult
    gate_3_refers: GateCheckResult
    gate_4_coheres: GateCheckResult
    all_passed: bool
    total_score: float
    audit_timestamp: str

class FullWeeklyModulePackage(BaseModel):
    week_number: int
    schedule: WeeklyTopicDecomposition
    lecture: LectureScript
    lab: Optional[LabAssignment] = None
    assessments: WeeklyAssessmentBank
    audit: Optional[FourGatesAuditResult] = None
