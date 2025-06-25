"""
Login Dialog Module for BAHI-KHATA Application

This module provides a login dialog window for user authentication
before accessing the main application functionality.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_connect import get_connection


class LoginDialog:
    """
    A modal login dialog window for user authentication.
    
    This class creates a professional-looking login dialog with username/password
    fields and handles authentication logic.
    """
    
    def __init__(self, parent):
        """
        Initialize the login dialog.
        
        Args:
            parent: The parent Tkinter window
        """
        self.parent = parent
        self.result = None  # Will store user info if login successful
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("BAHI-KHATA Login")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='#f0f8ff')
        
        # Center the dialog on screen first
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        # Make it modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Make the dialog visible and bring it to front
        self.dialog.deiconify()
        self.dialog.lift()
        self.dialog.attributes('-topmost', True)
        self.dialog.after(50, lambda: self.dialog.attributes('-topmost', False))
        self.dialog.focus_force()
        
        # Prevent closing with X button without authentication
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        self.create_login_ui()
        
    def create_login_ui(self):
        """Create the login dialog user interface."""
        # Main container
        main_frame = tk.Frame(self.dialog, bg='#f0f8ff', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="BAHI-KHATA", 
                              font=("Georgia", 24, "bold italic"), 
                              fg="#2c3e50", bg='#f0f8ff')
        title_label.pack(pady=(10, 5))
        
        subtitle_label = tk.Label(main_frame, text="Account Management System", 
                                 font=("Arial", 12, "italic"), 
                                 fg="#34495e", bg='#f0f8ff')
        subtitle_label.pack(pady=(0, 30))
        
        # Login form frame
        form_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=2, padx=20, pady=20)
        form_frame.pack(fill='x', pady=10)
        
        tk.Label(form_frame, text="Please enter login credentials:", 
                font=("Arial", 12, "bold"), fg="#2c3e50", bg='#ffffff').pack(pady=(0, 15))
        
        # Username field
        tk.Label(form_frame, text="Username:", font=("Arial", 11), 
                fg="#34495e", bg='#ffffff').pack(anchor='w', pady=(0, 5))
        self.username_entry = tk.Entry(form_frame, font=("Arial", 12), width=25, 
                                      relief='solid', bd=1, highlightthickness=2,
                                      highlightcolor="#3498db")
        self.username_entry.pack(pady=(0, 15))
        
        # Password field
        tk.Label(form_frame, text="Password:", font=("Arial", 11), 
                fg="#34495e", bg='#ffffff').pack(anchor='w', pady=(0, 5))
        self.password_entry = tk.Entry(form_frame, font=("Arial", 12), width=25, 
                                      show="*", relief='solid', bd=1, highlightthickness=2,
                                      highlightcolor="#3498db")
        self.password_entry.pack(pady=(0, 20))
        
        # Button frame
        button_frame = tk.Frame(form_frame, bg='#ffffff')
        button_frame.pack(fill='x')
        
        # Login button
        login_btn = tk.Button(button_frame, text="Login", 
                             font=("Arial", 12, "bold"), 
                             bg="#3498db", fg="white", 
                             relief='flat', padx=20, pady=8,
                             command=self.on_login,
                             cursor="hand2")
        login_btn.pack(side='left', padx=(0, 10))
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                              font=("Arial", 12), 
                              bg="#95a5a6", fg="white", 
                              relief='flat', padx=20, pady=8,
                              command=self.on_cancel,
                              cursor="hand2")
        cancel_btn.pack(side='left')
        
        # Bind Enter key to login
        self.dialog.bind('<Return>', lambda e: self.on_login())
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.on_login())
        
        # Set focus after a short delay to ensure dialog is fully rendered
        self.dialog.after(100, self.set_focus)
        
        # Default credentials hint
        hint_label = tk.Label(main_frame, text="Default: admin / admin123", 
                             font=("Arial", 9, "italic"), 
                             fg="#7f8c8d", bg='#f0f8ff')
        hint_label.pack(pady=(10, 0))
        
    def set_focus(self):
        """Set focus to username field after dialog is fully rendered."""
        self.username_entry.focus_set()
        self.username_entry.icursor(0)
        
    def authenticate_user(self, username, password):
        """
        Authenticate user against database.
        
        Args:
            username: The username to authenticate
            password: The password to check
            
        Returns:
            dict: User information if successful, None if failed
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Query for user
            query = "SELECT user_id, username, role FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            
            if user:
                # Return user information as dictionary
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'role': user[2]
                }
            else:
                return None
                
        except Exception as e:
            messagebox.showerror("Database Error", 
                               f"Error connecting to database:\n{str(e)}", 
                               parent=self.dialog)
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def on_login(self):
        """Handle login button click and authentication."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Login Error", 
                               "Please enter both username and password.",
                               parent=self.dialog)
            return
        
        # Authenticate against database
        user_info = self.authenticate_user(username, password)
        
        if user_info:
            self.result = user_info
            self.dialog.destroy()
        else:
            messagebox.showerror("Login Failed", 
                               "Invalid username or password.\n\nPlease try again.",
                               parent=self.dialog)
            self.password_entry.delete(0, tk.END)
            self.username_entry.focus()
    
    def on_cancel(self):
        """Handle cancel button click or window close."""
        if messagebox.askquestion("Exit", "Are you sure you want to exit the application?",
                                 parent=self.dialog) == 'yes':
            self.result = None
            self.dialog.destroy()
    
    def show(self):
        """
        Display the login dialog and wait for user interaction.
        
        Returns:
            dict or None: User information if login successful, None if cancelled
        """
        # Ensure dialog is visible and focused
        self.dialog.deiconify()
        self.dialog.lift()
        self.dialog.focus_force()
        
        # Set focus to username field with a delay
        self.dialog.after(200, self.set_focus)
        
        # Wait for the dialog to be closed
        self.parent.wait_window(self.dialog)
        return self.result


def show_login_dialog(parent):
    """
    Convenience function to show the login dialog.
    
    Args:
        parent: The parent Tkinter window
        
    Returns:
        dict or None: User information if login successful, None if cancelled
    """
    login = LoginDialog(parent)
    return login.show()
