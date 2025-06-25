#!/usr/bin/env python3
"""
Quick startup test for BAHI-KHATA application.
This script performs a minimal test to check if the app can start.
"""

import sys
import os
import traceback
from datetime import datetime

def main():
    print("="*50)
    print("BAHI-KHATA Quick Startup Test")
    print("="*50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print("-"*50)
    
    try:
        print("Step 1: Testing critical imports...")
        
        # Test tkinter
        import tkinter as tk
        print("  ✓ tkinter")
        
        # Test PIL
        from PIL import Image, ImageTk
        print("  ✓ PIL/Pillow")
        
        # Test MySQL connector
        import mysql.connector
        print("  ✓ mysql.connector")
        
        print("\nStep 2: Testing database connection...")
        try:
            # Change to the correct directory for imports
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import db_connect
            
            conn = db_connect.get_connection()
            if conn.is_connected():
                print("  ✓ Database connection successful")
                conn.close()
            else:
                print("  ✗ Database connection failed")
                return False
        except Exception as e:
            print(f"  ✗ Database error: {str(e)}")
            print("    (This is common if MySQL isn't running)")
        
        print("\nStep 3: Testing GUI initialization...")
        root = tk.Tk()
        root.title("Startup Test")
        root.geometry("300x200")
        print("  ✓ GUI window created")
        
        # Test basic widgets
        label = tk.Label(root, text="Startup Test Successful!")
        label.pack(pady=20)
        
        button = tk.Button(root, text="Close Test", command=root.quit)
        button.pack(pady=10)
        
        print("  ✓ GUI widgets created")
        print("\n" + "="*50)
        print("SUCCESS: Basic startup test passed!")
        print("The application should be able to start.")
        print("="*50)
        print("\nA test window will appear for 2 seconds...")
        
        # Show window briefly and auto-close
        root.after(2000, root.quit)
        root.mainloop()
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"\nFAILED: {str(e)}")
        print("\nFull error:")
        print(traceback.format_exc())
        print("\n" + "="*50)
        print("Startup test failed. Check the error above.")
        print("Run 'diagnose.bat' for more detailed troubleshooting.")
        print("="*50)
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\nCommon fixes:")
            print("- Install missing packages: pip install -r requirements.txt")
            print("- Start MySQL server")
            print("- Check database credentials in db_connect.py")
    except Exception as e:
        print(f"Test script error: {str(e)}")
    finally:
        input("\nPress Enter to close...")
