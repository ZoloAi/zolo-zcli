"""
Comm command execution for zCLI.
Service and communication management commands.
"""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def execute_comm(zcli, parsed):
    """
    Execute comm commands like 'comm start postgresql', 'comm status'.
    
    Args:
        zcli: zCLI instance
        parsed: Parsed command dictionary
        
    Returns:
        Command execution result
    """
    action = parsed["action"]
    args = parsed.get("args", [])
    options = parsed.get("options", {})
    
    # Initialize zComm if not already
    if not hasattr(zcli, 'comm') or zcli.comm is None:
        from zCLI.subsystems.zComm import ZComm
        zcli.comm = ZComm(zcli)
    
    # Handle different comm actions
    if action == "status":
        # Show status of all services or specific service
        service_name = args[0] if args else None
        status = zcli.comm.service_status(service_name)
        
        if service_name:
            # Single service status
            _display_service_status(service_name, status)
        else:
            # All services status
            print("\n═══════════════════════════════════════════")
            print("           zComm Service Status")
            print("═══════════════════════════════════════════\n")
            
            for name, info in status.items():
                _display_service_status(name, info)
                print()  # Blank line between services
        
        return {"status": "success", "data": status}
    
    elif action == "start":
        # Start a service
        if not args:
            return {"error": "Service name required. Usage: comm start <service>"}
        
        service_name = args[0]
        logger.info("Starting service: %s", service_name)
        
        success = zcli.comm.start_service(service_name, **options)
        
        if success:
            print(f"✅ {service_name} started successfully")
            
            # Show connection info
            conn_info = zcli.comm.get_service_connection_info(service_name)
            if conn_info:
                print("\nConnection Info:")
                for key, value in conn_info.items():
                    print(f"  {key}: {value}")
            
            return {"status": "success", "service": service_name}
        else:
            print(f"❌ Failed to start {service_name}")
            return {"error": f"Failed to start {service_name}"}
    
    elif action == "stop":
        # Stop a service
        if not args:
            return {"error": "Service name required. Usage: comm stop <service>"}
        
        service_name = args[0]
        logger.info("Stopping service: %s", service_name)
        
        success = zcli.comm.stop_service(service_name)
        
        if success:
            print(f"✅ {service_name} stopped successfully")
            return {"status": "success", "service": service_name}
        else:
            print(f"❌ Failed to stop {service_name}")
            return {"error": f"Failed to stop {service_name}"}
    
    elif action == "restart":
        # Restart a service
        if not args:
            return {"error": "Service name required. Usage: comm restart <service>"}
        
        service_name = args[0]
        logger.info("Restarting service: %s", service_name)
        
        success = zcli.comm.restart_service(service_name)
        
        if success:
            print(f"✅ {service_name} restarted successfully")
            return {"status": "success", "service": service_name}
        else:
            print(f"❌ Failed to restart {service_name}")
            return {"error": f"Failed to restart {service_name}"}
    
    elif action == "info":
        # Get connection info for a service
        if not args:
            return {"error": "Service name required. Usage: comm info <service>"}
        
        service_name = args[0]
        conn_info = zcli.comm.get_service_connection_info(service_name)
        
        if conn_info:
            print(f"\n{service_name.upper()} Connection Information:")
            print("─" * 40)
            for key, value in conn_info.items():
                print(f"  {key:20}: {value}")
            return {"status": "success", "data": conn_info}
        else:
            print(f"❌ No connection info available for {service_name}")
            return {"error": "Service not found or not running"}
    
    elif action == "install":
        # Help user install a service
        if not args:
            return {"error": "Service name required. Usage: comm install <service>"}
        
        service_name = args[0]
        return _install_service_helper(service_name, options)
    
    else:
        return {"error": f"Unknown comm action: {action}"}


def _display_service_status(service_name, status_info):
    """Display service status in a formatted way."""
    if isinstance(status_info, dict) and "error" in status_info:
        print(f"❌ {service_name}: {status_info['error']}")
        return
    
    running = status_info.get("running", False)
    status_icon = "🟢" if running else "🔴"
    status_text = "Running" if running else "Stopped"
    
    print(f"{status_icon} {service_name.upper()}: {status_text}")
    
    if "port" in status_info:
        print(f"   Port: {status_info['port']}")
    
    if "message" in status_info:
        print(f"   Note: {status_info['message']}")
    
    if running and "connection_info" in status_info:
        conn = status_info["connection_info"]
        if "connection_string" in conn:
            print(f"   URL: {conn['connection_string']}")


def _install_service_helper(service_name, options):
    """
    Guide user through service installation.
    
    Provides OS-specific installation instructions and optionally
    executes the installation command.
    """
    import platform
    import subprocess
    
    os_type = platform.system()
    auto_install = options.get("auto", False) or options.get("y", False)
    
    if service_name == "postgresql":
        print("\n" + "═" * 60)
        print("         PostgreSQL Installation Helper")
        print("═" * 60)
        
        # Provide OS-specific instructions
        if os_type == "Darwin":  # macOS
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
                        timeout=300  # 5 minutes
                    )
                    if result.returncode == 0:
                        print("✅ PostgreSQL installed successfully!")
                        print("\nStarting PostgreSQL...")
                        subprocess.run(["brew", "services", "start", "postgresql@14"])
                        print("✅ PostgreSQL started!")
                        return {"status": "success", "message": "PostgreSQL installed and started"}
                    else:
                        print(f"❌ Installation failed: {result.stderr}")
                        return {"error": "Installation failed"}
                except subprocess.TimeoutExpired:
                    print("❌ Installation timed out")
                    return {"error": "Installation timed out"}
                except Exception as e:
                    print(f"❌ Installation error: {e}")
                    return {"error": str(e)}
            else:
                print("\n💡 To install automatically, run:")
                print("   comm install postgresql --auto")
        
        elif os_type == "Linux":
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
        
        elif os_type == "Windows":
            print("\n📦 Installation for Windows:")
            print("   1. Download installer from:")
            print("      https://www.postgresql.org/download/windows/")
            print("   2. Run the installer (EDB PostgreSQL)")
            print("   3. Follow the installation wizard")
            print("\n🚀 PostgreSQL will start automatically as a Windows service")
        
        print("\n" + "─" * 60)
        print("📚 Python Driver (psycopg2):")
        print("   The Python library for PostgreSQL is installed with:")
        print("   pip install zolo-zcli[postgresql]")
        print("\n💡 Or to install all backend support:")
        print("   pip install zolo-zcli[all]")
        print("═" * 60 + "\n")
        
        return {"status": "success", "message": "Installation instructions provided"}
    
    else:
        print(f"❌ Unknown service: {service_name}")
        print("   Available services: postgresql")
        return {"error": f"Unknown service: {service_name}"}

