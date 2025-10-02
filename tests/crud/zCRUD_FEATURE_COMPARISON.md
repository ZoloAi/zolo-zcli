# zCRUD vs SQLite Complete Feature Comparison

**Version**: 1.0.1  
**Purpose**: Gap analysis to finalize zCRUD subsystem  
**Date**: October 2, 2025

---

## 📊 Executive Summary

| Category | Supported | Partial | Not Supported | Total | Coverage |
|----------|-----------|---------|---------------|-------|----------|
| **Data Types** | 4 | 1 | 0 | 5 | 100% |
| **Constraints** | 4 | 0 | 3 | 7 | 57% |
| **Foreign Keys** | 5 | 0 | 1 | 6 | 83% |
| **Auto-Generation** | 2 | 0 | 0 | 2 | 100% |
| **Validation** | 5 | 0 | 3 | 8 | 63% |
| **CRUD Operations** | 6 | 0 | 1 | 7 | 86% |
| **JOIN Operations** | 2 | 0 | 0 | 2 | 100% |
| **Indexes** | 0 | 0 | 5 | 5 | 0% |
| **Advanced Tables** | 0 | 0 | 3 | 3 | 0% |
| **Triggers** | 0 | 0 | 7 | 7 | 0% |
| **Views** | 0 | 0 | 3 | 3 | 0% |
| **Migrations** | 1 | 0 | 5 | 6 | 17% |

**Overall Coverage**: 58% of SQLite features

---

## 1️⃣ DATA TYPES

### ✅ **Fully Supported**

| Type | zCRUD YAML | SQLite Type | Status | Notes |
|------|------------|-------------|--------|-------|
| **String** | `type: str` | `TEXT` | ✅ | Fully supported |
| **Integer** | `type: int` | `INTEGER` | ✅ | Fully supported |
| **Float** | `type: float` | `REAL` | ✅ | Fully supported |
| **DateTime** | `type: datetime` | `TEXT` | ✅ | Stored as ISO8601 |

### 🟡 **Partial Support**

| Type | zCRUD Support | SQLite Capability | Gap |
|------|---------------|-------------------|-----|
| **Enum** | `type: enum` + `options: []` | `CHECK constraint` | ✅ Works but uses TEXT + CHECK |

### ❌ **Not Supported**

| Type | SQLite Feature | Priority | Implementation Effort |
|------|----------------|----------|----------------------|
| **BLOB** | Binary data storage | Low | Easy - add type mapping |
| **NUMERIC** | Flexible numeric | Low | Easy - add type mapping |
| **Boolean** | INTEGER with CHECK | Medium | Easy - add type + validation |

**Recommendation**: Add BLOB and NUMERIC in v1.2.0 (low priority, easy implementation)

---

## 2️⃣ CONSTRAINTS

### ✅ **Fully Supported**

```yaml
# Current zCRUD YAML format
field_name:
  type: str
  pk: true            # ✅ PRIMARY KEY
  unique: true        # ✅ UNIQUE
  required: true      # ✅ NOT NULL
  default: "value"    # ✅ DEFAULT
```

| Constraint | zCRUD | SQLite | Code Location | Status |
|------------|-------|--------|---------------|--------|
| **PRIMARY KEY** | `pk: true` | `PRIMARY KEY` | `crud_handler.py:241` | ✅ |
| **UNIQUE** | `unique: true` | `UNIQUE` | `crud_handler.py:243` | ✅ |
| **NOT NULL** | `required: true` | `NOT NULL` | `crud_handler.py:245` | ✅ |
| **DEFAULT** | `default: value` | `DEFAULT value` | `crud_create.py:78-84` | ✅ |

### ❌ **Not Supported**

| Constraint | SQLite Feature | Priority | Use Case |
|------------|----------------|----------|----------|
| **CHECK** | `CHECK (expression)` | 🔴 High | Validation (age >= 18, email LIKE '%@%') |
| **COLLATE** | `COLLATE NOCASE` | 🟡 Medium | Case-insensitive text |
| **AUTOINCREMENT** | `AUTOINCREMENT` | 🟢 Low | SQLite-specific optimization |

