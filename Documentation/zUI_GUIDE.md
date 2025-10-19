# zUI Guide - Building Interactive Menus

**Welcome!** This guide will teach you how to create interactive menus and user interfaces using simple YAML files. No programming experience required!

---

## What is a zUI File?

A **zUI file** is like a blueprint for an interactive menu. You write it once, and zCLI turns it into a working application with menus, buttons, and actions.

**Think of it like:** Creating a restaurant menu - you list the options, and customers (users) choose what they want.

### File Naming
All UI files must start with `zUI.`:
- `zUI.main_menu.yaml` ✅
- `zUI.settings.yaml` ✅
- `menu.yaml` ❌ (missing zUI prefix)

---

## Your First Menu

Let's create a simple menu with three options:

```yaml
# zUI.my_first_menu.yaml
zVaF:
  ~Root*: ["Say Hello", "Show Time", "stop"]
  
  "Say Hello":
    zDisplay:
      event: success
      content: "Hello! Welcome to zCLI!"
  
  "Show Time":
    zDisplay:
      event: info
      content: "The time is now!"
  
  stop:
    zDisplay:
      event: text
      content: "Goodbye!"
```

**What happens:**
1. User sees a menu with 3 options
2. They pick a number (1, 2, or 3)
3. The chosen action happens
4. "stop" exits the menu

---

## Understanding the Parts

### zVaF - The Container
Every zUI file needs a `zVaF:` at the top. Think of it as the "start here" marker.

```yaml
zVaF:
  # Everything goes inside here
```

### ~Root* - The Main Menu
This is your main menu list. The `~` and `*` are special markers that tell zCLI "this is a menu."

```yaml
~Root*: ["Option 1", "Option 2", "Option 3"]
```

**Rules:**
- Menu items go in `["quotes", "with", "commas"]`
- Names must EXACTLY match the options below
- Always include `"stop"` as the last option

### Menu Options - What Happens
Each option from your menu needs a section that says what to do:

```yaml
"Option 1":
  zDisplay:
    event: text
    content: "This shows when they pick option 1"
```

---

## Building Blocks

### 1. zDisplay - Show Messages

Show text, success messages, warnings, or errors to the user.

**Types of messages:**

```yaml
# Regular text
"Show Message":
  zDisplay:
    event: text
    content: "This is a regular message"

# Success (green)
"Great Job":
  zDisplay:
    event: success
    content: "You did it! ✅"

# Info (blue)
"Helpful Tip":
  zDisplay:
    event: info
    content: "Here's some information"

# Warning (yellow)
"Be Careful":
  zDisplay:
    event: warning
    content: "Watch out for this!"

# Error (red)
"Oops":
  zDisplay:
    event: error
    content: "Something went wrong"
```

### 2. Submenus - Menus Inside Menus

Create organized menus with multiple levels:

```yaml
zVaF:
  ~Root*: ["Games", "Settings", "stop"]
  
  "Games":
    ~Menu*: ["Play Game", "High Scores", "zBack"]
    
    "Play Game":
      zDisplay:
        event: success
        content: "Let's play!"
    
    "High Scores":
      zDisplay:
        event: info
        content: "Top 10 players..."
    
    "zBack":
      zDisplay:
        event: text
        content: "Going back..."
  
  "Settings":
    ~Menu*: ["Volume", "Graphics", "zBack"]
    
    "Volume":
      zDisplay:
        event: text
        content: "Adjusting volume..."
    
    "Graphics":
      zDisplay:
        event: text
        content: "Changing graphics..."
```

**Key points:**
- Use `~Menu*` for submenus (instead of `~Root*`)
- Always include `"zBack"` to let users go back
- You can nest menus as deep as you want!

### 3. Quick Actions with ^ (Bounce Back)

Sometimes you want to do something quick and return to the menu automatically:

```yaml
~Root*: ["View Stats", "^Quick Check", "stop"]

"View Stats":
  zDisplay:
    event: text
    content: "Here are your stats..."

"^Quick Check":
  # The ^ makes it bounce back automatically
  zDisplay:
    event: success
    content: "All systems OK! ✅"
  # User automatically returns to menu
```

**Use ^ when:** The action is quick and the user will want to do more after.

### 4. Delta Links $ - Jump Between Sections

Jump to different parts of your UI file:

