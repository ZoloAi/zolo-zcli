# zShell Guide - Your Interactive Command Center

**Welcome!** This guide will teach you how to use zCLI's interactive shell - think of it like a conversation with your computer where you type commands and get instant results!

---

## What is zShell?

**zShell** is like a text-based control panel for zCLI. Instead of clicking buttons, you type commands and press Enter. It's similar to:
- The Terminal app on Mac
- Command Prompt on Windows
- The Python interactive shell

**Think of it like:** Texting with your computer - you send a message (command), it responds with results!

---

## Getting Started

### Starting the Shell

```bash
# From your terminal
zcli

# You'll see:
╔═══════════════════════════════════════════════════════════╗
║                    zCLI Interactive Shell                 ║
╚═══════════════════════════════════════════════════════════╝

Type 'help' for available commands
Type 'exit' or 'quit' to leave

>
```

That `>` symbol means the shell is ready for your command!

### Your First Commands

```bash
# Say hello!
> echo Hello World
Hello World

# Check where you are
> pwd
Current Working Directory
  /Users/yourname/Projects

# Get help
> help
[Shows list of all commands]

# Exit when done
> exit
Goodbye!
```

---

## Essential Commands (Like Bash!)

### 1. echo - Print Messages

**What it does:** Displays text on the screen

```bash
# Simple message
> echo Hello there!
Hello there!

# Show a variable
> echo $zWorkspace
/Users/yourname/Projects/my_project

# Colored output
> echo --success Task complete!
✅ Task complete!

> echo --error Something went wrong
❌ Something went wrong
```

**Use it for:** Testing, displaying information, debugging

---

### 2. pwd - Where Am I?

**What it does:** Shows your current directory (like "You Are Here" on a map)

```bash
> pwd
Current Working Directory
  /Users/yourname/Projects/my_project
  (as zPath: ~.Projects.my_project)
```

**Use it for:** Checking your location before running commands

---

### 3. ls - List Files

**What it does:** Shows files and folders in a directory

```bash
# List current directory
> ls
Directory: /Users/yourname/Projects
Directories:
  📁 zTestSuite/
  📁 Documentation/
Files:
  📄 README.md
  📄 main.py
Total: 2 directories, 2 files

# List specific folder
> ls @.zTestSuite.demos
[Shows demo files]

# Show hidden files too
> ls --all

# Show file sizes
> ls --long
```

**Use it for:** Seeing what files you have, finding things

---

### 4. cd - Change Directory

**What it does:** Moves you to a different folder

```bash
# Go to a folder
> cd @.zTestSuite.demos
Changed directory to: /Users/yourname/Projects/zTestSuite/demos

# Go home
> cd ~
Changed directory to: /Users/yourname

# Go up one level
> cd ..
Changed directory to: /Users/yourname/Projects

# Go back home (no arguments)
> cd
Changed directory to: /Users/yourname
```

**Use it for:** Navigating your project folders

---

### 5. history - Remember Commands

**What it does:** Shows all the commands you've typed

```bash
# Show history
> history
Command History (showing 5 of 5 total)
   1: echo Hello
   2: pwd
   3: ls
   4: cd @.zTestSuite.demos
   5: history

# Search history
> history search echo
History Search: 'echo' (1 matches)
   1: echo Hello

# Clear history
> history --clear
Command history cleared (5 entries removed)

# Save history to file
> history save my_commands.json
History saved to: my_commands.json
(5 entries)
```

**Use it for:** Remembering what you did, repeating commands

---

### 6. alias - Create Shortcuts

**What it does:** Makes short names for long commands

```bash
# Create an alias
> alias ll="ls --long --all"
Alias created: ll → ls --long --all

# Use your alias
> ll
[Shows detailed file listing]

# List all aliases
> alias
Defined Aliases (1)
  ll → ls --long --all

# Remove an alias
> alias --remove ll
Alias removed: ll

# Save aliases
> alias --save
Aliases saved to: ~/.zcli/aliases.json
```

**Use it for:** Making your favorite commands shorter

---

## Working with Data

### load - Load a Database Schema

**What it does:** Loads a database schema so you can work with data

```bash
# Load a schema
> load @.zTestSuite.demos.zSchema.sqlite_demo --as mydb
Schema loaded and cached as: mydb

# Show what's loaded
> load --show
Pinned Cache (1 schemas):
  mydb → @.zTestSuite.demos.zSchema.sqlite_demo

# Clear a schema
> load --clear mydb
Schema 'mydb' removed from cache
```

**Why use it:** Load once, use many times with the short name!

---

### data - Work with Your Data

