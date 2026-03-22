@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo ============================================================
echo VISIONCART ACCURACY TESTING
echo ============================================================
echo.
echo This will test each product multiple times with camera
echo and generate an accuracy report.
echo.
echo Instructions:
echo   1. Place product in front of camera
echo   2. Press SPACE to capture each test
echo   3. Each product will be tested 20 times
echo   4. Report will be saved in testing/accuracy_report.json
echo.
echo ============================================================
pause
echo.
python testing/test_accuracy.py
echo.
pause
