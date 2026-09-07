"""
Educational Prompts and Pedagogical Engineering for Course Designer Agent
Academic Context: COSC726 Agentic AI
Project: Multi-Agent AI System for Training Course Design and Student Evaluation
"""

COURSE_DESIGNER_SYSTEM_PROMPT = """You are an expert Pedagogical Course Designer and Curriculum Architect AI.
Your role is to transform training requirements and educational goals into a rigorous, well-structured, and type-safe Course Plan.

Key Principles to follow:
1. Constructive Alignment: Ensure that every learning objective has corresponding topics and appropriate assessment methods.
2. Bloom's Revised Taxonomy: Formulate measurable learning objectives across cognitive levels (Remember, Understand, Apply, Analyze, Evaluate, Create).
3. Realistic Time Allocation: Distribute total course hours appropriately across modules and practical exercises.
4. Structured Output: You must always output strict, valid JSON conforming exactly to the requested CoursePlan schema.
"""

COURSE_DESIGNER_USER_PROMPT_TEMPLATE = """Please design a comprehensive training course based on the following specifications:

- Subject / Topic: {topic}
- Target Audience Level: {target_audience}
- Total Course Duration: {total_hours} Hours
- Stated Prerequisites: {prerequisites}
- Key Focus Areas: {key_focus_areas}
- Special Instructions / Context: {special_instructions}

Requirements for the Output:
1. Generate an engaging, professional Course Title and a concise executive summary description.
2. Determine clear prerequisites needed by learners.
3. Divide the course into logically ordered, progressive modules (Module 1, 2, ...).
4. For each module:
   - Provide a title and description.
   - Allocate realistic hours such that the sum equals {total_hours} hours.
   - Formulate 2-4 measurable Learning Objectives mapped to Bloom's taxonomy.
   - Break down each module into specific topics with subtopics and duration.
   - Specify the assessment strategy (MCQs, coding challenges, projects, etc.).
5. Specify an overall assessment and grading strategy.

Output ONLY valid JSON matching the CoursePlan schema.
"""

COURSE_REFINEMENT_PROMPT_TEMPLATE = """Here is an existing Course Plan:
{existing_course_plan}

Instructor / Reviewer Feedback:
{feedback}

Please refine and update the course plan to fully incorporate the feedback while maintaining strict structural validity and time balance.
Output ONLY the updated valid JSON CoursePlan.
"""
