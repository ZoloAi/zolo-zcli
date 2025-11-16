[← Back to Level 2](../Level_2_Config/README.md) | [Tutorial Home](../README.md)

# Level 3: User Input

**<span style="color:#8FBE6D">Learn to collect user input with validation!</span>**

## What You'll Build

An interactive Terminal app that demonstrates zDisplay's input capabilities:
1. **String Input** - Collect text from users
2. **Password Input** - Masked password entry
3. **Single Selection** - Choose one from a list
4. **Multi-Selection** - Choose multiple from a list
5. **Interactive Menus** - Number-based selections

## What You'll Learn

1. **<span style="color:#8FBE6D">Input methods</span>** - String, password, selection
2. **<span style="color:#F8961F">Validation</span>** - Automatic type checking
3. **<span style="color:#00D4FF">Selections</span>** - Single and multi-select
4. **<span style="color:#EA7171">Menus</span>** - Interactive number choices

## The Code

```python
from zCLI import zCLI

z = zCLI()

# String input
z.display.header("String Input", color="CYAN")
name = z.display.read_string("Enter your name: ")
z.display.success(f"Hello, {name}!")

# Password input (masked)
z.display.header("Password Input", color="YELLOW")
password = z.display.read_password("Enter password: ")
z.display.success(f"Password length: {len(password)} characters")

# Single selection
z.display.header("Single Selection", color="GREEN")
env = z.display.selection(
    "Choose environment:",
    ["Development", "Staging", "Production"]
)
z.display.success(f"Selected: {env}")

# Multi-selection
z.display.header("Multi Selection", color="MAGENTA")
features = z.display.selection(
    "Enable features (select multiple):",
    ["Logging", "Caching", "Debugging", "Profiling"],
    multi=True
)
z.display.success(f"Enabled: {', '.join(features)}")

# Interactive menu
z.display.header("Interactive Menu", color="BLUE")
menu_items = [
    (1, "View Profile"),
    (2, "Edit Settings"),
    (3, "Logout"),
]
choice = z.display.zMenu(menu_items, return_selection=True)
z.display.success(f"You selected: {choice}")
```

## How to Run

```bash
cd Demos/Layer_0/Terminal_Tutorial/Level_3_Input
python3 input_demo.py
```

The script will:
1. Prompt you for your name
2. Ask for a password (masked with `*`)
3. Show a list to select an environment
4. Show checkboxes for multiple features
5. Display a numbered menu

**Try it!** Follow the prompts and see how input is collected.

## Input Methods

### 1. String Input
```python
name = z.display.read_string("Enter your name: ")
```

**Features:**
- Plain text input
- No masking
- Returns a string
- Empty input allowed (unless validation added)

### 2. Password Input
```python
password = z.display.read_password("Enter password: ")
```

**Features:**
- Input is masked (shows `*` instead of characters)
- Secure input collection
- Returns a string
- Works in Terminal and GUI

### 3. Single Selection
```python
choice = z.display.selection(
    "Choose one:",
    ["Option 1", "Option 2", "Option 3"]
)
```

**Features:**
- Radio button style (only one selection)
- Arrow keys to navigate
- Enter to select
- Returns the selected string

### 4. Multi-Selection
```python
choices = z.display.selection(
    "Choose multiple:",
    ["Option 1", "Option 2", "Option 3"],
    multi=True
)
```

**Features:**
- Checkbox style (multiple selections)
- Arrow keys to navigate
- Space to toggle selection
- Enter to confirm
- Returns a list of selected strings

### 5. Interactive Menu
```python
menu_items = [
    (1, "View Profile"),
    (2, "Edit Settings"),
    (3, "Logout"),
]

choice = z.display.zMenu(menu_items, return_selection=True)
```

**Features:**
- Numbered options (1, 2, 3, ...)
- Type number and press Enter
- Returns the number selected
- Simple and familiar interface

## Terminal vs GUI Behavior

All these input methods work identically in Terminal and GUI:

| Method | Terminal | GUI |
|--------|----------|-----|
| `read_string()` | `input()` prompt | HTML `<input>` field |
| `read_password()` | `getpass()` masked | HTML `<input type="password">` |
| `selection()` | Arrow key navigation | Radio buttons or checkboxes |
| `zMenu()` | Number input | Clickable list |

**Key Point:** Write `z.display.read_string("Name:")` and it works everywhere. Same code, different rendering.

## Input Validation

Basic validation is built-in:

```python
# Empty string handling
name = z.display.read_string("Enter name (required): ")
if not name:
    z.display.error("Name cannot be empty!")

# Length validation
password = z.display.read_password("Password (min 8 chars): ")
if len(password) < 8:
    z.display.error("Password too short!")

# Choice validation
valid_envs = ["dev", "staging", "prod"]
env = z.display.read_string("Environment: ")
if env not in valid_envs:
    z.display.error(f"Invalid environment! Choose from: {valid_envs}")
```

For advanced validation (type checking, regex, custom rules), see **zDialog** in Layer 2 tutorials.

## Selection Styles

You can customize selection display:

