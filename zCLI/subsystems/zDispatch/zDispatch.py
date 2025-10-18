# zCLI/subsystems/zDispatch/zDispatch.py

"""zDispatch - Core Command Dispatch Subsystem for zCLI."""

from .zDispatch_modules.modifiers import ModifierProcessor
from .zDispatch_modules.launcher import CommandLauncher

class zDispatch:
    """Core command dispatch subsystem for zCLI."""

    def __init__(self, zcli):
        """Initialize zDispatch subsystem."""
        if zcli is None:
            raise ValueError("zDispatch requires a zCLI instance")

        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.mycolor = "DISPATCH"

        # Initialize modules
        self.modifiers = ModifierProcessor(self)
        self.launcher = CommandLauncher(self)

        # Print styled ready message
        self._print_ready()

        self.logger.info("[zDispatch] Command dispatch subsystem ready")

    def _print_ready(self):
        """Print styled 'Ready' message (before zDisplay is available)."""
        try:
            from zCLI.utils import Colors
            color_code = getattr(Colors, self.mycolor, Colors.RESET)
            label = "zDispatch Ready"
            BASE_WIDTH = 60
            char = "═"
            label_len = len(label) + 2
            space = BASE_WIDTH - label_len
            left = space // 2
            right = space - left
            colored_label = f"{color_code} {label} {Colors.RESET}"
            line = f"{char * left}{colored_label}{char * right}"
            print(line)
        except Exception:
            # Silently fail if Colors not available
            pass

    def handle(self, zKey, zHorizontal, context=None, walker=None):
        """Handle dispatch with optional wizard context and walker."""
        # Use walker's display if available, otherwise use zCLI's display
        display = walker.display if walker else self.zcli.display
        
        display.handle({
            "event": "sysmsg",
            "label": "handle zDispatch",
            "style": "full",
            "color": self.mycolor,
            "indent": 1
        })
        
        self.logger.info("zHorizontal: %s", zHorizontal)
        self.logger.info("handle zDispatch for key: %s", zKey)

        # Check for modifiers
        prefix_mods = self.modifiers.check_prefix(zKey)
        suffix_mods = self.modifiers.check_suffix(zKey)
        zModifiers = prefix_mods + suffix_mods

        self.logger.info("Prefix modifiers: %s", prefix_mods)
        self.logger.info("Suffix modifiers: %s", suffix_mods)
        self.logger.info("Detected modifiers for %s: %s", zKey, zModifiers)

        if zModifiers:
            result = self.modifiers.process(zModifiers, zKey, zHorizontal, context=context, walker=walker)
            self.logger.info("Modifier evaluation result: %s", result)
        else:
            result = self.launcher.launch(zHorizontal, context=context, walker=walker)
            self.logger.info("dispatch result: %s", result)

        self.logger.info("Modifier evaluation completed for key: %s", zKey)
        return result


def handle_zDispatch(zKey, zHorizontal, zcli=None, walker=None, context=None):
    """Standalone dispatch function with optional wizard context and walker."""
    # Determine zCLI instance
    if walker:
        zcli_instance = walker.zcli
    elif zcli:
        zcli_instance = zcli
    else:
        raise ValueError("handle_zDispatch requires either zcli or walker parameter")
    
    # Use zCLI's dispatch subsystem
    return zcli_instance.dispatch.handle(zKey, zHorizontal, context=context, walker=walker)
