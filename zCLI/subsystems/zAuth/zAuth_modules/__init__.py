"""
zAuth Modules - Modular Authentication System (v1.5.4+)

This package contains the modularized components of zAuth:
- password_security: bcrypt password hashing and verification
- session_persistence: SQLite-based persistent session management
- authentication: User authentication (local and remote)
- rbac: Role-Based Access Control with permissions

Architecture: Facade pattern with clear separation of concerns.
"""

from .password_security import PasswordSecurity
from .session_persistence import SessionPersistence
from .authentication import Authentication
from .rbac import RBAC

__all__ = [
    'PasswordSecurity',
    'SessionPersistence',
    'Authentication',
    'RBAC'
]

