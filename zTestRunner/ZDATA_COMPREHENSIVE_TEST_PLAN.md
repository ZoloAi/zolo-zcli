# zData Comprehensive Test Coverage Plan

## Current Status: 82/120+ Tests (68%) - Phase 1 & 2 Complete! ✅✅

### ✅ Already Covered (37 tests):
- **A. Initialization (3)**: Basic setup, dependencies, methods
- **B. SQLite CRUD (8)**: INSERT, SELECT, UPDATE, DELETE, basic filters
- **C. SQLite DDL (5)**: CREATE, DROP, ALTER, table_exists, list_tables
- **D. SQLite TCL (2)**: Transactions (commit), UPSERT
- **E. CSV Adapter (10)**: Basic CRUD operations
- **F. Error Handling (3)**: No adapter, invalid schema, table not found
- **G. Plugin Integration (6)**: UUID generation, timestamps
- **H. Connection Management (3)**: Status, disconnect, info

---

## ❌ MISSING TESTS (83+ tests needed):

### 1. VALIDATION TESTS (15 tests)
**Current**: Only basic validation in INSERT tests  
**Missing**:
- [ ] Test required field validation (comprehensive)
- [ ] Test type validation (str, int, float, bool, date)
- [ ] Test min/max length validation
- [ ] Test min/max value validation (numeric)
- [ ] Test email format validation
- [ ] Test pattern/regex validation
- [ ] Test unique constraint validation
- [ ] Test default values application
- [ ] Test NULL handling
- [ ] Test validation error messages
- [ ] Test INSERT vs UPDATE validation differences
- [ ] Test validation on complex data types
- [ ] Test validation hooks (pre-validation)
- [ ] Test validation bypass for trusted sources
- [ ] Test bulk validation performance

### 2. COMPLEX SELECT TESTS (12 tests)
**Current**: Basic WHERE, ORDER, LIMIT  
**Missing**:
- [ ] Test SELECT with JOINs (INNER, LEFT, RIGHT)
- [ ] Test SELECT with aggregations (COUNT, SUM, AVG, MIN, MAX)
- [ ] Test SELECT with GROUP BY
- [ ] Test SELECT with HAVING clause
- [ ] Test SELECT with subqueries
- [ ] Test SELECT with DISTINCT
- [ ] Test SELECT with OFFSET pagination
- [ ] Test SELECT with complex WHERE (AND, OR, NOT, IN, BETWEEN)
- [ ] Test SELECT with aliasing
- [ ] Test SELECT performance with large datasets
- [ ] Test SELECT with NULL handling
- [ ] Test SELECT with date/time functions

### 3. FOREIGN KEY TESTS (8 tests)
**Current**: Basic FK insert  
**Missing**:
- [ ] Test FK constraint validation
- [ ] Test CASCADE DELETE
- [ ] Test CASCADE UPDATE
- [ ] Test RESTRICT on delete
- [ ] Test SET NULL on delete
- [ ] Test circular FK references
- [ ] Test multi-column FK
- [ ] Test FK with JOINs

### 4. TRANSACTION TESTS (6 tests)
**Current**: Basic commit  
**Missing**:
- [ ] Test transaction rollback on error
- [ ] Test nested transactions (savepoints)
- [ ] Test transaction isolation levels
- [ ] Test deadlock handling
- [ ] Test long-running transactions
- [ ] Test wizard mode transaction persistence

### 5. WIZARD MODE TESTS (8 tests)
**Current**: None  
**Missing**:
- [ ] Test wizard mode connection reuse
- [ ] Test schema caching across operations
- [ ] Test wizard mode performance vs one-shot
- [ ] Test wizard mode cleanup
- [ ] Test wizard mode with multiple schemas
- [ ] Test wizard mode error recovery
- [ ] Test wizard mode state management
- [ ] Test wizard mode vs one-shot mode switching

### 6. UPSERT TESTS (5 tests)
**Current**: Basic upsert  
**Missing**:
- [ ] Test UPSERT with multiple conflict fields
- [ ] Test UPSERT with partial updates
- [ ] Test UPSERT performance
- [ ] Test UPSERT with validation
- [ ] Test UPSERT with hooks

### 7. ALTER TABLE TESTS (6 tests)
**Current**: Basic ADD COLUMN  
**Missing**:
- [ ] Test ALTER TABLE DROP COLUMN
- [ ] Test ALTER TABLE RENAME COLUMN
- [ ] Test ALTER TABLE MODIFY COLUMN (type change)
- [ ] Test ALTER TABLE with constraints
- [ ] Test ALTER TABLE with indexes
- [ ] Test ALTER TABLE with FK dependencies

### 8. HOOKS TESTS (8 tests)
**Current**: None  
**Missing**:
- [ ] Test onBeforeInsert hook
- [ ] Test onAfterInsert hook
- [ ] Test onBeforeUpdate hook
- [ ] Test onAfterUpdate hook
- [ ] Test onBeforeDelete hook
- [ ] Test onAfterDelete hook
- [ ] Test hook error handling
- [ ] Test hook chaining

### 9. zOPEN INTEGRATION TESTS (4 tests)
**Current**: None  
**Missing**:
- [ ] Test open_schema()
- [ ] Test open_csv()
- [ ] Test zPath resolution for schemas
- [ ] Test editor integration

### 10. MIGRATION TESTS (10 tests)
**Current**: None (but exist in old suite)  
**Missing**:
- [ ] Test schema_diff detection
- [ ] Test table additions
- [ ] Test table drops
- [ ] Test column additions
- [ ] Test column drops
- [ ] Test migration dry-run
- [ ] Test migration rollback
- [ ] Test migration history
- [ ] Test migration idempotency
- [ ] Test migration with data preservation

