#!/usr/bin/env python3
"""Show all zMachine values with z.config.get_machine() for copy-paste use."""

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
    print(f"python_executable : {machine.get('python_executable')}")
    print(f"libc_ver          : {machine.get('libc_ver')}")
    print(f"zcli_install_path : {machine.get('zcli_install_path')}")
    print(f"zcli_install_type : {machine.get('zcli_install_type')}")

if __name__ == "__main__":
    run_demo()
