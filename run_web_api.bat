@echo off
echo ========================================
echo   VisionCart - Backend API Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup first or create venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Check if web_api.py exists
if not exist "web_api.py" (
    echo ERROR: web_api.py not found!
    pause
    exit /b 1
)

echo.
echo Starting VisionCart Backend API...
echo.
echo Backend will be available at:
echo   - Local: http://localhost:8000
echo   - Network: http://YOUR_IP:8000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Start the API server
python web_api.py

pause
