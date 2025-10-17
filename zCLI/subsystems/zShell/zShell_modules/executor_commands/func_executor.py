# zCLI/subsystems/zShell/zShell_modules/executor_commands/func_executor.py

# zCLI/subsystems/zShell_modules/executor_commands/func_executor.py
# ───────────────────────────────────────────────────────────────
"""Function command execution for zCLI."""

def execute_func(zcli, parsed):
    """Execute function commands like 'func generate_id zU'."""
    func_name = parsed["action"]
    args = parsed["args"]
    
    # Format as zFunc expression
    func_expr = f"zFunc({func_name}({','.join(args)}))"
    
    zcli.logger.debug("Executing function: %s", func_expr)
    return zcli.funcs.handle(func_expr)
