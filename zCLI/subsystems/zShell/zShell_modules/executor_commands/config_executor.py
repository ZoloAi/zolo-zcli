# zCLI/subsystems/zShell_modules/executor_commands/config_executor.py
"""Configuration command executor (check system diagnostics)."""

import os
from pathlib import Path
from logger import Logger

logger = Logger.get_logger(__name__)

def execute_config(zcli, parsed):
    """Execute config commands (check)."""
    action = parsed.get("action")
    logger.debug("Executing config command: %s", action)

    if action == "check":
        return check_config_system(zcli)

    return {
        "error": f"Unknown config action: {action}",
        "available_actions": ["check"]
    }

def check_config_system(zcli):
    """Check system configuration folders and files accessibility."""
    logger.info("Checking zCLI configuration system...")

    results = {
        "status": "checking",
        "checks": {},
        "summary": {"total_checks": 0, "passed": 0, "failed": 0, "warnings": 0}
    }

    paths_info = zcli.config.get_paths_info()
    
    # Run all checks
    _run_directory_checks(results, paths_info)
    _run_file_checks(results, paths_info)
    results["checks"]["config_loader"] = check_config_loader(zcli)
    results["checks"]["machine_loading"] = check_machine_config_loading(zcli)

    for _check_name, check_result in results["checks"].items():
        results["summary"]["total_checks"] += 1
        if check_result["status"] == "pass":
            results["summary"]["passed"] += 1
        elif check_result["status"] == "fail":
            results["summary"]["failed"] += 1
        elif check_result["status"] == "warning":
            results["summary"]["warnings"] += 1

    if results["summary"]["failed"] == 0:
        results["status"] = "pass"
    elif results["summary"]["failed"] <= 2:
        results["status"] = "warning"
    else:
        results["status"] = "fail"

    print_config_check_results(results)
    return None


def _run_directory_checks(results, paths_info):
    """Run all directory checks."""
    try:
        import zCLI
        package_root = Path(zCLI.__file__).parent.parent
        package_config_dir = package_root / "config"
        results["checks"]["package_config"] = check_directory(
            str(package_config_dir), "Package configuration directory", required=True
        )
    except Exception:
        results["checks"]["package_config"] = check_directory(
            "N/A", "Package configuration directory", required=True
        )

    # Check 2: System config directory  
    results["checks"]["system_config"] = check_directory(
        paths_info.get("system_config", "N/A"), "System configuration directory", required=False
    )

    # Check 3: User config directory
    results["checks"]["user_config"] = check_directory(
        paths_info.get("user_config_active", "N/A"), "User configuration directory", required=True
    )

    # Check 4: User data directory with zMachine subdirectories
    user_data_dir = paths_info.get("user_data", "N/A")
    results["checks"]["user_data"] = check_directory(user_data_dir, "User data directory", required=True)
    
    if user_data_dir and user_data_dir != "N/A":
        for subdir in ["Config", "Cache"]:
            results["checks"][f"zmachine_{subdir.lower()}"] = check_directory(
                f"{user_data_dir}/{subdir}", f"zMachine.{subdir} subdirectory", required=True
            )


def _run_file_checks(results, paths_info):
    """Run all file checks."""
    user_config_dir = paths_info.get("user_config_active", "")
    machine_config_path = f"{user_config_dir}/machine.yaml" if user_config_dir and user_config_dir != "N/A" else "/machine.yaml"
    results["checks"]["machine_config"] = check_file(machine_config_path, "Machine configuration file", required=True)

    try:
        import zCLI
        package_root = Path(zCLI.__file__).parent.parent
        package_config_dir = package_root / "config"

        for config_file in ["zConfig.default.yaml", "zConfig.dev.yaml", "zConfig.prod.yaml", "zConfig.machine.yaml"]:
            results["checks"][f"default_{config_file.replace('.', '_')}"] = check_file(
                str(package_config_dir / config_file), f"Default {config_file}", required=True
            )
    except Exception:
        pass


def check_directory(path, description, required=True):
    """Check if a directory exists and is accessible."""
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
    """Check if config loader is working."""
    try:
        config_sources = zcli.config.get_config_sources()
        if config_sources:
            return {
                "status": "pass",
                "description": "Configuration loader",
                "message": f"Config loaded from {len(config_sources)} sources: {', '.join(config_sources)}",
                "sources": config_sources
            }
        
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
    """Check if machine config is loading."""
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
            
            return {
                "status": "warning",
                "description": "Machine configuration loading",
                "message": f"Machine config loaded but missing fields: {', '.join(missing)}"
            }
        
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
    # TODO: Replace with proper zDisplay text event once supported
    from zCLI.subsystems.zDisplay_new import zDisplay_new
    from zCLI.subsystems.zSession import zSession
    from logger import Logger
    
    logger = Logger.get_logger(__name__)
    display = zDisplay_new(zSession, logger=logger)
    display.handle({
        "event": "header",
        "label": "zCLI Configuration System Check",
        "color": "CYAN",
        "style": "=",
        "indent": 0
    })

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

    display.handle({
        "event": "header",
        "label": "Detailed Results",
        "color": "CYAN",
        "style": "-",
        "indent": 0
    })

    for _check_name, check_result in results["checks"].items():
        status_indicator = {"pass": "[OK]", "warning": "[WARN]", "fail": "[FAIL]"}.get(check_result["status"], "[UNKNOWN]")
        required_text = " (required)" if check_result.get("required", False) else ""

        detail_lines = [f"{status_indicator} {check_result['description']}{required_text}"]

        if "path" in check_result:
            detail_lines.append(f"   Path: {check_result['path']}")

        detail_lines.append(f"   Status: {check_result['message']}")

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

    display.handle({
        "event": "header",
        "label": "",
        "color": "CYAN",
        "style": "=",
        "indent": 0
    })
