# zCLI Documentation

**Version:** 1.3.0  
**Status:** Production Ready  
**Last Updated:** October 2, 2025

---

## 🚀 **Getting Started**

### **New to zCLI?**

1. **[INSTALL.md](INSTALL.md)** - Installation and setup
2. **[CRUD_GUIDE.md](CRUD_GUIDE.md)** - Complete CRUD operations guide
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and patterns

### **Quick Links**

- 📦 **Latest Release:** [v1.3.0](Releases/RELEASE_NOTES_v1.3.0.md)
- 🌈 **New Features:** UPSERT, Full ALTER TABLE, RGB System
- 📊 **All Releases:** [Releases/](Releases/)

---

## 📁 **Documentation Structure**

```
Documentation/
│
├── README.md              ← YOU ARE HERE
├── INSTALL.md             ← Installation guide
├── ARCHITECTURE.md        ← System architecture
├── CRUD_GUIDE.md          ← Main CRUD reference
│
├── Extras/                ← Detailed feature guides
│   ├── README.md          ← Feature guide index
│   ├── JOIN_GUIDE.md      ← JOIN operations
│   ├── WHERE_OPERATORS.md ← Advanced queries
│   ├── INDEX_GUIDE.md     ← Performance optimization
│   ├── VALIDATION_GUIDE.md← Data validation
│   ├── ON_DELETE_GUIDE.md ← Foreign key actions
│   ├── UPSERT_GUIDE.md    ← Insert-or-update (v1.3.0)
│   ├── ALTER_TABLE_GUIDE.md← Schema modifications (v1.3.0)
│   └── RGB_MIGRATION_IMPLEMENTATION.md← RGB system (v1.3.0)
│
├── Releases/              ← Version release notes
│   ├── README.md          ← Release index
│   ├── RELEASE_NOTES_v1.3.0.md
│   ├── GITHUB_RELEASE_v1.3.0.md
│   ├── ANNOUNCEMENT_v1.3.0.md
│   ├── RELEASE_CHECKLIST_v1.3.0.md
│   └── RELEASE_v1.2.0.md
│
└── WIP/                   ← Work in progress documents
    └── (internal development docs)
```

---

## 📖 **Core Documentation**

### **[INSTALL.md](INSTALL.md)**
Complete installation guide covering:
- Git SSH authentication
- Package installation
- Troubleshooting
- Verification steps

### **[ARCHITECTURE.md](ARCHITECTURE.md)**
System design documentation:
- Component architecture
- Database abstraction (zData pattern)
- Session management
- Plugin system
- Walker navigation

### **[CRUD_GUIDE.md](CRUD_GUIDE.md)**
Comprehensive CRUD operations guide:
- All CRUD operations (CREATE, READ, UPDATE, DELETE, UPSERT)
- Schema format and examples
- Quick start tutorials
- Best practices
- References to detailed guides in `Extras/`

---

## 🎯 **Feature Guides** (Extras/)

### **Essential Features**

**[JOIN_GUIDE.md](Extras/JOIN_GUIDE.md)**
- Auto-join based on foreign keys
- Manual JOIN specifications
- Nested relationships
- JOIN with WHERE clauses

**[VALIDATION_GUIDE.md](Extras/VALIDATION_GUIDE.md)**
- All validation rules
- Custom error messages
- Format presets (email, URL, phone)
- Required fields handling

**[ON_DELETE_GUIDE.md](Extras/ON_DELETE_GUIDE.md)**
- CASCADE - Delete children
- RESTRICT - Prevent deletion
- SET NULL - Nullify references
- SET DEFAULT - Use defaults
- NO ACTION - Deferred checks

### **Advanced Query Features** *(v1.2.0+)*

**[WHERE_OPERATORS.md](Extras/WHERE_OPERATORS.md)**
- Comparison operators: `<`, `>`, `<=`, `>=`, `!=`
- List operators: `IN`, `NOT IN`
- Pattern matching: `LIKE`, `NOT LIKE`
- NULL checks: `IS NULL`, `IS NOT NULL`
- OR conditions
- BETWEEN ranges

### **Performance** *(v1.3.0+)*

**[INDEX_GUIDE.md](Extras/INDEX_GUIDE.md)**
- Simple indexes
- Composite indexes
- Unique indexes
- Partial indexes (conditional)
- Expression indexes
- Performance best practices

### **Schema Management** *(v1.3.0+)*

**[UPSERT_GUIDE.md](Extras/UPSERT_GUIDE.md)**
- INSERT OR REPLACE syntax
- ON CONFLICT with selective updates
- Idempotent operations
- Session management patterns

**[ALTER_TABLE_GUIDE.md](Extras/ALTER_TABLE_GUIDE.md)**
- DROP COLUMN operations
- RENAME COLUMN operations
- RENAME TABLE operations
- Data preservation
- Migration history

**[RGB_MIGRATION_IMPLEMENTATION.md](Extras/RGB_MIGRATION_IMPLEMENTATION.md)**
- Quantum-inspired data integrity
- RGB weak nuclear force system
- Health analytics and reporting
- Migration impact tracking
- Intelligent suggestions

---

## 🔄 **Version-Specific Features**

