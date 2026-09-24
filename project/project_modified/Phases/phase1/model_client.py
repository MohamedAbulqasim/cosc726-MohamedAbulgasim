"""
phase_1_architecture_contracts/model_client.py
Expanded Multi-Model Inference Seam (ModelClient)
Supports:
  1. Local offline inference using Qwen 2.5 (1.5B via Ollama)
  2. Cohere Command-R via hosted API
  3. OpenAI (GPT-4o / GPT-4o-mini)
  4. Claude 3.5 (Anthropic)
  5. Deterministic Mock / Offline Test Provider (for local validation without API keys)
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

logger = logging.getLogger("ModelClient")

class GenerationConfig(BaseModel):
    temperature: float = 0.2
    max_tokens: int = 2048
    top_p: float = 0.95
    json_mode: bool = True

class ModelResponse(BaseModel):
    raw_text: str
    parsed_json: Optional[Dict[str, Any]] = None
    model_name: str
    provider: str
    usage_tokens: Optional[int] = 0

class ModelClient:
    """
    Unified seam isolating agent reasoning logic from underlying LLM provider endpoints.
    Allows hot-swapping between local open-weights and cloud inference engines.
    """
    def __init__(self, provider: str = "mock", model_name: Optional[str] = None, api_key: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key
        if model_name:
            self.model_name = model_name
        else:
            self.model_name = self._default_model_for_provider(self.provider)

        # Synchronize explicit api_key to os.environ so underlying SDKs pick it up seamlessly
        if self.api_key:
            if self.provider == "openai":
                os.environ["OPENAI_API_KEY"] = self.api_key
            elif self.provider == "cohere":
                os.environ["CO_API_KEY"] = self.api_key
                os.environ["COHERE_API_KEY"] = self.api_key
            elif self.provider == "claude":
                os.environ["ANTHROPIC_API_KEY"] = self.api_key
            elif self.provider in ["gemini", "google"]:
                os.environ["GEMINI_API_KEY"] = self.api_key

    def _default_model_for_provider(self, provider: str) -> str:
        defaults = {
            "ollama": "qwen2.5:1.5b",
            "cohere": "command-r-plus",
            "openai": "gpt-4o-mini",
            "claude": "claude-3-5-sonnet-20241022",
            "gemini": "gemini-2.5-flash",
            "mock": "mock-curriculum-synthesizer-v1"
        }
        return defaults.get(provider, "mock-curriculum-synthesizer-v1")

    def generate(self, prompt: str, system_prompt: Optional[str] = None, config: Optional[GenerationConfig] = None) -> ModelResponse:
        cfg = config or GenerationConfig()
        
        if self.provider == "ollama":
            return self._call_ollama(prompt, system_prompt, cfg)
        elif self.provider == "cohere":
            return self._call_cohere(prompt, system_prompt, cfg)
        elif self.provider == "openai":
            return self._call_openai(prompt, system_prompt, cfg)
        elif self.provider == "claude":
            return self._call_claude(prompt, system_prompt, cfg)
        elif self.provider in ["gemini", "google"]:
            return self._call_gemini(prompt, system_prompt, cfg)
        elif self.provider == "mock":
            return self._call_mock(prompt, system_prompt, cfg)
        else:
            logger.warning(f"Unknown provider '{self.provider}', falling back to mock provider.")
            return self._call_mock(prompt, system_prompt, cfg)

    def _call_ollama(self, prompt: str, system_prompt: Optional[str], cfg: GenerationConfig) -> ModelResponse:
        import requests
        url = os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt or "",
            "stream": False,
            "options": {
                "temperature": cfg.temperature,
                "num_predict": cfg.max_tokens,
                "top_p": cfg.top_p
            }
        }
        if cfg.json_mode:
            payload["format"] = "json"

        try:
            resp = requests.post(url, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data.get("response", "")
            parsed = self._extract_json(raw_text) if cfg.json_mode else None
            return ModelResponse(
                raw_text=raw_text,
                parsed_json=parsed,
                model_name=self.model_name,
                provider="ollama"
            )
        except Exception as e:
            logger.error(f"Ollama call failed: {e}. Falling back to deterministic mock response.")
            return self._call_mock(prompt, system_prompt, cfg)

    def _call_cohere(self, prompt: str, system_prompt: Optional[str], cfg: GenerationConfig) -> ModelResponse:
        api_key = self.api_key or os.getenv("CO_API_KEY") or os.getenv("COHERE_API_KEY")
        if not api_key:
            logger.warning("Cohere API key missing, falling back to mock.")
            return self._call_mock(prompt, system_prompt, cfg)
        try:
            import cohere
            co = cohere.Client(api_key=api_key)
            response = co.chat(
                model=self.model_name,
                message=prompt,
                preamble=system_prompt,
                temperature=cfg.temperature,
                response_format={"type": "json_object"} if cfg.json_mode else None
            )
            raw_text = response.text
            parsed = self._extract_json(raw_text) if cfg.json_mode else None
            return ModelResponse(
                raw_text=raw_text,
                parsed_json=parsed,
                model_name=self.model_name,
                provider="cohere"
            )
        except Exception as e:
            logger.error(f"Cohere call failed: {e}. Fallback to mock.")
            return self._call_mock(prompt, system_prompt, cfg)

    def _call_openai(self, prompt: str, system_prompt: Optional[str], cfg: GenerationConfig) -> ModelResponse:
        api_key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI API key missing, falling back to mock.")
            return self._call_mock(prompt, system_prompt, cfg)
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": cfg.temperature,
                "max_tokens": cfg.max_tokens
            }
            if cfg.json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            completion = client.chat.completions.create(**kwargs)
            raw_text = completion.choices[0].message.content or ""
            parsed = self._extract_json(raw_text) if cfg.json_mode else None
            return ModelResponse(
                raw_text=raw_text,
                parsed_json=parsed,
                model_name=self.model_name,
                provider="openai"
            )
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}. Fallback to mock.")
            return self._call_mock(prompt, system_prompt, cfg)

    def _call_claude(self, prompt: str, system_prompt: Optional[str], cfg: GenerationConfig) -> ModelResponse:
        api_key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("Anthropic API key missing, falling back to mock.")
            return self._call_mock(prompt, system_prompt, cfg)
        try:
            import httpx
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            body = {
                "model": self.model_name,
                "max_tokens": cfg.max_tokens,
                "temperature": cfg.temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                body["system"] = system_prompt
            res = httpx.post("https://api.anthropic.com/v1/messages", json=body, headers=headers, timeout=60.0)
            res.raise_for_status()
            data = res.json()
            raw_text = data["content"][0]["text"]
            parsed = self._extract_json(raw_text) if cfg.json_mode else None
            return ModelResponse(
                raw_text=raw_text,
                parsed_json=parsed,
                model_name=self.model_name,
                provider="claude"
            )
        except Exception as e:
            logger.error(f"Claude call failed: {e}. Fallback to mock.")
            return self._call_mock(prompt, system_prompt, cfg)

    def _call_gemini(self, prompt: str, system_prompt: Optional[str], cfg: GenerationConfig) -> ModelResponse:
        api_key = self.api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("Gemini API key missing, falling back to mock.")
            return self._call_mock(prompt, system_prompt, cfg)
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)

            config_params = {
                "temperature": cfg.temperature,
                "max_output_tokens": cfg.max_tokens,
            }
            if system_prompt:
                config_params["system_instruction"] = system_prompt
            if cfg.json_mode:
                config_params["response_mime_type"] = "application/json"

            config_obj = types.GenerateContentConfig(**config_params) if hasattr(types, "GenerateContentConfig") else config_params
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config_obj
            )
            raw_text = response.text or ""
            parsed = self._extract_json(raw_text) if cfg.json_mode else None
            return ModelResponse(
                raw_text=raw_text,
                parsed_json=parsed,
                model_name=self.model_name,
                provider="gemini"
            )
        except Exception as e:
            logger.error(f"Gemini call failed: {e}. Fallback to mock.")
            return self._call_mock(prompt, system_prompt, cfg)

    def _call_mock(self, prompt: str, system_prompt: Optional[str], cfg: GenerationConfig) -> ModelResponse:
        """
        High-fidelity deterministic offline generator for validation and unit tests.
        Produces calibrated structured responses dynamically matching whatever course and topic are requested.
        """
        import re
        prompt_lower = prompt.lower()

        # Extract week number dynamically (supporting English & Arabic)
        w_match = re.search(r"(?:week|الأسبوع|الاسبوع)\s*(\d+)", prompt, re.IGNORECASE)
        week_num = int(w_match.group(1)) if w_match else 1

        is_arabic = bool(re.search(r"[\u0600-\u06FF]", prompt))

        def is_valid_topic(text: str) -> bool:
            if not text or len(text) < 3:
                return False
            low = text.lower()
            bad_phrases = [
                "for this course", "based on", "topics from", "curriculum for",
                "strictly and directly", "strictly reflect", "directly from", "uploaded", "evidence below", "below:",
                "expert curriculum", "design standards", "return json", "mandatory",
                "reflecting the real concepts", "extract the week title", "extract exactly",
                "الموضوعات المستهدفة", "المرفوع", "المستوعب", "تعليمات", "المخطط", "أدناه"
            ]
            return not any(bp in low for bp in bad_phrases)

        # Extract topics list from prompt if available
        topics_list = []
        top_list_match = re.search(r"(?:Target Topics|الموضوعات المستهدفة)\s*[:\-]\s*([^\n\r]+)", prompt, re.IGNORECASE)
        if top_list_match:
            raw_t_str = top_list_match.group(1).strip()
            parts = re.split(r"[,،؛;]+", raw_t_str)
            topics_list = [p.strip() for p in parts if len(p.strip()) > 2 and is_valid_topic(p.strip())]

        # Extract evidence text lines for grounded synthesis
        evidence_lines = []
        ev_matches = re.findall(r"(?:EVIDENCE CHUNK|Grounded Evidence|السياق المنهجي|سياق وثيقة المنهج)[\s\S]*?(?=\n\n[A-Z\u0600-\u06FF]{3,}|\Z)", prompt)
        for ev in ev_matches:
            for l in ev.splitlines():
                cl = re.sub(r"---.*?---|\[.*?\]|Page\d+", "", l).strip()
                if len(cl) > 15 and not cl.startswith("#") and not cl.startswith("Section:"):
                    evidence_lines.append(cl)

        # 1. Search for week header in syllabus evidence context
        arabic_week_names = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر", "الحادي عشر", "الثاني عشر"]
        ar_num_str = arabic_week_names[week_num - 1] if week_num <= len(arabic_week_names) else str(week_num)

        topic = None
        # Clean out evidence chunk markers so we match authentic syllabus text lines
        clean_prompt = re.sub(r"--- EVIDENCE CHUNK[^\n\r]*\n", "", prompt)

        patterns = [
            rf"(?:WEEK|MODULE|UNIT|CHAPTER)\s*{week_num}\s*[:\-]\s*([^\n\r]+)",
            rf"(?:الأسبوع|الاسبوع)\s*(?:{week_num}|{ar_num_str})\s*[:\-]\s*([^\n\r]+)",
            rf"(?:الوحدة|المحور|الفصل)\s*(?:{week_num}|{ar_num_str})\s*[:\-]\s*([^\n\r]+)",
        ]
        for pat in patterns:
            m = re.search(pat, clean_prompt, re.IGNORECASE)
            if m:
                cand = m.group(1).split("Topics:")[0].split("الموضوعات:")[0].split("Target Topics:")[0].split("- Lecture")[0].split("- المحاضرة")[0].split("|")[0].split("(")[0].strip()
                cand = re.sub(r"^[:\- ]+|[:\- ]+$", "", cand)
                if is_valid_topic(cand):
                    topic = cand
                    break

        # If not matched, try "Week {week_num}: ..." or "الأسبوع {week_num}: ..." with required colon
        if not topic:
            m = re.search(rf"(?:الأسبوع|الاسبوع|week)\s*{week_num}\s*[:\-]\s*([^\n\r]+)", clean_prompt, re.IGNORECASE)
            if m:
                cand = m.group(1).split("Topics:")[0].split("الموضوعات:")[0].split("Target Topics:")[0].split("- Lecture")[0].split("|")[0].strip()
                cand = re.sub(r"^[:\- ]+|[:\- ]+$", "", cand)
                if is_valid_topic(cand):
                    topic = cand

        if not topic:
            if topics_list and is_valid_topic(topics_list[0]):
                topic = topics_list[0]
            elif evidence_lines and is_valid_topic(evidence_lines[0]):
                topic = evidence_lines[0][:60]
            else:
                topic = f"الوحدة {week_num}: الأساسيات والمفاهيم الجوهرية" if is_arabic else f"Module {week_num} Core Foundations"

        # Extract specific lecture topics from syllabus evidence text if topics_list is empty
        if not topics_list:
            lt_section = re.search(r"(?:Lecture Topics|المحاضرات|موضوعات المحاضرة|مواضيع المحاضرة)[:\-]?([\s\S]*?)(?=(?:Laboratory Tasks|المختبر العملي|المهام المعملية|Citations|المراجع|MANDATORY|\Z))", clean_prompt, re.IGNORECASE)
            if lt_section:
                b_list = [b.strip() for b in re.findall(r"(?:^|\n)\s*[*•\-]\s*([^\n\r]+)", lt_section.group(1))]
                valid_b = [
                    b for b in b_list 
                    if len(b) > 8 and is_valid_topic(b) 
                    and not b.lower().startswith("lecture") 
                    and not b.startswith("المحاضر")
                    and not b.startswith("موضوعات")
                ]
                if len(valid_b) >= 2:
                    topics_list = valid_b[:3]

        if not topics_list:
            extracted_sub = []
            for ev_line in evidence_lines:
                sub_m = re.search(r"(?:Lecture\s*\d*[:\-]|المحاضرة[:\-]|[-*•]\s*)([^\n\r]+)", ev_line, re.IGNORECASE)
                if sub_m:
                    scand = sub_m.group(1).strip()
                    if is_valid_topic(scand) and 10 <= len(scand) <= 100 and not scand.lower().startswith("lecture") and not scand.startswith("المحاضر"):
                        extracted_sub.append(scand)
            if len(extracted_sub) >= 2:
                topics_list = extracted_sub[:3]
            else:
                topics_list = [
                    f"الأسس والمفاهيم المحورية لـ {topic}" if is_arabic else f"Foundational principles of {topic}",
                    f"النماذج المعمارية والمنهجية في {topic}" if is_arabic else f"Architectural models and methods in {topic}",
                    f"المعايير والتطبيقات العملية لـ {topic}" if is_arabic else f"Operational standards and application of {topic}"
                ]

        # Extract specific lab tasks from syllabus evidence if available
        syllabus_labs = []
        lab_section = re.search(r"(?:Laboratory Tasks|المختبر العملي|المهام المعملية|التطبيقات المعملية)[:\-]?([\s\S]*?)(?=(?:Citations|المراجع|MANDATORY|\Z))", clean_prompt, re.IGNORECASE)
        if lab_section:
            lb_list = [b.strip() for b in re.findall(r"(?:^|\n)\s*[*•\-]\s*([^\n\r]+)", lab_section.group(1))]
            syllabus_labs = [
                b for b in lb_list 
                if len(b) > 8 and is_valid_topic(b)
                and not b.lower().startswith("laborat")
                and not b.startswith("المختبر")
                and not b.startswith("المهام")
            ]

        # Extract citation dynamically from prompt if present
        cit_match = re.search(r"(PARENT-\d{3}|REF-[\w\-]+)", prompt)
        citation_ref = cit_match.group(1) if cit_match else "PARENT-001"

        # Detect practical domain if specified in prompt
        practical_domain = "python"
        if "sql" in prompt_lower or "database" in prompt_lower or "بيانات" in prompt:
            practical_domain = "sql"
        elif "bash" in prompt_lower or "linux" in prompt_lower or "أوامر" in prompt:
            practical_domain = "bash"
        elif "case_study" in prompt_lower or "دراسة حالة" in prompt or "تحليل" in prompt:
            practical_domain = "case_study"

        # Scenario A: Module Decomposition
        if "decompose" in prompt_lower or "curriculum designer" in prompt_lower or "تفكيك" in prompt:
            if syllabus_labs and len(syllabus_labs) >= 2:
                lab_tasks = syllabus_labs[:2]
            elif is_arabic:
                if practical_domain == "sql":
                    lab_tasks = [
                        f"تطبيق {week_num}.1: تصميم مخطط وقواعد بيانات {topic}",
                        f"تطبيق {week_num}.2: كتابة استعلامات الفحص والتحقق لـ {topic}"
                    ]
                elif practical_domain == "case_study":
                    lab_tasks = [
                        f"تطبيق {week_num}.1: تحليل دراسة الحالة لـ {topic}",
                        f"تطبيق {week_num}.2: صياغة التوصيات وحلول {topic}"
                    ]
                else:
                    lab_tasks = [
                        f"تطبيق {week_num}.1: تنفيذ مكونات وتدريبات {topic}",
                        f"تطبيق {week_num}.2: الاختبارات والتحقق التطبيقي لـ {topic}"
                    ]
            else:
                if practical_domain == "sql":
                    lab_tasks = [
                        f"Lab {week_num}.1: Schema design and DDL queries for {topic}",
                        f"Lab {week_num}.2: Analytical SQL queries and verification for {topic}"
                    ]
                elif practical_domain == "case_study":
                    lab_tasks = [
                        f"Lab {week_num}.1: Case study requirements analysis for {topic}",
                        f"Lab {week_num}.2: Solution recommendations for {topic}"
                    ]
                else:
                    lab_tasks = [
                        f"Lab {week_num}.1: Hands-on implementation of {topic} components",
                        f"Lab {week_num}.2: Automated testing and error-handling harness for {topic}"
                    ]

            if is_arabic:
                data = {
                    "title": topic,
                    "lecture_topics": topics_list if len(topics_list) >= 2 else [
                        f"المفاهيم والأسس النظرية لـ {topic}",
                        f"النماذج المعمارية والمنهجية المتبعة في {topic}",
                        f"التطبيقات العملية والمعايير المهنية في {topic}"
                    ],
                    "lab_tasks": lab_tasks
                }
            else:
                data = {
                    "title": topic,
                    "lecture_topics": topics_list if len(topics_list) >= 2 else [
                        f"Foundations and core principles of {topic}",
                        f"Architectural models and operational frameworks for {topic}",
                        f"Practical design paradigms and industry standards in {topic}"
                    ],
                    "lab_tasks": lab_tasks
                }
            raw = json.dumps(data, indent=2, ensure_ascii=False)
            return ModelResponse(raw_text=raw, parsed_json=data, model_name=self.model_name, provider="mock")

        # Scenario B: Theory Specialist Generation
        if "pedagogical" in prompt_lower or "delivery_script" in prompt_lower or "نظري" in prompt:
            t1 = topics_list[0] if topics_list else topic
            t2 = topics_list[1] if len(topics_list) > 1 else topic
            t3 = topics_list[2] if len(topics_list) > 2 else topic

            if is_arabic:
                data = {
                    "delivery_script": (
                        f"مرحباً بكم في الأسبوع {week_num}: {topic}. في هذه الجلسة، يقوم المدرب بتقديم شرح معمق "
                        f"حول {t1} وتطبيقاته الأساسية. ننتقل بعد ذلك إلى استعراض {t2}، مع التركيز على التحليل الدقيق "
                        f"وضوابط التطبيق المنهجي لـ {t3}. تم تصميم هذا المحتوى لربط المفاهيم النظرية بالتطبيقات المعتمدة في وثيقة المنهج."
                    ),
                    "discussion_prompts": [
                        f"كيف يسهم تطبيق {t1} في تعزيز موثوقية وكفاءة العمل في {topic}؟",
                        f"ما هي التحديات والمفاضلات التقنية الأكثر بروزاً عند تنفيذ {t2}؟"
                    ],
                    "trainee_reading_summary": (
                        f"ملخص القراءة للأسبوع {week_num}: يركز هذا الجزء على إتقان المفاهيم المحورية لـ {topic}، "
                        f"مع دراسة مستفيضة لـ {t1} و{t2}. يتناول الملخص القواعد التشغيلية، وأفضل الممارسات، والمعايير الواجب اتباعها لضمان جودة الأداء."
                    ),
                    "learning_outcomes": [
                        f"استيعاب المبادئ والقواعد الأساسية لـ {t1}.",
                        f"تطبيق ومقارنة النماذج العملية في {t2}.",
                        f"تحليل وتقييم مخرجات العمل المرتبطة بـ {topic} وفق معايير الجودة."
                    ]
                }
            else:
                data = {
                    "delivery_script": (
                        f"Welcome to Week {week_num}: {topic}. In this lecture session, instructors guide trainees through "
                        f"the core theoretical concepts of {t1}. We then delve into {t2}, emphasizing systematic analysis, "
                        f"operational constraints, and industry-standard workflows for {t3}. The instruction directly aligns with the syllabus."
                    ),
                    "discussion_prompts": [
                        f"How does the implementation of {t1} directly impact system reliability and efficiency in {topic}?",
                        f"What critical trade-offs arise when deploying {t2} in production settings?"
                    ],
                    "trainee_reading_summary": (
                        f"Reading summary for Week {week_num}: Covers foundational principles of {topic}, "
                        f"with comprehensive analysis of {t1} and {t2}. Emphasizes architectural guidelines, design standards, and practical verification."
                    ),
                    "learning_outcomes": [
                        f"Master foundational concepts and technical architecture of {t1}.",
                        f"Implement and evaluate operational paradigms for {t2}.",
                        f"Apply rigorous verification standards to {topic} deliverables."
                    ]
                }
            raw = json.dumps(data, indent=2, ensure_ascii=False)
            return ModelResponse(raw_text=raw, parsed_json=data, model_name=self.model_name, provider="mock")

        # Scenario C: Assessment Generation
        if "assessment" in prompt_lower or "mcq" in prompt_lower or "تقييم" in prompt:
            active_topics = topics_list if topics_list else [topic]
            if is_arabic:
                mcq_stems = [
                    f"ما هو المفهوم الجوهري الذي يرتكز عليه {active_topics[0]} ضمن مقرر {topic}؟",
                    f"أيٌّ من الخيارات التالية يمثل الوظيفة أو الغرض الأساسي لـ {active_topics[1 % len(active_topics)]}؟",
                    f"كيف يسهم تطبيق {active_topics[2 % len(active_topics)]} في تحسين الأداء وموثوقية المعالجة في {topic}؟",
                    f"ما هو المعيار الحاسم الواجب مراعاته عند تصميم وتنفيذ {active_topics[3 % len(active_topics)]}؟",
                    f"أي الممارسات التالية تضمن الاستخدام الأمثل والفعال لـ {active_topics[4 % len(active_topics)]} في بيئة العمل الحقيقية؟"
                ]
                mcq_options_pool = [
                    [f"A) الفهم المنهجي والتطبيق السليم لـ {active_topics[0]}", f"B) التنفيذ العشوائي دون تخطيط أو معايير محددة لـ {active_topics[0]}", "C) إلغاء إجراءات التحقق وضوابط الجودة المعتمدة", "D) الاعتماد الحصري على المعالجة اليدوية غير المؤتمتة"],
                    [f"A) تجاهل مواصفات ومعايير {active_topics[1 % len(active_topics)]}", f"B) تمكين المعالجة المنظمة والمتوافقة مع متطلبات {active_topics[1 % len(active_topics)]}", "C) تقليل كفاءة التشغيل وزيادة زمن الاستجابة", "D) استبدال آليات الأتمتة بالتدخل اليدوي غير الموثق"],
                    ["A) عبر زيادة التعقيد غير المبرر في النظام", "B) بتعطيل آليات التتبع وسجلات التدقيق", f"C) من خلال تحسين إدارة الموارد وتطبيق ضوابط الجودة في {active_topics[2 % len(active_topics)]}", "D) بالتخلي التام عن فحوصات السلامة والاتساق"],
                    ["A) التغاضي عن حالات الفشل والأخطاء الاستثنائية", "B) تجاوز قيود ومحددات بيئة العمل", "C) إهمال التحقق من صحة المدخلات", f"D) الالتزام بمعايير التصميم الهيكلي والتكامل المنهجي لـ {active_topics[3 % len(active_topics)]}"],
                    [f"A) التحقق المستمر واختبار المخرجات وفق مؤشرات أداء {active_topics[4 % len(active_topics)]}", "B) نشر حلول غير موثقة دون اختبارات كافية", "C) حجب سجلات المراقبة والتقارير الدورية", "D) الاستخدام العشوائي دون إرشادات محددة"]
                ]
                mcq_answers = ["A", "B", "C", "D", "A"]

                tf_statements = [
                    (f"في سياق {topic}، يعد الفهم الدقيق لـ {active_topics[0]} متطلباً أساسياً لإتقان أهداف المقرر.", True),
                    (f"يمكن تجاهل الضوابط والمعايير المنهجية عند تطبيق {active_topics[1 % len(active_topics)]} دون التأثير على كفاءة النظام.", False),
                    (f"يسهم التصميم المنظم لـ {active_topics[2 % len(active_topics)]} في رفع استقرار وموثوقية مخرجات العمل.", True),
                    (f"عند تنفيذ مهام {active_topics[3 % len(active_topics)]}، لا توجد حاجة لاختبار المخرجات أو قياس مؤشرات الأداء.", False),
                    (f"يمثل التحليل المنهجي المستمر الركيزة الأساسية للتعامل مع متطلبات {topic}.", True)
                ]

                data = {
                    "week_number": week_num,
                    "mcqs": [
                        {
                            "question_id": f"W{week_num}-MCQ-{i}",
                            "week_number": week_num,
                            "stem": mcq_stems[i - 1],
                            "options": mcq_options_pool[i - 1],
                            "correct_answer": mcq_answers[i - 1],
                            "rationale": f"التعليل المنهجي للسؤال {i} المستمد مباشرة من مفاهيم {active_topics[(i - 1) % len(active_topics)]}.",
                            "citation_ref": citation_ref
                        } for i in range(1, 6)
                    ],
                    "true_false": [
                        {
                            "question_id": f"W{week_num}-TF-{i}",
                            "week_number": week_num,
                            "statement": tf_statements[i - 1][0],
                            "is_true": tf_statements[i - 1][1],
                            "rationale": f"التعليل المنهجي لصحة أو خطأ العبارة {i} استناداً لوثيقة المنهج.",
                            "citation_ref": citation_ref
                        } for i in range(1, 6)
                    ]
                }
            else:
                mcq_stems = [
                    f"What is the foundational concept that underpins {active_topics[0]} in {topic}?",
                    f"Which of the following best captures the primary operational objective of {active_topics[1 % len(active_topics)]}?",
                    f"How does the systematic implementation of {active_topics[2 % len(active_topics)]} enhance reliability in {topic}?",
                    f"What critical engineering standard or constraint must be enforced when deploying {active_topics[3 % len(active_topics)]}?",
                    f"Which industry best practice ensures sustained quality and validation for {active_topics[4 % len(active_topics)]}?"
                ]
                mcq_options_pool = [
                    [f"A) Systematic design and structured implementation of {active_topics[0]}", f"B) Monolithic execution without modularity or bounds for {active_topics[0]}", "C) Discarding schema verification and quality controls", "D) Relying exclusively on manual ad-hoc procedures"],
                    [f"A) Bypassing operational guidelines for {active_topics[1 % len(active_topics)]}", f"B) Enabling structured, verifiable workflows compliant with {active_topics[1 % len(active_topics)]}", "C) Increasing computational latency and error rates", "D) Deprecating automated testing harness"],
                    ["A) By introducing unnecessary structural coupling", "B) By disabling telemetry and execution logging", f"C) By optimizing resource management and ensuring robust bounds in {active_topics[2 % len(active_topics)]}", "D) By omitting boundary integrity checks entirely"],
                    ["A) Overlooking runtime exceptions and silent errors", "B) Exceeding allowable production resource envelopes", "C) Suppressing validation assertions", f"D) Adhering to architectural standards and structural cohesion in {active_topics[3 % len(active_topics)]}"],
                    [f"A) Continuous automated verification and standards benchmarking for {active_topics[4 % len(active_topics)]}", "B) Releasing unverified code into production", "C) Concealing diagnostic logs and monitoring metrics", "D) Ad-hoc random modifications without testing"]
                ]
                mcq_answers = ["A", "B", "C", "D", "A"]

                tf_statements = [
                    (f"Mastery of {topic} requires thorough understanding of core theoretical and operational aspects of {active_topics[0]}.", True),
                    (f"In {active_topics[1 % len(active_topics)]}, engineering teams should ignore domain constraints and operate without validation gates.", False),
                    (f"Structured architectural design of {active_topics[2 % len(active_topics)]} directly reinforces system reliability and maintainability.", True),
                    (f"When implementing {active_topics[3 % len(active_topics)]}, performance benchmarking and error verification are unnecessary.", False),
                    (f"Systematic automated verification is essential for production deployment of {topic}.", True)
                ]

                data = {
                    "week_number": week_num,
                    "mcqs": [
                        {
                            "question_id": f"W{week_num}-MCQ-{i}",
                            "week_number": week_num,
                            "stem": mcq_stems[i - 1],
                            "options": mcq_options_pool[i - 1],
                            "correct_answer": mcq_answers[i - 1],
                            "rationale": f"Pedagogical justification for question {i} based on {active_topics[(i - 1) % len(active_topics)]}.",
                            "citation_ref": citation_ref
                        } for i in range(1, 6)
                    ],
                    "true_false": [
                        {
                            "question_id": f"W{week_num}-TF-{i}",
                            "week_number": week_num,
                            "statement": tf_statements[i - 1][0],
                            "is_true": tf_statements[i - 1][1],
                            "rationale": f"Pedagogical justification for True/False item {i} grounded in syllabus evidence.",
                            "citation_ref": citation_ref
                        } for i in range(1, 6)
                    ]
                }
            raw = json.dumps(data, indent=2, ensure_ascii=False)
            return ModelResponse(raw_text=raw, parsed_json=data, model_name=self.model_name, provider="mock")


        # Scenario D: Lab Code / Practical Task Synthesis
        if "lab" in prompt_lower or "code" in prompt_lower or "starter" in prompt_lower or "عملي" in prompt:
            safe_fn = re.sub(r"[^a-zA-Z0-9_]+", "_", topic.lower()).strip("_")
            if not safe_fn:
                safe_fn = f"module_{week_num}"

            if practical_domain == "sql":
                starter = (
                    f"-- ==========================================================\n"
                    f"-- {('المختبر العملي' if is_arabic else 'LAB EXERCISE')} {week_num}: {topic.upper()}\n"
                    f"-- {('المطلوب: تنفيذ استعلامات' if is_arabic else 'TODO: Complete SQL queries for')} {topic}\n"
                    f"-- ==========================================================\n\n"
                    f"-- TODO: 1. Write DDL statements for {safe_fn}_table\n"
                    f"-- TODO: 2. Write analytical query with filtering and aggregations\n"
                    f"SELECT 'TODO: Write Query for {topic}' AS status;\n"
                )
                solution = (
                    f"-- ==========================================================\n"
                    f"-- {('الحل المرجعي والتحقق' if is_arabic else 'INSTRUCTOR SOLUTION')} {week_num}: {topic}\n"
                    f"-- ==========================================================\n\n"
                    f"CREATE TABLE IF NOT EXISTS {safe_fn}_records (\n"
                    f"    id INTEGER PRIMARY KEY,\n"
                    f"    module_week INT NOT NULL,\n"
                    f"    status VARCHAR(50) NOT NULL\n"
                    f");\n\n"
                    f"INSERT INTO {safe_fn}_records VALUES (1, {week_num}, 'verified');\n"
                    f"SELECT COUNT(*) AS total_verified FROM {safe_fn}_records WHERE status = 'verified';\n"
                )
                has_exec = False
            elif practical_domain == "case_study":
                starter = (
                    f"==========================================================\n"
                    f"{'دراسة حالة تطبيقية وتمرين عملي' if is_arabic else 'PRACTICAL CASE STUDY & SCENARIO'} {week_num}: {topic}\n"
                    f"==========================================================\n\n"
                    f"{'المطلوب من المتدرب:' if is_arabic else 'STUDENT TASKS (TODO):'}\n"
                    f"- TODO 1: {'تحليل السيناريو وتحديد المتطلبات الأساسية' if is_arabic else 'Analyze requirements for ' + topic}.\n"
                    f"- TODO 2: {'صياغة الحل وتقديم التوصيات' if is_arabic else 'Propose architecture and workflow'}.\n"
                )
                solution = (
                    f"==========================================================\n"
                    f"{'الحل المرجعي ومعايير التقييم' if is_arabic else 'INSTRUCTOR REFERENCE MODEL SOLUTION'}: {topic}\n"
                    f"==========================================================\n\n"
                    f"{'الحل النموذجي المكتمل:' if is_arabic else 'Comprehensive Model Solution:'}\n"
                    f"1. {'تحليل المتطلبات المنهجية: استيفاء كافة الشروط ومؤشرات الأداء.' if is_arabic else 'Requirement analysis complete.'}\n"
                    f"2. {'مصفوفة الحلول المطبقة واختبار الفاعلية.' if is_arabic else 'Verified solution implementation.'}\n"
                )
                has_exec = False
            else:
                # Default Python practical
                starter = (
                    f"# ==========================================================\n"
                    f"# {('مختبر المتدرب العملي' if is_arabic else 'TRAINEE LAB')} {week_num}: {topic.upper()}\n"
                    f"# {('أكمل المهام المطلوبة أدناه' if is_arabic else 'Complete the TODO tasks below.')}\n"
                    f"# ==========================================================\n\n"
                    f"from typing import Dict, Any\n\n"
                    f"def execute_{safe_fn}_task(payload: Dict[str, Any]) -> Dict[str, Any]:\n"
                    f"    \"\"\"\n"
                    f"    {('التطبيق العملي لـ' if is_arabic else 'Practical implementation for')} {topic}.\n"
                    f"    \"\"\"\n"
                    f"    # TODO: Validate that 'request_id' is present in payload\n"
                    f"    # TODO: Implement operational logic for {topic}\n"
                    f"    raise NotImplementedError('{('يجب على المتدرب كتابة الكود' if is_arabic else 'Trainee must implement this function')}')\n"
                )
                solution = (
                    f"# ==========================================================\n"
                    f"# {('الحل النموذجي واختبارات التحقق' if is_arabic else 'INSTRUCTOR REFERENCE SOLUTION & UNIT TESTS')}\n"
                    f"# {('الوحدة الأسبوعية' if is_arabic else 'Course Module')} {week_num}: {topic}\n"
                    f"# ==========================================================\n\n"
                    f"from typing import Dict, Any\n\n"
                    f"def execute_{safe_fn}_task(payload: Dict[str, Any]) -> Dict[str, Any]:\n"
                    f"    \"\"\"\n"
                    f"    {('الحل المرجعي لـ' if is_arabic else 'Reference solution for')} {topic}.\n"
                    f"    \"\"\"\n"
                    f"    if 'request_id' not in payload:\n"
                    f"        raise ValueError('Missing request_id in payload')\n"
                    f"    return {{\n"
                    f"        'status': 'success',\n"
                    f"        'module_week': {week_num},\n"
                    f"        'topic': '{topic}',\n"
                    f"        'verified': True\n"
                    f"    }}\n\n"
                    f"# Automated Unit Test Assertions\n"
                    f"sample_payload = {{'request_id': 'REQ-{week_num}-TEST'}}\n"
                    f"res = execute_{safe_fn}_task(sample_payload)\n"
                    f"assert res['status'] == 'success', 'Status check failed'\n"
                    f"assert res['verified'] is True, 'Verification flag failed'\n"
                    f"print('Unit tests for Module {week_num} ({topic}) passed successfully!')\n"
                )
                has_exec = True

            data = {
                "week_number": week_num,
                "assignment_title": f"{('التطبيق العملي:' if is_arabic else 'Practical Implementation:')} {topic}",
                "student_starter_code": starter,
                "student_debug_challenges": [
                    f"{('التحدي 1: معالجة المدخلات غير الصحيحة لـ' if is_arabic else 'Challenge 1: Handle invalid parameter types when invoking')} {safe_fn}.",
                    f"{('التحدي 2: فحص الحالات الحدية للبيانات الفارغة في' if is_arabic else 'Challenge 2: Implement boundary check for empty payload collections in')} {topic}."
                ],
                "instructor_solution_code": solution,
                "rubrics": [
                    f"{('معيار 1 (40%): صحة التطبيق الأساسي لـ' if is_arabic else 'Rubric 1 (40%): Correct implementation of core algorithms for')} {topic}.",
                    f"{('معيار 2 (30%): معالجة الأخطاء والحالات الاستثنائية.' if is_arabic else 'Rubric 2 (30%): Resolution of edge cases and exception handling.')}",
                    f"{('معيار 3 (30%): اكتمال متطلبات الحل واجتياز التحقق.' if is_arabic else 'Rubric 3 (30%): Clean execution passing 100% of unit test assertions.')}"
                ],
                "tool_or_language": practical_domain,
                "has_executable_code": has_exec
            }
            raw = json.dumps(data, indent=2, ensure_ascii=False)
            return ModelResponse(raw_text=raw, parsed_json=data, model_name=self.model_name, provider="mock")

        # Scenario E: General Structured Content
        default_data = {
            "status": "success",
            "message": f"Synthesized structured payload for {topic}.",
            "prompt_echo": prompt[:120]
        }
        return ModelResponse(raw_text=json.dumps(default_data), parsed_json=default_data, model_name=self.model_name, provider="mock")

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        try:
            return json.loads(text)
        except Exception:
            return None
