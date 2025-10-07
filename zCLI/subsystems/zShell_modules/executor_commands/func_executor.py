# zCLI/subsystems/zShell_modules/executor_commands/func_executor.py
# ───────────────────────────────────────────────────────────────
"""Function command execution for zCLI."""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def execute_func(zcli, parsed):
    """
    Execute function commands like 'func generate_id zU'.
    
    Args:
        zcli: zCLI instance
        parsed: Parsed command dictionary
        
    Returns:
        Function execution result
    """
    func_name = parsed["action"]
    args = parsed["args"]
    
    # Format as zFunc expression
    func_expr = f"zFunc({func_name}({','.join(args)}))"
    
    logger.debug("Executing function: %s", func_expr)
    return zcli.funcs.handle(func_expr)
