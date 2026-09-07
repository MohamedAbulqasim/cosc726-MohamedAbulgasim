"""
Unit Tests for Phase 1: Core Agent & Course Design
Academic Context: COSC726 Agentic AI
Project: Multi-Agent AI System for Training Course Design and Student Evaluation
"""

import unittest
import os
import tempfile
from pydantic import ValidationError

from phase1.schemas import (
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
from phase1.model_client import DeterministicCourseModelClient
from phase1.course_designer import CourseDesignerAgent


class TestPhase1Schemas(unittest.TestCase):
    """Test suite for Pydantic schema validation and constraints."""

    def test_learning_objective_validation(self):
        lo = LearningObjective(
            objective_id="LO-1.1",
            description="Understand the fundamental syntax and variables in Python",
            bloom_level=BloomTaxonomyLevel.UNDERSTAND,
            keywords=["variables", "syntax", "python"]
        )
        self.assertEqual(lo.objective_id, "LO-1.1")
        self.assertEqual(lo.bloom_level, BloomTaxonomyLevel.UNDERSTAND)
        self.assertEqual(len(lo.keywords), 3)

        # Invalid short description
        with self.assertRaises(ValidationError):
            LearningObjective(
                objective_id="LO-1.2",
                description="Short",  # < 10 chars
                bloom_level=BloomTaxonomyLevel.APPLY
            )

    def test_module_topic_validation(self):
        topic = ModuleTopic(
            topic_id="TOPIC-1.1",
            title="Introduction to Data Types",
            description="Detailed look at primitives and collections",
            subtopics=["integers", "floats", "strings", "booleans"],
            allocated_hours=2.5
        )
        self.assertEqual(topic.allocated_hours, 2.5)
        self.assertEqual(len(topic.subtopics), 4)

        # Negative or zero hours must fail
        with self.assertRaises(ValidationError):
            ModuleTopic(
                topic_id="TOPIC-1.2",
                title="Invalid Duration",
                description="Testing zero duration",
                allocated_hours=0
            )

    def test_course_module_constraints(self):
        lo = LearningObjective(
            objective_id="LO-1.1",
            description="Apply control flow structures to build automated scripts",
            bloom_level=BloomTaxonomyLevel.APPLY,
            keywords=["control flow", "loops"]
        )
        topic = ModuleTopic(
            topic_id="TOPIC-1.1",
            title="Conditional Statements and Loops",
            description="Mastering if-else, while, and for loops in Python",
            allocated_hours=4.0
        )
        mod = CourseModule(
            module_id="MOD-01",
            module_number=1,
            title="Control Flow & Automation",
            description="Comprehensive training on conditional logic, looping constructs, and iteration patterns.",
            allocated_hours=4.0,
            learning_objectives=[lo],
            topics=[topic]
        )
        self.assertEqual(mod.module_id, "MOD-01")
        self.assertEqual(len(mod.learning_objectives), 1)

        # Empty learning objectives must fail
        with self.assertRaises(ValidationError):
            CourseModule(
                module_id="MOD-02",
                module_number=2,
                title="Empty Objectives",
                description="Module with no learning objectives defined.",
                allocated_hours=4.0,
                learning_objectives=[],
                topics=[topic]
            )

    def test_course_plan_serialization_and_markdown(self):
        req = CourseRequirements(
            topic="Agentic AI Systems",
            target_audience=TargetAudienceLevel.ADVANCED,
            total_hours=24.0,
            prerequisites=["Python 3.10+", "OOP", "Basic LLM Knowledge"],
            key_focus_areas=["Tool Calling", "Memory Management", "Orchestration"]
        )
        client = DeterministicCourseModelClient()
        plan = client.generate_course_plan(req)

        self.assertIsInstance(plan, CoursePlan)
        self.assertEqual(plan.total_hours, 24.0)
        self.assertTrue(len(plan.modules) >= 3)
        self.assertEqual(sum(m.allocated_hours for m in plan.modules), 24.0)

        # Test Markdown generation
        md_content = plan.to_markdown()
        self.assertIn("# 📘", md_content)
        self.assertIn("Course ID:", md_content)
        self.assertIn("Module 1:", md_content)

        # Test JSON file export
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_json:
            tmp_path = tmp_json.name
        try:
            plan.to_json_file(tmp_path)
            self.assertTrue(os.path.exists(tmp_path))
            self.assertGreater(os.path.getsize(tmp_path), 100)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestCourseDesignerAgent(unittest.TestCase):
    """Test suite for the Course Designer Agent execution and tracing."""

    def setUp(self):
        self.agent = CourseDesignerAgent(enable_tracing=True)

    def test_course_designer_agent_execution(self):
        req = CourseRequirements(
            topic="Data Science with Python",
            target_audience=TargetAudienceLevel.BEGINNER,
            total_hours=30.0,
            key_focus_areas=["NumPy", "Pandas", "Matplotlib", "Seaborn"]
        )

        plan = self.agent.design_course(req)

        self.assertIsInstance(plan, CoursePlan)
        self.assertEqual(plan.total_hours, 30.0)
        self.assertTrue(plan.metadata["pedagogical_validation"]["passed"])
        self.assertGreater(len(self.agent.traces), 0)

        # Validate Bloom distribution
        bloom_dist = plan.metadata["bloom_distribution"]
        self.assertIn("Understand", bloom_dist)
        self.assertIn("Apply", bloom_dist)

    def test_course_refinement_workflow(self):
        req = CourseRequirements(
            topic="Cloud Computing with AWS",
            target_audience=TargetAudienceLevel.INTERMEDIATE,
            total_hours=18.0
        )
        plan = self.agent.design_course(req)
        
        feedback = "Please add Linux Command Line as an explicit prerequisite."
        refined = self.agent.refine_course(plan, feedback)

        self.assertIn("refined_at", refined.metadata)
        self.assertTrue(any("Linux Command Line" in p for p in refined.prerequisites))


if __name__ == "__main__":
    unittest.main()
