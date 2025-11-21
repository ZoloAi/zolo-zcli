"""
Level 6: Fire-and-Forget Pattern
=================================

Key: read_string() and read_password() return Futures in Bifrost mode.
Send all requests first, await after → all forms render simultaneously.
"""

from zCLI import zCLI

# Initialize zCLI in Bifrost mode (same as Level 5)
z = zCLI({
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False
    }
})

# Initialize zVars for input storage
if "zVars" not in z.session:
    z.session["zVars"] = {}


async def handle_show_inputs(_websocket, _message_data):
    """Fire-and-Forget: Send all input requests, then await responses."""
    
    z.display.header("Fire-and-Forget Pattern", color="CYAN")
    z.display.text("7 inputs (string, string, password, selection, multi-selection, button, button)!")
    z.display.text("")
    
    # 🔥 FIRE: Send all requests (don't await)
    future_name = z.display.read_string("Enter your name: ")
    future_email = z.display.read_string("Enter your email: ")
    future_password = z.display.read_password("Enter password: ")
    future_role = z.display.selection("Select your role:", ["Developer", "Designer", "Manager", "Other"])
    future_skills = z.display.selection("Select your skills:", ["Python", "JavaScript", "React", "Django", "zCLI"], multi=True, default=["Python", "zCLI"])
    future_save = z.display.button("Save Profile", action="save_profile", color="success")
    future_delete = z.display.button("Delete Account", action="delete_account", color="danger")
    
    z.display.info("💡 All 7 forms should now be visible!")
    z.display.text("")
    
    # ⏳ COLLECT: Await responses
    name_value = await future_name
    z.session["zVars"]["name"] = name_value
    z.display.success(f"Name: {name_value}")
    
    email_value = await future_email
    z.session["zVars"]["email"] = email_value
    z.display.success(f"Email: {email_value}")
    
    password_value = await future_password
    z.session["zVars"]["password_length"] = len(password_value)
    z.display.success(f"Password: {'•' * len(password_value)} ({len(password_value)} chars)")
    
    role_value = await future_role
    z.session["zVars"]["role"] = role_value
    z.display.success(f"Role: {role_value}")
    
    skills_value = await future_skills
    z.session["zVars"]["skills"] = skills_value
    z.display.success(f"Skills: {', '.join(skills_value) if skills_value else 'None selected'}")
    
    save_clicked = await future_save
    z.session["zVars"]["profile_saved"] = save_clicked
    if save_clicked:
        z.display.success("✅ Profile saved successfully!")
    else:
        z.display.info("Profile save cancelled.")
    
    delete_clicked = await future_delete
    z.session["zVars"]["account_deleted"] = delete_clicked
    if delete_clicked:
        z.display.warning("⚠️ Account marked for deletion!")
    else:
        z.display.info("Account deletion cancelled.")
    
    # Summary
    z.display.text("")
    z.display.header("Summary", color="BLUE")
    z.display.json_data(z.session["zVars"])


# Register handler
z.comm.websocket._event_map['show_inputs'] = handle_show_inputs  # noqa: SLF001

print("ws://127.0.0.1:8765")
print("👉 Open input_client.html")

# Start server
z.walker.run()

