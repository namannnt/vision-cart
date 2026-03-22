@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Running Quick System Test...
python quick_test.py
echo.
pause
