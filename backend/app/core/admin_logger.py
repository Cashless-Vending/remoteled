"""
Admin action logging utility
Logs all CRUD operations performed by admin users for audit trail
"""
from typing import Optional
from psycopg2.extras import RealDictCursor
from app.core.database import db


def log_admin_action(
    admin_email: str,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    admin_id: Optional[str] = None
) -> None:
    """
    Log an admin action to the admin_logs table
    
    Args:
        admin_email: Email of the admin performing the action
        action: Action type (LOGIN, REGISTER, CREATE_DEVICE, UPDATE_DEVICE, DELETE_DEVICE, etc.)
        entity_type: Type of entity being acted upon (device, service, order, etc.)
        entity_id: UUID of the entity being acted upon
        details: Human-readable description of the action
        ip_address: IP address of the request
        admin_id: UUID of the admin user
    """
    try:
        with db.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO admin_logs (admin_id, admin_email, action, entity_type, entity_id, details, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (admin_id, admin_email, action, entity_type, entity_id, details, ip_address)
            )
            cursor.connection.commit()
    except Exception as e:
        # Don't fail the main operation if logging fails
        print(f"Failed to log admin action: {e}")

