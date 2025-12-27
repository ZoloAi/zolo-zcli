# zSys/bootstrap_logger.py
"""
Bootstrap logger for pre-boot logging (Layer 0).

Buffers log messages before zCLI framework is initialized, then injects
them into zcli-framework.log once the framework logger is available.

Supports --verbose flag for CLI commands to display bootstrap process.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class BootstrapLogger:
    """
    Pre-boot logger that buffers messages until framework logger is ready.
    
    Features:
        - Buffers all pre-boot logs in memory
        - Injects into zcli-framework.log when framework ready
        - Supports --verbose flag for stdout display
        - Emergency dump on init failure
        - Zero zCLI dependencies (pure Python stdlib)
    
    Usage:
        # In main.py (ALWAYS use from first line)
        from zSys import BootstrapLogger
        
        boot_logger = BootstrapLogger()
        boot_logger.info("Starting zolo-zcli...")
        boot_logger.debug("Parsing arguments...")
        
        try:
            cli = zCLI()
            # Inject buffered logs (verbose=True shows on stdout)
            boot_logger.flush_to_framework(
                cli.logger.framework, 
                verbose=args.verbose
            )
        except Exception as e:
            # Emergency dump to stderr + temp file
            boot_logger.emergency_dump(e)
            sys.exit(1)
    """
    
    def __init__(self, name: str = "zCLI.bootstrap"):
        """Initialize bootstrap logger with in-memory buffer."""
        self.name = name
        self.buffer: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
    
    def debug(self, msg: str, *args):
        """Log debug message to buffer."""
        formatted_msg = msg % args if args else msg
        self._buffer_message("DEBUG", formatted_msg)
    
    def info(self, msg: str, *args):
        """Log info message to buffer."""
        formatted_msg = msg % args if args else msg
        self._buffer_message("INFO", formatted_msg)
    
    def warning(self, msg: str, *args):
        """Log warning message to buffer."""
        formatted_msg = msg % args if args else msg
        self._buffer_message("WARNING", formatted_msg)
    
    def error(self, msg: str, *args):
        """Log error message to buffer."""
        formatted_msg = msg % args if args else msg
        self._buffer_message("ERROR", formatted_msg)
    
    def critical(self, msg: str, *args):
        """Log critical message to buffer."""
        formatted_msg = msg % args if args else msg
        self._buffer_message("CRITICAL", formatted_msg)
    
    def _buffer_message(self, level: str, msg: str):
        """Store message in buffer with metadata."""
        self.buffer.append({
            'timestamp': datetime.now(),
            'level': level,
            'message': msg,
            'source': 'bootstrap'
        })
    
    def flush_to_framework(self, framework_logger: logging.Logger, verbose: bool = False):
        """
        Inject buffered messages into framework logger.
        
        Args:
            framework_logger: The zCLI framework logger instance
            verbose: If True, also print to stdout (for --verbose flag)
        """
        if not self.buffer:
            return
        
        # Calculate elapsed time
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        # Write to framework.log
        framework_logger.info("=" * 70)
        framework_logger.info("[Bootstrap] Pre-boot log injection (%d messages, %.3fs)", 
                             len(self.buffer), elapsed)
        framework_logger.info("=" * 70)
        
        # Inject all buffered messages
        for entry in self.buffer:
            level = entry['level'].lower()
            log_method = getattr(framework_logger, level)
            timestamp = entry['timestamp'].strftime("%H:%M:%S.%f")[:-3]
            log_method("[Bootstrap:%s] %s", timestamp, entry['message'])
            
            # If --verbose, also print to stdout
            if verbose:
                self._print_verbose_message(entry)
        
        framework_logger.info("=" * 70)
        framework_logger.info("[Bootstrap] Injection complete (%.3fs total)", elapsed)
        framework_logger.info("=" * 70)
        
        # If verbose, show completion
        if verbose:
            print(f"[Bootstrap] ✓ Initialized in {elapsed:.3f}s\n")
        
        # Clear buffer
        self.buffer.clear()
    
    def print_buffered_logs(self):
        """
        Print buffered logs to stdout (for cases without framework logger).
        
        Used when running commands that don't initialize zCLI (e.g., info banner)
        but still want to show bootstrap process with --verbose flag.
        """
        if not self.buffer:
            return
        
        # Print all buffered messages
        for entry in self.buffer:
            self._print_verbose_message(entry)
        
        # Show completion
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"[Bootstrap] ✓ Initialized in {elapsed:.3f}s\n")
        
        # Clear buffer
        self.buffer.clear()
    
    def _print_verbose_message(self, entry: Dict[str, Any]):
        """Print log entry to stdout in verbose mode."""
        timestamp = entry['timestamp'].strftime("%H:%M:%S")
        level = entry['level']
        message = entry['message']
        
        # Color codes for levels
        colors = {
            'DEBUG': '\033[90m',    # Gray
            'INFO': '\033[36m',     # Cyan
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[91m', # Bright Red
        }
        reset = '\033[0m'
        
        color = colors.get(level, '')
        print(f"{color}[{timestamp}] [Bootstrap] {message}{reset}")
    
    def emergency_dump(self, exception: Optional[Exception] = None):
        """
        Emergency dump to stderr and temp file if framework init fails.
        
        Args:
            exception: The exception that caused init failure (if any)
        """
        print("\n" + "=" * 70, file=sys.stderr)
        print("❌ CRITICAL: zCLI Framework Initialization Failed", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        
        if exception:
            print(f"\nError: {exception}\n", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
        
        print(f"\nPre-boot log buffer ({len(self.buffer)} messages):\n", file=sys.stderr)
        
        # Dump buffered messages
        for entry in self.buffer:
            timestamp = entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            level = entry['level']
            message = entry['message']
            print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)
        
        print("\n" + "=" * 70, file=sys.stderr)
        
        # Save to temp file as fallback
        temp_file = Path.home() / ".zolo-zcli-bootstrap-error.log"
        try:
            with open(temp_file, 'w') as f:
                f.write("=" * 70 + "\n")
                f.write("zCLI Bootstrap Failure Log\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write("=" * 70 + "\n\n")
                
                if exception:
                    f.write(f"Exception: {exception}\n\n")
                    import traceback
                    f.write(traceback.format_exc())
                    f.write("\n")
                
                f.write("Pre-boot Log Buffer:\n")
                f.write("-" * 70 + "\n\n")
                
                for entry in self.buffer:
                    timestamp = entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    level = entry['level']
                    message = entry['message']
                    f.write(f"[{timestamp}] [{level}] {message}\n")
            
            print(f"\n💾 Bootstrap log saved to: {temp_file}", file=sys.stderr)
        except Exception as e:
            print(f"\n⚠️  Failed to save bootstrap log: {e}", file=sys.stderr)

