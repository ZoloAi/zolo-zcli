"""
Zolo: A DRY, string-first declarative file format

Zolo is a human-friendly data serialization format that:
- Defaults all values to strings (no YAML quirks)
- Supports explicit type hints for opt-in type conversion
- Is quote-free and DRY
- Is backward compatible with YAML syntax

Usage:
    import zolo
    
    # Load from file
    data = zolo.load('config.zolo')
    
    # Load from string
    data = zolo.loads('key: value')
    
    # Dump to file
    zolo.dump(data, 'output.zolo')
    
    # Dump to string
    text = zolo.dumps(data)

Type Hints:
    port(int): 8080        # Integer
    price(float): 19.99    # Float
    enabled(bool): true    # Boolean
    id(str): 123           # Force string
    value(null):           # Null/None
    
String-First:
    All values without type hints default to strings in .zolo files,
    eliminating YAML's parsing quirks (NO → False, yes → True, etc.)
"""

__version__ = "1.0.0"
__author__ = "Zolo.ai"
__license__ = "MIT"

from .parser import load, loads, dump, dumps
from .exceptions import ZoloParseError, ZoloTypeError, ZoloDumpError

__all__ = [
    # Main API
    'load',
    'loads',
    'dump',
    'dumps',
    
    # Exceptions
    'ZoloParseError',
    'ZoloTypeError',
    'ZoloDumpError',
    
    # Metadata
    '__version__',
]
