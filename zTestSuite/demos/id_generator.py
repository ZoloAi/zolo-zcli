#!/usr/bin/env python3
# zTestSuite/demos/id_generator.py

"""
ID Generator Plugin - For testing plugin integration with zData.

Provides various ID generation functions commonly needed in database operations:
- UUID generation
- Prefixed IDs
- Sequential IDs
- Timestamps
"""

import uuid
import time
from datetime import datetime


def generate_uuid():
    """
    Generate a UUID string.
    
    Returns:
        str: UUID in string format
        
    Example:
        >>> generate_uuid()
        "550e8400-e29b-41d4-a716-446655440000"
    """
    return str(uuid.uuid4())


def prefixed_id(prefix):
    """
    Generate ID with custom prefix and timestamp.
    
    Args:
        prefix (str): Prefix for the ID
        
    Returns:
        str: Prefixed ID with timestamp and random component
        
    Example:
        >>> prefixed_id("USER")
        "USER_1234567890_a1b2c3d4"
    """
    timestamp = int(time.time())
    random_part = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{random_part}"


def short_uuid():
    """
    Generate a short UUID (8 characters).
    
    Returns:
        str: Short UUID
        
    Example:
        >>> short_uuid()
        "a1b2c3d4"
    """
    return uuid.uuid4().hex[:8]


def get_timestamp(format_type="iso"):
    """
    Get current timestamp in various formats.
    
    Args:
        format_type (str): Format type - "iso", "unix", or "readable"
        
    Returns:
        str or int: Timestamp in requested format
        
    Example:
        >>> get_timestamp("iso")
        "2025-10-19T16:30:00"
        >>> get_timestamp("unix")
        1729356600
    """
    now = datetime.now()
    
    if format_type == "iso":
        return now.isoformat()
    elif format_type == "unix":
        return int(now.timestamp())
    elif format_type == "readable":
        return now.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return now.isoformat()


def sequential_id(base=1000):
    """
    Generate a sequential ID starting from base.
    
    Args:
        base (int): Starting number
        
    Returns:
        int: Sequential ID
        
    Note:
        This is a simple implementation. For production use,
        query the database for the current max ID.
    """
    return base + int(time.time() % 1000)


def composite_id(prefix, separator="_"):
    """
    Generate a composite ID with multiple components.
    
    Args:
        prefix (str): ID prefix
        separator (str): Separator character
        
    Returns:
        str: Composite ID
        
    Example:
        >>> composite_id("ORD")
        "ORD_20251019_a1b2c3d4"
    """
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = uuid.uuid4().hex[:8]
    return f"{prefix}{separator}{date_part}{separator}{random_part}"

