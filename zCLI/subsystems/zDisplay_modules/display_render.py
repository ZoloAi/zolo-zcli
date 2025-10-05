# zCLI/subsystems/zDisplay_modules/display_render.py
"""
Rendering functions for zDisplay - Headers, menus, tables, markers, sessions
"""

import json
from zCLI.utils.logger import logger
from .display_colors import Colors, print_line


def render_marker(zDisplay_Obj):
    """Render zMarker (in/out markers)."""
    _, _, direction = zDisplay_Obj["event"].partition(".")
    direction = direction.lower() or "out"
    color = "GREEN" if direction == "in" else "MAGENTA"
    label = f"zMarker ({direction})"
    print()
    print_line(color, label, "full", 0)
    print()


def render_header(zDisplay_Obj):
    """Render zHeader (section headers)."""
    print_line(
        zDisplay_Obj["color"],
        zDisplay_Obj["label"],
        zDisplay_Obj["style"],
        zDisplay_Obj["indent"]
    )


def render_menu(zDisplay_Obj):
    """Render zMenu (numbered menu options)."""
    print("\n")
    for number, option in zDisplay_Obj["menu"]:
        print(f"  [{number}] {option}")


def render_session(zDisplay_Obj):
    """Render zSession view (session information)."""
    render_header({
        "event": "header",
        "label": "View_zSession",
        "color": "EXTERNAL",
        "style": "~",
        "indent": 0,
    })

    sess = zDisplay_Obj.get("zSession")
    if sess is None:
        # Lazy import to reduce circular import risk
        from zCLI.subsystems.zSession import zSession
        sess = zSession

    # Safe getters
    def g(key, default=None):
        return sess.get(key, default)

    def g_auth(key, default=None):
        return g("zAuth", {}).get(key, default)
    
    print(f"{Colors.GREEN}zSession_ID:{Colors.RESET} {g('zS_id')}")
    print(f"{Colors.GREEN}zMode:{Colors.RESET} {g('zMode')}")
    
    # Add machine information
    zMachine = g('zMachine', {})
    if zMachine:
        print(f"\n{Colors.GREEN}zMachine:{Colors.RESET}")
        print(f"  {Colors.YELLOW}platform:{Colors.RESET} {zMachine.get('platform')}")
        print(f"  {Colors.YELLOW}environment:{Colors.RESET} {zMachine.get('environment')}")
        print(f"  {Colors.YELLOW}architecture:{Colors.RESET} {zMachine.get('architecture')}")
        print(f"  {Colors.YELLOW}python_version:{Colors.RESET} {zMachine.get('python_version')}")
        print(f"  {Colors.YELLOW}zcli_version:{Colors.RESET} {zMachine.get('zcli_version')}")
        
        capabilities = zMachine.get('capabilities', {})
        print(f"  {Colors.YELLOW}capabilities:{Colors.RESET}")
        for cap, available in capabilities.items():
            status = "YES" if available else "NO"
            print(f"    {cap}: {status}")

    print(f"\n{Colors.GREEN}zWorkspace:{Colors.RESET} {g('zWorkspace')}")
    print(f"{Colors.GREEN}zVaFile_path:{Colors.RESET} {g('zVaFile_path')}")
    print(f"{Colors.GREEN}zVaFilename:{Colors.RESET} {g('zVaFilename')}")
    print(f"{Colors.GREEN}zBlock:{Colors.RESET} {g('zBlock')}")

    print(f"\n{Colors.GREEN}zAuth:{Colors.RESET}")
    print(f"  {Colors.YELLOW}id:{Colors.RESET} {g_auth('id')}")
    print(f"  {Colors.YELLOW}username:{Colors.RESET} {g_auth('username')}")
    print(f"  {Colors.YELLOW}role:{Colors.RESET} {g_auth('role')}")
    print(f"  {Colors.YELLOW}API_Key:{Colors.RESET} {g_auth('API_Key')}")

    print(f"\n{Colors.GREEN}zCrumbs:{Colors.RESET}")
    print(f"  {Colors.MAGENTA}{g('zCrumbs', {})}{Colors.RESET}")

    print(f"\n{Colors.GREEN}zCache:{Colors.RESET}")
    print(f"  {Colors.MAGENTA}{g('zCache', {})}{Colors.RESET}")


def render_json(zDisplay_Obj):
    """Render JSON data with formatting."""
    title  = zDisplay_Obj.get("title", "JSON")
    color  = zDisplay_Obj.get("color", "CYAN")
    style  = zDisplay_Obj.get("style", "~")
    indent = zDisplay_Obj.get("indent", 1)
    data   = zDisplay_Obj.get("payload", None)

    # Header
    print_line(color, title, style, indent)

    # JSON dump
    if data is not None:
        try:
            json_str = json.dumps(data, indent=4, ensure_ascii=False)
            print(f"{Colors.CYAN}{json_str}{Colors.RESET}")
        except Exception as e:
            logger.error("Failed to serialize JSON: %s", e)
            print(f"{Colors.RED}[Error serializing JSON]{Colors.RESET}")


def render_table(obj):
    """Render zTable (data table display)."""
    title = obj.get("title", "Table")
    rows = obj.get("rows", [])
    color = obj.get("color", "CYAN")
    style = obj.get("style", "~")
    indent = obj.get("indent", 1)

    # Header
    print_line(color, f"{title} rows", style, indent)

    # Render rows
    if rows:
        try:
            json_str = json.dumps(rows, indent=4, ensure_ascii=False)
            print(f"{Colors.CYAN}{json_str}{Colors.RESET}")
        except Exception as e:
            logger.error("Failed to serialize table rows: %s", e)
            print(f"{Colors.RED}[Error serializing table]{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}[No rows to display]{Colors.RESET}")


def print_crumbs(session=None):
    """
    Print breadcrumb trail from session.
    
    Args:
        session: Session dict to use (optional, defaults to global zSession)
    """
    from zCLI.subsystems.zSession import zSession as global_zSession
    target_session = session if session is not None else global_zSession
    
    zCrumbs_zPrint = {}
    for zScope, zTrail in target_session.get("zCrumbs", {}).items():
        path = " > ".join(zTrail) if zTrail else ""
        zCrumbs_zPrint[zScope] = path
    print("\nzCrumbs:")
    for zScope, path in zCrumbs_zPrint.items():
        print(f"{zScope}[{path}]")
