# Level 3: User Input - Primitives Only

**Difficulty:** Beginner  
**Prerequisites:** Level 0 (Hello), Level 1 (Display), Level 2 (Config & zVars)

---

## 🎯 What You'll Build

An interactive Terminal app that demonstrates zDisplay's **primitive input methods** with the **zVars pattern** for cross-mode compatibility:

1. **String Input** - `read_string()` for text collection
2. **Password Input** - `read_password()` for masked entry
3. **Session Storage** - Store inputs in `session["zVars"]`

---

## 🚀 Quick Start

```bash
cd Demos/Layer_1/zDisplay_Demo/Level_3_Input
python3 input_demo.py
```

The script will:
1. Initialize `session["zVars"]` for input storage
2. Prompt you for your name (stored in zVars)
3. Ask for a password (masked with `*`, stored in zVars)
4. Display all collected inputs from zVars in JSON format

---

## 📚 What You'll Learn

### 1. Primitive Input Methods

**String Input:**
```python
z.session["zVars"]["name"] = z.display.read_string("Enter your name: ")
z.display.success(f"Hello, {z.session['zVars']['name']}!")
```

**Password Input:**
```python
z.session["zVars"]["password"] = z.display.read_password("Enter password: ")
pwd_len = len(z.session["zVars"]["password"])
z.display.success(f"Password received ({pwd_len} characters)")
```

### 2. The zVars Pattern

**Why use `session["zVars"]`?**

✅ **Cross-mode compatibility** - Same pattern works in Terminal & Bifrost  
✅ **Async isolation** - In Bifrost, `await` only in input collection  
✅ **Session-wide access** - Inputs available across handlers  
✅ **Clean code** - Display logic reads synchronously (no `await` needed)

**Example:**
```python
# Initialize once
if "zVars" not in z.session:
    z.session["zVars"] = {}

# Collect and store
z.session["zVars"]["email"] = z.display.read_string("Email: ")

# Access many times (no repeated prompts)
z.display.info(f"Email: {z.session['zVars']['email']}")
z.display.info(f"Domain: {z.session['zVars']['email'].split('@')[1]}")
```

### 3. Terminal vs. Bifrost Return Types

| Mode | `read_string()` | `read_password()` |
|------|-----------------|-------------------|
| **Terminal** | Returns `str` immediately | Returns `str` immediately |
| **Bifrost** | Returns `asyncio.Future` (needs `await`) | Returns `asyncio.Future` (needs `await`) |

**In Terminal:**
```python
name = z.display.read_string("Name: ")  # Returns str
```

**In Bifrost:**
```python
name = await z.display.read_string("Name: ")  # Returns str after await
```

**With zVars, both modes use same storage pattern!**

---

## 🎨 The Code

**Complete Example:**
```python
from zCLI import zCLI

z = zCLI()

# Initialize zVars
if "zVars" not in z.session:
    z.session["zVars"] = {}

# 1. String Input → Store in zVars
z.session["zVars"]["name"] = z.display.read_string("Enter your name: ")
z.display.success(f"✅ Hello, {z.session['zVars']['name']}!")

# 2. Password Input → Store in zVars
z.session["zVars"]["password"] = z.display.read_password("Enter password: ")
pwd_len = len(z.session["zVars"]["password"])
z.display.success(f"✅ Password received ({pwd_len} characters)")

# 3. Display all collected inputs
collected_data = {
    "name": z.session["zVars"]["name"],
    "password": "*" * len(z.session["zVars"]["password"])  # Masked
}
z.display.json_data(collected_data)
```

---

## 🧪 Experiments

### 1. Add More Inputs

```python
# Add email
z.session["zVars"]["email"] = z.display.read_string("Email: ")

# Add age
z.session["zVars"]["age"] = z.display.read_string("Age: ")

# Display all
z.display.json_data(z.session["zVars"])
```

### 2. Add Validation

```python
# Validate age
age_str = z.display.read_string("Age: ")
try:
    z.session["zVars"]["age"] = int(age_str)
    if z.session["zVars"]["age"] < 18:
        z.display.warning("You must be 18+ to continue")
    else:
        z.display.success("Age verified!")
except ValueError:
    z.display.error("Age must be a number!")
```

### 3. Build a Registration Form

```python
z.display.header("User Registration", color="CYAN")

# Collect inputs
z.session["zVars"]["full_name"] = z.display.read_string("Full name: ")
z.session["zVars"]["email"] = z.display.read_string("Email: ")
z.session["zVars"]["password"] = z.display.read_password("Password: ")
z.session["zVars"]["confirm"] = z.display.read_password("Confirm password: ")

# Validate
if z.session["zVars"]["password"] != z.session["zVars"]["confirm"]:
    z.display.error("Passwords don't match!")
else:
z.display.success("Registration complete!")
    z.display.info(f"Welcome, {z.session['zVars']['full_name']}!")
```

---

## 🔍 Behind the Scenes

### Terminal Mode
```python
# zDisplay uses Python's built-in input()
def read_string(prompt):
    return input(prompt)

# For passwords, uses getpass (masked input)
import getpass
def read_password(prompt):
    return getpass.getpass(prompt)
```

### Bifrost Mode
```python
# zDisplay sends WebSocket event
async def read_string(prompt):
    request_id = generate_id()
    websocket.send({
        "event": "input_request",
        "requestId": request_id,
        "type": "string",
        "prompt": prompt
    })
    # Wait for response from browser
    return await future  # Returns when user submits form
```

**You never write this!** zDisplay handles mode detection automatically.

---

## ✅ Success Checklist

- ✅ **String input works** - You can enter your name
- ✅ **Password is masked** - Shows `*` instead of characters
- ✅ **zVars storage works** - Inputs stored in `session["zVars"]`
- ✅ **JSON display works** - Summary shows collected data

---

## 💡 Key Takeaways

1. **Primitive inputs** - `read_string()` and `read_password()` are the foundation
2. **zVars pattern** - Store in `session["zVars"]` for cross-mode compatibility
3. **Return types** - Terminal: `str`, Bifrost: `asyncio.Future` (needs `await`)
4. **No complex logic** - Focus on zDisplay behavior, not Python syntax

---

## 📖 Next Steps

**Ready for Bifrost?**
- **Level 6 (Bifrost):** Turn this Terminal demo into a web GUI!
  - See `Demos/Layer_0/zBifrost_Demo/Level_6_inputs/`
  - Same code structure, just add `await` for inputs
  - BifrostClient auto-renders HTML forms

**Want Complex Inputs?**
- Advanced tutorials cover `selection()`, `zMenu()`, `zDialog()`
- Build multi-step wizards with validation
- Create interactive menus with arrow key navigation

---

**Congratulations!** 🎉 You've mastered primitive input collection with the zVars pattern!

**Version**: 1.5.5  
**Time**: 10 minutes
