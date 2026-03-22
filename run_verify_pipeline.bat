@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Verifying VisionCart Pipeline...
python verify_pipeline.py
echo.
pause
