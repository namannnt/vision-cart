@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Starting Auto Billing Counter...
python auto_billing_counter.py
pause
