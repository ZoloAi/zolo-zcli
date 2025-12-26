# zCLI/subsystems/zConfig/zConfig_modules/config_zenv.py
"""
zEnv - Declarative Environment Configuration Loader

THE zCLI WAY: Replace traditional .env files with YAML/JSON declarative configs.

This module provides a secure, declarative alternative to python-dotenv while
maintaining backward compatibility. It parses zEnv.*.yaml/json files and injects
values into os.environ (just like dotenv), ensuring security and standard practices.

Key Features:
- Parse YAML/JSON declarative config files
- Flatten nested structures to JSON strings for complex values
- Priority-based loading (base → environment-specific)
- Secure: Values injected into os.environ (process-isolated)
- Backward compatible: Falls back to dotenv if YAML files not found

File Format:
-----------
zEnv.base.yaml         - Base configuration (shared across all environments)
zEnv.development.yaml  - Development-specific overrides
zEnv.production.yaml   - Production-specific overrides
zEnv.testing.yaml      - Testing-specific overrides

Priority Order:
--------------
1. zEnv.{environment}.yaml  (highest priority - environment-specific)
2. zEnv.base.yaml           (base configuration)
3. .zEnv.{environment}      (legacy dotenv fallback)
4. .zEnv                    (legacy dotenv base)

Example:
--------
# zEnv.base.yaml
ZNAVBAR:
  zVaF:
  zAccount:
    _rbac:
      require_role: [zAdmin]

AWS_SECRET_KEY: "secret123"
DEBUG: true

After loading:
os.getenv("ZNAVBAR")  # '{"zVaF": null, "zAccount": {"_rbac": {"require_role": ["zAdmin"]}}}'
os.getenv("AWS_SECRET_KEY")  # "secret123"
os.getenv("DEBUG")  # "true"

Security:
---------
- Values stored in os.environ (process-isolated, standard practice)
- No serialization risk (secrets not in Python objects)
- Works with Docker, K8s, systemd
- Audit trail via OS logging
"""

from zCLI import os, sys, yaml, json, Path, Any, Dict, Optional, List
from pathlib import Path

# Module constants
LOG_PREFIX = "[zEnv]"

