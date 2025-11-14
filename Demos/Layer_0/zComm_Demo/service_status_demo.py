#!/usr/bin/env python3
"""
zComm Demonstration: Service Status Checking

Scenario:
    A Python application needs to check if local development services
    (PostgreSQL, Redis, etc.) are running before connecting to them.
    zComm provides service status checking without manual port probing
    or OS-specific commands.

What this demo shows:
    - Check if PostgreSQL is running
    - Get connection info if available
    - Demonstrates service detection without needing external tools

Note:
    This demo only CHECKS service status—it doesn't start/stop services.
    You don't need PostgreSQL installed; the demo will simply report
    that it's not running (which is fine for demonstration purposes).

Run:
    python Demos/Layer_0/zComm_Demo/service_status_demo.py
"""

from pathlib import Path
from types import SimpleNamespace

from zCLI.subsystems.zConfig import zConfig
from zCLI.subsystems.zComm import zComm


class DemoZCLI(SimpleNamespace):
    """Minimal placeholder that loads only zConfig + zComm."""

    def __init__(self) -> None:
        super().__init__()
        self.session = {"zVars": {}}
        self.logger = None
        self.zspark_obj = {
            "zSpace": str(Path(__file__).parent),
            "env_file": str(Path(__file__).parent / ".zEnv")
        }
        self.config = zConfig(self, zSpark_obj=self.zspark_obj)
        self.comm = zComm(self)

    def run(self) -> None:
        print("=== zComm Service Status Demo ===\n")
        print("Checking local development services...")
        print("(No services will be started—read-only status check)\n")

        # Check PostgreSQL status
        service_name = "postgresql"
        print(f"[{service_name.upper()}]")
        
        status = self.comm.service_status(service_name)
        
        if status.get("running"):
            print(f"  Status: ✓ Running")
            
            # Get connection info
            conn_info = self.comm.get_service_connection_info(service_name)
            if conn_info:
                print(f"  Host: {conn_info.get('host', 'unknown')}")
                print(f"  Port: {conn_info.get('port', 'unknown')}")
                print(f"  Connection: Ready")
                print(f"\n  You can connect using:")
                print(f"    psql -h {conn_info.get('host')} -p {conn_info.get('port')}")
        else:
            print(f"  Status: ✗ Not running")
            if status.get("error"):
                print(f"  Reason: {status['error']}")
            print(f"\n  To use PostgreSQL with zCLI:")
            print(f"    1. Install: brew install postgresql (macOS)")
            print(f"    2. Start: brew services start postgresql")
            print(f"    3. Or use: z.comm.start_service('postgresql')")
        
        print("\n" + "="*50)
        print("Demo complete!")
        print("\nThis demo showed:")
        print("  • Service status checking (no manual port probing)")
        print("  • Connection info retrieval (no config files)")
        print("  • Cross-platform detection (macOS/Linux/Windows)")


def main() -> None:
    demo = DemoZCLI()
    demo.run()


if __name__ == "__main__":
    main()

