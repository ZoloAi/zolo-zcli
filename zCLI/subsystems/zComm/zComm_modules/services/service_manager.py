"""
Service Manager
Manages local services (PostgreSQL, Redis, etc.)
"""

from .postgresql_service import PostgreSQLService


class ServiceManager:
    """
    Manages local development services.
    
    Provides unified interface for starting, stopping, and monitoring
    local services like PostgreSQL, Redis, etc.
    """

    def __init__(self, logger):
        self.logger = logger
        self.services = {}
        self._register_services()

    def _register_services(self):
        """Register available service handlers."""
        self.services['postgresql'] = PostgreSQLService(self.logger)
        # Future: self.services['redis'] = RedisService(self.logger)
        # Future: self.services['mongodb'] = MongoDBService(self.logger)
    
    def start(self, service_name, **kwargs):
        """
        Start a service.
        
        Args:
            service_name (str): Service to start
            **kwargs: Service-specific configuration
            
        Returns:
            bool: True if started successfully
        """
        if service_name not in self.services:
            self.logger.error("Unknown service: %s", service_name)
            return False
        
        service = self.services[service_name]
        return service.start(**kwargs)
    
    def stop(self, service_name):
        """Stop a service."""
        if service_name not in self.services:
            self.logger.error("Unknown service: %s", service_name)
            return False
        
        service = self.services[service_name]
        return service.stop()
    
    def restart(self, service_name):
        """Restart a service."""
        self.stop(service_name)
        return self.start(service_name)
    
    def status(self, service_name=None):
        """
        Get service status.
        
        Args:
            service_name: Specific service or None for all
            
        Returns:
            dict: Status information
        """
        if service_name:
            if service_name not in self.services:
                return {"error": f"Unknown service: {service_name}"}
            return self.services[service_name].status()
        else:
            # Return status for all services
            return {
                name: service.status()
                for name, service in self.services.items()
            }
    
    def get_connection_info(self, service_name):
        """Get connection information for a service."""
        if service_name not in self.services:
            self.logger.error("Unknown service: %s", service_name)
            return None
        
        service = self.services[service_name]
        return service.get_connection_info()

