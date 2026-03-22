@echo off
echo ============================================================
echo MULTI-VIEW BOTTLE REGISTRATION
echo ============================================================
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo This will register cylindrical objects (bottles) using
echo multi-view capture for better recognition.
echo.
echo You will capture 3 views:
echo   1. Front label facing camera
echo   2. Rotate 45 degrees LEFT
echo   3. Rotate 45 degrees RIGHT
echo.
echo All 3 views will be averaged for robust recognition!
echo.
echo ============================================================
pause
echo.
python register_bottle_multiview.py
echo.
pause
