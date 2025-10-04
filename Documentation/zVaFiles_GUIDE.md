# zVaFiles Guide

## Introduction

**zVaFiles** (zVacuum Files) are YAML/JSON configuration files that serve as the foundation for `zolo-zcli`'s universal framework. They define both user interface structures and data models, enabling rapid development of applications through configuration-driven architecture.

> **Note:** zVaFiles are the core building blocks that power zWalker's interactive experiences and zCRUD's database operations. 

---

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

---

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

Schema zVaFiles define data models using `zTables`, `zFields`, and `zMeta` with comprehensive validation and constraint definitions, to support `zolo-zcli`'s **data handling** and **zDialog**.

### Schema Components:
- A **zTable** is a `zBlock`, of a named data model within a schema zVaFile that groups related fields together. Every schema zVaFile can contain multiple tables, each representing a distinct data entity.
- **Fields** are `zKeys` that define individual data attributes within a table, including type, validation rules, and constraints.
- **zField Properties** are configuration attributes `zKeys` that define how each zField behaves, including type, validation rules, and constraints.

### Schema Structure:
```yaml
# schema.example.yaml
TableName:                               # ← This is a zTable
  field1:                                # ← This is a zField
    type: "string"                       # ← This is a zField's Property
    required: true
  field2:
    type: "integer" 
    min: 1
    max: 100
  field3:
    type: "enum"
    options: ["option1", "option2", "option3"]
```

> **Note:** Each table is isolated within a schema zVaFile. Tables can reference each other through foreign keys but maintain separate field definitions.

### What is zMeta?

**Meta** is a special zBlock in schema zVaFiles (usually at the bottom of the schema zVaFile) that configures database type, location, and operational settings. 

### Structure:
```yaml
# schema.example.yaml
TableName:
  # ... table fields ...

Meta:
  Data_Type: sqlite                    # Database type
  Data_path: data/application.db       # Database location
```

> **Note:** Meta configuration is essential for zCRUD operations. Without proper Meta settings, database operations will fail.

### Database Configuration:

**SQLite (Current):**
```yaml
Meta:
  Data_Type: sqlite
  Data_path: data/myapp.db             # File path to SQLite database
```

**PostgreSQL (Future):**
```yaml
Meta:
  Data_Type: postgresql
  Data_path: postgresql://user:pass@localhost:5432/mydb
  # Or connection parameters:
  host: localhost
  port: 5432
  database: mydb
  user: username
  password: password
```

**CSV (Future):**
```yaml
Meta:
  Data_Type: csv
  Data_path: data/csv_files/           # Directory for CSV files
```

### Key Points:
- **Database abstraction:** Enables switching between database types
- **Connection management:** zCRUD uses Meta to establish database connections
- **Path configuration:** Specifies where data is stored or how to connect
- **Future extensibility:** Framework supports multiple database backends
- **Required for zCRUD:** All schema files need Meta for database operations


## zFields Properties

### Type

Defines the data type for a zField, determining storage, validation, and processing behavior.

**Supported Types:**
- **`string`** - Text data with length validation
- **`integer`** - Whole numbers with range constraints
- **`float`** - Decimal numbers with precision control
- **`boolean`** - True/false values
- **`datetime`** - Date and time with timezone support
- **`email`** - Email format validation
- **`url`** - URL format validation
- **`enum`** - Selection from predefined options
- **`json`** - JSON object storage

**Examples:**
```yaml
username:
  type: "string"
  min_length: 3
  max_length: 50

age:
  type: "integer"
  min: 18
  max: 120

email:
  type: "email"
  required: true

role:
  type: "enum"
  options: ["admin", "user", "guest"]
```

**Key Points:**
- **Required property:** Every zField must have a `type` definition
- **Validation:** Type determines available validation rules
- **Storage:** Maps to appropriate data types
- **zDialog integration:** Types define form input behavior

### Required

Specifies whether a zField must have a value during data operations.

**Syntax:**
```yaml
field_name:
  type: "string"
  required: true|false
```

