# zSchema Guide - Defining Your Data

**Welcome!** This guide will teach you how to define the structure of your data using simple YAML files. Think of it like creating a template for information you want to store.

---

## What is a zSchema File?

A **zSchema file** is like a form template that tells the computer:
- What information you want to collect
- What type each piece of information is (text, number, date, etc.)
- What rules the information must follow

**Think of it like:** A job application form - it has specific fields (name, age, email) and rules (age must be a number, email must be valid).

### File Naming
All schema files must start with `zSchema.`:
- `zSchema.students.yaml` ✅
- `zSchema.products.yaml` ✅
- `students.yaml` ❌ (missing zSchema prefix)

---

## Your First Schema

Let's create a simple schema for storing student information:

```yaml
# zSchema.students.yaml
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
  
  grade:
    type: integer
    min: 1
    max: 12
  
  email:
    type: email
    required: false

Meta:
  Data_Type: sqlite
  Data_Path: zMachine.school_data
```

**This creates a template for student records with:**
- Auto-generated ID
- Required name
- Age between 5-18
- Grade between 1-12
- Optional email

---

## Understanding the Parts

### Table Name (Students)
The first thing is the table name - this is what you're storing.

```yaml
Students:
  # Fields go here
```

**Examples:**
- `Students` - Store student information
- `Products` - Store product inventory
- `Homework` - Store homework assignments
- `Books` - Store book catalog

### Fields - What Information to Store

Each field is a piece of information you want to keep:

```yaml
name:
  type: string
  required: true
```

**Common fields:**
- `id` - Unique identifier
- `name` - Person's or thing's name
- `description` - Longer text description
- `created_at` - When it was created
- `status` - Current state (active, complete, etc.)

### Meta - Database Settings

Every schema needs a `Meta` section at the bottom:

```yaml
Meta:
  Data_Type: sqlite
  Data_Path: zMachine.my_data
```

**What this means:**
- `Data_Type: sqlite` - Use SQLite database (simple file-based)
- `Data_Path: zMachine.my_data` - Where to store the data (works on any computer)

---

## Field Types

### string - Text

For names, descriptions, any text:

```yaml
name:
  type: string
  required: true

description:
  type: string
  required: false
```

**Use for:** Names, titles, descriptions, addresses

### integer - Whole Numbers

For ages, quantities, counts:

```yaml
age:
  type: integer
  min: 13
  max: 19

quantity:
  type: integer
  min: 0
  max: 100
```

**Use for:** Ages, quantities, counts, ratings (1-5)

### float - Decimal Numbers

For prices, measurements, percentages:

```yaml
price:
  type: float
  min: 0.01
  max: 999.99

grade_percentage:
  type: float
  min: 0.0
  max: 100.0
```

**Use for:** Money, measurements, percentages, grades

### boolean - True/False

For yes/no questions:

```yaml
is_active:
  type: boolean
  default: true

completed:
  type: boolean
  default: false
```

**Use for:** Active/inactive, completed/incomplete, yes/no questions

### email - Email Addresses

For email addresses (automatically validates format):

```yaml
email:
  type: email
  required: true
  unique: true
```

**Automatically checks:** someone@example.com format

### datetime - Dates and Times

For dates, times, or both:

```yaml
due_date:
  type: datetime
  required: true

created_at:
  type: datetime
  default: now
```

**Use for:** Due dates, birth dates, creation times, appointments

### enum - Multiple Choice

For selecting from specific options:

```yaml
status:
  type: enum
  options: ["pending", "in_progress", "complete"]
  default: "pending"

grade_level:
  type: enum
  options: ["freshman", "sophomore", "junior", "senior"]
  required: true
```

**Use for:** Status, categories, roles, choices

---

## Field Properties

### required - Must Provide

If `true`, the user MUST fill this out:

```yaml
name:
  type: string
  required: true  # User must provide a name

nickname:
  type: string
  required: false  # Optional field
```

### unique - No Duplicates

If `true`, no two records can have the same value:

```yaml
email:
  type: email
  required: true
  unique: true  # No two users can have the same email

username:
  type: string
  required: true
  unique: true  # No duplicate usernames
```

### default - Automatic Values

Sets a value automatically if user doesn't provide one:

```yaml
status:
  type: enum
  options: ["active", "inactive"]
  default: "active"  # Automatically set to "active"

created_at:
  type: datetime
  default: now  # Automatically set to current time
```

### pk (Primary Key) - The Unique ID

Every table should have ONE field marked as `pk: true`. This is the unique identifier:

