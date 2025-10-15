"""Menu builder for zMenu."""

from logger import Logger

logger = Logger.get_logger(__name__)


class MenuBuilder:
    """Handles menu object construction for zMenu."""

    def __init__(self, menu):
        """Initialize menu builder."""
        self.menu = menu
        self.zcli = menu.zcli
        self.logger = menu.logger

    def build(self, options, title=None, allow_back=True):
        """
        Build menu object from options.
        
        Args:
            options: List of options or dict with options
            title: Optional menu title
            allow_back: Whether to add "Back" option
            
        Returns:
            Menu object ready for rendering
        """
        # Normalize options to list
        if isinstance(options, dict):
            option_list = list(options.keys())
        elif isinstance(options, list):
            option_list = options
        else:
            option_list = [str(options)]

        # Add back option if requested
        if allow_back and "zBack" not in option_list:
            option_list.append("zBack")

        # Create menu object
        menu_obj = {
            "options": option_list,
            "title": title,
            "allow_back": allow_back,
            "metadata": {
                "created_by": "zMenu",
                "timestamp": self._get_timestamp()
            }
        }

        self.logger.debug("Built menu object: %s", menu_obj)
        return menu_obj

    def build_dynamic(self, data_source, display_field=None, title=None, allow_back=True):
        """
        Build menu from dynamic data source.
        
        Args:
            data_source: Function that returns data or list of data
            display_field: Field to display from objects
            title: Optional menu title
            allow_back: Whether to add "Back" option
            
        Returns:
            Menu object
        """
        try:
            # Get data from source
            if callable(data_source):
                data = data_source()
            else:
                data = data_source

            # Extract display values
            if display_field and isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict):
                    options = [str(item.get(display_field, item)) for item in data]
                else:
                    options = [str(item) for item in data]
            else:
                options = [str(item) for item in data]

            return self.build(options, title, allow_back)

        except Exception as e:
            self.logger.error("Failed to build dynamic menu: %s", e)
            return self.build(["Error loading menu"], "Error", True)

    def build_from_function(self, func_name, *args, **kwargs):
        """
        Build menu from zFunc call.
        
        Args:
            func_name: Name of function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Menu object
        """
        try:
            # Call function through zFunc
            result = self.zcli.zfunc.handle(f"zFunc({func_name}, {args}, {kwargs})")
            
            # Convert result to menu options
            if isinstance(result, list):
                options = [str(item) for item in result]
            else:
                options = [str(result)]

            return self.build(options, f"Results from {func_name}", True)

        except Exception as e:
            self.logger.error("Failed to build menu from function %s: %s", func_name, e)
            return self.build(["Function error"], f"Error calling {func_name}", True)

    def _get_timestamp(self):
        """Get current timestamp for menu metadata."""
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S")
