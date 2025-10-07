# zCLI/subsystems/zShell_modules/executor_commands/config_executor.py
# ───────────────────────────────────────────────────────────────
"""Configuration command execution for zCLI."""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def execute_config(zcli, parsed):
    """
    Execute configuration commands.
    
    Currently supports:
    - config check: System configuration diagnostics
    
    Args:
        zcli: zCLI instance
        parsed: Parsed command dictionary
        
    Returns:
        Configuration operation result
    """
    action = parsed.get("action")

    logger.debug("Executing config command: %s", action)

    if action == "check":
        # Check system configuration folders and files
        return check_config_system(zcli)
    else:
        return {
            "error": f"Unknown config action: {action}",
            "available_actions": [
                "check"
            ]
        }


def check_config_system(zcli):
    """
    Check system configuration folders and files are properly installed and accessible.
    
    Args:
        zcli: zCLI instance
        
    Returns:
        Configuration system check result
    """
    import os
    from pathlib import Path

    logger.info("Checking zCLI configuration system...")

    results = {
        "status": "checking",
        "checks": {},
        "summary": {
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }
    }

    # Get paths info from zConfig
    paths_info = zcli.config.get_paths_info()

    # Check 1: Package config directory (get from package root)
    try:
        import zCLI
        from pathlib import Path
        package_root = Path(zCLI.__file__).parent.parent
        package_config_dir = package_root / "config"
        results["checks"]["package_config"] = check_directory(
            str(package_config_dir),
            "Package configuration directory",
            required=True
        )
    except Exception:
        results["checks"]["package_config"] = check_directory(
            "N/A",
            "Package configuration directory",
            required=True
        )

    # Check 2: System config directory  
    results["checks"]["system_config"] = check_directory(
        paths_info.get("system_config", "N/A"),
        "System configuration directory",
        required=False
    )

    # Check 3: User config directory
    results["checks"]["user_config"] = check_directory(
        paths_info.get("user_config_active", "N/A"),
        "User configuration directory", 
        required=True
    )

    # Check 4: Machine config file
    user_config_dir = paths_info.get("user_config_active", "")
    if user_config_dir and user_config_dir != "N/A":
        machine_config_path = f"{user_config_dir}/machine.yaml"
    else:
        machine_config_path = "/machine.yaml"
    results["checks"]["machine_config"] = check_file(
        machine_config_path,
        "Machine configuration file",
        required=True
    )

    # Check 5: Default config files
    try:
        import zCLI
        from pathlib import Path
        package_root = Path(zCLI.__file__).parent.parent
        package_config_dir = package_root / "config"

        default_configs = [
            "config.default.yaml",
            "config.dev.yaml", 
            "config.prod.yaml",
            "machine.default.yaml"
        ]

        for config_file in default_configs:
            config_path = str(package_config_dir / config_file)
            results["checks"][f"default_{config_file.replace('.', '_')}"] = check_file(
                config_path,
                f"Default {config_file}",
                required=True
            )
    except Exception:
        # Skip default config checks if package path can't be determined
        pass

    # Check 6: Config loader functionality
    results["checks"]["config_loader"] = check_config_loader(zcli)

    # Check 7: Machine config loading
    results["checks"]["machine_loading"] = check_machine_config_loading(zcli)

    # Calculate summary
    for check_name, check_result in results["checks"].items():
        results["summary"]["total_checks"] += 1
        if check_result["status"] == "pass":
            results["summary"]["passed"] += 1
        elif check_result["status"] == "fail":
            results["summary"]["failed"] += 1
        elif check_result["status"] == "warning":
            results["summary"]["warnings"] += 1

    # Overall status
    if results["summary"]["failed"] == 0:
        results["status"] = "pass"
    elif results["summary"]["failed"] <= 2:
        results["status"] = "warning"
    else:
        results["status"] = "fail"

    # Print results
    print_config_check_results(results)

    # Return None to prevent JSON output (formatted display already shown)
    return None


def check_directory(path, description, required=True):
    """Check if a directory exists and is accessible."""
    import os

    if path == "N/A":
        return {
            "status": "fail" if required else "warning",
            "description": description,
            "path": path,
            "message": "Path not configured",
            "required": required
        }

    if os.path.exists(path):
        if os.path.isdir(path):
            if os.access(path, os.R_OK):
                return {
                    "status": "pass",
                    "description": description,
                    "path": path,
                    "message": "Directory exists and is readable",
                    "required": required
                }
            else:
                return {
                    "status": "fail" if required else "warning",
                    "description": description,
                    "path": path,
                    "message": "Directory exists but is not readable",
                    "required": required
                }
        else:
            return {
                "status": "fail" if required else "warning",
                "description": description,
                "path": path,
                "message": "Path exists but is not a directory",
                "required": required
            }
    else:
        return {
            "status": "fail" if required else "warning",
            "description": description,
            "path": path,
            "message": "Directory does not exist",
            "required": required
        }


