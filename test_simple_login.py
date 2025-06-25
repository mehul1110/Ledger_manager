#!/usr/bin/env python3
"""
Simple test for login dialog
"""

import sys
import os
import tkinter as tk

# Add the frontend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'frontend'))

from login_dialog import show_login_dialog

def test_simple():
    print("Creating root window...")
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    print("Showing login dialog...")
    print("Try logging in with: admin / admin123")
    
    result = show_login_dialog(root)
    
    if result:
        print("✓ Login successful!")
        messagebox.showinfo("Success", "Login successful! You can now proceed.")
    else:
        print("✗ Login cancelled or failed")
    
    root.destroy()
    return result

if __name__ == "__main__":
    from tkinter import messagebox
    success = test_simple()
    print(f"Final result: {success}")
