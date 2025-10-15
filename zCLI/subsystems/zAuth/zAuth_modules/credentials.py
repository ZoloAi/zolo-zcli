"""
zAuth/zAuth_modules/credentials.py
Credential storage and management
"""

import os
import json
from pathlib import Path


class CredentialManager:
    """Manages credential storage and retrieval."""
    
    def __init__(self, credentials_dir=None):
        """Initialize credential manager."""
        self.credentials_dir = credentials_dir or (Path.home() / ".zolo")
        self.credentials_file = self.credentials_dir / "credentials"
        
        # Ensure credentials directory exists
        self.credentials_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, credentials, logger=None):
        """Save credentials to local file."""
        try:
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2)
            
            # Set file permissions to user-only (600)
            os.chmod(self.credentials_file, 0o600)
            
            if logger:
                logger.debug("Credentials saved to: %s", self.credentials_file)
        
        except Exception as e:
            if logger:
                logger.error("Error saving credentials: %s", e)
            raise
    
    def load(self, logger=None):
        """Load credentials from local file."""
        try:
            if not self.credentials_file.exists():
                return None
            
            with open(self.credentials_file, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
            
            if logger:
                logger.debug("Credentials loaded from: %s", self.credentials_file)
            return credentials
        
        except Exception as e:
            if logger:
                logger.error("Error loading credentials: %s", e)
            return None
    
    def delete(self, logger=None):
        """Delete stored credentials."""
        try:
            if self.credentials_file.exists():
                self.credentials_file.unlink()
                if logger:
                    logger.info("[*] Logged out - credentials removed")
                return True
            return False
        except Exception as e:
            if logger:
                logger.error("Error deleting credentials: %s", e)
            raise
    
    def restore_to_session(self, session, logger=None):
        """Restore zSession authentication from saved credentials file."""
        if not session:
            return
        
        credentials = self.load(logger)
        if credentials:
            # Update zSession with saved credentials
            session["zAuth"].update({
                "id": credentials.get("user_id"),
                "username": credentials.get("username"),
                "role": credentials.get("role"),
                "API_Key": credentials.get("api_key")
            })
            
            if logger:
                logger.debug("Restored zSession from saved credentials: %s", 
                            credentials.get("username"))

