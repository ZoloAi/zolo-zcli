# zCLI/subsystems/zComm/zComm_modules/service_manager.py
"""Service Manager for local services like PostgreSQL and Redis."""

from .services.postgresql_service import PostgreSQLService

class ServiceManager:
    """Manages local development services like PostgreSQL and Redis."""

    def __init__(self, logger):
        self.logger = logger
        self.services = {}
        self.logger.info("Initializing ServiceManager")
        self._register_services()
        self.logger.info("ServiceManager initialized with %d services", len(self.services))

    def _register_services(self):
        """Register available service handlers."""
        self.logger.debug("Registering available services")

        self.services['postgresql'] = PostgreSQLService(self.logger)
        self.logger.debug("Registered PostgreSQL service")

        # TODO: Add Redis service support
        # TODO: Add MongoDB service support
        self.logger.debug("Service registration completed")

    def start(self, service_name, **kwargs):
        """Start a service with optional configuration, returns success status."""
        self.logger.info("Starting service: %s", service_name)

        if service_name not in self.services:
            self.logger.error("Unknown service: %s", service_name)
            return False

        service = self.services[service_name]
        self.logger.debug("Found service handler for: %s", service_name)

        result = service.start(**kwargs)

        if result:
            self.logger.info("Service '%s' started successfully", service_name)
        else:
            self.logger.error("Failed to start service '%s'", service_name)

        return result

    def stop(self, service_name):
        """Stop a service."""
        self.logger.info("Stopping service: %s", service_name)

        if service_name not in self.services:
            self.logger.error("Unknown service: %s", service_name)
            return False

        service = self.services[service_name]
        self.logger.debug("Found service handler for: %s", service_name)

        result = service.stop()

        if result:
            self.logger.info("Service '%s' stopped successfully", service_name)
        else:
            self.logger.error("Failed to stop service '%s'", service_name)

        return result

    def restart(self, service_name):
        """Restart a service."""
        self.logger.info("Restarting service: %s", service_name)

        stop_result = self.stop(service_name)
        if not stop_result:
            self.logger.error("Failed to stop service '%s' during restart", service_name)
            return False

        start_result = self.start(service_name)

        if start_result:
            self.logger.info("Service '%s' restarted successfully", service_name)
        else:
            self.logger.error("Failed to restart service '%s'", service_name)

        return start_result

    def status(self, service_name=None):
        """Get service status. Returns status dict for specific service or all services."""
        if service_name:
            self.logger.debug("Getting status for service: %s", service_name)
            if service_name not in self.services:
                self.logger.error("Unknown service: %s", service_name)
                return {"error": f"Unknown service: {service_name}"}
            status = self.services[service_name].status()
            self.logger.debug("Service '%s' status: %s", service_name, status)
            return status

        self.logger.debug("Getting status for all services")
        # Return status for all services
        status = {
            name: service.status()
            for name, service in self.services.items()
        }
        self.logger.debug("All services status: %s", status)
        return status

    def get_connection_info(self, service_name):
        """Get connection information for a service."""
        self.logger.debug("Getting connection info for service: %s", service_name)

        if service_name not in self.services:
            self.logger.error("Unknown service: %s", service_name)
            return None

        service = self.services[service_name]
        info = service.get_connection_info()
        self.logger.debug("Service '%s' connection info: %s", service_name, info)
        return info
