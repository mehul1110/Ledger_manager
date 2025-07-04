import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

# Ensure the root directory is in the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from db_connect import get_connection

def get_total_for_field(cursor, field_name, end_date):
    """Generic function to get the total sum of a field up to a certain date from counter-entries."""
    query = f"""
        SELECT COALESCE(SUM({field_name}), 0)
        FROM journal_entries
        WHERE {field_name} IS NOT NULL
          AND entry_date < %s
          AND entry_id LIKE 'C%%'
    """
    cursor.execute(query, (end_date,))
    result = cursor.fetchone()[0] or 0
    return result

def get_balance_sheet_data_for_month(year, month):
    """Calculates all necessary balance sheet figures for a given month."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        first_day_of_month = datetime(year, month, 1)
        next_month_start = (first_day_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)

        # 1. Main Fund/Bank Balance (Brought Forward) - from NORMAL entries
        query_brought_forward = """
            SELECT
                (SELECT COALESCE(SUM(amount), 0) FROM journal_entries WHERE entry_type = 'Fund' AND entry_id NOT LIKE 'C%%' AND entry_date < %s) - 
                (SELECT COALESCE(SUM(amount), 0) FROM journal_entries WHERE entry_type = 'Bank' AND entry_id NOT LIKE 'C%%' AND entry_date < %s)
        """
        cursor.execute(query_brought_forward, (first_day_of_month, first_day_of_month))
        brought_forward_bank = cursor.fetchone()[0] or 0

        # Monthly movements for Main Fund - from NORMAL entries
        query_monthly_movements = """
            SELECT
              (SELECT COALESCE(SUM(amount), 0) FROM journal_entries WHERE entry_type = 'Fund' AND entry_id NOT LIKE 'C%%' AND entry_date >= %s AND entry_date < %s) as receipts,
              (SELECT COALESCE(SUM(amount), 0) FROM journal_entries WHERE entry_type = 'Bank' AND entry_id NOT LIKE 'C%%' AND entry_date >= %s AND entry_date < %s) as payments
        """
        cursor.execute(query_monthly_movements, (first_day_of_month, next_month_start, first_day_of_month, next_month_start))
        monthly_movement = cursor.fetchone()
        monthly_receipts = monthly_movement[0] or 0
        monthly_payments = monthly_movement[1] or 0
        closing_bank_balance = brought_forward_bank + monthly_receipts - monthly_payments

        # 2. Other Asset/Liability Totals (as of end of month) - from COUNTER entries
        total_fd = get_total_for_field(cursor, 'fd', next_month_start)
        total_property = get_total_for_field(cursor, 'property', next_month_start)
        total_sundry = get_total_for_field(cursor, 'sundry', next_month_start)

        # Fund Balance (Receipts - Payments from counter-entries)
        query_fund = """
            SELECT 
                (SELECT COALESCE(SUM(fund), 0) FROM journal_entries WHERE entry_id LIKE 'CERV%%' AND entry_date < %s) -
                (SELECT COALESCE(SUM(fund), 0) FROM journal_entries WHERE entry_id LIKE 'CEPV%%' AND entry_date < %s)
        """
        cursor.execute(query_fund, (next_month_start, next_month_start))
        total_fund = (cursor.fetchone()[0] or 0)

        return {
            "brought_forward_bank": brought_forward_bank,
            "monthly_receipts": monthly_receipts,
            "monthly_payments": monthly_payments,
            "closing_bank_balance": closing_bank_balance,
            "total_fd": total_fd,
            "total_property": total_property,
            "total_sundry": total_sundry,
            "total_fund": total_fund,
        }
    finally:
        cursor.close()
        conn.close()

def show_comparison_view(frame, go_back_callback):
    for widget in frame.winfo_children():
        widget.destroy()
    frame.pack(fill="both", expand=True)

    # --- Top Bar for Navigation ---
    top_bar = ttk.Frame(frame, padding=("10 10 10 0"))
    top_bar.pack(fill='x')
    back_button = ttk.Button(top_bar, text="← Go Back", command=go_back_callback)
    back_button.pack(side='left')
    
    header = ttk.Label(top_bar, text="Monthly Balance Sheet Comparison", font=("Georgia", 16, "bold"))
    header.pack(side='left', padx=20)


    # --- Input Frame ---
    input_frame = ttk.Frame(frame, padding="10")
    input_frame.pack(fill='x', pady=5)

    # Month 1
    ttk.Label(input_frame, text="Year 1:", font=("Georgia", 12)).pack(side='left', padx=(0, 5))
    year1_entry = ttk.Entry(input_frame, width=8)
    year1_entry.insert(0, datetime.now().year)
    year1_entry.pack(side='left', padx=5)

    ttk.Label(input_frame, text="Month 1:", font=("Georgia", 12)).pack(side='left', padx=5)
    month1_entry = ttk.Entry(input_frame, width=5)
    month1_entry.insert(0, datetime.now().month)
    month1_entry.pack(side='left', padx=5)

    # Month 2
    ttk.Label(input_frame, text="Year 2:", font=("Georgia", 12)).pack(side='left', padx=(20, 5))
    year2_entry = ttk.Entry(input_frame, width=8)
    year2_entry.insert(0, datetime.now().year)
    year2_entry.pack(side='left', padx=5)

    ttk.Label(input_frame, text="Month 2:", font=("Georgia", 12)).pack(side='left', padx=5)
    month2_entry = ttk.Entry(input_frame, width=5)
    # Set default to last month
    last_month = datetime.now() - timedelta(days=datetime.now().day)
    month2_entry.insert(0, last_month.month)
    year2_entry.delete(0, tk.END)
    year2_entry.insert(0, last_month.year)
    month2_entry.pack(side='left', padx=5)


    # --- Treeview for Display ---
    tree_frame = ttk.Frame(frame, padding="10")
    tree_frame.pack(fill="both", expand=True)

    columns = ('particulars', 'month1', 'month2')
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
    tree.heading('particulars', text='Particulars')
    tree.heading('month1', text='Period 1')
    tree.heading('month2', text='Period 2')
    tree.column('particulars', width=350)
    tree.column('month1', width=180, anchor='e')
    tree.column('month2', width=180, anchor='e')
    tree.pack(fill="both", expand=True)

    def generate_comparison():
        try:
            year1 = int(year1_entry.get())
            month1 = int(month1_entry.get())
            year2 = int(year2_entry.get())
            month2 = int(month2_entry.get())
            if not (1 <= month1 <= 12 and 1 <= month2 <= 12):
                raise ValueError("Month must be between 1 and 12")
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid year and month. Error: {e}")
            return

        for item in tree.get_children():
            tree.delete(item)

        try:
            data1 = get_balance_sheet_data_for_month(year1, month1)
            data2 = get_balance_sheet_data_for_month(year2, month2)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to fetch data: {e}")
            return
            
        month1_str = datetime(year1, month1, 1).strftime('%b %Y')
        month2_str = datetime(year2, month2, 1).strftime('%b %Y')
        tree.heading('month1', text=f'Amount for {month1_str} (INR)')
        tree.heading('month2', text=f'Amount for {month2_str} (INR)')

        # --- DISPLAY ---
        tree.insert('', 'end', values=("Main Fund / Bank Balance", "", ""), tags=('subheader',))
        
        tree.insert('', 'end', values=(
            "Brought Forward Balance", 
            f"{data1['brought_forward_bank']:,.2f}", 
            f"{data2['brought_forward_bank']:,.2f}"
        ))
        tree.insert('', 'end', values=(
            f"Add: Receipts", 
            f"{data1['monthly_receipts']:,.2f}", 
            f"{data2['monthly_receipts']:,.2f}"
        ))
        tree.insert('', 'end', values=(
            f"Less: Payments", 
            f"{data1['monthly_payments']:,.2f}", 
            f"{data2['monthly_payments']:,.2f}"
        ))
        tree.insert('', 'end', values=(
            "Closing Bank Balance", 
            f"{data1['closing_bank_balance']:,.2f}", 
            f"{data2['closing_bank_balance']:,.2f}"
        ), tags=('total',))

        tree.insert('', 'end', values=("", "", ""))
        tree.insert('', 'end', values=("Other Assets & Liabilities", "", ""), tags=('subheader',))
        
        tree.insert('', 'end', values=(
            "Total Fixed Deposits (FDs)", 
            f"{data1['total_fd']:,.2f}", 
            f"{data2['total_fd']:,.2f}"
        ))
        tree.insert('', 'end', values=(
            "Total Property Value", 
            f"{data1['total_property']:,.2f}", 
            f"{data2['total_property']:,.2f}"
        ))
        tree.insert('', 'end', values=(
            "Total Sundry Credits/Debits", 
            f"{data1['total_sundry']:,.2f}", 
            f"{data2['total_sundry']:,.2f}"
        ))
        tree.insert('', 'end', values=(
            "Total Fund", 
            f"{data1['total_fund']:,.2f}", 
            f"{data2['total_fund']:,.2f}"
        ), tags=('total',))

        tree.insert('', 'end', values=("", "", "")) # Spacer

        # --- COMPARATIVE ANALYSIS ---
        tree.insert('', 'end', values=("Comparative Analysis", "Change Details", ""), tags=('subheader',))

        def get_change_details(val1, val2):
            diff = val2 - val1
            if diff > 1e-6:  # Use a small epsilon for float comparison
                return f"Increased by {diff:,.2f}", "increase"
            elif diff < -1e-6:
                return f"Decreased by {abs(diff):,.2f}", "decrease"
            return "No change", "no_change"

        analysis_items = [
            ("Change in Closing Bank Balance", data1['closing_bank_balance'], data2['closing_bank_balance']),
            ("Change in Total FDs", data1['total_fd'], data2['total_fd']),
            ("Change in Total Property", data1['total_property'], data2['total_property']),
            ("Change in Total Sundry", data1['total_sundry'], data2['total_sundry']),
            ("Change in Total Fund", data1['total_fund'], data2['total_fund'])
        ]

        for label, val1, val2 in analysis_items:
            change_text, tag = get_change_details(val1, val2)
            tree.insert('', 'end', values=(label, change_text, ""), tags=(tag,))

        # --- STYLING ---
        tree.tag_configure('subheader', font=('Georgia', 12, 'bold'))
        tree.tag_configure('total', font=('Georgia', 11, 'bold'))
        tree.tag_configure('increase', font=('Georgia', 10, 'italic'), foreground='green')
        tree.tag_configure('decrease', font=('Georgia', 10, 'italic'), foreground='red')
        tree.tag_configure('no_change', font=('Georgia', 10, 'italic'), foreground='grey')


    compare_button = ttk.Button(input_frame, text="Generate Comparison", command=generate_comparison)
    compare_button.pack(side='left', padx=20)

    # Initial generation
    generate_comparison()

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Balance Sheet Comparison")
    root.geometry("800x600")
    main_frame = ttk.Frame(root)
    show_comparison_view(main_frame, lambda: root.destroy())
    root.mainloop()
