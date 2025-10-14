# zCLI/subsystems/zDisplay_new_modules/events/composed/session.py
"""
Session display handler - show session information.

Composed event that displays complete session state using basic and primitive events.
"""


def handle_session(obj, output_adapter, input_adapter=None):
    """
    Display session information with optional break.
    
    Shows complete session state including zMachine, zAuth, and session fields.
    
    Args:
        obj: Display object with:
            - zSession (dict): Session dictionary to display
            - break (bool, optional): Auto-break after display (default: True)
            - break_message (str, optional): Custom break message
        output_adapter: Output adapter for rendering
        input_adapter: Input adapter for break (optional)
    """
    from ..basic.sysmsg import handle_sysmsg
    from ..basic.text import handle_text
    from ..basic.control import handle_break
    from ...utils import Colors
    
    sess = obj.get("zSession")
    should_break = obj.get("break", True)
    break_message = obj.get("break_message")
    
    if sess is None:
        handle_text({"content": "No session available", "break": False}, output_adapter)
        return
    
    # Header
    handle_sysmsg(
        {"label": "View zSession", "indent": 0}, 
        output_adapter,
        session=sess,
        mycolor="MAIN"
    )
    
    # Helper to display a field
    def display_field(label, value, indent=0, color="GREEN"):
        """Display a labeled field."""
        color_code = getattr(Colors, color, Colors.RESET)
        content = f"{color_code}{label}:{Colors.RESET} {value}"
        if indent > 0:
            content = "  " * indent + content
        handle_text({"content": content, "break": False}, output_adapter)
    
    def display_section(title, indent=0, color="GREEN"):
        """Display a section title."""
        color_code = getattr(Colors, color, Colors.RESET)
        content = f"{color_code}{title}:{Colors.RESET}"
        if indent > 0:
            content = "  " * indent + content
        handle_text({"content": content, "break": False}, output_adapter)
    
    # Core session fields
    display_field("zSession_ID", sess.get("zS_id"))
    display_field("zMode", sess.get("zMode"))
    
    # zMachine section
    zMachine = sess.get("zMachine", {})
    if zMachine:
        handle_text({"content": "", "break": False}, output_adapter)  # Blank line
        display_section("zMachine", color="GREEN")
        
        # Identity
        display_field("  os", zMachine.get("os"), color="YELLOW")
        display_field("  hostname", zMachine.get("hostname"), color="YELLOW")
        display_field("  architecture", zMachine.get("architecture"), color="YELLOW")
        display_field("  python_version", zMachine.get("python_version"), color="YELLOW")
        
        # Deployment
        display_field("  deployment", zMachine.get("deployment"), color="YELLOW")
        display_field("  role", zMachine.get("role"), color="YELLOW")
        
        # Tool Preferences
        if any([zMachine.get("browser"), zMachine.get("ide"), zMachine.get("shell")]):
            handle_text({"content": "", "break": False}, output_adapter)
            display_section("  Tool Preferences", color="CYAN")
            if zMachine.get("browser"):
                display_field("    browser", zMachine.get("browser"), color="RESET")
            if zMachine.get("ide"):
                display_field("    ide", zMachine.get("ide"), color="RESET")
            if zMachine.get("shell"):
                display_field("    shell", zMachine.get("shell"), color="RESET")
        
        # System Capabilities
        if zMachine.get("cpu_cores") or zMachine.get("memory_gb"):
            handle_text({"content": "", "break": False}, output_adapter)
            display_section("  System", color="CYAN")
            if zMachine.get("cpu_cores"):
                display_field("    cpu_cores", zMachine.get("cpu_cores"), color="RESET")
            if zMachine.get("memory_gb"):
                display_field("    memory_gb", zMachine.get("memory_gb"), color="RESET")
        
        # zcli version
        if zMachine.get("zcli_version"):
            handle_text({"content": "", "break": False}, output_adapter)
            display_field("  zcli_version", zMachine.get("zcli_version"), color="YELLOW")
    
    # Session fields
    handle_text({"content": "", "break": False}, output_adapter)
    display_field("zWorkspace", sess.get("zWorkspace"))
    display_field("zVaFile_path", sess.get("zVaFile_path"))
    display_field("zVaFilename", sess.get("zVaFilename"))
    display_field("zBlock", sess.get("zBlock"))
    
    # zAuth section
    handle_text({"content": "", "break": False}, output_adapter)
    display_section("zAuth", color="GREEN")
    zAuth = sess.get("zAuth", {})
    display_field("  id", zAuth.get("id"), color="YELLOW")
    display_field("  username", zAuth.get("username"), color="YELLOW")
    display_field("  role", zAuth.get("role"), color="YELLOW")
    display_field("  API_Key", zAuth.get("API_Key"), color="YELLOW")
    
    # Optional break at the end
    if should_break and input_adapter:
        handle_text({"content": "", "break": False}, output_adapter)  # Blank line
        break_obj = {}
        if break_message:
            break_obj["message"] = break_message
        handle_break(break_obj, output_adapter, input_adapter)

