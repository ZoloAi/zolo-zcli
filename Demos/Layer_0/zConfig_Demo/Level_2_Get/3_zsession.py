#!/usr/bin/env python3
"""
Level 1: zSession Get
==============================

Goal:
    Show key zSession values that are influenced by zSpark, so you can
    copy/paste these accessors into your own code.

Run:
    python3 Demos/Layer_0/zConfig_Demo/Level_1_Get/zsession_get.py
"""

from zCLI import zCLI


def run_demo():
    """Print core zSession values with copy/paste-ready accessors."""
    z = zCLI()
    session = z.session

    print("\n# Direct zSession accessors:")
    print(f"zSession_id      : {session.get('zS_id')}")
    print(f"zSpace           : {session.get('zSpace')}")
    print(f"zMode            : {session.get('zMode')}")
    print(f"zLogger          : {session.get('zLogger')}")
    print(f"zTraceback       : {session.get('zTraceback')}")
    print(f"zSpark           : {session.get('zSpark')}")
    print(f"virtual_env      : {session.get('virtual_env')}")
    print(f"system_env PATH  : {session.get('system_env')}")
    print(f"zVars            : {session.get('zVars')}")


if __name__ == "__main__":
    run_demo()


