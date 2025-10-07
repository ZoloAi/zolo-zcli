from logger import Logger
from zCLI.subsystems.zDisplay import handle_zDisplay
from zCLI.subsystems.zWalker.zWalker_modules.zDispatch import handle_zDispatch
# Global session import removed - use instance-based sessions
import re

# Logger instance
logger = Logger.get_logger(__name__)


class ZWizard:
    def __init__(self, walker=None):
        self.walker = walker
        self.zSession = getattr(walker, "zSession", None)
        if not self.zSession:
            raise ValueError("ZWizard requires a walker with a session")
        self.logger = getattr(walker, "logger", logger) if walker else logger

    def handle(self, zWizard_obj):
        """Execute a sequence of steps, storing results in zHat."""
        handle_zDisplay({
            "event": "sysmsg",
            "label": "Handle zWizard",
            "style": "full",
            "color": "ZWIZARD",
            "indent": 1,
        })

        zHat = []
        for step_key, step_value in zWizard_obj.items():
            handle_zDisplay({
                "event": "sysmsg",
                "label": f"zWizard step: {step_key}",
                "style": "single",
                "color": "ZWIZARD",
                "indent": 2,
            })

            if isinstance(step_value, str):
                def repl(match):
                    idx = int(match.group(1))
                    return repr(zHat[idx]) if idx < len(zHat) else "None"
                step_value = re.sub(r"zHat\[(\d+)\]", repl, step_value)

            result = handle_zDispatch(step_key, step_value, walker=self.walker)
            zHat.append(result)

        self.logger.info("zWizard completed with zHat: %s", zHat)
        return zHat


def handle_zWizard(zWizard_obj, walker=None):
    return ZWizard(walker).handle(zWizard_obj)
