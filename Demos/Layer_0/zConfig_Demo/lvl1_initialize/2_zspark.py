#!/usr/bin/env python3
"""zSpark = dict you pass to zCLI() to override config (highest priority)

Default in this demo:
    "deployment": "Production"  # minimal output, ERROR logging

Try:
    - Change "Production" to "Debug" for verbose output.
"""


from zCLI import zCLI


def run_demo():
    # Production deployment = minimal output + ERROR logging (auto-default)
    z = zCLI({
        "deployment": "Production",
        # logger: "ERROR" is implicit in Production
        # Add explicit "logger": "INFO" or "DEBUG" to override
    })

    print("\n# Notice:")
    print("  - No 'Ready' banners in Production mode")
    print("  - Logger defaults to ERROR (minimal logging)")
    print("  - Console output is minimal")
    print("  - Override logger explicitly if you need different verbosity")


if __name__ == "__main__":
    run_demo()
