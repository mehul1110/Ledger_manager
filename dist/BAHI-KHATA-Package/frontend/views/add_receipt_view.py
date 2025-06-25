import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
from tkcalendar import Calendar
from add_receipt import add_receipt
import db_connect

def show_add_receipt_form(app, go_back_callback):
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
    cursor.execute("SELECT account_name FROM accounts WHERE account_type = 'unit' ORDER BY account_name ASC")
    unit_accounts = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    # Add 'Select' as the first/default option for all dropdowns
    unit_accounts_with_custom = ['Select'] + unit_accounts + ["Other (custom...)"]
    account_var = tk.StringVar(value='Select')
    mop_options_with_custom = ['Select', 'Cash', 'Cheque', 'Bank Transfer', 'UPI', 'Other (custom...)']
    mop_var = tk.StringVar(value='Select')
    RECEIPT_NARRATION_OPTIONS_WITH_CUSTOM = ['Select', 'UCS', 'Interest on FD', 'Other (custom...)']
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
    add_row("From (account name):", account_menu, account_var, custom_account_entry)
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

    # Cheque widgets must be defined before on_mop_change
    cheque_label = tk.Label(app.root, text="Cheque No (if cheque):", font=label_font)
    cheque_entry = tk.Entry(app.root, width=25, font=entry_font)
    error_labels[cheque_entry] = tk.Label(app.root, text='', fg='red', font=entry_font, bg=app.root['bg'])
    # Do not grid cheque_label or cheque_entry here; only show in on_mop_change

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
        top.title("Select Date")
        cal = Calendar(top, selectmode='day', date_pattern='dd-mm-yyyy')
        cal.pack(padx=10, pady=10)
        def set_date():
            date_var.set(cal.get_date())
            top.destroy()
        tk.Button(top, text="Select", command=set_date).pack(pady=5)
    cal_btn = tk.Button(app.root, text="📅", command=open_calendar, font=button_font)
    cal_btn.grid(row=row, column=2, padx=5, pady=8, sticky='w')
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
        if mop_var.get() == "Cheque":
            cheque_label.grid(row=row, column=0, padx=10, pady=8, sticky='e')
            cheque_entry.grid(row=row, column=1, padx=10, pady=8, sticky='w')
            error_labels[cheque_entry].grid(row=row, column=2, padx=5, sticky='w')
        else:
            cheque_label.grid_forget()
            cheque_entry.grid_forget()
            error_labels[cheque_entry].grid_forget()
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
        return custom_account_entry.get() if account_var.get() == "Other (custom...)" else account_var.get()
    def get_mop_value():
        return custom_mop_entry.get() if mop_var.get() == "Other (custom...)" else mop_var.get()
    def get_narration_value():
        return custom_narration_entry.get() if narration_var.get() == "Other (custom...)" else narration_var.get()

    # --- Validation and Submission ---
    def submit(event=None):
        empty = False
        # Build list of all visible entries to validate
        entries = [amount_entry, narration_menu, date_entry]
        if mop_var.get() == 'Cheque':
            entries.append(cheque_entry)
        if account_var.get() == 'Other (custom...)':
            entries.append(custom_account_entry)
        if mop_var.get() == 'Other (custom...)':
            entries.append(custom_mop_entry)
        if narration_var.get() == 'Other (custom...)':
            entries.append(custom_narration_entry)
        # Validate
        for entry in entries:
            value = entry.get() if hasattr(entry, 'get') else narration_var.get() if entry == narration_menu else entry.get()
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
        if empty:
            return
        try:
            add_receipt(
                account_name=get_account_value(),
                amount=float(amount_entry.get()),
                mop=get_mop_value(),
                narration=get_narration_value(),
                date_str=date_entry.get(),
                remarks=cheque_entry.get() if mop_var.get() == 'Cheque' else None
            )
            tk.Label(app.root, text="✅ Receipt and journal entries recorded!", fg="green", font=label_font).grid(row=row+1, columnspan=3, pady=10)
        except Exception as e:
            tk.Label(app.root, text=f"❌ Error: {e}", fg="red", font=label_font).grid(row=row+1, columnspan=3, pady=10)
    tk.Button(app.root, text="Submit", command=submit, width=18, font=button_font).grid(row=row, columnspan=2, pady=15)
    # Keyboard navigation
    account_menu.bind('<Return>', lambda e: amount_entry.focus_set())
    amount_entry.bind('<Return>', lambda e: mop_menu.focus_set())
    mop_menu.bind('<Return>', lambda e: cheque_entry.focus_set() if mop_var.get() == 'Cheque' else narration_menu.focus_set())
    cheque_entry.bind('<Return>', lambda e: narration_menu.focus_set())
    narration_menu.bind('<Return>', lambda e: date_entry.focus_set())
    date_entry.bind('<Return>', lambda e: submit())
    # Set up grid weights for alignment (fix label cutoff)
    app.root.grid_columnconfigure(0, weight=3, minsize=180)  # Label column wider
    app.root.grid_columnconfigure(1, weight=2, minsize=120)
    app.root.grid_columnconfigure(2, weight=1, minsize=80)
    app.root.grid_columnconfigure(3, weight=1, minsize=80)
    app.root.grid_columnconfigure(4, weight=1, minsize=80)