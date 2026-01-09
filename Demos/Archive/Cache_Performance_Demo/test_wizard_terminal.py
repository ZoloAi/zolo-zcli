#!/usr/bin/env python3
"""
Test zWizard sequence in Terminal mode
Tests the cache demo wizard without WebSocket complexity
"""

import sys
from pathlib import Path

# IMPORTANT: Force Python to use LOCAL workspace version
workspace_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(workspace_root))
print(f"🔧 Using local zCLI from: {workspace_root}")

from zKernel import zKernel

def main():
    print("=" * 60)
    print("🧪 Testing zWizard Sequence - Terminal Mode")
    print("=" * 60)
    print()
    
    # Use Cache_Performance_Demo directory
    current_dir = Path(__file__).parent
    print(f"📁 Workspace: {current_dir}")
    
    # Initialize zCLI in Terminal mode
    z = zKernel({
        "zWorkspace": str(current_dir),
        "zVaFile": "@.zUI.cache_demo",
        "zBlock": "zVaF",
        "zMode": "Terminal",  # Terminal mode for testing
        "zTraceback": False,  # Disable interactive prompts for automated testing
        "zPlugin": ["@.cache_test_aggregator"],
    })
    
    print()
    print("=" * 60)
    print("🚀 Executing zWizard: ^Run All Cache Tests")
    print("=" * 60)
    print()
    
    try:
        # Execute the wizard command using zDispatch with walker context
        result = z.dispatch.handle(
            zKey="^Run All Cache Tests", 
            zHorizontal="^Run All Cache Tests",
            walker=z.walker  # Provide walker context for ^ modifier
        )
        
        print()
        print("=" * 60)
        print("✅ zWizard Result:")
        print("=" * 60)
        print()
        
        if result:
            import json
            print(json.dumps(result, indent=2))
        else:
            print("⚠️  No result returned")
            
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Error:")
        print("=" * 60)
        print(f"{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

