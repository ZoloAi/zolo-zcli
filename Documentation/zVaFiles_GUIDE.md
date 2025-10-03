# zVaFiles Guide

## Introduction

**zVaFiles** (zVacuum Files) are YAML/JSON configuration files that serve as the foundation for `zolo-zcli`'s universal framework. They define both user interface structures and data models, enabling rapid development of applications through configuration-driven architecture.

> **Note:** zVaFiles are the core building blocks that power zWalker's interactive experiences and zCRUD's database operations. 

## zVaFile Types

`zolo-zcli` recognizes two primary zVaFile types based on their filename prefixes:

### UI zVaFiles (ui.*)
- **Purpose:** Define interactive user interfaces, navigation structures, and automated workflows for `zWalker`
- **Naming:** Must start with `ui.` (e.g., `ui.manual.yaml`, `ui.dashboard.yaml`)
- **Usage:** Power `zWalker`'s menu systems, forms, interactive experiences, and automated function sequences

### Schema zVaFiles (schema.*)
- **Purpose:** Define data models and validation structures for both `zCRUD` operations and `zDialog` form validation
- **Naming:** Must start with `schema.` (e.g., `schema.users.yaml`, `schema.products.yaml`)
- **Usage:** Enable database operations, form validation, data manipulation, and interactive form handling

## File Structure & Naming

### Naming Convention:
```
ui.{name}.yaml          # UI interface files
schema.{name}.yaml      # Data model files
```

### Supported Extensions:
- `.yaml` **(recommended)**
- `.yml`
- `.json`

## zPath Resolution

zVaFiles use zPath syntax for referencing and loading:

### Path Structure:
```
@.path.to.{type}.{name}.{zBlock}
```

### Examples:
```yaml
# UI files
@.Zolo.ui.manual.Root          # → ui.manual.yaml (Root block)
@.Zolo.ui.dashboard.Main       # → ui.dashboard.yaml (Main block)

# Schema files  
@.Zolo.schema.users.Users      # → schema.users.yaml (Users table)
@.Zolo.schema.products.Items   # → schema.products.yaml (Items table)
```

> **Note:** For complete zPath documentation, see [zParser_GUIDE.md](/Documentation/zParser_GUIDE.md)

## UI zVaFiles

UI zVaFiles define interactive interfaces using **zBlocks** and **zKeys**.

### What is a zBlock?
A **zBlock** is a named section within a UI zVaFile that groups related zKeys together. Every UI zVaFile must have at least one zBlock, typically named `zVaF` as the root block.

**Flow:** zKeys within a zBlock are processed sequentially from top to bottom.

### Structure:
```yaml
# ui.example.yaml
zVaF:                                   # ← This is a zBlock
  item_1: "zFunc(@.path.to.function)"       # ← These are zKeys
  item_2: "zLink(@.path.to.other.ui.block)" # ← These are zKeys
  item_3: "zDialog(...)"                    # ← These are zKeys
```

**Isolation:** zBlocks are isolated within a UI zVaFile. If zWalker is assigned to zBlock A, it will NOT automatically move to zBlock B - you must explicitly navigate using delta links (`$`) or external links.

## zKeys

**zKeys** are individual menu items, functions, actions, or values within a zBlock.

### zMenu:
Menus create interactive numbered lists for user selection:

**Requirements:**
- **Menu suffix:** Must end with `*` (e.g., `Root*`, `Settings*`)
- **Array format:** Menu items must be in array format `["item1", "item2"]`
- **Exact matching:** Menu item names must exactly match zKey names (including modifiers)
- **Anchor mode:** Use `~` prefix on menu zKeys (ending with `*`) to prevent auto-generation of zBack
- **Delta links:** Use `$` prefix to switch between zBlocks in same file

```yaml
# ui.example.yaml
zVaF:
  Root*: ["option1", "option2", "$other_block"]  # ← Regular menu
  ~Settings*: ["setting1", "setting2"]  # ← Anchor menu (no auto zBack)
  option1: "zFunc(@.path.to.function)"
  option2: "zLink(@.path.to.other.ui.block)"
  setting1: "zFunc(@.path.to.setting.function)"
  setting2: "zLink(@.path.to.other.block)"
  
other_block:                         # ← Another zBlock (delta link target)
  Settings*: ["setting1", "setting2", "$zVaF"]  # ← Delta link back to root
    setting1: "zFunc(@.path.to.settings.function)"
    setting2: "zLink(@.path.to.other.block)"
```

### zLink:
Navigates to other UI zVaFiles or zBlocks within the same file. Enables modular UI design and cross-file navigation.

**Syntax:**
```yaml
zKey_name: "zLink(@.path.to.ui.file.zBlock)"  # Workspace-relative
zKey_name: "zLink(~.path.to.ui.file.zBlock)"  # Absolute path
```

**Examples:**
```yaml
# ui.example.yaml
zVaF:
  Navigation:
    local_users: "zLink(@.ui.users.List)"        # Relative to zWorkspace
    absolute_admin: "zLink(~.admin.ui.dashboard)" # Absolute path
    local_products: "zLink(@.ui.products.Catalog)"
```

