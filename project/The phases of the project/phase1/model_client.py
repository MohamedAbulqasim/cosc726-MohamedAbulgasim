"""
Model Client Abstraction for Agentic Course Design
Supports deterministic offline generation and live LLM APIs.
Academic Context: COSC726 Agentic AI
Project: Multi-Agent AI System for Training Course Design and Student Evaluation
"""

import os
import json
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from .schemas import (
    CoursePlan,
    CourseRequirements,
    CourseModule,
    LearningObjective,
    ModuleTopic,
    AssessmentStrategy,
    AssessmentMethod,
    BloomTaxonomyLevel,
    TargetAudienceLevel,
)
from .prompts import COURSE_DESIGNER_SYSTEM_PROMPT, COURSE_DESIGNER_USER_PROMPT_TEMPLATE


class BaseModelClient(ABC):
    """Abstract interface for LLM model clients."""

    @abstractmethod
    def generate_course_plan(self, requirements: CourseRequirements) -> CoursePlan:
        """Generate a complete CoursePlan from requirements."""
        pass

    @abstractmethod
    def refine_course_plan(self, existing_plan: CoursePlan, feedback: str) -> CoursePlan:
        """Refine an existing CoursePlan based on feedback."""
        pass


class DeterministicCourseModelClient(BaseModelClient):
    """
    Intelligent Model Client supporting both Live LLM APIs (Gemini, OpenAI, DeepSeek, Ollama)
    and High-Fidelity Level-Aware Offline Generation.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        self.llm_client = llm_client
        if self.llm_client is None:
            try:
                from common.llm_client import UniversalLLMClient
                self.llm_client = UniversalLLMClient()
            except Exception:
                self.llm_client = None

    def generate_course_plan(self, requirements: CourseRequirements) -> CoursePlan:
        topic_clean = requirements.topic.strip()
        total_hours = float(requirements.total_hours)
        level = requirements.target_audience
        num_modules = max(3, min(6, int(round(total_hours / 6.0))))
        hours_per_module = round(total_hours / num_modules, 1)

        # 1. Attempt Live LLM Generation if available
        if self.llm_client and hasattr(self.llm_client, "is_live_llm_available") and self.llm_client.is_live_llm_available():
            try:
                sys_prompt = "You are a Senior Principal Curriculum Architect and AI Pedagogical Engine. Design a structured, accredited training curriculum adhering to Bloom's Taxonomy. Output strictly valid JSON."
                user_prompt = f"""
Design a complete educational curriculum for:
- Course Topic: {topic_clean}
- Target Audience Level: {level.value} (Ensure depth, complexity, and prerequisites strictly match this level)
- Total Duration: {total_hours} Hours
- Number of Modules: {num_modules}

