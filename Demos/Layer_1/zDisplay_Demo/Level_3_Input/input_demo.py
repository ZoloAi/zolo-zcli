"""
Level 3: User Input - Primitives Only
======================================

Demonstrates zDisplay's primitive input methods:
- read_string() - Plain text input
- read_password() - Masked password input
- Storing inputs in session["zVars"] for cross-mode compatibility

Key Concept: Store inputs in zVars for clean async handling in Bifrost mode

Note: Complex inputs (selection, menus, dialogs) are covered in advanced tutorials.
"""

from zCLI import zCLI

# Initialize zCLI
z = zCLI()

# Initialize zVars for input storage
if "zVars" not in z.session:
    z.session["zVars"] = {}

# ============================================
# Introduction
# ============================================
z.display.header("Level 3: User Input Demo", color="CYAN")
z.display.text("Collect user input and store in session variables")
z.display.info("All methods work in Terminal AND Bifrost modes!")
z.display.info("💡 Inputs are stored in session['zVars'] for easy access")
z.display.text("")

# ============================================
# 1. String Input → Stored in zVars
# ============================================
z.display.header("1. String Input", color="GREEN")
z.display.text("Collect plain text and store in session:")

# Collect and store in zVars
z.session["zVars"]["name"] = z.display.read_string("Enter your name: ")

# Access from zVars
z.display.success(f"✅ Hello, {z.session['zVars']['name']}!")
z.display.info("Stored in: session['zVars']['name']")

z.display.text("")

# ============================================
# 2. Password Input → Stored in zVars
# ============================================
z.display.header("2. Password Input", color="YELLOW")
z.display.text("Masked input stored in session:")

# Collect and store in zVars
z.session["zVars"]["password"] = z.display.read_password("Enter a password: ")

# Access from zVars
pwd_len = len(z.session["zVars"]["password"])
z.display.success(f"✅ Password received ({pwd_len} characters)")
z.display.info("Stored in: session['zVars']['password']")
z.display.warning("⚠️  In real apps, hash passwords before storing!")

z.display.text("")

# ============================================
# 3. View All Collected Inputs
# ============================================
z.display.header("3. Session Variables Summary", color="BLUE")
z.display.text("All inputs collected and stored in session['zVars']:")
z.display.text("")

# Display collected data (mask password for security)
collected_data = {
    "name": z.session["zVars"]["name"],
    "password": "*" * len(z.session["zVars"]["password"])  # Masked
}
z.display.json_data(collected_data)

z.display.text("")
z.display.success("✅ All inputs stored in session and accessible!")

# ============================================
# Summary
# ============================================
z.display.text("")
z.display.header("Summary", color="MAGENTA")
z.display.text("You've learned about:")
features_learned = [
    "read_string() - Plain text input with prompt",
    "read_password() - Masked password input (hidden characters)",
    "session['zVars'] - Store inputs for session-wide access",
    "Cross-mode compatibility - Same pattern works in Terminal & Bifrost",
    "Async handling - zVars isolate async complexity in Bifrost mode"
]
z.display.list(features_learned)

z.display.text("")
z.display.success("🎉 Input primitives + zVars mastered!")
z.display.text("")
z.display.info("💡 Next: Learn zBifrost to turn this Terminal demo into a web GUI!")