```yaml
zVaF:
  ~Root*: ["Main Menu", "$Settings", "$Help", "stop"]
  
  "Main Menu":
    zDisplay:
      event: text
      content: "This is the main menu"

Settings:
  ~Root*: ["Option 1", "Option 2", "$zVaF"]
  
  "Option 1":
    zDisplay:
      event: text
      content: "Setting 1"
  
  "Option 2":
    zDisplay:
      event: text
      content: "Setting 2"

Help:
  ~Root*: ["About", "Contact", "$zVaF"]
  
  "About":
    zDisplay:
      event: info
      content: "Version 1.0"
  
  "Contact":
    zDisplay:
      event: text
      content: "help@example.com"
```

**Key points:**
- Use `$SectionName` to jump to another section
- Use `$zVaF` to return to the top
- No quotes around delta links in the menu list!

---

## Working with Data

### zDialog - Ask for Input

Collect information from users with forms:

```yaml
"Add Student":
  zDialog:
    model: "zSchema.students.Students"
    fields: ["name", "age", "grade"]
    onSubmit: "zFunc(@.save_student)"
```

**What happens:**
1. Form appears asking for name, age, and grade
2. User fills it out
3. Data is validated (checked for errors)
4. If OK, `save_student` function runs with the data

### zData - Work with Databases

Read, create, update, or delete data:

```yaml
"View All Students":
  zData:
    action: read
    table: students
    limit: 10

"Add New Student":
  zData:
    action: create
    table: students
    data:
      name: "John Doe"
      age: 16
      grade: 10
```

**Actions you can do:**
- `read` - View data
- `create` - Add new records
- `update` - Change existing records
- `delete` - Remove records

---

## Advanced Features

### zWizard - Multi-Step Processes

When you need to do several things in order:

```yaml
"Setup Account":
  zWizard:
    step1:
      zDisplay:
        event: info
        content: "Welcome! Let's set up your account."
    
    step2:
      zDialog:
        model: "zSchema.users.Users"
        fields: ["username", "email"]
    
    step3:
      zData:
        action: create
        table: users
        data: "zHat"
    
    step4:
      zDisplay:
        event: success
        content: "Account created! You can now log in."
```

**How it works:**
- Steps run in order (step1, step2, step3, etc.)
- Data from one step can be used in the next
- If any step fails, the wizard stops

### Plugins - Special Functions

Use pre-built functions with the `&` symbol:

```yaml
"Generate ID":
  zDisplay:
    event: text
    content: "&id_generator.generate_uuid()"

"Get Current Time":
  zDisplay:
    event: text
    content: "&id_generator.get_timestamp()"
```

**Built-in plugins:**
- `id_generator` - Create unique IDs and timestamps
- More plugins available in the plugin guide!

---

## Linking to Other Files

### Cross-File Navigation

Link to menus in other zUI files:

```yaml
# In zUI.main_menu.yaml
~Root*: ["Games Menu", "Settings Menu", "stop"]

"Games Menu":
  zLink: "@.zUI.games_menu.zVaF"

"Settings Menu":
  zLink: "@.zUI.settings_menu.zVaF"
```

```yaml
# In zUI.games_menu.yaml
zVaF:
  ~Root*: ["Play Game", "High Scores", "$MainMenu"]
  # More options...
```

**Benefits:**
- Keep files organized and small
- Reuse menus in different places
- Easier to maintain

---

## Tips for Success

### ✅ DO:
1. **Use clear names:** "Save Data" is better than "Save"
2. **Include stop:** Always give users a way to exit
3. **Test often:** Run your menu after each change
4. **Keep it simple:** Start with basic menus, add features later
5. **Add zBack:** Let users navigate back easily

### ❌ DON'T:
1. **Forget quotes:** Menu items need `"quotes"`
2. **Mismatch names:** Menu item must EXACTLY match the section name
3. **Skip indentation:** YAML is picky about spaces
4. **Use tabs:** Always use spaces (2 or 4 spaces per level)
5. **Forget stop:** Users need a way out!

---

## Common Mistakes & Fixes

### Problem: "Menu item not found"
```yaml
# ❌ WRONG - Names don't match
~Root*: ["Save Data", "stop"]
"save data":  # lowercase, won't work!
  zDisplay:
    event: text
    content: "Saving..."

# ✅ CORRECT - Names match exactly
~Root*: ["Save Data", "stop"]
"Save Data":
  zDisplay:
    event: text
    content: "Saving..."
```

