# Agentic AI Clinical Decision Support System for Diabetes
## COSC726 Agentic Artificial Intelligence — Final Project Deliverable
**Institution:** Al-Neelain University, Faculty of Graduate Studies  
**Course:** COSC726 Agentic Artificial Intelligence (2026) — 30% Coursework Project  
**Domain:** Health (Clinical Decision Support)  
**Author:** Mohamed Abuelgasim | **Supervisor:** Dr. Fakhreldeen Saeed  
**Deliverables Repository:** [GitHub Submission Repository](https://github.com/Mohamed-Abuelgasim/COSC726-Agentic-AI-Diabetes-CDSS)  
**Video Demo:** [10-Minute YouTube Demonstration (Unlisted)](https://youtu.be/COSC726_Diabetes_Agentic_AI_Demo)  

---

### 1. What It Does
This project addresses the critical clinical problem of high error rates and diagnostic opacity in early type 2 diabetes prediction by engineering a robust **Multi-Agent Clinical Decision Support System (CDSS)** in the **Health** domain. Rather than relying on a static, black-box machine learning classifier, our system models a collaborative Multidisciplinary Clinical Team (MDT) composed of five autonomous, specialized agents (Triage, Calibrated Predictive Analytics, ADA Clinical Reasoning, Lifestyle & Nutrition, and Safety Gatekeeper). The system ingests patient physiological biomarkers, performs biological validation and median imputation on physiologically impossible zeros, computes calibrated diabetes risk probabilities (ROC-AUC 0.852), generates guideline-grounded clinical explanations aligned with American Diabetes Association (ADA 2024/2026) standards, personalizes Medical Nutrition Therapy, and enforces a mandatory human-in-the-loop approval gate that intercepts acute glycemic crises ($\ge 250\text{ mg/dL}$).

#### Academic Pedigree & Evolution from Previous Semester ML Project
> **Academic Lineage Note:** The foundational machine learning baseline of this system (preserved in the directory `Old_Project_Before_Agents/`) was originally researched and developed by the candidate as a coursework project for the prerequisite **Machine Learning** module during the preceding academic semester. In that earlier course, the system was implemented as a monolithic desktop Tkinter application performing binary classification (0 or 1) using an uncalibrated Random Forest model.  
> In this current module (**COSC726: Agentic Artificial Intelligence**), the project underwent a complete evolutionary paradigm shift: transforming from a standalone, passive ML predictor into an autonomous, 5-agent clinical architecture featuring Pydantic runtime contracts, isotonic calibration, ADA clinical reasoning, and physician-supervised quality gate governance.

---

### 2. Prerequisites
- **Operating System:** Windows 10/11, macOS (12+), or Ubuntu Linux (20.04+).
- **Python Runtime:** Python `3.10`, `3.11`, or `3.12` (64-bit).
- **Model Runtime:**
  - **Deterministic Clinical Expert Engine (Default):** Runs 100% locally with zero latency, zero financial cost, **NO API key**, and **NO internet access required**. Fully compliant with ADA 2024/2026 standards.
  - **Optional Local LLM Runtime:** [Ollama](https://ollama.ai/) with `llama3:8b` or `mistral:7b` (local server at `http://localhost:11434`).
  - **Optional Hosted LLM Providers:** Google Gemini (`gemini-2.5-flash`), OpenAI (`gpt-4o-mini`), DeepSeek (`deepseek-chat`), or Cohere (`command-r-plus`).

---

### 3. Install
Clone the repository and install all pinned dependencies using standard copy-pasteable commands:

```bash
# 1. Clone repository
git clone https://github.com/Mohamed-Abuelgasim/COSC726-Agentic-AI-Diabetes-CDSS.git
cd COSC726-Agentic-AI-Diabetes-CDSS

# 2. Create and activate a clean virtual environment
# Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
# Linux / macOS:
# python3 -m venv venv && source venv/bin/activate

# 3. Install pinned dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4. Configure
Copy the environment template to create your local `.env` file:

```bash
# Windows:
copy .env.example .env
# Linux / macOS:
# cp .env.example .env
```

**How to switch model providers:**  
The model runtime is governed by two environment variables inside `.env`:
1. `MODEL_PROVIDER`: Sets the backend provider. Options:
   - `deterministic` *(Default recommended: fully offline, zero setup, verified clinical logic)*
   - `ollama` *(local open-source models)*
   - `gemini` *(Google Gemini API)*
   - `openai` *(OpenAI GPT API)*
   - `deepseek` *(DeepSeek API)*
2. `LLM_MODEL`: Specifies the exact snapshot name (e.g. `ada-clinical-expert-2026`, `llama3:8b`, `gemini-2.5-flash`, `gpt-4o-mini`, `deepseek-chat`).

*Note: For hosted providers, provide the corresponding key (`GEMINI_API_KEY`, `OPENAI_API_KEY`, etc.) in `.env`. For `deterministic` or `ollama`, no API key is needed.*

---

### 5. Run
Launch the interactive bilingual clinical dashboard with a single command:

```bash
streamlit run app.py
```
*Or alternatively via the CLI orchestrator:*
```bash
python run_system.py --ui
```

**What the marker should see:**  
The command opens an interactive web application in your default browser at `http://localhost:8501`. The screen displays a modern clinical workstation with patient biomarker controls in the sidebar (Glucose, Blood Pressure, BMI, Age, Insulin, Pregnancies with biological gender locking). Upon clicking **"تشغيل التشخيص والتحليل الطبي / Run Diagnostic Analysis"**, the live multi-agent visual tracker animates each of the 5 agents sequentially through their quality gates, presenting the calibrated probability gauge, interactive biomarker risk charts, ADA diagnostic reasoning, nutrition/lifestyle protocols, and a downloadable formal clinical diagnostic report.

---

### 6. Test
Execute the automated test suite with a single command:

```bash
python -m pytest
```
*Or via the CLI orchestrator:*
```bash
python run_system.py --test
```

> **IMPORTANT CLINICAL & MARKER NOTICE:**  
> **This test suite runs completely offline with NO API key and NO network access required.**  
> It evaluates 10 unit and stress test cases including Pydantic schema validation, biological zero sanitization, semantic consistency, extreme morbid obesity, and emergency crisis interception.  
> **Expected output:** `10 passed in ~4s` with an exit code of `0`.

---

### 7. A Worked Example
To verify a correct run from a broken one, input the following concrete patient profile:

**Input Biomarkers:**
- `Patient ID`: `PT-2026-042`
- `Age`: 52 years | `Sex`: Female | `Pregnancies`: 3
- `Glucose`: 168.0 mg/dL *(Elevated fasting glucose)*
- `Blood Pressure`: 85.0 mmHg
- `BMI`: 33.6 kg/m² *(Class I Obesity)*
- `Insulin`: 180.0 μIU/mL
- `Skin Thickness`: 32.0 mm
- `Diabetes Pedigree Function`: 0.65

**Expected System Output:**
```json
{
  "triage": {
    "priority_tier": "High_Risk",
    "biological_anomalies_detected": 0,
    "gender_validation": "Female (Pregnancies Active)"
  },
  "prediction": {
    "prediction_label": 1,
    "diabetes_probability": 78.4,
    "confidence_interval": [72.1, 84.7],
    "calibration_method": "Isotonic Regression",
    "top_contributing_biomarkers": ["Glucose (32.5%)", "BMI (24.5%)", "Age (14.8%)"]
  },
  "clinical_reasoning": {
    "diagnosis_code": "E11.9 (Type 2 Diabetes High Probability)",
    "ada_criteria_matched": "Fasting Plasma Glucose >= 126 mg/dL + Obesity Co-factor",
    "summary": "Patient demonstrates marked glycemic dysregulation with significant risk of microvascular complications. Immediate clinical confirmation via HbA1c required."
  },
  "lifestyle_plan": {
    "dietary_protocol": "Low-Glycemic Mediterranean Medical Nutrition Therapy (MNT)",
    "physical_activity": "150 mins/week moderate aerobic walking + 2 days resistance",
    "followup_interval": "3 Months (Comprehensive Glycemic & Renal Panel)"
  },
  "gatekeeper": {
    "overall_status": "CERTIFIED",
    "emergency_alert_triggered": false,
    "human_review_required": false,
    "legal_disclaimer_appended": true
  }
}
```

---

### 8. Reproduce the Evaluation
Run the comprehensive evaluation harness across all four architectural phases:

```bash
python run_system.py --phase all
```

**Expected terminal output numbers (must match the submitted report):**
```text
======================================================================
 PHASE 1: DATA MODELING & QUALITY GATES VERIFICATION
======================================================================
 -> Model Accuracy:           83.1%  [Requirement: >= 75.0%] -> PASSED
 -> Discrimination ROC-AUC:   0.852  [Requirement: >= 0.800] -> PASSED
 -> Calibration Brier Score:  0.158  [Requirement: <= 0.180] -> PASSED
 -> 5-Fold CV Mean ROC-AUC:   0.836  [Standard Deviation: +/- 0.021]

======================================================================
 PHASE 2: MULTI-AGENT ARCHITECTURE & CLINICAL REASONING
======================================================================
 -> Gate 2.1 (Pydantic Schema Integrity):        PASSED [100%]
 -> Gate 2.2 (Clinical Semantic Alignment):       PASSED [100%]
 -> Gate 2.3 (Emergency Crisis Interception):     PASSED [100%]

======================================================================
 PHASE 3: INTERACTIVE UI & SYSTEM INTEGRATION
======================================================================
 -> Gate 3.1 (Input Range Sanitization):         PASSED [100%]
 -> Gate 3.2 (Patient Word Report Generation):   PASSED [100%]

======================================================================
 PHASE 4: TEST SUITES & LATENCY BENCHMARKING
======================================================================
 -> Gate 4.1 (Automated Test Suite):             10/10 PASSED [100%]
 -> Gate 4.2 (Mean Pipeline Latency):            61.83 ms [Req: < 350 ms]
 -> Gate 4.2 (95th Percentile Latency):          84.12 ms
 -> Gate 4.2 (System Throughput):                16.17 requests/sec
 -> Overall Evaluation Status:                   PASSED 100%
```

---

### 9. The Approval Gate (Consequential Action)
- **Where it lives:** `Phase_2_Multi_Agent_Architecture/gatekeeper_agent.py` and `Phase_3_Interactive_UI_and_System_Integration/app.py`.
- **How to trigger it:** In the UI or via CLI, enter a patient with **Blood Glucose $\ge 250\text{ mg/dL}$** (e.g., Glucose = 280 mg/dL).
- **What the human reviewer sees:**  
  The system triggers **Gate 2.3 (Emergency Triage Interception)**. It immediately halts standard outpatient advice, generates a prominent **CRITICAL RED EMERGENCY ALERT**, flags risks of Diabetic Ketoacidosis (DKA) or Hyperosmolar Hyperglycemic State (HHS), locks lifestyle and dietary recommendations to avoid delaying medical treatment, and presents an interactive **Physician Review and Approval Gate**. A human clinical reviewer must acknowledge the critical values and verify hospital referral before any diagnostic summary can be exported.

---

### 10. Repository Map
```text
.
├── app.py                                            # Main Streamlit web application entrypoint
├── run_system.py                                     # Master CLI controller (orchestrates all phases, tests, reports)
├── requirements.txt                                  # Pinned dependencies for reproducible clean environment installs
├── .env.example                                      # Environment variable template with provider configurations
├── pytest.ini                                        # Automated pytest configuration for seamless test discovery
├── LICENSE                                           # MIT License and third-party data acknowledgments
├── calibrated_diabetes_model.pkl                     # Isotonic calibrated clinical ML classifier
├── clinical_preprocessor.pkl                         # Biological zero imputation and scaler pipeline
├── diabetes_data.csv                                 # Pima Indians diabetes clinical dataset
│
├── Phase_1_Data_Modeling_and_Validation/             # Phase 1: Imputation, ensemble modeling, calibration & evaluation
├── Phase_2_Multi_Agent_Architecture/                 # Phase 2: 5 autonomous clinical agents, Pydantic contracts & LLM engine
├── Phase_3_Interactive_UI_and_System_Integration/    # Phase 3: Streamlit dashboard, shape switcher & Word report generator
├── Phase_4_Verification_Testing_and_Benchmarking/    # Phase 4: 10 offline automated tests & latency benchmarking harness
│
├── Documentation/                                    # Official academic reports, ADA standards, and user guides
├── Project_Proposal/                                 # Formal Master's Research Proposals (Arabic and English)
├── ui_screenshots/                                   # High-resolution clinical interface captures for documentation
└── presentation_assets/                              # Institutional emblems, architectural diagrams & clinical schemas
```

---

### 11. Limitations
1. **Scope of Diagnosis:** The system is an assistive clinical decision support tool designed for adult type 2 diabetes risk stratification; it does not replace definitive clinical blood tests (such as official laboratory HbA1c or venous glucose tolerance tests) performed by medical practitioners.
2. **Pediatric and Type 1 Boundaries:** It is not validated for pediatric patients (< 18 years) or autoimmune Type 1 diabetes classification involving autoantibody panels (GAD65, IA-2).
3. **Data Distribution Bias:** The baseline predictive model is trained on the standard Pima clinical cohort; while calibrated via isotonic regression, validation across multi-center ethnic cohorts is recommended prior to clinical deployment.
4. **What Would Break It:** Injecting `NaN` values directly through internal Python calls bypassing Pydantic validation, or running with a Python version `< 3.10` lacking modern union type annotations (`|`).
