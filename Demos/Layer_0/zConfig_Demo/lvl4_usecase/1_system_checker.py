#!/usr/bin/env python3
"""System Requirements Checker

Checks if your computer meets project requirements.
Requirements are defined in .zEnv file.

Run: python3 Demos/Layer_0/zConfig_Demo/lvl4_usecase/1_system_checker.py
"""

from zKernel import zKernel
import sys


def check_cpu(z, required, actual):
    """Check if CPU has enough cores."""
    # Compare what we have vs what we need
    if actual >= required:
        # We have enough cores - pass!
        z.logger.info(f"CPU: {actual} cores (need {required}) - PASS")
        return True
    else:
        # Not enough cores - fail
        z.logger.warning(f"CPU: {actual} cores (need {required}) - FAIL")
        return False


def check_memory(z, required, actual):
    """Check if system has enough RAM."""
    # Compare GB of RAM we have vs what we need
    if actual >= required:
        # We have enough memory - pass!
        z.logger.info(f"Memory: {actual}GB (need {required}GB) - PASS")
        return True
    else:
        # Not enough memory - fail
        z.logger.warning(f"Memory: {actual}GB (need {required}GB) - FAIL")
        return False


def check_python(z, required, actual):
    """Check if Python version is new enough."""
    # Compare version numbers (3.12 > 3.11, for example)
    if actual >= required:
        # Python is new enough - pass!
        z.logger.info(f"Python: {actual} (need {required}+) - PASS")
        return True
    else:
        # Python is too old - fail
        z.logger.warning(f"Python: {actual} (need {required}+) - FAIL")
        return False


def check_gpu(z, required, available, gpu_name):
    """Check if GPU is available when required."""
    # Three cases: required and missing, available, or not needed
    if required and not available:
        # Project needs GPU but we don't have one - fail
        z.logger.error("GPU: required but not found - FAIL")
        return False
    elif available:
        # We have a GPU - pass!
        z.logger.info(f"GPU: {gpu_name} - PASS")
        return True
    else:
        # GPU not required for this project - pass!
        z.logger.info("GPU: not required - PASS")
        return True


def main():
    """Main function - checks system requirements."""

    # Step 1: Initialize zCLI
    # This loads configuration from multiple sources automatically
    zSpark = {
        "deployment": "Production",  # Clean output, no banners
        "title": "system-checker",   # Name for our log file
        "logger": "INFO",             # Show INFO level and above
        "logger_path": "./logs",      # Save logs in local folder
    }
    z = zKernel(zSpark)  # Create zCLI instance

    # Step 2: Get project info from .zEnv
    # .zEnv file is auto-loaded from workspace
    project_name = z.config.environment.get_env_var("PROJECT_NAME", "Unknown Project")
    project_version = z.config.environment.get_env_var("PROJECT_VERSION", "0.0.0")

    z.logger.info(f"Checking: {project_name} v{project_version}")

    # Step 3: Get requirements from .zEnv (what we need)
    # Convert strings to numbers where needed
    required_cpu = int(z.config.environment.get_env_var("MIN_CPU_CORES", "2"))
    required_memory = int(z.config.environment.get_env_var("MIN_MEMORY_GB", "4"))
    required_python = z.config.environment.get_env_var("MIN_PYTHON_VERSION", "3.8")
    # Convert "true"/"false" string to actual boolean
    required_gpu = z.config.environment.get_env_var("REQUIRED_GPU", "false").lower() == "true"

    # Step 4: Get machine specs from zMachine (what we have)
    # zMachine auto-detected hardware when zCLI first ran
    machine = z.config.get_machine()
    actual_cpu = machine.get('cpu_cores')
    actual_memory = machine.get('memory_gb')
    actual_python = machine.get('python_version')
    actual_gpu = machine.get('gpu_available')
    gpu_name = machine.get('gpu_type', 'None')

    # Step 5: Run all checks
    # Each returns True (pass) or False (fail)
    cpu_pass = check_cpu(z, required_cpu, actual_cpu)
    memory_pass = check_memory(z, required_memory, actual_memory)
    python_pass = check_python(z, required_python, actual_python)
    gpu_pass = check_gpu(z, required_gpu, actual_gpu, gpu_name)

    # Step 6: Final result
    # All checks must pass for system to be ready
    all_passed = cpu_pass and memory_pass and python_pass and gpu_pass

    if all_passed:
        z.logger.info("SYSTEM READY - All requirements met")
        return 0  # Exit code 0 = success
    else:
        z.logger.error("SYSTEM NOT READY - Some requirements not met")
        return 1  # Exit code 1 = failure

if __name__ == "__main__":
    # Run the main function and get result (0 or 1)
    exit_code = main()
    # Exit with that code (so other programs know if we succeeded)
    sys.exit(exit_code)
