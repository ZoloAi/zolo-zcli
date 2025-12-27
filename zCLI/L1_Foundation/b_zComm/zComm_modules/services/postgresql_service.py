# zCLI/subsystems/zComm/zComm_modules/services/postgresql_service.py
"""
PostgreSQL Service Manager for zCLI.

Cross-platform PostgreSQL service management supporting macOS (Homebrew, pg_ctl),
Linux (systemd, pg_ctl), and Windows (Windows services). Provides start/stop/status
operations and connection information retrieval.
"""

from zCLI import subprocess, socket, platform, Path, Any, Dict, Optional, List

# ═══════════════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════════════

# Logging
LOG_PREFIX = "[PostgreSQLService]"

# OS Type Identifiers
OS_DARWIN = "Darwin"
OS_LINUX = "Linux"
OS_WINDOWS = "Windows"

# Timeouts (seconds)
SOCKET_TIMEOUT = 1
SUBPROCESS_TIMEOUT = 10
COMMAND_CHECK_TIMEOUT = 5

# Port Configuration
PORT_MIN = 1
PORT_MAX = 65535

# Default Configuration
DEFAULT_PORT = 5432
DEFAULT_USER = "postgres"
DEFAULT_DATABASE = "postgres"
DEFAULT_HOST = "localhost"

# Status Dict Keys
STATUS_KEY_SERVICE = "service"
STATUS_KEY_RUNNING = "running"
STATUS_KEY_PORT = "port"
STATUS_KEY_OS = "os"
STATUS_KEY_CONNECTION_INFO = "connection_info"
STATUS_KEY_MESSAGE = "message"

# Connection Info Keys
CONN_KEY_HOST = "host"
CONN_KEY_PORT = "port"
CONN_KEY_USER = "user"
CONN_KEY_DATABASE = "database"
CONN_KEY_CONNECTION_STRING = "connection_string"

# Service Identifiers
SERVICE_NAME_POSTGRES = "postgresql"
SERVICE_NAME_POSTGRES_14 = "postgresql@14"

# Commands
CMD_BREW = "brew"
CMD_SYSTEMCTL = "systemctl"
CMD_PG_CTL = "pg_ctl"
CMD_WHICH = "which"
CMD_WHERE = "where"
CMD_SUDO = "sudo"
CMD_NET = "net"

# Brew Commands
BREW_SERVICES = "services"
BREW_START = "start"
BREW_STOP = "stop"

# PostgreSQL Data Directory Paths
PG_DATA_PATH_HOMEBREW_14 = "/usr/local/var/postgresql@14"
PG_DATA_PATH_HOMEBREW = "/usr/local/var/postgres"
PG_DATA_PATH_LINUX = "/var/lib/postgresql/data"
PG_DATA_PATH_USER_HOME = ".postgres"
PG_VERSION_FILE = "PG_VERSION"

# Log Messages - Status
LOG_ALREADY_RUNNING = "PostgreSQL is already running on port {port}"
LOG_NOT_RUNNING = "PostgreSQL is not running"
LOG_STARTING = "Starting PostgreSQL service..."
LOG_STOPPING = "Stopping PostgreSQL service..."
LOG_CHECK_PORT_ERROR = "Error checking PostgreSQL port: {error}"

# Log Messages - Success
LOG_SUCCESS_STARTED_BREW = "[OK] PostgreSQL started via Homebrew"
LOG_SUCCESS_STARTED_SYSTEMD = "[OK] PostgreSQL started via systemd"
LOG_SUCCESS_STARTED_PG_CTL = "[OK] PostgreSQL started with pg_ctl"
LOG_SUCCESS_STARTED_WINDOWS = "[OK] PostgreSQL started via Windows service"
LOG_SUCCESS_STOPPED = "[OK] PostgreSQL stopped"

# Error Messages - Start
ERROR_UNSUPPORTED_OS = "Unsupported operating system: {os}"
ERROR_START_BREW = "Failed to start PostgreSQL via brew: {error}"
ERROR_START_SYSTEMD = "Failed to start PostgreSQL via systemd: {error}"
ERROR_START_WINDOWS = "Failed to start PostgreSQL on Windows: {error}"
ERROR_START_PG_CTL = "Failed to start PostgreSQL with pg_ctl: {error}"
ERROR_NO_DATA_DIR = "Could not find PostgreSQL data directory"
ERROR_INSTALL_BREW = "[ERROR] Could not start PostgreSQL. Install with: brew install postgresql"
ERROR_INSTALL_LINUX = "[ERROR] Could not start PostgreSQL"

