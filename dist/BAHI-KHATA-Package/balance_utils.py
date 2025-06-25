
from db_connect import get_connection
from datetime import datetime, timedelta

def get_account_balance(account_name, as_of_date):
    """
    Calculates the balance of a specific account as of a given date (exclusive).
    This is a running balance from the beginning of time up to the day before as_of_date.
    The logic is derived from how receipts and payments affect accounts.
    'Bank' entry_type represents money coming in (credit to the account from user's perspective).
    'Fund' entry_type represents money going out (debit from the account from user's perspective).
    """
    conn = get_connection()
    cursor = conn.cursor()
    balance = 0
    try:
        # This logic should apply to any account that receives payments or makes receipts,
        # including 'main fund' and all bank accounts.
        query = """
            SELECT
              COALESCE(SUM(CASE WHEN entry_type = 'Bank' THEN amount ELSE 0 END), 0) -
              COALESCE(SUM(CASE WHEN entry_type = 'Fund' THEN amount ELSE 0 END), 0) AS balance
            FROM journal_entries
            WHERE LOWER(account_name) = %s
              AND entry_date < %s
        """
        cursor.execute(query, (account_name.lower(), as_of_date))
        result = cursor.fetchone()
        if result and result[0] is not None:
            balance = result[0]
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
        # 2. Get transactions for the month
        cursor.execute("""
            SELECT entry_date, narration, remarks,
                   (CASE WHEN entry_type = 'Bank' THEN amount ELSE 0 END) as credit,
                   (CASE WHEN entry_type = 'Fund' THEN amount ELSE 0 END) as debit
            FROM journal_entries
            WHERE LOWER(account_name) = %s
              AND entry_date >= %s AND entry_date < %s
            ORDER BY entry_date, entry_id
        """, (account_name.lower(), first_day, last_day))
        
        transactions = cursor.fetchall()

        # 3. Print statement
        print(f"\n--- Monthly Statement for '{account_name}' ---")
        print(f"--- For {first_day.strftime('%B %Y')} ---")
        print("-" * 100)
        print(f"Opening Balance as of {first_day.strftime('%Y-%m-%d')}: {opening_balance:,.2f}")
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
        closing_balance = opening_balance + total_credit - total_debit
        
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
    try:
        account_name = input("Enter the account name (e.g., main fund): ")
        year = int(input("Enter the year (e.g., 2023): "))
        month = int(input("Enter the month (1-12): "))
        if not (1 <= month <= 12):
            print("Invalid month. Please enter a number between 1 and 12.")
            return
        generate_monthly_statement(account_name, year, month)
    except ValueError:
        print("Invalid input. Please enter numbers for year and month.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    prompt_for_statement()
