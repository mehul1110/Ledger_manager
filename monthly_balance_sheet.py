from db_connect import get_connection
from datetime import datetime, timedelta

def display_monthly_balance_sheet(year, month):
    conn = get_connection()
    cursor = conn.cursor()
    # Get first and last day of the month
    first_day = datetime(year, month, 1)
    if month == 12:
        last_day = datetime(year+1, 1, 1)
    else:
        last_day = datetime(year, month+1, 1)
    # Calculate brought forward (opening) balances up to the end of previous month
    opening_day = first_day - timedelta(days=1)
    cursor.execute("""
        SELECT SUM(COALESCE(amount,0)), SUM(COALESCE(fd,0)), SUM(COALESCE(sundry,0)), SUM(COALESCE(property,0))
        FROM journal_entries
        WHERE entry_date < %s
    """, (first_day,))
    opening_amount, opening_fd, opening_sundry, opening_property = cursor.fetchone()
    cursor.execute("""
        SELECT SUM(COALESCE(amount,0)) FROM journal_entries
        WHERE entry_date < %s AND LOWER(account_name) = 'main fund'
    """, (first_day,))
    opening_main_fund = cursor.fetchone()[0] or 0
    # Calculate totals for the current month
    cursor.execute("""
        SELECT SUM(COALESCE(amount,0)), SUM(COALESCE(fd,0)), SUM(COALESCE(sundry,0)), SUM(COALESCE(property,0))
        FROM journal_entries
        WHERE entry_date >= %s AND entry_date < %s
    """, (first_day, last_day))
    total_amount, total_fd, total_sundry, total_property = cursor.fetchone()
    cursor.execute("""
        SELECT SUM(COALESCE(amount,0)) FROM journal_entries
        WHERE entry_date >= %s AND entry_date < %s AND LOWER(account_name) = 'main fund'
    """, (first_day, last_day))
    total_main_fund = cursor.fetchone()[0] or 0
    print(f"\nBalance Sheet for {first_day.strftime('%B %Y')}")
    print("Opening (Brought Forward) Balances:")
    print(f"Amount: {opening_amount or 0} | FD: {opening_fd or 0} | Sundry: {opening_sundry or 0} | Property: {opening_property or 0} | Main Fund: {opening_main_fund}")
    print("-"*50)
    print("This Month's Totals:")
    print("Amount | FD | Sundry | Property | Main Fund")
    print("-"*50)
    print(f"{total_amount or 0} | {total_fd or 0} | {total_sundry or 0} | {total_property or 0} | {total_main_fund}")
    
    # --- Closing Balances (to be carried to next month) ---
    closing_amount = (opening_amount or 0) + (total_amount or 0)
    closing_fd = (opening_fd or 0) + (total_fd or 0)
    closing_sundry = (opening_sundry or 0) + (total_sundry or 0)
    closing_property = (opening_property or 0) + (total_property or 0)
    closing_main_fund = (opening_main_fund or 0) + (total_main_fund or 0)
    print("-"*50)
    print("Closing Balances (Carried Forward to Next Month):")
    print(f"Amount: {closing_amount} | FD: {closing_fd} | Sundry: {closing_sundry} | Property: {closing_property} | Main Fund: {closing_main_fund}")
    print("-"*50)
    # --- Double Entry Check Tables (using ID prefixes, amount only) ---
    # Set your counter entry prefix here:
    COUNTER_PREFIX = 'C'  # Change as per your convention

    # Table 1: Totals from normal entries (not starting with counter prefix)
    cursor.execute("""
        SELECT COUNT(*), SUM(COALESCE(amount,0))
        FROM journal_entries
        WHERE entry_date >= %s AND entry_date < %s AND (entry_id NOT LIKE %s)
    """, (first_day, last_day, COUNTER_PREFIX + '%'))
    t1_count, t1_total = cursor.fetchone()
    print("\n[Table 1] Normal Entries Totals (amount only):")
    print(f"Count: {t1_count} | Total Amount: {t1_total or 0}")

    # Table 2: Total from all counter entries (entry_id starts with counter prefix)
    cursor.execute("""
        SELECT COUNT(*), SUM(COALESCE(amount,0))
        FROM journal_entries
        WHERE entry_date >= %s AND entry_date < %s AND entry_id LIKE %s
    """, (first_day, last_day, COUNTER_PREFIX + '%'))
    t2_count, t2_total = cursor.fetchone()
    print("\n[Table 2] Counter Entries Total (amount only):")
    print(f"Count: {t2_count} | Total Amount: {t2_total or 0}")

    # Double entry check
    if (t1_total or 0) == (t2_total or 0):
        print("\n✅ Double entry check PASSED: Both totals are equal.")
    else:
        print("\n❌ Double entry check FAILED: Totals do not match!")
        # Print all unique prefixes for debugging
        cursor.execute("""
            SELECT DISTINCT LEFT(entry_id, 1) FROM journal_entries WHERE entry_date >= %s AND entry_date < %s
        """, (first_day, last_day))
        prefixes = [row[0] for row in cursor.fetchall()]
        print(f"Unique entry_id prefixes for this month: {prefixes}")

    # --- Monthly Summary Table ---
    print("\n==== Monthly Ledger Summary Table ====")
    # Sum of each field for all receipts and payments (i.e., all journal_entries for the month)
    cursor.execute("""
        SELECT 
            COALESCE(SUM(fd),0), 
            COALESCE(SUM(property),0), 
            COALESCE(SUM(amount),0), 
            COALESCE(SUM(sundry),0)
        FROM journal_entries
        WHERE entry_date >= %s AND entry_date < %s
    """, (first_day, last_day))
    sum_fd, sum_property, sum_amount, sum_sundry = cursor.fetchone()

    # Total under main fund for the month
    cursor.execute("""
        SELECT COALESCE(SUM(amount),0) FROM journal_entries
        WHERE entry_date >= %s AND entry_date < %s AND LOWER(account_name) = 'main fund'
    """, (first_day, last_day))
    sum_main_fund = cursor.fetchone()[0]

    print(f"FD: {sum_fd} | Property: {sum_property} | Amount: {sum_amount} | Sundry: {sum_sundry} | Main Fund: {sum_main_fund}")
    print(f"Sum of FD+Property+Amount+Sundry: {sum_fd + sum_property + sum_amount + sum_sundry}")
    if (sum_main_fund == sum_fd + sum_property + sum_amount + sum_sundry):
        print("\n✅ Main Fund matches sum of all fields. Double entry integrity OK.")
    else:
        print("\n❌ Main Fund does NOT match sum of all fields! Check entries.")

    cursor.close()
    conn.close()

def prompt_and_display():
    from datetime import datetime
    conn = get_connection()
    cursor = conn.cursor()
    # Get all unique months with entries, sorted descending
    cursor.execute("""
        SELECT DISTINCT YEAR(entry_date) AS y, MONTH(entry_date) AS m
        FROM journal_entries
        ORDER BY y DESC, m DESC
    """)
    months = cursor.fetchall()
    cursor.close()
    conn.close()
    # Only show up to 4 most recent months
    months = months[:4]
    if not months:
        print("No entries found.")
        return
    # Automatically select the most recent month
    y, m = months[0]
    display_monthly_balance_sheet(y, m)

if __name__ == "__main__":
    prompt_and_display()
