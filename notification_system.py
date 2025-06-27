"""
Notification System for BAHI-KHATA
Handles creating and managing user notifications, especially for transaction approvals/rejections
"""

import db_connect
from datetime import datetime


def create_notification(user_id, title, message, notification_type='info', transaction_id=None):
    """
    Create a notification for a specific user
    
    Args:
        user_id (int): ID of the user to notify
        title (str): Short title for the notification
        message (str): Detailed message
        notification_type (str): Type of notification ('approval', 'rejection', 'info', 'warning', 'error')
        transaction_id (int, optional): ID of related transaction
    
    Returns:
        bool: True if notification was created successfully
    """
    try:
        conn = db_connect.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notifications (user_id, title, message, notification_type, transaction_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, title, message, notification_type, transaction_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Notification created for user {user_id}: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating notification: {e}")
        return False


def notify_accountants_transaction_approved(entry_id, transaction_details):
    """
    Notify all accountants when a transaction is approved by admin
    
    Args:
        entry_id (str): The entry ID that was approved
        transaction_details (dict): Details of the approved transaction
    """
    try:
        conn = db_connect.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all users with 'accountant' role
        cursor.execute("SELECT user_id, username FROM users WHERE role = 'accountant' AND is_active = TRUE")
        accountants = cursor.fetchall()
        
        if not accountants:
            print("ℹ️ No active accountants found to notify")
            cursor.close()
            conn.close()
            return
        
        # Create notification for each accountant
        title = f"Transaction Approved - Entry #{entry_id}"
        message = f"Transaction entry #{entry_id} has been approved by admin.\n\n" \
                 f"Details:\n" \
                 f"• Type: {transaction_details.get('transaction_type', 'Unknown').title()}\n" \
                 f"• Account: {transaction_details.get('account_name', 'Unknown')}\n" \
                 f"• Amount: ₹{transaction_details.get('amount', 0):,.2f}\n" \
                 f"• Date: {transaction_details.get('transaction_date', 'Unknown')}\n" \
                 f"• Narration: {transaction_details.get('narration', 'N/A')}"
        
        for accountant in accountants:
            create_notification(
                user_id=accountant['user_id'],
                title=title,
                message=message,
                notification_type='approval',
                transaction_id=entry_id
            )
        
        cursor.close()
        conn.close()
        print(f"✅ Notified {len(accountants)} accountants about approved transaction #{entry_id}")
        
    except Exception as e:
        print(f"❌ Error notifying accountants about approval: {e}")


def notify_accountants_transaction_rejected(entry_id, transaction_details):
    """
    Notify all accountants when a transaction is rejected by admin
    
    Args:
        entry_id (str): The entry ID that was rejected
        transaction_details (dict): Details of the rejected transaction
    """
    try:
        conn = db_connect.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all users with 'accountant' role
        cursor.execute("SELECT user_id, username FROM users WHERE role = 'accountant' AND is_active = TRUE")
        accountants = cursor.fetchall()
        
        if not accountants:
            print("ℹ️ No active accountants found to notify")
            cursor.close()
            conn.close()
            return
        
        # Create notification for each accountant
        title = f"Transaction Rejected - Entry #{entry_id}"
        message = f"Transaction entry #{entry_id} has been rejected by admin.\n\n" \
                 f"Details:\n" \
                 f"• Type: {transaction_details.get('transaction_type', 'Unknown').title()}\n" \
                 f"• Account: {transaction_details.get('account_name', 'Unknown')}\n" \
                 f"• Amount: ₹{transaction_details.get('amount', 0):,.2f}\n" \
                 f"• Date: {transaction_details.get('transaction_date', 'Unknown')}\n" \
                 f"• Narration: {transaction_details.get('narration', 'N/A')}\n\n" \
                 f"Please review the transaction details and create a new entry if needed."
        
        for accountant in accountants:
            create_notification(
                user_id=accountant['user_id'],
                title=title,
                message=message,
                notification_type='rejection',
                transaction_id=entry_id
            )
        
        cursor.close()
        conn.close()
        print(f"✅ Notified {len(accountants)} accountants about rejected transaction #{entry_id}")
        
    except Exception as e:
        print(f"❌ Error notifying accountants about rejection: {e}")


def get_user_notifications(user_id, limit=50, unread_only=False):
    """
    Get notifications for a specific user
    
    Args:
        user_id (int): ID of the user
        limit (int): Maximum number of notifications to retrieve
        unread_only (bool): If True, only return unread notifications
    
    Returns:
        list: List of notification dictionaries
    """
    try:
        conn = db_connect.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        base_query = """
            SELECT notification_id, title, message, notification_type, is_read, 
                   created_at, read_at, transaction_id
            FROM notifications 
            WHERE user_id = %s
        """
        
        if unread_only:
            base_query += " AND is_read = FALSE"
        
        base_query += " ORDER BY created_at DESC LIMIT %s"
        
        cursor.execute(base_query, (user_id, limit))
        notifications = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return notifications
        
    except Exception as e:
        print(f"❌ Error getting user notifications: {e}")
        return []


def mark_notification_as_read(notification_id):
    """
    Mark a notification as read
    
    Args:
        notification_id (int): ID of the notification to mark as read
    
    Returns:
        bool: True if successfully marked as read
    """
    try:
        conn = db_connect.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE notifications 
            SET is_read = TRUE, read_at = %s 
            WHERE notification_id = %s
        """, (datetime.now(), notification_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error marking notification as read: {e}")
        return False


def get_unread_notification_count(user_id):
    """
    Get the count of unread notifications for a user
    
    Args:
        user_id (int): ID of the user
    
    Returns:
        int: Number of unread notifications
    """
    try:
        conn = db_connect.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = %s AND is_read = FALSE", (user_id,))
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return count
        
    except Exception as e:
        print(f"❌ Error getting unread notification count: {e}")
        return 0


def delete_old_notifications(days_old=30):
    """
    Delete notifications older than specified days
    
    Args:
        days_old (int): Delete notifications older than this many days
    
    Returns:
        int: Number of notifications deleted
    """
    try:
        conn = db_connect.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM notifications 
            WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (days_old,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Deleted {deleted_count} old notifications")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Error deleting old notifications: {e}")
        return 0


if __name__ == "__main__":
    # Test the notification system
    print("🧪 Testing Notification System...")
    
    # Test creating a notification (you'll need to adjust user_id to existing user)
    print("Testing notification creation...")
    # create_notification(1, "Test Notification", "This is a test message", "info")
    
    print("✅ Notification system ready")
