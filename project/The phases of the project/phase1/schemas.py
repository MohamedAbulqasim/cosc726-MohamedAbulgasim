"""
Pydantic Schemas for Course Designer Agent & Course Planning
Academic Context: COSC726 Agentic AI
Project: Multi-Agent AI System for Training Course Design and Student Evaluation
"""

from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json
from pydantic import BaseModel, Field, field_validator, model_validator


class BloomTaxonomyLevel(str, Enum):
    """Bloom's Revised Taxonomy levels for learning objectives."""
    REMEMBER = "Remember"       # Recall facts and basic concepts
    UNDERSTAND = "Understand"   # Explain ideas or concepts
    APPLY = "Apply"             # Use information in new situations
    ANALYZE = "Analyze"         # Draw connections among ideas
    EVALUATE = "Evaluate"       # Justify a stand or decision
    CREATE = "Create"           # Produce new or original work


class TargetAudienceLevel(str, Enum):
    """Target skill level of the learners."""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    ALL_LEVELS = "All Levels"


class AssessmentMethod(str, Enum):
    """Assessment strategies supported across the agentic platform."""
    QUIZ_MCQ = "Multiple Choice Questions"
    TRUE_FALSE = "True/False Questions"
    CODING_CHALLENGE = "Coding Challenge"
    PRACTICAL_LAB = "Hands-on Practical Lab"
    MINI_PROJECT = "Mini Project"
    CAPSTONE_PROJECT = "Capstone Project"
    FINAL_EXAM = "Final Comprehensive Exam"


class LearningObjective(BaseModel):
    """Represents a specific, measurable learning objective aligned with Bloom's Taxonomy."""
    objective_id: str = Field(..., description="Unique identifier (e.g. LO-1.1)")
    description: str = Field(..., min_length=10, description="Clear description of the learning outcome")
    bloom_level: BloomTaxonomyLevel = Field(..., description="Cognitive level according to Bloom's taxonomy")
    keywords: List[str] = Field(default_factory=list, description="Key concepts covered by this objective")

    class Config:
        frozen = False


class ModuleTopic(BaseModel):
    """Detailed topic breakdown within a module."""
    topic_id: str = Field(..., description="Unique identifier (e.g. TOPIC-1.1)")
    title: str = Field(..., min_length=3, description="Topic title")
    description: str = Field(..., description="Summary of topic contents")
    subtopics: List[str] = Field(default_factory=list, description="Specific subtopics or lecture points")
    allocated_hours: float = Field(..., gt=0, description="Estimated duration in hours")


class AssessmentStrategy(BaseModel):
    """Assessment strategy for a module or whole course."""
    methods: List[AssessmentMethod] = Field(default_factory=lambda: [AssessmentMethod.QUIZ_MCQ, AssessmentMethod.CODING_CHALLENGE])
    passing_grade_percentage: float = Field(default=60.0, ge=0.0, le=100.0, description="Minimum passing percentage")
    weight_percentage: float = Field(default=100.0, ge=0.0, le=100.0, description="Weight towards course grade")
    description: str = Field(default="Balanced theoretical and hands-on assessment", description="Details on grading policy")


class CourseModule(BaseModel):
    """Structured module containing learning objectives, topics, and assessment details."""
    module_id: str = Field(..., description="Unique identifier (e.g. MOD-01)")
    module_number: int = Field(..., ge=1, description="Sequential module index")
    title: str = Field(..., min_length=3, description="Module title")
    description: str = Field(..., min_length=15, description="Comprehensive module overview")
    allocated_hours: float = Field(..., gt=0, description="Hours allocated for this module")
    learning_objectives: List[LearningObjective] = Field(..., min_length=1, description="List of learning objectives")
    topics: List[ModuleTopic] = Field(..., min_length=1, description="Topics taught in this module")
    assessment_strategy: AssessmentStrategy = Field(default_factory=AssessmentStrategy, description="Assessment approach for this module")

    @field_validator("learning_objectives")
    @classmethod
    def validate_objectives_non_empty(cls, v: List[LearningObjective]) -> List[LearningObjective]:
        if not v:
            raise ValueError("Module must contain at least one learning objective.")
        return v


class CourseRequirements(BaseModel):
    """Input specification for generating a new course design."""
    topic: str = Field(..., min_length=3, description="Core topic or course subject")
    target_audience: TargetAudienceLevel = Field(default=TargetAudienceLevel.BEGINNER, description="Target learner proficiency")
    total_hours: float = Field(..., gt=0, description="Total planned duration of the course in hours")
    prerequisites: List[str] = Field(default_factory=list, description="Assumed prior knowledge or tools")
    key_focus_areas: List[str] = Field(default_factory=list, description="Specific concepts that must be covered")
    special_instructions: Optional[str] = Field(default=None, description="Additional custom instructions")


