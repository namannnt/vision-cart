@echo off
echo ============================================================
echo VISIONCART CUSTOMER CHECKOUT COUNTER
echo ============================================================
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Starting Customer Checkout Dashboard...
echo.
echo This will open:
echo   - Streamlit dashboard (browser)
echo   - Customer-facing interface
echo   - Auto-detection and billing
echo.
echo ============================================================
pause
echo.
streamlit run ui/customer_checkout.py
pause