```yaml
id:
  type: string
  pk: true  # This is the unique identifier
  source: generate_id(STU)  # Auto-generate it
```

**Think of it like:** Your student ID number - no one else has the same one

### source - Auto-Generate Values

Automatically create values using functions:

```yaml
id:
  type: string
  pk: true
  source: generate_id(STU)  # Creates: STU_a1b2c3d4

created_at:
  type: datetime
  source: now  # Or use default: now
```

---

## Validation Rules

### min / max - Number Limits

Set minimum and maximum values for numbers:

```yaml
age:
  type: integer
  min: 13  # At least 13
  max: 19  # At most 19

price:
  type: float
  min: 0.01  # At least one cent
  max: 999.99  # At most $999.99
```

### min_length / max_length - Text Length

Set minimum and maximum length for text:

```yaml
username:
  type: string
  min_length: 3  # At least 3 characters
  max_length: 20  # At most 20 characters
  required: true

password:
  type: string
  min_length: 8  # At least 8 characters
  required: true
```

---

## Real-World Examples

### Example 1: Homework Tracker

```yaml
# zSchema.homework.yaml
Homework:
  id:
    type: string
    pk: true
    source: generate_id(HW)
  
  subject:
    type: enum
    options: ["Math", "Science", "English", "History", "Other"]
    required: true
  
  title:
    type: string
    required: true
    min_length: 3
    max_length: 100
  
  description:
    type: string
    required: false
  
  due_date:
    type: datetime
    required: true
  
  status:
    type: enum
    options: ["not_started", "in_progress", "complete"]
    default: "not_started"
  
  priority:
    type: enum
    options: ["low", "medium", "high"]
    default: "medium"
  
  created_at:
    type: datetime
    default: now

Meta:
  Data_Type: sqlite
  Data_Path: zMachine.homework_data
```

### Example 2: Product Inventory

```yaml
# zSchema.products.yaml
Products:
  id:
    type: string
    pk: true
    source: generate_id(PRD)
  
  name:
    type: string
    required: true
    min_length: 2
    max_length: 100
  
  category:
    type: enum
    options: ["Electronics", "Clothing", "Food", "Books", "Other"]
    required: true
  
  price:
    type: float
    min: 0.01
    max: 9999.99
    required: true
  
  stock:
    type: integer
    min: 0
    default: 0
  
  in_stock:
    type: boolean
    default: true
  
  added_date:
    type: datetime
    default: now

Meta:
  Data_Type: sqlite
  Data_Path: zMachine.inventory_data
```

### Example 3: Contact List

```yaml
# zSchema.contacts.yaml
Contacts:
  id:
    type: string
    pk: true
    source: generate_id(CNT)
  
  first_name:
    type: string
    required: true
    min_length: 1
    max_length: 50
  
  last_name:
    type: string
    required: true
    min_length: 1
    max_length: 50
  
  email:
    type: email
    required: true
    unique: true
  
  phone:
    type: string
    required: false
  
  relationship:
    type: enum
    options: ["family", "friend", "classmate", "teacher", "other"]
    default: "other"
  
  notes:
    type: string
    required: false
  
  created_at:
    type: datetime
    default: now

Meta:
  Data_Type: sqlite
  Data_Path: zMachine.contacts_data
```

---

## Advanced Features

### Foreign Keys - Linking Tables

Connect information between tables:

```yaml
# zSchema.blog.yaml
Posts:
  id:
    type: string
    pk: true
    source: generate_id(POST)
  
  title:
    type: string
    required: true
  
  content:
    type: string
    required: true
  
  author_id:
    type: string
    required: true
    fk: Authors.id  # Links to Authors table

Authors:
  id:
    type: string
    pk: true
    source: generate_id(AUTH)
  
  name:
    type: string
    required: true
    unique: true
  
  email:
    type: email
    required: true
    unique: true

Meta:
  Data_Type: sqlite
  Data_Path: zMachine.blog_data
```

**What `fk` means:** "This author_id must be an ID that exists in the Authors table"

---

## Tips for Success

### ✅ DO:
1. **Always include an id field** with `pk: true`
2. **Use clear field names:** `due_date` instead of `date`
3. **Set reasonable limits:** min/max for numbers and lengths
4. **Use enums for choices:** Better than free text
5. **Add defaults when appropriate:** Makes data entry easier

### ❌ DON'T:
1. **Forget the Meta section:** Database won't work without it
2. **Make everything required:** Give users flexibility
3. **Use weird field names:** `fld1` is confusing, `first_name` is clear
4. **Skip validation rules:** min/max help prevent errors
5. **Forget the pk field:** Every table needs a unique identifier

