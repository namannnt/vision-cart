@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Running system check...
python system_check.py
echo.
pause
