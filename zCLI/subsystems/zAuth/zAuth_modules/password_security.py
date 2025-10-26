"""
Password Security Module - bcrypt hashing and verification (v1.5.4+)

This module handles all password hashing and verification using bcrypt.
Isolated from zCLI dependencies for maximum testability and reusability.
"""

import bcrypt


class PasswordSecurity:
    """
    Password hashing and verification using bcrypt.
    
    Security Features:
    - bcrypt with 12 rounds (good balance of security/speed)
    - Random salting for each hash
    - One-way hashing (cannot recover plaintext)
    - Timing-safe comparison
    - 72-byte limit handling
    """
    
    def __init__(self, logger=None):
        """Initialize password security module.
        
        Args:
            logger: Optional logger instance for warnings/errors
        """
        self.logger = logger
    
    def hash_password(self, plain_password: str) -> str:
        """
        Hash a plaintext password using bcrypt.
        
        Args:
            plain_password: Plaintext password string
            
        Returns:
            str: bcrypt hashed password (UTF-8 decoded)
            
        Raises:
            ValueError: If password is empty or None
            
        Example:
            >>> pwd_security = PasswordSecurity()
            >>> hashed = pwd_security.hash_password("mypassword")
            >>> print(hashed[:7])
            '$2b$12$'
            
        Security:
            - Uses bcrypt with 12 rounds (good balance of security/speed)
            - Each hash includes a random salt
            - Same password produces different hashes (salted)
            - One-way: cannot recover plaintext from hash
            - Passwords > 72 bytes are truncated (bcrypt limit)
        """
        if not plain_password:
            raise ValueError("Password cannot be empty")
        
        # bcrypt has a 72-byte limit - truncate if necessary
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            if self.logger:
                self.logger.warning("[PasswordSecurity] Password > 72 bytes, truncating (bcrypt limit)")
            password_bytes = password_bytes[:72]
        
        # Generate salt and hash (12 rounds = ~0.3s on modern hardware)
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string (bcrypt returns bytes)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plaintext password against a bcrypt hash.
        
        Args:
            plain_password: Plaintext password to verify
            hashed_password: bcrypt hashed password (from database/storage)
            
        Returns:
            bool: True if password matches, False otherwise
            
        Example:
            >>> pwd_security = PasswordSecurity()
            >>> hashed = pwd_security.hash_password("correct_password")
            >>> pwd_security.verify_password("correct_password", hashed)
            True
            >>> pwd_security.verify_password("wrong_password", hashed)
            False
            
        Security:
            - Timing-safe comparison (constant time)
            - Handles invalid hashes gracefully (returns False)
            - Logs errors without exposing password details
            - Truncates passwords > 72 bytes (to match hash_password behavior)
        """
        if not plain_password or not hashed_password:
            return False
        
        try:
            # Truncate to 72 bytes (same as hash_password)
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            
            return bcrypt.checkpw(
                password_bytes,
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"[PasswordSecurity] Password verification error: {e}")
            return False