---

## Common Mistakes & Fixes

### Problem: "Table not found"
```yaml
# ❌ WRONG - No Meta section
Students:
  name:
    type: string

# ✅ CORRECT - Has Meta section
Students:
  name:
    type: string

Meta:
  Data_Type: sqlite
  Data_Path: zMachine.my_data
```

### Problem: "Invalid type"
```yaml
# ❌ WRONG - Typo in type
age:
  type: interger  # Wrong spelling!

# ✅ CORRECT - Correct spelling
age:
  type: integer
```

### Problem: "No primary key"
```yaml
# ❌ WRONG - No pk field
Students:
  name:
    type: string

# ✅ CORRECT - Has pk field
Students:
  id:
    type: string
    pk: true
    source: generate_id(STU)
  name:
    type: string
```

---

## Practice Exercises

### Exercise 1: Movie Collection
Create a schema for tracking movies with title, genre, rating (1-5), and watched status.

<details>
<summary>Show Solution</summary>

```yaml
# zSchema.movies.yaml
Movies:
  id:
    type: string
    pk: true
    source: generate_id(MOV)
  
  title:
    type: string
    required: true
    min_length: 1
    max_length: 200
  
  genre:
    type: enum
    options: ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Other"]
    required: true
  
  rating:
    type: integer
    min: 1
    max: 5
    required: false
  
  watched:
    type: boolean
    default: false
  
  notes:
    type: string
    required: false
  
  added_date:
    type: datetime
    default: now

Meta:
  Data_Type: sqlite
  Data_Path: zMachine.movies_data
```
</details>

### Exercise 2: Recipe Book
Create a schema for recipes with name, category, prep time (minutes), and difficulty.

<details>
<summary>Show Solution</summary>

```yaml
# zSchema.recipes.yaml
Recipes:
  id:
    type: string
    pk: true
    source: generate_id(RCP)
  
  name:
    type: string
    required: true
    min_length: 2
    max_length: 100
  
  category:
    type: enum
    options: ["Breakfast", "Lunch", "Dinner", "Dessert", "Snack"]
    required: true
  
  prep_time_minutes:
    type: integer
    min: 1
    max: 300
    required: true
  
  difficulty:
    type: enum
    options: ["easy", "medium", "hard"]
    default: "medium"
  
  ingredients:
    type: string
    required: true
  
  instructions:
    type: string
    required: true
  
  favorite:
    type: boolean
    default: false
  
  created_at:
    type: datetime
    default: now

Meta:
  Data_Type: sqlite
  Data_Path: zMachine.recipes_data
```
</details>

---

## Quick Reference

### Common Types
```yaml
type: string    # Text
type: integer   # Whole numbers
type: float     # Decimal numbers
type: boolean   # true/false
type: email     # Email addresses
type: datetime  # Dates and times
type: enum      # Multiple choice
```

### Common Properties
```yaml
required: true       # Must provide
unique: true         # No duplicates
pk: true            # Primary key (unique ID)
default: value      # Auto-fill if empty
source: generate_id # Auto-generate
min: number         # Minimum value
max: number         # Maximum value
min_length: number  # Minimum text length
max_length: number  # Maximum text length
options: [...]      # Choices for enum
```

### Meta Section (Required!)
```yaml
Meta:
  Data_Type: sqlite
  Data_Path: zMachine.my_data
```

### ID Generation Prefixes
```yaml
source: generate_id(STU)  # Student: STU_a1b2c3d4
source: generate_id(PRD)  # Product: PRD_a1b2c3d4
source: generate_id(USR)  # User: USR_a1b2c3d4
# Use any 3-4 letter prefix you want!
```

---

## Next Steps

Now that you know how to create schemas, learn about:
- **[zUI Guide](zUI_GUIDE.md)** - Build menus that use your data
- **[zData Guide](zData_GUIDE.md)** - Work with your data
- **[zWalker Guide](zWalker_GUIDE.md)** - Create complete applications

---

## Getting Help

**Common questions:**
- "What type should I use?" → Use `string` for text, `integer` for whole numbers, `float` for decimals
- "Do I need a primary key?" → Yes! Always include an `id` field with `pk: true`
- "What's the Meta section for?" → Tells the system what database to use and where to store data
- "Can I have multiple tables?" → Yes! Just add them above the Meta section

**Remember:** Start simple with a few fields, test it, then add more. You've got this! 🚀

