# zCLI/subsystems/zDialog.py — Dialog/Form Subsystem
# ───────────────────────────────────────────────────────────────

"""
zDialog - Interactive Form/Dialog Subsystem

Purpose:
- Collect user input through interactive forms
- Validate input against schema models
- Handle form submission (onSubmit)
- Integration with zData for CRUD operations

Key Responsibilities:
- Form rendering (via zDisplay)
- Input collection and validation
- Context management (model, fields, zConv)
- Submission handling (dict or string expressions)
"""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)
from zCLI.subsystems.zDisplay import handle_zDisplay
from zCLI.subsystems.zSession import zSession
from zCLI.subsystems.zDialog_modules import create_dialog_context, handle_submit


class ZDialog:
    """
    zDialog - Interactive Form/Dialog Subsystem
    
    Handles user input collection through interactive forms with
    schema-based validation and submission handling.
    
    Key Features:
    - Schema-driven form rendering
    - Field validation
    - Context management (model, fields, zConv)
    - Flexible submission (dict or string expressions)
    
    Architecture:
        User → zDialog → zDisplay (render form)
                    ↓
              Collect input (zConv)
                    ↓
              onSubmit → zDispatch/zFunc → zData
    """
    
    def __init__(self, walker=None):
        """
        Initialize zDialog subsystem.
        
        Args:
            walker: Optional walker instance for context
        """
        self.walker = walker
        self.zSession = getattr(walker, "zSession", zSession)
        self.logger = getattr(walker, "logger", logger) if walker else logger

    def handle(self, zHorizontal):
        """
        Main entry point for dialog handling.
        
        Workflow:
        1. Parse dialog configuration (model, fields, onSubmit)
        2. Create dialog context
        3. Render form and collect input (via zDisplay)
        4. Handle submission if onSubmit provided
        
        Args:
            zHorizontal: Dialog configuration dict with zDialog key
            
        Returns:
            zConv (collected data) or submission result
        """
        handle_zDisplay({
            "event": "sysmsg",
            "label": "zDialog",
            "style": "full",
            "color": "ZDIALOG",
            "indent": 1
        })

        self.logger.info("\nReceived zHorizontal: %s", zHorizontal)

        # Validate input
        if not isinstance(zHorizontal, dict):
            msg = f"Unsupported zDialog expression type: {type(zHorizontal)}"
            self.logger.error(msg)
            raise TypeError(msg)

        # Extract dialog configuration
        zDialog_obj = zHorizontal["zDialog"]
        model = zDialog_obj["model"]
        fields = zDialog_obj["fields"]
        on_submit = zDialog_obj.get("onSubmit")

        self.logger.info(
            "\n   └─ model: %s"
            "\n   └─ fields: %s"
            "\n   └─ on_submit: %s",
            model,
            fields,
            on_submit
        )

        # Create dialog context
        zContext = create_dialog_context(model, fields)
        self.logger.info("\nzContext: %s", zContext)

        # Render form and collect input
        zConv = handle_zDisplay({
            "event": "zDialog",
            "context": zContext,
            "walker": self.walker,
        })
        
        # Add collected data to context
        zContext["zConv"] = zConv

        # Handle submission if onSubmit provided
        try:
            if on_submit:
                self.logger.info("Found onSubmit → Executing via handle_submit()")
                return handle_submit(on_submit, zContext, walker=self.walker)
            
            # No onSubmit - return collected data
            return zConv
            
        except Exception as e:
            self.logger.error("zDialog onSubmit failed: %s", e, exc_info=True)
            raise


# ─────────────────────────────────────────────────────────────────────────────
# Backward Compatibility Function
# ─────────────────────────────────────────────────────────────────────────────

def handle_zDialog(zHorizontal, walker=None):
    """
    Backward-compatible function for dialog handling.
    
    Args:
        zHorizontal: Dialog configuration dict
        walker: Optional walker instance
        
    Returns:
        zConv or submission result
    """
    return ZDialog(walker).handle(zHorizontal)
