# Phase 1: Core Agent & Course Design

Part of the **COSC726 Agentic AI** Project: *Design of a Multi-Agent AI System for Training Course Design and Student Evaluation*.

---

## 📂 Contents
- `schemas.py`: Pydantic V2 models for `CoursePlan`, `CourseModule`, `LearningObjective`, `BloomTaxonomyLevel`, and `AssessmentStrategy`.
- `prompts.py`: System prompts and pedagogical guidelines.
- `model_client.py`: Dual-mode model client (offline deterministic + OpenAI API).
- `course_designer.py`: `CourseDesignerAgent` with execution tracing and pedagogical validation gates.
- `test_phase1.py`: Unit test suite.
- `main.py`: Standalone CLI execution script.
- `PHASE1_REPORT.md`: Comprehensive phase report.
- `outputs/`: Generated course plan JSON, Markdown, and agent execution traces.

---

## 🚀 How to Run

### 1. Run the Course Designer Pipeline
```bash
python main.py
```
Or customize the course topic:
```bash
python main.py --topic "Data Science with Python" --audience "Beginner" --hours 30.0
```

### 2. Run the Unit Tests
```bash
python -m unittest test_phase1.py
```
