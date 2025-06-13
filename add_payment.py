from db_connect import get_connection
from utils import parse_date
from journal_utils import insert_journal_entry

MAIN_FUND_ACCOUNT = "main fund"
NARRATION_OPTIONS = [
    "Petty", "Maintenance", "Salary", "Misc", "FD in bank", "Credit lend to other accounts",
    "Internet bill", "Article appreciation amount", "Property", "Printing of happenings"
]

def add_payment():
    conn = get_connection()
    cursor = conn.cursor()
 
    try:
        print("Narration options:")
        for idx, option in enumerate(NARRATION_OPTIONS, 1):
            print(f"{idx}. {option}")
        narration_choice = input(f"Choose narration (1-{len(NARRATION_OPTIONS)}): ").strip()
        try:
            narration = NARRATION_OPTIONS[int(narration_choice)-1]
        except (ValueError, IndexError):
            narration = input("Enter custom narration: ").strip()

        # Ask for account name and payment details first
        name = input("To (account name): ").strip()
        amount = float(input("Amount paid: "))
        mop = input("Mode of payment (Cash/Cheque/Bank Transfer/UPI): ")
        cheque_no = input("Cheque No (if cheque, else leave blank): ") if mop == "Cheque" else None
        date_str = input("Enter transaction date (DD-MM-YYYY): ")
        date = parse_date(date_str)
        if not date:
            return

        # Special prompts for new narration options (grouped for readability)
        extra_narration = ""
        item_name = description = item_type = author = other_account = fd_duration = fd_interest = None
        if narration == "Article appreciation amount":
            author = input("Enter the name of the author: ").strip()
            extra_narration = f" | Author: {author}"
        elif narration == "Property":
            item_name = input("Enter the item name: ").strip()
            print("Description options:")
            print("1. Expendable")
            print("2. Non-expendable")
            desc_choice = input("Choose description (1-2): ").strip()
            if desc_choice == "1":
                description = "expendable"
            else:
                description = "non-expendable"
            item_type = input("Type (electronic/furniture/stationery/etc): ").strip().lower()
            # Set depreciation rate based on item_type
            depreciation_rates = {
                'electronic': 15.0,
                'furniture': 10.0,
                'stationery': 20.0,
                'vehicle': 20.0,
                'building': 5.0
            }
            depreciation_rate = depreciation_rates.get(item_type, 10.0)  # Default 10% if not found
        elif narration == "FD in bank":
            # Use the 'name' as the bank account, do not ask again
            other_account = name
            fd_duration = input("Enter the duration of the FD (e.g., 12 months): ").strip()
            fd_interest = input("Enter the interest rate applied (e.g., 6.5): ").strip()
        elif narration == "Credit lend to other accounts":
            other_account = input("Enter the account to credit (e.g., account name): ").strip()

        narration_full = narration + extra_narration if extra_narration else narration

        cursor.execute("""
            INSERT INTO payments (account_name, amount, mop, cheque_no, narration, date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, amount, mop, cheque_no, narration_full, date))
        conn.commit()

        cursor.execute("SELECT payment_id FROM payments ORDER BY id DESC LIMIT 1")
        payment_id = cursor.fetchone()[0]

        # Special handling for FD in bank and Credit lend
        if narration == "FD in bank":
            # Calculate maturity date
            from datetime import timedelta
            months = int(fd_duration.split()[0]) if fd_duration and fd_duration.split()[0].isdigit() else 12
            maturity_year = date.year + ((date.month - 1 + months) // 12)
            maturity_month = ((date.month - 1 + months) % 12) + 1
            maturity_day = date.day
            import calendar
            last_day = calendar.monthrange(maturity_year, maturity_month)[1]
            maturity_day = min(maturity_day, last_day)
            maturity_date = date.replace(year=maturity_year, month=maturity_month, day=maturity_day)
            principal = amount
            rate = float(fd_interest) if fd_interest else 0.0
            maturity_amount = round(principal * (1 + (rate/100) * (months/12)), 2)
            narration_full_fd = f"{narration}"
            # FD: principal goes out from main fund (amount=0, fd=principal)
            insert_journal_entry(conn, MAIN_FUND_ACCOUNT, 'Credit', 0, narration_full_fd, mop, cheque_no, date, fd=amount)
            # FD: principal appears as asset in FD account (amount=0, fd=principal)
            insert_journal_entry(conn, other_account, 'Debit', 0, narration_full_fd, mop, cheque_no, date, fd=amount)
            cursor.execute("""
                INSERT INTO fd_details (payment_id, bank_account, amount, duration, interest_rate, narration, fd_date, maturity_date, maturity_amount, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Active')
            """, (payment_id, other_account, amount, fd_duration, fd_interest, narration_full_fd, date, maturity_date, maturity_amount))
            conn.commit()
        elif narration == "Credit lend to other accounts":
            insert_journal_entry(conn, MAIN_FUND_ACCOUNT, 'Credit', amount, narration_full, mop, cheque_no, date)
            insert_journal_entry(conn, other_account, 'Debit', amount, narration_full, mop, cheque_no, date)
        elif narration == "Property":
            if description and description.strip().lower() == "non-expendable":
                # Credit main fund (amount column), Debit property (property column)
                insert_journal_entry(conn, MAIN_FUND_ACCOUNT, 'Credit', amount, narration_full, mop, cheque_no, date)
                insert_journal_entry(conn, name, 'Debit', 0, narration_full, mop, cheque_no, date, property=amount)
                cursor.execute("""
                    INSERT INTO property_details (payment_id, item_name, description, item_type, narration, amount, date, depreciation_rate, new_rate)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (payment_id, item_name, description, item_type, narration_full, amount, date, depreciation_rate, amount))
                conn.commit()
                # Auto-run depreciation after insert
                from depreciate_property import depreciate_property_assets
                depreciate_property_assets()
            else:
                # Expendable property: treat as expense
                insert_journal_entry(conn, MAIN_FUND_ACCOUNT, 'Credit', amount, narration_full, mop, cheque_no, date)
                insert_journal_entry(conn, name, 'Debit', amount, narration_full, mop, cheque_no, date)
        else:
            insert_journal_entry(conn, MAIN_FUND_ACCOUNT, 'Credit', amount, narration_full, mop, cheque_no, date)
            insert_journal_entry(conn, name, 'Debit', amount, narration_full, mop, cheque_no, date)

        conn.commit()
        print("✅ Payment and journal entries recorded.")

    except Exception as e:
        print("❌ Error:", e)
        from datetime import datetime
        with open("error.log", "a") as log_file:
            log_file.write(f"{datetime.now()} - Error in add_payment: {e}\n")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def display_monthly_unit_account_balances(conn):
    """
    For each unit account, display the total value at the start of each month.
    """
    cursor = conn.cursor()
    # Get all unique unit accounts from property_details
    cursor.execute("SELECT DISTINCT item_name FROM property_details")
    unit_accounts = [row[0] for row in cursor.fetchall()]

    from datetime import datetime, timedelta
    today = datetime.today()
    first_of_month = today.replace(day=1)
    # For each unit account, get the sum of value up to the end of previous month
    for unit in unit_accounts:
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM property_details
            WHERE item_name = %s AND date < %s
        """, (unit, first_of_month))
        value = cursor.fetchone()[0]
        print(f"\n==== {unit} (Value as of {first_of_month.strftime('%Y-%m-%d')}): {value} ====")

if __name__ == "__main__":
    conn = get_connection()
    # Removed display_brought_forward_balances from this file. Use brought_forward_balances.py instead.
    # Optionally, display_monthly_unit_account_balances(conn) for per-property breakdown
    # ...then display your detailed tables or reports...
    conn.close()