### 11. WHERE PARSER TESTS (5 tests)
**Current**: Basic WHERE  
**Missing**:
- [ ] Test complex WHERE parsing (AND, OR, NOT)
- [ ] Test WHERE with operators (=, !=, <, >, <=, >=, IN, LIKE, BETWEEN)
- [ ] Test WHERE with NULL handling
- [ ] Test WHERE with special characters
- [ ] Test WHERE parser error handling

### 12. VALUE PARSER TESTS (5 tests)
**Current**: None  
**Missing**:
- [ ] Test type conversion (str→int, str→float, str→bool, str→date)
- [ ] Test NULL parsing
- [ ] Test boolean parsing (true, false, 1, 0, yes, no)
- [ ] Test date parsing (ISO format, custom formats)
- [ ] Test value parser error handling

### 13. zDISPLAY INTEGRATION TESTS (4 tests)
**Current**: None  
**Missing**:
- [ ] Test AdvancedData.zTable() integration
- [ ] Test query result display
- [ ] Test pagination display
- [ ] Test mode-agnostic output (Terminal, Bifrost)

### 14. DATA EXPORT TESTS (5 tests)
**Current**: None  
**Missing**:
- [ ] Test export to CSV
- [ ] Test export to JSON
- [ ] Test export with filters
- [ ] Test export large datasets
- [ ] Test export with formatting

### 15. CSV ADVANCED TESTS (8 tests)
**Current**: Basic CSV CRUD  
**Missing**:
- [ ] Test CSV multi-table JOINs
- [ ] Test CSV DataFrame caching
- [ ] Test CSV with complex queries
- [ ] Test CSV performance with large files
- [ ] Test CSV file locking
- [ ] Test CSV encoding issues
- [ ] Test CSV with missing columns
- [ ] Test CSV data integrity

### 16. POSTGRESQL TESTS (12 tests - when psycopg2 available)
**Current**: Skipped  
**Missing**:
- [ ] Test PostgreSQL connection strings
- [ ] Test PostgreSQL-specific types (ARRAY, JSON, UUID)
- [ ] Test PostgreSQL-specific operations (RETURNING)
- [ ] Test PostgreSQL indexes
- [ ] Test PostgreSQL views
- [ ] Test PostgreSQL DCL (GRANT, REVOKE)
- [ ] Test PostgreSQL schemas (not tables)
- [ ] Test PostgreSQL sequences
- [ ] Test PostgreSQL triggers
- [ ] Test PostgreSQL stored procedures
- [ ] Test PostgreSQL full-text search
- [ ] Test PostgreSQL connection pooling

### 17. HEAD/DESCRIBE TESTS (3 tests)
**Current**: None  
**Missing**:
- [ ] Test head() table structure
- [ ] Test head() with metadata
- [ ] Test head() error handling

### 18. PERFORMANCE TESTS (5 tests)
**Current**: None  
**Missing**:
- [ ] Test bulk insert performance
- [ ] Test query performance with indexes
- [ ] Test connection pool performance
- [ ] Test cache hit rates
- [ ] Test memory usage with large datasets

---

## PRIORITY IMPLEMENTATION ORDER:

### Phase 1: Critical Missing Tests (20 tests) - HIGH PRIORITY
1. **Validation Tests** (5 most important):
   - Required field validation
   - Type validation
   - Min/max validation
   - Pattern validation
   - Default values

2. **Complex SELECT** (5 most important):
   - JOINs
   - Aggregations
   - GROUP BY
   - Complex WHERE
   - Subqueries

3. **Transaction Tests** (5 most important):
   - Rollback on error
   - Nested transactions
   - Wizard mode persistence
   - Error recovery
   - Isolation

4. **Wizard Mode** (5 most important):
   - Connection reuse
   - Schema caching
   - Performance comparison
   - State management
   - Cleanup

### Phase 2: Important Missing Tests (25 tests) - MEDIUM PRIORITY
5. **Foreign Keys** (8 tests)
6. **UPSERT** (5 tests)
7. **ALTER TABLE** (6 tests)
8. **WHERE Parser** (5 tests)

### Phase 3: Integration Tests (15 tests) - MEDIUM PRIORITY
9. **Hooks** (8 tests)
10. **zOpen Integration** (4 tests)
11. **zDisplay Integration** (4 tests)

### Phase 4: Advanced Tests (20 tests) - LOW PRIORITY
12. **Migrations** (10 tests)
13. **Data Export** (5 tests)
14. **Value Parser** (5 tests)

### Phase 5: Backend-Specific Tests (20 tests) - LOW PRIORITY
15. **CSV Advanced** (8 tests)
16. **PostgreSQL** (12 tests - conditional)

---

## TOTAL TARGET: 120+ Tests

**Current Coverage**: 37 tests (31%)  
**Target Coverage**: 120+ tests (100%)  
**Tests to Add**: 83+ tests

---

## NEXT STEPS:

1. ✅ **Review this plan** with user - COMPLETE
2. ✅ **Implement Phase 1** (Critical - 20 tests) - COMPLETE
3. ✅ **Implement Phase 2** (Important - 25 tests) - COMPLETE
4. ⏳ **Implement Phase 3** (Integration - 15 tests)
5. ⏳ **Implement Phase 4** (Advanced - 15 tests)
6. ⏳ **Implement Phase 5** (Performance - 8 tests)

---

## ESTIMATED TIME:
- Phase 1: ~2 hours (20 tests @ 6 min/test)
- Phase 2: ~2.5 hours (25 tests @ 6 min/test)
- Phase 3: ~1.5 hours (15 tests @ 6 min/test)
- Phase 4: ~2 hours (20 tests @ 6 min/test)
- Phase 5: ~2 hours (20 tests @ 6 min/test)

**Total**: ~10 hours to achieve 100% comprehensive coverage