**Behavior:**
- **`true`** - Field must be provided in CREATE/UPDATE operations
- **`false`** - Field is optional and can be omitted
- **`null`** - Uses type-specific defaults (string=optional, integer=optional)

**Examples:**
```yaml
username:
  type: "string"
  required: true        # Must be provided

email:
  type: "email"
  required: true
  unique: true

description:
  type: "string"
  required: false       # Optional field

created_at:
  type: "datetime"
  required: true
  default: now
```

**Key Points:**
- **Validation:** Required fields are validated before database operations
- **zDialog integration:** Required fields show validation indicators in forms
- **Database constraints:** Maps to data NOT NULL constraints
- **Default behavior:** Fields with `default` values are automatically non-required

### unique

Enforces uniqueness constraints on a zField, preventing duplicate values in the database.

**Syntax:**
```yaml
field_name:
  type: "string"
  unique: true|false
```

**Behavior:**
- **`true`** - Field values must be unique across all records
- **`false`** - Field allows duplicate values (default)
- **Database enforcement:** Creates UNIQUE constraint in SQLite

**Examples:**
```yaml
email:
  type: "email"
  required: true
  unique: true        # No duplicate emails allowed

username:
  type: "string"
  unique: true
  required: true

product_code:
  type: "string"
  unique: true
  source: generate_id(PRD)

description:
  type: "string"
  unique: false       # Multiple products can have same description
```

**Key Points:**
- **Database constraint:** Maps to SQLite UNIQUE constraint
- **Validation:** Prevents duplicate values during CREATE/UPDATE operations
- **Error handling:** Throws "UNIQUE constraint failed" on duplicate attempts
- **Common use cases:** Email addresses, usernames, product codes, identifiers
- **zDialog integration:** Unique fields show validation feedback in forms

### default

Sets default values for zFields when no value is provided during data operations.

**Syntax:**
```yaml
field_name:
  type: "string"
  default: value
```

**Behavior:**
- **Static values:** String, integer, float, boolean literals
- **`now`** - Auto-generates current timestamp (UTC ISO format)
- **Auto-population:** Applied during CREATE/UPDATE when field is missing
- **Database mapping:** Maps to SQLite DEFAULT constraint

**Examples:**
```yaml
version:
  type: "string"
  default: "1.0.0"         # Static default value

status:
  type: "enum"
  options: ["active", "inactive"]
  default: "active"        # Default enum selection

created_at:
  type: "datetime"
  default: now             # Auto-timestamp on creation

priority:
  type: "integer"
  default: 1               # Default numeric value

is_public:
  type: "boolean"
  default: false           # Default boolean value
```

**Key Points:**
- **Auto-population:** Missing fields get default values during CREATE/UPDATE
- **Timestamp handling:** `default: now` generates UTC ISO datetime strings
- **Validation bypass:** Fields with defaults are automatically non-required
- **Database constraints:** Maps to SQLite DEFAULT column constraints
- **zDialog integration:** Default values pre-populate form fields

### Primary Key (pk)

Designates a zField as the primary key for the table, ensuring uniqueness and enabling efficient record identification.

**Syntax:**
```yaml
field_name:
  type: "string"
  pk: true|false
```

**Behavior:**
- **`true`** - Field becomes the table's primary key
- **`false`** - Field is not a primary key (default)
- **Database enforcement:** Creates PRIMARY KEY constraint in SQLite
- **Automatic constraints:** Primary key fields are automatically unique and required

**Examples:**
```yaml
id:
  type: "string"
  pk: true
  source: generate_id(zU)  # Auto-generated primary key

user_id:
  type: "string"
  pk: true
  required: true

email:
  type: "email"
  pk: true
  unique: true             # Redundant - pk implies unique

username:
  type: "string"
  pk: false                # Not a primary key
  unique: true
```

**Key Points:**
- **Database constraint:** Maps to data PRIMARY KEY constraint
- **Automatic properties:** Primary keys are automatically unique and required
- **Record identification:** Enables efficient record lookup and foreign key references
- **Composite support:** Use table-level `primary_key: [field1, field2]` for composite keys
- **zDialog integration:** Primary keys are typically hidden in forms but used for record updates