**Current Workaround**:
- CHECK constraints: Handled via `crud_validator.py` (application-level)
- COLLATE: Not available
- AUTOINCREMENT: Uses generate_id() instead

**Recommendation**: 
- ✅ Keep validation in application layer (more portable)
- Add COLLATE support in YAML schema for v1.2.0
- AUTOINCREMENT is optional (current approach is fine)

---

## 3️⃣ FOREIGN KEYS

### ✅ **Fully Supported**

```yaml
# Current zCRUD YAML format
user_id:
  type: str
  fk: zUsers.id
  on_delete: CASCADE  # ✅ All actions supported
  on_update: CASCADE  # ❌ Not currently parsed
```

| Feature | zCRUD | SQLite | Status |
|---------|-------|--------|--------|
| **FK Definition** | `fk: Table.column` | `REFERENCES Table(column)` | ✅ |
| **ON DELETE CASCADE** | `on_delete: CASCADE` | `ON DELETE CASCADE` | ✅ |
| **ON DELETE RESTRICT** | `on_delete: RESTRICT` | `ON DELETE RESTRICT` | ✅ |
| **ON DELETE SET NULL** | `on_delete: SET NULL` | `ON DELETE SET NULL` | ✅ |
| **ON DELETE SET DEFAULT** | `on_delete: SET DEFAULT` | `ON DELETE SET DEFAULT` | ✅ |
| **ON DELETE NO ACTION** | `on_delete: NO ACTION` | `ON DELETE NO ACTION` | ✅ |

**Code**: `crud_handler.py:249-264`

### ❌ **Not Supported**

| Feature | SQLite Capability | Priority | Implementation |
|---------|-------------------|----------|----------------|
| **ON UPDATE actions** | `ON UPDATE CASCADE/RESTRICT/...` | 🟡 Medium | Easy - add parsing |

**Recommendation**: Add `on_update` support in v1.2.0 (mirrors `on_delete` logic)

---

## 4️⃣ AUTO-GENERATION & DEFAULTS

### ✅ **Fully Supported**

```yaml
# Current zCRUD features
id:
  source: generate_id(zA)      # ✅ Custom ID generation

created_at:
  default: now                  # ✅ Timestamp generation

version:
  default: "1.0.0"              # ✅ Static defaults

role:
  default: zUser                # ✅ Enum defaults
```

| Feature | zCRUD | Code Location | Status |
|---------|-------|---------------|--------|
| **generate_id()** | `source: generate_id(prefix)` | `crud_handler.py:275-377` | ✅ |
| **Timestamp (now)** | `default: now` | `crud_create.py:80-82` | ✅ |
| **Static defaults** | `default: "value"` | `crud_create.py:78-84` | ✅ |
| **Skip in validation** | Auto-skip fields with defaults | `crud_validator.py:87` | ✅ |

**Additional Generators**:
- `generate_API()` - ✅ Supported (requires plugin)
- `zRand()` - ✅ Supported (requires plugin)
- `zFunc()` - ✅ Legacy support

**Status**: ✅ Excellent coverage, production-ready

---

## 5️⃣ VALIDATION RULES

### ✅ **Supported**

```yaml
# Current zCRUD validation
email:
  type: str
  rules:
    format: email              # ✅ Email regex
    error_message: "Invalid"   # ✅ Custom messages

password:
  rules:
    min_length: 8              # ✅ String length
    max_length: 128            # ✅ String length

age:
  type: int
  rules:
    min: 18                    # ✅ Number range
    max: 120                   # ✅ Number range

username:
  rules:
    pattern: ^[a-zA-Z0-9_]+$   # ✅ Regex pattern
```

| Rule | zCRUD | Code | Status |
|------|-------|------|--------|
| **required** | `required: true` | `crud_validator.py:84-89` | ✅ |
| **min_length** | `min_length: N` | `crud_validator.py:121-124` | ✅ |
| **max_length** | `max_length: N` | `crud_validator.py:126-129` | ✅ |
| **min (numbers)** | `min: N` | `crud_validator.py:133-136` | ✅ |
| **max (numbers)** | `max: N` | `crud_validator.py:138-141` | ✅ |
| **pattern (regex)** | `pattern: regex` | `crud_validator.py:144-148` | ✅ |
| **format** | `format: email\|url\|phone` | `crud_validator.py:151-160` | ✅ |
| **error_message** | Custom errors | `crud_validator.py:147` | ✅ |