def check_file(path, description, required=True):
    """Check if a file exists and is accessible."""
    import os

    if not path or path == "N/A":
        return {
            "status": "fail" if required else "warning",
            "description": description,
            "path": path,
            "message": "Path not configured",
            "required": required
        }

    if os.path.exists(path):
        if os.path.isfile(path):
            if os.access(path, os.R_OK):
                # Get file size
                size = os.path.getsize(path)
                return {
                    "status": "pass",
                    "description": description,
                    "path": path,
                    "message": f"File exists and is readable ({size} bytes)",
                    "required": required,
                    "size": size
                }
            else:
                return {
                    "status": "fail" if required else "warning",
                    "description": description,
                    "path": path,
                    "message": "File exists but is not readable",
                    "required": required
                }
        else:
            return {
                "status": "fail" if required else "warning",
                "description": description,
                "path": path,
                "message": "Path exists but is not a file",
                "required": required
            }
    else:
        return {
            "status": "fail" if required else "warning",
            "description": description,
            "path": path,
            "message": "File does not exist",
            "required": required
        }


def check_config_loader(zcli):
    """Check if config loader is working properly."""
    try:
        # Test config loading
        config_sources = zcli.config.get_config_sources()
        if config_sources:
            return {
                "status": "pass",
                "description": "Configuration loader",
                "message": f"Config loaded from {len(config_sources)} sources: {', '.join(config_sources)}",
                "sources": config_sources
            }
        else:
            return {
                "status": "warning",
                "description": "Configuration loader", 
                "message": "Config loader working but no sources loaded"
            }
    except Exception as e:
        return {
            "status": "fail",
            "description": "Configuration loader",
            "message": f"Config loader failed: {str(e)}"
        }


def check_machine_config_loading(zcli):
    """Check if machine config is loading properly."""
    try:
        machine_info = zcli.config.get_machine()
        if machine_info:
            required_fields = ["os", "hostname", "deployment"]
            missing = [field for field in required_fields if not machine_info.get(field)]

            if not missing:
                return {
                    "status": "pass",
                    "description": "Machine configuration loading",
                    "message": f"Machine config loaded: {machine_info.get('os')} on {machine_info.get('hostname')}",
                    "machine": {
                        "os": machine_info.get("os"),
                        "hostname": machine_info.get("hostname"),
                        "deployment": machine_info.get("deployment")
                    }
                }
            else:
                return {
                    "status": "warning",
                    "description": "Machine configuration loading",
                    "message": f"Machine config loaded but missing fields: {', '.join(missing)}"
                }
        else:
            return {
                "status": "fail",
                "description": "Machine configuration loading",
                "message": "Machine config not loaded"
            }
    except Exception as e:
        return {
            "status": "fail",
            "description": "Machine configuration loading",
            "message": f"Machine config loading failed: {str(e)}"
        }


def print_config_check_results(results):
    """Display formatted configuration check results using zDisplay."""
    from zCLI.subsystems.zDisplay import ZDisplay

    # Create display instance
    display = ZDisplay()

    # Header
    display.handle({
        "event": "header",
        "label": "zCLI Configuration System Check",
        "color": "CYAN",
        "style": "=",
        "indent": 0
    })

    # Summary first
    summary = results["summary"]
    summary_lines = [f"Summary: {summary['passed']}/{summary['total_checks']} checks passed"]
    if summary["warnings"] > 0:
        summary_lines.append(f"Warnings: {summary['warnings']}")
    if summary["failed"] > 0:
        summary_lines.append(f"Failed: {summary['failed']}")

    display.handle({
        "event": "text",
        "value": "\n".join(summary_lines),
        "color": "WHITE",
        "indent": 0
    })

    # Detailed results header
    display.handle({
        "event": "header",
        "label": "Detailed Results",
        "color": "CYAN",
        "style": "-",
        "indent": 0
    })

    # Detailed results
    for check_name, check_result in results["checks"].items():
        status_indicator = {"pass": "[OK]", "warning": "[WARN]", "fail": "[FAIL]"}.get(check_result["status"], "[UNKNOWN]")
        required_text = " (required)" if check_result.get("required", False) else ""

        detail_lines = [f"{status_indicator} {check_result['description']}{required_text}"]

        if "path" in check_result:
            detail_lines.append(f"   Path: {check_result['path']}")

        detail_lines.append(f"   Status: {check_result['message']}")

        # Additional info
        if "size" in check_result:
            detail_lines.append(f"   Size: {check_result['size']} bytes")
        if "sources" in check_result:
            detail_lines.append(f"   Sources: {', '.join(check_result['sources'])}")
        if "machine" in check_result:
            machine = check_result["machine"]
            detail_lines.append(f"   OS: {machine.get('os')} | Host: {machine.get('hostname')} | Env: {machine.get('deployment')}")

        display.handle({
            "event": "text",
            "value": "\n".join(detail_lines),
            "color": "RESET",
            "indent": 0
        })

    # Overall status at the bottom (most important)
    status_indicator = {"pass": "[OK]", "warning": "[WARN]", "fail": "[FAIL]"}.get(results["status"], "[UNKNOWN]")
    status_color = {"pass": "GREEN", "warning": "YELLOW", "fail": "RED"}.get(results["status"], "RESET")

    display.handle({
        "event": "header",
        "label": "Final Result",
        "color": "CYAN",
        "style": "-",
        "indent": 0
    })

    display.handle({
        "event": "text",
        "value": f"\n{status_indicator} Overall Status: {results['status'].upper()}\n",
        "color": status_color,
        "indent": 0
    })

    # Footer
    display.handle({
        "event": "header",
        "label": "",
        "color": "CYAN",
        "style": "=",
        "indent": 0
    })
