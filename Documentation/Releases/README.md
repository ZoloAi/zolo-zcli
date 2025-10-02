# zCLI Release Notes

This folder contains release documentation for all versions of zCLI.

---

## 📦 **Latest Release**

**Current Version:** v1.3.0  
**Release Date:** October 2, 2025  
**Status:** Production Ready

**See:** [RELEASE_NOTES_v1.3.0.md](RELEASE_NOTES_v1.3.0.md)

---

## 📚 **Version History**

| Version | Date | Type | Key Features |
|---------|------|------|--------------|
| **[v1.3.0](RELEASE_NOTES_v1.3.0.md)** | Oct 2, 2025 | Major | UPSERT, Full ALTER TABLE, RGB System |
| **[v1.2.0](RELEASE_v1.2.0.md)** | Oct 1, 2025 | Major | Composite PKs, WHERE operators, Auto-migration |
| **v1.0.1** | Sep 30, 2025 | Patch | Bug fixes, documentation |
| **v1.0.0** | Sep 29, 2025 | Initial | Core CRUD, JOINs, Validation |

---

## 📄 **Release Documentation**

Each release includes:

- **RELEASE_NOTES_vX.X.X.md** - Complete technical documentation
- **GITHUB_RELEASE_vX.X.X.md** - GitHub release page content
- **ANNOUNCEMENT_vX.X.X.md** - User announcement template
- **RELEASE_CHECKLIST_vX.X.X.md** - Release process checklist

---

## 🚀 **Upgrade Guide**

### **To Latest Version (v1.3.0):**

```bash
pip install --upgrade git+ssh://git@github.com/ZoloAi/zolo-zcli.git@v1.3.0
```

**Breaking Changes:**
- v1.3.0 → None (100% backward compatible)
- v1.2.0 → None (100% backward compatible)

**Migration Notes:**
- New tables (`zMigrations`) created automatically
- RGB columns added to new tables only
- Existing databases continue working without changes

---

## 📊 **Release Metrics**

### v1.3.0 Statistics:
- **Features:** 4 major (UPSERT, ALTER TABLE, Migration History, RGB System)
- **Files Changed:** 15+
- **Lines Added:** 2000+
- **Test Coverage:** 100%
- **Breaking Changes:** 0

### v1.2.0 Statistics:
- **Features:** 3 major (Composite PKs, WHERE operators, Auto-migration)
- **Files Changed:** 10+
- **Lines Added:** 1500+
- **Test Coverage:** 100%
- **Breaking Changes:** 0

---

## 🔮 **Roadmap**

### **v1.4.0 (Planned):**
- ON UPDATE foreign key actions
- CHECK constraint support
- COLLATE support
- RGB decay scheduler

### **v2.0.0 (Future):**
- PostgreSQL support
- Triggers and views
- Generated columns
- Advanced data types (BLOB, JSON)

---

**Install the latest version today!** 🚀

