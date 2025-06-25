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
def show_add_payment_form(app, go_back_callback):
    # Clear the window before adding the form
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()
    app.get_responsive_fonts()
    label_font = app.fonts['label']
    entry_font = app.fonts['entry']
    button_font = app.fonts['button']
    tk.Button(app.root, text="← Go Back", command=go_back_callback, font=button_font).grid(row=0, column=0, padx=10, pady=10, sticky='w')
    tk.Label(app.root, text="To (account name):", font=label_font).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    conn = db_connect.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account_name FROM accounts WHERE account_type != 'unit' ORDER BY account_name ASC")
    account_names = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    # Cheque widgets must be defined before show_cheque_field
    cheque_label = tk.Label(app.root, text="Cheque No (if cheque):", font=label_font)
    cheque_entry = tk.Entry(app.root, font=entry_font)
    # Do not grid cheque_label or cheque_entry here; only show in show_cheque_field
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
    mop_options_with_custom = ['Select', 'Cash', 'Cheque', 'Bank Transfer', 'UPI', 'Other (custom...)']
    mop_var = tk.StringVar(value='Select')
    mop_menu = tk.OptionMenu(app.root, mop_var, *mop_options_with_custom)
    mop_menu.config(font=entry_font)
    mop_menu.grid(row=3, column=1, padx=10, pady=10, sticky='ew')
    custom_mop_entry = tk.Entry(app.root, font=entry_font)
    def show_cheque_field(*args):
        if mop_var.get() == "Cheque":
            cheque_label.grid(row=3, column=3, padx=10, pady=10, sticky='e')
            cheque_entry.grid(row=3, column=4, padx=10, pady=10, sticky='ew')
        else:
            cheque_label.grid_remove()
            cheque_entry.grid_remove()
        if mop_var.get() == "Other (custom...)":
            custom_mop_entry.grid(row=3, column=2, padx=10, pady=10, sticky='ew')
        else:
            custom_mop_entry.grid_remove()
    mop_var.trace_add('write', show_cheque_field)
    show_cheque_field()
    tk.Label(app.root, text="Narration:", font=label_font).grid(row=4, column=0, padx=10, pady=10, sticky='e')
    # Narration dropdown with custom option
    NARRATION_OPTIONS = [
        "Petty", "Maintenance", "Salary", "Misc", "FD in bank", "Fund lend to other accounts",
        "Internet bill", "Article appreciation amount", "Property", "Printing of happenings"
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
    author_label = tk.Label(app.root, text="Author (for Article appreciation):", font=label_font)
    author_entry = tk.Entry(app.root, font=entry_font)
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
    PROPERTY_TYPES = ["Select", "electronic", "furniture", "stationery", "vehicle", "building"]
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
        for w in [author_label, author_entry, item_label, item_entry, desc_radio1, desc_radio2, type_label, type_menu, fd_duration_label, fd_duration_number, fd_duration_unit_menu, fd_interest_label, fd_interest_entry]:
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
    for e in [account_menu, amount_entry, cheque_entry, date_entry, remarks_entry, author_entry, item_entry, fd_duration_number, fd_interest_entry]:
        style_entry(e)
    # Validation and error labels
    # Use only widgets as keys in error_labels
    error_labels = {}
    # Map: (label, variable, widget)
    fields = [
        ("To (account name)", account_var, account_menu),
        ("Amount paid", amount_entry, amount_entry),
        ("Transaction date", date_entry, date_entry)
    ]
    if mop_var.get() == "Cheque":
        fields.append(("Cheque No", cheque_entry, cheque_entry))
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
    for _, _, widget in fields:
        error_labels[widget] = tk.Label(app.root, text='', fg='red', font=entry_font, bg=app.root['bg'])
        # Place error labels as before (grid logic)
    # Validation
    def submit(event=None):
        empty = False
        fd_unit = fd_duration_unit.get() if narration_var.get() == "FD in bank" else ''
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
                months = int(fd_num) if fd_unit == 'months' else int(fd_num) / 30
                rate = float(fd_interest_entry.get())
                maturity_amount = round(principal * (1 + (rate/100) * (months/12)), 2)
            except Exception:
                maturity_amount = None
        # Helper functions for custom dropdowns
        def get_account_value():
            return custom_account_entry.get() if account_var.get() == "Other (custom...)" else account_var.get()
        def get_mop_value():
            return custom_mop_entry.get() if mop_var.get() == "Other (custom...)" else mop_var.get()
        def get_narration_value():
            return custom_narration_entry.get() if narration_var.get() == "Other (custom...)" else narration_var.get()
        # Always pass all required arguments for each narration type
        try:
            add_payment(
                name=get_account_value(),
                amount=float(amount_entry.get()),
                mop=get_mop_value(),
                cheque_no=cheque_entry.get() if get_mop_value() == 'Cheque' else None,
                date_str=date_entry.get(),
                narration=get_narration_value(),
                author=None,
                item_name=item_entry.get() if narration_var.get() == 'Property' else None,
                description=desc_var.get() if narration_var.get() == 'Property' else None,
                item_type=type_var.get() if narration_var.get() == 'Property' else None,
                fd_duration=fd_duration_val if narration_var.get() == 'FD in bank' else None,
                fd_interest=fd_interest_entry.get() if narration_var.get() == 'FD in bank' else None,
                remarks=remarks_entry.get() if remarks_entry.get().strip() else None
            )
            msg = "✅ Payment and journal entries recorded!"
            if narration_var.get() == "FD in bank":
                try:
                    principal = float(amount_entry.get()) if amount_entry.get() else 0
                    months = int(fd_num) if fd_unit == 'months' else int(fd_num) / 30
                    rate = float(fd_interest_entry.get())
                    maturity_amount = round(principal * (1 + (rate/100) * (months/12)), 2)
                    msg += f"  Maturity Amount: {maturity_amount}"
                except Exception:
                    msg += "  (Maturity calculation error)"
            app.message_label = tk.Label(app.root, text=msg, fg="green", font=label_font, bg=app.root['bg'])
            app.message_label.grid(row=999, columnspan=4, pady=10, sticky='ew')
        except Exception as e:
            app.message_label = tk.Label(app.root, text=f"❌ Error: {e}", fg="red", font=label_font, bg=app.root['bg'])
            app.message_label.grid(row=999, columnspan=4, pady=10, sticky='ew')
    tk.Button(app.root, text="Submit", command=submit, font=button_font, width=18).grid(row=100, columnspan=2, pady=15)
    account_menu.bind('<Return>', lambda e: amount_entry.focus_set())
    amount_entry.bind('<Return>', lambda e: mop_menu.focus_set())
    mop_menu.bind('<Return>', lambda e: cheque_entry.focus_set() if mop_var.get() == 'Cheque' else narration_menu.focus_set())
    # Only bind cheque_entry if Cheque is selected
    def update_cheque_entry_binding(*args):
        if mop_var.get() == "Cheque":
            cheque_entry.bind('<Return>', lambda e: narration_menu.focus_set())
        else:
            cheque_entry.unbind('<Return>')
    mop_var.trace_add('write', update_cheque_entry_binding)
    update_cheque_entry_binding()
    narration_menu.bind('<Return>', lambda e: (
        item_entry.focus_set() if narration_var.get() == 'Property' else
        fd_duration_number.focus_set() if narration_var.get() == 'FD in bank' else
        date_entry.focus_set()
    ))
    author_entry.bind('<Return>', lambda e: date_entry.focus_set())
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
