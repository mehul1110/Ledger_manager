#!/usr/bin/env python3
"""
Test database connection and identify unread result issues
"""

import mysql.connector
import db_connect

def test_basic_connection():
    """Test basic database connection"""
    print("=== Testing Basic Database Connection ===")
    try:
        conn = db_connect.get_connection()
        print("✅ Connection established")
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f"✅ Query result: {result}")
        
        cursor.close()
        conn.close()
        print("✅ Connection closed properly")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_table_access():
    """Test access to all main tables"""
    print("\n=== Testing Table Access ===")
    tables_to_test = [
        'accounts', 'payments', 'receipts', 
        'journal_entries', 'pending_transactions', 'users'
    ]
    
    try:
        conn = db_connect.get_connection()
        cursor = conn.cursor()
        
        for table in tables_to_test:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: {count} records")
            except Exception as e:
                print(f"❌ {table}: {e}")
        
        cursor.close()
        conn.close()
        print("✅ Table access test completed")
        return True
        
    except Exception as e:
        print(f"❌ Table access error: {e}")
        return False

def test_module_imports():
    """Test importing all backend modules"""
    print("\n=== Testing Module Imports ===")
    modules_to_test = [
        'db_connect', 'add_payment', 'add_receipt', 
        'add_account', 'journal_utils', 'transaction_approver'
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} imported successfully")
        except Exception as e:
            print(f"❌ {module_name}: {e}")

if __name__ == "__main__":
    print("BAHI-KHATA Backend Connection Test")
    print("=" * 40)
    
    # Run all tests
    test_basic_connection()
    test_table_access()
    test_module_imports()
    
    print("\n" + "=" * 40)
    print("Backend connection test completed!")
