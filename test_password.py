#!/usr/bin/env python3
"""
Test script to check password entry functionality
"""

import tkinter as tk
from tkinter import messagebox

def test_password_entry():
    root = tk.Tk()
    root.title("Password Entry Test")
    root.geometry("300x200")
    
    # Test variables
    username_var = tk.StringVar()
    password_var = tk.StringVar()
    
    # Create entries
    tk.Label(root, text="Username:").pack(pady=5)
    username_entry = tk.Entry(root, textvariable=username_var, font=("Arial", 12))
    username_entry.pack(pady=5)
    
    tk.Label(root, text="Password:").pack(pady=5)
    password_entry = tk.Entry(root, textvariable=password_var, font=("Arial", 12), show='•')
    password_entry.pack(pady=5)
    
    def check_values():
        u = username_var.get()
        p = password_var.get()
        messagebox.showinfo("Values", f"Username: '{u}'\nPassword: '{p}'\nPassword length: {len(p)}")
    
    tk.Button(root, text="Check Values", command=check_values).pack(pady=10)
    
    username_entry.focus()
    root.mainloop()

if __name__ == "__main__":
    test_password_entry()
