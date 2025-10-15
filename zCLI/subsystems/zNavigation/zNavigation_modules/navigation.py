"""Navigation state management for zNavigation."""

from logger import Logger

logger = Logger.get_logger(__name__)


class Navigation:
    """Navigation state and history management."""

    def __init__(self, navigation):
        """Initialize navigation manager."""
        self.navigation = navigation
        self.zcli = navigation.zcli
        self.logger = navigation.logger

    def navigate_to(self, target, context=None):
        """
        Navigate to a specific target.
        
        Args:
            target: Navigation target (file, block, key, etc.)
            context: Optional navigation context
            
        Returns:
            Navigation result
        """
        self.logger.debug("Navigating to: %s", target)
        
        # Store current location in history
        current = self.get_current_location()
        if current:
            self._add_to_history(current)
        
        # Update current location
        self._set_current_location(target, context)
        
        return {"status": "navigated", "target": target}

    def get_current_location(self):
        """Get current navigation location."""
        return self.zcli.session.get("current_location", {})

    def get_navigation_history(self):
        """Get navigation history."""
        return self.zcli.session.get("navigation_history", [])

    def _add_to_history(self, location):
        """Add location to navigation history."""
        history = self.get_navigation_history()
        history.append(location)
        
        # Limit history size
        if len(history) > 50:  # Keep last 50 navigation points
            history.pop(0)
        
        self.zcli.session["navigation_history"] = history

    def _set_current_location(self, target, context=None):
        """Set current navigation location."""
        location = {
            "target": target,
            "context": context,
            "timestamp": self._get_timestamp()
        }
        self.zcli.session["current_location"] = location

    def _get_timestamp(self):
        """Get current timestamp for navigation metadata."""
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def go_back(self):
        """Navigate back to previous location."""
        history = self.get_navigation_history()
        if not history:
            return {"status": "error", "message": "No navigation history"}
        
        previous = history.pop()
        self.zcli.session["navigation_history"] = history
        
        # Navigate to previous location
        return self.navigate_to(previous["target"], previous.get("context"))

    def clear_history(self):
        """Clear navigation history."""
        self.zcli.session["navigation_history"] = []
        self.logger.info("Navigation history cleared")
