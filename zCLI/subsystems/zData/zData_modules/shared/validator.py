# zCLI/subsystems/zData/zData_modules/shared/validator.py
"""Data validation engine for schema-based CRUD operations."""

from zCLI import re

class DataValidator:
    """Data validation engine enforcing schema rules before CRUD operations."""

    def __init__(self, schema, logger=None, zcli=None):
        """Initialize validator with schema, logger, and optional zcli instance.
        
        Args:
            schema (dict): Schema definition with table/field structure
            logger: Optional logger instance
            zcli: Optional zCLI instance (required for plugin validators)
        """
        self.schema = schema
        self.logger = logger
        self.zcli = zcli  # For plugin validator resolution
        self.format_validators = {
            'email': self._validate_email,
            'url': self._validate_url,
            'phone': self._validate_phone,
        }

    def validate_insert(self, table, data):
        """Validate data for INSERT - checks rules and required fields."""
        table_schema = self.schema.get(table, {})
        if not table_schema:
            if self.logger:
                self.logger.warning("No schema found for table: %s", table)
            return True, None

        errors = {}

        for field_name, value in data.items():
            field_def = table_schema.get(field_name)
            if not field_def or not isinstance(field_def, dict):
                continue

            rules = field_def.get('rules', {})
            if not rules:
                continue

            # Pass table_name and full_data for plugin validator context
            is_valid, error_msg = self._validate_field(field_name, value, rules, field_def, table_name=table, full_data=data)
            if not is_valid:
                errors[field_name] = error_msg

        for field_name, field_def in table_schema.items():
            if not isinstance(field_def, dict):
                continue

            is_required = field_def.get('required', False)
            if is_required and field_name not in data:
                if field_def.get('pk', False) or 'default' in field_def:
                    continue
                errors[field_name] = f"{field_name} is required"

        if errors:
            if self.logger:
                self.logger.warning("Validation failed with %d error(s)", len(errors))
            return False, errors

        if self.logger:
            self.logger.debug("[OK] Validation passed for table: %s", table)
        return True, None

    def validate_update(self, table, data):
        """Validate data for UPDATE - partial validation (no required field checks)."""
        table_schema = self.schema.get(table, {})
        if not table_schema:
            if self.logger:
                self.logger.warning("No schema found for table: %s", table)
            return True, None

        errors = {}

        for field_name, value in data.items():
            field_def = table_schema.get(field_name)
            if not field_def or not isinstance(field_def, dict):
                continue

            rules = field_def.get('rules', {})
            if not rules:
                continue

            # Pass table_name and full_data for plugin validator context
            is_valid, error_msg = self._validate_field(field_name, value, rules, field_def, table_name=table, full_data=data)
            if not is_valid:
                errors[field_name] = error_msg

        if errors:
            if self.logger:
                self.logger.warning("Validation failed with %d error(s)", len(errors))
            return False, errors

        if self.logger:
            self.logger.debug("[OK] Validation passed for table: %s", table)
        return True, None

    def _validate_field(self, field_name, value, rules, field_def, table_name=None, full_data=None):
        """Validate single field against schema rules (layered validation).
        
        Validation Order (fail-fast):
            Layer 1: String rules (min_length, max_length)
            Layer 2: Numeric rules (min, max)
            Layer 3: Pattern rules (regex)
            Layer 4: Format rules (email, url, phone)
            Layer 5: Plugin validator (custom business logic) - NEW!
        
        Args:
            field_name (str): Name of the field being validated
            value: Value to validate
            rules (dict): Validation rules from schema
            field_def (dict): Full field definition
            table_name (str): Table name (for plugin context)
            full_data (dict): All field data (for cross-field validation)
        
        Returns:
            tuple: (is_valid: bool, error_msg: str or None)
        """
        if value is None or value == "":
            return (True, None) if not field_def.get('required', False) else (False, f"{field_name} is required")

        # Layer 1: String rules
        error = self._check_string_rules(field_name, value, rules)
        if error:
            return False, error

        # Layer 2: Numeric rules
        error = self._check_numeric_rules(field_name, value, rules)
        if error:
            return False, error

        # Layer 3: Pattern rules
        error = self._check_pattern_rules(field_name, value, rules)
        if error:
            return False, error

        # Layer 4: Format rules
        error = self._check_format_rules(field_name, value, rules)
        if error:
            return False, error

        # Layer 5: Plugin validator (NEW - runs AFTER all built-in validators pass)
        error = self._check_plugin_validator(field_name, value, rules, table_name, full_data)
        if error:
            return False, error

        return True, None

    def _check_string_rules(self, field_name, value, rules):
        """Check string length rules."""
        if not isinstance(value, str):
            return None

        min_length = rules.get('min_length')
        if min_length and len(value) < min_length:
            return rules.get('error_message') or f"{field_name} must be at least {min_length} characters"

        max_length = rules.get('max_length')
        if max_length and len(value) > max_length:
            return rules.get('error_message') or f"{field_name} cannot exceed {max_length} characters"

        return None

    def _check_numeric_rules(self, field_name, value, rules):
        """Check numeric range rules."""
        if not isinstance(value, (int, float)):
            return None

        min_val = rules.get('min')
        if min_val is not None and value < min_val:
            return rules.get('error_message') or f"{field_name} must be at least {min_val}"

        max_val = rules.get('max')
        if max_val is not None and value > max_val:
            return rules.get('error_message') or f"{field_name} cannot exceed {max_val}"

        return None

    def _check_pattern_rules(self, field_name, value, rules):
        """Check regex pattern rules."""
        pattern = rules.get('pattern')
        if pattern and isinstance(value, str) and not re.match(pattern, value):
            return rules.get('pattern_message') or rules.get('error_message') or f"Invalid format for {field_name}"
        return None

    def _check_format_rules(self, field_name, value, rules):  # pylint: disable=unused-argument
        """Check format validation rules."""
        format_type = rules.get('format')
        if not format_type or not isinstance(value, str):
            return None

        validator = self.format_validators.get(format_type.lower())
        if validator:
            is_valid, error = validator(value)
            if not is_valid:
                return rules.get('error_message') or error
        else:
            if self.logger:
                self.logger.warning("Unknown format type: %s", format_type)

        return None

    def _validate_email(self, value):
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, value):
            return True, None
        return False, "Invalid email address format"

    def _validate_url(self, value):
        """Validate URL format."""
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if re.match(url_pattern, value, re.IGNORECASE):
            return True, None
        return False, "Invalid URL format"

    def _validate_phone(self, value):
        """Validate phone number format."""
        cleaned = re.sub(r'[\s\-\(\)\.]', '', value)
        phone_pattern = r'^\+?[0-9]{10,15}$'
        if re.match(phone_pattern, cleaned):
            return True, None
        return False, "Invalid phone number format"

    def _check_plugin_validator(self, field_name, value, rules, table_name=None, full_data=None):
        """Check custom plugin validator (Layer 5 - business logic).
        
        Plugin validators run AFTER all built-in validators pass (layered validation).
        Uses existing zCLI plugin infrastructure (&PluginName.function(args) pattern).
        
        Args:
            field_name (str): Name of the field being validated
            value: Field value to validate
            rules (dict): Validation rules from schema
            table_name (str): Table name (for context)
            full_data (dict): All field data (for cross-field validation)
        
        Returns:
            str or None: Error message if validation fails, None if valid/no validator
        
        Example schema usage:
            email:
              type: str
              rules:
                format: email  # Built-in (Layer 4)
                validator: "&validators.check_email_domain(['company.com'])"  # Plugin (Layer 5)
        """
        validator_spec = rules.get('validator')
        if not validator_spec:
            return None  # No plugin validator specified
        
        # Check if zcli instance is available (required for plugin resolution)
        if not self.zcli:
            if self.logger:
                self.logger.warning("Plugin validator specified but zcli not provided to DataValidator: %s", validator_spec)
            return None  # Graceful degradation
        
        # Validate plugin invocation syntax (must start with &)
        if not isinstance(validator_spec, str) or not validator_spec.startswith('&'):
            if self.logger:
                self.logger.warning("Invalid validator syntax (must start with &): %s", validator_spec)
            return None  # Skip invalid syntax
        
        try:
            # Use existing zCLI plugin infrastructure to resolve and execute
            # Parse the plugin invocation (e.g., "&validators.check_email_domain(['company.com'])")
            from zCLI.subsystems.zParser.zParser_modules.zParser_plugin import (
                _parse_invocation, _parse_arguments
            )
            
            plugin_name, function_name, args_str = _parse_invocation(validator_spec)
            
            # Check plugin cache first (reuse existing infrastructure)
            cached_module = self.zcli.loader.cache.get(plugin_name, cache_type="plugin")
            
            if not cached_module:
                # Plugin not found - graceful degradation
                if self.logger:
                    self.logger.warning("Plugin validator not found (skipping validation): %s", plugin_name)
                return None  # Skip validation if plugin missing
            
            # Get function from cached module
            if not hasattr(cached_module, function_name):
                if self.logger:
                    self.logger.warning("Function '%s' not found in plugin '%s'", function_name, plugin_name)
                return None  # Skip if function missing
            
            func = getattr(cached_module, function_name)
            
            # Parse user-provided arguments from schema
            user_args, user_kwargs = _parse_arguments(args_str)
            
            # Inject validator-specific arguments:
            # User args come first, then value, field_name, then kwargs context
            final_args = list(user_args) + [value, field_name]
            final_kwargs = {
                **user_kwargs,
                'table': table_name,
                'full_data': full_data or {}
            }
            
            # Execute validator plugin
            result = func(*final_args, **final_kwargs)
            
            # Validate return format (must be tuple: (is_valid, error_msg))
            if not isinstance(result, tuple) or len(result) != 2:
                if self.logger:
                    self.logger.error("Plugin validator must return (is_valid, error_msg) tuple: %s.%s", 
                                    plugin_name, function_name)
                return f"Plugin validator error: invalid return format"
            
            is_valid, error_msg = result
            
            # Return custom error_message if specified in rules, otherwise use plugin's error
            if not is_valid:
                return rules.get('error_message') or error_msg
            
            return None  # Validation passed
            
        except Exception as e:
            # Log plugin execution errors but don't crash validation
            if self.logger:
                self.logger.error("Plugin validator execution error (%s): %s", validator_spec, e, exc_info=True)
            return f"Plugin validator error: {str(e)}"
