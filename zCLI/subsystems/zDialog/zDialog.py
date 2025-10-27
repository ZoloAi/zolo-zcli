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
        self.display.zDeclare("zDialog Ready", color=self.mycolor, indent=0, style="full")

    def handle(self, zHorizontal, context=None):
        """Handle dialog form input and submission."""
        self.display.zDeclare("zDialog", color=self.mycolor, indent=1, style="single")

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
            "\n   |-- model: %s"
            "\n   |-- fields: %s"
            "\n   |-- on_submit: %s",
            model,
            fields,
            on_submit
        )

        # Create dialog context
        zContext = create_dialog_context(model, fields, self.logger)
        self.logger.info("\nzContext: %s", zContext)

        # Check if data is pre-provided (WebSocket/GUI mode)
        if context and "websocket_data" in context:
            ws_data = context["websocket_data"]
            if "data" in ws_data:
                zConv = ws_data["data"]
                self.logger.info("Using pre-provided data from WebSocket: %s", zConv)
            else:
                zConv = {}
        else:
            # Render form and collect input (Terminal/Walker mode)
            zConv = self.display.zDialog(zContext, self.zcli, self.walker)
        
        # Add collected data to context
        zContext["zConv"] = zConv

        # ──────────────────────────────────────────────────────────────────
        # AUTO-VALIDATION (Week 5.2): Validate form data against zSchema
        # ──────────────────────────────────────────────────────────────────
        if model and isinstance(model, str) and model.startswith('@'):
            self.logger.info("Auto-validation enabled (model: %s)", model)
            
            try:
                # Load schema from model path
                schema_dict = self.zcli.loader.handle(model)
                
                # Extract table name from model path (e.g., '@.zSchema.users' → 'users')
                table_name = model.split('.')[-1]
                
                # Create DataValidator instance
                from zCLI.subsystems.zData.zData_modules.shared.validator import DataValidator
                validator = DataValidator(schema_dict, self.logger)
                
                # Validate collected form data (use validate_insert for new data)
                is_valid, errors = validator.validate_insert(table_name, zConv)
                
                if not is_valid:
                    self.logger.warning("Auto-validation failed with %d error(s)", len(errors))
                    
                    # Display validation errors
                    from zCLI.subsystems.zData.zData_modules.shared.operations.helpers import display_validation_errors
                    
                    # Create a mock ops object with required attributes for display_validation_errors
                    class ValidationOps:
                        def __init__(self, zcli):
                            self.zcli = zcli
                            self.logger = zcli.logger
                            self.display = zcli.display
                    
                    ops = ValidationOps(self.zcli)
                    display_validation_errors(table_name, errors, ops)
                    
                    # For zBifrost mode, also emit WebSocket event
                    if self.session.get('zMode') == 'zBifrost':
                        try:
                            self.zcli.comm.websocket.broadcast({
                                'event': 'validation_error',
                                'table': table_name,
                                'errors': errors,
                                'fields': list(errors.keys())
                            })
                        except Exception as ws_err:
                            self.logger.warning("Failed to broadcast validation errors via WebSocket: %s", ws_err)
                    
                    # Don't proceed to onSubmit - return None to indicate validation failure
                    self.display.zDeclare("zDialog Return (validation failed)", color=self.mycolor, indent=1, style="~")
                    return None
                
                self.logger.info("[OK] Auto-validation passed for %s", table_name)
                
            except Exception as val_err:
                # If auto-validation fails (schema not found, etc.), log warning but proceed
                # This maintains backward compatibility - forms without valid models still work
                self.logger.warning("Auto-validation error (proceeding anyway): %s", val_err)
        
        elif model:
            self.logger.debug("Auto-validation skipped (model doesn't start with '@'): %s", model)
        else:
            self.logger.debug("Auto-validation skipped (no model specified)")

        # Handle submission if onSubmit provided
        try:
            if on_submit:
                self.logger.info("Found onSubmit => Executing via handle_submit()")
                return handle_submit(on_submit, zContext, self.logger, walker=self.walker)
            
            # No onSubmit - return collected data
            return zConv
            
        except Exception as e:
            self.logger.error("zDialog onSubmit failed: %s", e, exc_info=True)
            raise


# ─────────────────────────────────────────────────────────────────────────────
# Backward Compatibility Function
# ─────────────────────────────────────────────────────────────────────────────

def handle_zDialog(zHorizontal, walker=None, zcli=None, context=None):
    """Backward-compatible function for dialog handling."""
    # Modern: use zcli directly if provided
    if zcli:
        return zDialog(zcli, walker=walker).handle(zHorizontal, context=context)
    
    # Legacy: extract zcli from walker
    if walker and hasattr(walker, 'zcli'):
        return zDialog(walker.zcli, walker=walker).handle(zHorizontal, context=context)
    
    raise ValueError("handle_zDialog requires either zcli or walker with zcli attribute")
