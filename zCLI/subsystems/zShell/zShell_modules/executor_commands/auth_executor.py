# zCLI/subsystems/zShell/zShell_modules/executor_commands/auth_executor.py

# zCLI/subsystems/zShell_modules/executor_commands/auth_executor.py
"""Authentication command executor (login, logout, status)."""

def execute_auth(zcli, parsed):
    """Execute auth commands (login, logout, status)."""
    action = parsed["action"]
    args = parsed.get("args", [])

    zcli.logger.debug("Executing auth command: %s", action)

    if action == "login":
        username = args[0] if len(args) > 0 else None
        password = args[1] if len(args) > 1 else None
        return zcli.auth.login(username, password)

    if action == "logout":
        return zcli.auth.logout()

    if action == "status":
        return zcli.auth.status()

    return {"error": f"Unknown auth action: {action}"}