### Problem: "Invalid YAML"
```yaml
# ❌ WRONG - Inconsistent indentation
zVaF:
  ~Root*: ["Option 1", "stop"]
   "Option 1":  # Extra space!
    zDisplay:
      event: text

# ✅ CORRECT - Consistent indentation
zVaF:
  ~Root*: ["Option 1", "stop"]
  "Option 1":
    zDisplay:
      event: text
```

### Problem: Menu doesn't show
```yaml
# ❌ WRONG - Missing * or ~
Root: ["Option 1", "stop"]

# ✅ CORRECT - Has both ~ and *
~Root*: ["Option 1", "stop"]
```

---

## Complete Example

Here's a complete school assignment tracker:

```yaml
# zUI.homework_tracker.yaml
zVaF:
  ~Root*: ["View Homework", "Add Homework", "Mark Complete", "$Settings", "stop"]
  
  "View Homework":
    zData:
      action: read
      table: homework
      where: "status = 'pending'"
      limit: 10
  
  "Add Homework":
    zWizard:
      step1:
        zDialog:
          model: "zSchema.homework.Homework"
          fields: ["subject", "description", "due_date"]
      step2:
        zData:
          action: create
          table: homework
          data: "zHat"
      step3:
        zDisplay:
          event: success
          content: "Homework added! Don't forget to do it!"
  
  "Mark Complete":
    zWizard:
      step1:
        zDialog:
          model: "zSchema.homework.Homework"
          fields: ["id"]
      step2:
        zData:
          action: update
          table: homework
          where: "id = zHat[id]"
          data:
            status: "complete"
      step3:
        zDisplay:
          event: success
          content: "Great job! Assignment completed! ✅"

Settings:
  ~Root*: ["View All", "Clear Completed", "$zVaF"]
  
  "View All":
    zData:
      action: read
      table: homework
      limit: 50
  
  "Clear Completed":
    zData:
      action: delete
      table: homework
      where: "status = 'complete'"
```

---

## Practice Exercises

### Exercise 1: Simple Calculator Menu
Create a menu with options for Add, Subtract, Multiply, Divide.

<details>
<summary>Show Solution</summary>

```yaml
zVaF:
  ~Root*: ["Add", "Subtract", "Multiply", "Divide", "stop"]
  
  "Add":
    zDisplay:
      event: text
      content: "5 + 3 = 8"
  
  "Subtract":
    zDisplay:
      event: text
      content: "5 - 3 = 2"
  
  "Multiply":
    zDisplay:
      event: text
      content: "5 × 3 = 15"
  
  "Divide":
    zDisplay:
      event: text
      content: "6 ÷ 3 = 2"
```
</details>

### Exercise 2: Two-Level Menu
Create a main menu with "Games" and "Settings" submenus.

<details>
<summary>Show Solution</summary>

```yaml
zVaF:
  ~Root*: ["Games", "Settings", "stop"]
  
  "Games":
    ~Menu*: ["Play", "High Scores", "zBack"]
    "Play":
      zDisplay:
        event: success
        content: "Starting game..."
    "High Scores":
      zDisplay:
        event: info
        content: "Top 5 players..."
  
  "Settings":
    ~Menu*: ["Volume", "Graphics", "zBack"]
    "Volume":
      zDisplay:
        event: text
        content: "Volume settings..."
    "Graphics":
      zDisplay:
        event: text
        content: "Graphics settings..."
```
</details>

---

## Next Steps

Now that you know how to create UI files, learn about:
- **[zSchema Guide](zSchema_GUIDE.md)** - Define your data structure
- **[zWalker Guide](zWalker_GUIDE.md)** - Advanced navigation features
- **[zPlugin Guide](zPlugin_GUIDE.md)** - Create custom functions

---

## Quick Reference

### Menu Structure
```yaml
zVaF:
  ~Root*: ["Option 1", "Option 2", "stop"]
  "Option 1": # action
  "Option 2": # action
```

### Display Types
- `event: text` - Regular message
- `event: success` - Green success message
- `event: info` - Blue information
- `event: warning` - Yellow warning
- `event: error` - Red error

### Special Symbols
- `~` - Anchor (prevents auto-back)
- `*` - Menu marker
- `$` - Delta link (jump to section)
- `^` - Bounce (auto-return to menu)
- `@` - Workspace path
- `&` - Plugin function

### Common Actions
- `zDisplay` - Show messages
- `zDialog` - Get user input
- `zData` - Work with database
- `zWizard` - Multi-step process
- `zLink` - Go to another file
- `zFunc` - Run a function

---

**Remember:** Start simple, test often, and build up gradually. You've got this! 🚀

