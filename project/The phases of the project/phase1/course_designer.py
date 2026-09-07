"""
Course Designer Agent Implementation
Academic Context: COSC726 Agentic AI
Project: Multi-Agent AI System for Training Course Design and Student Evaluation
"""

import time
from datetime import datetime, timezone
import json
from typing import Optional, List, Dict, Any, Tuple

from .schemas import (
    CoursePlan,
    CourseRequirements,
    BloomTaxonomyLevel,
)
from .model_client import BaseModelClient, ModelClientFactory


class CourseDesignerAgent:
    """
    Autonomous Course Designer Agent.
    Responsible for architecting high-level course structures, module breakdowns,
    Bloom's Taxonomy-aligned learning objectives, and assessment strategies.
    """

    def __init__(self, model_client: Optional[BaseModelClient] = None, enable_tracing: bool = True):
        self.client = model_client or ModelClientFactory.create_client()
        self.enable_tracing = enable_tracing
        self.traces: List[Dict[str, Any]] = []

    def _log_trace(self, action: str, details: Dict[str, Any]) -> None:
        if not self.enable_tracing:
            return
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": "CourseDesignerAgent",
            "action": action,
            "details": details,
        }
        self.traces.append(entry)

    def design_course(self, requirements: CourseRequirements) -> CoursePlan:
        """
        Executes the course design workflow:
        1. Logs incoming design request.
        2. Generates initial course plan via ModelClient.
        3. Validates pedagogical integrity and structural constraints.
        4. Attaches audit metadata and execution trace.
        """
        start_time = time.time()
        self._log_trace("START_DESIGN", {
            "topic": requirements.topic,
            "total_hours": requirements.total_hours,
            "target_audience": requirements.target_audience.value,
            "prerequisites": requirements.prerequisites,
            "key_focus_areas": requirements.key_focus_areas
        })

        # 1. Model generation
        plan = self.client.generate_course_plan(requirements)

        # 2. Structural & Pedagogical validation
        is_valid, validation_notes = self.validate_plan_pedagogy(plan)

        elapsed = round(time.time() - start_time, 3)
        self._log_trace("COMPLETE_DESIGN", {
            "course_id": plan.course_id,
            "course_title": plan.course_title,
            "module_count": len(plan.modules),
            "is_pedagogically_valid": is_valid,
            "validation_notes": validation_notes,
            "elapsed_seconds": elapsed,
        })

        # Attach execution metrics
        plan.metadata["execution_time_seconds"] = elapsed
        plan.metadata["pedagogical_validation"] = {
            "passed": is_valid,
            "notes": validation_notes,
        }
        plan.metadata["total_learning_objectives"] = sum(len(m.learning_objectives) for m in plan.modules)
        plan.metadata["bloom_distribution"] = self._compute_bloom_distribution(plan)

        return plan

    def refine_course(self, existing_plan: CoursePlan, feedback: str) -> CoursePlan:
        """
        Interactive refinement step (Human-in-the-Loop support).
        Updates existing plan incorporating instructor feedback.
        """
        self._log_trace("START_REFINEMENT", {
            "course_id": existing_plan.course_id,
            "feedback": feedback
        })

        updated_plan = self.client.refine_course_plan(existing_plan, feedback)
        
        is_valid, validation_notes = self.validate_plan_pedagogy(updated_plan)
        
        self._log_trace("COMPLETE_REFINEMENT", {
            "course_id": updated_plan.course_id,
            "is_valid": is_valid,
            "validation_notes": validation_notes
        })

        return updated_plan

    def validate_plan_pedagogy(self, plan: CoursePlan) -> Tuple[bool, List[str]]:
        """
        Deterministic pedagogical validation gate:
        - Hours conservation.
        - Minimum module count.
        - Bloom Taxonomy diversity.
        - Unique objective IDs.
        """
        notes: List[str] = []
        is_valid = True

        # Check total hours
        mod_hours_sum = sum(m.allocated_hours for m in plan.modules)
        if abs(mod_hours_sum - plan.total_hours) > 0.01:
            notes.append(f"Hours mismatch: sum of modules is {mod_hours_sum}h vs declared {plan.total_hours}h.")
            is_valid = False
        else:
            notes.append(f"Hours balanced: {mod_hours_sum}h exactly matches total duration.")

        # Check Bloom levels
        bloom_levels = set()
        all_lo_ids = set()
        for mod in plan.modules:
            for lo in mod.learning_objectives:
                bloom_levels.add(lo.bloom_level)
                if lo.objective_id in all_lo_ids:
                    notes.append(f"Duplicate objective ID found: {lo.objective_id}")
                    is_valid = False
                all_lo_ids.add(lo.objective_id)

        notes.append(f"Bloom taxonomy levels covered: {', '.join(b.value for b in bloom_levels)} ({len(bloom_levels)} distinct levels).")

        if len(plan.modules) < 1:
            notes.append("Course has no modules defined.")
            is_valid = False

        return is_valid, notes

    def _compute_bloom_distribution(self, plan: CoursePlan) -> Dict[str, int]:
        dist: Dict[str, int] = {level.value: 0 for level in BloomTaxonomyLevel}
        for mod in plan.modules:
            for lo in mod.learning_objectives:
                dist[lo.bloom_level.value] = dist.get(lo.bloom_level.value, 0) + 1
        return dist

    def export_traces(self, file_path: str) -> None:
        """Exports audit logs to file for auditing and system evaluation."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.traces, f, indent=2, ensure_ascii=False)
