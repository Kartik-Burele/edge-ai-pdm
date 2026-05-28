@echo off
echo ========================================================
echo Starting Edge-AI BLDC Predictive Maintenance Dashboard
echo ========================================================
echo.
echo Launching local Streamlit server for BLDC Motor Digital Twin...
cd /d "%~dp0"
..\.venv\Scripts\python.exe -m streamlit run src/demo/app.py
pause