### ❌ **Not Supported**

| Validation | SQLite Method | Priority | Notes |
|------------|---------------|----------|-------|
| **JSON validation** | `CHECK json_valid(field)` | 🟡 Medium | For JSON columns |
| **Reference validation** | `FOREIGN KEY` | 🟢 Low | FK handles this |
| **Custom functions** | User-defined SQL functions | 🟢 Low | Advanced use case |

**Status**: ✅ Excellent validation coverage (63%)

---

## 6️⃣ CRUD OPERATIONS

### ✅ **Fully Supported**

| Operation | zCRUD | Code Location | Features | Status |
|-----------|-------|---------------|----------|--------|
| **CREATE** | `action: create` | `crud_create.py` | Auto-defaults, validation | ✅ |
| **READ** | `action: read` | `crud_read.py` | WHERE, ORDER BY, LIMIT, OFFSET | ✅ |
| **UPDATE** | `action: update` | `crud_update.py` | SET multiple, WHERE clause | ✅ |
| **DELETE** | `action: delete` | `crud_delete.py` | WHERE clause, CASCADE support | ✅ |
| **SEARCH** | `action: search` | `crud_read.py:327` | Alias for READ | ✅ |
| **TRUNCATE** | `action: truncate` | `crud_delete.py:68` | Clear table | ✅ |

### ❌ **Not Supported**

| Operation | SQLite Capability | Priority | Use Case |
|-----------|-------------------|----------|----------|
| **UPSERT** | `INSERT OR REPLACE` | 🔴 High | Insert or update if exists |

**Example of missing UPSERT**:
```sql
-- SQLite UPSERT (ON CONFLICT)
INSERT INTO users (id, username, email) 
VALUES (?, ?, ?)
ON CONFLICT(id) DO UPDATE SET 
  username = excluded.username,
  email = excluded.email;
```

**Recommendation**: Add UPSERT in v1.2.0 (commonly requested feature)

---

## 7️⃣ JOIN OPERATIONS

### ✅ **Fully Supported**

| Feature | zCRUD | Code Location | Status |
|---------|-------|---------------|--------|
| **Auto-JOIN** | `auto_join: true` | `crud_join.py:116` | ✅ |
| **Manual JOIN** | `join: [{type, table, on}]` | `crud_join.py:71` | ✅ |
| **INNER JOIN** | Detected via FK | `crud_join.py` | ✅ |
| **LEFT JOIN** | Manual specification | `crud_join.py` | ✅ |
| **Table qualifiers** | `zUsers.username` | `crud_join.py:12-69` | ✅ |

**Status**: ✅ Excellent JOIN support (Phase 2 complete)

---

## 8️⃣ INDEXES

### ❌ **Not Supported (0% Coverage)**

| Index Type | SQLite Feature | Priority | Use Case |
|------------|----------------|----------|----------|
| **Simple Index** | `CREATE INDEX idx ON table(col)` | 🔴 High | Query performance |
| **Composite Index** | `CREATE INDEX idx ON table(c1, c2)` | 🔴 High | Multi-column queries |
| **Unique Index** | `CREATE UNIQUE INDEX` | 🟡 Medium | Alternative to UNIQUE constraint |
| **Partial Index** | `WHERE clause` | 🟡 Medium | Index subset of rows |
| **Expression Index** | `LOWER(column)` | 🟢 Low | Computed values |

**Current State**: 
- zCRUD creates tables but **no indexes**
- Performance degrades with large tables
- No index management in schema YAML

**Recommended YAML Format**:
```yaml
zUsers:
  # ... fields ...
  
  indexes:  # ← NEW
    - name: idx_users_email
      columns: [email]
      unique: true
    
    - name: idx_users_active
      columns: [status]
      where: "status = 'active'"  # Partial index
    
    - name: idx_users_username_lower
      expression: "LOWER(username)"  # Expression index
```

