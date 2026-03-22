@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Starting Live Recognition...
python live_recognition.py
pause
