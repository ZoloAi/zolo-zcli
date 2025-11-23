#!/usr/bin/env python3
"""
Level 2: zSettings (zSpark Entry Point)
======================================

Goal:
    Use zSpark_obj as the *first* way to influence zConfig settings (mode, traceback,
    logger level) before touching YAML or .zEnv files. This is the minimal control
    surface for runtime settings.

Run:
    python3 Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zspark_demo.py
"""


from zCLI import zCLI


def run_demo():
    z = zCLI({
        "zMode": "Terminal",
        "logger": "PROD",
    })
    session = z.session

    print("\n# Session state (copy/paste these lines):")
    print(f"zMode           : {session.get('zMode')}")
    print(f"zSpace          : {session.get('zSpace')}")
    print(f"zTraceback      : {session.get('zTraceback')}")
    print(f"zLogger (level) : {session.get('zLogger')}")
    print(f"Stored zSpark   : {session.get('zSpark')}")


if __name__ == "__main__":
    run_demo()
