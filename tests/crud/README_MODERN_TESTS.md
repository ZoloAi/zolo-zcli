# Modern zData Test Suite

**Status:** ✅ Updated for v1.4.0+ architecture  
**Paradigm:** Classical data management  
**Adapters:** SQLite, CSV, PostgreSQL

---

## Overview

This directory contains modern test files for the current zData architecture, using:
- Classical paradigm handlers
- Shared operations (file-per-action pattern)
- Modern adapter system
- Schema-based validation
- Advanced WHERE clauses
- AUTO-JOIN and manual JOIN support

## Test Files

### `test_modern_zdata.py`
**Comprehensive CRUD tests across all adapters**

Tests:
- `test_sqlite_basic_crud()` - Basic INSERT, SELECT, UPDATE, DELETE
- `test_sqlite_advanced_where()` - OR, IN, IS NULL, comparison operators
- `test_sqlite_validation()` - Schema validation rules
- `test_sqlite_auto_join()` - AUTO-JOIN based on FK relationships
- `test_sqlite_upsert()` - UPSERT operation
- `test_csv_basic_crud()` - CSV adapter CRUD
- `test_csv_advanced_where()` - CSV WHERE clauses
- `test_multi_adapter_consistency()` - Ensures all adapters behave consistently

### `test_modern_joins.py`
**JOIN operation tests**

Tests:
- `test_auto_join_two_tables()` - AUTO-JOIN detection from FK
- `test_manual_join_inner()` - Manual INNER JOIN
- `test_manual_join_left()` - Manual LEFT JOIN
- `test_join_with_where()` - JOIN + WHERE combination
- `test_join_with_field_selection()` - JOIN with specific fields

### `test_modern_validation.py`
**Schema validation tests**

Tests:
- `test_required_field_validation()` - Required fields
- `test_min_length_validation()` - String min_length rule
- `test_max_length_validation()` - String max_length rule
- `test_email_format_validation()` - Email format validator
- `test_min_max_value_validation()` - Numeric range validation
- `test_update_validation()` - Validation on UPDATE operations
- `test_posts_validation()` - Validation on related tables

### `test_modern_where.py`
**Advanced WHERE clause tests**

Tests:
- `test_simple_equality()` - Basic = operator
- `test_or_conditions()` - $or conditions
- `test_in_operator()` - IN operator with lists
- `test_like_operator()` - LIKE pattern matching
- `test_is_null()` - IS NULL check
- `test_is_not_null()` - IS NOT NULL check
- `test_comparison_operators()` - >, >=, <, <=, !=
- `test_combined_conditions()` - Multiple conditions together

### `test_alias_and_wizard.py`
**Alias and wizard mode tests**

Tests:
- `test_alias_loading()` - load --as alias
- `test_data_command_with_alias()` - Using $alias in commands
- `test_wizard_persistent_connection()` - Connection reuse in wizard
- `test_wizard_transaction_rollback()` - Transaction management

---

## Running Tests

### Run all modern tests:
```bash
pytest tests/crud/test_modern_*.py -v
```

### Run specific test file:
```bash
pytest tests/crud/test_modern_zdata.py -v
```

### Run specific test:
```bash
pytest tests/crud/test_modern_zdata.py::test_sqlite_basic_crud -v
```

### Run with coverage:
```bash
pytest tests/crud/test_modern_*.py --cov=zCLI.subsystems.zData -v
```

---

## Test Data

All tests use schemas from `/zCLI/Schemas/`:
- `zSchema.sqlite_demo.yaml` - SQLite test schema
- `zSchema.csv_demo.yaml` - CSV test schema
- `zSchema.postgresql_demo.yaml` - PostgreSQL test schema

Each schema includes:
- **users** table with validation rules
- **posts** table with FK to users (for JOIN testing)
- **products** table for multi-table scenarios

---

## Deprecated Tests

The following test files use the old architecture and should NOT be used:
- `test_crud_with_fixtures.py` - Uses old infrastructure
- `test_direct_operations.py` - Uses deprecated operations folder
- `test_validation.py` - Uses old validation wrapper
- `test_join.py` - Uses old JOIN implementation
- All RGB-related tests - Moved to quantum/WIP

These files are kept in `/tests/archive/crud/` for reference.

---

## Architecture Notes

### Modern zData Flow:
```
zCLI → zData → ClassicalData → DataOperations → Adapter
                                     ↓
                            Individual operation handlers
                            (crud_insert, crud_read, etc.)
```

### Validation Flow:
```
DataOperations → DataValidator → Schema Rules → Adapter
```

### JOIN Flow:
```
select() → adapter.select() → _build_join_clause() → Auto or Manual JOIN
```

---

## Future Work

- Add PostgreSQL-specific tests (requires psycopg2)
- Add performance benchmarks
- Add quantum paradigm tests (when implemented)
- Add migration tests (quantum/WIP)

