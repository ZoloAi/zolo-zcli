# zCLI/subsystems/zData/zData_modules/shared/validator.py
# ----------------------------------------------------------------
# Data validation engine for classical CRUD operations.
#
# Validates data against schema rules before INSERT/UPDATE operations.
# Supports: required, min/max length, min/max values, regex patterns, 
# and format validators (email, url, phone).
# ----------------------------------------------------------------

import re
from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


class DataValidator:
    """
    Data validation engine for CRUD operations.
    
    Validates data against schema-defined rules to ensure data integrity
    before database operations.
    """
    
    def __init__(self, schema):
        """
        Initialize validator with schema.
        
        Args:
            schema (dict): Parsed schema dictionary with table definitions
        """
        self.schema = schema
        
        # Built-in format validators
        self.format_validators = {
            'email': self._validate_email,
            'url': self._validate_url,
            'phone': self._validate_phone,
        }
    
    def validate_insert(self, table, data):
        """
        Validate data for INSERT operation.
        
        Checks all validation rules and required fields.
        
        Args:
            table (str): Table name
            data (dict): Dictionary of field:value pairs to validate
            
        Returns:
            tuple: (is_valid: bool, errors: dict or None)
        """
        logger.debug("Validating INSERT operation for table: %s", table)
        
        # Get table schema
        table_schema = self.schema.get(table, {})
        if not table_schema:
            logger.warning("No schema found for table: %s", table)
            return True, None  # No schema = no validation
        
        errors = {}
        
        # Validate each field in the data
        for field_name, value in data.items():
            field_def = table_schema.get(field_name)
            if not field_def or not isinstance(field_def, dict):
                continue  # Skip if no definition
            
            # Get validation rules
            rules = field_def.get('rules', {})
            if not rules:
                continue  # No rules = skip validation
            
            # Validate the field
            is_valid, error_msg = self._validate_field(field_name, value, rules, field_def)
            if not is_valid:
                errors[field_name] = error_msg
        
        # Check for required fields that are missing
        for field_name, field_def in table_schema.items():
            if not isinstance(field_def, dict):
                continue
            
            # Check if field is required
            is_required = field_def.get('required', False)
            if is_required and field_name not in data:
                # Skip if field has auto-generation (pk, default value)
                if field_def.get('pk', False) or 'default' in field_def:
                    continue
                errors[field_name] = f"{field_name} is required"
        
        if errors:
            logger.warning("Validation failed with %d error(s)", len(errors))
            return False, errors
        
        logger.debug("✅ Validation passed for table: %s", table)
        return True, None
    
    def validate_update(self, table, data):
        """
        Validate data for UPDATE operation.
        
        Similar to INSERT but doesn't check for required fields
        (since UPDATE is partial).
        
        Args:
            table (str): Table name
            data (dict): Dictionary of field:value pairs to validate
            
        Returns:
            tuple: (is_valid: bool, errors: dict or None)
        """
        logger.debug("Validating UPDATE operation for table: %s", table)
        
        # Get table schema
        table_schema = self.schema.get(table, {})
        if not table_schema:
            logger.warning("No schema found for table: %s", table)
            return True, None  # No schema = no validation
        
        errors = {}
        
        # Validate each field in the data
        for field_name, value in data.items():
            field_def = table_schema.get(field_name)
            if not field_def or not isinstance(field_def, dict):
                continue  # Skip if no definition
            
            # Get validation rules
            rules = field_def.get('rules', {})
            if not rules:
                continue  # No rules = skip validation
            
            # Validate the field
            is_valid, error_msg = self._validate_field(field_name, value, rules, field_def)
            if not is_valid:
                errors[field_name] = error_msg
        
        if errors:
            logger.warning("Validation failed with %d error(s)", len(errors))
            return False, errors
        
        logger.debug("✅ Validation passed for table: %s", table)
        return True, None
    
    def _validate_field(self, field_name, value, rules, field_def):
        """
        Validate a single field against its rules.
        
        Args:
            field_name (str): Name of the field
            value: Field value
            rules (dict): Dictionary of validation rules
            field_def (dict): Full field definition (for type info)
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        # Skip validation if value is None/empty and field is not required
        if value is None or value == "":
            if not field_def.get('required', False):
                return True, None
            return False, f"{field_name} is required"
        
        # 1. Length validation (for strings)
        if isinstance(value, str):
            min_length = rules.get('min_length')
            if min_length and len(value) < min_length:
                msg = rules.get('error_message') or f"{field_name} must be at least {min_length} characters"
                return False, msg
            
            max_length = rules.get('max_length')
            if max_length and len(value) > max_length:
                msg = rules.get('error_message') or f"{field_name} cannot exceed {max_length} characters"
                return False, msg
        
        # 2. Range validation (for numbers)
        if isinstance(value, (int, float)):
            min_val = rules.get('min')
            if min_val is not None and value < min_val:
                msg = rules.get('error_message') or f"{field_name} must be at least {min_val}"
                return False, msg
            
            max_val = rules.get('max')
            if max_val is not None and value > max_val:
                msg = rules.get('error_message') or f"{field_name} cannot exceed {max_val}"
                return False, msg
        
        # 3. Pattern validation (regex)
        pattern = rules.get('pattern')
        if pattern and isinstance(value, str):
            if not re.match(pattern, value):
                msg = rules.get('pattern_message') or rules.get('error_message') or f"Invalid format for {field_name}"
                return False, msg
        
        # 4. Format validation (email, url, phone, etc.)
        format_type = rules.get('format')
        if format_type and isinstance(value, str):
            validator = self.format_validators.get(format_type.lower())
            if validator:
                is_valid, error = validator(value)
                if not is_valid:
                    msg = rules.get('error_message') or error
                    return False, msg
            else:
                logger.warning("Unknown format type: %s", format_type)
        
        return True, None
    
    def _validate_email(self, value):
        """
        Validate email format.
        
        Args:
            value (str): Email string to validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        # Basic email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(email_pattern, value):
            return True, None
        return False, "Invalid email address format"
    
    def _validate_url(self, value):
        """
        Validate URL format.
        
        Args:
            value (str): URL string to validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        # Basic URL pattern
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        
        if re.match(url_pattern, value, re.IGNORECASE):
            return True, None
        return False, "Invalid URL format"
    
    def _validate_phone(self, value):
        """
        Validate phone number format.
        
        Args:
            value (str): Phone string to validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]', '', value)
        
        # Check if it's a valid phone number (10-15 digits, optional + prefix)
        phone_pattern = r'^\+?[0-9]{10,15}$'
        
        if re.match(phone_pattern, cleaned):
            return True, None
        return False, "Invalid phone number format"

