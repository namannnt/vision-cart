@echo off
echo ============================================================
echo VISIONCART CHECKOUT BACKEND (OpenCV Version)
echo ============================================================
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Starting Checkout Counter with Camera...
echo.
echo Instructions:
echo   - Place items in scanning area
echo   - Auto-detection will add to cart
echo   - Press 'C' to checkout
echo   - Press 'R' to remove last item
echo   - Press 'Q' to quit
echo.
echo ============================================================
pause
echo.
python customer_checkout_backend.py
pause
