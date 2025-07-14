import tkinter as tk
from tkinter import ttk, messagebox
from db_connect import get_connection
import db_connect
from datetime import datetime, timedelta

def get_total_for_field(cursor, field_name, end_date):
    """Generic function to get the total sum of a field up to a certain date."""
    # This query now correctly sums values from specialized columns in counter-entries
    # and includes the opening balance for the field.
    query = f"""
        SELECT COALESCE(SUM({field_name}), 0)
        FROM journal_entries
        WHERE {field_name} IS NOT NULL
          AND entry_date < %s
          AND (entry_id LIKE 'C%%' OR narration = 'Opening Balances')
    """
    cursor.execute(query, (end_date,))
    result = cursor.fetchone()[0] or 0
    print(f"[DEBUG] Total for {field_name} up to {end_date}: {result}")
    return result

def get_monthly_for_field(cursor, field_name, start_date, end_date):
    """Generic function to get the sum of a field for a specific month from counter-entries."""
    query = f"""
        SELECT COALESCE(SUM({field_name}), 0)
        FROM journal_entries
        WHERE {field_name} IS NOT NULL
          AND entry_date >= %s AND entry_date < %s
          AND entry_id LIKE 'C%%'
    """
    cursor.execute(query, (start_date, end_date))
    result = cursor.fetchone()[0] or 0
    print(f"[DEBUG] Monthly total for {field_name} from {start_date} to {end_date}: {result}")
    return result

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
        end_last_month = first_day_of_month - timedelta(days=1)

        # --- CALCULATIONS ---
        print(f"[DEBUG] First day of month: {first_day_of_month}, Next month start: {next_month_start}")

        # 1. Main Fund/Bank Balance (Brought Forward) - from NORMAL entries plus Opening Balance
        query_brought_forward = """
            SELECT
                (
                    (SELECT COALESCE(SUM(amount), 0) FROM journal_entries WHERE entry_type = 'Fund' AND entry_id NOT LIKE 'C%%' AND entry_date < %s) - 
                    (SELECT COALESCE(SUM(amount), 0) FROM journal_entries WHERE entry_type = 'Bank' AND entry_id NOT LIKE 'C%%' AND entry_date < %s) +
                    (SELECT COALESCE(SUM(amount), 0) FROM journal_entries WHERE narration = 'Opening Balances' AND entry_date < %s)
                )
        """
        print(f"[DEBUG] Query for brought forward balance: {query_brought_forward}")
        cursor.execute(query_brought_forward, (first_day_of_month, first_day_of_month, first_day_of_month))
        brought_forward_bank = cursor.fetchone()[0] or 0
        print(f"[DEBUG] Brought forward bank balance (including opening balance): {brought_forward_bank}")

        # Monthly movements for Main Fund - from NORMAL entries
        query_monthly_movements = """
            SELECT
              (SELECT COALESCE(SUM(amount), 0) FROM journal_entries WHERE entry_type = 'Fund' AND entry_id NOT LIKE 'C%%' AND entry_date >= %s AND entry_date < %s) as receipts,
              (SELECT COALESCE(SUM(amount), 0) FROM journal_entries WHERE entry_type = 'Bank' AND entry_id NOT LIKE 'C%%' AND entry_date >= %s AND entry_date < %s) as payments
        """
        print(f"[DEBUG] Query for monthly movements: {query_monthly_movements}")
        cursor.execute(query_monthly_movements, (first_day_of_month, next_month_start, first_day_of_month, next_month_start))
        monthly_movement = cursor.fetchone()
        print(f"[DEBUG] Monthly movement raw result: {monthly_movement}")
        monthly_receipts = monthly_movement[0] or 0
        monthly_payments = monthly_movement[1] or 0
        closing_bank_balance = brought_forward_bank + monthly_receipts - monthly_payments
        print(f"[DEBUG] Monthly receipts: {monthly_receipts}, Monthly payments: {monthly_payments}, Closing bank balance: {closing_bank_balance}")

        # 2. Other Asset/Liability Totals (as of end of month) - from COUNTER entries
        total_fd = get_total_for_field(cursor, 'fd', next_month_start)
        total_property = get_total_for_field(cursor, 'property', next_month_start)
        total_sundry = get_total_for_field(cursor, 'sundry', next_month_start)
        total_cash = get_total_for_field(cursor, 'cash', next_month_start)

        # Calculate monthly changes for assets/liabilities
        month_name = first_day_of_month.strftime('%B')
        monthly_fd = get_monthly_for_field(cursor, 'fd', first_day_of_month, next_month_start)
        monthly_property = get_monthly_for_field(cursor, 'property', first_day_of_month, next_month_start)
        monthly_sundry = get_monthly_for_field(cursor, 'sundry', first_day_of_month, next_month_start)

        # Fund Balance (Receipts - Payments from counter-entries) + Opening Fund Balance
        query_fund = """
            SELECT 
                (
                    (SELECT COALESCE(SUM(fund), 0) FROM journal_entries WHERE entry_id LIKE 'CERV%%' AND entry_date < %s) -
                    (SELECT COALESCE(SUM(fund), 0) FROM journal_entries WHERE entry_id LIKE 'CEPV%%' AND entry_date < %s) +
                    (SELECT COALESCE(SUM(fund), 0) FROM journal_entries WHERE narration = 'Opening Balances' AND entry_date < %s)
                ) AS total_fund
        """
        cursor.execute(query_fund, (next_month_start, next_month_start, next_month_start))
        total_fund_result = cursor.fetchone()
        total_fund = total_fund_result[0] if total_fund_result and total_fund_result[0] is not None else 0

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
        
        tree.insert('', 'end', values=(f"Fixed Deposits (FDs) in {month_name}", f"{monthly_fd:,.2f}"))
        tree.insert('', 'end', values=("Total Fixed Deposits (FDs)", f"{total_fd:,.2f}"))
        
        tree.insert('', 'end', values=(f"Property Value added in {month_name}", f"{monthly_property:,.2f}"))
        tree.insert('', 'end', values=("Total Property Value", f"{total_property:,.2f}"))

        tree.insert('', 'end', values=(f"Sundry Credits/Debits in {month_name}", f"{monthly_sundry:,.2f}"))
        tree.insert('', 'end', values=("Total Sundry Credits/Debits", f"{total_sundry:,.2f}"))

        tree.insert('', 'end', values=("Total Fund", f"{total_fund:,.2f}"))
        tree.insert('', 'end', values=("Total Cash", f"{total_cash:,.2f}"))

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
