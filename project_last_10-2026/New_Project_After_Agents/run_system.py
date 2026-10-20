"""
Root System Launcher & CLI Controller:
Neelain University Master's Project: Multi-Agent Clinical AI for Diabetes Prediction.
Author: Mohamed Abolgasim | Supervisor: Dr. Fakhreldeen Saeed.

Usage:
  python run_system.py --ui                      # Launches interactive Streamlit web dashboard
  python run_system.py --phase 1                 # Runs Phase 1 Validation & Modeling
  python run_system.py --phase 2                 # Runs Phase 2 Multi-Agent Architecture Validation
  python run_system.py --phase 3                 # Runs Phase 3 UI & Report Generator Validation
  python run_system.py --phase 4                 # Runs Phase 4 Verification & Test Suites
  python run_system.py --phase all               # Runs all phases sequentially
  python run_system.py --generate-all-reports    # Compiles all 6 Word proposals and reports
"""

import os
import sys
import subprocess
import argparse

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

PHASES = {
    '1': {
        'name': 'Phase 1: Data Modeling & Quality Gates',
        'dir': os.path.join(ROOT_DIR, 'Phase_1_Data_Modeling_and_Validation'),
        'validator': 'run_phase1_validation.py',
        'report_gen': 'generate_phase1_report.py',
        'report_file': 'Phase_1_Report_Bilingual.docx'
    },
    '2': {
        'name': 'Phase 2: Multi-Agent Architecture & LLM Reasoning',
        'dir': os.path.join(ROOT_DIR, 'Phase_2_Multi_Agent_Architecture'),
        'validator': 'run_phase2_validation.py',
        'report_gen': 'generate_phase2_report.py',
        'report_file': 'Phase_2_Report_Bilingual.docx'
    },
    '3': {
        'name': 'Phase 3: Interactive UI & System Integration',
        'dir': os.path.join(ROOT_DIR, 'Phase_3_Interactive_UI_and_System_Integration'),
        'validator': 'run_phase3_validation.py',
        'report_gen': 'generate_phase3_report.py',
        'report_file': 'Phase_3_Report_Bilingual.docx'
    },
    '4': {
        'name': 'Phase 4: Verification Testing & Benchmarking',
        'dir': os.path.join(ROOT_DIR, 'Phase_4_Verification_Testing_and_Benchmarking'),
        'validator': 'run_phase4_verification.py',
        'report_gen': 'generate_phase4_report.py',
        'report_file': 'Phase_4_Report_Bilingual.docx'
    }
}

def run_phase(phase_id: str):
    p_info = PHASES.get(phase_id)
    if not p_info:
        print(f"Unknown phase: {phase_id}")
        return False

    print("\n" + "=" * 70)
    print(f" EXECUTING {p_info['name']}")
    print("=" * 70)

    val_script = os.path.join(p_info['dir'], p_info['validator'])
    res = subprocess.run([sys.executable, val_script], cwd=p_info['dir'])
    return res.returncode == 0

def generate_proposals():
    print("\n[PROPOSALS] Generating Academic Master's Project Proposals (Arabic & English)...")
    prop_script = os.path.join(ROOT_DIR, 'Project_Proposal', 'generate_proposals.py')
    res = subprocess.run([sys.executable, prop_script], cwd=os.path.join(ROOT_DIR, 'Project_Proposal'))
    return res.returncode == 0

def generate_all_reports():
    print("\n" + "=" * 70)
    print(" GENERATING ALL ACADEMIC WORD REPORTS AND PROPOSALS (.DOCX)")
    print("=" * 70)

    # 1. Proposals
    generate_proposals()

    # 2. Phase Reports
    for pid, p_info in PHASES.items():
        print(f"\n[{p_info['name']}] Generating Bilingual Report...")
        gen_script = os.path.join(p_info['dir'], p_info['report_gen'])
        subprocess.run([sys.executable, gen_script], cwd=p_info['dir'])

    # 3. Walkthrough and Operations Guides
    print("\n[DOCUMENTATION] Generating Walkthrough & Project Guide Word Documents (AR & EN)...")
    docs_script = os.path.join(ROOT_DIR, 'generate_guides_and_walkthrough_docx.py')
    subprocess.run([sys.executable, docs_script], cwd=ROOT_DIR)

    # 4. Illustrated User Guides (with App Screenshots and Tab Explanations)
    print("\n[ILLUSTRATED GUIDES] Generating Comprehensive Illustrated User Guides (AR & EN)...")
    illus_script = os.path.join(ROOT_DIR, 'build_illustrated_guides.py')
    subprocess.run([sys.executable, illus_script], cwd=ROOT_DIR)

    # 5. ADA Standards of Care 2024 / 2026 Reference Reports
    print("\n[ADA STANDARDS] Generating ADA Standards of Care 2024 / 2026 Word Reports (AR & EN)...")
    ada_script = os.path.join(ROOT_DIR, 'Documentation', 'generate_ada_report.py')
    subprocess.run([sys.executable, ada_script], cwd=os.path.join(ROOT_DIR, 'Documentation'))

    print("\n" + "=" * 70)
    print(" [COMPLETED] All Word documents, guides, and ADA reports successfully compiled!")
    print("=" * 70)

