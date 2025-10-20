import os, sys
from dotenv import load_dotenv

load_dotenv()

try:
    from zCLI import zCLI  # type: ignore
except Exception:
    print("zCLI is required. Please install `zolo-zcli`.", file=sys.stderr)
    sys.exit(1)

def main():
    print("Starting User Management System...")
    print("Loading interface...\n")

    # Configure zCLI with UI file
    z = zCLI({
        "zWorkspace": os.getcwd(),
        "zVaFile": "@.zUI.users_menu",
        "zBlock": "zVaF"
    })

    # Load and run the UI menu
    # The zUI will handle schema loading automatically via zData operations
    try:
        z.walker.run()
    except Exception as e:
        print(f"Failed to load UI menu: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

