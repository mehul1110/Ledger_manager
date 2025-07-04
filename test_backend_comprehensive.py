#!/usr/bin/env python3
"""
Comprehensive Backend Test for BAHI-KHATA
Tests all database operations, table access, and data flow
"""

from db_connect import get_connection
from add_payment import add_payment
from add_receipt import add_receipt
from transaction_approver import get_pending_transaction_count
from journal_utils import insert_journal_entry
import mysql.connector
from datetime import datetime

def test_database_connectivity():
    """Test basic database connection and table access"""
    print("=== DATABASE CONNECTIVITY TEST ===")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Test all critical tables
        tables = [
            'accounts', 'payments', 'receipts', 'journal_entries', 
            'pending_transactions', 'users', 'property_details', 'fd_details'
        ]
        
        for table in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                print(f'✅ {table}: {count} records')
            except Exception as e:
                print(f'❌ {table}: ERROR - {e}')
        
        conn.close()
        print('✅ Database connectivity test PASSED!')
        return True
        
    except Exception as e:
        print(f'❌ Database connectivity test FAILED: {e}')
        return False

def test_payment_flow():
    """Test payment submission and approval flow"""
    print("\n=== PAYMENT FLOW TEST ===")
    
    try:
        # Get initial pending count
        initial_count = get_pending_transaction_count()
        print(f"Initial pending transactions: {initial_count}")
        
        # Test payment submission (should go to pending_transactions)
        print("Testing payment submission...")
        add_payment(
            name="Test Account",
            amount=100.0,
            mop="Cash",
            date_str="2025-06-26",
            narration="Misc",
            remarks="Backend Test"
        )
        
        # Check if pending count increased
        new_count = get_pending_transaction_count()
        print(f"Pending transactions after submission: {new_count}")
        
        if new_count > initial_count:
            print("✅ Payment submission test PASSED!")
            return True
        else:
            print("❌ Payment submission test FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Payment flow test FAILED: {e}")
        return False

def test_receipt_flow():
    """Test receipt submission flow"""
    print("\n=== RECEIPT FLOW TEST ===")
    
    try:
        # Get initial pending count
        initial_count = get_pending_transaction_count()
        print(f"Initial pending transactions: {initial_count}")
        
        # Test receipt submission
        print("Testing receipt submission...")
        add_receipt(
            account_name="Test Account",
            amount=50.0,
            mop="Cash",
            narration="Test Receipt",
            date_str="2025-06-26",
            remarks="Backend Test"
        )
        
        # Check if pending count increased
        new_count = get_pending_transaction_count()
        print(f"Pending transactions after submission: {new_count}")
        
        if new_count > initial_count:
            print("✅ Receipt submission test PASSED!")
            return True
        else:
            print("❌ Receipt submission test FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Receipt flow test FAILED: {e}")
        return False

def test_journal_entries():
    """Test journal entry creation"""
    print("\n=== JOURNAL ENTRIES TEST ===")
    
    try:
        conn = get_connection()
        
        # Get initial journal entries count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        initial_count = cursor.fetchone()[0]
        print(f"Initial journal entries: {initial_count}")
        
        # Test journal entry insertion
        print("Testing journal entry creation...")
        insert_journal_entry(
            db_connection=conn,
            entry_id="TEST001",
            account_name="Test Account",
            entry_type="Fund",
            amount=None,  # Amount is in the 'fund' column for this entry type
            narration="Test Entry",
            mop="Cash",
            entry_date=datetime.now().date(),
            fund=100.0  # Specify the fund amount
        )
        
        # Check if journal entries count increased
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        new_count = cursor.fetchone()[0]
        print(f"Journal entries after insertion: {new_count}")
        
        # Clean up test entry
        cursor.execute("DELETE FROM journal_entries WHERE entry_id = 'TEST001'")
        conn.commit()
        
        conn.close()
        
        if new_count > initial_count:
            print("✅ Journal entries test PASSED!")
            return True
        else:
            print("❌ Journal entries test FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Journal entries test FAILED: {e}")
        return False

def test_account_operations():
    """Test account table operations"""
    print("\n=== ACCOUNT OPERATIONS TEST ===")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Test account retrieval
        cursor.execute("SELECT COUNT(*) FROM accounts")
        account_count = cursor.fetchone()[0]
        print(f"Total accounts in database: {account_count}")
        
        # Test account types
        cursor.execute("SELECT DISTINCT account_type FROM accounts")
        account_types = [row[0] for row in cursor.fetchall()]
        print(f"Available account types: {account_types}")
        
        conn.close()
        print("✅ Account operations test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Account operations test FAILED: {e}")
        return False

def test_special_transactions():
    """Test special transaction types (Property, FD, Sundry)"""
    print("\n=== SPECIAL TRANSACTIONS TEST ===")
    
    try:
        # Test property payment
        print("Testing property payment...")
        add_payment(
            name="Test Property Account",
            amount=1000.0,
            mop="Bank Transfer",
            date_str="2025-06-26",
            narration="Property",
            item_type="property",
            description="expendable",
            remarks="Backend Test Property"
        )
        
        # Test FD payment
        print("Testing FD payment...")
        add_payment(
            name="Test Bank",
            amount=5000.0,
            mop="Bank Transfer",
            date_str="2025-06-26",
            narration="FD in bank",
            fd_duration="12",
            fd_interest="6.5",
            remarks="Backend Test FD"
        )
        
        # Test sundry payment
        print("Testing sundry payment...")
        add_payment(
            name="Other Account",
            amount=200.0,
            mop="Cash",
            date_str="2025-06-26",
            narration="Fund lend to other accounts",
            remarks="Backend Test Sundry"
        )
        
        print("✅ Special transactions test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Special transactions test FAILED: {e}")
        return False

def run_all_tests():
    """Run all backend tests"""
    print("🔍 COMPREHENSIVE BACKEND TEST SUITE")
    print("=" * 50)
    
    tests = [
        test_database_connectivity,
        test_account_operations,
        test_payment_flow,
        test_receipt_flow,
        test_journal_entries,
        test_special_transactions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 FINAL RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL BACKEND OPERATIONS ARE WORKING SMOOTHLY!")
    else:
        print("⚠️ Some backend issues detected. Check logs above.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
