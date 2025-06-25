@echo off
echo ================================================
echo     BAHI-KHATA - Diagnostic Tests
echo ================================================
echo.
echo This script will run diagnostic tests to identify
echo why the BAHI-KHATA app might not be starting.
echo.

echo [1/3] Testing Python imports...
echo.
python test_imports.py
echo.

echo [2/3] Testing GUI components...
echo.
python test_gui.py
echo.

echo [3/3] Testing app startup (development mode)...
echo.
echo Starting the app in development mode to see any errors...
echo If a login dialog appears, the app is working correctly.
echo If you see errors, they will help identify the problem.
echo.
echo Press Ctrl+C to stop if the app hangs.
echo.
pause
echo.

cd frontend
python app.py

echo.
echo ================================================
echo     Diagnostic Tests Complete
echo ================================================
echo.
echo If the app didn't start:
echo 1. Check the error messages above
echo 2. Ensure MySQL server is running
echo 3. Verify database credentials in db_connect.py
echo 4. Install missing packages if needed:
echo    pip install pillow mysql-connector-python
echo.
pause
