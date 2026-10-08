"""
Agent 3: Clinical Reasoning and LLM Explainer Agent
Responsibilities:
- Interprets ML probability and biomarker contributions into natural language clinical reasoning
- Aligns explanations with American Diabetes Association (ADA) clinical standards
- Generates comprehensive bilingual output (Arabic & English)
- Enforces Gate 3: Semantic Alignment Gate (prevents contradictory diagnosis)
"""

from typing import Dict, Any
from schemas import PatientInput, PredictionResult, ClinicalReasoningResult
from llm_engine import ClinicalLLMEngine

class ClinicalReasoningAgent:
    def __init__(self, llm_engine: ClinicalLLMEngine = None):
        self.agent_name = "Clinical Reasoning & LLM Explainer Agent"
        self.agent_name_ar = "وكيل التعليل السريري وتفسير الذكاء الاصطناعي"
        self.llm = llm_engine or ClinicalLLMEngine()

    def execute(self, patient: PatientInput, prediction: PredictionResult) -> ClinicalReasoningResult:
        p_dict = patient.model_dump()
        pred_dict = prediction.model_dump()

        # Generate reasoning from LLM engine (Gemini, OpenAI, or ADA deterministic expert)
        reasoning_data = self.llm.generate_clinical_reasoning(p_dict, pred_dict)

        # Gate 3: Semantic Alignment Verification
        # Check that explanation does not contradict prediction label
        label = prediction.prediction_label
        prob = prediction.diabetes_probability
        summary_ar = reasoning_data.get('summary_ar', '')
        summary_en = reasoning_data.get('summary_en', '')

        contradiction_detected = False
        if label == 1 and ("منخفضة" in summary_ar and "مرتفعة" not in summary_ar):
            contradiction_detected = True
        elif label == 0 and ("إصابة بداء السكري" in summary_ar and "منخفضة" not in summary_ar):
            contradiction_detected = True

        gate_status = "PASSED" if not contradiction_detected else "FAILED_SEMANTIC_MISMATCH"

        return ClinicalReasoningResult(
            summary_ar=summary_ar,
            summary_en=summary_en,
            detailed_explanation_ar=reasoning_data.get('detailed_explanation_ar', ''),
            detailed_explanation_en=reasoning_data.get('detailed_explanation_en', ''),
            ada_guidelines_alignment=reasoning_data.get('ada_guidelines_alignment', []),
            key_drivers_identified=reasoning_data.get('key_drivers_identified', []),
            gate_status=gate_status
        )
