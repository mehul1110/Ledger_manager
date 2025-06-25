from db_connect import get_connection
from datetime import datetime

def monthly_balance_sheet(year, month):
    conn = get_connection()
    cursor = conn.cursor()
    # Get first and last day of the month
    first_day = datetime(year, month, 1)
    if month == 12:
        last_day = datetime(year+1, 1, 1)
    else:
        last_day = datetime(year, month+1, 1)

    print(f"\nBalance Sheet for {first_day.strftime('%B %Y')}")
    print("-"*60)

    # --- Receipts (Income) ---
    cursor.execute("""
        SELECT account_name, amount, narration, mop, cheque_no, entry_date
        FROM journal_entries
        WHERE entry_type = 'Bank' AND LOWER(account_name) = 'main fund' AND entry_date >= %s AND entry_date < %s
    """, (first_day, last_day))
    receipts = cursor.fetchall()
    total_receipts = 0
    print("RECEIPTS (Money In):")
    for row in receipts:
        acc, amt, narr, mop, cheque, dt = row
        print(f"  {dt} | {acc} | {amt} | {narr} | {mop} | {cheque}")
        total_receipts += amt or 0
    print(f"Total Receipts: {total_receipts}")
    print("-"*60)

    # --- Payments (Outgoing) ---
    cursor.execute("""
        SELECT account_name, amount, narration, mop, cheque_no, entry_date
        FROM journal_entries
        WHERE entry_type = 'Fund' AND LOWER(account_name) = 'main fund' AND entry_date >= %s AND entry_date < %s
    """, (first_day, last_day))
    payments = cursor.fetchall()
    total_payments = 0
    print("PAYMENTS (Money Out):")
    for row in payments:
        acc, amt, narr, mop, cheque, dt = row
        print(f"  {dt} | {acc} | {amt} | {narr} | {mop} | {cheque}")
        total_payments += amt or 0
    print(f"Total Payments: {total_payments}")
    print("-"*60)

    # --- Sundry, FD, Property columns ---
    # Property column should show sum of all current property values (after depreciation), only for non-expendable
    # Depreciation starts only after 2 years from purchase date
    cursor.execute("""
        SELECT COALESCE(SUM(
            CASE 
                WHEN description = 'non-expendable' AND DATEDIFF(%s, purchase_date) > 730 THEN value
                WHEN description = 'non-expendable' AND DATEDIFF(%s, purchase_date) <= 730 THEN value
                ELSE 0
            END
        ), 0)
        FROM property_details
        WHERE description = 'non-expendable' AND purchase_date <= %s
    """, (last_day, last_day, last_day))
    total_property = cursor.fetchone()[0]
    print(f"Cumulative Property asset value (non-expendable, after depreciation if >2 years, till this month): {total_property}")

    # Show monthly FD and Sundry totals as well
    cursor.execute("""
        SELECT COALESCE(SUM(fd),0), COALESCE(SUM(sundry),0)
        FROM journal_entries
        WHERE entry_date >= %s AND entry_date < %s
    """, (first_day, last_day))
    sum_fd, sum_sundry = cursor.fetchone()
    print(f"FD column total (this month): {sum_fd}")
    print(f"Sundry column total (this month): {sum_sundry}")
    print("-"*60)

    # --- Tally Check ---
    net_fund_change = total_receipts - total_payments
    print(f"Net Main Fund Change (Receipts - Payments): {net_fund_change}")
    # Sum of all main fund entries (Bank - Fund)
    cursor.execute("""
        SELECT COALESCE(SUM(CASE WHEN entry_type='Bank' THEN amount ELSE 0 END),0) - COALESCE(SUM(CASE WHEN entry_type='Fund' THEN amount ELSE 0 END),0)
        FROM journal_entries
        WHERE LOWER(account_name) = 'main fund' AND entry_date >= %s AND entry_date < %s
    """, (first_day, last_day))
    main_fund_balance = cursor.fetchone()[0]
    print(f"Main Fund Book Balance (should match net change): {main_fund_balance}")
    if main_fund_balance == net_fund_change:
        print("\n✅ Main fund tally PASSED.")
    else:
        print("\n❌ Main fund tally FAILED! Check entries.")
    print("-"*60)

    # --- Store closing balance as opening for next month ---
    # Find next month's first day
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    next_month_first = datetime(next_year, next_month, 1)
    # Store in a table (create if not exists): monthly_main_fund_balance (month VARCHAR(7) PRIMARY KEY, opening DECIMAL(12,2), closing DECIMAL(12,2))
    month_str = f"{year}-{str(month).zfill(2)}"
    next_month_str = f"{next_year}-{str(next_month).zfill(2)}"

    # Get previous closing as opening for this month
    # If opening is None, set it to previous month's closing
    # Loop back to find the last non-null closing if needed
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1
    found = False
    while not found and prev_year >= 2000:  # reasonable lower bound
        prev_month_str = f"{prev_year}-{str(prev_month).zfill(2)}"
        cursor.execute("SELECT closing FROM monthly_main_fund_balance WHERE month = %s", (prev_month_str,))
        prev_closing = cursor.fetchone()
        if prev_closing and prev_closing[0] is not None:
            opening_balance = prev_closing[0]
            found = True
        else:
            prev_month -= 1
            if prev_month == 0:
                prev_month = 12
                prev_year -= 1
    if not found:
        opening_balance = 0.0
    # Set opening for this month if not already set
    cursor.execute("SELECT opening, closing FROM monthly_main_fund_balance WHERE month = %s", (month_str,))
    existing = cursor.fetchone()
    if not existing:
        # No record for this month, insert with opening and closing
        cursor.execute("""
            INSERT INTO monthly_main_fund_balance (month, opening, closing)
            VALUES (%s, %s, %s)
        """, (month_str, opening_balance, main_fund_balance))
    else:
        existing_opening, existing_closing = existing
        # If opening is None or 0, update it to opening_balance
        if existing_opening is None or existing_opening == 0:
            cursor.execute("UPDATE monthly_main_fund_balance SET opening=%s WHERE month=%s", (opening_balance, month_str))
        # Always update closing to current main_fund_balance
        cursor.execute("UPDATE monthly_main_fund_balance SET closing=%s WHERE month=%s", (main_fund_balance, month_str))
    # Set next month's opening to this month's closing
    cursor.execute("""
        INSERT INTO monthly_main_fund_balance (month, opening, closing)
        VALUES (%s, %s, NULL)
        ON DUPLICATE KEY UPDATE opening=VALUES(opening)
    """, (next_month_str, main_fund_balance))
    conn.commit()
    print(f"Opening balance for {next_month_str} set to {main_fund_balance}")
    print(f"Opening balance for {month_str}: {opening_balance}")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    # Prompt user for year and month
    try:
        year = int(input("Enter year (e.g. 2024): ").strip())
        month = int(input("Enter month (1-12): ").strip())
        if 1 <= month <= 12:
            monthly_balance_sheet(year, month)
        else:
            print("Invalid month. Please enter a value from 1 to 12.")
    except Exception as e:
        print(f"Invalid input: {e}")
