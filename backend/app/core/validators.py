"""
Input validation utilities
"""
import re
from fastapi import HTTPException


def validate_uuid(uuid_string: str, field_name: str = "UUID") -> str:
    """
    Validate UUID format (RFC 4122)
    
    Args:
        uuid_string: The UUID string to validate
        field_name: Name of the field for error messages
        
    Returns:
        The validated UUID string
        
    Raises:
        HTTPException: If UUID format is invalid
    """
    uuid_pattern = r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'
    
    if not uuid_string or not re.match(uuid_pattern, uuid_string):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} format. Expected UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )
    
    return uuid_string


def validate_positive_integer(value: int, field_name: str = "Value") -> int:
    """
    Validate that an integer is positive
    
    Args:
        value: The integer to validate
        field_name: Name of the field for error messages
        
    Returns:
        The validated value
        
    Raises:
        HTTPException: If value is not positive
    """
    if value < 0:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be a positive number. Got: {value}"
        )
    
    return value




