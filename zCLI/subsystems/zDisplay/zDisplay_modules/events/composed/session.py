# zCLI/subsystems/zDisplay/zDisplay_modules/events/composed/session.py

"""Show session information with optional break."""

from ..basic.sysmsg import handle_sysmsg
from ..basic.text import handle_text
from ..basic.control import handle_break


def _display_field(label, value, output_adapter, indent=0, color="GREEN"):
    """Display a labeled field."""
    color_code = getattr(output_adapter.colors, color, output_adapter.colors.RESET)
    content = f"{color_code}{label}:{output_adapter.colors.RESET} {value}"
    if indent > 0:
        content = "  " * indent + content
    handle_text({"content": content, "break": False}, output_adapter)


def _display_section(title, output_adapter, indent=0, color="GREEN"):
    """Display a section title."""
    color_code = getattr(output_adapter.colors, color, output_adapter.colors.RESET)
    content = f"{color_code}{title}:{output_adapter.colors.RESET}"
    if indent > 0:
        content = "  " * indent + content
    handle_text({"content": content, "break": False}, output_adapter)


def _display_zmachine(zMachine, output_adapter):
    """Display zMachine section."""
    handle_text({"content": "", "break": False}, output_adapter)
    _display_section("zMachine", output_adapter, color="GREEN")
    
    # Identity & Deployment
    for field in ["os", "hostname", "architecture", "python_version", "deployment", "role"]:
        _display_field(f"  {field}", zMachine.get(field), output_adapter, color="YELLOW")
    
    # Tool Preferences
    if any([zMachine.get("browser"), zMachine.get("ide"), zMachine.get("shell")]):
        handle_text({"content": "", "break": False}, output_adapter)
        _display_section("  Tool Preferences", output_adapter, color="CYAN")
        for tool in ["browser", "ide", "shell"]:
            if zMachine.get(tool):
                _display_field(f"    {tool}", zMachine.get(tool), output_adapter, color="RESET")
    
    # System Capabilities
    if zMachine.get("cpu_cores") or zMachine.get("memory_gb"):
        handle_text({"content": "", "break": False}, output_adapter)
        _display_section("  System", output_adapter, color="CYAN")
        for field in ["cpu_cores", "memory_gb"]:
            if zMachine.get(field):
                _display_field(f"    {field}", zMachine.get(field), output_adapter, color="RESET")
    
    # zcli version
    if zMachine.get("zcli_version"):
        handle_text({"content": "", "break": False}, output_adapter)
        _display_field("  zcli_version", zMachine.get("zcli_version"), output_adapter, color="YELLOW")


def _display_zauth(zAuth, output_adapter):
    """Display zAuth section."""
    handle_text({"content": "", "break": False}, output_adapter)
    _display_section("zAuth", output_adapter, color="GREEN")
    for field in ["id", "username", "role", "API_Key"]:
        _display_field(f"  {field}", zAuth.get(field), output_adapter, color="YELLOW")


def handle_session(obj, output_adapter, input_adapter=None, logger=None):
    """Display session information with optional break."""
    sess = obj.get("zSession")
    should_break = obj.get("break", True)
    break_message = obj.get("break_message")
    
    if sess is None:
        handle_text({"content": "No session available", "break": False}, output_adapter)
        return
    
    # Header
    handle_sysmsg({"label": "View zSession", "indent": 0}, output_adapter, session=sess, mycolor="MAIN")
    
    # Core session fields
    _display_field("zSession_ID", sess.get("zS_id"), output_adapter)
    _display_field("zMode", sess.get("zMode"), output_adapter)
    
    # zMachine section
    zMachine = sess.get("zMachine", {})
    if zMachine:
        _display_zmachine(zMachine, output_adapter)
    
    # Session fields
    handle_text({"content": "", "break": False}, output_adapter)
    for field in ["zWorkspace", "zVaFile_path", "zVaFilename", "zBlock"]:
        _display_field(field, sess.get(field), output_adapter)
    
    # zAuth section
    zAuth = sess.get("zAuth", {})
    _display_zauth(zAuth, output_adapter)
    
    # Optional break at the end
    if should_break and input_adapter:
        handle_text({"content": "", "break": False}, output_adapter)
        break_obj = {"message": break_message} if break_message else {}
        handle_break(break_obj, output_adapter, input_adapter, logger)

