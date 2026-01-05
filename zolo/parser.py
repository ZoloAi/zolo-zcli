"""
Zolo Parser

Main parser module with public API (load, loads, dump, dumps).
"""

import yaml
import json
from pathlib import Path
from typing import Any, Union, Optional, IO

from .type_hints import process_type_hints
from .constants import FILE_EXT_ZOLO, FILE_EXT_YAML, FILE_EXT_YML, FILE_EXT_JSON
from .exceptions import ZoloParseError, ZoloDumpError


def load(fp: Union[str, Path, IO], file_extension: Optional[str] = None) -> Any:
    """
    Load data from a .zolo file (or compatible format).
    
    Args:
        fp: File path (str/Path) or file-like object
        file_extension: Optional file extension override (.zolo, .yaml, .json)
                       If None, will detect from file path or default to .zolo
    
    Returns:
        Parsed data (dict, list, or scalar)
    
    Raises:
        ZoloParseError: If parsing fails
        FileNotFoundError: If file doesn't exist
    
    Examples:
        >>> # Load .zolo file (string-first)
        >>> data = zolo.load('config.zolo')
        
        >>> # Load .yaml file (native types)
        >>> data = zolo.load('config.yaml')
        
        >>> # Load with explicit extension
        >>> data = zolo.load('config.txt', file_extension='.zolo')
    """
    # Handle file path vs file-like object
    if isinstance(fp, (str, Path)):
        file_path = Path(fp)
        
        # Detect file extension if not provided
        if file_extension is None:
            file_extension = file_path.suffix.lower()
            if not file_extension:
                file_extension = FILE_EXT_ZOLO  # Default to .zolo
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise ZoloParseError(f"Error reading file {file_path}: {e}") from e
    else:
        # File-like object
        try:
            content = fp.read()
        except Exception as e:
            raise ZoloParseError(f"Error reading from file object: {e}") from e
        
        # Try to detect extension from file name
        if file_extension is None and hasattr(fp, 'name'):
            file_extension = Path(fp.name).suffix.lower()
        if not file_extension:
            file_extension = FILE_EXT_ZOLO  # Default to .zolo
    
    # Parse content
    return loads(content, file_extension=file_extension)


def loads(s: str, file_extension: Optional[str] = None) -> Any:
    """
    Load data from a .zolo string (or compatible format).
    
    Args:
        s: String content to parse
        file_extension: Optional file extension hint (.zolo, .yaml, .json)
                       Defaults to .zolo if not provided
    
    Returns:
        Parsed data (dict, list, or scalar)
    
    Raises:
        ZoloParseError: If parsing fails
    
    Examples:
        >>> # Parse .zolo string (string-first)
        >>> data = zolo.loads('port: 8080')
        {'port': '8080'}  # String by default
        
        >>> # Parse with type hint
        >>> data = zolo.loads('port(int): 8080')
        {'port': 8080}  # Integer via type hint
        
        >>> # Parse .yaml string (native types)
        >>> data = zolo.loads('port: 8080', file_extension='.yaml')
        {'port': 8080}  # Integer via YAML
    """
    if not s or not s.strip():
        return None
    
    # Default to .zolo if not specified
    if file_extension is None:
        file_extension = FILE_EXT_ZOLO
    
    # Normalize extension
    file_extension = file_extension.lower()
    if not file_extension.startswith('.'):
        file_extension = '.' + file_extension
    
    # Determine if string-first should be applied
    string_first = (file_extension == FILE_EXT_ZOLO)
    
    # Parse based on format
    try:
        if file_extension == FILE_EXT_JSON:
            # Parse as JSON
            parsed = json.loads(s)
        else:
            # Parse as YAML (default for .zolo, .yaml, .yml)
            parsed = yaml.safe_load(s)
        
        # Process type hints
        parsed = process_type_hints(parsed, string_first=string_first)
        
        return parsed
    
    except yaml.YAMLError as e:
        raise ZoloParseError(f"YAML parsing error: {e}") from e
    except json.JSONDecodeError as e:
        raise ZoloParseError(f"JSON parsing error: {e}") from e
    except Exception as e:
        raise ZoloParseError(f"Parsing error: {e}") from e


def dump(data: Any, fp: Union[str, Path, IO], file_extension: Optional[str] = None, **kwargs) -> None:
    """
    Dump data to a .zolo file (or compatible format).
    
    Args:
        data: Data to dump (dict, list, or scalar)
        fp: File path (str/Path) or file-like object
        file_extension: Optional file extension override (.zolo, .yaml, .json)
                       If None, will detect from file path or default to .zolo
        **kwargs: Additional arguments passed to YAML/JSON dumper
                 For YAML: default_flow_style=False, allow_unicode=True
                 For JSON: indent=2, ensure_ascii=False
    
    Raises:
        ZoloDumpError: If dumping fails
    
    Examples:
        >>> data = {'port': 8080, 'enabled': True}
        >>> zolo.dump(data, 'config.zolo')
        
        >>> # Dump as JSON
        >>> zolo.dump(data, 'config.json')
        
        >>> # Dump with custom kwargs
        >>> zolo.dump(data, 'config.yaml', default_flow_style=True)
    """
    # Convert to string
    content = dumps(data, file_extension=file_extension, **kwargs)
    
    # Handle file path vs file-like object
    if isinstance(fp, (str, Path)):
        file_path = Path(fp)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise ZoloDumpError(f"Error writing file {file_path}: {e}") from e
    else:
        # File-like object
        try:
            fp.write(content)
        except Exception as e:
            raise ZoloDumpError(f"Error writing to file object: {e}") from e


def dumps(data: Any, file_extension: Optional[str] = None, **kwargs) -> str:
    """
    Dump data to a .zolo string (or compatible format).
    
    Args:
        data: Data to dump (dict, list, or scalar)
        file_extension: Optional file extension hint (.zolo, .yaml, .json)
                       Defaults to .zolo if not provided
        **kwargs: Additional arguments passed to YAML/JSON dumper
    
    Returns:
        Formatted string
    
    Raises:
        ZoloDumpError: If dumping fails
    
    Examples:
        >>> data = {'port': 8080, 'enabled': True}
        >>> print(zolo.dumps(data))
        port: 8080
        enabled: true
        
        >>> # Dump as JSON
        >>> print(zolo.dumps(data, file_extension='.json'))
        {
          "port": 8080,
          "enabled": true
        }
    """
    # Default to .zolo if not specified
    if file_extension is None:
        file_extension = FILE_EXT_ZOLO
    
    # Normalize extension
    file_extension = file_extension.lower()
    if not file_extension.startswith('.'):
        file_extension = '.' + file_extension
    
    # Dump based on format
    try:
        if file_extension == FILE_EXT_JSON:
            # Dump as JSON
            json_kwargs = {
                'indent': 2,
                'ensure_ascii': False,
            }
            json_kwargs.update(kwargs)
            return json.dumps(data, **json_kwargs)
        else:
            # Dump as YAML (default for .zolo, .yaml, .yml)
            yaml_kwargs = {
                'default_flow_style': False,
                'allow_unicode': True,
                'sort_keys': False,
            }
            yaml_kwargs.update(kwargs)
            return yaml.dump(data, **yaml_kwargs)
    
    except Exception as e:
        raise ZoloDumpError(f"Dumping error: {e}") from e