**Key Points:**
- **External navigation:** Links to other UI zVaFiles and specific zBlocks
- **Cross-file design:** Enables modular UI architecture
- **Path resolution:** Uses zPath syntax for file and block targeting
- **Path prefixes:** `@` for workspace-relative paths, `~` for absolute paths
- **Optional permissions:** Can include permission checks for secure navigation
- **Return navigation:** Use `zBack` or link back to parent UI

### zOpen:
Opens files and URLs with intelligent fallbacks based on machine capabilities and environment detection.

**Syntax:**
```yaml
zKey_name: "zOpen(path_or_url)"
```

**Examples:**
```yaml
# URL opening (intelligent fallbacks)
OpenWebsite: "zOpen(https://example.com)"

# Local file opening
OpenReadme: "zOpen(/path/to/readme.txt)"
OpenHTML: "zOpen(/path/to/index.html)"

# zPath opening
OpenManual: "zOpen(@.docs.manual.html)"
OpenConfig: "zOpen(@.config.settings.yaml)"
```

**Key Points:**
- **Intelligent URL handling:** Uses browser if available, falls back to curl on headless systems
- **File type detection:** Automatically routes HTML files to browser, text files to editor
- **zPath integration:** Supports workspace-relative (`@`) and absolute (`~`) paths
- **Machine capability aware:** Uses streamlined capabilities (browser, imports, default_text_editor)
- **Environment detection:** Different behavior for GUI vs headless systems
- **Graceful fallbacks:** Displays content or URL info when opening fails
- **Universal support:** Works across all platforms (Windows, macOS, Linux)

### zFunc:
Executes Python functions directly within a zKey. Used for calling specific functions without user interaction.

**Bounce prefix (`^`):** Execute function and return to parent menu (useful for quick actions)

**Syntax:**
```yaml
zKey_name: "zFunc(@.path.to.file.function_name, args)"
```

**Examples:**
```yaml
# ui.example.yaml
zVaF:
  Actions:
    save_data: "zFunc(@.utils.data.save, {table: 'users'})"
    generate_report: "zFunc(@.reports.generate_summary)"
    cleanup: "zFunc(@.utils.cleanup_temp_files)"
    
  Menu*: ["save_data", "generate_report", "cleanup", "^quick_action"]
    save_data: "zFunc(@.utils.data.save, {table: 'users'})"
    generate_report: "zFunc(@.reports.generate_summary)"
    cleanup: "zFunc(@.utils.cleanup_temp_files)"
    ^quick_action: "zFunc(@.utils.quick_process)"  # ← Bounce: execute and return to menu
```

**Key Points:**
- **Direct execution:** Functions run immediately when zKey is processed
- **Arguments:** Pass data as second parameter (JSON object or variables)
- **Return values:** Can return data for use by other zKeys when used with `zDialog` or `zWizard`
- **Path resolution:** Uses zPath syntax for function location

### zDialog:
Creates interactive forms for user input with validation using schema zVaFiles.

**Syntax:**
```yaml
zKey_name:
  zDialog:
    model: "schema.file_name.TableName"
    fields: ["field1", "field2", "field3"]
    onSubmit: "zFunc(@.path.to.function, zConv)"
```

**Key Points:**
- **Form validation:** Uses schema zVaFiles for field validation and constraints
- **Field selection:** Choose specific fields from schema to display in form
- **Data handling:** `zConv` contains form data for processing
- **onSubmit:** Function called when form is submitted with validated data
- **Integration:** Works seamlessly with zCRUD operations

### zWizard:
Manages multi-step workflows by executing sequential steps and storing results in `zHat` array for data passing between steps.

**Syntax:**
```yaml
zKey_name:
  zWizard:
    step1: "zFunc(@.path.to.function1)"
    step2: "zFunc(@.path.to.function2)"
    step3: "zFunc(@.path.to.function3, {zHat[0], zHat[1]})"
```

**Key Points:**
- **Sequential execution:** Steps execute in order (step1, step2, step3, etc.)
- **Data storage:** Results stored in `zHat` array (zHat[0], zHat[1], etc.)
- **Data passing:** Use `zHat[index]` to pass data between steps
- **Complex workflows:** Ideal for multi-step business processes
- **Error handling:** Failed steps can halt the entire workflow

---

## Schema zVaFiles

Schema zVaFiles define data models with field types, constraints, and validation rules.

### Structure:
```yaml
# schema.example.yaml
TableName:
  fields:
    field1: 
      type: "string"
      required: true
    field2:
      type: "integer" 
      min: 1
      max: 100
    field3:
      type: "enum"
      options: ["option1", "option2", "option3"]
```

### Field Types:
- **string:** Text input
- **integer:** Numeric input
- **float:** Decimal input
- **boolean:** True/false values
- **enum:** Selection from predefined options
- **date:** Date values
- **email:** Email format validation

