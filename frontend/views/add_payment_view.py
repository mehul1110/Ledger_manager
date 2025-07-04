import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
from tkcalendar import Calendar
import sys, os, io
import db_connect
from add_payment import add_payment

# This module contains the Add Payment form logic, extracted from the main app.
# The function expects the parent (root) and callbacks as arguments.
def show_add_payment_form(app, go_back_callback=None, user_info=None):
    # Add permission check at the top
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from role_permissions import check_permission_with_message, Permissions
    
    if user_info and not check_permission_with_message(user_info, Permissions.ADD_PAYMENTS, "add payments"):
        return
    
    # Clear the window before adding the form
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()
    app.get_responsive_fonts()
    label_font = app.fonts['label']
    entry_font = app.fonts['entry']
    button_font = app.fonts['button']
    tk.Button(app.root, text="← Go Back", command=go_back_callback, font=button_font).grid(row=0, column=0, padx=10, pady=10, sticky='w')
    tk.Label(app.root, text="To (Payee):", font=label_font).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    conn = db_connect.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account_name FROM accounts WHERE account_type NOT IN ('payer', 'unit') ORDER BY account_name ASC")
    account_names = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    # Cheque widgets removed - no longer needed
    # Account dropdown with custom option
    account_names_with_custom = ['Select'] + account_names + ["Other (custom...)"]
    account_var = tk.StringVar(value='Select')
    account_menu = tk.OptionMenu(app.root, account_var, *account_names_with_custom)
    account_menu.config(font=entry_font)
    account_menu.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
    custom_account_entry = tk.Entry(app.root, font=entry_font)
    def on_account_change(*args):
        if account_var.get() == "Other (custom...)":
            custom_account_entry.grid(row=1, column=2, padx=10, pady=10, sticky='ew')
        else:
            custom_account_entry.grid_remove()
    account_var.trace_add('write', on_account_change)
    tk.Label(app.root, text="Amount paid:", font=label_font).grid(row=2, column=0, padx=10, pady=10, sticky='e')
    amount_entry = tk.Entry(app.root, font=entry_font)
    amount_entry.grid(row=2, column=1, padx=10, pady=10, sticky='ew')
    # Mode of payment dropdown with custom option
    tk.Label(app.root, text="Mode of Payment:", font=label_font).grid(row=3, column=0, padx=10, pady=10, sticky='e')
    mop_options_with_custom = ['Select', 'Cash', 'Cheque/DD', 'Bank Transfer', 'UPI', 'Other (custom...)']
    mop_var = tk.StringVar(value='Select')
    mop_menu = tk.OptionMenu(app.root, mop_var, *mop_options_with_custom)
    mop_menu.config(font=entry_font)
    mop_menu.grid(row=3, column=1, padx=10, pady=10, sticky='ew')
    custom_mop_entry = tk.Entry(app.root, font=entry_font)
    def show_mop_custom_field(*args):
        if mop_var.get() == "Other (custom...)":
            custom_mop_entry.grid(row=3, column=2, padx=10, pady=10, sticky='ew')
        else:
            custom_mop_entry.grid_remove()
    mop_var.trace_add('write', show_mop_custom_field)
    show_mop_custom_field()
    tk.Label(app.root, text="Narration:", font=label_font).grid(row=4, column=0, padx=10, pady=10, sticky='e')
    # Narration dropdown with custom option
    NARRATION_OPTIONS = [
        "Petty Cash withdrawal", "Maintenance", "Salary", "Property", "FD in bank", "Misc", 
    "Article appreciation amount", "Internet bill", "Fund lend to other accounts", 
    "Printing of happenings"
    ]
    NARRATION_OPTIONS_WITH_CUSTOM = ['Select'] + NARRATION_OPTIONS + ["Other (custom...)"]
    narration_var = tk.StringVar(value='Select')
    narration_menu = tk.OptionMenu(app.root, narration_var, *NARRATION_OPTIONS_WITH_CUSTOM)
    narration_menu.config(font=entry_font)
    narration_menu.grid(row=4, column=1, padx=10, pady=10, sticky='ew')
    custom_narration_entry = tk.Entry(app.root, font=entry_font)
    def on_narration_change(*args):
        if narration_var.get() == "Other (custom...)":
            custom_narration_entry.grid(row=4, column=2, padx=10, pady=10, sticky='ew')
        else:
            custom_narration_entry.grid_remove()
    narration_var.trace_add('write', on_narration_change)
    
    # Property fields
    item_label = tk.Label(app.root, text="Item Name (for Property):", font=label_font)
    item_entry = tk.Entry(app.root, font=entry_font)
    desc_var = tk.StringVar(value="expendable")
    # Description radio buttons for Property
    desc_frame = tk.Frame(app.root, bg=app.root['bg'])
    desc_label = tk.Label(desc_frame, text="Description:", font=label_font, bg=app.root['bg'])
    desc_label.pack(side='left', padx=(0, 10))
    desc_radio1 = tk.Radiobutton(desc_frame, text="Expendable", variable=desc_var, value="expendable", font=label_font, bg=app.root['bg'], anchor='w')
    desc_radio1.pack(side='left', padx=(0, 20))
    desc_radio2 = tk.Radiobutton(desc_frame, text="Non-expendable", variable=desc_var, value="non-expendable", font=label_font, bg=app.root['bg'], anchor='w')
    desc_radio2.pack(side='left')
    type_label = tk.Label(app.root, text="Type (electronic/furniture/etc):", font=label_font)
    # Property type dropdown for 'Type' field with 'Select' as default
    PROPERTY_TYPES = ["Select", "electronic", "furniture", "stationery", "vehicle", "building", "other"]
    type_var = tk.StringVar(value=PROPERTY_TYPES[0])
    type_menu = tk.OptionMenu(app.root, type_var, *PROPERTY_TYPES)
    type_menu.config(font=entry_font)
    fd_duration_label = tk.Label(app.root, text="FD Duration (for FD in bank):", font=label_font)
    fd_duration_number = tk.Entry(app.root, font=entry_font, width=8)
    fd_duration_unit = tk.StringVar(value="Select")
    fd_duration_unit_menu = tk.OptionMenu(app.root, fd_duration_unit, "Select", "days", "months")
    fd_duration_unit_menu.config(font=entry_font)
    fd_interest_label = tk.Label(app.root, text="FD Interest Rate (for FD in bank):", font=label_font)
    fd_interest_entry = tk.Entry(app.root, font=entry_font)
    # Transaction date (with calendar)
    tk.Label(app.root, text="Transaction date:", font=label_font).grid(row=5, column=0, padx=10, pady=10, sticky='e')
    date_var = tk.StringVar()
    date_entry = tk.Entry(app.root, font=entry_font, textvariable=date_var)
    date_entry.grid(row=5, column=1, padx=10, pady=10, sticky='ew')
    
    # Remarks field (general for all transactions)
    tk.Label(app.root, text="Remarks (optional):", font=label_font).grid(row=6, column=0, padx=10, pady=10, sticky='e')
    remarks_entry = tk.Entry(app.root, font=entry_font)
    remarks_entry.grid(row=6, column=1, padx=10, pady=10, sticky='ew')
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
            bg='#2196F3',
            fg='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            activebackground='#1976D2',
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
        bg='#2196F3',          # Blue background
        fg='white',            # White text
        relief='flat',         # Flat modern look
        bd=0,                  # No border
        padx=10,               # Internal padding
        pady=5,
        cursor='hand2',        # Hand cursor on hover
        activebackground='#1976D2',  # Darker blue when clicked
        activeforeground='white'
    )
    cal_btn.grid(row=5, column=2, padx=5, pady=10, sticky='w')
    def hide_all_extras():
        for w in [item_label, item_entry, desc_radio1, desc_radio2, type_label, type_menu, fd_duration_label, fd_duration_number, fd_duration_unit_menu, fd_interest_label, fd_interest_entry]:
            w.grid_forget()
    def show_extras(*args):
        hide_all_extras()
        row = 7  # Start from row 7 since remarks is now at row 6
        if narration_var.get() == "Property":
            item_label.grid(row=row, column=0, padx=10, pady=10, sticky='e')
            item_entry.grid(row=row, column=1, padx=10, pady=10, sticky='ew')
            row += 1
            # Use the desc_frame for description radio buttons
            desc_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky='w')
            row += 1
            type_label.grid(row=row, column=0, padx=10, pady=10, sticky='e')
            type_menu.grid(row=row, column=1, padx=10, pady=10, sticky='ew')
            row += 1
        if narration_var.get() == "FD in bank":
            fd_duration_label.grid(row=row, column=0, padx=10, pady=10, sticky='e')
            fd_duration_number.grid(row=row, column=1, padx=(10,0), pady=10, sticky='w')
            fd_duration_unit_menu.grid(row=row, column=1, padx=(80,10), pady=10, sticky='w')
            row += 1
            fd_interest_label.grid(row=row, column=0, padx=10, pady=10, sticky='e')
            fd_interest_entry.grid(row=row, column=1, padx=10, pady=10, sticky='ew')
            row += 1
    narration_var.trace_add('write', show_extras)
    show_extras()
    def style_entry(entry):
        entry.config(relief='flat', highlightthickness=2, highlightbackground='#cccccc', highlightcolor='#4A90E2', bd=0)
    for e in [account_menu, amount_entry, date_entry, remarks_entry, item_entry, fd_duration_number, fd_interest_entry]:
        style_entry(e)
    # Validation and error labels
    # Use only widgets as keys in error_labels
    error_labels = {}
    
    # Validation
    def submit(event=None):
        empty = False
        fd_unit = fd_duration_unit.get() if narration_var.get() == "FD in bank" else ''
        
        # Build fields list dynamically based on current form state
        fields = [
            ("To (Payee)", account_var, account_menu),
            ("Amount paid", amount_entry, amount_entry),
            ("Transaction date", date_entry, date_entry)
        ]
        
        # Add custom account field if needed
        if account_var.get() == "Other (custom...)":
            fields.append(("Custom Account Name", custom_account_entry, custom_account_entry))
            
        # Add custom MoP field if needed
        if mop_var.get() == "Other (custom...)":
            fields.append(("Custom Mode of Payment", custom_mop_entry, custom_mop_entry))
            
        # Add custom narration field if needed
        if narration_var.get() == "Other (custom...)":
            fields.append(("Custom Narration", custom_narration_entry, custom_narration_entry))
        
        # Add narration-specific fields
        if narration_var.get() == "Property":
            fields.extend([
                ("Item Name", item_entry, item_entry),
                ("Type", type_var, type_menu)
            ])
        if narration_var.get() == "FD in bank":
            fields.extend([
                ("FD Duration", fd_duration_number, fd_duration_number),
                ("FD Interest Rate", fd_interest_entry, fd_interest_entry)
            ])
        
        # Ensure error labels exist for all widgets
        for _, _, widget in fields:
            if widget not in error_labels:
                error_labels[widget] = tk.Label(app.root, text='', fg='red', font=entry_font, bg=app.root['bg'])
        
        # Validate all fields
        for label, var, widget in fields:
            value = var.get() if hasattr(var, 'get') else var.get()
            if label in ["Amount paid", "FD Interest Rate"]:
                if not value.strip():
                    if hasattr(widget, 'config'):
                        widget.config(bg="#ffe6e6")
                    error_labels[widget].config(text='Required')
                    empty = True
                else:
                    try:
                        float(value)
                        if hasattr(widget, 'config'):
                            widget.config(bg="white")
                        error_labels[widget].config(text='')
                    except ValueError:
                        if hasattr(widget, 'config'):
                            widget.config(bg="#ffe6e6")
                        error_labels[widget].config(text='Must be a number')
                        empty = True
            else:
                if not value.strip() or value == 'Select':
                    if hasattr(widget, 'config'):
                        widget.config(bg="#ffe6e6")
                    error_labels[widget].config(text='Required')
                    empty = True
                else:
                    if hasattr(widget, 'config'):
                        widget.config(bg="white")
                    error_labels[widget].config(text='')
        # FD Duration number validation
        if narration_var.get() == "FD in bank":
            fd_num = fd_duration_number.get().strip()
            if not fd_num.isdigit():
                error_labels[fd_duration_number].config(text='Enter a number')
                fd_duration_number.config(bg="#ffe6e6")
                return
            fd_duration_val = f"{fd_num} {fd_unit}"
        else:
            fd_num = ''
            fd_duration_val = ''
        if empty:
            return
        # Calculate maturity amount for FD in bank
        maturity_amount = None
        if narration_var.get() == "FD in bank":
            try:
                principal = float(amount_entry.get()) if amount_entry.get() else 0
                # Convert duration to years for simple interest calculation
                if fd_unit == 'months':
                    time_in_years = int(fd_num) / 12
                elif fd_unit == 'days':
                    # Convert days to years (using 365.25 to account for leap years)
                    time_in_years = int(fd_num) / 365.25
                else:
                    time_in_years = 0
                rate = float(fd_interest_entry.get())
                # Simple Interest Formula: SI = (P × R × T) / 100
                simple_interest = (principal * rate * time_in_years) / 100
                # Maturity Amount = Principal + Simple Interest
                maturity_amount = round(principal + simple_interest, 2)
            except Exception:
                maturity_amount = None
        # Helper functions for custom dropdowns
        def get_account_value():
            if account_var.get() == "Other (custom...)":
                custom_name = custom_account_entry.get().strip()
                if not custom_name:
                    raise ValueError("Custom account name cannot be empty")
                if len(custom_name) > 100:
                    raise ValueError("Account name too long (max 100 characters)")
                # Check for invalid characters that might cause database issues
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
        # Always pass all required arguments for each narration type
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
            
            
            add_payment(
                name=account_name,
                amount=float(amount_entry.get()),
                mop=mop_value,
                cheque_no=None,
                date_str=date_entry.get(),
                narration=narration_value,
                item_name=item_entry.get() if narration_var.get() == 'Property' else None,
                description=desc_var.get() if narration_var.get() == 'Property' else None,
                item_type=type_var.get() if narration_var.get() == 'Property' else None,
                fd_duration=fd_duration_val if narration_var.get() == 'FD in bank' else None,
                fd_interest=fd_interest_entry.get() if narration_var.get() == 'FD in bank' else None,
                remarks=remarks_entry.get() if remarks_entry.get().strip() else None
            )
            
            # Success message
            msg = "✅ Payment submitted for approval!"
            if account_var.get() == "Other (custom...)":
                msg += f"\n✅ Custom account '{account_name}' created successfully!"
            
            if narration_var.get() == "FD in bank":
                try:
                    principal = float(amount_entry.get()) if amount_entry.get() else 0
                    # Convert duration to years for simple interest calculation
                    if fd_unit == 'months':
                        time_in_years = int(fd_num) / 12
                    elif fd_unit == 'days':
                        # Convert days to years (using 365.25 to account for leap years)
                        time_in_years = int(fd_num) / 365.25
                    else:
                        time_in_years = 0
                    rate = float(fd_interest_entry.get())
                    # Simple Interest Formula: SI = (P × R × T) / 100
                    simple_interest = (principal * rate * time_in_years) / 100
                    # Maturity Amount = Principal + Simple Interest
                    maturity_amount = round(principal + simple_interest, 2)
                    msg += f"\n💰 Maturity Amount: ₹{maturity_amount:,.2f}"
                    msg += f"\n📈 Interest Earned: ₹{simple_interest:,.2f}"
                except Exception:
                    msg += "\n⚠️ (Maturity calculation error)"
            
            app.message_label = tk.Label(app.root, text=msg, fg="green", font=label_font, bg=app.root['bg'])
            app.message_label.grid(row=999, columnspan=4, pady=10, sticky='ew')
            
        except ValueError as ve:
            # Handle validation errors
            app.message_label = tk.Label(app.root, text=f"⚠️ Validation Error: {ve}", fg="orange", font=label_font, bg=app.root['bg'])
            app.message_label.grid(row=999, columnspan=4, pady=10, sticky='ew')
            
        except Exception as e:
            # Handle other errors
            error_msg = str(e)
            if "foreign key constraint" in error_msg.lower():
                app.message_label = tk.Label(
                    app.root, 
                    text=f"❌ Database Error: Account validation failed. Please check account name.", 
                    fg="red", font=label_font, bg=app.root['bg']
                )
            else:
                app.message_label = tk.Label(
                    app.root, 
                    text=f"❌ Error: {error_msg}", 
                    fg="red", font=label_font, bg=app.root['bg']
                )
            app.message_label.grid(row=999, columnspan=4, pady=10, sticky='ew')
    tk.Button(app.root, text="Submit", command=submit, font=button_font, width=18).grid(row=100, columnspan=2, pady=15)
    account_menu.bind('<Return>', lambda e: amount_entry.focus_set())
    amount_entry.bind('<Return>', lambda e: mop_menu.focus_set())
    mop_menu.bind('<Return>', lambda e: narration_menu.focus_set())
    # Remove cheque entry keyboard navigation
    def update_mop_entry_binding(*args):
        pass  # No special binding needed anymore
    mop_var.trace_add('write', update_mop_entry_binding)
    update_mop_entry_binding()
    narration_menu.bind('<Return>', lambda e: (
        item_entry.focus_set() if narration_var.get() == 'Property' else
        fd_duration_number.focus_set() if narration_var.get() == 'FD in bank' else
        date_entry.focus_set()
    ))
    item_entry.bind('<Return>', lambda e: desc_radio1.focus_set())
    desc_radio1.bind('<Return>', lambda e: desc_radio2.focus_set())
    desc_radio2.bind('<Return>', lambda e: type_menu.focus_set())
    type_menu.bind('<Return>', lambda e: date_entry.focus_set())
    fd_duration_number.bind('<Return>', lambda e: fd_interest_entry.focus_set())
    fd_interest_entry.bind('<Return>', lambda e: date_entry.focus_set())
    date_entry.bind('<Return>', lambda e: submit())
    # Set up grid weights for alignment (fix label cutoff)
    app.root.grid_columnconfigure(0, weight=3, minsize=180)  # Label column wider
    app.root.grid_columnconfigure(1, weight=2, minsize=120)
    app.root.grid_columnconfigure(2, weight=1, minsize=80)
    app.root.grid_columnconfigure(3, weight=1, minsize=80)
    app.root.grid_columnconfigure(4, weight=1, minsize=80)