### source

Enables auto-generation of field values using generator functions during data operations.

**Syntax:**
```yaml
field_name:
  type: "string"
  source: generate_function(parameters)
```

**Supported Generators:**
- **`generate_id(prefix)`** - Generates unique IDs with custom prefix (format: `prefix_xxxxxxxx`)
- **`generate_API(prefix)`** - Generates API keys (requires zCloud plugin)
- **`zRand(seed)`** - Generates random values (requires zCloud plugin)
- **Custom zPlugin functions** - Any function available in loaded zPlugins

**Behavior:**
- **Auto-population:** Applied during CREATE/UPDATE when field is missing
- **Priority:** Source generation takes precedence over default values
- **Validation bypass:** Fields with source are automatically non-required
- **Walker integration:** Uses walker.utils functions when available

**Examples:**
```yaml
id:
  type: "string"
  pk: true
  source: generate_id(zU)        # Generates: zU_a1b2c3d4

api_key:
  type: "string"
  unique: true
  source: generate_API(zAPI)     # Generates API key (requires plugin)

product_code:
  type: "string"
  source: generate_id(PRD)       # Generates: PRD_f8e9d2c1

user_token:
  type: "string"
  source: zRand(secure)          # Generates random value (requires plugin)

custom_field:
  type: "string"
  source: myPlugin.generateCode() # Custom zPlugin function
```

**Key Points:**
- **ID format:** `generate_id(prefix)` creates `prefix_` + 8 hex characters
- **Plugin support:** `generate_API` and `zRand` require zCloud plugin installation
- **zPlugin integration:** Any function from loaded zPlugins can be used as source
- **Fallback handling:** Falls back to ZUtils() if walker.utils unavailable
- **Auto-generation:** Fields are populated automatically during CREATE/UPDATE operations
- **zDialog integration:** Source fields are typically hidden in forms

### notes

Provides documentation and descriptive information for zFields, improving schema readability and maintainability.

**Syntax:**
```yaml
field_name:
  type: "string"
  notes: "Description or documentation text"
```

**Behavior:**
- **Documentation only:** Notes are parsed but not used in database operations
- **Schema clarity:** Helps developers understand field purpose and usage
- **Maintenance aid:** Improves long-term schema maintainability
- **No validation impact:** Notes do not affect field validation or constraints

**Examples:**
```yaml
user_id:
  type: "string"
  pk: true
  notes: "Primary key for user records, auto-generated with zU prefix"

email:
  type: "email"
  required: true
  unique: true
  notes: "User's primary email address, must be unique across all users"

created_at:
  type: "datetime"
  default: now
  notes: "Timestamp when record was first created, automatically set"

status:
  type: "enum"
  options: ["active", "inactive", "pending"]
  default: "pending"
  notes: "Current status of the user account"
```

**Key Points:**
- **Documentation purpose:** Notes are for human readability, not system functionality
- **Schema parsing:** Notes are preserved during schema parsing and validation
- **No database impact:** Notes do not create database constraints or affect operations
- **Development aid:** Improves code documentation and team collaboration
- **Optional property:** Notes can be omitted without affecting field behavior

### Foreign Key (fk)

Establishes foreign key relationships between tables, enabling referential integrity and automatic JOIN operations.

**Syntax:**
```yaml
field_name:
  type: "string"
  fk: referenced_table.referenced_column
```

**Behavior:**
- **Referential integrity:** Ensures values exist in referenced table
- **Database constraint:** Creates FOREIGN KEY constraint in data
- **Auto-JOIN support:** Enables automatic table joins based on relationships
- **zDialog integration:** Provides picker interface for selecting referenced values

**Examples:**
```yaml
user_id:
  type: "string"
  fk: zUsers.id              # References zUsers.id

app_id:
  type: "string"
  fk: zApps.id
  on_delete: CASCADE         # Delete child when parent deleted

parent_comment_id:
  type: "string"
  fk: zComments.id           # Self-reference for nested comments

category_id:
  type: "string"
  fk: zCategories.id
  on_delete: SET NULL        # Keep product if category deleted
```

