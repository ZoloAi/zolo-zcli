"""
Connection Info Module - Provides server information to clients
"""


class ConnectionInfoManager:
    """Manages connection information sent to clients"""
    
    def __init__(self, logger, cache_manager, zcli, walker):
        """
        Initialize connection info manager
        
        Args:
            logger: Logger instance
            cache_manager: CacheManager instance
            zcli: zCLI instance
            walker: Walker instance
        """
        self.logger = logger
        self.cache = cache_manager
        self.zcli = zcli
        self.walker = walker
    
    def get_connection_info(self):
        """
        Get connection info to send to client on connect
        
        Returns:
            dict: Connection information
        """
        info = {
            "server_version": "1.5.4",
            "features": ["schema_cache", "query_cache", "connection_info", "realtime_sync"],
            "cache_stats": self.cache.get_all_stats()
        }
        
        # Add available models if zData is available
        if self.walker and hasattr(self.walker, 'data'):
            try:
                info["available_models"] = self._discover_models()
            except Exception as e:
                self.logger.debug(f"[ConnectionInfo] Could not discover models: {e}")
        
        # Add session data if available
        if self.zcli and hasattr(self.zcli, 'session'):
            try:
                info["session"] = {
                    "workspace": getattr(self.zcli.session, 'workspace', None),
                    "mode": getattr(self.zcli, 'mode', 'Terminal')
                }
            except Exception as e:
                self.logger.debug(f"[ConnectionInfo] Could not get session info: {e}")
        
        return info
    
    def _discover_models(self):
        """
        Discover available data models by introspecting zData
        
        Returns:
            list: List of model info dicts
        """
        models = []
        
        try:
            # Try to get available models from zData
            if self.walker and hasattr(self.walker, 'data'):
                # Check if we can list tables
                if hasattr(self.walker.data, 'list_tables'):
                    tables = self.walker.data.list_tables()
                    for table in tables:
                        models.append({
                            'name': table,
                            'type': 'table',
                            'operations': ['create', 'read', 'update', 'delete']
                        })
                
                # Check if we can get schema info
                elif hasattr(self.walker.data, 'get_all_schemas'):
                    schemas = self.walker.data.get_all_schemas()
                    for schema_name, schema_data in schemas.items():
                        models.append({
                            'name': schema_name,
                            'type': 'schema',
                            'fields': list(schema_data.get('fields', {}).keys()) if isinstance(schema_data, dict) else [],
                            'operations': ['create', 'read', 'update', 'delete']
                        })
        
        except Exception as e:
            self.logger.debug(f"[ConnectionInfo] Model discovery error: {e}")
        
        return models
    
    def introspect_model(self, model_name):
        """
        Get detailed information about a specific model
        
        Args:
            model_name: Model name to introspect
            
        Returns:
            dict: Model metadata including fields, types, constraints
        """
        try:
            if self.walker and hasattr(self.walker, 'data'):
                schema = self.walker.data.get_schema(model_name)
                if schema:
                    return {
                        'name': model_name,
                        'schema': schema,
                        'operations': ['create', 'read', 'update', 'delete'],
                        'cacheable': True
                    }
        except Exception as e:
            self.logger.warning(f"[ConnectionInfo] Failed to introspect {model_name}: {e}")
        
        return None

