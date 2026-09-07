"""
Phase 1: Core Agent & Course Design
Academic Context: COSC726 Agentic AI
Project: Multi-Agent AI System for Training Course Design and Student Evaluation
"""

from .schemas import (
    BloomTaxonomyLevel,
    TargetAudienceLevel,
    AssessmentMethod,
    LearningObjective,
    ModuleTopic,
    CourseModule,
    AssessmentStrategy,
    CourseRequirements,
    CoursePlan,
)
from .course_designer import CourseDesignerAgent
from .model_client import ModelClientFactory, BaseModelClient

__all__ = [
    "BloomTaxonomyLevel",
    "TargetAudienceLevel",
    "AssessmentMethod",
    "LearningObjective",
    "ModuleTopic",
    "CourseModule",
    "AssessmentStrategy",
    "CourseRequirements",
    "CoursePlan",
    "CourseDesignerAgent",
    "ModelClientFactory",
    "BaseModelClient",
]
