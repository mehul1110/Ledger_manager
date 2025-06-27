"""
BAHI-KHATA Role-Based Permission System

Simple and clean permission management for 3 roles:
- admin: Everything
- accountant: Everything except transaction approval
- viewer: Read-only access
"""

class Permissions:
    """All available permissions in the system"""
    
    # 📊 Viewing Data
    VIEW_ACCOUNTS = "view_accounts"
    VIEW_TRANSACTIONS = "view_transactions"
    VIEW_PENDING_TRANSACTIONS = "view_pending_transactions"
    VIEW_REPORTS = "view_reports"
    VIEW_BALANCE_SHEET = "view_balance_sheet"
    VIEW_JOURNAL_ENTRIES = "view_journal_entries"
    VIEW_ERROR_LOGS = "view_error_logs"
    
    # ✏️ Creating/Editing Data
    ADD_ACCOUNTS = "add_accounts"
    ADD_RECEIPTS = "add_receipts"
    ADD_PAYMENTS = "add_payments"
    ADD_PROPERTY = "add_property"
    ADD_FD = "add_fd"
    EDIT_ACCOUNTS = "edit_accounts"
    EDIT_TRANSACTIONS = "edit_transactions"
    EDIT_PROPERTY = "edit_property"
    
    # ❌ Deleting Data
    DELETE_ACCOUNTS = "delete_accounts"
    DELETE_TRANSACTIONS = "delete_transactions"
    
    # ✅ Approvals
    APPROVE_TRANSACTIONS = "approve_transactions"
    REJECT_TRANSACTIONS = "reject_transactions"
    APPROVE_FD_MATURITY = "approve_fd_maturity"
    
    # 🔧 System Functions
    EXPORT_DATA = "export_data"
    MANAGE_USERS = "manage_users"
    BACKUP_DATABASE = "backup_database"
    SYSTEM_SETTINGS = "system_settings"


# Define role permissions - CUSTOMIZED FOR YOUR BUSINESS
ROLE_PERMISSIONS = {
    'admin': [
        # 🔑 ADMIN HAS EVERYTHING
        Permissions.VIEW_ACCOUNTS,
        Permissions.VIEW_TRANSACTIONS,
        Permissions.VIEW_PENDING_TRANSACTIONS,
        Permissions.VIEW_REPORTS,
        Permissions.VIEW_BALANCE_SHEET,
        Permissions.VIEW_JOURNAL_ENTRIES,
        Permissions.VIEW_ERROR_LOGS,
        Permissions.ADD_ACCOUNTS,
        Permissions.ADD_RECEIPTS,
        Permissions.ADD_PAYMENTS,
        Permissions.ADD_PROPERTY,
        Permissions.ADD_FD,
        Permissions.EDIT_ACCOUNTS,
        Permissions.EDIT_TRANSACTIONS,
        Permissions.EDIT_PROPERTY,
        Permissions.DELETE_ACCOUNTS,
        Permissions.DELETE_TRANSACTIONS,
        Permissions.APPROVE_TRANSACTIONS,
        Permissions.REJECT_TRANSACTIONS,
        Permissions.APPROVE_FD_MATURITY,
        Permissions.EXPORT_DATA,
        Permissions.MANAGE_USERS,
        Permissions.BACKUP_DATABASE,
        Permissions.SYSTEM_SETTINGS,
    ],
    
    'accountant': [
        # 📊 ACCOUNTANT: Everything EXCEPT transaction approval
        Permissions.VIEW_ACCOUNTS,
        Permissions.VIEW_TRANSACTIONS,
        Permissions.VIEW_PENDING_TRANSACTIONS,
        Permissions.VIEW_REPORTS,
        Permissions.VIEW_BALANCE_SHEET,
        Permissions.VIEW_JOURNAL_ENTRIES,
        Permissions.VIEW_ERROR_LOGS,
        Permissions.ADD_ACCOUNTS,
        Permissions.ADD_RECEIPTS,
        Permissions.ADD_PAYMENTS,
        Permissions.ADD_PROPERTY,
        Permissions.ADD_FD,
        Permissions.EDIT_ACCOUNTS,
        Permissions.EDIT_TRANSACTIONS,
        Permissions.EDIT_PROPERTY,
        Permissions.DELETE_ACCOUNTS,
        Permissions.DELETE_TRANSACTIONS,
        # ❌ NO TRANSACTION APPROVAL - Only admin can approve
        Permissions.APPROVE_FD_MATURITY,  # ✅ Can approve FD maturity
        Permissions.EXPORT_DATA,
    ],
    
    'viewer': [
        # 👁️ VIEWER: Read-only access to everything
        Permissions.VIEW_ACCOUNTS,
        Permissions.VIEW_TRANSACTIONS,
        Permissions.VIEW_PENDING_TRANSACTIONS,
        Permissions.VIEW_REPORTS,
        Permissions.VIEW_BALANCE_SHEET,
        Permissions.VIEW_JOURNAL_ENTRIES,
        # ❌ Cannot add, edit, delete, or approve anything
    ],
}


def has_permission(user_role, permission):
    """Check if a user role has a specific permission"""
    if user_role not in ROLE_PERMISSIONS:
        return False
    return permission in ROLE_PERMISSIONS[user_role]


def get_user_permissions(user_role):
    """Get all permissions for a specific user role"""
    return ROLE_PERMISSIONS.get(user_role, [])


def check_permission_with_message(user_info, permission, action_name="perform this action"):
    """Check permission and show user-friendly message if denied"""
    user_role = user_info.get('role', 'viewer')
    
    if has_permission(user_role, permission):
        return True
    
    from tkinter import messagebox
    messagebox.showwarning(
        "Access Denied", 
        f"You don't have permission to {action_name}.\n\n"
        f"Your role: {user_role.title()}\n"
        f"Required permission: {permission.replace('_', ' ').title()}\n\n"
        f"Please contact your administrator if you need access."
    )
    return False


def get_role_description(role):
    """Get a human-readable description of a role's capabilities"""
    descriptions = {
        'admin': "Full system access - Everything including user management and transaction approval",
        'accountant': "Full accounting access - Can enter transactions, approve FD maturity, but cannot approve transactions after input",
        'viewer': "Read-only access - Can view all accounts, transactions, and reports"
    }
    return descriptions.get(role, "Unknown role")


if __name__ == "__main__":
    # Test the permission system
    print("=== BAHI-KHATA Permission System ===\n")
    
    for role in ROLE_PERMISSIONS:
        print(f"{role.upper()}: {get_role_description(role)}")
        permissions = get_user_permissions(role)
        print(f"  Total permissions: {len(permissions)}")
        print()
    
    # Test specific permissions
    print("=== PERMISSION TESTS ===")
    print(f"Admin can approve transactions: {has_permission('admin', Permissions.APPROVE_TRANSACTIONS)}")
    print(f"Accountant can approve transactions: {has_permission('accountant', Permissions.APPROVE_TRANSACTIONS)}")
    print(f"Accountant can approve FD maturity: {has_permission('accountant', Permissions.APPROVE_FD_MATURITY)}")
    print(f"Viewer can view transactions: {has_permission('viewer', Permissions.VIEW_TRANSACTIONS)}")
    print(f"Viewer can add payments: {has_permission('viewer', Permissions.ADD_PAYMENTS)}")
