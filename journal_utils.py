import mysql.connector

def insert_journal_entry(db_connection, entry_id, account_name, entry_type, amount, narration, mop, entry_date, fd=None, sundry=None, property_value=None, fund=None, cash=None):
    """
    Inserts a journal entry into the journal_entries table.
    The amount for FD, Sundry, Property, Fund or Cash transactions can be entered in the respective column.
    Enforces that entry_type is either 'Bank', 'Fund', or 'System'.
    """
    # Format all monetary values to two decimal places
    if amount is not None:
        try:
            amount = round(float(amount), 2)
        except (ValueError, TypeError):
            pass  # Keep original value if conversion fails
    if fd is not None:
        try:
            fd = round(float(fd), 2)
        except (ValueError, TypeError):
            pass
    if sundry is not None:
        try:
            sundry = round(float(sundry), 2)
        except (ValueError, TypeError):
            pass
    if property_value is not None:
        try:
            property_value = round(float(property_value), 2)
        except (ValueError, TypeError):
            pass
    if fund is not None:
        try:
            fund = round(float(fund), 2)
        except (ValueError, TypeError):
            pass
    if cash is not None:
        try:
            cash = round(float(cash), 2)
        except (ValueError, TypeError):
            pass

    print(f"[DEBUG] insert_journal_entry: entry_id={repr(entry_id)}, entry_type={repr(entry_type)}, account_name={repr(account_name)}, amount={repr(amount)}, narration={repr(narration)}, mop={repr(mop)}, entry_date={repr(entry_date)}, fd={repr(fd)}, sundry={repr(sundry)}, property_value={repr(property_value)}, fund={repr(fund)}, cash={repr(cash)}")
    if entry_type not in ("Bank", "Fund", "System"):
        raise ValueError(f"Invalid entry_type '{entry_type}'. Must be 'Bank', 'Fund', or 'System'.")
    try:
        cursor = db_connection.cursor()
        query = """
            INSERT INTO journal_entries
            (entry_id, account_name, entry_type, amount, narration, mop, entry_date, fd, sundry, property, fund, cash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (entry_id, account_name, entry_type, amount, narration, mop, entry_date, fd, sundry, property_value, fund, cash)
        
        print(f"[DEBUG] SQL values: {values}")

        # Execute the query and confirm insertion
        cursor.execute(query, values)
        print("[DEBUG] SQL query executed successfully.")
        db_connection.commit()
        print("[DEBUG] Transaction committed successfully.")
    except mysql.connector.Error as err:
        print(f"❌ Error inserting journal entry: {err}")
        db_connection.rollback()
        raise err  # Re-raise the error instead of silently failing
    finally:
        cursor.close()
