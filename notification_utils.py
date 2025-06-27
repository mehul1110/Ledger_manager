from db_connect import get_connection

def create_notification(entry_id, status):
    """
    Create a global notification about entry approval/rejection visible to all users
    
    Args:
        entry_id: The entry ID that was approved/rejected
        status: 'approved' or 'rejected'
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notifications (entry_id, status)
            VALUES (%s, %s)
        """, (entry_id, status))
        
        conn.commit()
        print(f"✅ Notification created: {entry_id} {status}")
        
    except Exception as e:
        print(f"❌ Error creating notification: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def get_recent_notifications(limit=5):
    """
    Get recent notifications for display on sidebar (visible to all users)
    
    Args:
        limit: Maximum number of notifications to return (default 5)
        
    Returns:
        List of notification dictionaries
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT entry_id, status, created_at 
            FROM notifications 
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                'entry_id': row[0],
                'status': row[1],
                'created_at': row[2]
            })
        
        return notifications
        
    except Exception as e:
        print(f"❌ Error getting notifications: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def cleanup_old_notifications(days_old=30):
    """
    Remove notifications older than specified days to prevent table bloat
    
    Args:
        days_old: Delete notifications older than this many days (default 30)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM notifications 
            WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (days_old,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        if deleted_count > 0:
            print(f"✅ Cleaned up {deleted_count} old notifications")
        
    except Exception as e:
        print(f"❌ Error cleaning up notifications: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