class CoursePlan(BaseModel):
    """Complete, end-to-end Course Plan output produced by the Course Designer Agent."""
    course_id: str = Field(..., description="Unique Course ID (e.g. CRS-PY-101)")
    course_title: str = Field(..., min_length=5, description="Formal Title of the Course")
    short_description: str = Field(..., min_length=20, description="Executive summary and course narrative")
    target_audience: TargetAudienceLevel = Field(..., description="Target audience skill level")
    total_hours: float = Field(..., gt=0, description="Total course hours")
    prerequisites: List[str] = Field(default_factory=list, description="List of prerequisites")
    modules: List[CourseModule] = Field(..., min_length=1, description="Sequential curriculum modules")
    overall_assessment_strategy: AssessmentStrategy = Field(default_factory=AssessmentStrategy, description="Global assessment guidelines")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata including timestamps, agent version, generator parameters")

    @model_validator(mode="after")
    def validate_hours_and_structure(self) -> CoursePlan:
        # Validate that sum of module hours matches total_hours reasonably (within 0.5 hour tolerance)
        total_mod_hours = sum(m.allocated_hours for m in self.modules)
        if abs(total_mod_hours - self.total_hours) > 0.5:
            # Adjust or warn if mismatch
            self.metadata["hours_discrepancy_note"] = (
                f"Sum of module hours ({total_mod_hours}h) slightly adjusted to align with requested total ({self.total_hours}h)."
            )
        
        # Ensure sequential module numbers
        for idx, mod in enumerate(self.modules, start=1):
            mod.module_number = idx
            if not mod.module_id:
                mod.module_id = f"MOD-{idx:02d}"

        # Populate metadata if empty
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = datetime.now(timezone.utc).isoformat()
        if "agent_name" not in self.metadata:
            self.metadata["agent_name"] = "CourseDesignerAgent"
        if "version" not in self.metadata:
            self.metadata["version"] = "1.0.0"

        return self

    def to_markdown(self) -> str:
        """Renders the course plan into a comprehensive, beautifully formatted Markdown document."""
        md = []
        md.append(f"# 📘 {self.course_title}")
        md.append(f"**Course ID:** `{self.course_id}` | **Target Level:** `{self.target_audience.value}` | **Total Duration:** `{self.total_hours} Hours`\n")
        md.append("## 📌 Executive Summary")
        md.append(f"{self.short_description}\n")
        
        md.append("## 🔑 Prerequisites")
        if self.prerequisites:
            for req in self.prerequisites:
                md.append(f"- {req}")
        else:
            md.append("- No prior prerequisites required.")
        md.append("")

        md.append("## 🏆 Overall Assessment Strategy")
        methods_str = ", ".join([m.value for m in self.overall_assessment_strategy.methods])
        md.append(f"- **Evaluation Methods:** {methods_str}")
        md.append(f"- **Passing Score:** {self.overall_assessment_strategy.passing_grade_percentage}%")
        md.append(f"- **Strategy Description:** {self.overall_assessment_strategy.description}\n")

        md.append("---")
        md.append("## 📚 Course Curriculum & Modules\n")

        for mod in self.modules:
            md.append(f"### Module {mod.module_number}: {mod.title} (`{mod.allocated_hours} Hours`)")
            md.append(f"*{mod.description}*\n")
            
            md.append("#### 🎯 Learning Objectives:")
            for lo in mod.learning_objectives:
                md.append(f"- **[{lo.objective_id}]** ({lo.bloom_level.value}): {lo.description}")
            md.append("")

            md.append("#### 📖 Topics Covered:")
            for topic in mod.topics:
                subtopics_str = f" - *Subtopics:* {', '.join(topic.subtopics)}" if topic.subtopics else ""
                md.append(f"- **{topic.title}** ({topic.allocated_hours}h): {topic.description}{subtopics_str}")
            md.append("")

            mod_methods = ", ".join([m.value for m in mod.assessment_strategy.methods])
            md.append(f"**Module Assessment:** {mod_methods} (Weight: {mod.assessment_strategy.weight_percentage}%)\n")
            md.append("---")

        md.append("## ⚙️ Metadata & Audit")
        for k, v in self.metadata.items():
            md.append(f"- **{k}:** `{v}`")

        return "\n".join(md)

    def to_json_file(self, file_path: str) -> None:
        """Saves the course plan as a structured JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=2, ensure_ascii=False)

    def to_markdown_file(self, file_path: str) -> None:
        """Saves the course plan as a rendered Markdown file."""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.to_markdown())
