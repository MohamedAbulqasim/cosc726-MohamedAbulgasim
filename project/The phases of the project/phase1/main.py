"""
Executable Runner for Phase 1: Core Agent & Course Design
Can be run directly from terminal: python phase1/main.py or from within phase1/
Academic Context: COSC726 Agentic AI
Project: Multi-Agent AI System for Training Course Design and Student Evaluation
"""

import sys
import os
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root and current folder to sys.path so it runs standalone
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))

try:
    from schemas import (
        CourseRequirements,
        TargetAudienceLevel,
        CoursePlan,
    )
    from course_designer import CourseDesignerAgent
    from model_client import ModelClientFactory
except ImportError:
    from phase1.schemas import (
        CourseRequirements,
        TargetAudienceLevel,
        CoursePlan,
    )
    from phase1.course_designer import CourseDesignerAgent
    from phase1.model_client import ModelClientFactory


def run_phase1_pipeline(
    topic: str = "Modern Python & Agentic AI Engineering",
    audience: str = "Intermediate",
    total_hours: float = 36.0,
    output_dir: str = None
) -> CoursePlan:
    """Executes the Phase 1 Course Design pipeline and saves the outputs."""
    
    out_path = Path(output_dir) if output_dir else current_dir / "outputs"
    out_path.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("[PHASE 1] Running Course Designer Agent Pipeline")
    print(f"Academic Context: COSC726 Agentic AI")
    print("=" * 70)
    print(f"Course Topic     : {topic}")
    print(f"Target Audience  : {audience}")
    print(f"Total Hours      : {total_hours} Hours")
    print("-" * 70)

    # Initialize requirements
    audience_enum = TargetAudienceLevel(audience) if audience in [e.value for e in TargetAudienceLevel] else TargetAudienceLevel.INTERMEDIATE
    requirements = CourseRequirements(
        topic=topic,
        target_audience=audience_enum,
        total_hours=total_hours,
        prerequisites=[
            "Foundational programming logic",
            "Basic object-oriented programming concepts",
            "Basic CLI experience"
        ],
        key_focus_areas=[
            "Pydantic Structured Schemas",
            "Autonomous Tool Calling",
            "Stateful Memory & Context Window Management",
            "Deterministic Evaluation & Guardrails"
        ],
        special_instructions="Emphasize production readiness and strict type-safety."
    )

    # Initialize agent
    agent = CourseDesignerAgent(enable_tracing=True)
    
    print("\n[AGENT] Invoking Course Designer Agent...")
    plan = agent.design_course(requirements)

    print(f"\n[SUCCESS] Course Designed Successfully!")
    print(f"   - Course Title : {plan.course_title}")
    print(f"   - Course ID    : {plan.course_id}")
    print(f"   - Modules Count: {len(plan.modules)}")
    print(f"   - Total LOs    : {plan.metadata.get('total_learning_objectives')}")
    print(f"   - Exec Time    : {plan.metadata.get('execution_time_seconds')}s")

    # Export Course Plan to Markdown and JSON
    json_path = out_path / "course_plan.json"
    md_path = out_path / "course_plan.md"
    trace_path = out_path / "agent_traces.json"

    plan.to_json_file(str(json_path))
    plan.to_markdown_file(str(md_path))
    agent.export_traces(str(trace_path))

    print("\n[ARTIFACTS] Exported Files:")
    print(f"   - JSON Schema Output : {json_path}")
    print(f"   - Rendered Markdown  : {md_path}")
    print(f"   - Execution Traces   : {trace_path}")

    print("\n" + "=" * 70)
    print("Bloom's Revised Taxonomy Coverage:")
    for level, count in plan.metadata.get("bloom_distribution", {}).items():
        bar = "#" * (count * 2)
        print(f"   - {level:<12}: {bar} ({count})")
    print("=" * 70)

    return plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 1: Course Designer Agent Runner")
    parser.add_argument("--topic", type=str, default="Modern Python & Agentic AI Engineering", help="Course Subject")
    parser.add_argument("--audience", type=str, default="Intermediate", help="Beginner, Intermediate, Advanced, All Levels")
    parser.add_argument("--hours", type=float, default=36.0, help="Total course duration in hours")
    parser.add_argument("--output-dir", type=str, default=None, help="Directory to save generated outputs")

    args = parser.parse_args()
    run_phase1_pipeline(
        topic=args.topic,
        audience=args.audience,
        total_hours=args.hours,
        output_dir=args.output_dir
    )
