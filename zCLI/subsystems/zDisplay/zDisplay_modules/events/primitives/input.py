# zCLI/subsystems/zDisplay/zDisplay_modules/events/primitives/input.py

"""Input primitive handlers for reading strings and passwords."""


def handle_read(obj, input_adapter, logger):
    """Read string primitive - blocks until Enter, returns string."""
    prompt = obj.get("prompt", "")
    logger.debug("handle_read: prompt='%s'", prompt)
    return input_adapter.read_string(prompt)


def handle_read_password(obj, input_adapter, logger):
    """Read password primitive - masked input, returns string."""
    prompt = obj.get("prompt", "")
    logger.debug("handle_read_password: prompt='%s'", prompt)
    return input_adapter.read_password(prompt)
