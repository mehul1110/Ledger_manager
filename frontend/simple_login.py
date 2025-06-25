"""
Simple Login Dialog for BAHI-KHATA Application
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_connect import get_connection


def authenticate_user(username, password):
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
        messagebox.showerror("Database Error", f"Error connecting to database:\n{str(e)}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def show_simple_login():
    """
    Show a simple login dialog using standard dialogs.
    
    Returns:
        dict or None: User information if login successful, None if cancelled
    """
    max_attempts = 3
    attempts = 0
    
    while attempts < max_attempts:
        # Get username
        username = simpledialog.askstring("BAHI-KHATA Login", 
                                        "Enter Username:\n\nDefault credentials:\n• admin / admin123\n• accountant / account123\n• viewer / viewer123",
                                        initialvalue="admin")
        
        if username is None:  # User cancelled
            return None
            
        # Get password
        password = simpledialog.askstring("BAHI-KHATA Login", 
                                        f"Enter Password for '{username}':",
                                        show='*')
        
        if password is None:  # User cancelled
            return None
        
        # Authenticate
        user_info = authenticate_user(username.strip(), password.strip())
        
        if user_info:
            messagebox.showinfo("Login Successful", 
                              f"Welcome {user_info['username']}!\nRole: {user_info['role'].title()}")
            return user_info
        else:
            attempts += 1
            remaining = max_attempts - attempts
            if remaining > 0:
                messagebox.showerror("Login Failed", 
                                   f"Invalid username or password.\n\nAttempts remaining: {remaining}")
            else:
                messagebox.showerror("Login Failed", 
                                   "Maximum login attempts exceeded.\nApplication will exit.")
                return None
    
    return None


class SimpleLoginDialog:
    """A simple, reliable login dialog that definitely accepts input."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        
        # Create a simpler, properly sized dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("BAHI-KHATA - Login")
        self.dialog.geometry("400x320")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='white')
        
        # Create the UI
        self.create_ui()
        
        # Center and configure
        self.center_dialog()
        
        # Make it modal
        self.dialog.grab_set()
        
        # Force the dialog to show and come to front
        self.dialog.deiconify()
        self.dialog.lift()
        self.dialog.attributes('-topmost', True)
        self.dialog.focus_force()
        
        # Focus on username entry after a short delay
        self.dialog.after(100, lambda: self.username_entry.focus_set())
        
        # Bind close
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def center_dialog(self):
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (320 // 2)
        self.dialog.geometry(f"400x320+{x}+{y}")
    
    def create_ui(self):
        # Simple header
        header_frame = tk.Frame(self.dialog, bg='#2c3e50', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="BAHI-KHATA", 
                font=("Arial", 20, "bold"), 
                fg="white", bg='#2c3e50').pack(pady=15)
        
        # Main form area - single container with proper padding
        main_frame = tk.Frame(self.dialog, bg='white', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Welcome text
        tk.Label(main_frame, text="Please sign in", 
                font=("Arial", 14, "bold"), 
                fg="#2c3e50", bg='white').pack(pady=(0, 20))
        
        # Username section
        tk.Label(main_frame, text="Username", 
                font=("Arial", 11, "bold"), 
                fg="#34495e", bg='white').pack(anchor='w')
        
        self.username_entry = tk.Entry(main_frame, 
                                      textvariable=self.username, 
                                      font=("Arial", 12), 
                                      bg="#f8f9fa",
                                      fg="#2c3e50",
                                      relief='solid',
                                      bd=1,
                                      highlightthickness=1,
                                      highlightcolor="#3498db")
        self.username_entry.pack(fill='x', pady=(5, 15), ipady=6)
        
        # Password section
        tk.Label(main_frame, text="Password", 
                font=("Arial", 11, "bold"), 
                fg="#34495e", bg='white').pack(anchor='w')
        
        self.password_entry = tk.Entry(main_frame, 
                                      textvariable=self.password, 
                                      font=("Arial", 12), 
                                      show='*',
                                      bg="#f8f9fa",
                                      fg="#2c3e50",
                                      relief='solid',
                                      bd=1,
                                      highlightthickness=1,
                                      highlightcolor="#3498db")
        self.password_entry.pack(fill='x', pady=(5, 20), ipady=6)
        
        # Button section
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Login button
        login_btn = tk.Button(button_frame, 
                             text="Sign In", 
                             command=self.login,
                             font=("Arial", 11, "bold"), 
                             bg="#3498db", 
                             fg="white",
                             relief='flat',
                             bd=0,
                             padx=25,
                             pady=8,
                             cursor="hand2")
        login_btn.pack(side='left', padx=(0, 10))
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, 
                              text="Cancel", 
                              command=self.cancel,
                              font=("Arial", 11), 
                              bg="#95a5a6", 
                              fg="white",
                              relief='flat',
                              bd=0,
                              padx=25,
                              pady=8,
                              cursor="hand2")
        cancel_btn.pack(side='left')
        
        # Default credentials hint at bottom
        hint_frame = tk.Frame(main_frame, bg='white')
        hint_frame.pack(fill='x', pady=(15, 0))
        
        tk.Label(hint_frame, text="Default: admin / admin123", 
                font=("Arial", 9, "italic"), 
                fg="#7f8c8d", bg='white').pack()
        
        # Keyboard bindings
        self.dialog.bind('<Return>', lambda e: self.login())
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Add hover effects
        self.add_hover_effects(login_btn, "#2980b9", "#3498db")
        self.add_hover_effects(cancel_btn, "#7f8c8d", "#95a5a6")
    
    def add_hover_effects(self, button, hover_color, normal_color):
        """Add hover effects to buttons"""
        def on_enter(event):
            button.config(bg=hover_color)
        
        def on_leave(event):
            button.config(bg=normal_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def login(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.", parent=self.dialog)
            if not username:
                self.username_entry.focus()
            else:
                self.password_entry.focus()
            return
        
        user_info = authenticate_user(username, password)
        if user_info:
            self.result = user_info
            self.dialog.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.", parent=self.dialog)
            self.password.set("")
            self.password_entry.focus()
    
    def cancel(self):
        if messagebox.askquestion("Exit", "Exit application?", parent=self.dialog) == 'yes':
            self.result = None
            self.dialog.destroy()
    
    def show(self):
        """Display the dialog and wait for user interaction"""
        # Ensure dialog is visible
        self.dialog.deiconify()
        self.dialog.lift()
        self.dialog.attributes('-topmost', True)
        self.dialog.focus_force()
        
        # Wait for user interaction
        self.parent.wait_window(self.dialog)
        return self.result


def show_login_dialog(parent):
    """
    Show login dialog and return user info.
    
    Returns:
        dict or None: User information if successful, None if cancelled
    """
    try:
        dialog = SimpleLoginDialog(parent)
        return dialog.show()
    except Exception as e:
        messagebox.showerror("Login Error", f"An error occurred while showing the login dialog:\n{str(e)}")
        return None
