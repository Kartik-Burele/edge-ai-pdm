@echo off
echo ========================================================
echo Starting Edge-AI Predictive Maintenance Dashboard
echo ========================================================
echo.
echo Launching local Streamlit server...
cd /d "%~dp0"
uv run python -m streamlit run src/demo/app.py
pause
