from db_connect import get_connection

MAIN_FUND_ACCOUNT = "main fund"

def display_brought_forward_balances(conn):
    """
    Display brought forward balances for main fund, FDs, property, and Fund given at the start of the current month.
    """
    from datetime import datetime
    cursor = conn.cursor()
    today = datetime.today()
    first_of_month = today.replace(day=1)

    # Main Fund
    cursor.execute("""
        SELECT (COALESCE(SUM(CASE WHEN entry_type = 'Fund' THEN amount ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN entry_type = 'Bank' THEN amount ELSE 0 END), 0))
        FROM journal_entries
        WHERE account_name = %s AND entry_id NOT LIKE 'C%%' AND entry_date < %s
    """, (MAIN_FUND_ACCOUNT, first_of_month))
    main_fund_balance = cursor.fetchone()[0] or 0
    print(f"\n==== Main Fund (Brought Forward as of {first_of_month.strftime('%Y-%m-%d')}): {main_fund_balance} ====")

    # FDs
    cursor.execute("""
        SELECT COALESCE(SUM(fd), 0) FROM journal_entries WHERE entry_type = 'Fund' AND fd IS NOT NULL AND entry_id NOT LIKE 'C%%' AND entry_date < %s
    """, (first_of_month,))
    fd_balance = cursor.fetchone()[0] or 0
    print(f"\n==== FDs (Brought Forward as of {first_of_month.strftime('%Y-%m-%d')}): {fd_balance} ====")

    # Property
    cursor.execute("""
        SELECT COALESCE(SUM(property), 0) FROM journal_entries WHERE entry_type = 'Fund' AND property IS NOT NULL AND entry_id NOT LIKE 'C%%' AND entry_date < %s
    """, (first_of_month,))
    property_balance = cursor.fetchone()[0] or 0
    print(f"\n==== Property (Brought Forward as of {first_of_month.strftime('%Y-%m-%d')}): {property_balance} ====")

    # Fund Given (Sundry)
    cursor.execute("""
        SELECT COALESCE(SUM(sundry), 0) FROM journal_entries WHERE entry_type = 'Fund' AND sundry IS NOT NULL AND entry_id NOT LIKE 'C%%' AND entry_date < %s
    """, (first_of_month,))
    fund_given = cursor.fetchone()[0] or 0
    print(f"\n==== Fund Given (Brought Forward as of {first_of_month.strftime('%Y-%m-%d')}): {fund_given} ====")

if __name__ == "__main__":
    conn = get_connection()
    display_brought_forward_balances(conn)
    conn.close()
