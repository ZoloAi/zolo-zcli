# zCLI/subsystems/zLoader_modules/schema_cache.py
"""
Schema Cache - Active database connection management
"""

import time
from logger import Logger


class SchemaCache:
    """
    Schema cache for active database connections.
    
    Heavyweight cache - holds ACTIVE CONNECTIONS, not just parsed data.
    
    Lifecycle:
    - Single command: one-shot (connect → execute → disconnect)
    - zWizard: persistent (connect → reuse → disconnect at end)
    
    Can draw parsed schema from pinned_cache to speed up initialization,
    but manages its own connection instances.
    
    Key features:
    - Connection pooling (in-memory)
    - Transaction management
    - Auto-cleanup
    """
    
    def __init__(self, session):
        """
        Initialize schema cache.
        
        Args:
            session: zSession dict
        """
        self.session = session
        self.logger = Logger.get_logger()
        
        # In-memory connection storage (NOT in session)
        # Connections cannot be serialized, so we keep them in memory only
        self.connections = {}  # {alias_name: handler_instance}
        self.transaction_active = {}  # {alias_name: bool}
        
        # Ensure namespace exists (for metadata only)
        self._ensure_namespace()
    
    def _ensure_namespace(self):
        """Ensure schema_cache namespace exists in session (for metadata)."""
        if "zCache" not in self.session:
            self.session["zCache"] = {}
        
        if "schema_cache" not in self.session["zCache"]:
            self.session["zCache"]["schema_cache"] = {}
    
    def get_connection(self, alias_name):
        """
        Get active connection for alias.
        
        Args:
            alias_name: Alias name (without $ prefix)
            
        Returns:
            Handler instance or None
        """
        connection = self.connections.get(alias_name)
        if connection:
            self.logger.debug("[SchemaCache] Found connection for $%s", alias_name)
        return connection
    
    def set_connection(self, alias_name, handler):
        """
        Store active connection (in-memory).
        
        Args:
            alias_name: Alias name (without $ prefix)
            handler: ClassicalData or QuantumData handler instance
        """
        self.connections[alias_name] = handler
        
        # Store metadata in session (not the connection itself)
        self.session["zCache"]["schema_cache"][alias_name] = {
            "active": True,
            "connected_at": time.time(),
            "backend": handler.schema.get("Meta", {}).get("Data_Type", "unknown")
        }
        
        self.logger.debug("[SchemaCache] Stored connection for $%s", alias_name)
    
    def has_connection(self, alias_name):
        """
        Check if connection exists for alias.
        
        Args:
            alias_name: Alias name (without $ prefix)
            
        Returns:
            bool
        """
        return alias_name in self.connections
    
    def begin_transaction(self, alias_name):
        """
        Begin transaction for alias.
        
        Args:
            alias_name: Alias name (without $ prefix)
        """
        if alias_name in self.connections:
            handler = self.connections[alias_name]
            handler.adapter.begin_transaction()
            self.transaction_active[alias_name] = True
            self.logger.info("🔄 Transaction started for $%s", alias_name)
        else:
            self.logger.warning("Cannot begin transaction - no connection for $%s", alias_name)
    
    def commit_transaction(self, alias_name):
        """
        Commit transaction for alias.
        
        Args:
            alias_name: Alias name (without $ prefix)
        """
        if alias_name in self.connections:
            handler = self.connections[alias_name]
            handler.adapter.commit()
            self.transaction_active[alias_name] = False
            self.logger.info("✅ Transaction committed for $%s", alias_name)
        else:
            self.logger.warning("Cannot commit transaction - no connection for $%s", alias_name)
    
    def rollback_transaction(self, alias_name):
        """
        Rollback transaction for alias.
        
        Args:
            alias_name: Alias name (without $ prefix)
        """
        if alias_name in self.connections:
            handler = self.connections[alias_name]
            handler.adapter.rollback()
            self.transaction_active[alias_name] = False
            self.logger.warning("↩️  Transaction rolled back for $%s", alias_name)
        else:
            self.logger.warning("Cannot rollback transaction - no connection for $%s", alias_name)
    
    def is_transaction_active(self, alias_name):
        """
        Check if transaction is active for alias.
        
        Args:
            alias_name: Alias name (without $ prefix)
            
        Returns:
            bool
        """
        return self.transaction_active.get(alias_name, False)
    
    def disconnect(self, alias_name):
        """
        Disconnect specific connection.
        
        Args:
            alias_name: Alias name (without $ prefix)
        """
        if alias_name in self.connections:
            try:
                handler = self.connections[alias_name]
                handler.disconnect()
                self.logger.debug("[SchemaCache] Disconnected $%s", alias_name)
            except Exception as e:
                self.logger.warning("[SchemaCache] Error disconnecting $%s: %s", alias_name, e)
            finally:
                # Always remove from tracking
                del self.connections[alias_name]
                if alias_name in self.transaction_active:
                    del self.transaction_active[alias_name]
                if alias_name in self.session["zCache"]["schema_cache"]:
                    del self.session["zCache"]["schema_cache"][alias_name]
    
    def clear(self):
        """
        Disconnect all connections and clear cache.
        
        Used when zWizard completes or on cleanup.
        """
        for alias_name in list(self.connections.keys()):
            self.disconnect(alias_name)
        
        self.logger.debug("[SchemaCache] Cleared all connections")
    
    def list_connections(self):
        """
        List all active connections.
        
        Returns:
            List of dicts with connection info
        """
        connections = []
        for alias_name, metadata in self.session["zCache"]["schema_cache"].items():
            connections.append({
                "alias": alias_name,
                "backend": metadata.get("backend"),
                "connected_at": metadata.get("connected_at"),
                "age": time.time() - metadata.get("connected_at", time.time()),
                "transaction_active": self.is_transaction_active(alias_name)
            })
        return connections

