@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Starting Simple Accuracy Test...
echo Show products to camera and check recognition
echo Press 'q' to quit
echo.
python simple_accuracy_test.py
pause
