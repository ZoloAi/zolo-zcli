"""
zAuth/zAuth_modules/helpers.py
Authentication helper functions
"""


def check_authentication(zcli):
    """Check if user is authenticated, prompt if not."""
    if not hasattr(zcli, 'auth') or not zcli.auth.is_authenticated():
        zcli.display.handle({"event": "text", "content": ""})
        zcli.display.handle({"event": "text", "content": "[*] Authentication Required"})
        zcli.display.handle({"event": "text", "content": "═" * 50})
        zcli.display.handle({"event": "text", "content": "zCLI requires authentication to use."})
        zcli.display.handle({"event": "text", "content": "Please login with your Zolo credentials."})
        zcli.display.handle({"event": "text", "content": "═" * 50})
        zcli.display.handle({"event": "text", "content": ""})
        
        # Prompt for login
        choice = input("Login now? (y/n): ").strip().lower()
        if choice == 'y':
            result = zcli.auth.login()
            return result.get("status") == "success"
        else:
            zcli.display.handle({"event": "text", "content": ""})
            zcli.display.handle({"event": "text", "content": "[X] Authentication required. Exiting."})
            zcli.display.handle({"event": "text", "content": ""})
            return False
    
    return True

