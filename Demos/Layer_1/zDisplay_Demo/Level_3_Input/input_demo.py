"""
Level 3: User Input
====================

Demonstrates zDisplay's input capabilities:
- String input (plain text)
- Password input (masked)
- Single selection (choose one)
- Multi-selection (choose multiple)
- Interactive menus (numbered options)

Key Concept: Same input API works in Terminal (input()) and GUI (HTML forms)
"""

from zCLI import zCLI

# Initialize zCLI
z = zCLI()

# ============================================
# Introduction
# ============================================
z.display.header("Level 3: User Input Demo", color="CYAN")
z.display.text("This demo shows how to collect user input in zCLI")
z.display.info("All methods work in Terminal AND GUI mode!")
z.display.text("")

# ============================================
# 1. String Input
# ============================================
z.display.header("1. String Input", color="GREEN")
z.display.text("Collect plain text from the user:")

name = z.display.read_string("Enter your name: ")
z.display.success(f"✅ Hello, {name}!")

age = z.display.read_string("Enter your age: ")
z.display.success(f"✅ You are {age} years old")

z.display.text("")

# ============================================
# 2. Password Input (masked)
# ============================================
z.display.header("2. Password Input", color="YELLOW")
z.display.text("Passwords are masked with * characters:")

password = z.display.read_password("Enter a password: ")
z.display.success(f"✅ Password received ({len(password)} characters)")
z.display.info(f"First character: {password[0] if password else 'N/A'}")
z.display.warning("⚠️  In real apps, hash passwords before storing!")

z.display.text("")

# ============================================
# 3. Single Selection
# ============================================
z.display.header("3. Single Selection", color="BLUE")
z.display.text("Choose one option from a list:")
z.display.info("Use arrow keys (↑↓) to navigate, Enter to select")

environments = ["Development", "Staging", "Production"]
env = z.display.selection(
    "Choose deployment environment:",
    environments
)
z.display.success(f"✅ Selected: {env}")

z.display.text("")

# ============================================
# 4. Multi-Selection
# ============================================
z.display.header("4. Multi-Selection", color="MAGENTA")
z.display.text("Choose multiple options from a list:")
z.display.info("Use arrow keys (↑↓) to navigate, Space to toggle, Enter to confirm")

feature_options = ["Logging", "Caching", "Debugging", "Profiling", "Analytics"]
features = z.display.selection(
    "Enable features (select multiple):",
    feature_options,
    multi=True
)

if features:
    z.display.success(f"✅ Enabled {len(features)} features:")
    for feature in features:
        z.display.text(f"  • {feature}", indent=1)
else:
    z.display.warning("No features selected")

z.display.text("")

# ============================================
# 5. Interactive Menu
# ============================================
z.display.header("5. Interactive Menu", color="CYAN")
z.display.text("Numbered menu options (type number and press Enter):")

menu_items = [
    (1, "View Profile"),
    (2, "Edit Settings"),
    (3, "View Logs"),
    (4, "Logout"),
]

choice = z.display.zMenu(
    menu_items,
    prompt="Choose an option:",
    return_selection=True
)

z.display.success(f"✅ You selected option {choice}")

# Map choice to action
action_map = {
    1: "Viewing profile...",
    2: "Opening settings...",
    3: "Loading logs...",
    4: "Logging out...",
}
z.display.info(action_map.get(choice, "Unknown action"))

z.display.text("")

# ============================================
# 6. Putting It All Together: Mini Registration Form
# ============================================
z.display.header("6. Complete Form Example", color="GREEN")
z.display.text("A simple registration form combining all input types:")

# Collect user data
z.display.text("Registration Form", indent=0)
username = z.display.read_string("  Username: ")
email = z.display.read_string("  Email: ")
password = z.display.read_password("  Password: ")

role = z.display.selection(
    "  Select role:",
    ["Admin", "Editor", "Viewer"]
)

permissions = z.display.selection(
    "  Select permissions:",
    ["Read", "Write", "Delete", "Share"],
    multi=True
)

# Display summary
z.display.text("")
z.display.header("Registration Summary", color="BLUE")

summary_data = {
    "Username": username,
    "Email": email,
    "Password": "*" * len(password),  # Masked
    "Role": role,
    "Permissions": ", ".join(permissions) if permissions else "None"
}

z.display.json_data(summary_data)

z.display.text("")
z.display.success("✅ Registration complete!")

# ============================================
# Summary
# ============================================
z.display.text("")
z.display.header("Summary", color="MAGENTA")
z.display.text("You've learned about:")
features_learned = [
    "read_string() - Plain text input",
    "read_password() - Masked password input",
    "selection() - Single choice from list",
    "selection(multi=True) - Multiple choices from list",
    "zMenu() - Numbered menu options",
    "Building complete forms by combining input methods"
]
z.display.list(features_learned)

z.display.text("")
z.display.success("🎉 Congratulations! You've completed the Layer 0 Terminal Tutorial!")
z.display.text("")
z.display.info("Next steps:")
z.display.text("  • Explore zBifrost - Turn Terminal apps into web GUIs", indent=1)
z.display.text("  • Learn zWalker - Build UIs from YAML", indent=1)
z.display.text("  • Try zData - Database operations", indent=1)
z.display.text("  • Build a real app - Combine all layers", indent=1)