Return JSON conforming exactly to this structure:
{{
  "course_title": "{topic_clean}: Comprehensive Training & Mastery Program",
  "short_description": "A comprehensive {total_hours}-hour curriculum for {level.value} learners...",
  "prerequisites": ["...", "..."],
  "modules": [
    {{
      "module_number": 1,
      "title": "Module Title",
      "description": "Module Overview",
      "allocated_hours": {hours_per_module},
      "learning_objectives": [
        {{"objective_id": "LO-1.1", "description": "...", "bloom_level": "Understand"}},
        {{"objective_id": "LO-1.2", "description": "...", "bloom_level": "Apply"}},
        {{"objective_id": "LO-1.3", "description": "...", "bloom_level": "Analyze"}}
      ],
      "topics": [
        {{"topic_id": "TOPIC-1.1", "title": "Topic 1", "description": "...", "allocated_hours": 2.0, "subtopics": ["Subtopic A", "Subtopic B"]}}
      ]
    }}
  ]
}}
"""
                llm_json = self.llm_client.generate_json_response(user_prompt, sys_prompt)
                if llm_json and "modules" in llm_json:
                    parsed_modules = []
                    for m_idx, m_data in enumerate(llm_json.get("modules", []), start=1):
                        los = []
                        for l_idx, l_data in enumerate(m_data.get("learning_objectives", []), start=1):
                            b_str = l_data.get("bloom_level", "Understand").capitalize()
                            b_enum = BloomTaxonomyLevel(b_str) if b_str in [e.value for e in BloomTaxonomyLevel] else BloomTaxonomyLevel.UNDERSTAND
                            los.append(LearningObjective(
                                objective_id=l_data.get("objective_id", f"LO-{m_idx}.{l_idx}"),
                                description=l_data.get("description", "Core concept"),
                                bloom_level=b_enum,
                                keywords=[topic_clean.lower()]
                            ))
                        
                        top_list = []
                        for t_idx, t_data in enumerate(m_data.get("topics", []), start=1):
                            top_list.append(ModuleTopic(
                                topic_id=t_data.get("topic_id", f"TOPIC-{m_idx}.{t_idx}"),
                                title=t_data.get("title", f"Topic {t_idx}"),
                                description=t_data.get("description", "Detailed lecture topic"),
                                allocated_hours=float(t_data.get("allocated_hours", 2.0)),
                                subtopics=t_data.get("subtopics", ["Key Concepts", "Hands-on Practice"])
                            ))
                        if not top_list:
                            top_list = [ModuleTopic(topic_id=f"TOPIC-{m_idx}.1", title=m_data.get("title", "Topic"), description="Overview", allocated_hours=hours_per_module, subtopics=["Core Principles"])]

                        parsed_modules.append(CourseModule(
                            module_id=f"MOD-{m_idx:02d}",
                            module_number=m_idx,
                            title=m_data.get("title", f"Module {m_idx}"),
                            description=m_data.get("description", "Module description"),
                            allocated_hours=float(m_data.get("allocated_hours", hours_per_module)),
                            learning_objectives=los,
                            topics=top_list
                        ))

                    if parsed_modules:
                        course_id = f"CRS-{re.sub(r'[^A-Za-z0-9]', '', topic_clean).upper()[:6]}-{int(total_hours)}H"
                        assessment = AssessmentStrategy(
                            methods=[AssessmentMethod.QUIZ_MCQ, AssessmentMethod.CODING_CHALLENGE, AssessmentMethod.CAPSTONE_PROJECT],
                            passing_grade_percentage=70.0,
                            weight_percentage=100.0,
                            description="Continuous assessment with 30% weekly quizzes, 40% practical labs, and 30% capstone project."
                        )
                        return CoursePlan(
                            course_id=course_id,
                            course_title=llm_json.get("course_title", f"{topic_clean}: Comprehensive Training & Mastery Program"),
                            short_description=llm_json.get("short_description", f"Intensive {total_hours}h course for {level.value} learners."),
                            target_audience=level,
                            total_hours=total_hours,
                            prerequisites=llm_json.get("prerequisites", ["Basic computer literacy"]),
                            modules=parsed_modules,
                            overall_assessment_strategy=assessment,
                            metadata={"generator_engine": "UniversalLLMClient", "mode": "live_llm"}
                        )
            except Exception as e:
                print(f"[Phase 1] Live LLM curriculum generation error: {e}. Falling back to dynamic offline generator.")

        # 2. Dynamic Level-Aware Generator
        modules = self._build_dynamic_modules(topic_clean, level, num_modules, hours_per_module, requirements.key_focus_areas)
        allocated_so_far = sum(m.allocated_hours for m in modules[:-1])
        modules[-1].allocated_hours = round(total_hours - allocated_so_far, 1)

        prereqs = list(requirements.prerequisites) if requirements.prerequisites else [
            "Basic computer literacy",
            "Familiarity with foundational programming logic" if level != TargetAudienceLevel.BEGINNER else "No prior experience required"
        ]

        course_id = f"CRS-{re.sub(r'[^A-Za-z0-9]', '', topic_clean).upper()[:6]}-{int(total_hours)}H"
        assessment = AssessmentStrategy(
            methods=[AssessmentMethod.QUIZ_MCQ, AssessmentMethod.CODING_CHALLENGE, AssessmentMethod.CAPSTONE_PROJECT],
            passing_grade_percentage=70.0,
            weight_percentage=100.0,
            description="Continuous assessment with 30% weekly quizzes, 40% practical labs, and 30% capstone project."
        )

        return CoursePlan(
            course_id=course_id,
            course_title=f"{topic_clean}: Comprehensive Training & Mastery Program",
            short_description=(
                f"An intensive, hands-on {total_hours}-hour curriculum designed for {level.value} learners "
                f"focusing on mastery of {topic_clean} principles, real-world development, and objective-based evaluation."
            ),
            target_audience=level,
            total_hours=total_hours,
            prerequisites=prereqs,
            modules=modules,
            overall_assessment_strategy=assessment,
            metadata={
                "generator_engine": "DeterministicCourseModelClient",
                "mode": "deterministic_offline",
                "focus_areas": requirements.key_focus_areas,
                "special_instructions": requirements.special_instructions,
            }
        )

    def _build_dynamic_modules(
        self, topic: str, level: TargetAudienceLevel, count: int, hours_per_mod: float, focus_areas: list[str]
    ) -> list[CourseModule]:
        """Dynamically crafts domain-aligned modules with rigorous Bloom taxonomy objectives."""
        t_lower = topic.lower()

        if "html" in t_lower or "css" in t_lower or "web design" in t_lower or "frontend" in t_lower:
            domain_stages = [
                ("HTML5 Document Structure, Head/Body & Core Tags", BloomTaxonomyLevel.UNDERSTAND, ["Document Structure & DOCTYPE", "Headings & Paragraphs", "Links (<a>) & Images (<img>)"]),
                ("Semantic HTML5 Elements, Lists & Tables", BloomTaxonomyLevel.APPLY, ["Semantic Tags (header/nav/footer)", "Ordered & Unordered Lists", "Tables & Data Representation"]),
                ("HTML Forms, Input Types & Validation", BloomTaxonomyLevel.APPLY, ["Form Elements & Actions", "Input Types & Placeholders", "Client-Side Form Validation"]),
                ("CSS3 Fundamentals, Selectors & Box Model", BloomTaxonomyLevel.APPLY, ["CSS Syntax & Selectors", "Box Model (Margin/Padding/Border)", "Colors & Typography"]),
                ("Modern CSS Layouts: Flexbox & Grid Systems", BloomTaxonomyLevel.ANALYZE, ["Flex Container & Alignment", "CSS Grid Columns & Rows", "Responsive Media Queries"]),
                ("HTML5 Multimedia, Accessibility (a11y) & SEO", BloomTaxonomyLevel.CREATE, ["Audio/Video Integration", "Web Accessibility & ARIA", "SEO & Meta Tags"]),
            ]
        elif "c++" in t_lower or "cpp" in t_lower:
            domain_stages = [
                ("C++ Syntax, Compilers, Variables & I/O", BloomTaxonomyLevel.UNDERSTAND, ["g++/Clang Toolchain", "Variables & Types", "cin/cout Streams"]),
                ("Control Flow, Conditionals & Loops", BloomTaxonomyLevel.APPLY, ["if/else & switch", "for & while Loops", "Break & Continue"]),
                ("Functions, Scope & Pass-by-Reference", BloomTaxonomyLevel.APPLY, ["Function Declarations", "Pass-by-Reference (&)", "Function Overloading"]),
                ("Arrays, Pointers & Memory Management", BloomTaxonomyLevel.ANALYZE, ["Pointers & Address-Of", "Dynamic Memory (new/delete)", "std::vector"]),
                ("Object-Oriented Programming (OOP) in C++", BloomTaxonomyLevel.CREATE, ["Classes & Objects", "Constructors & Destructors", "Encapsulation & Access Modifiers"]),
                ("Inheritance, Polymorphism & Modern C++", BloomTaxonomyLevel.CREATE, ["Inheritance & Virtual Functions", "STL Containers", "Best Practices"]),
            ]
        elif "python" in t_lower:
            domain_stages = [
                ("Python Foundations & Data Types", BloomTaxonomyLevel.UNDERSTAND, ["Python Syntax", "Lists, Tuples & Dicts", "Virtual Environments"]),
                ("Control Structures, Loops & Functions", BloomTaxonomyLevel.APPLY, ["Conditionals & Loops", "Functions & Lambdas", "Modules & Imports"]),
                ("Object-Oriented Python & Type Hints", BloomTaxonomyLevel.APPLY, ["Classes & Methods", "Type Annotations", "Pydantic Schemas"]),
                ("File I/O, Error Handling & Logging", BloomTaxonomyLevel.ANALYZE, ["Exception Handling", "File Operations", "Structured Logging"]),
                ("Data Processing & Third-Party Packages", BloomTaxonomyLevel.CREATE, ["Data Manipulation", "API Requests", "Testing with Pytest"]),
                ("Advanced Python & Asynchronous Logic", BloomTaxonomyLevel.CREATE, ["Async/Await", "Decorators & Generators", "Architecture"]),
            ]
        elif "java" in t_lower:
            domain_stages = [
                ("Java Syntax, JVM & Core Data Types", BloomTaxonomyLevel.UNDERSTAND, ["JVM & Compilation", "Primitives & Strings", "I/O Scanner"]),
                ("Control Flow, Loops & Arrays", BloomTaxonomyLevel.APPLY, ["Conditionals & Switches", "Looping Constructs", "Arrays & Collections"]),
                ("Object-Oriented Design in Java", BloomTaxonomyLevel.APPLY, ["Classes & Objects", "Constructors & This", "Encapsulation"]),
                ("Inheritance, Interfaces & Polymorphism", BloomTaxonomyLevel.ANALYZE, ["Abstract Classes", "Interfaces", "Polymorphism"]),
                ("Exception Handling & Collections Framework", BloomTaxonomyLevel.CREATE, ["Try-Catch-Finally", "ArrayList & HashMap", "Generics"]),
                ("Java Streams, Concurrency & Modern APIs", BloomTaxonomyLevel.CREATE, ["Lambdas & Streams", "Multithreading", "Spring Basics"]),
            ]
        elif "web" in t_lower or "javascript" in t_lower or "html" in t_lower:
            domain_stages = [
                ("Web Foundations: HTML5, CSS3 & Layouts", BloomTaxonomyLevel.UNDERSTAND, ["Semantic HTML", "CSS Flexbox/Grid", "Responsive Design"]),
                ("JavaScript Fundamentals & DOM Manipulation", BloomTaxonomyLevel.APPLY, ["JS Syntax & Variables", "DOM Events", "Functions & Scope"]),
                ("Modern JavaScript (ES6+) & Async Programming", BloomTaxonomyLevel.APPLY, ["Promises & Fetch API", "Async/Await", "Modules"]),
                ("Frontend Frameworks & Component Architecture", BloomTaxonomyLevel.ANALYZE, ["State Management", "Component Lifecycle", "Routing"]),
                ("Backend APIs & Database Integration", BloomTaxonomyLevel.CREATE, ["RESTful Endpoints", "JSON Data Flow", "Authentication"]),
                ("Fullstack Deployment & Performance", BloomTaxonomyLevel.CREATE, ["Build Tools", "Cloud Deployment", "Security Best Practices"]),
            ]
        elif "database" in t_lower or "sql" in t_lower:
            domain_stages = [
                ("Relational Database Concepts & SQL Basics", BloomTaxonomyLevel.UNDERSTAND, ["RDBMS Architecture", "SELECT, INSERT, UPDATE", "Data Types"]),
                ("Joins, Aggregations & Complex Queries", BloomTaxonomyLevel.APPLY, ["INNER/LEFT Joins", "GROUP BY & HAVING", "Subqueries"]),
                ("Database Schema Design & Normalization", BloomTaxonomyLevel.APPLY, ["1NF, 2NF, 3NF", "Primary & Foreign Keys", "Constraints"]),
                ("Indexing, Optimization & Transactions", BloomTaxonomyLevel.ANALYZE, ["B-Tree Indexes", "ACID Properties", "Query Execution Plans"]),
                ("Stored Procedures, Views & Triggers", BloomTaxonomyLevel.CREATE, ["Stored Procedures", "Triggers", "Views & Security"]),
                ("Modern Databases: NoSQL & Distributed DBs", BloomTaxonomyLevel.CREATE, ["Document Stores", "Scalability", "Backup & Recovery"]),
            ]
        else:
            domain_stages = [
                (f"{topic} Foundations & Core Principles", BloomTaxonomyLevel.UNDERSTAND, ["Core Concepts", "Environment Setup", "Architecture"]),
                (f"{topic} Fundamental Techniques & Syntax", BloomTaxonomyLevel.APPLY, ["Data Structures", "Control Flow", "Key Operations"]),
                (f"{topic} Advanced Implementation & Patterns", BloomTaxonomyLevel.ANALYZE, ["Design Patterns", "Optimization", "Integration"]),
                (f"{topic} System Architecture & Scalability", BloomTaxonomyLevel.EVALUATE, ["Performance Tuning", "Security", "Best Practices"]),
                (f"{topic} Practical Capstone & Deployment", BloomTaxonomyLevel.CREATE, ["Project Implementation", "Testing", "Deployment"]),
                (f"{topic} Specialized Topics & Future Trends", BloomTaxonomyLevel.CREATE, ["Emerging Frameworks", "Case Studies", "Future Directions"]),
            ]

        modules: list[CourseModule] = []
        
        for i in range(count):
            stage_idx = min(i, len(domain_stages) - 1)
            stage_name, bloom_lvl, subpoints = domain_stages[stage_idx]
            
            extra_topic = focus_areas[i] if i < len(focus_areas) else f"Practical Applications in {subpoints[0]}"
            
            mod_num = i + 1
            mod_id = f"MOD-{mod_num:02d}"
            mod_title = f"{stage_name}"
            mod_desc = f"Comprehensive study of {stage_name.lower()} specifically tailored to {topic} at the {level.value} level."
            
            # Learning objectives
            los = [
                LearningObjective(
                    objective_id=f"LO-{mod_num}.1",
                    description=f"{bloom_lvl.value} the core principles and syntax mechanisms of {subpoints[0]} in {topic}.",
                    bloom_level=bloom_lvl,
                    keywords=[topic.lower(), subpoints[0].lower(), "fundamentals"]
                ),
                LearningObjective(
                    objective_id=f"LO-{mod_num}.2",
                    description=f"Apply standard industry techniques to construct and debug {topic} solutions involving {subpoints[1]}.",
                    bloom_level=BloomTaxonomyLevel.APPLY if bloom_lvl == BloomTaxonomyLevel.UNDERSTAND else bloom_lvl,
                    keywords=[topic.lower(), subpoints[1].lower(), "hands-on"]
                ),
                LearningObjective(
                    objective_id=f"LO-{mod_num}.3",
                    description=f"Evaluate best practices and solve problem scenarios relating to {subpoints[2]} in {topic}.",
                    bloom_level=BloomTaxonomyLevel.ANALYZE if bloom_lvl in [BloomTaxonomyLevel.UNDERSTAND, BloomTaxonomyLevel.APPLY] else BloomTaxonomyLevel.CREATE,
                    keywords=[topic.lower(), subpoints[2].lower(), "advanced"]
                ),
            ]

            # Topics
            t_hours = round(hours_per_mod / 2.0, 1)
            topics = [
                ModuleTopic(
                    topic_id=f"TOPIC-{mod_num}.1",
                    title=f"{subpoints[0]} & {subpoints[1]}",
                    description=f"In-depth explanation and core technical concepts for {subpoints[0]} and {subpoints[1]} in {topic}.",
                    subtopics=[f"Intro to {subpoints[0]}", f"Syntax and rules for {subpoints[1]}", "Common pitfalls"],
                    allocated_hours=t_hours
                ),
                ModuleTopic(
                    topic_id=f"TOPIC-{mod_num}.2",
                    title=f"Practical Hands-on: {subpoints[2]}",
                    description=f"Hands-on exercises and coding sessions focusing on {subpoints[2]} in {topic}.",
                    subtopics=[f"Step-by-step code implementation", f"Debugging and validation", "Practical exercises"],
                    allocated_hours=round(hours_per_mod - t_hours, 1)
                )
            ]

            modules.append(CourseModule(
                module_id=mod_id,
                module_number=mod_num,
                title=mod_title,
                description=mod_desc,
                allocated_hours=hours_per_mod,
                learning_objectives=los,
                topics=topics,
                assessment_strategy=AssessmentStrategy(
                    methods=[AssessmentMethod.QUIZ_MCQ, AssessmentMethod.CODING_CHALLENGE],
                    passing_grade_percentage=65.0,
                    weight_percentage=round(100.0 / count, 1),
                    description=f"Module {mod_num} assessment comprising practical exercises and concept check."
                )
            ))

        return modules

    def refine_course_plan(self, existing_plan: CoursePlan, feedback: str) -> CoursePlan:
        updated = existing_plan.model_copy(deep=True)
        updated.metadata["latest_feedback"] = feedback
        updated.metadata["refined_at"] = "Refined based on instructor feedback"
        
        # Add feedback to description or adjust
        if "prerequisite" in feedback.lower():
            updated.prerequisites.append(f"Additional requirement: {feedback}")
        
        return updated


class OpenAIModelClient(BaseModelClient):
    """
    OpenAI-compatible client with strict structured output decoding.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable.")
        
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)

    def generate_course_plan(self, requirements: CourseRequirements) -> CoursePlan:
        prompt = COURSE_DESIGNER_USER_PROMPT_TEMPLATE.format(
            topic=requirements.topic,
            target_audience=requirements.target_audience.value,
            total_hours=requirements.total_hours,
            prerequisites=", ".join(requirements.prerequisites) if requirements.prerequisites else "None",
            key_focus_areas=", ".join(requirements.key_focus_areas) if requirements.key_focus_areas else "Standard core areas",
            special_instructions=requirements.special_instructions or "None"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": COURSE_DESIGNER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return CoursePlan.model_validate(data)

    def refine_course_plan(self, existing_plan: CoursePlan, feedback: str) -> CoursePlan:
        from .prompts import COURSE_REFINEMENT_PROMPT_TEMPLATE
        prompt = COURSE_REFINEMENT_PROMPT_TEMPLATE.format(
            existing_course_plan=existing_plan.model_dump_json(indent=2),
            feedback=feedback
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": COURSE_DESIGNER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return CoursePlan.model_validate(data)


class ModelClientFactory:
    """Factory to instantiate the appropriate ModelClient."""

    @staticmethod
    def create_client(force_deterministic: bool = False, model_name: str = "gpt-4o") -> BaseModelClient:
        if force_deterministic or not os.getenv("OPENAI_API_KEY"):
            return DeterministicCourseModelClient()
        try:
            return OpenAIModelClient(model=model_name)
        except Exception:
            return DeterministicCourseModelClient()
