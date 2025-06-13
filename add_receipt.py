from db_connect import get_connection
from utils import parse_date
from datetime import datetime
from journal_utils import insert_journal_entry

MAIN_FUND_ACCOUNT = "main fund"

def add_receipt():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        account_name = input("From (account name): ").strip()
        amount = float(input("Amount received: "))
        mop = input("Mode of payment (Cash/Cheque/Bank Transfer/UPI): ")
        cheque_no = input("Cheque No (if cheque, else leave blank): ") if mop == "Cheque" else None
        narration = input("Narration: ")
        date_str = input("Enter transaction date (DD-MM-YYYY): ")
        date = parse_date(date_str)
        if not date:
            return

        cursor.execute("""
            INSERT INTO receipts (account_name, amount, mop, cheque_no, narration, date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (account_name, amount, mop, cheque_no, narration, date))
        conn.commit()

        cursor.execute("SELECT receipt_id FROM receipts ORDER BY id DESC LIMIT 1")
        receipt_id = cursor.fetchone()[0]

        print("✅ Receipt and journal entries recorded.")

        # Double-entry: Debit main fund, Credit unit account
        insert_journal_entry(conn, MAIN_FUND_ACCOUNT, 'Debit', amount, narration, mop, cheque_no, date)
        insert_journal_entry(conn, account_name, 'Credit', amount, narration, mop, cheque_no, date)

    except Exception as e:
        print("❌ Error:", e)
        with open("error.log", "a") as log_file:
            log_file.write(f"{datetime.now()} - Error in add_receipt: {e}\n")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
