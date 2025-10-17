# zCLI/subsystems/zData/zData_modules/shared/validator.py
"""Data validation engine for schema-based CRUD operations."""

import re

class DataValidator:
    """Data validation engine enforcing schema rules before CRUD operations."""

    def __init__(self, schema):
        """Initialize validator with schema."""
        self.schema = schema
        self.format_validators = {
            'email': self._validate_email,
            'url': self._validate_url,
            'phone': self._validate_phone,
        }

    def validate_insert(self, table, data):
        """Validate data for INSERT - checks rules and required fields."""
        table_schema = self.schema.get(table, {})
        if not table_schema:
            logger.warning("No schema found for table: %s", table)
            return True, None

        errors = {}

        for field_name, value in data.items():
            field_def = table_schema.get(field_name)
            if not field_def or not isinstance(field_def, dict):
                continue

            rules = field_def.get('rules', {})
            if not rules:
                continue

            is_valid, error_msg = self._validate_field(field_name, value, rules, field_def)
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
            logger.warning("Validation failed with %d error(s)", len(errors))
            return False, errors

        logger.debug("[OK] Validation passed for table: %s", table)
        return True, None

    def validate_update(self, table, data):
        """Validate data for UPDATE - partial validation (no required field checks)."""
        table_schema = self.schema.get(table, {})
        if not table_schema:
            logger.warning("No schema found for table: %s", table)
            return True, None

        errors = {}

        for field_name, value in data.items():
            field_def = table_schema.get(field_name)
            if not field_def or not isinstance(field_def, dict):
                continue

            rules = field_def.get('rules', {})
            if not rules:
                continue

            is_valid, error_msg = self._validate_field(field_name, value, rules, field_def)
            if not is_valid:
                errors[field_name] = error_msg

        if errors:
            logger.warning("Validation failed with %d error(s)", len(errors))
            return False, errors

        logger.debug("[OK] Validation passed for table: %s", table)
        return True, None

    def _validate_field(self, field_name, value, rules, field_def):
        """Validate single field against schema rules."""
        if value is None or value == "":
            return (True, None) if not field_def.get('required', False) else (False, f"{field_name} is required")

        error = self._check_string_rules(field_name, value, rules)
        if error:
            return False, error

        error = self._check_numeric_rules(field_name, value, rules)
        if error:
            return False, error

        error = self._check_pattern_rules(field_name, value, rules)
        if error:
            return False, error

        error = self._check_format_rules(field_name, value, rules)
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
            logger.warning("Unknown format type: %s", format_type)

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