### **v1.3.0 Features:**
- 📝 UPSERT operations → [UPSERT_GUIDE.md](Extras/UPSERT_GUIDE.md)
- 🔧 Full ALTER TABLE → [ALTER_TABLE_GUIDE.md](Extras/ALTER_TABLE_GUIDE.md)
- 📊 Index support → [INDEX_GUIDE.md](Extras/INDEX_GUIDE.md)
- 🌈 RGB system → [RGB_MIGRATION_IMPLEMENTATION.md](Extras/RGB_MIGRATION_IMPLEMENTATION.md)
- 📋 Migration history
- 🎯 Health analytics

### **v1.2.0 Features:**
- 🔑 Composite primary keys
- 🔍 Advanced WHERE operators → [WHERE_OPERATORS.md](Extras/WHERE_OPERATORS.md)
- 🔄 Automatic schema migration (ADD COLUMN)

### **v1.0.0 Features:**
- ✅ Basic CRUD operations
- 🔗 JOIN support → [JOIN_GUIDE.md](Extras/JOIN_GUIDE.md)
- ✅ Validation rules → [VALIDATION_GUIDE.md](Extras/VALIDATION_GUIDE.md)
- 🔑 Foreign keys → [ON_DELETE_GUIDE.md](Extras/ON_DELETE_GUIDE.md)

---

## 🎓 **Learning Paths**

### **Path 1: Basic CRUD User**
1. [INSTALL.md](INSTALL.md) - Setup
2. [CRUD_GUIDE.md](CRUD_GUIDE.md) - Basic operations
3. [VALIDATION_GUIDE.md](Extras/VALIDATION_GUIDE.md) - Data quality

### **Path 2: Application Developer**
1. [CRUD_GUIDE.md](CRUD_GUIDE.md) - All CRUD ops
2. [JOIN_GUIDE.md](Extras/JOIN_GUIDE.md) - Relationships
3. [WHERE_OPERATORS.md](Extras/WHERE_OPERATORS.md) - Complex queries
4. [ON_DELETE_GUIDE.md](Extras/ON_DELETE_GUIDE.md) - FK management

### **Path 3: Database Administrator**
1. [ARCHITECTURE.md](ARCHITECTURE.md) - System design
2. [INDEX_GUIDE.md](Extras/INDEX_GUIDE.md) - Performance
3. [ALTER_TABLE_GUIDE.md](Extras/ALTER_TABLE_GUIDE.md) - Schema changes
4. [RGB_MIGRATION_IMPLEMENTATION.md](Extras/RGB_MIGRATION_IMPLEMENTATION.md) - Health monitoring

### **Path 4: Advanced User**
1. [UPSERT_GUIDE.md](Extras/UPSERT_GUIDE.md) - Atomic operations
2. [RGB_MIGRATION_IMPLEMENTATION.md](Extras/RGB_MIGRATION_IMPLEMENTATION.md) - Data integrity
3. All advanced features

---

## 🔍 **Quick Search**

### **I want to...**

- **Install zCLI** → [INSTALL.md](INSTALL.md)
- **Learn CRUD basics** → [CRUD_GUIDE.md](CRUD_GUIDE.md)
- **Join tables** → [JOIN_GUIDE.md](Extras/JOIN_GUIDE.md)
- **Filter queries** → [WHERE_OPERATORS.md](Extras/WHERE_OPERATORS.md)
- **Validate data** → [VALIDATION_GUIDE.md](Extras/VALIDATION_GUIDE.md)
- **Optimize performance** → [INDEX_GUIDE.md](Extras/INDEX_GUIDE.md)
- **Handle deletions** → [ON_DELETE_GUIDE.md](Extras/ON_DELETE_GUIDE.md)
- **Insert or update** → [UPSERT_GUIDE.md](Extras/UPSERT_GUIDE.md)
- **Modify schema** → [ALTER_TABLE_GUIDE.md](Extras/ALTER_TABLE_GUIDE.md)
- **Monitor data health** → [RGB_MIGRATION_IMPLEMENTATION.md](Extras/RGB_MIGRATION_IMPLEMENTATION.md)
- **Understand architecture** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **See release notes** → [Releases/](Releases/)

---

## 📊 **Documentation Status**

| Category | Status | Coverage |
|----------|--------|----------|
| **Installation** | ✅ Complete | 100% |
| **Core CRUD** | ✅ Complete | 100% |
| **Advanced Features** | ✅ Complete | 100% |
| **Examples** | ✅ Complete | Extensive |
| **API Reference** | 🔜 Planned | - |
| **Video Tutorials** | 🔜 Planned | - |

---

## 🤝 **Contributing to Docs**

Documentation follows this structure:
- **Root:** High-level guides (INSTALL, ARCHITECTURE, CRUD_GUIDE)
- **Extras/:** Feature-specific deep dives
- **Releases/:** Version release documentation
- **WIP/:** Work-in-progress (internal use)

**Style Guide:**
- Use clear headings and sections
- Include code examples
- Add "See Also" cross-references
- Mark version-specific features
- Keep examples production-ready

---

## 📞 **Support**

- **Questions:** Check relevant guide first
- **Issues:** Review troubleshooting sections
- **Contact:** gal@zolo.media
- **Repository:** https://github.com/ZoloAi/zolo-zcli (private)

---

**zCLI v1.3.0 - Complete, Organized, Production-Ready Documentation** 📚

