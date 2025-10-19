# zCLI/subsystems/zShell/zShell_modules/zShell_help.py

# zCLI/subsystems/zShell_modules/zShell_help.py — Help System
# ───────────────────────────────────────────────────────────────
"""Help system for zCLI shell - centralized command documentation."""

class HelpSystem:
    """Help system for zCLI - provides documentation and usage examples."""

    def __init__(self, display=None):
        """Initialize help system with display instance."""
        self.display = display

    # Centralized command definitions
    COMMANDS = {
        "data": {
            "desc": "Data operations (CRUD)",
            "usage": [
                "data read <table> [--model PATH] [--limit N] [--where CLAUSE]",
                "data insert <table> [--model PATH] [--fields ...] [--values ...]",
                "data update <table> [--model PATH] [--fields ...] [--values ...] [--where CLAUSE]",
                "data delete <table> [--model PATH] [--where CLAUSE]",
                "data upsert <table> [--model PATH] [--fields ...] [--values ...]",
                "data create <table> [--model PATH]",
                "data drop <table> [--model PATH]",
                "data head <table> [--model PATH]",
            ],
            "examples": [
                "data read users --model @.zCLI.Schemas.zSchema.sqlite_demo",
                "data read users --model $sqlite_demo",
                "data read users,posts --model $sqlite_demo --auto-join",
                "data insert users --model $sqlite_demo --fields name,email --values 'Alice','alice@example.com'",
                "data read users --where 'age > 25' --limit 10",
            ]
        },
        "load": {
            "desc": "Load and cache resources (schemas, UI files)",
            "usage": [
                "load <zPath> [--as ALIAS]",
                "load --show",
                "load --clear [ALIAS]",
            ],
            "examples": [
                "load @.zCLI.Schemas.zSchema.sqlite_demo --as sqlite_demo",
                "load @.zCLI.Schemas.zSchema.csv_demo --as csv_demo",
                "load --show",
                "load --clear sqlite_demo",
            ]
        },
        "wizard": {
            "desc": "Multi-step workflow orchestration",
            "usage": [
                "wizard --start",
                "wizard --stop",
                "wizard --run",
                "wizard --show",
                "wizard --clear",
            ],
            "examples": [
                "wizard --start",
                "  # Enter YAML or commands, then:",
                "wizard --run",
            ]
        },
        "func": {
            "desc": "Execute utility functions",
            "usage": [
                "func <function_name> [args...]",
                "func generate_id <prefix>",
                "func generate_API <prefix>",
            ],
            "examples": [
                "func generate_id zU",
                "func generate_API zApp",
            ]
        },
        "utils": {
            "desc": "Utility operations",
            "usage": [
                "utils <util_name> [args...]",
                "utils hash_password <password>",
            ],
            "examples": [
                "utils hash_password mypassword",
            ]
        },
        "session": {
            "desc": "Session management",
            "usage": [
                "session info",
                "session set <key> <value>",
                "session get <key>",
            ],
            "examples": [
                "session info",
                "session set zWorkspace /path/to/project",
            ]
        },
        "auth": {
            "desc": "Authentication",
            "usage": [
                "auth login",
                "auth logout",
                "auth status",
            ],
            "examples": [
                "auth login",
                "auth status",
            ]
        },
        "walker": {
            "desc": "Launch UI mode from shell",
            "usage": [
                "walker run",
            ],
            "examples": [
                "session set zWorkspace /path/to/project",
                "session set zVaFilename ui.main.yaml",
                "walker run",
            ]
        },
        "open": {
            "desc": "Open files or URLs",
            "usage": [
                "open <path_or_url>",
            ],
            "examples": [
                "open @.index.html",
                "open https://example.com",
            ]
        },
        "config": {
            "desc": "Configuration management",
            "usage": [
                "config show",
                "config get <key>",
                "config set <key> <value>",
            ],
            "examples": [
                "config show",
                "config get zWorkspace",
            ]
        },
        "export": {
            "desc": "Export data",
            "usage": [
                "export <table> [--format FORMAT] [--output PATH]",
            ],
            "examples": [
                "export users --format csv --output users.csv",
            ]
        },
        "test": {
            "desc": "Run test suites",
            "usage": [
                "test run",
                "test session",
            ],
            "examples": [
                "test run",
                "test session",
            ]
        },
        "comm": {
            "desc": "Communication/socket operations",
            "usage": [
                "comm <operation> [args...]",
            ],
            "examples": [
                "comm status",
            ]
        },
    }

    def show_help(self):
        """Display comprehensive help information."""
        if self.display:
            self.display.header("zCLI Interactive Shell", style="box")
            self.display.break_line()
            self.display.text("Available Commands:", color="HEADER")

            # Generate command list
            for cmd, info in HelpSystem.COMMANDS.items():
                self.display.text(f"  {cmd:12} - {info['desc']}", indent=1)

            self.display.break_line()
            self.display.text("General:", color="HEADER")
            self.display.text("  help [command]  - Show help (or help for specific command)", indent=1)
            self.display.text("  tips            - Show quick tips", indent=1)
            self.display.text("  clear/cls       - Clear screen", indent=1)
            self.display.text("  exit/quit/q     - Exit shell", indent=1)

            self.display.break_line()
            self.display.text("Usage:", color="HEADER")
            self.display.text("  • Type 'help <command>' for detailed help on a specific command", indent=1)
            self.display.text("  • Use Tab for command history (↑/↓ arrows)", indent=1)
            self.display.text("  • Press Ctrl+C to interrupt operations", indent=1)

            self.display.break_line()
            self.display.text("Examples:", color="HEADER")
            self.display.text("  help data       - Show detailed data command help", indent=1)
            self.display.text("  help load       - Show detailed load command help", indent=1)
            self.display.text("  help wizard     - Show detailed wizard command help", indent=1)
        else:
            # Fallback if no display available
            print("Help system requires display instance")

    def show_command_help(self, command_type):
        """Show help for a specific command type."""
        if command_type not in HelpSystem.COMMANDS:
            if self.display:
                self.display.warning(f"No help available for: {command_type}")
                self.display.info("Use 'help' for list of all commands")
            else:
                print(f"No help available for: {command_type}")
                print("Use 'help' for list of all commands")
            return

        cmd_info = HelpSystem.COMMANDS[command_type]

        if self.display:
            self.display.header(f"{command_type.upper()} Command Help", style="box")
            self.display.break_line()
            self.display.text("Description:", color="HEADER")
            self.display.text(f"  {cmd_info['desc']}", indent=1)

            self.display.break_line()
            self.display.text("Usage:", color="HEADER")
            for usage in cmd_info['usage']:
                self.display.text(f"  {usage}", indent=1)

            self.display.break_line()
            self.display.text("Examples:", color="HEADER")
            for example in cmd_info['examples']:
                self.display.text(f"  {example}", indent=1)
        else:
            # Fallback
            print(f"Help for {command_type} requires display instance")

    @staticmethod
    def get_welcome_message():
        """Return welcome message for shell startup."""
        return """
╔═══════════════════════════════════════════════════════════╗
║                    zCLI Interactive Shell                 ║
╚═══════════════════════════════════════════════════════════╝

Type 'help' for available commands
Type 'exit' or 'quit' to leave

"""

    @staticmethod
    def get_quick_tips():
        """Return quick tips for shell usage."""
        return """
Quick Tips:
  • Press Ctrl+C to interrupt long operations
  • Use 'session info' to check your current context
  • Commands are case-sensitive
  • Use Tab for... (coming soon: autocomplete)
"""
