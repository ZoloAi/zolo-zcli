# zCLI/subsystems/zDisplay_modules/display_render.py
"""
Rendering functions for zDisplay - Headers, menus, tables, markers, sessions
"""

import json
from logger import Logger
from .display_colors import Colors, print_line

# Logger instance
logger = Logger.get_logger(__name__)


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


def render_text(zDisplay_Obj):
    """Render text paragraph with simple line separators."""
    value = zDisplay_Obj.get("value", "")
    color = zDisplay_Obj.get("color", "RESET")
    indent = zDisplay_Obj.get("indent", 0)
    pause = zDisplay_Obj.get("pause", False)
    
    # Support \n and <br> for line breaks
    text = value.replace("<br>", "\n")
    
    color_code = getattr(Colors, color, Colors.RESET)
    indent_str = "  " * indent
    
    # Simple separators
    print()
    print(f"{indent_str}{'-' * 60}")
    print(f"{indent_str}{color_code}{text}{Colors.RESET}")
    print(f"{indent_str}{'-' * 60}")
    print()
    
    # Pause if requested
    if pause:
        input(f"{indent_str}Press Enter to continue...")

def render_menu(zDisplay_Obj):
    """Render zMenu (numbered menu options)."""
    print("\n")
    for number, option in zDisplay_Obj["menu"]:
        print(f"  [{number}] {option}")


def render_session(zDisplay_Obj):
    """Render zSession view (session information)."""
    render_header({
        "event": "sysmsg",
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
    
    # Add machine information (from machine.yaml)
    zMachine = g('zMachine', {})
    if zMachine:
        print(f"\n{Colors.GREEN}zMachine:{Colors.RESET} (from machine.yaml)")
        
        # Identity
        print(f"  {Colors.YELLOW}os:{Colors.RESET} {zMachine.get('os')}")
        print(f"  {Colors.YELLOW}hostname:{Colors.RESET} {zMachine.get('hostname')}")
        print(f"  {Colors.YELLOW}architecture:{Colors.RESET} {zMachine.get('architecture')}")
        print(f"  {Colors.YELLOW}python_version:{Colors.RESET} {zMachine.get('python_version')}")
        
        # Deployment
        print(f"  {Colors.YELLOW}deployment:{Colors.RESET} {zMachine.get('deployment')}")
        print(f"  {Colors.YELLOW}role:{Colors.RESET} {zMachine.get('role')}")
        
        # Tool Preferences (streamlined - no text_editor)
        print(f"\n  {Colors.CYAN}Tool Preferences:{Colors.RESET}")
        print(f"    browser: {zMachine.get('browser')}")
        print(f"    ide: {zMachine.get('ide')}")
        print(f"    shell: {zMachine.get('shell')}")
        
        # System Capabilities
        if zMachine.get('cpu_cores') or zMachine.get('memory_gb'):
            print(f"\n  {Colors.CYAN}System:{Colors.RESET}")
            if zMachine.get('cpu_cores'):
                print(f"    cpu_cores: {zMachine.get('cpu_cores')}")
            if zMachine.get('memory_gb'):
                print(f"    memory_gb: {zMachine.get('memory_gb')}")
        
        # zcli version (if available)
        if zMachine.get('zcli_version'):
            print(f"\n  {Colors.YELLOW}zcli_version:{Colors.RESET} {zMachine.get('zcli_version')}")

    print(f"\n{Colors.GREEN}zWorkspace:{Colors.RESET} {g('zWorkspace')}")
    print(f"{Colors.GREEN}zVaFile_path:{Colors.RESET} {g('zVaFile_path')}")
    print(f"{Colors.GREEN}zVaFilename:{Colors.RESET} {g('zVaFilename')}")
    print(f"{Colors.GREEN}zBlock:{Colors.RESET} {g('zBlock')}")

    print(f"\n{Colors.GREEN}zAuth:{Colors.RESET}")
    print(f"  {Colors.YELLOW}id:{Colors.RESET} {g_auth('id')}")
    print(f"  {Colors.YELLOW}username:{Colors.RESET} {g_auth('username')}")
    print(f"  {Colors.YELLOW}role:{Colors.RESET} {g_auth('role')}")
    print(f"  {Colors.YELLOW}API_Key:{Colors.RESET} {g_auth('API_Key')}")

    # Show breadcrumb trails
    print(f"\n{Colors.GREEN}zCrumbs:{Colors.RESET}")
    crumbs = g('zCrumbs', {})
    if crumbs:
        for scope, trail in crumbs.items():
            trail_str = " > ".join(trail) if trail else "(empty)"
            print(f"  {Colors.YELLOW}{scope}:{Colors.RESET} {trail_str}")
    else:
        print(f"  {Colors.MAGENTA}(no breadcrumbs){Colors.RESET}")

    # Show 3-tier cache with actual contents
    print(f"\n{Colors.GREEN}zCache:{Colors.RESET} (3-tier)")
    cache = g('zCache', {})
    
    if cache:
        # System cache (LRU auto-managed UI/config files)
        system_cache = cache.get('system_cache', {})
        print(f"  {Colors.CYAN}system_cache:{Colors.RESET} ({len(system_cache)} cached)")
        if system_cache:
            for cache_key, cache_entry in list(system_cache.items())[:5]:
                # Show complete structure of cached data
                cached_data = cache_entry.get("data", {}) if isinstance(cache_entry, dict) else cache_entry
                
                if isinstance(cached_data, dict):
                    # Show all top-level keys (blocks)
                    blocks = list(cached_data.keys())
                    total_keys = sum(len(v) if isinstance(v, dict) else 1 for v in cached_data.values())
                    print(f"    - {cache_key}")
                    print(f"      └─ {len(blocks)} blocks, {total_keys} total keys (complete file cached)")
                else:
                    print(f"    - {cache_key}: {type(cached_data).__name__}")
            if len(system_cache) > 5:
                print(f"    ... and {len(system_cache) - 5} more")
        
        # Pinned cache (user-loaded aliases)
        pinned_cache = cache.get('pinned_cache', {})
        print(f"  {Colors.CYAN}pinned_cache:{Colors.RESET} ({len(pinned_cache)} aliases)")
        if pinned_cache:
            for cache_key in pinned_cache.keys():
                print(f"    - {cache_key}")
        
        # Schema cache (active connections - metadata only)
        schema_cache = cache.get('schema_cache', {})
        print(f"  {Colors.CYAN}schema_cache:{Colors.RESET} ({len(schema_cache)} connections)")
        if schema_cache:
            for alias_name, metadata in schema_cache.items():
                status = "active" if metadata.get("active") else "inactive"
                print(f"    - ${alias_name}: {status}")
    else:
        print(f"  {Colors.MAGENTA}(empty){Colors.RESET}")


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
