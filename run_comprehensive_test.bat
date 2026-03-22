@echo off
echo ============================================================
echo VISIONCART COMPREHENSIVE TESTING SUITE
echo ============================================================
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo This will run professional-grade tests:
echo   - Correct Product Recognition (20 attempts per product)
echo   - Detection Rate Measurement
echo   - Recognition Accuracy Calculation
echo   - Performance Metrics Collection
echo   - Professional Report Generation
echo.
echo Results will be saved in:
echo   - testing/comprehensive_report.json
echo   - FINAL_TEST_REPORT.md (template)
echo.
echo ============================================================
pause
echo.
python testing/comprehensive_test.py
echo.
echo ============================================================
echo Testing completed! Check the reports.
echo ============================================================
pause
