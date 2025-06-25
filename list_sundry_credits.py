from db_connect import get_connection
from datetime import datetime, date
from calendar import monthrange

# Account types to exclude from payment expectation
EXCLUDE_TYPES = ['main fund', 'bank', 'cash']

# Financial year calculation
def get_financial_year_dates(ref_date=None):
    if ref_date is None:
        ref_date = date.today()
    year = ref_date.year
    if ref_date.month < 4:
        start = date(year-1, 4, 1)
        end = date(year, 3, 31)
    else:
        start = date(year, 4, 1)
        end = date(year+1, 3, 31)
    return start, end

# Table to store monthly outstanding (create this table in your DB):
# CREATE TABLE IF NOT EXISTS monthly_sundry_outstanding (
#   month VARCHAR(6) PRIMARY KEY,  -- YYYYMM
#   brought_forward INT,
#   current_outstanding INT
# );

def get_prev_month(year, month):
    if month == 1:
        return year - 1, 12
    else:
        return year, month - 1

def list_sundry_Funds():
    conn = get_connection()
    cursor = conn.cursor()
    fy_start, fy_end = get_financial_year_dates()
    print(f"\nFinancial Year: {fy_start} to {fy_end}")

    # Get all accounts expected to pay (only type 'unit')
    cursor.execute("SELECT account_name FROM accounts WHERE account_type = %s", ('unit',))
    accounts = [row[0] for row in cursor.fetchall()]

    # Get current financial year for entry id
    today = date.today()
    # Force financial year to 2024-2025
    fy_start = date(2024, 4, 1)
    fy_end = date(2025, 3, 31)
    fy_label = "24-25"
    # Find the last used entry id for this financial year
    cursor.execute("""
        SELECT entry_id FROM sundry_Funds WHERE entry_date >= %s AND entry_date <= %s ORDER BY entry_id DESC LIMIT 1
    """, (fy_start, fy_end))
    last_id_row = cursor.fetchone()
    if last_id_row and last_id_row[0]:
        last_num = int(last_id_row[0])
    else:
        last_num = 0

    # Calculate brought forward (previous month's outstanding)
    year = today.year
    month = today.month
    prev_year, prev_month = get_prev_month(year, month)
    prev_month_str = f"{prev_year}{str(prev_month).zfill(2)}"
    cursor.execute("SELECT current_outstanding FROM monthly_sundry_outstanding WHERE month = %s", (prev_month_str,))
    prev_row = cursor.fetchone()
    brought_forward = prev_row[0] if prev_row else 0

    # For each account, check if payment received in this FY
    sundry_list = []
    for acc in accounts:
        cursor.execute("""
            SELECT COUNT(*) FROM receipts
            WHERE account_name = %s AND date BETWEEN %s AND %s
        """, (acc, fy_start, fy_end))
        paid = cursor.fetchone()[0]
        if paid == 0:
            sundry_list.append(acc)

    # Output
    print(f"\nBrought forward outstanding (from {prev_month_str}): {brought_forward}")
    print("\nAccounts with outstanding (sundry Fund):")
    for acc in sundry_list:
        print(f"  {acc}")

    # Store this month's outstanding for next month (total_due is not needed here)
    month_prefix = today.strftime('%Y%m')
    cursor.execute("REPLACE INTO monthly_sundry_outstanding (month, brought_forward, current_outstanding) VALUES (%s, %s, %s)",
                   (month_prefix, brought_forward, 0))
    conn.commit()

    cursor.close()
    conn.close()

if __name__ == "__main__":
    list_sundry_Funds()
