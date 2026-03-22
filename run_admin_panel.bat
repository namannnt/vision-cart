@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Starting Admin Panel...
streamlit run ui/admin_panel.py
pause
