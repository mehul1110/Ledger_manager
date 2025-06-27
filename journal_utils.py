import mysql.connector

def insert_journal_entry(db_connection, entry_id, account_name, entry_type, amount, narration, mop, entry_date, fd=None, sundry=None, property=None):
    """
    Inserts a journal entry into the journal_entries table.
    The amount for FD, Sundry, or Property transactions is entered in the respective column, not in the 'amount' column.
    Only one of fd, sundry, property should be set per entry; all others must be None.
    Enforces that entry_type is either 'Bank' or 'Fund'.
    """
    print(f"[DEBUG] insert_journal_entry: entry_id={repr(entry_id)}, entry_type={repr(entry_type)}, account_name={repr(account_name)}, amount={repr(amount)}, narration={repr(narration)}, mop={repr(mop)}, entry_date={repr(entry_date)}, fd={repr(fd)}, sundry={repr(sundry)}, property={repr(property)}")
    if entry_type not in ("Bank", "Fund"):
        raise ValueError(f"Invalid entry_type '{entry_type}'. Must be 'Bank' or 'Fund'.")
    try:
        cursor = db_connection.cursor()
        query = """
            INSERT INTO journal_entries
            (entry_id, account_name, entry_type, amount, narration, mop, entry_date, fd, sundry, property)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Ensure only one specialized column is populated
        if sum([fd is not None, sundry is not None, property is not None]) > 1:
            raise ValueError("Only one of fd, sundry, or property can be set per entry.")

        # Only one of fd, sundry, property should have the transaction amount, others None
        if fd is not None:
            values = (entry_id, account_name, entry_type, None, narration, mop, entry_date, fd, None, None)
        elif sundry is not None:
            values = (entry_id, account_name, entry_type, None, narration, mop, entry_date, None, sundry, None)
        elif property is not None:
            values = (entry_id, account_name, entry_type, None, narration, mop, entry_date, None, None, property)
        else:
            values = (entry_id, account_name, entry_type, amount, narration, mop, entry_date, None, None, None)
        
        # Ensure specialized columns are populated based on narration
        if narration == "FD in bank":
            if fd is None:
                raise ValueError("FD value must be provided for 'FD in bank' narration.")
            print(f"[DEBUG] FD narration detected. FD value: {fd}")
        elif narration == "Property":
            if property is None:
                raise ValueError("Property value must be provided for 'Property' narration.")
            print(f"[DEBUG] Property narration detected. Property value: {property}")
        elif narration in ["Fund lend to other accounts", "Sundry"]:
            if sundry is None:
                raise ValueError("Sundry value must be provided for 'Fund lend to other accounts' or 'Sundry' narration.")
            print(f"[DEBUG] Sundry narration detected. Sundry value: {sundry}")
        else:
            print(f"[DEBUG] General narration detected. Amount value: {amount}")

        # Debugging specialized column values
        if fd is not None:
            print(f"[DEBUG] FD column populated with value: {fd}")
        elif sundry is not None:
            print(f"[DEBUG] Sundry column populated with value: {sundry}")
        elif property is not None:
            print(f"[DEBUG] Property column populated with value: {property}")
        else:
            print("[DEBUG] No specialized column populated; using amount column.")
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
