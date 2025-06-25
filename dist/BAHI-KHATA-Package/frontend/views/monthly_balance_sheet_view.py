import tkinter as tk
from tkinter import ttk, messagebox
from db_connect import get_connection
from datetime import datetime, timedelta

def get_total_for_field(cursor, field_name, end_date):
    """Generic function to get the total sum of a field up to a certain date."""
    query = f"SELECT COALESCE(SUM({field_name}), 0) FROM journal_entries WHERE entry_date < %s"
    cursor.execute(query, (end_date,))
    return cursor.fetchone()[0] or 0

def show_monthly_balance_sheet_ui(frame, go_back_callback):
    for widget in frame.winfo_children():
        widget.destroy()

    frame.pack(fill="both", expand=True)

    # --- Top Bar for Navigation ---
    top_bar = ttk.Frame(frame, padding=("10 10 10 0"))
    top_bar.pack(fill='x')
    back_button = ttk.Button(top_bar, text="← Go Back", command=go_back_callback)
    back_button.pack(side='left')

    # --- Input Frame ---
    input_frame = ttk.Frame(frame, padding="10")
    input_frame.pack(fill='x', pady=5)

    ttk.Label(input_frame, text="Year:", font=("Georgia", 12)).pack(side='left', padx=(0, 5))
    year_entry = ttk.Entry(input_frame, width=10)
    year_entry.insert(0, datetime.now().year)
    year_entry.pack(side='left', padx=5)

    ttk.Label(input_frame, text="Month:", font=("Georgia", 12)).pack(side='left', padx=5)
    month_entry = ttk.Entry(input_frame, width=5)
    month_entry.insert(0, datetime.now().month)
    month_entry.pack(side='left', padx=5)

    # --- Treeview for Display ---
    tree_frame = ttk.Frame(frame, padding="10")
    tree_frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(tree_frame, columns=('particulars', 'amount'), show='headings')
    tree.heading('particulars', text='Particulars')
    tree.heading('amount', text='Amount (INR)')
    tree.column('particulars', width=300)
    tree.column('amount', width=150, anchor='e')
    tree.pack(fill="both", expand=True)

    def generate_balance_sheet():
        try:
            year = int(year_entry.get())
            month = int(month_entry.get())
            if not (1 <= month <= 12):
                raise ValueError("Month must be between 1 and 12")
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid year and month. Error: {e}")
            return

        for item in tree.get_children():
            tree.delete(item)

        conn = get_connection()
        cursor = conn.cursor()

        first_day_of_month = datetime(year, month, 1)
        next_month_start = (first_day_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)

        # --- CALCULATIONS ---
        # 1. Main Fund/Bank Balance
        cursor.execute("""
            SELECT
              COALESCE(SUM(CASE WHEN entry_type = 'Bank' THEN amount ELSE 0 END), 0) -
              COALESCE(SUM(CASE WHEN entry_type = 'Fund' THEN amount ELSE 0 END), 0)
            FROM journal_entries
            WHERE account_name = 'main fund' AND entry_date < %s
        """, (first_day_of_month,))
        brought_forward_bank = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT
              COALESCE(SUM(CASE WHEN entry_type = 'Bank' THEN amount ELSE 0 END), 0) as receipts,
              COALESCE(SUM(CASE WHEN entry_type = 'Fund' THEN amount ELSE 0 END), 0) as payments
            FROM journal_entries
            WHERE account_name = 'main fund' AND entry_date >= %s AND entry_date < %s
        """, (first_day_of_month, next_month_start))
        monthly_movement = cursor.fetchone()
        monthly_receipts = monthly_movement[0] or 0
        monthly_payments = monthly_movement[1] or 0
        closing_bank_balance = brought_forward_bank + monthly_receipts - monthly_payments

        # 2. Other Asset/Liability Totals (as of end of month)
        total_fd = get_total_for_field(cursor, 'fd', next_month_start)
        total_property = get_total_for_field(cursor, 'property', next_month_start)
        total_sundry = get_total_for_field(cursor, 'sundry', next_month_start)

        # --- DISPLAY ---
        tree.insert('', 'end', values=(f"Balance Sheet for {first_day_of_month.strftime('%B %Y')}", ""), tags=('header',))
        tree.tag_configure('header', font=('Georgia', 14, 'bold'))

        tree.insert('', 'end', values=("", ""))
        tree.insert('', 'end', values=("Main Fund / Bank Balance", ""), tags=('subheader',))
        tree.tag_configure('subheader', font=('Georgia', 12, 'bold'))

        tree.insert('', 'end', values=("Brought Forward Balance", f"{brought_forward_bank:,.2f}"))
        tree.insert('', 'end', values=(f"Add: Receipts in {first_day_of_month.strftime('%B')}", f"{monthly_receipts:,.2f}"))
        tree.insert('', 'end', values=(f"Less: Payments in {first_day_of_month.strftime('%B')}", f"{monthly_payments:,.2f}"))
        tree.insert('', 'end', values=("Closing Bank Balance", f"{closing_bank_balance:,.2f}"), tags=('total',))

        tree.insert('', 'end', values=("", ""))
        tree.insert('', 'end', values=("Other Assets & Liabilities", ""), tags=('subheader',))
        tree.insert('', 'end', values=("Total Fixed Deposits (FDs)", f"{total_fd:,.2f}"))
        tree.insert('', 'end', values=("Total Property Value", f"{total_property:,.2f}"))
        tree.insert('', 'end', values=("Total Sundry Credits/Debits", f"{total_sundry:,.2f}"))

        tree.tag_configure('total', font=('Georgia', 11, 'bold'))

        cursor.close()
        conn.close()

    generate_button = ttk.Button(input_frame, text="Generate Balance Sheet", command=generate_balance_sheet)
    generate_button.pack(side='left', padx=10)

    # Initial generation for the current month
    generate_balance_sheet()

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Monthly Balance Sheet")
    root.geometry("600x500")
    main_frame = ttk.Frame(root)
    show_monthly_balance_sheet_ui(main_frame, lambda: print("Go back button clicked!"))
    root.mainloop()
