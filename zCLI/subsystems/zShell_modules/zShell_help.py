# zCLI/zCore/Help.py — Help System
# ───────────────────────────────────────────────────────────────

class HelpSystem:
    """Help system for zCLI - provides documentation and usage examples."""
    
    @staticmethod
    def show_help():
        """Display comprehensive help information."""
        help_text = """
═══════════════════════════════════════════════════════════════
                    zCLI Shell Commands
═══════════════════════════════════════════════════════════════

CRUD Operations:
  crud read <table> [options]     - Read data from table
  crud create <table> [options]   - Create new record
  crud update <table> [options]   - Update existing record
  crud delete <table> [options]   - Delete record
  crud search <table> [options]   - Search in table
  
  Options:
    --limit N                     - Limit results to N records
    --model PATH                  - Specify schema model path

  Examples:
    crud read zUsers
    crud read zUsers --limit 10
    crud create zUsers --model @.zCloud.schemas.schema.zIndex.zUsers

───────────────────────────────────────────────────────────────

Resource Loading:
  load <zPath>                    - Load and pin resource to cache
  load --show                     - Show loaded resources
  load --clear [pattern]          - Clear loaded resources
  
  Examples:
    load @.schemas.schema
    load @.ui.admin
    load --show
    load --clear schema:*

───────────────────────────────────────────────────────────────

Functions:
  func <function_name> [args]     - Execute function
  func generate_id <prefix>       - Generate ID with prefix
  func generate_API <prefix>      - Generate API key
  
  Examples:
    func generate_id zU
    func generate_API zApp

───────────────────────────────────────────────────────────────

Utilities:
  utils <util_name> [args]        - Execute utility function
  utils hash_password <password>  - Hash password
  
  Examples:
    utils hash_password mypassword

───────────────────────────────────────────────────────────────

Authentication:
  auth login                      - Login with Zolo credentials
  auth logout                     - Logout and clear credentials
  auth status                     - Show authentication status
  
  Examples:
    auth login
    auth status
    auth logout

───────────────────────────────────────────────────────────────

Session Management:
  session info                    - Show session information
  session set <key> <value>       - Set session value
  session get <key>               - Get session value
  
  Examples:
    session info
    session set zWorkspace /path/to/project
    session set zVaFilename ui.main.yaml
    session set zVaFile_path @
    session set zBlock Root

───────────────────────────────────────────────────────────────

File & URL Operations:
  open <path>                     - Open HTML file or URL
  
  Examples:
    open @.zProducts.zTimer.index.html
    open https://example.com

───────────────────────────────────────────────────────────────

Walker (UI Mode):
  walker run                      - Launch Walker from session config
  
  Required session fields:
    - zWorkspace                  - Project workspace path
    - zVaFilename                 - UI YAML filename
    - zVaFile_path                - UI file path (default: @)
    - zBlock                      - Starting block (default: Root)
  
  Examples:
    # Configure session first
    session set zWorkspace /path/to/project
    session set zVaFilename ui.main.yaml
    session set zVaFile_path @
    session set zBlock Root
    
    # Then launch Walker
    walker run

───────────────────────────────────────────────────────────────

Testing:
  test run                       - Run all test suites (Core + CRUD + RGB)
  test session                   - Quick session isolation test
  
  Examples:
    test run
    test session

───────────────────────────────────────────────────────────────

General:
  help                           - Show this help
  exit                           - Exit shell
  quit                           - Exit shell

═══════════════════════════════════════════════════════════════
        """
        print(help_text)
    
    @staticmethod
    def show_command_help(command_type):
        """Show help for a specific command type."""
        help_sections = {
            "crud": """
CRUD Operations Help:
  
  crud read <table> [--limit N] [--model PATH]
    Read records from a table
    
  crud create <table> [--model PATH]
    Create a new record (will prompt for fields)
    
  crud update <table> [--model PATH]
    Update an existing record
    
  crud delete <table> [--model PATH]
    Delete a record
    
  crud search <table> [--model PATH]
    Search for records
""",
            "func": """
Function Operations Help:

  func <function_name> [args...]
    Execute a function with optional arguments
    
  Common functions:
    - generate_id <prefix>    Generate unique ID
    - generate_API <prefix>   Generate API key
""",
            "session": """
Session Management Help:

  session info
    Display current session information
    
  session set <key> <value>
    Set a session variable
    
  session get <key>
    Get a session variable value
""",
            "walker": """
Walker Mode Help:

  walker run
    Launch Walker UI mode using session configuration
    
  Required session fields:
    - zWorkspace      Project workspace path
    - zVaFilename     UI YAML filename (e.g., ui.main.yaml)
    - zVaFile_path    UI file path (default: @)
    - zBlock          Starting block (default: Root)
  
  Example workflow:
    1. session set zWorkspace /path/to/project
    2. session set zVaFilename ui.main.yaml
    3. session set zVaFile_path @
    4. session set zBlock Root
    5. walker run
  
  The Walker will use your current session (same zS_id, zAuth, etc.)
  Type 'exit' in Walker to return to Shell mode.
""",
            "test": """
Testing Help:

  test run
    Run the core zCLI test suite (79 tests)
    Tests: Session isolation, subsystem integration, zParser,
           plugin loading, version management
    
  test crud
    Run CRUD test suite only (4 test files)
    Tests: Validation, JOIN operations, direct operations
    
  test all
    Run ALL test suites (core + CRUD)
    Comprehensive test coverage of entire framework
    
  test session
    Quick test to verify current shell has unique session ID
    Useful for debugging session isolation
""",
            "auth": """
Authentication Help:

  auth login
    Authenticate with your Zolo credentials
    Credentials are stored locally in ~/.zolo/credentials
    
  auth logout
    Clear stored credentials and logout
    
  auth status
    Display current authentication status and user information
    
  Note: Authentication is required to use zCLI
""",
        }
        
        if command_type in help_sections:
            print(help_sections[command_type])
        else:
            print(f"No specific help available for: {command_type}")
            print("Use 'help' for general help")
    
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

