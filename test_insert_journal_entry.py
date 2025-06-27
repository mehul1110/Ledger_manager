import mysql.connector
from journal_utils import insert_journal_entry

def test_insert_journal_entry():
    # Mock database connection
    class MockCursor:
        def execute(self, query, values):
            print(f"[TEST] Executing query: {query}")
            print(f"[TEST] With values: {values}")

        def close(self):
            pass

    class MockConnection:
        def cursor(self):
            return MockCursor()

        def commit(self):
            print("[TEST] Transaction committed.")

        def rollback(self):
            print("[TEST] Transaction rolled back.")

    conn = MockConnection()

    # Test data
    test_data = [
        {
            "entry_id": "PV00001",
            "account_name": "PNB",
            "entry_type": "Bank",
            "amount": 500000,
            "narration": "FD in bank",
            "mop": "Bank Transfer",
            "entry_date": "2025-06-27",
            "fd": None,  # FD value populated
            "sundry": None,
            "property": None
        },
        {
            "entry_id": "PV00002",
            "account_name": "Property Account",
            "entry_type": "Fund",
            "amount": 10000,
            "narration": "Property",
            "mop": "Bank Transfer",
            "entry_date": "2025-06-27",
            "fd": None,
            "sundry": None,
            "property": None  # Property value populated
        },
        {
            "entry_id": "PV00003",
            "account_name": "Sundry Account",
            "entry_type": "Fund",
            "amount": 2000,
            "narration": "Sundry",
            "mop": "Cash",
            "entry_date": "2025-06-27",
            "fd": None,
            "sundry": None,  # Sundry value populated
            "property": None
        }
    ]

    # Simulate app logic for determining specialized column values
    for data in test_data:
        if data["narration"] == "FD in bank":
            data["fd"] = data["amount"]  # FD value derived from amount
        elif data["narration"] == "Property":
            data["property"] = data["amount"]  # Property value derived from amount
        elif data["narration"] in ["Fund lend to other accounts", "Sundry"]:
            data["sundry"] = data["amount"]  # Sundry value derived from amount

        print(f"\n[TEST] Testing entry: {data['entry_id']}")
        insert_journal_entry(
            db_connection=conn,
            entry_id=data["entry_id"],
            account_name=data["account_name"],
            entry_type=data["entry_type"],
            amount=data["amount"],
            narration=data["narration"],
            mop=data["mop"],
            entry_date=data["entry_date"],
            fd=data["fd"],
            sundry=data["sundry"],
            property=data["property"]
        )

if __name__ == "__main__":
    test_insert_journal_entry()