**Key Points:**
- **Format:** `fk: TableName.columnName` (e.g., `zUsers.id`)
- **Database enforcement:** Maps to SQLite FOREIGN KEY constraint
- **Referential integrity:** Prevents orphaned records
- **Auto-JOIN:** Enables automatic table joins in queries
- **zDialog integration:** FK fields show picker interfaces in forms
- **Combined with on_delete:** Controls cascade behavior when referenced records are deleted

### validation/rules

Defines validation constraints and rules for zFields, ensuring data integrity before database operations.

**Syntax (Two Formats Supported):**

**Format 1 - Rules Block:**
```yaml
field_name:
  type: "string"
  rules:
    rule_name: value
    error_message: "Custom error message"
```

**Format 2 - Field Level:**
```yaml
field_name:
  type: "string"
  rule_name: value
  error_message: "Custom error message"
```

**Supported Rules:**
- **`min_length`** - Minimum string length
- **`max_length`** - Maximum string length  
- **`min`** - Minimum numeric value
- **`max`** - Maximum numeric value
- **`pattern`** - Regex pattern validation
- **`format`** - Built-in format validators (email, url, phone)
- **`error_message`** - Custom error message for validation failures

**Behavior:**
- **Pre-validation:** Rules are checked before database operations
- **Error handling:** Failed validation returns descriptive error messages
- **Type-aware:** Different rules apply based on field type
- **Custom messages:** Override default error messages with `error_message`

**Examples:**

**Using Rules Block:**
```yaml
username:
  type: "string"
  required: true
  rules:
    min_length: 3
    max_length: 50
    pattern: "^[a-zA-Z0-9_]+$"
    error_message: "Username must be 3-50 characters, letters/numbers/underscores only"

email:
  type: "string"
  required: true
  rules:
    format: email
    error_message: "Please provide a valid email address"
```

**Using Field Level:**
```yaml
age:
  type: "integer"
  min: 18
  max: 120
  error_message: "Age must be between 18 and 120"

password:
  type: "string"
  required: true
  min_length: 8
  max_length: 128
  pattern: "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)"
  error_message: "Password must contain uppercase, lowercase, and number"
```

**Key Points:**
- **Flexible syntax:** Validation rules can be defined in `rules:` block OR at field level
- **Built-in formats:** `email`, `url`, `phone` provide common validation patterns
- **Regex patterns:** Use `pattern` for custom validation logic
- **Error messages:** Customize validation feedback with `error_message`
- **Type-specific:** Rules automatically adapt to field type (string vs numeric)
- **Required integration:** Works with `required` field to ensure completeness
- **zDialog integration:** Validation errors are displayed in form interfaces

### enum

Defines enumerated field types with predefined options, providing controlled selection lists for data entry.

**Syntax:**
```yaml
field_name:
  type: "enum"
  options: ["option1", "option2", "option3"]
```

**Behavior:**
- **Controlled selection:** Limits values to predefined options
- **Interactive selection:** Provides numbered choice lists in zDialog
- **Database storage:** Stored as TEXT with validation
- **Default support:** Can specify default option from the list

**Examples:**
```yaml
role:
  type: "enum"
  options: ["admin", "user", "guest"]
  default: "user"
  required: true

status:
  type: "enum"
  options: ["active", "inactive", "pending", "suspended"]
  default: "pending"

app_type:
  type: "enum"
  options: ["web", "desktop", "mobile"]
  default: "web"
  required: true

priority:
  type: "enum"
  options: ["low", "medium", "high", "critical"]
  default: "medium"
```

**Key Points:**
- **Options array:** Must provide `options` array with valid choices
- **Interactive selection:** zDialog displays numbered options for user selection
- **Validation:** Only values from options array are accepted
- **Default values:** Can set `default` to any value from the options array
- **Database mapping:** Stored as TEXT with implicit CHECK constraint
- **zDialog integration:** Enum fields show interactive selection interfaces
- **Type safety:** Prevents invalid values from being entered

### Advanced Properties

Additional field properties for specialized use cases and advanced data handling.

#### on_delete