```python
# Numbered list (default)
choice = z.display.selection(
    "Pick one:",
    ["A", "B", "C"],
    style="numbered"  # 1. A, 2. B, 3. C
)

# Bulleted list
choice = z.display.selection(
    "Pick one:",
    ["A", "B", "C"],
    style="bullet"  # • A, • B, • C
)

# Letters
choice = z.display.selection(
    "Pick one:",
    ["A", "B", "C"],
    style="letter"  # a) A, b) B, c) C
)
```

## Menu vs Selection

**When to use `selection()`:**
- Need to present a list of options
- Want arrow key navigation
- Need checkboxes (multi-select)
- Modern, interactive feel

**When to use `zMenu()`:**
- Need numbered options (1, 2, 3)
- Simple type-number-and-enter flow
- Familiar Terminal menu style
- Older users or scripts

**Both work!** Choose based on your users and use case.

## Experiment!

### 1. Create a simple form
```python
z.display.header("User Registration", color="CYAN")

name = z.display.read_string("Full name: ")
email = z.display.read_string("Email: ")
password = z.display.read_password("Password: ")

z.display.success("Registration complete!")
z.display.info(f"Name: {name}")
z.display.info(f"Email: {email}")
```

### 2. Add validation loop
```python
while True:
    password = z.display.read_password("Password (min 8): ")
    if len(password) >= 8:
        z.display.success("Password accepted!")
        break
    z.display.error("Too short! Try again.")
```

### 3. Build a settings menu
```python
while True:
    menu = [
        (1, "Change Name"),
        (2, "Change Email"),
        (3, "Change Password"),
        (4, "Exit"),
    ]
    choice = z.display.zMenu(menu, return_selection=True)
    
    if choice == 1:
        name = z.display.read_string("New name: ")
    elif choice == 2:
        email = z.display.read_string("New email: ")
    elif choice == 3:
        password = z.display.read_password("New password: ")
    elif choice == 4:
        break
```

### 4. Multi-step wizard
```python
# Step 1: Basic info
name = z.display.read_string("Name: ")

# Step 2: Choose role
role = z.display.selection("Role:", ["Admin", "User", "Guest"])

# Step 3: Choose permissions
perms = z.display.selection(
    "Permissions:",
    ["Read", "Write", "Delete", "Share"],
    multi=True
)

# Summary
z.display.header("Summary", color="GREEN")
z.display.info(f"Name: {name}")
z.display.info(f"Role: {role}")
z.display.info(f"Permissions: {', '.join(perms)}")
```

## Success Checklist

- **<span style="color:#8FBE6D">String input works</span>**
- **<span style="color:#F8961F">Password is masked</span>** (shows `*`)
- **<span style="color:#00D4FF">Single selection works</span>** (arrow keys)
- **<span style="color:#EA7171">Multi-selection works</span>** (checkboxes)
- **<span style="color:#AE84D3">Menu returns choice</span>** (number)

## What's Happening Under the Hood

### Terminal Input
```python
# zDisplay uses Python's built-in input()
def read_string(prompt):
    return input(prompt)

# For passwords, uses getpass (masked input)
import getpass
def read_password(prompt):
    return getpass.getpass(prompt)
```

### GUI Input
```python
# zDisplay sends a WebSocket event
def read_string(prompt):
    websocket.send({
        "event": "input_request",
        "prompt": prompt,
        "type": "text"
    })
    # Wait for response from browser
    return await websocket.recv()
```

**You never write this!** zDisplay handles mode detection automatically.

### Selection Implementation

Selections use a library like `inquirer` or `bullet` in Terminal:
- Arrow keys → navigate options
- Space → toggle (multi-select)
- Enter → confirm

In GUI mode, it renders as HTML radio buttons or checkboxes.

## What's Next?

**Congratulations!** You've completed the Layer 0 Terminal Tutorial!

You now understand:
- ✅ **Level 0**: Hello zCLI (initialization)
- ✅ **Level 1**: Display & Signals (output)
- ✅ **Level 2**: Config & Paths (configuration)
- ✅ **Level 3**: User Input (interaction)

### Continue Learning

**Layer 1 (Core Services):**
- zAuth - Three-tier authentication
- zDispatch - Command routing
- zNavigation - Menus and breadcrumbs
- zParser - Advanced path resolution
- zLoader - File caching
- zUtils - Plugin system

**Layer 2 (Business Logic):**
- zFunc - Execute Python from YAML
- zDialog - Forms with validation
- zData - Database operations
- zWizard - Multi-step workflows

**Layer 3 (Orchestration):**
- zWalker - Declarative UI from YAML
- zShell - Interactive command center
- zServer - Static file server + zBifrost

### Next Steps

1. **Explore zBifrost** - Turn this Terminal app into a web GUI (zero code changes!)
   - See `Demos/Layer_0/zBifrost_Demo/`
   
2. **Try zWalker** - Build UIs from YAML (no Python code needed!)
   - See `Demos/Archive/01_Foundation/`
   
3. **Build a real app** - Combine all layers
   - See `Demos/Archive/User Manager/` for a complete example

---

**Version**: 1.5.5  
**Difficulty**: Beginner  
**Time**: 15 minutes  
**Prerequisites**: Levels 0-2

