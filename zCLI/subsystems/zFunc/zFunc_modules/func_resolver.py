# zCLI/subsystems/zFunc/zFunc_modules/func_resolver.py

"""Function resolution and loading utilities."""

import os
import importlib.util


def resolve_callable(file_path, func_name, logger_instance):
    """Resolve and load a callable function from a Python file."""
    try:
        logger_instance.debug("File path: %s", file_path)
        logger_instance.debug("Function name: %s", func_name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No such file: {file_path}")

        # Load module from file
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get function from module
        func = getattr(module, func_name)
        logger_instance.debug("Resolved callable: %s", func)
        return func

    except Exception as e:
        logger_instance.error("Failed to resolve callable from '%s > %s': %s", 
                            file_path, func_name, e, exc_info=True)
        raise

