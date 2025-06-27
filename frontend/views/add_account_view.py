import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import tkinter as tk
import sys, os, io
from add_account import add_account

def show_add_account_form(app, user_info=None):
    # Add permission check at the top
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from role_permissions import check_permission_with_message, Permissions
    
    if user_info and not check_permission_with_message(user_info, Permissions.ADD_ACCOUNTS, "add accounts"):
        return
    
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()
    app.get_responsive_fonts()
    label_font = app.fonts['label']
    entry_font = app.fonts['entry']
    button_font = app.fonts['button']
    tk.Button(app.root, text="\u2190 Go Back", command=app.show_main_menu, font=button_font).grid(row=0, column=0, padx=10, pady=10, sticky='w')
    tk.Label(app.root, text="Account Name:", font=label_font).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    name_entry = tk.Entry(app.root, font=entry_font)
    name_entry.grid(row=1, column=1, padx=10, pady=10)
    tk.Label(app.root, text="Account Type:", font=label_font).grid(row=2, column=0, padx=10, pady=10, sticky='e')
    # Account Type dropdown with 'Select' as default
    account_types = ['Select', 'main fund', 'bank', 'cash', 'salary', 'unit', 'printer', 'payer', 'payee']
    type_var = tk.StringVar(value=account_types[0])
    type_menu = tk.OptionMenu(app.root, type_var, *account_types)
    type_menu.config(font=entry_font)
    type_menu.grid(row=2, column=1, padx=10, pady=10)
    def style_entry(entry):
        entry.config(relief='flat', highlightthickness=2, highlightbackground='#cccccc', highlightcolor='#4A90E2', bd=0)
    for e in [name_entry, type_menu]:
        style_entry(e)
    error_labels = {}
    error_labels[name_entry] = tk.Label(app.root, text='', fg='red', font=entry_font, bg=app.root['bg'])
    error_labels[name_entry].grid(row=1, column=2, padx=5, sticky='w')
    error_labels[type_menu] = tk.Label(app.root, text='', fg='red', font=entry_font, bg=app.root['bg'])
    error_labels[type_menu].grid(row=2, column=2, padx=5, sticky='w')
    def submit(event=None):
        empty = False
        # Validate name_entry
        if not name_entry.get().strip():
            name_entry.config(bg="#ffe6e6")
            error_labels[name_entry].config(text='Required')
            empty = True
        else:
            name_entry.config(bg="white")
            error_labels[name_entry].config(text='')
        # Validate type_menu (using type_var)
        if type_var.get() == 'Select' or not type_var.get().strip():
            error_labels[type_menu].config(text='Required')
            empty = True
        else:
            error_labels[type_menu].config(text='')
        if empty:
            return
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(f"{name_entry.get()}\n{type_var.get()}\n")
        try:
            add_account()
            app.show_accounts_view()  # Show updated accounts list after adding
        except Exception as e:
            tk.Label(app.root, text=f"❌ Error: {e}", fg="red", font=label_font).grid(row=4, columnspan=2, pady=10)
        finally:
            sys.stdin = old_stdin
    tk.Button(app.root, text="Submit", command=submit, font=button_font, width=18).grid(row=3, columnspan=2, pady=15)
    name_entry.bind('<Return>', lambda e: submit())
    type_menu.bind('<Return>', lambda e: submit())