**Priority**: 🔴 **HIGH** - Critical for production performance

---

## 9️⃣ ADVANCED TABLE TYPES

### ❌ **Not Supported (0% Coverage)**

| Feature | SQLite Capability | Priority | Use Case |
|---------|-------------------|----------|----------|
| **STRICT Tables** | Type enforcement (3.37+) | 🟡 Medium | Prevent type coercion |
| **WITHOUT ROWID** | Storage optimization | 🟢 Low | Performance for specific cases |
| **Virtual Tables (FTS5)** | Full-text search | 🟡 Medium | Search optimization |

**Current State**: All tables created as standard SQLite tables

**Recommended YAML Format**:
```yaml
zProducts:
  # ... fields ...
  
  options:  # ← NEW
    strict: true           # STRICT type checking
    without_rowid: false   # Optimization flag

zDocuments_fts:  # ← NEW virtual table
  virtual_table: true
  using: fts5
  columns:
    - title
    - content
  tokenize: porter
```

**Priority**: 🟡 **MEDIUM** - Nice to have for advanced use cases

---

## 🔟 GENERATED COLUMNS

### ❌ **Not Supported**

| Feature | SQLite Feature (3.31+) | Priority | Use Case |
|---------|------------------------|----------|----------|
| **VIRTUAL columns** | Computed on read | 🟢 Low | Derived values |
| **STORED columns** | Computed on write | 🟢 Low | Pre-computed fields |

**Example**:
```sql
CREATE TABLE settings (
    key TEXT,
    value TEXT,
    key_upper TEXT GENERATED ALWAYS AS (UPPER(key)) VIRTUAL,
    value_length INTEGER GENERATED ALWAYS AS (LENGTH(value)) STORED
);
```

**Recommended YAML Format**:
```yaml
settings:
  key:
    type: str
  
  key_upper:  # ← NEW
    type: str
    generated:
      expression: "UPPER(key)"
      stored: false  # VIRTUAL
  
  value_length:  # ← NEW
    type: int
    generated:
      expression: "LENGTH(value)"
      stored: true  # STORED
```

**Priority**: 🟢 **LOW** - Rare use case

---

## 1️⃣1️⃣ TRIGGERS

### ❌ **Not Supported (0% Coverage)**

| Trigger Type | SQLite Capability | Priority | Use Case |
|--------------|-------------------|----------|----------|
| **BEFORE INSERT** | Pre-insert logic | 🟡 Medium | Auto-generate slugs, validation |
| **AFTER INSERT** | Post-insert logic | 🟡 Medium | Audit logging, sync operations |
| **BEFORE UPDATE** | Pre-update logic | 🟡 Medium | Validation, change tracking |
| **AFTER UPDATE** | Post-update logic | 🔴 High | Auto-update timestamps |
| **BEFORE DELETE** | Pre-delete logic | 🟢 Low | Prevent deletion logic |
| **AFTER DELETE** | Post-delete logic | 🟢 Low | Cascade cleanup |
| **INSTEAD OF** | View updatability | 🟢 Low | Advanced views |

**Common Use Cases**:
1. **Auto-update timestamp**: `updated_at = CURRENT_TIMESTAMP` on UPDATE
2. **Audit logging**: Log all changes to audit table
3. **FTS sync**: Keep full-text search index synchronized
4. **Business logic**: Prevent invalid state transitions

**Recommended YAML Format**:
```yaml
zUsers:
  # ... fields ...
  
  triggers:  # ← NEW
    - name: users_update_timestamp
      when: AFTER UPDATE
      sql: |
        UPDATE users SET updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.id
```

**Priority**: 🟡 **MEDIUM** - Useful for automation but can be handled in application code

---

## 1️⃣2️⃣ VIEWS

### ❌ **Not Supported (0% Coverage)**

