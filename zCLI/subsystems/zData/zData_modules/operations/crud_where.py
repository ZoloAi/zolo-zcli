#!/usr/bin/env python3
# zCLI/subsystems/crud/crud_where.py — Advanced WHERE Clause Builder
# ───────────────────────────────────────────────────────────────

"""
Advanced WHERE Clause Builder for zCRUD

Supports:
- Comparison operators: <, >, <=, >=, !=, =
- IN operator: field: [val1, val2, val3]
- LIKE patterns: field: {LIKE: "%pattern%"}
- IS NULL / IS NOT NULL: field: None or {IS NOT: None}
- OR conditions: OR: [{cond1}, {cond2}]
- AND conditions: Default behavior

Examples:
    # Simple equality (backward compatible)
    where = {"type": "web", "status": "active"}
    # SQL: WHERE type = ? AND status = ?

    # Comparison operators
    where = {"age": {">": 18}, "score": {"<=": 100}}
    # SQL: WHERE age > ? AND score <= ?

    # IN operator
    where = {"type": ["web", "mobile"], "status": "active"}
    # SQL: WHERE type IN (?, ?) AND status = ?

    # LIKE patterns
    where = {"name": {"LIKE": "%test%"}}
    # SQL: WHERE name LIKE ?

    # IS NULL
    where = {"deleted_at": None}
    # SQL: WHERE deleted_at IS NULL

    # OR conditions
    where = {"OR": [{"status": "active"}, {"priority": {">=": 5}}]}
    # SQL: WHERE (status = ? OR priority >= ?)
"""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def build_where_clause(filters, table_prefix=None):
    """
    Build an advanced WHERE clause with support for multiple operators.
    
    Args:
        filters (dict): Filter conditions
        table_prefix (str, optional): Table name to prefix columns
        
    Returns:
        tuple: (where_clause, params)
    """
    if not filters or not isinstance(filters, dict):
        return "", []
    
    conditions, params = _parse_conditions(filters, table_prefix)
    
    if not conditions:
        return "", []
    
    where_clause = " WHERE " + " AND ".join(conditions)
    logger.debug("Built WHERE clause: %s | params: %s", where_clause, params)
    
    return where_clause, params


def _parse_conditions(filters, table_prefix=None):
    """Parse filter dictionary into SQL conditions and parameters."""
    conditions = []
    params = []
    
    for key, value in filters.items():
        # Handle OR conditions
        if key.upper() == "OR":
            if isinstance(value, list) and value:
                or_conditions, or_params = _parse_or_conditions(value, table_prefix)
                if or_conditions:
                    conditions.append(f"({or_conditions})")
                    params.extend(or_params)
            continue
        
        # Regular field conditions
        field = f"{table_prefix}.{key}" if table_prefix and "." not in key else key
        
        # Handle different value types
        if value is None:
            conditions.append(f"{field} IS NULL")
        
        elif isinstance(value, dict):
            cond, cond_params = _parse_operator_condition(field, value)
            if cond:
                conditions.append(cond)
                params.extend(cond_params)
        
        elif isinstance(value, list):
            if value:
                placeholders = ", ".join(["?"] * len(value))
                conditions.append(f"{field} IN ({placeholders})")
                params.extend(value)
        
        else:
            conditions.append(f"{field} = ?")
            params.append(value)
    
    return conditions, params


def _parse_or_conditions(or_list, table_prefix=None):
    """Parse OR conditions from a list of condition dictionaries."""
    or_conditions = []
    or_params = []
    
    for condition_dict in or_list:
        if not isinstance(condition_dict, dict):
            continue
        
        conds, cond_params = _parse_conditions(condition_dict, table_prefix)
        if conds:
            if len(conds) > 1:
                or_conditions.append(f"({' AND '.join(conds)})")
            else:
                or_conditions.append(conds[0])
            or_params.extend(cond_params)
    
    or_clause = " OR ".join(or_conditions)
    return or_clause, or_params


def _parse_operator_condition(field, operator_dict):
    """Parse operator-based condition."""
    conditions = []
    params = []
    
    for operator, value in operator_dict.items():
        op_upper = operator.upper()
        
        if op_upper in [">", "<", ">=", "<=", "!=", "<>", "="]:
            conditions.append(f"{field} {op_upper} ?")
            params.append(value)
        
        elif op_upper == "LIKE":
            conditions.append(f"{field} LIKE ?")
            params.append(value)
        
        elif op_upper == "NOT LIKE":
            conditions.append(f"{field} NOT LIKE ?")
            params.append(value)
        
        elif op_upper == "IS" and value is None:
            conditions.append(f"{field} IS NULL")
        
        elif op_upper == "IS NOT" and value is None:
            conditions.append(f"{field} IS NOT NULL")
        
        elif op_upper == "BETWEEN":
            if isinstance(value, (list, tuple)) and len(value) == 2:
                conditions.append(f"{field} BETWEEN ? AND ?")
                params.extend(value)
        
        elif op_upper == "IN":
            if isinstance(value, list) and value:
                placeholders = ", ".join(["?"] * len(value))
                conditions.append(f"{field} IN ({placeholders})")
                params.extend(value)
        
        elif op_upper == "NOT IN":
            if isinstance(value, list) and value:
                placeholders = ", ".join(["?"] * len(value))
                conditions.append(f"{field} NOT IN ({placeholders})")
                params.extend(value)
        
        else:
            logger.warning("Unknown operator: %s", operator)
    
    condition = " AND ".join(conditions) if conditions else ""
    return condition, params


def build_where_with_tables(filters):
    """Legacy function for backward compatibility."""
    return build_where_clause(filters)

