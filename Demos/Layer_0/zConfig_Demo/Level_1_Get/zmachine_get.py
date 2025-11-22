#!/usr/bin/env python3
"""
Level 1: zMachine Get
=====================

Goal:
    Show all zMachine values via z.config.get_machine() so developers can
    copy/paste these accessor lines into their own code.

Run:
    python3 Demos/Layer_0/zConfig_Demo/Level_1_Get/zmachine_get.py
"""

from zCLI import zCLI


def run_demo():
    """Print all zMachine values with copy/paste-ready accessor lines."""
    z = zCLI()
    # (copy these lines as needed to fetch zMachine values)
    machine = z.config.get_machine()

    print("\n# Direct zMachine accessors:")
    print(f"os                : {machine.get('os')}")
    print(f"os_name           : {machine.get('os_name')}")
    print(f"os_version        : {machine.get('os_version')}")
    print(f"architecture      : {machine.get('architecture')}")
    print(f"processor         : {machine.get('processor')}")
    print(f"cpu_cores         : {machine.get('cpu_cores')}")
    print(f"memory_gb         : {machine.get('memory_gb')}")
    print(f"hostname          : {machine.get('hostname')}")
    print(f"username          : {machine.get('username')}")
    print(f"home              : {machine.get('home')}")
    print(f"cwd               : {machine.get('cwd')}")
    print(f"browser           : {machine.get('browser')}")
    print(f"ide               : {machine.get('ide')}")
    print(f"terminal          : {machine.get('terminal')}")
    print(f"shell             : {machine.get('shell')}")
    print(f"lang              : {machine.get('lang')}")
    print(f"timezone          : {machine.get('timezone')}")
    print(f"path              : {machine.get('path')}")
    print(f"user_data_dir     : {machine.get('user_data_dir')}")
    print(f"python_version    : {machine.get('python_version')}")
    print(f"python_impl       : {machine.get('python_impl')}")
    print(f"python_build      : {machine.get('python_build')}")
    print(f"python_compiler   : {machine.get('python_compiler')}")
    print(f"libc_ver          : {machine.get('libc_ver')}")

if __name__ == "__main__":
    run_demo()