def launch_ui():
    print("\n[LAUNCHING UI] Starting Streamlit Interactive Application...")
    app_script = os.path.join(ROOT_DIR, "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_script])

def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Diabetes Clinical Decision System Controller")
    parser.add_argument('--phase', choices=['1', '2', '3', '4', 'all'], help="Run specific phase validation")
    parser.add_argument('--ui', action='store_true', help="Launch interactive Streamlit UI")
    parser.add_argument('--generate-all-reports', action='store_true', help="Compile all Word documents (.docx)")
    parser.add_argument('--ada-report', action='store_true', help="Generate ADA Standards of Care 2024/2026 reports (AR & EN)")
    parser.add_argument('--test', action='store_true', help="Run automated test suite (10/10 offline tests, NO API key or network required)")
    parser.add_argument('--presentation', nargs='?', const='all', choices=['all', 'ar', 'en'],
                        help="Generate Master's PowerPoint presentation (.pptx): 'all' (both), 'ar' (Arabic), or 'en' (English)")

    args = parser.parse_args()

    if args.presentation:
        mode = args.presentation
        print("\n" + "=" * 70)
        print(" GENERATING MASTER'S POWERPOINT PRESENTATION (.PPTX)")
        print("=" * 70)
        if mode in ('all', 'ar'):
            print("\n[PRESENTATION AR] Generating Arabic PowerPoint Presentation...")
            pres_script_ar = os.path.join(ROOT_DIR, "generate_presentation_after_agents.py")
            subprocess.run([sys.executable, pres_script_ar], cwd=ROOT_DIR)
        if mode in ('all', 'en'):
            print("\n[PRESENTATION EN] Generating English PowerPoint Presentation...")
            pres_script_en = os.path.join(ROOT_DIR, "generate_presentation_after_agents_english.py")
            subprocess.run([sys.executable, pres_script_en], cwd=ROOT_DIR)
    elif args.generate_all_reports:
        generate_all_reports()
    elif args.ada_report:
        print("\n" + "=" * 70)
        print(" GENERATING ADA STANDARDS OF CARE 2024 / 2026 REPORTS (.DOCX)")
        print("=" * 70)
        ada_script = os.path.join(ROOT_DIR, 'Documentation', 'generate_ada_report.py')
        subprocess.run([sys.executable, ada_script], cwd=os.path.join(ROOT_DIR, 'Documentation'))
    elif args.test:
        print("\n" + "=" * 70)
        print(" RUNNING AUTOMATED CLINICAL TEST SUITES (OFFLINE, ZERO API KEY)")
        print("=" * 70)
        res = subprocess.run([sys.executable, "-m", "pytest", "-v"], cwd=ROOT_DIR)
        sys.exit(res.returncode)
    elif args.ui:
        launch_ui()
    elif args.phase:
        if args.phase == 'all':
            all_ok = True
            for p in ['1', '2', '3', '4']:
                ok = run_phase(p)
                if not ok:
                    all_ok = False
                    break
            print("\n[ALL PHASES RESULT]:", "PASSED 100%" if all_ok else "SOME PHASES FAILED")
        else:
            run_phase(args.phase)
    else:
        # Default banner
        print("=" * 70)
        print("  AL-NEELAIN UNIVERSITY - MASTER'S THESIS PROJECT")
        print("  Multi-Agent Clinical AI Decision Support System for Diabetes")
        print("  Author: Mohamed Abolgasim | Supervisor: Dr. Fakhreldeen Saeed")
        print("=" * 70)
        print("\nAvailable Commands:")
        print("  python run_system.py --ui                    : Launch Streamlit Dashboard")
        print("  python run_system.py --test                  : Run automated test suite (10/10 offline, no API key)")
        print("  python run_system.py --phase all             : Run and verify all 4 phases")
        print("  python run_system.py --phase 1 (or 2, 3, 4)  : Run specific phase")
        print("  python run_system.py --generate-all-reports  : Re-generate all Word documents")
        print("  python run_system.py --ada-report            : Generate ADA Standards of Care 2024/2026 reports")
        print("  python run_system.py --presentation          : Re-generate both Arabic & English presentations")
        print("  python run_system.py --presentation ar / en  : Re-generate specific presentation")

if __name__ == "__main__":
    main()
