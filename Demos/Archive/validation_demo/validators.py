"""Example plugin validators for zCLI - demonstrating custom business logic validation.

These validators extend built-in validation (pattern, format, min/max) with domain-specific rules.
"""

def check_email_domain(allowed_domains, value, field_name, **kwargs):
    """Validate email domain against allowed list.
    
    This validator demonstrates layered validation:
    - Built-in format validator checks email structure (Layer 4)
    - This plugin checks business rule: approved domains (Layer 5)
    
    Args:
        allowed_domains (list): User-provided from schema (e.g., ['company.com', 'partner.com'])
        value (str): Field value (auto-injected by DataValidator)
        field_name (str): Field name (auto-injected by DataValidator)
        **kwargs: Context (table, full_data)
    
    Returns:
        tuple: (is_valid: bool, error_msg: str or None)
    
    Example schema usage:
        email:
          type: str
          rules:
            format: email  # Built-in (structural validation)
            validator: "&validators.check_email_domain(['company.com', 'partner.com'])"
            error_message: "Email must be from approved domain"
    """
    # Defensive: email format should already be validated by Layer 4
    if '@' not in value:
        return False, f"{field_name} must be a valid email"
    
    domain = value.split('@')[1].lower()
    
    # Normalize allowed domains to lowercase
    allowed_lower = [d.lower() for d in allowed_domains]
    
    if domain not in allowed_lower:
        return False, f"{field_name} must use approved domain: {', '.join(allowed_domains)}"
    
    return True, None  # ✅ Valid


def check_username_blacklist(blacklist, value, field_name, **kwargs):
    """Validate username is not in blacklist.
    
    Demonstrates custom business rule enforcement.
    
    Args:
        blacklist (list): Forbidden usernames (e.g., ['admin', 'root', 'system'])
        value (str): Field value
        field_name (str): Field name
        **kwargs: Context
    
    Returns:
        tuple: (is_valid: bool, error_msg: str or None)
    
    Example schema usage:
        username:
          type: str
          rules:
            pattern: "^[a-zA-Z0-9_]{3,20}$"  # Built-in (structural)
            validator: "&validators.check_username_blacklist(['admin', 'root', 'system'])"
    """
    # Case-insensitive check
    value_lower = value.lower()
    blacklist_lower = [name.lower() for name in blacklist]
    
    if value_lower in blacklist_lower:
        return False, f"{field_name} '{value}' is reserved and cannot be used"
    
    return True, None  # ✅ Valid


def check_sku_format_extended(prefix_required, value, field_name, **kwargs):
    """Validate SKU has specific company prefix.
    
    Demonstrates extending pattern validation with business logic.
    
    Args:
        prefix_required (str): Required SKU prefix (e.g., 'ACME-')
        value (str): Field value
        field_name (str): Field name
        **kwargs: Context
    
    Returns:
        tuple: (is_valid: bool, error_msg: str or None)
    
    Example schema usage:
        sku:
          type: str
          rules:
            pattern: "^[A-Z]{2,4}-[0-9]{4,6}$"  # Built-in (structural format)
            validator: "&validators.check_sku_format_extended('ACME-')"
            error_message: "SKU must start with company prefix ACME-"
    """
    if not value.startswith(prefix_required):
        return False, f"{field_name} must start with prefix: {prefix_required}"
    
    return True, None  # ✅ Valid


def check_password_strength(min_upper, min_digit, value, field_name, **kwargs):
    """Validate password strength (business policy).
    
    Demonstrates complex business rule (password policy).
    
    Args:
        min_upper (int): Minimum uppercase letters required
        min_digit (int): Minimum digits required
        value (str): Field value
        field_name (str): Field name
        **kwargs: Context
    
    Returns:
        tuple: (is_valid: bool, error_msg: str or None)
    
    Example schema usage:
        password:
          type: str
          rules:
            min_length: 8  # Built-in (structural)
            validator: "&validators.check_password_strength(1, 1)"
            error_message: "Password must contain at least 1 uppercase and 1 digit"
    """
    upper_count = sum(1 for c in value if c.isupper())
    digit_count = sum(1 for c in value if c.isdigit())
    
    errors = []
    if upper_count < min_upper:
        errors.append(f"at least {min_upper} uppercase letter(s)")
    if digit_count < min_digit:
        errors.append(f"at least {min_digit} digit(s)")
    
    if errors:
        return False, f"{field_name} must contain {' and '.join(errors)}"
    
    return True, None  # ✅ Valid


def check_age_eligibility(min_age, value, field_name, **kwargs):
    """Validate age meets eligibility requirement.
    
    Demonstrates simple business rule on top of built-in numeric validation.
    
    Args:
        min_age (int): Minimum age required
        value (int): Field value
        field_name (str): Field name
        **kwargs: Context
    
    Returns:
        tuple: (is_valid: bool, error_msg: str or None)
    
    Example schema usage:
        age:
          type: int
          rules:
            min: 0  # Built-in (structural)
            max: 150  # Built-in (structural)
            validator: "&validators.check_age_eligibility(18)"
            error_message: "Must be 18 or older to register"
    """
    if value < min_age:
        return False, f"Must be {min_age} or older"
    
    return True, None  # ✅ Valid


def check_cross_field_match(other_field, value, field_name, **kwargs):
    """Validate field matches another field (cross-field validation).
    
    Demonstrates using full_data context for cross-field validation.
    
    Args:
        other_field (str): Name of field that must match
        value: Field value
        field_name (str): Field name
        **kwargs: Context (full_data contains all fields)
    
    Returns:
        tuple: (is_valid: bool, error_msg: str or None)
    
    Example schema usage:
        password_confirm:
          type: str
          rules:
            validator: "&validators.check_cross_field_match('password')"
            error_message: "Passwords must match"
    """
    full_data = kwargs.get('full_data', {})
    other_value = full_data.get(other_field)
    
    if other_value is None:
        return False, f"Cannot validate {field_name}: {other_field} not provided"
    
    if value != other_value:
        return False, f"{field_name} must match {other_field}"
    
    return True, None  # ✅ Valid

