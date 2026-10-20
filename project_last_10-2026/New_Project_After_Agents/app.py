"""
Root Application Launcher for Multi-Agent Clinical AI System for Diabetes Prediction.
Run directly using: streamlit run app.py
"""

import os
import sys

# Add subdirectories to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
P1_DIR = os.path.join(BASE_DIR, 'Phase_1_Data_Modeling_and_Validation')
P2_DIR = os.path.join(BASE_DIR, 'Phase_2_Multi_Agent_Architecture')
P3_DIR = os.path.join(BASE_DIR, 'Phase_3_Interactive_UI_and_System_Integration')

for p in [P1_DIR, P2_DIR, P3_DIR, BASE_DIR]:
    if p not in sys.path:
        sys.path.append(p)

# Import and execute Phase 3 App
import importlib.util
app_path = os.path.join(P3_DIR, "app.py")
spec = importlib.util.spec_from_file_location("phase3_app", app_path)
app_module = importlib.util.module_from_spec(spec)
sys.modules["phase3_app"] = app_module
spec.loader.exec_module(app_module)
