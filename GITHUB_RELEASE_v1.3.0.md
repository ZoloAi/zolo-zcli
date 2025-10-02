# zCLI v1.3.0 - Quantum Data Integrity Release 🌈

**Major feature release** introducing enterprise-grade schema management and revolutionary data health monitoring.

---

## 🚀 **Major Features**

### 1. **UPSERT Operation**
Atomic "insert or update if exists" functionality:
- Simple `INSERT OR REPLACE` syntax
- Advanced `ON CONFLICT DO UPDATE` with selective field updates
- Full validation and auto-field support
- Works with composite primary keys

### 2. **Migration History Tracking**
Complete audit trail of all schema changes:
- Ghost `zMigrations` table automatically tracks all migrations
- Records migration type, status, timestamps, and RGB impact
- Criticality levels for prioritization
- Full compliance and debugging support

### 3. **Full ALTER TABLE Support**
Complete schema modification capabilities:
- **DROP COLUMN** (with fallback for older SQLite)
- **RENAME COLUMN** (with fallback for older SQLite)
- **RENAME TABLE** (full support)
- Automatic migration history logging
- Data preservation guaranteed

### 4. **RGB Weak Nuclear Force System** *(BONUS)*
Revolutionary quantum-inspired data integrity monitoring:

#### **Automatic RGB Columns**
Every table now includes three special integrity columns:
- `weak_force_r` (Red): Time freshness (255=fresh, 0=ancient)
- `weak_force_g` (Green): Access frequency (255=popular, 0=unused)
- `weak_force_b` (Blue): Migration stability (255=stable, 0=unstable)

#### **Advanced Features**
- **Time-Based Decay**: Automatic aging simulation
- **Health Analytics**: Real-time data quality scoring
- **Intelligent Suggestions**: Automatic recommendations based on RGB values
- **Migration Integration**: RGB impact tracking for every schema change

---

## 📊 **What This Means**

Your databases now:
- ✅ Self-monitor their own health
- ✅ Track data freshness and usage patterns
- ✅ Predict maintenance needs
- ✅ Provide complete migration audit trails
- ✅ Support advanced CRUD operations

---

## 🔄 **Migration from v1.2.0**

**Breaking Changes:** None! 100% backward compatible.

**New Tables:**
- `zMigrations` - Automatically created on first use

**Schema Changes:**
- All new tables include RGB columns
- Existing tables continue working without changes

---

## 🧪 **Testing**

**Complete Test Suite Passing:**
```
Core Tests:  [PASS] ✅
CRUD Tests:  [PASS] ✅
  - 12 test suites
  - 3 new RGB phase tests
  - 100% feature coverage
```

---

## 📦 **Installation**

### **Via Git SSH:**
```bash
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git@v1.3.0
```

### **Update Existing Installation:**
```bash
pip install --upgrade git+ssh://git@github.com/ZoloAi/zolo-zcli.git@v1.3.0
```

---

## 📚 **Documentation**

- **Release Notes:** See `RELEASE_NOTES_v1.3.0.md` for complete details
- **RGB Implementation Guide:** See `Documentation/RGB_MIGRATION_IMPLEMENTATION.md`
- **CRUD Guide:** See `Documentation/CRUD_GUIDE.md`

---

## 🎯 **Quick Start with New Features**

### **UPSERT Example:**
```python
{
    "action": "upsert",
    "tables": ["zUsers"],
    "fields": ["id", "username", "email"],
    "values": ["user1", "john", "john@example.com"],
    "on_conflict": {
        "update_fields": ["email"]
    }
}
```

### **ALTER TABLE Example:**
```python
{
    "action": "alter_table",
    "table": "zUsers",
    "operation": "rename_column",
    "old_name": "username",
    "new_name": "user_name"
}
```

### **Check RGB Health:**
```python
from zCLI.subsystems.zMigrate import ZMigrate

migrator = ZMigrate()
health = migrator.get_rgb_health_report(zData)
suggestions = migrator.suggest_migrations_for_rgb_health(zData)
```

---

## 🌟 **Highlights**

> **"The world's first CRUD framework with quantum-inspired data integrity monitoring."**

- 🧠 Self-monitoring databases
- 🎯 Predictive data maintenance
- 📈 Automatic usage analytics
- 🔄 Complete migration control
- ⚡ Zero breaking changes

---

## 🙏 **What's Next**

**v1.4.0+ Roadmap:**
- RGB decay scheduler
- Automatic archiving
- Migration rollback
- Advanced analytics dashboard

---

**Full changelog available in `RELEASE_NOTES_v1.3.0.md`**

