# zCLI/subsystems/zShell/zShell_modules/executor_commands/comm_executor.py

"""Communication and service management command executor."""


def execute_comm(zcli, parsed):
    """Execute comm commands (start, stop, status, info, install)."""
    action = parsed["action"]
    args = parsed.get("args", [])
    options = parsed.get("options", {})

    if not hasattr(zcli, 'comm') or zcli.comm is None:
        from zCLI.subsystems.zComm import ZComm
        zcli.comm = ZComm(zcli)

    action_map = {
        "status": _handle_status,
        "start": _handle_start,
        "stop": _handle_stop,
        "restart": _handle_restart,
        "info": _handle_info,
        "install": _handle_install,
    }

    handler = action_map.get(action)
    if handler:
        return handler(zcli, args, options)

    return {"error": f"Unknown comm action: {action}"}

def _handle_status(zcli, args, options):  # pylint: disable=unused-argument
    """Handle status command."""
    service_name = args[0] if args else None
    status = zcli.comm.service_status(service_name)

    if service_name:
        _display_service_status(zcli, service_name, status)
    else:
        zcli.display.zDeclare("zComm Service Status", color="INFO", indent=0, style="full")

        for name, info in status.items():
            _display_service_status(zcli, name, info)

    return {"status": "success", "data": status}

def _handle_start(zcli, args, options):
    """Handle start command."""
    if not args:
        return {"error": "Service name required. Usage: comm start <service>"}

    service_name = args[0]
    zcli.logger.info("Starting service: %s", service_name)

    success = zcli.comm.start_service(service_name, **options)

    if success:
        zcli.display.success(f"{service_name} started successfully")

        conn_info = zcli.comm.get_service_connection_info(service_name)
        if conn_info:
            zcli.display.info("Connection Info:", indent=1)
            for key, value in conn_info.items():
                zcli.display.text(f"{key}: {value}", indent=2)

        return {"status": "success", "service": service_name}

    zcli.display.error(f"Failed to start {service_name}")
    return {"error": f"Failed to start {service_name}"}


def _handle_stop(zcli, args, options):  # pylint: disable=unused-argument
    """Handle stop command."""
    if not args:
        return {"error": "Service name required. Usage: comm stop <service>"}

    service_name = args[0]
    zcli.logger.info("Stopping service: %s", service_name)

    success = zcli.comm.stop_service(service_name)

    if success:
        zcli.display.success(f"{service_name} stopped successfully")
        return {"status": "success", "service": service_name}

    zcli.display.error(f"Failed to stop {service_name}")
    return {"error": f"Failed to stop {service_name}"}

def _handle_restart(zcli, args, options):  # pylint: disable=unused-argument
    """Handle restart command."""
    if not args:
        return {"error": "Service name required. Usage: comm restart <service>"}

    service_name = args[0]
    zcli.logger.info("Restarting service: %s", service_name)

    success = zcli.comm.restart_service(service_name)

    if success:
        zcli.display.success(f"{service_name} restarted successfully")
        return {"status": "success", "service": service_name}

    zcli.display.error(f"Failed to restart {service_name}")
    return {"error": f"Failed to restart {service_name}"}

def _handle_info(zcli, args, options):  # pylint: disable=unused-argument
    """Handle info command."""
    if not args:
        return {"error": "Service name required. Usage: comm info <service>"}

    service_name = args[0]
    conn_info = zcli.comm.get_service_connection_info(service_name)

    if conn_info:
        zcli.display.zDeclare(f"{service_name.upper()} Connection Information:", color="INFO", indent=0, style="full")
        for key, value in conn_info.items():
            zcli.display.text(f"{key:20}: {value}", indent=1)
        return {"status": "success", "data": conn_info}

    zcli.display.error(f"No connection info available for {service_name}")
    return {"error": "Service not found or not running"}

def _handle_install(zcli, args, options):
    """Handle install command."""
    if not args:
        return {"error": "Service name required. Usage: comm install <service>"}

    service_name = args[0]
    return _install_service_helper(zcli, service_name, options)

def _display_service_status(zcli, service_name, status_info):
    """Display service status using zDisplay."""
    if isinstance(status_info, dict) and "error" in status_info:
        zcli.display.text(f"{service_name}: {status_info['error']}", indent=1)
        return

    running = status_info.get("running", False)
    status_text = "Running" if running else "Stopped"

    zcli.display.text(f"{service_name.upper()}: {status_text}", indent=1)

    if "port" in status_info:
        zcli.display.text(f"Port: {status_info['port']}", indent=2)

    if "message" in status_info:
        zcli.display.text(f"Note: {status_info['message']}", indent=2)

    if running and "connection_info" in status_info:
        conn = status_info["connection_info"]
        if "connection_string" in conn:
            zcli.display.text(f"URL: {conn['connection_string']}", indent=2)

