from zCLI.utils.logger import logger
from zCLI.subsystems.zFunc import handle_zFunc
from zCLI.subsystems.zDisplay import handle_zDisplay
from zCLI.subsystems.zSession import zSession

class ZDialog:
    def __init__(self, walker=None):
        self.walker = walker
        self.zSession = getattr(walker, "zSession", zSession)
        self.logger = getattr(walker, "logger", logger) if walker else logger

    def handle(self, zHorizontal):
        handle_zDisplay({
            "event": "header",
            "label": "zDialog",
            "style": "full",
            "color": "ZDIALOG",
            "indent": 1
        })

        self.logger.info("\nReceived zHorizontal: %s", zHorizontal)

        if not isinstance(zHorizontal, dict):
            msg = f"Unsupported zDialog expression type: {type(zHorizontal)}"
            self.logger.error(msg)
            raise TypeError(msg)

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
            on_submit)

        zContext = {
            "model": model,
            "fields": fields,
        }
        self.logger.info("\nzContext: %s", zContext)

        zConv = handle_zDisplay({
            "event": "zDialog",
            "context": zContext,
            "walker": self.walker,  # Pass walker for session context
        })
        zContext["zConv"] = zConv
        try:
            if on_submit:
                self.logger.info("Found onSubmit → Executing via handle_submit()")
                return self.handle_submit(on_submit, zContext)
            return zConv
        except Exception as e:
            self.logger.error("zDialog onSubmit failed: %s", e, exc_info=True)
            raise

# ────────────────────────────────────────────────────────────────

    def handle_submit(self, submit_expr, zContext):
        """Handle the zDialog onSubmit expression.

        Supports legacy string-based expressions (evaluated via zFunc) and the
        new dict-based syntax which is dispatched through zLaunch/zCRUD directly.
        """

        handle_zDisplay({
            "event": "header",
            "label": "zSubmit",
            "style": "single",
            "color": "ZDIALOG",
            "indent": 2
        })

        self.logger.debug("zSubmit_expr: %s", submit_expr)
        self.logger.debug("zContext keys: %s | zConv: %s", list(zContext.keys()), zContext.get("zConv"))

        # ── New: dict-based submission → launch via zDispatch ─────────────
        if isinstance(submit_expr, dict):
            self.logger.debug("zSubmit detected dict payload; preparing for zLaunch")

            def inject_placeholders(obj):
                """Recursively replace placeholder strings like 'zConv[...]'."""
                if isinstance(obj, dict):
                    return {k: inject_placeholders(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [inject_placeholders(v) for v in obj]
                if isinstance(obj, str):
                    if obj == "zConv":
                        return zContext.get("zConv")
                    if obj.startswith("zConv"):
                        try:
                            # Handle dot notation for dict access (e.g., zConv.id → zConv['id'])
                            zconv_data = zContext.get("zConv", {})
                            if "." in obj and isinstance(zconv_data, dict):
                                # Convert zConv.key to dict access
                                parts = obj.split(".", 1)
                                if parts[0] == "zConv" and len(parts) == 2:
                                    return zconv_data.get(parts[1])
                            return eval(obj, {}, {"zConv": zconv_data})
                        except Exception as e:
                            self.logger.error("Failed to eval placeholder '%s': %s", obj, e)
                            return obj
                return obj

            submit_dict = inject_placeholders(submit_expr)
            # Ensure model is passed to zCRUD - it expects it at the top level of the zCRUD action
            if "zCRUD" in submit_dict and isinstance(submit_dict["zCRUD"], dict):
                if "model" not in submit_dict["zCRUD"]:
                    submit_dict["zCRUD"]["model"] = zContext.get("model")
            elif "model" not in submit_dict:
                submit_dict["model"] = zContext.get("model")

            from zCLI.walker.zDispatch import zLauncher  # local import to avoid cycle
            self.logger.info("Dispatching dict onSubmit via zLauncher: %s", submit_dict)
            # Pass walker so downstream uses proper context when available
            result = zLauncher(submit_dict, walker=self.walker)

            handle_zDisplay({
                "event": "header",
                "label": "zSubmit Return",
                "style": "~",
                "color": "ZDIALOG",
                "indent": 3
            })

            handle_zDisplay({
                "event": "header",
                "label": "zDialog Return",
                "style": "~",
                "color": "ZDIALOG",
                "indent": 2
            })

            return result

    # ── Legacy string-based submission via zFunc ───────────────────────────
        if not isinstance(submit_expr, str):
            self.logger.error("zSubmit expression must be a string or dict.")
            return False

        if "zConv" in submit_expr:
            self.logger.debug("Detected 'zConv' in submit_expr — injecting...")
            try:
                injected_value = repr(zContext.get("zConv", {}))
                self.logger.debug("Injected zConv value: %s", injected_value)
                submit_expr = submit_expr.replace("zConv", injected_value)
            except Exception as e:
                self.logger.error("Failed to inject zConv: %s", e)
                return False

        self.logger.info("Final zSubmit to execute: %s", submit_expr)
        handle_zDisplay({
            "event": "header",
            "label": " → Handle zFunc",
            "style": "single",
            "color": "DISPATCH",
            "indent": 5
        })
        result = handle_zFunc(submit_expr, zContext=zContext, walker=self.walker)
        self.logger.debug("zSubmit result: %s", result)
        handle_zDisplay({
            "event": "header",
            "label": "zSubmit Return",
            "style": "~",
            "color": "ZDIALOG",
            "indent": 3
        })

        handle_zDisplay({
            "event": "header",
            "label": "zDialog Return",
            "style": "~",
            "color": "ZDIALOG",
            "indent": 2
        })

        return result


def handle_zDialog(zHorizontal, walker=None):
    return ZDialog(walker).handle(zHorizontal)