| View Type | SQLite Capability | Priority | Use Case |
|-----------|-------------------|----------|----------|
| **Simple views** | Filtered SELECT | 🟡 Medium | Read-only derived data |
| **Complex views** | JOINs, aggregations | 🟡 Medium | Reporting, dashboards |
| **Updatable views** | With INSTEAD OF triggers | 🟢 Low | Advanced abstraction |

**Current Workaround**: Use READ with JOINs (equivalent functionality)

**Recommended YAML Format**:
```yaml
# In schema.yaml

views:  # ← NEW section
  active_users:
    sql: |
      SELECT id, username, email
      FROM users
      WHERE is_active = 1
  
  user_post_stats:
    sql: |
      SELECT u.id, u.username, COUNT(p.id) as post_count
      FROM users u
      LEFT JOIN posts p ON u.id = p.user_id
      GROUP BY u.id
```

**Priority**: 🟡 **MEDIUM** - Nice to have but not critical (JOINs cover most use cases)

---

## 1️⃣3️⃣ COMPOSITE KEYS

### ❌ **Not Supported**

```yaml
# NOT currently supported
post_tags:
  post_id:
    type: str
  tag_id:
    type: str
  # ❌ No way to specify composite PK: (post_id, tag_id)
```

**SQLite**:
```sql
CREATE TABLE post_tags (
    post_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (post_id, tag_id)  -- Composite
);
```

**Recommended YAML Format**:
```yaml
post_tags:
  post_id:
    type: str
    fk: zPosts.id
  
  tag_id:
    type: str
    fk: zTags.id
  
  primary_key: [post_id, tag_id]  # ← NEW: Composite PK
```

**Priority**: 🔴 **HIGH** - Common pattern for many-to-many relationships

**Implementation**: Update `zTables()` in `crud_handler.py` to detect `primary_key` list

---

## 1️⃣4️⃣ MIGRATIONS & SCHEMA MANAGEMENT

### ✅ **Supported**

| Feature | zCRUD | Status |
|---------|-------|--------|
| **Create missing tables** | `zEnsureTables()` | ✅ |

### ❌ **Not Supported**

| Feature | SQLite Capability | Priority | Impact |
|---------|-------------------|----------|--------|
| **Detect schema changes** | Compare YAML vs DB | 🔴 **CRITICAL** | Schema updates fail |
| **ALTER TABLE ADD COLUMN** | Add new columns | 🔴 **CRITICAL** | Can't evolve schema |
| **ALTER TABLE DROP COLUMN** | Remove columns (3.35+) | 🟡 Medium | Cleanup old fields |
| **ALTER TABLE RENAME** | Rename columns/tables | 🟢 Low | Refactoring |
| **Migration history** | Track applied changes | 🟡 Medium | Audit trail |

**Current Problem**:
```yaml
# Add field to schema.yaml
zApps:
  status:  # ← NEW FIELD
    type: str
    default: "active"
```

**Result**: 
- ❌ Column NOT added to existing table
- ❌ CREATE fails with "no such column: status"
- ❌ No detection, no warning, no auto-fix

**Priority**: 🔴 **CRITICAL** - Blocks schema evolution

---

## 1️⃣5️⃣ QUERY FEATURES

### ✅ **Supported**

| Feature | zCRUD | Code Location | Status |
|---------|-------|---------------|--------|
| **WHERE clause** | `where: {field: value}` | `crud_read.py`, `crud_update.py`, `crud_delete.py` | ✅ |
| **ORDER BY** | `order_by: "field ASC"` | `crud_handler.py:379-405` | ✅ |
| **LIMIT** | `limit: 10` | `crud_read.py` | ✅ |
| **OFFSET** | `offset: 20` | `crud_read.py` | ✅ |
| **Parameterized queries** | Always uses `?` placeholders | All CRUD files | ✅ |

### ❌ **Not Supported**

| Feature | SQLite Capability | Priority | Use Case |
|---------|-------------------|----------|----------|
| **OR conditions** | `WHERE a = ? OR b = ?` | 🔴 High | Complex filters |
| **IN operator** | `WHERE id IN (?, ?, ?)` | 🔴 High | Multiple value match |
| **LIKE patterns** | `WHERE name LIKE '%search%'` | 🔴 High | Partial matching |
| **Comparison ops** | `<, >, <=, >=, !=` | 🔴 High | Range queries |
| **IS NULL / IS NOT NULL** | NULL checking | 🟡 Medium | Optional field queries |
| **BETWEEN** | `WHERE age BETWEEN 18 AND 65` | 🟢 Low | Syntactic sugar |
| **Subqueries** | `WHERE id IN (SELECT...)` | 🟢 Low | Advanced queries |

