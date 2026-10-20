@echo off
chcp 65001 >nul
title [Al-Neelain University] Multi-Agent Clinical AI System (Streamlit Dashboard)
echo ======================================================================
echo    AL-NEELAIN UNIVERSITY - MASTER'S THESIS PROJECT
echo    Multi-Agent Clinical AI Decision Support System for Diabetes
echo    Author: Mohamed Abuelgasim - Supervisor: Dr. Fakhreldeen Saeed
echo ======================================================================
echo.
echo [STARTING] Launching Interactive Streamlit Dashboard...
echo [INFO] Once started, your web browser will automatically open at:
echo        http://localhost:8501
echo.
python -m streamlit run app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Streamlit encountered an issue starting the application.
)
pause
