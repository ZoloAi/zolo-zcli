# zVaFiles Guide

> **📌 Note:** This guide has been split into two user-friendly guides for easier learning!

---

## Quick Navigation

### 🎨 Building Menus and User Interfaces?
**→ See [zUI_GUIDE.md](zUI_GUIDE.md)**

Learn how to create interactive menus, forms, and user interfaces using simple YAML files. Perfect for beginners and high school students!

**Topics covered:**
- Creating menus with options
- Showing messages and information
- Collecting user input with forms
- Working with databases
- Multi-step processes
- Linking between pages

---

### 📊 Defining Data Structure?
**→ See [zSchema_GUIDE.md](zSchema_GUIDE.md)**

Learn how to define what information you want to store and what rules it must follow. Like creating a template for your data!

**Topics covered:**
- Field types (text, numbers, dates, etc.)
- Validation rules (required, unique, min/max)
- Auto-generated values
- Multiple choice options
- Connecting related data
- Database settings

---

## What are zVaFiles?

**zVaFiles** (short for "zVacuum Files") are YAML configuration files that power zCLI. There are two main types:

### 1. zUI Files - User Interfaces
Files that start with `zUI.` define menus and interactive experiences.

**Example:** `zUI.main_menu.yaml`

```yaml
zVaF:
  ~Root*: ["Option 1", "Option 2", "stop"]
  
  "Option 1":
    zDisplay:
      event: success
      content: "You selected option 1!"
```

**→ Full guide:** [zUI_GUIDE.md](zUI_GUIDE.md)

---

### 2. zSchema Files - Data Definitions
Files that start with `zSchema.` define the structure of your data.

**Example:** `zSchema.students.yaml`

```yaml
Students:
  id:
    type: string
    pk: true
    source: generate_id(STU)
  
  name:
    type: string
    required: true
  
  age:
    type: integer
    min: 5
    max: 18

Meta:
  Data_Type: sqlite
  Data_Path: zMachine.school_data
```

**→ Full guide:** [zSchema_GUIDE.md](zSchema_GUIDE.md)

---

## Why Two Types?

Think of it like building with LEGO:

- **zUI Files** = The instructions (what to build and how)
- **zSchema Files** = The pieces (what shapes and sizes you have)

You use them together:
1. **zSchema** defines what information you can store
2. **zUI** creates menus that let users work with that information

---

## How They Work Together

### Example: Student Management System

**Step 1 - Define the data (zSchema):**
```yaml
# zSchema.students.yaml
Students:
  id:
    type: string
    pk: true
  name:
    type: string
    required: true
  grade:
    type: integer
    min: 1
    max: 12

Meta:
  Data_Type: sqlite
  Data_Path: zMachine.students
```

**Step 2 - Create the interface (zUI):**
```yaml
# zUI.student_menu.yaml
zVaF:
  ~Root*: ["View Students", "Add Student", "stop"]
  
  "View Students":
    zData:
      action: read
      table: students
      limit: 10
  
  "Add Student":
    zDialog:
      model: "zSchema.students.Students"
      fields: ["name", "grade"]
```

The zUI file references the zSchema file to know what information to collect and how to validate it!

---

## File Naming Rules

### ✅ Correct Names:
```
zUI.main_menu.yaml      ✓
zUI.settings.yaml       ✓
zSchema.students.yaml   ✓
zSchema.products.yaml   ✓
```

### ❌ Incorrect Names:
```
ui.menu.yaml           ✗ (missing zUI prefix)
schema.students.yaml   ✗ (missing zSchema prefix)
students.yaml          ✗ (missing zSchema prefix)
menu.yaml              ✗ (missing zUI prefix)
```

**Remember:** 
- UI files → `zUI.name.yaml`
- Schema files → `zSchema.name.yaml`

---

## Quick Start

### New to zCLI?