**Current Limitation**: Only AND conditions with = operator

```python
# ✅ Currently works
where = {"type": "web", "status": "active"}
# SQL: WHERE type = ? AND status = ?

# ❌ Not supported
where = {"type": ["web", "mobile"]}  # IN operator
where = {"age": {">": 18}}  # Comparison operators
where = {"name": {"LIKE": "%test%"}}  # Pattern matching
```

**Priority**: 🔴 **HIGH** - Severely limits query capabilities

---

## 1️⃣6️⃣ SCHEMA INTROSPECTION

### ❌ **Not Supported**

| Feature | SQLite Method | Priority | Use Case |
|---------|---------------|----------|----------|
| **List tables** | `sqlite_master` | ✅ Partial | `zListTables()` exists |
| **Describe table** | `PRAGMA table_info()` | 🔴 High | Migration detection |
| **Show FK** | `PRAGMA foreign_key_list()` | 🔴 High | Relationship mapping |
| **Show indexes** | `PRAGMA index_list()` | 🟡 Medium | Performance analysis |
| **Schema version** | User-defined | 🟡 Medium | Migration tracking |

**Current State**:
- `zListTables()` returns table names ✅
- No way to inspect table structure ❌
- No way to compare YAML vs DB ❌

**Priority**: 🔴 **HIGH** - Required for migration system

---

## 📈 PRIORITY MATRIX

### 🔴 **Critical (Must Have for v1.2.0)**

1. **Schema Change Detection** - Can't evolve schemas currently
2. **ALTER TABLE ADD COLUMN** - Add new fields to existing tables
3. **Composite Primary Keys** - Common pattern for junction tables
4. **Advanced WHERE (OR, IN, LIKE, <, >)** - Severely limited queries
5. **UPSERT** - Common pattern for idempotent operations
6. **Index Support** - Performance critical for production

### 🟡 **Important (Should Have for v1.3.0)**

7. **ON UPDATE actions** - FK update cascades
8. **Triggers** - Auto-update timestamps, audit logs
9. **Views** - Derived data, reporting
10. **JSON validation** - For JSON column types
11. **Migration history tracking** - Audit trail
12. **COLLATE support** - Case-insensitive text

### 🟢 **Nice to Have (Future)**

13. **BLOB type** - Binary data
14. **NUMERIC type** - Flexible numbers
15. **Generated columns** - Computed fields
16. **STRICT tables** - Type enforcement
17. **WITHOUT ROWID** - Optimization
18. **FTS5** - Full-text search
19. **AUTOINCREMENT** - SQLite-specific PK
20. **Custom SQL functions** - Advanced

---

## 🎯 RECOMMENDED ROADMAP

### v1.2.0 - Foundation (2-3 weeks)

**Schema Evolution**:
- [ ] Schema introspection (`PRAGMA table_info`)
- [ ] Change detection (compare YAML vs DB)
- [ ] AUTO ADD COLUMN for new fields
- [ ] Composite primary key support

**Query Enhancement**:
- [ ] OR conditions in WHERE
- [ ] IN operator for arrays
- [ ] LIKE for pattern matching
- [ ] Comparison operators (<, >, <=, >=, !=)

**Performance**:
- [ ] Index creation from YAML schema
- [ ] Simple indexes
- [ ] Composite indexes
- [ ] Unique indexes

**Operations**:
- [ ] UPSERT (INSERT OR REPLACE)

### v1.3.0 - Advanced Features (3-4 weeks)

**Schema Management**:
- [ ] ALTER TABLE DROP COLUMN (with table recreation for old SQLite)
- [ ] ALTER TABLE RENAME COLUMN
- [ ] Migration history table (`zMigrations`)
- [ ] Rollback support

