from db_connect import get_connection
from utils import parse_date
from journal_utils import insert_journal_entry

MAIN_FUND_ACCOUNT = "main fund"
NARRATION_OPTIONS = [
    "Petty", "Maintenance", "Salary", "Property", "FD in bank", "Misc", "Article appreciation amount",
    "Internet bill", "Fund lend to other accounts", "Printing of happenings"
]

def add_payment(
    name, amount, mop, cheque_no=None, date_str=None, narration=None,
    author=None, item_name=None, description=None, item_type=None, fd_duration=None, fd_interest=None, other_account=None, remarks=None, **kwargs
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if not name or str(amount).strip() == "" or not mop or not narration or not date_str:
            raise ValueError("Core payment fields must be provided")

        date = parse_date(date_str)
        if not date:
            raise ValueError("Invalid date format")

        # Map cheque_no or other_account into remarks if provided
        if cheque_no:
            remarks = cheque_no
        elif other_account:
            remarks = other_account
        query = """
            INSERT INTO pending_transactions (
                transaction_type, account_name, amount, mop, narration, transaction_date, remarks,
                author, item_name, description, property_type, fd_duration, fd_interest
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            'payment', name, float(amount), mop, narration, date, remarks,
            author, item_name, description, item_type, fd_duration, fd_interest
        )
        cursor.execute(query, params)
        conn.commit()
        print("✅ Payment submitted for approval.")

    except Exception as e:
        print("❌ Error:", e)
        from datetime import datetime
        with open("error.log", "a") as log_file:
            log_file.write(f"{datetime.now()} - Error in add_payment: {e}\n")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def add_payment_to_final_tables(conn, cursor, transaction):
    # This function contains the logic to insert an approved payment
    # into the final payments table and handle related tables like
    # property_details and fd_details.
    
    # Extract data from the transaction dictionary
    name = transaction['account_name']
    amount = transaction['amount']
    mop = transaction['mop']
    narration = transaction['narration']
    date = transaction['transaction_date']
    remarks = transaction['remarks']
    author = transaction['author']
    item_name = transaction['item_name']
    description = transaction['description']
    item_type = transaction['property_type']
    fd_duration = transaction['fd_duration']
    fd_interest = transaction['fd_interest']

    # Check if this is an FD maturity transaction
    is_fd_maturity = item_type == 'fd_maturity'
    
    if is_fd_maturity:
        # Handle FD maturity specially
        handle_fd_maturity_payment(conn, cursor, transaction)
        return

    extra_narration = ""
    # Article appreciation amount no longer requires author field
    
    narration_full = narration

    # --- ID GENERATION LOGIC ---
    # Get the last payment number, increment it, and format the new ID
    cursor.execute("SELECT MAX(CAST(SUBSTRING(payment_id, 3) AS UNSIGNED)) as max_id FROM payments")
    result = cursor.fetchone()
    last_id_num = result['max_id'] if result else 0
    new_id_num = (last_id_num or 0) + 1
    new_payment_id = f"PY{new_id_num:05d}"

    cursor.execute("""
        INSERT INTO payments (payment_id, account_name, amount, mop, narration, remarks, date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (new_payment_id, name, amount, mop, narration_full, remarks, date))
    
    payment_id = new_payment_id

    # Extract the numeric part of the ID (e.g., '00001' from 'PY00001')
    id_numeric_part = payment_id[2:]
    # Construct the correct journal entry IDs as per user requirement
    payment_journal_id = f"PV{id_numeric_part}"
    counter_journal_id = f"CEPV{id_numeric_part}"

    # Create journal entries for the payment
    # For payments: main entry_type = bank, counter = fund
    # The main entry should debit the payer's account.
    main_entry_type = 'Bank'
    counter_entry_type = 'Fund'
    is_sundry = narration in ['Fund lend to other accounts', 'Sundry']
    is_fd = narration == "FD in bank"
    is_property = narration == "Property"
    is_non_expendable_property = (is_property and description and description.strip().lower() == "non-expendable")

    # Determine columns for the DEBIT entry (recipient account)
    # Normal payment entries ALWAYS use the main amount column
    debit_amount = amount
    debit_fd = None
    debit_property = None
    debit_sundry = None

    # Refine logic for specialized columns based on narration
    debit_fd = amount if is_fd else None  # Use amount instead of fd_interest
    debit_property = amount if is_property else None
    debit_sundry = amount if is_sundry else None

    # Debit the account that received the payment
    insert_journal_entry(
        db_connection=conn,
        entry_id=payment_journal_id,
        account_name=name,
        entry_type=main_entry_type,
        amount=debit_amount,
        narration=narration,
        mop=mop,
        entry_date=date,
        fd=debit_fd,
        property=debit_property,
        sundry=debit_sundry
    )

    # Credit the main fund account (counter entry)
    # For payments, the main fund is being debited (money going out)
    # We put the amount in specialized columns to categorize the spending
    # Initialize all counter values
    counter_amount = amount # Always populate the main amount for balance calculation
    counter_fd = None
    counter_sundry = None
    counter_property = None
    counter_fund = None

    # For the counter-entry, place the amount in the correct specialized column
    if is_fd:
        counter_fd = amount
    elif is_non_expendable_property:
        counter_property = amount
    elif is_sundry:
        counter_sundry = amount
    else:
        # For all other non-specialized payments, the value goes into the 'fund' column.
        counter_fund = amount
    
    insert_journal_entry(
        db_connection=conn,
        entry_id=counter_journal_id,
        account_name=MAIN_FUND_ACCOUNT,
        entry_type=counter_entry_type,
        amount=None, # Main amount for balance
        narration=narration,
        mop=mop,
        entry_date=date,
        fd=counter_fd,
        sundry=counter_sundry,
        property=counter_property,
        fund=counter_fund # Specialized column for categorization
    )

    if narration == "FD in bank":
        if not fd_duration or not fd_interest:
            raise ValueError("FD duration and interest must be provided for FD in bank")
        
        from datetime import timedelta
        import calendar

        duration_val_str, duration_period = fd_duration.split()
        duration_val = int(duration_val_str)
        
        maturity_date = None
        time_in_years = 0
        if duration_period.lower() in ['day', 'days']:
            maturity_date = date + timedelta(days=duration_val)
            time_in_years = duration_val / 365.25
        elif duration_period.lower() in ['month', 'months']:
            total_months = duration_val
            maturity_year = date.year + ((date.month - 1 + total_months) // 12)
            maturity_month = ((date.month - 1 + total_months) % 12) + 1
            last_day_of_maturity_month = calendar.monthrange(maturity_year, maturity_month)[1]
            maturity_day = min(date.day, last_day_of_maturity_month)
            maturity_date = date.replace(year=maturity_year, month=maturity_month, day=maturity_day)
            time_in_years = total_months / 12.0
        elif duration_period.lower() in ['year', 'years']:
            maturity_year = date.year + duration_val
            last_day_of_maturity_month = calendar.monthrange(maturity_year, date.month)[1]
            maturity_day = min(date.day, last_day_of_maturity_month)
            maturity_date = date.replace(year=maturity_year, day=maturity_day)
            time_in_years = float(duration_val)
        else:
            raise ValueError("Invalid FD duration period. Use 'Days', 'Months', or 'Years'.")

        principal = float(amount)
        rate = float(fd_interest)

        # Using compound interest formula A = P(1 + r/n)^(nt)
        # Assuming interest is compounded quarterly (n=4) as is common.
        n = 4
        r = rate / 100  # Convert annual rate to decimal
        maturity_amount = round(principal * (1 + r / n)**(n * time_in_years), 2)

        narration_full_fd = f"{narration}"

        cursor.execute("""
            INSERT INTO fd_details (payment_id, bank_account, amount, duration, interest_rate, narration, fd_date, maturity_date, maturity_amount, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Active')
        """, (payment_id, name, principal, fd_duration, fd_interest, narration_full_fd, date, maturity_date, maturity_amount))

    elif narration == "Property":
        if not item_name or not description or not item_type:
            raise ValueError("Item name, description, and type must be provided for Property")
        
        depreciation_rates = {
            'electronic': 15.0,
            'furniture': 10.0,
            'stationery': 20.0,
            'vehicle': 20.0,
            'building': 5.0
        }
        depreciation_rate = depreciation_rates.get(item_type, 10.0)

        if description.strip().lower() == "non-expendable":
            cursor.execute("""
                INSERT INTO property_details (payment_id, item_name, description, type, value, purchase_date, depreciation_rate)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (payment_id, item_name, description, item_type, amount, date, depreciation_rate))
        else:
            cursor.execute("""
                INSERT INTO property_details (payment_id, item_name, description, type, value, purchase_date, depreciation_rate)
                VALUES (%s, %s, %s, %s, %s, %s, 0)
            """, (payment_id, item_name, description, item_type, amount, date))

    print("✅ Payment processed and recorded in final tables.")

def handle_fd_maturity_payment(conn, cursor, transaction):
    """
    Special handler for FD maturity payments that come through the approval workflow.
    This handles the complex logic of posting the maturity amount and interest correctly.
    """
    name = transaction['account_name']
    amount = transaction['amount']
    mop = transaction['mop']
    narration = transaction['narration']
    date = transaction['transaction_date']
    remarks = transaction['remarks']
    description = transaction['description']
    
    # Extract original payment ID from remarks
    original_payment_id = None
    if remarks and "Original payment ID" in remarks:
        original_payment_id = remarks.split("Original payment ID ")[-1].strip()
    
    # Parse principal and interest from description
    principal_amount = 0
    interest_amount = 0
    if description and "Principal:" in description and "Interest:" in description:
        try:
            parts = description.split(", ")
            for part in parts:
                if "Principal:" in part:
                    principal_amount = float(part.split("Principal: ")[1])
                elif "Interest:" in part:
                    interest_amount = float(part.split("Interest: ")[1])
        except (ValueError, IndexError):
            # If parsing fails, treat entire amount as principal
            principal_amount = float(amount)
            interest_amount = 0
    
    # --- ID GENERATION LOGIC ---
    cursor.execute("SELECT MAX(CAST(SUBSTRING(payment_id, 3) AS UNSIGNED)) as max_id FROM payments")
    result = cursor.fetchone()
    last_id_num = result['max_id'] if result else 0
    new_id_num = (last_id_num or 0) + 1
    new_payment_id = f"PY{new_id_num:05d}"

    # Insert the payment record for the full maturity amount
    cursor.execute("""
        INSERT INTO payments (payment_id, account_name, amount, mop, narration, remarks, date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (new_payment_id, name, amount, mop, narration, remarks, date))
    
    # Extract the numeric part of the ID
    id_numeric_part = new_payment_id[2:]
    payment_journal_id = f"PV{id_numeric_part}"
    counter_journal_id = f"CEPV{id_numeric_part}"
    
    # Create journal entries for the FD maturity
    # Debit the bank account for the full maturity amount
    insert_journal_entry(
        db_connection=conn,
        entry_id=payment_journal_id,
        account_name=name,
        entry_type='Fund',
        amount=amount,
        narration=narration,
        mop=mop,
        entry_date=date,
        fd=None,
        property=None,
        sundry=None
    )

    # Credit main fund: principal goes to regular amount, interest goes to FD column
    if interest_amount > 0:
        # If there's interest, credit principal to regular amount and interest to FD column
        insert_journal_entry(
            db_connection=conn,
            entry_id=counter_journal_id,
            account_name=MAIN_FUND_ACCOUNT,
            entry_type='Bank',
            amount=principal_amount,  # Principal in regular amount column
            narration=narration,
            mop=mop,
            entry_date=date,
            fd=interest_amount,  # Interest in FD column
            sundry=None,
            property=None
        )
    else:
        # No interest, just credit the full amount to regular column
        insert_journal_entry(
            db_connection=conn,
            entry_id=counter_journal_id,
            account_name=MAIN_FUND_ACCOUNT,
            entry_type='Bank',
            amount=amount,
            narration=narration,
            mop=mop,
            entry_date=date,
            fd=None,
            sundry=None,
            property=None
        )
    
    # Clean up the original FD record if we have the original payment ID
    if original_payment_id:
        cursor.execute("""
            DELETE FROM fd_details WHERE payment_id = %s
        """, (original_payment_id,))
        print(f"✅ Original FD record {original_payment_id} removed from fd_details.")
    
    print("✅ FD maturity payment processed and recorded in final tables.")
