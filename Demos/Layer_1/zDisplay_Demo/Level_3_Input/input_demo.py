"""
Level 3: User Input - Terminal Mode
====================================

Demonstrates zDisplay's input methods:
- read_string() - Plain text input
- read_password() - Masked password input
- selection() - Single and multi-select
- Storing inputs in session["zVars"]

Key: SAME CODE works in Terminal AND Bifrost modes!
"""

from zCLI import zCLI

# Initialize zCLI
z = zCLI()

# Initialize zVars for input storage
if "zVars" not in z.session:
    z.session["zVars"] = {}

# ============================================
# SAME LOGIC as Bifrost demo (input_bifrost.py)
# ============================================
z.display.header("Fire-and-Forget Pattern", color="CYAN")
z.display.text("5 inputs (string, string, password, selection, multi-selection)!")
z.display.text("")

# Terminal mode: Direct execution (no await needed)
name_value = z.display.read_string("Enter your name: ")
z.session["zVars"]["name"] = name_value
z.display.success(f"Name: {name_value}")

email_value = z.display.read_string("Enter your email: ")
z.session["zVars"]["email"] = email_value
z.display.success(f"Email: {email_value}")

password_value = z.display.read_password("Enter password: ")
z.session["zVars"]["password_length"] = len(password_value)
z.display.success(f"Password: {'•' * len(password_value)} ({len(password_value)} chars)")

role_value = z.display.selection("Select your role:", ["Developer", "Designer", "Manager", "Other"])
z.session["zVars"]["role"] = role_value
z.display.success(f"Role: {role_value}")

skills_value = z.display.selection("Select your skills:", ["Python", "JavaScript", "React", "Django", "zCLI"], multi=True, default=["Python", "zCLI"])
z.session["zVars"]["skills"] = skills_value
z.display.success(f"Skills: {', '.join(skills_value) if skills_value else 'None selected'}")

# Summary
z.display.text("")
z.display.header("Summary", color="BLUE")
z.display.json_data(z.session["zVars"])