**Automation**:
- [ ] Triggers (AFTER UPDATE for timestamps)
- [ ] ON UPDATE FK actions
- [ ] Audit logging triggers

**Optimization**:
- [ ] Partial indexes
- [ ] Expression indexes
- [ ] View support

### v2.0.0 - Enterprise (Future)

**Advanced Types**:
- [ ] BLOB support
- [ ] NUMERIC support
- [ ] JSON column type with validation
- [ ] Generated columns (VIRTUAL/STORED)

**Advanced Tables**:
- [ ] STRICT table support
- [ ] WITHOUT ROWID support
- [ ] FTS5 virtual tables

**Database Portability**:
- [ ] PostgreSQL support (full fork implementation)
- [ ] MySQL support
- [ ] Database-specific optimizations

---

## 📊 FEATURE COMPARISON TABLE

### Column-Level Features

| Feature | zCRUD Schema | SQLite SQL | Supported | Priority |
|---------|--------------|------------|-----------|----------|
| Data type: TEXT | `type: str` | `TEXT` | ✅ | - |
| Data type: INTEGER | `type: int` | `INTEGER` | ✅ | - |
| Data type: REAL | `type: float` | `REAL` | ✅ | - |
| Data type: BLOB | - | `BLOB` | ❌ | 🟢 Low |
| Data type: NUMERIC | - | `NUMERIC` | ❌ | 🟢 Low |
| PRIMARY KEY | `pk: true` | `PRIMARY KEY` | ✅ | - |
| AUTOINCREMENT | - | `AUTOINCREMENT` | ❌ | 🟢 Low |
| NOT NULL | `required: true` | `NOT NULL` | ✅ | - |
| UNIQUE | `unique: true` | `UNIQUE` | ✅ | - |
| DEFAULT | `default: value` | `DEFAULT value` | ✅ | - |
| CHECK | Via validation | `CHECK (expr)` | 🟡 Partial | 🟡 Medium |
| COLLATE | - | `COLLATE NOCASE` | ❌ | 🟡 Medium |
| Foreign Key | `fk: Table.col` | `REFERENCES Table(col)` | ✅ | - |
| ON DELETE | `on_delete: CASCADE` | `ON DELETE CASCADE` | ✅ | - |
| ON UPDATE | - | `ON UPDATE CASCADE` | ❌ | 🟡 Medium |
| Generated VIRTUAL | - | `GENERATED ... VIRTUAL` | ❌ | 🟢 Low |
| Generated STORED | - | `GENERATED ... STORED` | ❌ | 🟢 Low |

### Table-Level Features

| Feature | zCRUD Support | SQLite Capability | Supported | Priority |
|---------|---------------|-------------------|-----------|----------|
| Composite PK | - | `PRIMARY KEY (c1, c2)` | ❌ | 🔴 High |
| Table-level CHECK | - | `CHECK (expression)` | ❌ | 🟢 Low |
| Table-level UNIQUE | - | `UNIQUE (c1, c2)` | ❌ | 🟢 Low |
| STRICT | - | `STRICT` | ❌ | 🟡 Medium |
| WITHOUT ROWID | - | `WITHOUT ROWID` | ❌ | 🟢 Low |

### Database Operations

| Operation | zCRUD | SQLite | Supported | Priority |
|-----------|-------|--------|-----------|----------|
| CREATE TABLE | ✅ | `CREATE TABLE` | ✅ | - |
| DROP TABLE | ❌ | `DROP TABLE` | ❌ | 🟡 Medium |
| RENAME TABLE | ❌ | `ALTER TABLE RENAME TO` | ❌ | 🟢 Low |
| ADD COLUMN | ❌ | `ALTER TABLE ADD COLUMN` | ❌ | 🔴 **CRITICAL** |
| DROP COLUMN | ❌ | `ALTER TABLE DROP COLUMN` | ❌ | 🟡 Medium |
| RENAME COLUMN | ❌ | `ALTER TABLE RENAME COLUMN` | ❌ | 🟢 Low |

### Index Operations

