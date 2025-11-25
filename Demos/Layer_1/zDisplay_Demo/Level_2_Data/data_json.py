#!/usr/bin/env python3
"""
Level 2: JSON Display
======================

Goal:
    Learn json_data() for pretty-printing structured data.
    - Automatic formatting and indentation
    - Optional color syntax highlighting
    - Perfect for configs and API responses

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_2_Data/data_json.py
"""

from zCLI import zCLI

def run_demo():
    """Demonstrate JSON data display."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== Level 2: JSON Display ===")
    print()
    
    # ============================================
    # 1. Simple JSON
    # ============================================
    z.display.header("Simple JSON", color="CYAN", indent=0)
    z.display.text("Basic configuration object:")
    
    simple_config = {
        "app_name": "MyApp",
        "version": "1.0.0",
        "debug": True,
        "port": 8080
    }
    z.display.json_data(simple_config, indent=1)
    z.display.text("")
    
    # ============================================
    # 2. Nested JSON
    # ============================================
    z.display.header("Nested JSON", color="GREEN", indent=0)
    z.display.text("Complex configuration with nested objects:")
    
    nested_config = {
        "version": "1.5.5",
        "mode": "Terminal",
        "subsystems": {
            "zConfig": "loaded",
            "zDisplay": "loaded",
            "zComm": "loaded"
        },
        "features": [
            "ANSI colors",
            "Interactive input",
            "Smart formatting"
        ],
        "debug": True
    }
    z.display.json_data(nested_config, indent=1)
    z.display.text("")
    
    # ============================================
    # 3. API Response Example
    # ============================================
    z.display.header("API Response Example", color="YELLOW", indent=0)
    z.display.text("Typical REST API response:")
    
    api_response = {
        "status": "success",
        "code": 200,
        "data": {
            "user": {
                "id": 42,
                "name": "Alice",
                "email": "alice@example.com",
                "roles": ["admin", "developer"]
            },
            "session": {
                "token": "abc123xyz789",
                "expires": "2024-12-31T23:59:59Z"
            }
        },
        "meta": {
            "timestamp": "2024-01-15T10:30:00Z",
            "request_id": "req-123456"
        }
    }
    z.display.json_data(api_response, indent=1)
    z.display.text("")
    
    # ============================================
    # 4. Array of Objects
    # ============================================
    z.display.header("Array of Objects", color="MAGENTA", indent=0)
    z.display.text("List of users from database:")
    
    users_list = {
        "total": 3,
        "users": [
            {"id": 1, "name": "Alice", "active": True},
            {"id": 2, "name": "Bob", "active": False},
            {"id": 3, "name": "Charlie", "active": True}
        ]
    }
    z.display.json_data(users_list, indent=1)
    z.display.text("")
    
    # ============================================
    # 5. Custom Indentation
    # ============================================
    z.display.header("Custom Indentation", color="BLUE", indent=0)
    z.display.text("Same data with indent_size=4 (default is 2):")
    
    compact_data = {
        "name": "zCLI",
        "layers": {
            "0": "Foundation",
            "1": "Core Services",
            "2": "Business Logic"
        }
    }
    z.display.json_data(compact_data, indent_size=4, indent=1)
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ json_data() - Pretty-print Python dicts")
    z.display.text("✓ Automatic indentation and formatting")
    z.display.text("✓ indent_size parameter - Control JSON spacing")
    z.display.text("✓ Works with nested objects and arrays")
    z.display.text("✓ Perfect for configs, API responses, debug output")
    z.display.text("")
    
    print("Tip: json_data() makes complex data structures readable!")
    print()

if __name__ == "__main__":
    run_demo()

