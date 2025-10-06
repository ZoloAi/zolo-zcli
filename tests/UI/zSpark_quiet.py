#!/usr/bin/env python3
"""
zSpark - Walker Launcher for ui.zolo.yaml (Quiet Mode - No System Messages)
"""

from zCLI import zCLI

# zSpark configuration - single source of truth for Walker
zSpark_config = {
    "zSpark": "Zolo UI Walker (Quiet)",  # Label
    "zWorkspace": "/Users/galnachshon/Projects/zolo-zcli",  # Project workspace path
    "zVaFile_path": "@.tests.UI",  # UI file path (workspace-relative)
    "zVaFilename": "ui.zolo",  # UI file name (without .yaml extension)
    "zBlock": "zVaF",  # Starting block in UI file
    "zMode": "Terminal",  # Terminal mode
    "logger": "prod",
    "debug": False  # Hide system messages (sysmsg) - clean production UI
}

if __name__ == "__main__":
    # Create zCLI instance with zSpark configuration
    cli = zCLI(zSpark_config)
    
    # Launch Walker
    cli.run()

