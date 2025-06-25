# BAHI-KHATA Troubleshooting Guide

## If the Application Won't Start

When the BAHI-KHATA app doesn't start, it could be due to several common issues. Follow these steps to diagnose and fix the problem:

### Step 1: Run Diagnostic Tests

First, run the diagnostic script to identify the problem:

```batch
diagnose.bat
```

This will test:
- Python imports
- GUI components
- Database connectivity
- App startup in development mode

### Step 2: Check Common Issues

#### Missing Dependencies
If you see import errors, install the required packages:

```batch
pip install -r requirements.txt
```

Or install individual packages:
```batch
pip install Pillow mysql-connector-python PyInstaller
```

#### Database Connection Issues
- Ensure MySQL server is running
- Check database credentials in `db_connect.py`
- Verify the database `ledger_db` exists

#### GUI Issues
- If Tkinter fails to load, you may need to reinstall Python with Tkinter support
- On some systems, install tkinter separately: `sudo apt-get install python3-tk` (Linux)

### Step 3: Check Error Logs

Look for error log files in the application directory:
- `error.log` - All application error logs
- Console output when running the app

### Step 4: Development Mode Testing

Run the app in development mode to see detailed error messages:

```batch
cd frontend
python app.py
```

This will show real-time error messages and help identify the exact problem.

### Step 5: Common Solutions

#### Problem: "No module named 'PIL'"
**Solution:** Install Pillow
```batch
pip install Pillow
```

#### Problem: "No module named 'mysql.connector'"
**Solution:** Install MySQL connector
```batch
pip install mysql-connector-python
```

#### Problem: Database connection errors
**Solution:** 
1. Start MySQL server
2. Check credentials in `db_connect.py`
3. Ensure database exists: `CREATE DATABASE ledger_db;`

#### Problem: "tkinter" import fails
**Solution:** 
- Reinstall Python with Tkinter support
- Use Python from python.org (includes Tkinter)

#### Problem: Application hangs at startup
**Solution:**
1. Check if login dialog is hidden behind other windows
2. Press Alt+Tab to find the login window
3. Check for any background processes

### Step 6: Rebuild the Application

If the executable is corrupted, rebuild it:

```batch
quick_update.bat
```

Or for a complete rebuild:
```batch
build_complete.bat
```

### Step 7: System Requirements

Ensure your system meets the requirements:
- Windows 10 or later
- Python 3.8 or later
- MySQL Server 8.0 or later
- At least 100MB free disk space

### Getting Help

If problems persist:
1. Check the error logs for specific error messages
2. Run `diagnose.bat` and note which tests fail
3. Take screenshots of any error dialogs
4. Document the exact steps that lead to the problem

### Advanced Troubleshooting

#### Enable Debug Mode
Edit `frontend/app.py` and change the logging level:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

#### Check Python Environment
Verify your Python installation:
```batch
python --version
python -c "import tkinter; print('Tkinter OK')"
python -c "import PIL; print('PIL OK')"
python -c "import mysql.connector; print('MySQL OK')"
```

#### Test Database Manually
```batch
python test_connection.py
```

This guide should help resolve most startup issues with the BAHI-KHATA application.