class zEnv:
    """
    Declarative environment configuration loader (THE zCLI WAY).
    
    Replaces python-dotenv with YAML/JSON declarative configs while
    maintaining security through os.environ injection.
    """
    
    def __init__(self, workspace_dir: str, environment: str = "development", logger=None):
        """
        Initialize zEnv loader.
        
        Args:
            workspace_dir: Path to workspace directory containing zEnv files
            environment: Current environment (development, production, testing)
            logger: Optional logger instance for debug output
        """
        self.workspace_dir = Path(workspace_dir)
        self.environment = environment.lower()
        self.logger = logger
        self._loaded_files: List[str] = []
        
    def load(self) -> bool:
        """
        Load environment configuration from YAML/JSON files into os.environ.
        
        Priority order:
        1. zEnv.base.yaml (base configuration)
        2. zEnv.{environment}.yaml (environment-specific overrides)
        3. Fallback to dotenv if YAML files not found
        
        Returns:
            bool: True if any YAML files were loaded, False if fell back to dotenv
        """
        yaml_loaded = False
        
        # Priority 1: Load base configuration
        base_file = self.workspace_dir / "zEnv.base.yaml"
        base_config = self._load_file(base_file)
        
        if base_config:
            self._inject_to_environ(base_config)
            self._loaded_files.append(str(base_file))
            yaml_loaded = True
            self._log(f"✅ Loaded base config from {base_file.name}")
        
        # Priority 2: Load environment-specific configuration (overrides base)
        env_file = self.workspace_dir / f"zEnv.{self.environment}.yaml"
        env_config = self._load_file(env_file)
        
        if env_config:
            self._inject_to_environ(env_config)
            self._loaded_files.append(str(env_file))
            yaml_loaded = True
            self._log(f"✅ Loaded {self.environment} config from {env_file.name}")
        
        # Priority 3: Fallback to dotenv (backward compatibility)
        if not yaml_loaded:
            self._log("⚠️  No zEnv YAML files found, falling back to dotenv")
            self._fallback_to_dotenv()
            return False
        
        return True
    
    def _load_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load and parse a YAML or JSON file.
        
        Args:
            file_path: Path to the file to load
        
        Returns:
            Dict containing parsed data, or None if file doesn't exist or parse failed
        """
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try YAML first (supports both YAML and JSON)
            try:
                data = yaml.safe_load(content)
                if data is None:
                    self._log(f"⚠️  {file_path.name} is empty")
                    return None
                return data
            except yaml.YAMLError as e:
                # Fallback to JSON
                try:
                    data = json.loads(content)
                    return data
                except json.JSONDecodeError as e2:
                    self._log(f"❌ Failed to parse {file_path.name}: YAML error: {e}, JSON error: {e2}")
                    return None
        
        except Exception as e:
            self._log(f"❌ Failed to read {file_path.name}: {e}")
            return None
    
    def _inject_to_environ(self, config: Dict[str, Any]) -> None:
        """
        Inject configuration values into os.environ.
        
        Nested structures (dicts, lists) are flattened to JSON strings.
        Simple values are converted to strings.
        
        Args:
            config: Dictionary of configuration values to inject
        """
        for key, value in config.items():
            if value is None:
                # Skip None values (don't set env var)
                continue
            
            if isinstance(value, (dict, list)):
                # Flatten complex structures to JSON strings
                os.environ[key] = json.dumps(value, ensure_ascii=False)
                self._log(f"  {key}: <complex> (JSON string)")
            elif isinstance(value, bool):
                # Convert boolean to lowercase string (true/false)
                os.environ[key] = str(value).lower()
                self._log(f"  {key}: {value}")
            else:
                # Simple values to strings
                os.environ[key] = str(value)
                self._log(f"  {key}: {value}")
    
    def _fallback_to_dotenv(self) -> None:
        """
        Fallback to traditional dotenv loading (backward compatibility).
        
        Loads .zEnv and .zEnv.{environment} files using python-dotenv.
        """
        try:
            from dotenv import load_dotenv
            
            # Load base .zEnv
            base_dotenv = self.workspace_dir / ".zEnv"
            if base_dotenv.exists():
                load_dotenv(base_dotenv)
                self._log(f"✅ Loaded legacy dotenv: {base_dotenv.name}")
            
            # Load environment-specific .zEnv.{environment}
            env_dotenv = self.workspace_dir / f".zEnv.{self.environment}"
            if env_dotenv.exists():
                load_dotenv(env_dotenv, override=True)
                self._log(f"✅ Loaded legacy dotenv: {env_dotenv.name}")
        
        except ImportError:
            self._log("⚠️  python-dotenv not installed, skipping dotenv fallback")
        except Exception as e:
            self._log(f"❌ Failed to load dotenv: {e}")
    
    def _log(self, message: str) -> None:
        """
        Log a message (if logger is available).
        
        Args:
            message: Message to log
        """
        if self.logger:
            self.logger.framework.info(f"{LOG_PREFIX} {message}")
        # Silently skip if no logger (during bootstrap)


def load_zenv(workspace_dir: str, environment: str = "development", logger=None) -> bool:
    """
    Convenience function to load zEnv configuration.
    
    Args:
        workspace_dir: Path to workspace directory containing zEnv files
        environment: Current environment (development, production, testing)
        logger: Optional logger instance
    
    Returns:
        bool: True if YAML files were loaded, False if fell back to dotenv
    
    Example:
        >>> from zCLI.subsystems.zConfig.zConfig_modules.config_zenv import load_zenv
        >>> load_zenv("/path/to/workspace", "development")
        True
    """
    loader = zEnv(workspace_dir, environment, logger)
    return loader.load()

