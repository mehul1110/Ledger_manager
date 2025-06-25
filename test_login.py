#!/usr/bin/env python3
"""
Test script to check login dialog functionality
"""

import sys
import os
import tkinter as tk

# Add the frontend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'frontend'))

try:
    from login_dialog import show_login_dialog
    print("✓ Successfully imported login_dialog")
except Exception as e:
    print(f"✗ Failed to import login_dialog: {e}")
    sys.exit(1)

def test_login():
    print("Creating root window...")
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    print("Root window created and hidden")
    
    print("Showing login dialog...")
    user_info = show_login_dialog(root)
    print(f"Login dialog result: {user_info}")
    
    if user_info:
        print(f"Login successful!")
        print(f"Username: {user_info['username']}")
        print(f"Role: {user_info['role']}")
        print(f"User ID: {user_info['user_id']}")
        root.deiconify()
        tk.Label(root, text=f"Login Successful!\nWelcome {user_info['username']}\nRole: {user_info['role']}", 
                font=("Arial", 16), justify='center').pack(pady=50)
        tk.Button(root, text="Close", command=root.quit).pack()
        root.mainloop()
    else:
        print("Login cancelled or failed")
    
    root.destroy()

if __name__ == "__main__":
    test_login()