**What it does:** Read, add, update, or delete data in your database

```bash
# View data
> data read users --model $mydb --limit 5
[Shows first 5 users in a table]

# Add data
> data insert users --model $mydb --fields name,age --values "Alice",16
Record inserted successfully

# Update data
> data update users --model $mydb --fields age --values 17 --where "name = 'Alice'"
Record updated successfully

# Delete data
> data delete users --model $mydb --where "age < 13"
Records deleted successfully
```

**Use it for:** Managing your homework tracker, contact list, inventory, etc.

---

## Multi-Step Workflows (Wizard Mode)

### What is Wizard Mode?

**Wizard mode** lets you prepare multiple commands and run them all at once - like making a recipe where you gather all ingredients before cooking!

### How to Use It

```bash
# 1. Start wizard mode
> wizard --start
📝 Wizard Canvas Mode Active
   Type commands or YAML, then 'wizard --run' to execute

# 2. Add your commands (they won't run yet!)
> data insert users --model $mydb --fields name,age --values "Bob",15
> data insert users --model $mydb --fields name,age --values "Carol",16

# 3. Check what you've added
> wizard --show
Wizard Buffer (2 lines):
  1: data insert users --model $mydb --fields name,age --values "Bob",15
  2: data insert users --model $mydb --fields name,age --values "Carol",16

# 4. Run everything at once
> wizard --run
Executing wizard buffer (2 lines)...
✅ 2 commands executed successfully
Buffer cleared after execution

# 5. Exit wizard mode
> wizard --stop
Exited wizard canvas - 0 lines discarded
```

### Why Use Wizard Mode?

- **All or nothing:** If one command fails, everything is undone (like Ctrl+Z)
- **Faster:** Multiple operations happen together
- **Safer:** Test your commands before running them
- **Organized:** See all steps before executing

---

## Getting Help

### General Help

```bash
> help
╔═══════════════════════════════════════════════════════════╗
║                    zCLI Interactive Shell                 ║
╚═══════════════════════════════════════════════════════════╝

Available Commands:
  echo         - Print messages and variables
  pwd          - Print working directory
  ls           - List directory contents
  cd           - Change directory
  history      - Command history management
  alias        - Create command shortcuts
  data         - Data operations (CRUD)
  load         - Load and cache resources
  wizard       - Multi-step workflow orchestration
  [... and more ...]

General:
  help [command]  - Show help (or help for specific command)
  tips            - Show quick tips
  clear/cls       - Clear screen
  exit/quit/q     - Exit shell
```

### Command-Specific Help

```bash
> help data
DATA Command Help
═════════════════════════════════════════════════════════════

Description:
  Data operations (CRUD)

Usage:
  data read <table> [--model PATH] [--limit N]
  data insert <table> [--model PATH] [--fields ...] [--values ...]
  [... more examples ...]

Examples:
  data read users --model @.zTestSuite.demos.zSchema.sqlite_demo
  data insert users --model $mydb --fields name --values "Alice"
```

---

## Useful Tips

### Tip 1: Use Aliases for Common Tasks

```bash
# Create shortcuts for things you do often
> alias demos="cd @.zTestSuite.demos"
> alias ll="ls --long --all"
> alias loaddb="load @.zTestSuite.demos.zSchema.sqlite_demo --as db"

# Now you can just type:
> demos
> ll
> loaddb
```

### Tip 2: Check Your Work with pwd and ls

```bash
# Always know where you are
> pwd
> ls

# Before running important commands
> pwd
> echo I am about to delete files here!
```

### Tip 3: Use History to Repeat Commands

```bash
# Find a command you ran before
> history search data
History Search: 'data' (3 matches)
   5: data read users --model $mydb
  12: data insert users --model $mydb --fields name --values "Alice"
  18: data update users --model $mydb --where "id = 1"

# Then copy and modify it!
```

### Tip 4: Test with echo Before Running

```bash
# Not sure what a variable contains?
> echo $mydb
@.zTestSuite.demos.zSchema.sqlite_demo

# Check before using it
> data read users --model $mydb
```

### Tip 5: Use Wizard Mode for Important Operations

```bash
# When adding multiple related things
> wizard --start
> data insert users --model $mydb --fields name --values "Alice"
> data insert posts --model $mydb --fields title,author --values "Hello","Alice"
> wizard --run

# If anything fails, NOTHING changes!
```

---

## Common Patterns

### Pattern 1: Load and Query

```bash
# Load your database
> load @.zTestSuite.demos.zSchema.sqlite_demo --as db

# Query it
> data read users --model $db --limit 10

# Add something
> data insert users --model $db --fields name,age --values "Alice",16
```