Controls cascade behavior when referenced foreign key records are deleted.

**Syntax:**
```yaml
field_name:
  type: "string"
  fk: referenced_table.column
  on_delete: CASCADE|RESTRICT|SET_NULL|SET_DEFAULT|NO_ACTION
```

**Supported Actions:**
- **`CASCADE`** - Delete dependent records when parent is deleted
- **`RESTRICT`** - Prevent parent deletion if dependencies exist
- **`SET_NULL`** - Set foreign key to NULL when parent is deleted
- **`SET_DEFAULT`** - Set foreign key to default value when parent is deleted
- **`NO_ACTION`** - Deferred constraint check (similar to RESTRICT)

**Examples:**
```yaml
user_id:
  type: "string"
  fk: zUsers.id
  on_delete: CASCADE         # Delete posts when user is deleted

category_id:
  type: "string"
  fk: zCategories.id
  on_delete: SET_NULL        # Keep product but remove category reference

parent_id:
  type: "string"
  fk: zComments.id
  on_delete: RESTRICT        # Prevent deletion of parent comments
```

**Key Points:**
- **Requires FK:** Must be used with `fk` property
- **Database constraint:** Maps to SQLite ON DELETE clause
- **Referential integrity:** Maintains data consistency across related tables
- **Common use case:** CASCADE for parent-child relationships, SET_NULL for optional references

#### format

Specifies field-level formatting and display behavior (separate from validation format).

**Syntax:**
```yaml
field_name:
  type: "string"
  format: format_type
```

**Behavior:**
- **Display formatting:** Controls how values are presented in zDialog
- **Input formatting:** May affect input validation and processing
- **Type-specific:** Different formats available for different field types

**Examples:**
```yaml
phone_number:
  type: "string"
  format: "phone"            # Format as (xxx) xxx-xxxx

currency:
  type: "float"
  format: "currency"         # Format as $X.XX

date_field:
  type: "datetime"
  format: "date"             # Display date only, not time
```

#### multiple

Indicates whether a field can accept multiple values (for array-like data).

**Syntax:**
```yaml
field_name:
  type: "string"
  multiple: true|false
```

**Behavior:**
- **Array support:** Allows field to store multiple values
- **Input handling:** zDialog may provide array input interfaces
- **Storage:** Values stored as JSON array or comma-separated string

**Examples:**
```yaml
tags:
  type: "string"
  multiple: true             # Allow multiple tag values

categories:
  type: "enum"
  options: ["web", "mobile", "desktop"]
  multiple: true             # Allow multiple category selections
```

#### nullable

Explicitly controls whether a field can accept NULL values.

**Syntax:**
```yaml
field_name:
  type: "string"
  nullable: true|false
```

**Behavior:**
- **NULL handling:** Explicitly allows or prevents NULL values
- **Database constraint:** Maps to NOT NULL constraint when false
- **Validation:** Overrides default NULL behavior for field type

**Examples:**
```yaml
description:
  type: "string"
  nullable: true             # Explicitly allow NULL values

required_field:
  type: "string"
  nullable: false            # Explicitly prevent NULL values
  required: true
```

#### condition

Defines conditional logic for field behavior based on other field values.

**Syntax:**
```yaml
field_name:
  type: "string"
  condition: conditional_expression
```

**Behavior:**
- **Conditional validation:** Field is only validated/required under certain conditions
- **Dynamic behavior:** Field behavior changes based on other field values
- **Expression syntax:** Uses field references and comparison operators

**Examples:**
```yaml
email:
  type: "email"
  required: true
  condition: "contact_method == 'email'"  # Only required if contact_method is email

phone:
  type: "string"
  condition: "contact_method == 'phone'"  # Only validated if contact_method is phone

admin_notes:
  type: "string"
  condition: "role == 'admin'"           # Only available for admin users
```

**Key Points:**
- **Advanced feature:** Provides dynamic field behavior
- **Expression evaluation:** Conditions are evaluated at runtime
- **Validation integration:** Works with validation rules and required fields
- **Complex logic:** Enables sophisticated form behavior based on user input

### Legacy Properties

