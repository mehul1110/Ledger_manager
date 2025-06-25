from db_connect import get_connection
from datetime import datetime, timedelta

def display_brought_forward_main_fund():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get last month range
        today = datetime.today()
        first_of_this_month = today.replace(day=1)
        last_month_end = first_of_this_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        next_month_first = first_of_this_month

        # Calculate closing balance for last month
        cursor.execute("""
            SELECT
              COALESCE(SUM(CASE WHEN entry_type = 'Bank' THEN amount ELSE 0 END), 0) -
              COALESCE(SUM(CASE WHEN entry_type = 'Fund' THEN amount ELSE 0 END), 0) AS balance
            FROM journal_entries
            WHERE account_name = %s
              AND entry_date BETWEEN %s AND %s
        """, ('main fund', last_month_start.date(), last_month_end.date()))
        balance = cursor.fetchone()[0] or 0

        print(f"Brought Forward Balance for {next_month_first.strftime('%B %Y')}: {balance}")
    
    except Exception as e:
        print("❌ Error in display_brought_forward_main_fund:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    display_brought_forward_main_fund()
