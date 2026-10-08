"""
Multi-Agent Orchestrator:
Coordinates the sequential execution of all 5 clinical agents through Quality Gates:
1. Clinical Triage & Validation Agent
2. ML Diagnostic & Predictive Analytics Agent
3. Clinical Reasoning & LLM Explainer Agent
4. Personalized Lifestyle & Nutrition Agent
5. Safety Guardrails & Governance Gatekeeper Agent
"""

import time
from typing import Callable, Optional, Dict, Any
from schemas import PatientInput, MultiAgentDiagnosticDossier
from triage_agent import ClinicalTriageAgent
from diagnostic_agent import MLDiagnosticAgent
from reasoning_agent import ClinicalReasoningAgent
from lifestyle_agent import LifestyleNutritionAgent
from gatekeeper_agent import SafetyGatekeeperAgent
from llm_engine import ClinicalLLMEngine

class ClinicalAgentOrchestrator:
    def __init__(
        self,
        llm_provider: str = "auto",
        api_key: str = None,
        model_name: str = None,
        base_url: str = None
    ):
        self.llm_engine = ClinicalLLMEngine(
            provider=llm_provider,
            api_key=api_key,
            model_name=model_name,
            base_url=base_url
        )
        self.triage_agent = ClinicalTriageAgent()
        self.diagnostic_agent = MLDiagnosticAgent()
        self.reasoning_agent = ClinicalReasoningAgent(llm_engine=self.llm_engine)
        self.lifestyle_agent = LifestyleNutritionAgent(llm_engine=self.llm_engine)
        self.gatekeeper_agent = SafetyGatekeeperAgent()

    def run_pipeline(
        self,
        patient: PatientInput,
        progress_callback: Optional[Callable[[str, int, str], None]] = None
    ) -> MultiAgentDiagnosticDossier:
        """
        Executes the full clinical multi-agent workflow.
        `progress_callback` receives (agent_name, progress_percent, status_message)
        """
        start_total = time.perf_counter()

        # Step 1: Clinical Triage
        if progress_callback:
            progress_callback("وكيل الفرز والتحقق السريري (Triage Agent)", 20, "فحص الحدود البيولوجية وتصفية الأصفار...")
        triage_res = self.triage_agent.execute(patient)

        # Step 2: ML Diagnostic & Predictive Analytics
        if progress_callback:
            progress_callback("وكيل النمذجة التنبؤية (ML Diagnostic Agent)", 45, "تشغيل النماذج المعايرة وحساب احتمالية الخطر...")
        diag_res = self.diagnostic_agent.execute(triage_res)

        # Step 3: Clinical Reasoning & LLM Explainer
        if progress_callback:
            progress_callback("وكيل التعليل السريري (Clinical Reasoning Agent)", 65, "توليد الشرح الطبي المستند لمعايير ADA...")
        reason_res = self.reasoning_agent.execute(patient, diag_res)

        # Step 4: Lifestyle & Nutrition Planning
        if progress_callback:
            progress_callback("وكيل نمط الحياة والتغذية (Lifestyle Agent)", 85, "صياغة الخطة الغذائية والنشاط البدني الآمن...")
        lifestyle_res = self.lifestyle_agent.execute(patient, diag_res)

        # Step 5: Safety Guardrails & Governance Gatekeeper
        if progress_callback:
            progress_callback("وكيل الحوكمة والأمان (Gatekeeper Agent)", 95, "تدقيق بوابات الجودة وكشف حالات الطوارئ...")
        gate_res = self.gatekeeper_agent.execute(patient, triage_res, diag_res, reason_res, lifestyle_res)

        if progress_callback:
            progress_callback("اكتمال الملف التشخيصي", 100, "تم اعتماد وتوثيق نتائج كافة الوكلاء بنجاح!")

        total_elapsed_ms = (time.perf_counter() - start_total) * 1000.0

        return MultiAgentDiagnosticDossier(
            patient_input=patient,
            triage=triage_res,
            prediction=diag_res,
            reasoning=reason_res,
            lifestyle=lifestyle_res,
            gatekeeper=gate_res,
            execution_time_ms=round(total_elapsed_ms, 2),
            overall_status="CERTIFIED" if gate_res.is_approved else "ACTION_REQUIRED"
        )