1. **Start with zUI_GUIDE.md** - Learn to create your first menu
2. **Then read zSchema_GUIDE.md** - Learn to define your data
3. **Combine them** - Build your first application!

### Want to Build Something?

Try these starter projects (in order of difficulty):

#### 🟢 Beginner: Simple Calculator Menu
- **zUI only** - Create menu with math operations
- **Time:** 10-15 minutes
- **Guide:** [zUI_GUIDE.md - Exercise 1](zUI_GUIDE.md#exercise-1-simple-calculator-menu)

#### 🟡 Intermediate: Homework Tracker
- **zUI + zSchema** - Track assignments and due dates
- **Time:** 30-45 minutes
- **Guides:** [zUI_GUIDE.md](zUI_GUIDE.md#complete-example) + [zSchema_GUIDE.md](zSchema_GUIDE.md#example-1-homework-tracker)

#### 🔴 Advanced: Contact Manager
- **zUI + zSchema + Multiple Tables** - Manage contacts with categories
- **Time:** 1-2 hours
- **Guides:** Both full guides

---

## Path Resolution (zPath)

Both file types use **zPath** syntax to reference files:

```yaml
@.path.to.file.Section
```

**Examples:**
```yaml
# Reference a UI file
zLink: "@.zUI.settings_menu.zVaF"

# Reference a schema
model: "zSchema.students.Students"

# Reference a function
zFunc: "@.utils.save_data"
```

**Symbols:**
- `@` - Workspace-relative path (recommended)
- `~` - Absolute path
- `zMachine` - Machine-specific data directory

**→ Full details:** [zParser_GUIDE.md](zParser_GUIDE.md)

---

## Support File Extensions

All zVaFiles support these extensions:
- `.yaml` ✅ **(recommended)**
- `.yml` ✅
- `.json` ✅

**Recommendation:** Use `.yaml` for better readability.

---

## Complete Documentation

### For Developers

If you're comfortable with programming and want technical details:
- **Architecture:** [zWalker_GUIDE.md](zWalker_GUIDE.md)
- **Data Operations:** [zData_GUIDE.md](zData_GUIDE.md)
- **Path Resolution:** [zParser_GUIDE.md](zParser_GUIDE.md)
- **Plugin System:** [zPlugin_GUIDE.md](zPlugin_GUIDE.md)

### For Everyone Else

Start here and learn step-by-step:
1. **[zUI_GUIDE.md](zUI_GUIDE.md)** - Build menus (start here!)
2. **[zSchema_GUIDE.md](zSchema_GUIDE.md)** - Define data
3. Practice with the examples
4. Build your own projects!

---

## Getting Help

**Common Questions:**

**Q: Which guide do I read first?**  
A: Start with [zUI_GUIDE.md](zUI_GUIDE.md) - it's easier and you'll see results immediately!

**Q: Do I need to know programming?**  
A: Nope! These guides are written for beginners. If you can write a list and follow a recipe, you can use zCLI!

**Q: What's the difference between zUI and zSchema?**  
A: zUI creates menus (what users see), zSchema defines data (what you store).

**Q: Can I use just one type?**  
A: Yes! Start with zUI for simple menus. Add zSchema when you need to store data.

**Q: I'm getting errors. What do I do?**  
A: Check the "Common Mistakes" section in each guide - they show the most common errors and how to fix them!

---

## Version History

- **v1.4.0** - Split into zUI_GUIDE.md and zSchema_GUIDE.md for better usability
- **v1.3.0** - Original combined zVaFiles_GUIDE.md
- **v1.2.0** - Added schema validation and Meta section
- **v1.1.0** - Added zDialog and zWizard support
- **v1.0.0** - Initial release

---

**Ready to start?** Pick a guide and dive in! 🚀

- **→ [zUI_GUIDE.md](zUI_GUIDE.md)** - Create interactive menus
- **→ [zSchema_GUIDE.md](zSchema_GUIDE.md)** - Define data structure
