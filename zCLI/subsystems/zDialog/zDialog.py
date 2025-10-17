# zCLI/subsystems/zDialog/zDialog.py

"""Interactive Form/Dialog Subsystem for collecting and validating user input."""

from .zDialog_modules import create_dialog_context, handle_submit

class zDialog:
    """Interactive Form/Dialog Subsystem for collecting and validating user input."""

    def __init__(self, zcli, walker=None):
        """Initialize zDialog subsystem."""
        if zcli is None:
            raise ValueError("zDialog requires a zCLI instance")

        if not hasattr(zcli, 'session'):
            raise ValueError("Invalid zCLI instance: missing 'session' attribute")

        # Modern architecture: zCLI instance provides all dependencies
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.display = zcli.display
        self.zparser = zcli.zparser
        self.zfunc = zcli.zfunc  # For onSubmit processing

        # Keep walker for legacy compatibility
        self.walker = walker
        self.mycolor = "ZDIALOG"
        self.display.handle({
            "event": "sysmsg",
            "label": "zDialog Ready",
            "color": self.mycolor,
            "indent": 0
        })

    def handle(self, zHorizontal):
        """Handle dialog form input and submission."""
        self.display.handle({
            "event": "sysmsg",
            "label": "zDialog",
            "color": self.mycolor,
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
        zContext = create_dialog_context(model, fields, self.logger)
        self.logger.info("\nzContext: %s", zContext)

        # Render form and collect input
        zConv = self.display.handle({
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
                return handle_submit(on_submit, zContext, self.logger, walker=self.walker)
            
            # No onSubmit - return collected data
            return zConv
            
        except Exception as e:
            self.logger.error("zDialog onSubmit failed: %s", e, exc_info=True)
            raise


# ─────────────────────────────────────────────────────────────────────────────
# Backward Compatibility Function
# ─────────────────────────────────────────────────────────────────────────────

def handle_zDialog(zHorizontal, walker=None, zcli=None):
    """Backward-compatible function for dialog handling."""
    # Modern: use zcli directly if provided
    if zcli:
        return zDialog(zcli, walker=walker).handle(zHorizontal)
    
    # Legacy: extract zcli from walker
    if walker and hasattr(walker, 'zcli'):
        return zDialog(walker.zcli, walker=walker).handle(zHorizontal)
    
    raise ValueError("handle_zDialog requires either zcli or walker with zcli attribute")