# Error Messages - Stop
ERROR_STOP_BREW = "Failed to stop PostgreSQL: {error}"
ERROR_STOP_SYSTEMD = "Failed to stop PostgreSQL: {error}"
ERROR_STOP_WINDOWS = "Failed to stop PostgreSQL: {error}"

# Error Messages - Validation
ERROR_INVALID_PORT = "Port must be between {min} and {max}, got: {port}"
ERROR_LOGGER_NONE = "Logger cannot be None"

# Installation Messages
MSG_NOT_DETECTED = "PostgreSQL not detected. Install with: {command}"
INSTALL_CMD_MACOS = "brew install postgresql"
INSTALL_CMD_LINUX = "sudo apt-get install postgresql  # or: sudo yum install postgresql-server"
INSTALL_CMD_WINDOWS = "Download from: https://www.postgresql.org/download/windows/"
INSTALL_CMD_DEFAULT = "See: https://www.postgresql.org/download/"


class PostgreSQLService:
    """
    Cross-platform PostgreSQL service lifecycle manager.
    
    Auto-detects installation method and manages PostgreSQL via Homebrew (macOS),
    systemd/pg_ctl (Linux), or Windows services. Provides start/stop/status operations.
    
    Attributes:
        logger: Logger instance for output
        os_type: Operating system ('Darwin', 'Linux', 'Windows')
    """

    def __init__(self, logger: Any) -> None:
        """
        Initialize PostgreSQL service manager.
        
        Args:
            logger: Logger instance (required)
            
        Raises:
            ValueError: If logger is None
        """
        if logger is None:
            raise ValueError(ERROR_LOGGER_NONE)
            
        self.logger = logger
        self.os_type = platform.system()  # 'Darwin', 'Linux', 'Windows'

    def start(self, **kwargs: Any) -> bool:  # pylint: disable=unused-argument
        """
        Start PostgreSQL service using platform-appropriate method.
        
        Args:
            **kwargs: Reserved for future use (API consistency)
            
        Returns:
            True if started successfully, False otherwise
        """
        # Check if already running
        if self.is_running():
            self.logger.info(f"{LOG_PREFIX} {LOG_ALREADY_RUNNING.format(port=DEFAULT_PORT)}")
            return True

        self.logger.info(f"{LOG_PREFIX} {LOG_STARTING}")

        # Try different start methods based on OS
        if self.os_type == OS_DARWIN:  # macOS
            return self._start_macos()
        elif self.os_type == OS_LINUX:
            return self._start_linux()
        elif self.os_type == OS_WINDOWS:
            return self._start_windows()
        else:
            self.logger.error(f"{LOG_PREFIX} {ERROR_UNSUPPORTED_OS.format(os=self.os_type)}")
            return False

    def stop(self) -> bool:
        """
        Stop PostgreSQL service using platform-appropriate method.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.is_running():
            self.logger.info(f"{LOG_PREFIX} {LOG_NOT_RUNNING}")
            return True

        self.logger.info(f"{LOG_PREFIX} {LOG_STOPPING}")

        if self.os_type == OS_DARWIN:
            return self._stop_macos()
        elif self.os_type == OS_LINUX:
            return self._stop_linux()
        elif self.os_type == OS_WINDOWS:
            return self._stop_windows()

        return False

    def is_running(self, port: Optional[int] = None) -> bool:
        """
        Check if PostgreSQL is running on specified port.
        
        Args:
            port: Port to check (default: 5432, range: 1-65535)
            
        Returns:
            True if running, False otherwise
            
        Raises:
            ValueError: If port outside valid range
        """
        check_port = port if port is not None else DEFAULT_PORT

        # Validate port range
        if not isinstance(check_port, int) or check_port < PORT_MIN or check_port > PORT_MAX:
            raise ValueError(ERROR_INVALID_PORT.format(
                min=PORT_MIN, max=PORT_MAX, port=check_port
            ))

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(SOCKET_TIMEOUT)
            result = sock.connect_ex((DEFAULT_HOST, check_port))
            sock.close()
            return result == 0  # 0 means port is in use (PostgreSQL running)
        except (socket.error, OSError) as e:
            self.logger.debug(f"{LOG_PREFIX} {LOG_CHECK_PORT_ERROR.format(error=e)}")
            return False

    def status(self) -> Dict[str, Any]:
        """
        Get comprehensive PostgreSQL service status.
        
        Returns:
            Dict with 'service', 'running', 'port', 'os', and optionally
            'connection_info' (if running) or 'message' (if not running)
        """
        running = self.is_running()

        status_info = {
            STATUS_KEY_SERVICE: SERVICE_NAME_POSTGRES,
            STATUS_KEY_RUNNING: running,
            STATUS_KEY_PORT: DEFAULT_PORT,
            STATUS_KEY_OS: self.os_type
        }

        if running:
            status_info[STATUS_KEY_CONNECTION_INFO] = self.get_connection_info()
        else:
            install_cmd = self._get_install_command()
            status_info[STATUS_KEY_MESSAGE] = MSG_NOT_DETECTED.format(command=install_cmd)

        return status_info

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get PostgreSQL connection information.
        
        Returns:
            Dict with 'host', 'port', 'user', 'database', 'connection_string'
        """
        return {
            CONN_KEY_HOST: DEFAULT_HOST,
            CONN_KEY_PORT: DEFAULT_PORT,
            CONN_KEY_USER: DEFAULT_USER,
            CONN_KEY_DATABASE: DEFAULT_DATABASE,
            CONN_KEY_CONNECTION_STRING: (
                f"postgresql://{DEFAULT_USER}@{DEFAULT_HOST}:{DEFAULT_PORT}/{DEFAULT_DATABASE}"
            )
        }

    # ═══════════════════════════════════════════════════════════════════
    # Platform-Specific Start Methods
    # ═══════════════════════════════════════════════════════════════════

    def _start_macos(self) -> bool:
        """
        Start PostgreSQL on macOS via Homebrew or pg_ctl.
        
        Returns:
            True if started, False otherwise
        """
        # Try Homebrew first
        if self._has_command(CMD_BREW):
            # Try versioned PostgreSQL first
            if self._run_command(
                [CMD_BREW, BREW_SERVICES, BREW_START, SERVICE_NAME_POSTGRES_14],
                LOG_SUCCESS_STARTED_BREW,
                ERROR_START_BREW
            ):
                return True

            # Try without version
            if self._run_command(
                [CMD_BREW, BREW_SERVICES, BREW_START, SERVICE_NAME_POSTGRES],
                LOG_SUCCESS_STARTED_BREW,
                ERROR_START_BREW
            ):
                return True

        # Try pg_ctl
        if self._has_command(CMD_PG_CTL):
            return self._start_with_pg_ctl()

        self.logger.error(f"{LOG_PREFIX} {ERROR_INSTALL_BREW}")
        return False

    def _start_linux(self) -> bool:
        """
        Start PostgreSQL on Linux via systemd or pg_ctl.
        
        Returns:
            True if started, False otherwise
        """
        # Try systemd
        if self._has_command(CMD_SYSTEMCTL):
            if self._run_command(
                [CMD_SUDO, CMD_SYSTEMCTL, BREW_START, SERVICE_NAME_POSTGRES],
                LOG_SUCCESS_STARTED_SYSTEMD,
                ERROR_START_SYSTEMD
            ):
                return True

        # Try pg_ctl
        if self._has_command(CMD_PG_CTL):
            return self._start_with_pg_ctl()

        self.logger.error(f"{LOG_PREFIX} {ERROR_INSTALL_LINUX}")
        return False

    def _start_windows(self) -> bool:
        """
        Start PostgreSQL on Windows via 'net start' command.
        
        Returns:
            True if started, False otherwise
        """
        return self._run_command(
            [CMD_NET, BREW_START, SERVICE_NAME_POSTGRES],
            LOG_SUCCESS_STARTED_WINDOWS,
            ERROR_START_WINDOWS
        )

    def _start_with_pg_ctl(self) -> bool:
        """
        Start PostgreSQL using pg_ctl with auto-detected data directory.
        
        Returns:
            True if started, False otherwise
        """
        # Find data directory
        data_dir = self._find_postgres_data_dir()
        if not data_dir:
            self.logger.error(f"{LOG_PREFIX} {ERROR_NO_DATA_DIR}")
            return False

        return self._run_command(
            [CMD_PG_CTL, "-D", str(data_dir), BREW_START],
            LOG_SUCCESS_STARTED_PG_CTL,
            ERROR_START_PG_CTL
        )

    # ═══════════════════════════════════════════════════════════════════
    # Platform-Specific Stop Methods
    # ═══════════════════════════════════════════════════════════════════

    def _stop_macos(self) -> bool:
        """
        Stop PostgreSQL on macOS via Homebrew.
        
        Returns:
            True if stopped, False otherwise
        """
        if self._has_command(CMD_BREW):
            return self._run_command(
                [CMD_BREW, BREW_SERVICES, BREW_STOP, SERVICE_NAME_POSTGRES],
                LOG_SUCCESS_STOPPED,
                ERROR_STOP_BREW,
                log_on_error=True
            )
        return False

    def _stop_linux(self) -> bool:
        """
        Stop PostgreSQL on Linux via systemd.
        
        Returns:
            True if stopped, False otherwise
        """
        if self._has_command(CMD_SYSTEMCTL):
            return self._run_command(
                [CMD_SUDO, CMD_SYSTEMCTL, BREW_STOP, SERVICE_NAME_POSTGRES],
                LOG_SUCCESS_STOPPED,
                ERROR_STOP_SYSTEMD,
                log_on_error=True
            )
        return False

    def _stop_windows(self) -> bool:
        """
        Stop PostgreSQL on Windows via 'net stop' command.
        
        Returns:
            True if stopped, False otherwise
        """
        return self._run_command(
            [CMD_NET, BREW_STOP, SERVICE_NAME_POSTGRES],
            LOG_SUCCESS_STOPPED,
            ERROR_STOP_WINDOWS,
            log_on_error=True
        )

    # ═══════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════

    def _run_command(
        self,
        cmd: List[str],
        success_msg: str,
        error_msg_template: str,
        timeout: int = SUBPROCESS_TIMEOUT,
        log_on_error: bool = False
    ) -> bool:
        """
        Run subprocess command with consistent error handling (DRY helper).
        
        Args:
            cmd: Command and arguments
            success_msg: Success log message
            error_msg_template: Error template (supports {error} placeholder)
            timeout: Timeout in seconds
            log_on_error: Whether to log errors
            
        Returns:
            True if returncode == 0, False otherwise
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            if result.returncode == 0:
                self.logger.info(f"{LOG_PREFIX} {success_msg}")
                return True
            return False
        except subprocess.TimeoutExpired:
            if log_on_error:
                error_msg = error_msg_template.format(error=f"Timeout after {timeout}s")
                self.logger.error(f"{LOG_PREFIX} {error_msg}")
            return False
        except (subprocess.SubprocessError, OSError) as e:
            if log_on_error:
                error_msg = error_msg_template.format(error=str(e))
                self.logger.error(f"{LOG_PREFIX} {error_msg}")
            return False

    def _has_command(self, command: str) -> bool:
        """
        Check if command is available on system (uses 'which'/'where').
        
        Args:
            command: Command name
            
        Returns:
            True if available, False otherwise
        """
        try:
            check_cmd = CMD_WHERE if self.os_type == OS_WINDOWS else CMD_WHICH
            result = subprocess.run(
                [check_cmd, command],
                capture_output=True,
                timeout=COMMAND_CHECK_TIMEOUT,
                check=False
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, OSError):
            return False

    def _find_postgres_data_dir(self) -> Optional[Path]:
        """
        Find PostgreSQL data directory in common platform-specific locations.
        
        Returns:
            Path if found, None otherwise
        """
        common_paths = [
            Path(PG_DATA_PATH_HOMEBREW_14),
            Path(PG_DATA_PATH_HOMEBREW),
            Path(PG_DATA_PATH_LINUX),
            Path.home() / PG_DATA_PATH_USER_HOME,
        ]

        for path in common_paths:
            try:
                if path.exists() and (path / PG_VERSION_FILE).exists():
                    return path
            except (OSError, PermissionError):
                continue

        return None

    def _get_install_command(self) -> str:
        """
        Get platform-specific PostgreSQL installation command.
        
        Returns:
            Installation command or URL
        """
        if self.os_type == OS_DARWIN:
            return INSTALL_CMD_MACOS
        elif self.os_type == OS_LINUX:
            return INSTALL_CMD_LINUX
        elif self.os_type == OS_WINDOWS:
            return INSTALL_CMD_WINDOWS
        return INSTALL_CMD_DEFAULT
