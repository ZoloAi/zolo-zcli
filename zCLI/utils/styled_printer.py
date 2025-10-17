# zCLI/utils/styled_printer.py

"""
Styled printer utilities for zCLI subsystems.

Provides styled output capabilities for subsystems that need to print
before zDisplay is available (like zConfig, zAuth, etc.).
"""


class StyledPrinter:
    """Utility class for styled console output."""
    
    @staticmethod
    def print_ready(label, color="SCHEMA", width=60):
        """
        Print a styled 'Ready' message.
        
        Args:
            label: The label to display (e.g., "zConfig Ready")
            color: Color name to use (default: "CONFIG" for green)
            width: Total width of the banner (default: 60)
        """
        try:
            # Use Colors from utils (available early)
            from zCLI.utils.colors import Colors
            color_code = getattr(Colors, color, Colors.RESET)
            
            char = "═"
            label_len = len(label) + 2
            space = width - label_len
            left = space // 2
            right = space - left
            colored_label = f"{color_code} {label} {Colors.RESET}"
            line = f"{char * left}{colored_label}{char * right}"
            print(line)
            
        except Exception:  # pylint: disable=broad-except
            # Fallback to plain text if Colors not available
            char = "═"
            label_len = len(label) + 2
            space = width - label_len
            left = space // 2
            right = space - left
            line = f"{char * left} {label} {char * right}"
            print(line)
    
    @staticmethod
    def print_banner(text, char="=", width=60):
        """
        Print a simple text banner.
        
        Args:
            text: Text to display
            char: Character to use for borders (default: "=")
            width: Width of the banner (default: 60)
        """
        print(char * width)
        print(text.center(width))
        print(char * width)
    
    @staticmethod
    def print_section(title, char="-", width=60):
        """
        Print a section header.
        
        Args:
            title: Section title
            char: Character to use for underline (default: "-")
            width: Width of the section header (default: 60)
        """
        print(f"\n{title}")
        print(char * min(len(title), width))
    
    @staticmethod
    def print_success(message, details=None):
        """
        Print a success message.
        
        Args:
            message: Success message
            details: Optional details to show
        """
        print(f"\n✅ {message}")
        if details:
            print(f"   {details}")
        print()
    
    @staticmethod
    def print_error(message, details=None):
        """
        Print an error message.
        
        Args:
            message: Error message
            details: Optional details to show
        """
        print(f"\n❌ {message}")
        if details:
            print(f"   {details}")
        print()
    
    @staticmethod
    def print_warning(message, details=None):
        """
        Print a warning message.
        
        Args:
            message: Warning message
            details: Optional details to show
        """
        print(f"\n⚠️  {message}")
        if details:
            print(f"   {details}")
        print()
    
    @staticmethod
    def print_info(message, details=None):
        """
        Print an info message.
        
        Args:
            message: Info message
            details: Optional details to show
        """
        print(f"\nℹ️  {message}")
        if details:
            print(f"   {details}")
        print()


# Convenience functions for common use cases
def print_subsystem_ready(subsystem_name, color="SCHEMA"):
    """Print a standard subsystem ready message."""
    StyledPrinter.print_ready(f"{subsystem_name} Ready", color)


# Global function that accepts any subsystem name
def print_ready(subsystem_name, color=None):
    """
    Print a subsystem ready message with automatic color mapping.
    
    Args:
        subsystem_name: Name of the subsystem (e.g., "zConfig", "zAuth", "zData")
        color: Optional color override. If None, will auto-map based on subsystem name.
    """
    # Auto-map colors based on subsystem name if not provided
    if color is None:
        color_mapping = {
            "zConfig": "SCHEMA",
            "zAuth": "AUTH", 
            "zData": "DATA",
            "zShell": "SHELL",
            "zDisplay": "DISPLAY",
            "zWalker": "WALKER",
            "zWizard": "WIZARD",
            "zNavigation": "NAV",
            "zDialog": "DIALOG",
            "zDispatch": "DISPATCH",
            "zFunc": "FUNC",
            "zLoader": "LOADER",
            "zLogger": "LOGGER",
            "zOpen": "OPEN",
            "zParser": "PARSER",
            "zSession": "SESSION",
            "zUtils": "UTILS",
        }
        color = color_mapping.get(subsystem_name, "SCHEMA")
    
    print_subsystem_ready(subsystem_name, color)


# Backward compatibility functions
def print_config_ready():
    """Print zConfig ready message."""
    print_ready("zConfig", "CONFIG")


def print_auth_ready():
    """Print zAuth ready message."""
    print_ready("zAuth")


def print_data_ready():
    """Print zData ready message."""
    print_ready("zData")


def print_shell_ready():
    """Print zShell ready message."""
    print_ready("zShell")