def _install_service_helper(zcli, service_name, options):  # pylint: disable=unused-argument
    """Guide user through service installation with OS-specific instructions."""
    if service_name == "postgresql":
        return _install_postgresql(options)

    print(f"❌ Unknown service: {service_name}")
    print("   Available services: postgresql")
    return {"error": f"Unknown service: {service_name}"}

def _install_postgresql(options):
    """Install PostgreSQL with OS-specific instructions."""
    # TODO: Replace print() with zDisplay once it supports raw text output
    # Currently zDisplay only supports sysmsg events, not multi-line formatted text
    from zCLI import platform
    
    os_type = platform.system()
    auto_install = options.get("auto", False) or options.get("y", False)
    
    print("\n" + "═" * 60)
    print("         PostgreSQL Installation Helper")
    print("═" * 60)
    
    if os_type == "Darwin":
        return _install_postgresql_macos(auto_install)
    if os_type == "Linux":
        return _install_postgresql_linux(auto_install)
    if os_type == "Windows":
        return _install_postgresql_windows()
    
    _print_postgresql_driver_info()
    return {"status": "success", "message": "Installation instructions provided"}


def _install_postgresql_macos(auto_install):
    """Install PostgreSQL on macOS."""
    import subprocess
    
    print("\n📦 Installation command for macOS (Homebrew):")
    print("   brew install postgresql@14")
    print("\n🚀 To start PostgreSQL after installation:")
    print("   brew services start postgresql@14")
    print("   OR")
    print("   comm start postgresql")
    
    if auto_install:
        print("\n⚙️  Installing PostgreSQL...")
        try:
            result = subprocess.run(
                ["brew", "install", "postgresql@14"],
                capture_output=True,
                text=True,
                timeout=300,
                check=False
            )
            if result.returncode == 0:
                print("✅ PostgreSQL installed successfully!")
                print("\nStarting PostgreSQL...")
                subprocess.run(["brew", "services", "start", "postgresql@14"], check=False)
                print("✅ PostgreSQL started!")
                _print_postgresql_driver_info()
                return {"status": "success", "message": "PostgreSQL installed and started"}
            
            print(f"❌ Installation failed: {result.stderr}")
            return {"error": "Installation failed"}
        except subprocess.TimeoutExpired:
            print("❌ Installation timed out")
            return {"error": "Installation timed out"}
        except Exception as e:
            print(f"❌ Installation error: {e}")
            return {"error": str(e)}
    
    print("\n💡 To install automatically, run:")
    print("   comm install postgresql --auto")
    _print_postgresql_driver_info()
    return {"status": "success", "message": "Installation instructions provided"}


def _install_postgresql_linux(auto_install):
    """Install PostgreSQL on Linux."""
    print("\n📦 Installation commands for Linux:")
    print("\n   Ubuntu/Debian:")
    print("      sudo apt update")
    print("      sudo apt install postgresql postgresql-contrib")
    print("\n   RHEL/CentOS/Fedora:")
    print("      sudo yum install postgresql-server postgresql-contrib")
    print("      sudo postgresql-setup --initdb")
    print("\n🚀 To start PostgreSQL after installation:")
    print("   sudo systemctl start postgresql")
    print("   sudo systemctl enable postgresql")
    print("   OR")
    print("   comm start postgresql")
    
    if auto_install:
        print("\n⚠️  Auto-installation on Linux requires sudo permissions.")
        print("Please run the commands above manually.")
    
    _print_postgresql_driver_info()
    return {"status": "success", "message": "Installation instructions provided"}


def _install_postgresql_windows():
    """Install PostgreSQL on Windows."""
    print("\n📦 Installation for Windows:")
    print("   1. Download installer from:")
    print("      https://www.postgresql.org/download/windows/")
    print("   2. Run the installer (EDB PostgreSQL)")
    print("   3. Follow the installation wizard")
    print("\n🚀 PostgreSQL will start automatically as a Windows service")
    
    _print_postgresql_driver_info()
    return {"status": "success", "message": "Installation instructions provided"}


def _print_postgresql_driver_info():
    """Print PostgreSQL Python driver installation info."""
    print("\n" + "─" * 60)
    print("📚 Python Driver (psycopg2):")
    print("   The Python library for PostgreSQL is installed with:")
    print("   pip install zolo-zcli[postgresql]")
    print("\n💡 Or to install all backend support:")
    print("   pip install zolo-zcli[all]")
    print("═" * 60 + "\n")

