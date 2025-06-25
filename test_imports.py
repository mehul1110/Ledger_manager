#!/usr/bin/env python3
"""
Test script to check if all required modules can be imported successfully.
This helps identify any missing dependencies or import issues.
"""

import sys
import traceback
from datetime import datetime

def test_import(module_name, description=""):
    """Test importing a specific module and report results."""
    try:
        __import__(module_name)
        print(f"✓ {module_name} - OK {description}")
        return True
    except Exception as e:
        print(f"✗ {module_name} - FAILED: {str(e)} {description}")
        return False

def main():
    print("="*60)
    print("BAHI-KHATA Import Test")
    print("="*60)
    print(f"Python version: {sys.version}")
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*60)
    
    failed_imports = 0
    total_imports = 0
    
    # Test core Python modules
    modules_to_test = [
        ("tkinter", "(GUI framework)"),
        ("PIL", "(Python Imaging Library/Pillow)"),
        ("mysql.connector", "(MySQL database connector)"),
        ("datetime", "(Date/time utilities)"),
        ("logging", "(Logging framework)"),
        ("traceback", "(Error tracking)"),
        ("sys", "(System utilities)"),
        ("os", "(Operating system interface)"),
    ]
    
    for module, desc in modules_to_test:
        total_imports += 1
        if not test_import(module, desc):
            failed_imports += 1
    
    print("-"*60)
    
    # Test app-specific modules
    print("Testing application modules...")
    app_modules = [
        "db_connect",
        "frontend.login_dialog",
        "frontend.views.add_payment_view",
        "frontend.views.add_receipt_view",
        "frontend.views.add_account_view",
        "transaction_approver",
    ]
    
    for module in app_modules:
        total_imports += 1
        if not test_import(module, "(App module)"):
            failed_imports += 1
    
    print("-"*60)
    
    # Test database connection
    print("Testing database connection...")
    try:
        import db_connect
        conn = db_connect.get_connection()
        if conn.is_connected():
            print("✓ Database connection - OK")
            conn.close()
        else:
            print("✗ Database connection - FAILED: Not connected")
            failed_imports += 1
    except Exception as e:
        print(f"✗ Database connection - FAILED: {str(e)}")
        failed_imports += 1
    
    total_imports += 1
    
    print("="*60)
    print(f"Results: {total_imports - failed_imports}/{total_imports} imports successful")
    
    if failed_imports == 0:
        print("✓ All tests passed! The application should start correctly.")
        return True
    else:
        print(f"✗ {failed_imports} test(s) failed. Fix these issues before running the app.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\nTo fix import issues:")
            print("1. Install missing packages: pip install pillow mysql-connector-python")
            print("2. Ensure MySQL server is running")
            print("3. Check database credentials in db_connect.py")
        
        input("\nPress Enter to close...")
    except Exception as e:
        print(f"Test script failed: {str(e)}")
        print(traceback.format_exc())
        input("\nPress Enter to close...")