### Dual Usage - zCRUD & zDialog:
Schema zVaFiles serve both database operations and form validation:

**zCRUD Operations:**
```yaml
# Used for database table creation and data validation
zCRUD: create Users
# Validates against schema.users.yaml field definitions
```

**zDialog Form Validation:**
```yaml
# ui.forms.yaml
zVaF:
  UserForm:
    zDialog:
      model: "schema.users.Users"  # References schema file
      fields: ["username", "email", "role"]
      onSubmit: "zFunc(@.users.save_user, zConv)"
```

> **Note:** Same schema file validates both database operations and interactive forms

### Example Schema zVaFile:
```yaml
# schema.users.yaml
Users:
  fields:
    id:
      type: "integer"
      primary_key: true
      auto_increment: true
    username:
      type: "string"
      required: true
      min_length: 3
      max_length: 50
    email:
      type: "email"
      required: true
    role:
      type: "enum"
      options: ["admin", "user", "guest"]
      default: "user"
    created_at:
      type: "date"
      auto_timestamp: true
```

### Schema Features:
- **Field validation:** Type checking, length limits, required fields
- **Constraints:** Min/max values, unique constraints
- **Defaults:** Automatic value assignment
- **Relationships:** Foreign key definitions
- **Indexes:** Performance optimization

> **Note:** For complete CRUD operations, see [CRUD_GUIDE_v1.3.0.md](/Documentation/CRUD_GUIDE_v1.3.0.md)

## File Loading & Caching

### Loading Process:
1. **Path Resolution:** zPath decoded to file system path
2. **File Detection:** Automatic extension detection (.yaml, .yml, .json)
3. **Type Identification:** UI vs Schema based on filename prefix
4. **Parsing:** YAML/JSON content parsed into data structures
5. **Caching:** Results cached for performance

### Cache Management:
- Files are automatically cached after first load
- Cache invalidation on file modification
- Session-based cache isolation
- Memory-efficient storage

### Error Handling:
- File not found errors with helpful messages
- Invalid YAML/JSON syntax detection
- Type validation errors
- Path resolution failures

## Best Practices

### File Organization:
```
project/
├── ui/                    # UI zVaFiles
│   ├── ui.main.yaml
│   ├── ui.users.yaml
│   └── ui.settings.yaml
├── schema/               # Schema zVaFiles
│   ├── schema.users.yaml
│   ├── schema.products.yaml
│   └── schema.orders.yaml
└── docs/                 # Documentation
```

### Naming Conventions:
- Use descriptive names: `ui.user_management.yaml`
- Keep names consistent: `ui.dashboard.yaml`, `schema.dashboard.yaml`
- Use lowercase with underscores: `ui.user_profile.yaml`
- Avoid special characters and spaces

### File Structure:
- Keep zBlocks logically grouped
- Use consistent indentation (2 spaces)
- Add comments for complex logic
- Validate YAML syntax before deployment

### Performance:
- Minimize file size for faster loading
- Use caching effectively
- Avoid deeply nested structures
- Group related functionality together

## Integration Examples

### UI + Schema Integration:
```yaml
# ui.user_form.yaml
zVaF:
  UserForm*: ["create", "update", "delete"]
    create:
      zDialog:
        model: "@.schema.users.Users"
        fields: ["username", "email", "role"]
        onSubmit: "zCRUD({action: create, model: '@.schema.users.Users', data: zConv})"
    update:
      zDialog:
        model: "@.schema.users.Users"
        fields: ["username", "email", "role"]
        onSubmit: "zCRUD({action: update, model: '@.schema.users.Users', data: zConv})"
```

### Cross-File References:
```yaml
# ui.main.yaml
zVaF:
  Main*: ["users", "products", "orders"]
    users: "zLink(@.ui.users.List)"
    products: "zLink(@.ui.products.Catalog)" 
    orders: "zLink(@.ui.orders.History)"

# ui.users.yaml  
zVaF:
  List*: ["add_user", "edit_user", "delete_user"]
    add_user: "zLink(@.ui.users.Create)"
    edit_user: "zLink(@.ui.users.Edit)"
    delete_user: "zFunc(@.users.delete_selected)"
```

## Troubleshooting

### Common Issues:

**File Not Found:**
- Check zPath syntax
- Verify file exists in workspace
- Confirm correct file extension

**Invalid YAML:**
- Validate syntax with YAML linter
- Check indentation (use 2 spaces)
- Verify quotes around special characters

**Type Detection Errors:**
- Ensure filename starts with `ui.` or `schema.`
- Check file extension is supported
- Verify file is readable

**Cache Issues:**
- Clear session cache
- Restart zCLI instance
- Check file modification timestamps

> **Note:** For detailed troubleshooting, see [zParser_GUIDE.md](/Documentation/zParser_GUIDE.md)

---

**zVaFiles** are the foundation of zolo-zcli's configuration-driven architecture, enabling rapid development through YAML-based interface and data model definitions.