### Pattern 2: Navigate and Explore

```bash
# See where you are
> pwd

# List files
> ls

# Go somewhere
> cd @.zTestSuite.demos

# List again
> ls
```

### Pattern 3: Create Workflow

```bash
# Start wizard
> wizard --start

# Add steps
> data insert students --model $db --fields name,grade --values "Bob",10
> data insert homework --model $db --fields student,subject --values "Bob","Math"

# Review
> wizard --show

# Execute
> wizard --run
```

---

## Quick Reference Card

### Navigation
```bash
pwd              # Where am I?
ls               # What's here?
cd <path>        # Go somewhere
cd ..            # Go up one level
cd ~             # Go home
```

### Files & Info
```bash
echo <message>   # Print something
history          # Show past commands
alias            # Show shortcuts
help             # Get help
help <command>   # Help for specific command
```

### Data Operations
```bash
load <path> --as <name>     # Load schema
data read <table>           # View data
data insert <table>         # Add data
data update <table>         # Change data
data delete <table>         # Remove data
```

### Wizard Mode
```bash
wizard --start   # Begin workflow
wizard --show    # Review steps
wizard --run     # Execute all
wizard --stop    # Exit mode
wizard --clear   # Clear buffer
```

### Shell Control
```bash
clear / cls      # Clear screen
exit / quit / q  # Leave shell
```

---

## Practice Exercises

### Exercise 1: Basic Navigation

Try these commands in order:
```bash
1. pwd                    # See where you are
2. ls                     # See what's here
3. cd @.zTestSuite.demos  # Go to demos folder
4. ls                     # See demo files
5. cd ..                  # Go back up
6. pwd                    # Confirm location
```

### Exercise 2: Working with Data

```bash
1. load @.zTestSuite.demos.zSchema.sqlite_demo --as db
2. data read users --model $db --limit 5
3. echo I see the users!
4. history
```

### Exercise 3: Create Shortcuts

```bash
1. alias demos="cd @.zTestSuite.demos"
2. alias showusers="data read users --model $db --limit 10"
3. alias
4. demos
5. showusers
```

### Exercise 4: Wizard Workflow

```bash
1. wizard --start
2. echo Step 1
3. echo Step 2
4. wizard --show
5. wizard --run
6. wizard --stop
```

---

## Troubleshooting

### "Command not found"

```bash
> dataa read users
❌ Unknown command: dataa

# Fix: Check spelling
> data read users
✅ Works!

# Or get help
> help
```

### "Path not found"

```bash
> cd @.wrong.path
❌ Directory not found

# Fix: Check with ls first
> ls
> cd @.correct.path
```

### "Schema not loaded"

```bash
> data read users --model $mydb
❌ Schema 'mydb' not found

# Fix: Load it first
> load @.zTestSuite.demos.zSchema.sqlite_demo --as mydb
> data read users --model $mydb
```

### Stuck in Wizard Mode?

```bash
# Exit wizard mode
> wizard --stop
Exited wizard canvas

# Or clear and exit
> wizard --clear
> wizard --stop
```

---

## Next Steps

Now that you know the shell basics:

1. **Try the demos:** `cd @.zTestSuite.demos` and explore
2. **Create your own database:** Use zSchema to define your data
3. **Build workflows:** Use wizard mode for multi-step tasks
4. **Make shortcuts:** Create aliases for your common commands
5. **Read other guides:**
   - [zUI_GUIDE.md](zUI_GUIDE.md) - Build interactive menus
   - [zSchema_GUIDE.md](zSchema_GUIDE.md) - Define your data
   - [zData_GUIDE.md](zData_GUIDE.md) - Advanced data operations

---

## Remember

- **Type `help` when stuck** - It's always there to help you!
- **Use `pwd` often** - Know where you are
- **Test with `echo`** - Check variables before using them
- **Save your work** - Use `history save` and `alias --save`
- **Wizard mode is your friend** - Use it for important operations
- **Practice makes perfect** - The more you use it, the easier it gets!

---

## Quick Start Checklist

✅ Start the shell: `zcli`  
✅ Get help: `help`  
✅ Check location: `pwd`  
✅ List files: `ls`  
✅ Load a database: `load @.path --as name`  
✅ View data: `data read table --model $name`  
✅ Create shortcuts: `alias name="command"`  
✅ Save history: `history save`  
✅ Exit: `exit`

**You've got this!** 🚀

---

**Total Commands Available:** 20  
**Difficulty:** Beginner-Friendly  
**Best For:** Students, beginners, anyone new to command-line tools