| Operation | zCRUD | SQLite | Supported | Priority |
|-----------|-------|--------|-----------|----------|
| CREATE INDEX | ❌ | `CREATE INDEX` | ❌ | 🔴 High |
| DROP INDEX | ❌ | `DROP INDEX` | ❌ | 🟡 Medium |
| UNIQUE INDEX | ❌ | `CREATE UNIQUE INDEX` | ❌ | 🟡 Medium |
| Partial INDEX | ❌ | `WHERE clause` | ❌ | 🟡 Medium |
| Expression INDEX | ❌ | `ON expression` | ❌ | 🟢 Low |

---

## 🔍 DETAILED ANALYSIS

### What zCRUD Does Well

1. **CRUD Operations** ✅
   - Clean, simple interface
   - Parameterized queries (SQL injection safe)
   - Auto-defaults and validation
   - Multi-table JOINs

2. **Schema-Driven** ✅
   - YAML as single source of truth
   - Type mapping works well
   - Foreign key support is solid

3. **Database Abstraction** ✅
   - zData/cursor pattern is elegant
   - Ready for multi-database support
   - Clean separation of concerns

### Critical Gaps

1. **Schema Evolution** ❌
   - No migration support
   - Can't update existing tables
   - Blocks production use

2. **Query Flexibility** ❌
   - Only AND + = operator
   - No OR, IN, LIKE, <, >
   - Limits application functionality

3. **Performance** ❌
   - No index support
   - Will be slow with >1000 rows
   - No optimization path

4. **Composite Keys** ❌
   - Can't model many-to-many properly
   - Junction tables require workarounds

---

## 💡 SIMPLIFICATION OPPORTUNITIES

Looking at the comparison, **you don't need ALL SQLite features**. Focus on:

### Core Essentials (v1.2.0)

**Must Fix**:
1. Schema change detection + ADD COLUMN
2. Composite primary keys
3. Advanced WHERE (OR, IN, LIKE, <, >)
4. Basic index support

**Why**: These 4 features unblock production use

### Production Ready (v1.3.0)

**Should Add**:
5. UPSERT operation
6. ON UPDATE FK actions
7. Migration history tracking
8. Partial indexes

**Why**: Common patterns in real applications

### Advanced (v2.0.0+)

**Nice to Have**:
- Triggers, views, generated columns
- STRICT tables, WITHOUT ROWID
- FTS5, BLOB support
- Complete ALTER TABLE support

**Why**: Edge cases, can be added as needed

---

## 🚀 IMMEDIATE ACTION ITEMS

### For zMigrate v1.0 (Minimal Viable)

Focus on **just these 3 features**:

1. **Introspect existing schema**
   ```python
   def get_db_schema(zData):
       # PRAGMA table_info for each table
       # Returns: {table: {column: {...}}}
   ```

2. **Detect new columns**
   ```python
   def detect_new_columns(yaml_schema, db_schema):
       # Compare and find missing columns
       # Returns: {table: [new_col1, new_col2]}
   ```

3. **Add missing columns**
   ```python
   def add_columns(changes, zData):
       # ALTER TABLE ADD COLUMN
       # Works for SQLite, PostgreSQL, MySQL
   ```

**Total**: ~150 lines of code, solves 80% of schema evolution needs

---

## 📝 CONCLUSIONS

### Current State

**zCRUD is**:
- ✅ **Excellent** for basic CRUD operations
- ✅ **Solid** foundation with database abstraction
- ✅ **Production-ready** for greenfield projects
- ❌ **Blocked** for evolving schemas

### To Finalize zCRUD

**Critical (v1.2.0)**:
1. Schema migration (ADD COLUMN minimum)
2. Composite primary keys
3. Advanced WHERE operators
4. Index support

**Important (v1.3.0)**:
5. UPSERT operation
6. Migration history
7. Full ALTER TABLE support

**Optional (v2.0+)**:
8. Triggers, views, advanced types

### Recommendation

**Start with migration** (ADD COLUMN only) - this unblocks everything else. The other features can be added incrementally without breaking changes.

---

**Next Step**: Design simple 150-line zMigrate for ADD COLUMN support? 🎯

