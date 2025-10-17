# zCLI/subsystems/zShell/zShell_modules/executor_commands/alias_utils.py

# zCLI/subsystems/zShell_modules/executor_commands/alias_utils.py
"""Alias resolution utilities for $alias references in commands."""

def resolve_alias(value, pinned_cache, logger, raise_on_missing=True):
    """Resolve $alias to cached content from PinnedCache, returns (resolved_value, is_alias)."""
    if not isinstance(value, str) or not value.startswith("$"):
        return value, False

    alias_name = value[1:]
    cached = pinned_cache.get_alias(alias_name)

    if cached is not None:
        logger.debug("[ALIAS] Resolved $%s from PinnedCache", alias_name)
        return cached, True

    if raise_on_missing:
        error_msg = (
            f"Alias not found: ${alias_name}\n"
            f"Use 'load <zPath> --as {alias_name}' to create this alias.\n"
            f"Example: load @.zCLI.Schemas.zSchema.{alias_name} --as {alias_name}"
        )
        logger.error("[ALIAS] %s", error_msg)
        raise ValueError(error_msg)

    logger.warning("[ALIAS] Alias $%s not found, using original value", alias_name)
    return value, False

def get_alias_name(alias_ref):
    """Extract alias name from $alias reference (returns None if not an alias)."""
    if isinstance(alias_ref, str) and alias_ref.startswith("$"):
        return alias_ref[1:]
    return None

def is_alias(value):
    """Check if value is an alias reference (starts with $)."""
    return isinstance(value, str) and value.startswith("$")

def resolve_option_aliases(options, loaded_cache, logger, option_keys=None):
    """Resolve $alias references in options dict, returning new dict with resolved values."""
    resolved_options = options.copy()
    resolved_info = {}

    keys_to_check = option_keys if option_keys else options.keys()

    for key in keys_to_check:
        if key not in options:
            continue

        value = options[key]

        if is_alias(value):
            try:
                resolved_value, was_alias = resolve_alias(value, loaded_cache, logger)
                if was_alias:
                    resolved_options[key] = resolved_value
                    resolved_info[key] = get_alias_name(value)
                    logger.debug("[ALIAS] Resolved option --%s: %s", key, value)
            except ValueError as e:
                raise ValueError(f"Failed to resolve --{key} alias: {e}") from e

    if resolved_info:
        resolved_options["_alias_resolved"] = resolved_info

    return resolved_options
