# zCLI CRUD Feature Guides

This folder contains detailed documentation for specific CRUD features and advanced capabilities.

---

## 📚 **Available Guides**

### **Core CRUD Features**

| Guide | Description | Version |
|-------|-------------|---------|
| **[JOIN_GUIDE.md](JOIN_GUIDE.md)** | Auto-join and manual join operations | v1.0.0+ |
| **[VALIDATION_GUIDE.md](VALIDATION_GUIDE.md)** | Field validation rules and custom messages | v1.0.0+ |
| **[ON_DELETE_GUIDE.md](ON_DELETE_GUIDE.md)** | Foreign key actions (CASCADE, SET NULL, etc.) | v1.0.0+ |

### **Advanced Query Features**

| Guide | Description | Version |
|-------|-------------|---------|
| **[WHERE_OPERATORS.md](WHERE_OPERATORS.md)** | Advanced query operators (OR, IN, LIKE, <, >) | v1.2.0+ |

### **Performance & Optimization**

| Guide | Description | Version |
|-------|-------------|---------|
| **[INDEX_GUIDE.md](INDEX_GUIDE.md)** | Index types, creation, and performance optimization | v1.3.0+ |

### **Schema Management** *(v1.3.0)*

| Guide | Description | Version |
|-------|-------------|---------|
| **[UPSERT_GUIDE.md](UPSERT_GUIDE.md)** | Insert-or-update operations with ON CONFLICT | v1.3.0+ |
| **[ALTER_TABLE_GUIDE.md](ALTER_TABLE_GUIDE.md)** | DROP/RENAME column and table operations | v1.3.0+ |
| **[RGB_MIGRATION_IMPLEMENTATION.md](RGB_MIGRATION_IMPLEMENTATION.md)** | Quantum-inspired data integrity system | v1.3.0+ |

---

## 🎯 **Quick Reference**

### **For Basic CRUD:**
Start with the main **[CRUD_GUIDE.md](../CRUD_GUIDE.md)**, then dive into specific features as needed.

### **For Relationships:**
1. [JOIN_GUIDE.md](JOIN_GUIDE.md) - Connect tables
2. [ON_DELETE_GUIDE.md](ON_DELETE_GUIDE.md) - Manage cascading deletes

### **For Queries:**
1. [WHERE_OPERATORS.md](WHERE_OPERATORS.md) - Filter records
2. [INDEX_GUIDE.md](INDEX_GUIDE.md) - Optimize performance

### **For Schema Changes:**
1. [ALTER_TABLE_GUIDE.md](ALTER_TABLE_GUIDE.md) - Modify structure
2. [RGB_MIGRATION_IMPLEMENTATION.md](RGB_MIGRATION_IMPLEMENTATION.md) - Track impact

### **For Data Quality:**
1. [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) - Validate input
2. [RGB_MIGRATION_IMPLEMENTATION.md](RGB_MIGRATION_IMPLEMENTATION.md) - Monitor health

---

## 🌟 **Feature Highlights**

### **What's New in v1.3.0:**

**🔧 ALTER TABLE Support:**
- DROP COLUMN, RENAME COLUMN, RENAME TABLE
- See: [ALTER_TABLE_GUIDE.md](ALTER_TABLE_GUIDE.md)

**📝 UPSERT Operations:**
- Atomic insert-or-update
- See: [UPSERT_GUIDE.md](UPSERT_GUIDE.md)

**📊 Index Management:**
- Simple, composite, unique, partial, expression indexes
- See: [INDEX_GUIDE.md](INDEX_GUIDE.md)

**🌈 RGB System:**
- Automatic data integrity monitoring
- See: [RGB_MIGRATION_IMPLEMENTATION.md](RGB_MIGRATION_IMPLEMENTATION.md)

---

## 📖 **Documentation Hierarchy**

```
Documentation/
├── INSTALL.md              ← Start here
├── ARCHITECTURE.md         ← System design
├── CRUD_GUIDE.md          ← Main CRUD reference
│
├── Extras/                ← YOU ARE HERE
│   ├── README.md          ← This file
│   ├── JOIN_GUIDE.md      ← Detailed JOIN docs
│   ├── WHERE_OPERATORS.md ← Query operators
│   ├── INDEX_GUIDE.md     ← Performance
│   ├── VALIDATION_GUIDE.md← Data validation
│   ├── ON_DELETE_GUIDE.md ← FK actions
│   ├── UPSERT_GUIDE.md    ← v1.3.0
│   ├── ALTER_TABLE_GUIDE.md← v1.3.0
│   └── RGB_MIGRATION_IMPLEMENTATION.md← v1.3.0
│
├── Releases/              ← Version history
│   ├── README.md
│   ├── RELEASE_NOTES_v1.3.0.md
│   ├── RELEASE_NOTES_v1.2.0.md
│   └── ...
│
└── WIP/                   ← Work in progress docs
```

---

## 🎓 **Learning Path**

1. **Beginners:** Start with [CRUD_GUIDE.md](../CRUD_GUIDE.md)
2. **Relationships:** Read [JOIN_GUIDE.md](JOIN_GUIDE.md) + [ON_DELETE_GUIDE.md](ON_DELETE_GUIDE.md)
3. **Queries:** Master [WHERE_OPERATORS.md](WHERE_OPERATORS.md)
4. **Performance:** Learn [INDEX_GUIDE.md](INDEX_GUIDE.md)
5. **Advanced:** Explore [RGB_MIGRATION_IMPLEMENTATION.md](RGB_MIGRATION_IMPLEMENTATION.md)

---

**All guides are production-tested and reflect zCLI v1.3.0 capabilities.** ✅