Deprecated field properties maintained for backward compatibility but not recommended for new schemas.

#### Legacy Type Markers

**Syntax:**
```yaml
field_name: "type!"    # Required field (legacy)
field_name: "type?"    # Optional field (legacy)
```

**Modern Equivalent:**
```yaml
field_name:
  type: "string"
  required: true|false
```

**Examples:**
```yaml
# Legacy syntax (deprecated)
username: "string!"    # Required string
description: "string?" # Optional string

# Modern syntax (recommended)
username:
  type: "string"
  required: true

description:
  type: "string"
  required: false
```

#### Legacy zFunc Expressions

**Syntax:**
```yaml
field_name:
  source: "zFunc(generate_id, prefix)"
```

**Modern Equivalent:**
```yaml
field_name:
  source: "generate_id(prefix)"
```

**Examples:**
```yaml
# Legacy syntax (deprecated)
id:
  source: "zFunc(generate_id, zU)"

# Modern syntax (recommended)
id:
  source: "generate_id(zU)"
```

**Key Points:**
- **Backward compatibility:** Legacy syntax is still supported but deprecated
- **Migration path:** Legacy properties are automatically converted to modern equivalents
- **Recommendation:** Use modern syntax for all new schemas
- **Auto-conversion:** Legacy properties are parsed and normalized during schema processing

### Table-Level Properties

Properties that apply to entire tables rather than individual fields, providing table-wide configuration and constraints.

#### primary_key

Defines composite primary keys using multiple fields.

**Syntax:**
```yaml
TableName:
  field1:
    type: "string"
  field2:
    type: "string"
  primary_key: [field1, field2]  # Composite primary key
```

**Behavior:**
- **Composite constraint:** Multiple fields together form the primary key
- **Database enforcement:** Creates table-level PRIMARY KEY constraint
- **Field exclusion:** Individual fields in composite PK should not have `pk: true`

**Examples:**
```yaml
PostTags:
  post_id:
    type: "string"
    fk: zPosts.id
    required: true
  
  tag_id:
    type: "string"
    fk: zTags.id
    required: true
  
  primary_key: [post_id, tag_id]  # Composite PK
```

#### indexes

Defines database indexes for performance optimization.

**Syntax:**
```yaml
TableName:
  field1:
    type: "string"
  indexes:
    - name: index_name
      columns: [field1, field2]
      unique: true|false
```

**Behavior:**
- **Performance optimization:** Improves query speed on indexed columns
- **Automatic creation:** Indexes are created during table creation
- **Composite support:** Can index multiple columns together

**Examples:**
```yaml
Users:
  username:
    type: "string"
    unique: true
  
  email:
    type: "email"
    unique: true
  
  status:
    type: "enum"
    options: ["active", "inactive"]
  
  indexes:
    - name: idx_email
      columns: [email]
      unique: true
    
    - name: idx_username_status
      columns: [username, status]
    
    - name: idx_status
      columns: [status]
```

---

### Dual Usage of ui.* & schema.* zVaFiles

Schema zVaFiles serve both database operations and form validation through unified field definitions. zDialog automatically adapts field presentation based on zSession mode (terminal vs GUI) for optimal user experience across different display environments.

**Example Schema:**
```yaml
# schema.users.yaml
Users:
  id:
    type: "string"
    pk: true
    source: "generate_id(zU)"
    
  username:
    type: "string"
    required: true
    unique: true
    rules:
      min_length: 3
      max_length: 50
    
  email:
    type: "email"
    required: true
    unique: true
    
  role:
    type: "enum"
    options: ["admin", "user", "guest"]
    default: "user"
    required: true

Meta:
  Data_Type: sqlite
  Data_path: data/users.db
```

**zCRUD Operations:**
```yaml
# Database table creation and validation
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

> **Note:** Same schema file validates both database operations and interactive forms.<br>For more information about zDialog, zCRUD operations, and display modes, see [zDialog_GUIDE.md](/Documentation/zDialog_GUIDE.md) and [zDisplay_GUIDE.md](/Documentation/zDisplay_GUIDE.md)