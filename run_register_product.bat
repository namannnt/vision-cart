@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Starting Product Registration...
python register_product_app.py
pause
