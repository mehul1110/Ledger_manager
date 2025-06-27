from datetime import datetime
from db_connect import get_connection
from utils import parse_date
from journal_utils import insert_journal_entry

MAIN_FUND_ACCOUNT = "main fund"

def add_receipt(account_name=None, amount=None, mop=None, cheque_no=None, narration=None, date_str=None, remarks=None):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Require all arguments for GUI use
        if not account_name or amount is None or str(amount).strip() == "" or not mop or not narration or not date_str:
            raise ValueError("All receipt fields must be provided")
        
        date = parse_date(date_str)
        if not date:
            raise ValueError("Invalid date format")

        # Map cheque number to remarks if provided
        if cheque_no:
            remarks = cheque_no

        query = """
            INSERT INTO pending_transactions (
                transaction_type, account_name, amount, mop, narration, transaction_date, remarks
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            'receipt', account_name, float(amount), mop, narration, date, remarks
        )
        cursor.execute(query, params)
        conn.commit()

        print("✅ Receipt submitted for approval.")

    except Exception as e:
        print("❌ Error:", e)
        with open("error.log", "a") as log_file:
            log_file.write(f"{datetime.now()} - Error in add_receipt: {e}\n")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def add_receipt_to_final_table(conn, cursor, transaction):
    # This function inserts an approved receipt into the final receipts table.
    
    # Extract data from the transaction dictionary
    account_name = transaction['account_name']
    amount = transaction['amount']
    mop = transaction['mop']
    narration = transaction['narration']
    date = transaction['transaction_date']
    remarks = transaction['remarks']

    # --- ID GENERATION LOGIC ---
    # Get the last receipt number, increment it, and format the new ID
    cursor.execute("SELECT MAX(CAST(SUBSTRING(receipt_id, 3) AS UNSIGNED)) as max_id FROM receipts")
    result = cursor.fetchone()
    last_id_num = result['max_id'] if result and result['max_id'] is not None else 0
    new_id_num = last_id_num + 1
    new_receipt_id = f"RV{new_id_num:05d}"

    cursor.execute("""
        INSERT INTO receipts (receipt_id, account_name, amount, mop, narration, remarks, date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (new_receipt_id, account_name, amount, mop, narration, remarks, date))

    receipt_id = new_receipt_id

    # Extract the numeric part of the ID (e.g., '00001' from 'RV00001')
    id_numeric_part = receipt_id[2:]
    # Construct the correct journal entry IDs as per user requirement
    receipt_journal_id = f"RV{id_numeric_part}"
    counter_journal_id = f"CERV{id_numeric_part}"

    # Create journal entries for the receipt
    # For receipts: main entry_type = Bank, counter = Fund
    main_entry_type = 'Bank'
    counter_entry_type = 'Fund'

    # Debit the main fund account (main entry)
    insert_journal_entry(
        db_connection=conn,
        entry_id=receipt_journal_id,
        account_name=MAIN_FUND_ACCOUNT,
        entry_type=main_entry_type,
        amount=amount,
        narration=narration,
        mop=mop,
        entry_date=date,
        fd=None,
        sundry=None,
        property=None
    )

    # Credit the account that made the payment (counter entry, always positive amount)
    insert_journal_entry(
        db_connection=conn,
        entry_id=counter_journal_id,
        account_name=account_name,
        entry_type=counter_entry_type,
        amount=amount,
        narration=narration,
        mop=mop,
        entry_date=date,
        fd=None,
        sundry=None,
        property=None
    )

    print("✅ Receipt processed and recorded in final tables.")
