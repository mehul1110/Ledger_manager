from db_connect import get_connection
from datetime import datetime, timedelta

def get_account_balance(account_name, as_of_date):
    """
    Calculates the balance of a specific account as of a given date (exclusive).
    Includes the 'System' entry type in the calculation.
    """
    conn = get_connection()
    cursor = conn.cursor()
    balance = 0
    try:
        # Include 'System' entry type in the calculation
        query = """
            SELECT
              COALESCE(SUM(CASE WHEN entry_type IN ('Fund', 'System') THEN amount ELSE 0 END), 0) - 
              COALESCE(SUM(CASE WHEN entry_type = 'Bank' THEN amount ELSE 0 END), 0) AS balance,
              COALESCE(SUM(fd), 0) AS fd_balance,
              COALESCE(SUM(property), 0) AS property_balance,
              COALESCE(SUM(sundry), 0) AS sundry_balance,
              COALESCE(SUM(fund), 0) AS fund_balance,
              COALESCE(SUM(cash), 0) AS cash_balance
            FROM journal_entries
            WHERE LOWER(account_name) = %s
              AND entry_date < %s
              AND (entry_id NOT LIKE 'CE%%' OR narration = 'Opening Balances')
        """
        cursor.execute(query, (account_name.lower(), as_of_date))
        result = cursor.fetchone()
        if result:
            balance = {
                'main_balance': result[0] or 0,
                'fd_balance': result[1] or 0,
                'property_balance': result[2] or 0,
                'sundry_balance': result[3] or 0,
                'fund_balance': result[4] or 0,
                'cash_balance': result[5] or 0
            }
    except Exception as e:
        print(f"Error calculating balance for {account_name}: {e}")
    finally:
        cursor.close()
        conn.close()
    return balance

def generate_monthly_statement(account_name, year, month):
    """
    Generates and prints a statement for an account for a given month.
    Includes opening balance, a list of transactions, and a closing balance.
    """
    first_day = datetime(year, month, 1)
    if month == 12:
        last_day = datetime(year + 1, 1, 1)
    else:
        last_day = datetime(year, month + 1, 1)

    # 1. Calculate Opening Balance (as of the first day of the month)
    opening_balance = get_account_balance(account_name, first_day)

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 2. Get transactions for the month, excluding counter-entries
        cursor.execute("""
            SELECT entry_date, narration, remarks,
                   (CASE WHEN entry_type = 'Fund' THEN amount ELSE 0 END) as credit,
                   (CASE WHEN entry_type = 'Bank' THEN amount ELSE 0 END) as debit
            FROM journal_entries
            WHERE LOWER(account_name) = %s
              AND entry_date >= %s AND entry_date < %s
              AND entry_id NOT LIKE 'CE%%'
            ORDER BY entry_date, entry_id
        """, (account_name.lower(), first_day, last_day))
        
        transactions = cursor.fetchall()

        # 3. Print statement
        print(f"\n--- Monthly Statement for '{account_name}' ---")
        print(f"--- For {first_day.strftime('%B %Y')} ---")
        print("-" * 100)
        print(f"Opening Balance as of {first_day.strftime('%Y-%m-%d')}: {opening_balance['main_balance']:,.2f}")
        print("-" * 100)
        print(f"{ 'Date' :<12} {'Narration' :<30} {'Remarks' :<30} {'Debit' :>12} {'Credit' :>12}")
        print("=" * 100)

        total_debit = 0
        total_credit = 0

        if not transactions:
            print("No transactions for this month.")
        else:
            for trans in transactions:
                date, narration, remarks, credit, debit = trans
                total_credit += credit
                total_debit += debit
                print(f"{date.strftime('%Y-%m-%d'):<12} {str(narration or ''):<30} {str(remarks or ''):<30} {debit:,.2f} {credit:,.2f}")

        # 4. Calculate Closing Balance
        closing_balance = opening_balance['main_balance'] + total_credit - total_debit
        
        print("=" * 100)
        print(f"{ '' :<74} {'Totals:':<12} {total_debit:,.2f} {total_credit:,.2f}")
        print("-" * 100)
        print(f"Closing Balance as of {(last_day - timedelta(days=1)).strftime('%Y-%m-%d')}: {closing_balance:,.2f}")
        print("-" * 100)

        # Verification
        calculated_balance_at_end = get_account_balance(account_name, last_day)
        if abs(closing_balance - calculated_balance_at_end) > 0.01:
            print(f"!!! Verification FAILED: Closing balance {closing_balance:,.2f} does not match calculated EOD balance {calculated_balance_at_end:,.2f}")
        else:
            print("Verification successful: Closing balance matches the opening balance for the next day.")

    except Exception as e:
        print(f"Error generating statement for {account_name}: {e}")
    finally:
        cursor.close()
        conn.close()

def prompt_for_statement():
    """Prompts user for account, year, and month to generate a statement."""
    # Automatically approve and generate statement for a default/test account and date
    account_name = "main fund"  # Set your default or test account here
    year = 2024  # Set a default/test year
    month = 1    # Set a default/test month
    generate_monthly_statement(account_name, year, month)

if __name__ == "__main__":
    prompt_for_statement()
