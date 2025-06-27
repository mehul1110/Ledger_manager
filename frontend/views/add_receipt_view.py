import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
from tkcalendar import Calendar
from add_receipt import add_receipt
import db_connect

def show_add_receipt_form(app, go_back_callback=None, user_info=None):
    # Add permission check at the top
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from role_permissions import check_permission_with_message, Permissions
    
    if user_info and not check_permission_with_message(user_info, Permissions.ADD_RECEIPTS, "add receipts"):
        return
    
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()
    app.get_responsive_fonts()
    label_font = app.fonts['label']
    entry_font = app.fonts['entry']
    button_font = app.fonts['button']

    tk.Button(app.root, text="\u2190 Go Back", command=go_back_callback, font=button_font).grid(row=0, column=0, padx=10, pady=10, sticky='w')

    # Fetch accounts
    conn = db_connect.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account_name FROM accounts WHERE account_type IN ('unit', 'bank','payer') ORDER BY account_name ASC")
    unit_accounts = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    # Add 'Select' as the first/default option for all dropdowns
    unit_accounts_with_custom = ['Select'] + unit_accounts + ["Other (custom...)"]
    account_var = tk.StringVar(value='Select')
    mop_options_with_custom = ['Select', 'Cash', 'Cheque', 'Bank Transfer', 'UPI', 'Other (custom...)']
    mop_var = tk.StringVar(value='Select')
    RECEIPT_NARRATION_OPTIONS_WITH_CUSTOM = ['Select', 'UCS', 'LCS', 'Interest on FD', 'Other (custom...)']
    narration_var = tk.StringVar(value='Select')

    # --- Widgets ---
    widgets = {}
    error_labels = {}
    row = 1
    def add_row(label, widget, var=None, custom_widget=None):
        nonlocal row
        tk.Label(app.root, text=label, font=label_font).grid(row=row, column=0, padx=10, pady=8, sticky='e')
        widget.grid(row=row, column=1, padx=10, pady=8, sticky='ew')
        widgets[label] = widget
        error = tk.Label(app.root, text='', fg='red', font=entry_font, bg=app.root['bg'])
        error.grid(row=row, column=2, padx=5, sticky='w')
        error_labels[widget] = error
        if custom_widget:
            custom_widget.grid(row=row, column=3, padx=10, pady=8, sticky='ew')
            error_labels[custom_widget] = tk.Label(app.root, text='', fg='red', font=entry_font, bg=app.root['bg'])
            error_labels[custom_widget].grid(row=row, column=4, padx=5, sticky='w')
            custom_widget.grid_remove()
            error_labels[custom_widget].grid_remove()
        row += 1

    # Account
    account_menu = tk.OptionMenu(app.root, account_var, *unit_accounts_with_custom)
    account_menu.config(font=entry_font)
    custom_account_entry = tk.Entry(app.root, width=25, font=entry_font)
    add_row("From (payer):", account_menu, account_var, custom_account_entry)
    custom_account_entry.grid_remove()
    error_labels[custom_account_entry].grid_remove()

    # Amount
    amount_entry = tk.Entry(app.root, width=25, font=entry_font)
    add_row("Amount received:", amount_entry)

    # Mode of payment
    mop_menu = tk.OptionMenu(app.root, mop_var, *mop_options_with_custom)
    mop_menu.config(font=entry_font)
    custom_mop_entry = tk.Entry(app.root, width=25, font=entry_font)
    add_row("Mode of payment:", mop_menu, mop_var, custom_mop_entry)
    custom_mop_entry.grid_remove()
    error_labels[custom_mop_entry].grid_remove()

    # Cheque widgets removed - no longer needed

    # Narration
    narration_menu = tk.OptionMenu(app.root, narration_var, *RECEIPT_NARRATION_OPTIONS_WITH_CUSTOM)
    narration_menu.config(font=entry_font)
    custom_narration_entry = tk.Entry(app.root, width=25, font=entry_font)
    add_row("Narration:", narration_menu, narration_var, custom_narration_entry)
    custom_narration_entry.grid_remove()
    error_labels[custom_narration_entry].grid_remove()

    # Transaction date (with calendar)
    tk.Label(app.root, text="Transaction date:", font=label_font).grid(row=row, column=0, padx=10, pady=8, sticky='e')
    date_var = tk.StringVar()
    date_entry = tk.Entry(app.root, font=entry_font, textvariable=date_var)
    date_entry.grid(row=row, column=1, padx=10, pady=8, sticky='ew')
    def open_calendar():
        top = tk.Toplevel(app.root)
        top.title("📅 Select Date")
        top.resizable(False, False)
        top.configure(bg='#f0f0f0')
        
        # Center the popup
        top.geometry("280x320")
        x = app.root.winfo_x() + (app.root.winfo_width() // 2) - 140
        y = app.root.winfo_y() + (app.root.winfo_height() // 2) - 160
        top.geometry(f"280x320+{x}+{y}")
        
        # Add a title label
        title_label = tk.Label(
            top, 
            text="Select Date", 
            font=('Segoe UI', 12, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=(10, 5))
        
        cal = Calendar(top, selectmode='day', date_pattern='dd-mm-yyyy')
        cal.pack(padx=15, pady=10)
        def set_date():
            date_var.set(cal.get_date())
            top.destroy()
        
        def cancel_date():
            top.destroy()
        
        # Button frame for better layout
        btn_frame = tk.Frame(top, bg='#f0f0f0')
        btn_frame.pack(pady=10)
        
        select_btn = tk.Button(
            btn_frame, 
            text="✓ Select Date", 
            command=set_date,
            font=('Segoe UI', 10, 'bold'),
            bg='#4CAF50',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            activebackground='#45a049',
            activeforeground='white'
        )
        select_btn.pack(side='left', padx=(0, 5))
        
        cancel_btn = tk.Button(
            btn_frame, 
            text="✕ Cancel", 
            command=cancel_date,
            font=('Segoe UI', 10),
            bg='#f44336',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            activebackground='#d32f2f',
            activeforeground='white'
        )
        cancel_btn.pack(side='left', padx=(5, 0))
    cal_btn = tk.Button(
        app.root, 
        text="📅 Select Date", 
        command=open_calendar, 
        font=('Segoe UI', 10, 'bold'),
        bg='#4CAF50',          # Green background
        fg='white',            # White text
        relief='flat',         # Flat modern look
        bd=0,                  # No border
        padx=10,               # Internal padding
        pady=5,
        cursor='hand2',        # Hand cursor on hover
        activebackground='#45a049',  # Darker green when clicked
        activeforeground='white'
    )
    cal_btn.grid(row=row, column=2, padx=5, pady=8, sticky='w')
    row += 1
    
    # Remarks field (general for all transactions)
    tk.Label(app.root, text="Remarks (optional):", font=label_font).grid(row=row, column=0, padx=10, pady=8, sticky='e')
    remarks_entry = tk.Entry(app.root, font=entry_font)
    remarks_entry.grid(row=row, column=1, padx=10, pady=8, sticky='ew')
    row += 1

    # --- Show/hide logic for custom fields ---
    def on_account_change(*args):
        if account_var.get() == "Other (custom...)":
            custom_account_entry.grid()
            error_labels[custom_account_entry].grid()
        else:
            custom_account_entry.grid_remove()
            error_labels[custom_account_entry].grid_remove()
    account_var.trace_add('write', on_account_change)

    def on_mop_change(*args):
        if mop_var.get() == "Other (custom...)":
            custom_mop_entry.grid()
            error_labels[custom_mop_entry].grid()
        else:
            custom_mop_entry.grid_remove()
            error_labels[custom_mop_entry].grid_remove()
    mop_var.trace_add('write', on_mop_change)
    on_mop_change()

    def on_narration_change(*args):
        if narration_var.get() == "Other (custom...)":
            custom_narration_entry.grid()
            error_labels[custom_narration_entry].grid()
        else:
            custom_narration_entry.grid_remove()
            error_labels[custom_narration_entry].grid_remove()
    narration_var.trace_add('write', on_narration_change)

    # --- Helper functions ---
    def get_account_value():
        if account_var.get() == "Other (custom...)":
            custom_name = custom_account_entry.get().strip()
            if not custom_name:
                raise ValueError("Custom account name cannot be empty")
            if len(custom_name) > 100:
                raise ValueError("Account name too long (max 100 characters)")
            # Check for invalid characters
            invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
            for char in invalid_chars:
                if char in custom_name:
                    raise ValueError(f"Account name cannot contain '{char}'")
            return custom_name
        else:
            return account_var.get()
    
    def get_mop_value():
        if mop_var.get() == "Other (custom...)":
            custom_mop = custom_mop_entry.get().strip()
            if not custom_mop:
                raise ValueError("Custom mode of payment cannot be empty")
            return custom_mop
        else:
            return mop_var.get()
    
    def get_narration_value():
        if narration_var.get() == "Other (custom...)":
            custom_narration = custom_narration_entry.get().strip()
            if not custom_narration:
                raise ValueError("Custom narration cannot be empty")
            return custom_narration
        else:
            return narration_var.get()

    # --- Validation and Submission ---
    def submit(event=None):
        empty = False
        # Build list of all visible entries to validate
        entries = [amount_entry, narration_menu, date_entry]
        if account_var.get() == 'Other (custom...)':
            entries.append(custom_account_entry)
        if mop_var.get() == 'Other (custom...)':
            entries.append(custom_mop_entry)
        if narration_var.get() == 'Other (custom...)':
            entries.append(custom_narration_entry)
        # Validate
        for entry in entries:
            value = entry.get() if hasattr(entry, 'get') else narration_var.get() if entry == narration_menu else entry.get()
            # Only access error_labels if the entry has one
            if entry in error_labels:
                if not value.strip() or value == 'Select':
                    if hasattr(entry, 'config'):
                        entry.config(bg="#ffe6e6")
                    error_labels[entry].config(text='Required')
                    empty = True
                else:
                    if hasattr(entry, 'config'):
                        entry.config(bg="white")
                    error_labels[entry].config(text='')
                if entry == amount_entry:
                    try:
                        float(value)
                        error_labels[entry].config(text='')
                    except ValueError:
                        error_labels[entry].config(text='Must be a number')
                        empty = True
            else:
                # Basic validation for entries without error labels
                if not value.strip() or value == 'Select':
                    if hasattr(entry, 'config'):
                        entry.config(bg="#ffe6e6")
                    empty = True
                else:
                    if hasattr(entry, 'config'):
                        entry.config(bg="white")
        if empty:
            return
        try:
            # Validate custom inputs first
            account_name = get_account_value()
            mop_value = get_mop_value()
            narration_value = get_narration_value()
            
            # Additional validation for custom account name
            if account_var.get() == "Other (custom...)":
                if not account_name:
                    raise ValueError("Please enter a custom account name")
                
                # Create the custom account immediately
                conn = db_connect.get_connection()
                cursor = conn.cursor()
                try:
                    # Check if account already exists
                    cursor.execute("SELECT COUNT(*) FROM accounts WHERE account_name = %s", (account_name,))
                    exists = cursor.fetchone()[0] > 0
                    
                    if not exists:
                        # Create account with type 'custom'
                        cursor.execute(
                            "INSERT INTO accounts (account_name, account_type) VALUES (%s, %s)",
                            (account_name, 'custom')
                        )
                        conn.commit()
                        print(f"✅ Created custom account: {account_name}")
                    
                    cursor.close()
                    conn.close()
                    
                except Exception as db_error:
                    cursor.close()
                    conn.close()
                    raise ValueError(f"Failed to create custom account: {db_error}")
            
            
            add_receipt(
                account_name=account_name,
                amount=float(amount_entry.get()),
                mop=mop_value,
                narration=narration_value,
                date_str=date_entry.get(),
                remarks=remarks_entry.get() if remarks_entry.get().strip() else None
            )
            
            # Success message
            msg = "✅ Receipt submitted for approval!"
            if account_var.get() == "Other (custom...)":
                msg += f"\n✅ Custom account '{account_name}' created successfully!"
            
            tk.Label(app.root, text=msg, fg="green", font=label_font, bg=app.root['bg']).grid(row=row+1, columnspan=3, pady=10)
            
        except ValueError as ve:
            # Handle validation errors
            tk.Label(app.root, text=f"⚠️ Validation Error: {ve}", fg="orange", font=label_font, bg=app.root['bg']).grid(row=row+1, columnspan=3, pady=10)
            
        except Exception as e:
            # Handle other errors
            error_msg = str(e)
            if "foreign key constraint" in error_msg.lower():
                tk.Label(app.root, text=f"❌ Database Error: Account validation failed. Please check account name.", fg="red", font=label_font, bg=app.root['bg']).grid(row=row+1, columnspan=3, pady=10)
            else:
                tk.Label(app.root, text=f"❌ Error: {error_msg}", fg="red", font=label_font, bg=app.root['bg']).grid(row=row+1, columnspan=3, pady=10)
    tk.Button(app.root, text="Submit", command=submit, width=18, font=button_font).grid(row=row, columnspan=2, pady=15)
    # Keyboard navigation
    account_menu.bind('<Return>', lambda e: amount_entry.focus_set())
    amount_entry.bind('<Return>', lambda e: mop_menu.focus_set())
    mop_menu.bind('<Return>', lambda e: narration_menu.focus_set())
    narration_menu.bind('<Return>', lambda e: date_entry.focus_set())
    date_entry.bind('<Return>', lambda e: submit())
    # Set up grid weights for alignment (fix label cutoff)
    app.root.grid_columnconfigure(0, weight=3, minsize=180)  # Label column wider
    app.root.grid_columnconfigure(1, weight=2, minsize=120)
    app.root.grid_columnconfigure(2, weight=1, minsize=80)
    app.root.grid_columnconfigure(3, weight=1, minsize=80)
    app.root.grid_columnconfigure(4, weight=1, minsize=80)