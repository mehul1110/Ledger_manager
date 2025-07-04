@echo off

REM Run the SQL setup script
ECHO Running setup_bahi_khata.sql...
sqlcmd -S . -d YourDatabaseName -i setup_bahi_khata.sql
IF %ERRORLEVEL% NEQ 0 (
    ECHO Failed to execute setup_bahi_khata.sql
    EXIT /B 1
)

REM Run the cx_Freeze setup script
ECHO Running setup_cxfreeze.py...
E:\bahikhata\Ledger_manager\.venv\Scripts\python.exe E:\bahikhata\Ledger_manager\setup_cxfreeze.py build
IF %ERRORLEVEL% NEQ 0 (
    ECHO Failed to execute setup_cxfreeze.py
    EXIT /B 1
)

ECHO Setup completed successfully.
