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
        SELECT COALESCE(SUM(CASE WHEN entry_type='Fund' THEN amount ELSE -amount END), 0)
        FROM journal_entries
        WHERE account_name = %s AND entry_date < %s
    """, (MAIN_FUND_ACCOUNT, first_of_month))
    main_fund_balance = cursor.fetchone()[0]
    print(f"\n==== Main Fund (Brought Forward as of {first_of_month.strftime('%Y-%m-%d')}): {main_fund_balance} ====")

    # FDs
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM fd_details WHERE fd_date < %s
    """, (first_of_month,))
    fd_balance = cursor.fetchone()[0]
    print(f"\n==== FDs (Brought Forward as of {first_of_month.strftime('%Y-%m-%d')}): {fd_balance} ====")

    # Property
    cursor.execute("""
        SELECT COALESCE(SUM(value), 0) FROM property_details WHERE purchase_date < %s
    """, (first_of_month,))
    property_balance = cursor.fetchone()[0]
    print(f"\n==== Property (Brought Forward as of {first_of_month.strftime('%Y-%m-%d')}): {property_balance} ====")

    # Fund Given (sum all Fund lend to other accounts up to the start of the month)
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM payments
        WHERE narration LIKE '%Fund lend to other accounts%' AND date < %s
    """, (first_of_month,))
    Fund_given = cursor.fetchone()[0]
    print(f"\n==== Fund Given (Brought Forward as of {first_of_month.strftime('%Y-%m-%d')}): {Fund_given} ====")

if __name__ == "__main__":
    conn = get_connection()
    display_brought_forward_balances(conn)
    conn.close()
