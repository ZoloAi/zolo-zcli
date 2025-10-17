# zCLI/subsystems/zComm/zComm_modules/services/postgresql_service.py

"""
PostgreSQL Service Manager
Detects and manages local PostgreSQL installation
"""

from zCLI import subprocess, socket, platform, Path


class PostgreSQLService:
    """
    Manages local PostgreSQL service.
    
    Supports:
    - System PostgreSQL (via brew, systemd, pg_ctl)
    - Detection of running instances
    - Connection information
    """
    
    DEFAULT_PORT = 5432
    DEFAULT_USER = "postgres"
    
    def __init__(self, logger):
        self.logger = logger
        self.os_type = platform.system()  # 'Darwin', 'Linux', 'Windows'
    
    def start(self, **kwargs):  # pylint: disable=unused-argument
        """
        Start PostgreSQL service.
        
        Tries multiple methods based on OS and installation type.
        """
        # Check if already running
        if self.is_running():
            self.logger.info("PostgreSQL is already running on port %d", self.DEFAULT_PORT)
            return True
        
        self.logger.info("Starting PostgreSQL service...")
        
        # Try different start methods based on OS
        if self.os_type == "Darwin":  # macOS
            return self._start_macos()
        elif self.os_type == "Linux":
            return self._start_linux()
        elif self.os_type == "Windows":
            return self._start_windows()
        else:
            self.logger.error("Unsupported operating system: %s", self.os_type)
            return False
    
    def stop(self):
        """Stop PostgreSQL service."""
        if not self.is_running():
            self.logger.info("PostgreSQL is not running")
            return True
        
        self.logger.info("Stopping PostgreSQL service...")
        
        if self.os_type == "Darwin":
            return self._stop_macos()
        elif self.os_type == "Linux":
            return self._stop_linux()
        elif self.os_type == "Windows":
            return self._stop_windows()
        
        return False
    
    def is_running(self, port=None):
        """
        Check if PostgreSQL is running.
        
        Args:
            port: Port to check (default: 5432)
            
        Returns:
            bool: True if running
        """
        check_port = port or self.DEFAULT_PORT
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', check_port))
            sock.close()
            return result == 0  # 0 means port is in use (PostgreSQL running)
        except Exception as e:
            self.logger.debug("Error checking PostgreSQL port: %s", e)
            return False
    
    def status(self):
        """
        Get PostgreSQL service status.
        
        Returns:
            dict: Status information
        """
        running = self.is_running()
        
        status_info = {
            "service": "postgresql",
            "running": running,
            "port": self.DEFAULT_PORT,
            "os": self.os_type
        }
        
        if running:
            status_info["connection_info"] = self.get_connection_info()
        else:
            status_info["message"] = "PostgreSQL not detected. Install with: " + self._get_install_command()
        
        return status_info
    
    def get_connection_info(self):
        """Get connection information for PostgreSQL."""
        return {
            "host": "localhost",
            "port": self.DEFAULT_PORT,
            "user": self.DEFAULT_USER,
            "database": "postgres",  # Default database
            "connection_string": f"postgresql://{self.DEFAULT_USER}@localhost:{self.DEFAULT_PORT}/postgres"
        }
    
    # ═══════════════════════════════════════════════════════════
    # Platform-Specific Start Methods
    # ═══════════════════════════════════════════════════════════
    
    def _start_macos(self):
        """Start PostgreSQL on macOS."""
        # Try Homebrew first
        if self._has_command("brew"):
            try:
                result = subprocess.run(
                    ["brew", "services", "start", "postgresql@14"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.logger.info("✅ PostgreSQL started via Homebrew")
                    return True
                
                # Try without version
                result = subprocess.run(
                    ["brew", "services", "start", "postgresql"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.logger.info("✅ PostgreSQL started via Homebrew")
                    return True
                    
            except Exception as e:
                self.logger.error("Failed to start PostgreSQL via brew: %s", e)
        
        # Try pg_ctl
        if self._has_command("pg_ctl"):
            return self._start_with_pg_ctl()
        
        self.logger.error("❌ Could not start PostgreSQL. Install with: brew install postgresql")
        return False
    
    def _start_linux(self):
        """Start PostgreSQL on Linux."""
        # Try systemd
        if self._has_command("systemctl"):
            try:
                result = subprocess.run(
                    ["sudo", "systemctl", "start", "postgresql"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.logger.info("✅ PostgreSQL started via systemd")
                    return True
            except Exception as e:
                self.logger.error("Failed to start PostgreSQL via systemd: %s", e)
        
        # Try pg_ctl
        if self._has_command("pg_ctl"):
            return self._start_with_pg_ctl()
        
        self.logger.error("❌ Could not start PostgreSQL")
        return False
    
    def _start_windows(self):
        """Start PostgreSQL on Windows."""
        # Try Windows service
        try:
            result = subprocess.run(
                ["net", "start", "postgresql"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info("✅ PostgreSQL started via Windows service")
                return True
        except Exception as e:
            self.logger.error("Failed to start PostgreSQL on Windows: %s", e)
        
        return False
    
    def _start_with_pg_ctl(self):
        """Start PostgreSQL using pg_ctl."""
        # Find data directory
        data_dir = self._find_postgres_data_dir()
        if not data_dir:
            self.logger.error("Could not find PostgreSQL data directory")
            return False
        
        try:
            result = subprocess.run(
                ["pg_ctl", "-D", str(data_dir), "start"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info("✅ PostgreSQL started with pg_ctl")
                return True
        except Exception as e:
            self.logger.error("Failed to start PostgreSQL with pg_ctl: %s", e)
        
        return False
    
    # ═══════════════════════════════════════════════════════════
    # Platform-Specific Stop Methods
    # ═══════════════════════════════════════════════════════════
    
    def _stop_macos(self):
        """Stop PostgreSQL on macOS."""
        if self._has_command("brew"):
            try:
                subprocess.run(["brew", "services", "stop", "postgresql"], timeout=10)
                self.logger.info("✅ PostgreSQL stopped")
                return True
            except Exception as e:
                self.logger.error("Failed to stop PostgreSQL: %s", e)
        return False
    
    def _stop_linux(self):
        """Stop PostgreSQL on Linux."""
        if self._has_command("systemctl"):
            try:
                subprocess.run(["sudo", "systemctl", "stop", "postgresql"], timeout=10)
                self.logger.info("✅ PostgreSQL stopped")
                return True
            except Exception as e:
                self.logger.error("Failed to stop PostgreSQL: %s", e)
        return False
    
    def _stop_windows(self):
        """Stop PostgreSQL on Windows."""
        try:
            subprocess.run(["net", "stop", "postgresql"], timeout=10)
            self.logger.info("✅ PostgreSQL stopped")
            return True
        except Exception as e:
            self.logger.error("Failed to stop PostgreSQL: %s", e)
        return False
    
    # ═══════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════
    
    def _has_command(self, command):
        """Check if a command is available."""
        try:
            result = subprocess.run(
                ["which", command] if self.os_type != "Windows" else ["where", command],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _find_postgres_data_dir(self):
        """Find PostgreSQL data directory."""
        common_paths = [
            Path("/usr/local/var/postgresql@14"),
            Path("/usr/local/var/postgres"),
            Path("/var/lib/postgresql/data"),
            Path.home() / ".postgres",
        ]
        
        for path in common_paths:
            if path.exists() and (path / "PG_VERSION").exists():
                return path
        
        return None
    
    def _get_install_command(self):
        """Get installation command for current OS."""
        if self.os_type == "Darwin":
            return "brew install postgresql"
        elif self.os_type == "Linux":
            return "sudo apt-get install postgresql  # or: sudo yum install postgresql-server"
        elif self.os_type == "Windows":
            return "Download from: https://www.postgresql.org/download/windows/"
        return "See: https://www.postgresql.org/download/"

