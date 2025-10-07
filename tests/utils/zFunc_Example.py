import os
import sys
from logger import Logger
from zCLI.subsystems.zDisplay import handle_zDisplay

def Func_Example(session=None):
    """
    Simple proof that a standalone Python function can be executed from zolo-zcli.
    """
    
    # Simple proof data
    proof = {
        "python_executable": sys.executable,
        "process_id": os.getpid(),
        "message": "Standalone Python function executed successfully!"
    }
    
    # Log it
    logger.info("Func_Example executed - Process ID: %s", proof["process_id"])
    
    # Display simple proof
    handle_zDisplay({
        "event": "text",
        "value": f"""
✅ SUCCESS! Standalone Python Function Executed!

Python: {proof['python_executable']}
Process ID: {proof['process_id']}

This proves zolo-zcli can execute standalone Python functions!
        """,
        "color": "GREEN",
        "pause": True
    })
    
    return proof