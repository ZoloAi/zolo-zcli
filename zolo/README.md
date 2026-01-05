# Zolo: A DRY, String-First Declarative File Format

**Zolo** is a human-friendly data serialization format that eliminates YAML's parsing quirks while maintaining its readability and power.

## Why Zolo?

### YAML's Problems

```yaml
# YAML has notorious parsing quirks:
country: NO              # → False (not "NO"!) ❌
enabled: yes             # → True (not "yes"!)
light: on                # → True (not "on"!)
version: 1.0             # → 1.0 float (not "1.0" string!)
id: 00123                # → 83 (octal conversion!) ❌
```

### Zolo's Solution

```yaml
# Zolo defaults everything to strings (string-first):
country: NO              # → "NO" ✅
enabled: yes             # → "yes" ✅
light: on                # → "on" ✅
version: 1.0             # → "1.0" ✅
id: 00123                # → "00123" ✅

# Use type hints when you need other types:
port(int): 8080          # → 8080 (int)
price(float): 19.99      # → 19.99 (float)
enabled(bool): true      # → True (bool)
```

## Installation

```bash
pip install zolo
```

## Quick Start

### Load from File

```python
import zolo

# Load .zolo file (string-first default)
data = zolo.load('config.zolo')

# Load .yaml file (backward compatible)
data = zolo.load('config.yaml')
```

### Load from String

```python
import zolo

# Parse string (defaults to .zolo format)
data = zolo.loads('''
port: 8080
country: NO
enabled: yes
''')

# Result (all strings by default):
# {'port': '8080', 'country': 'NO', 'enabled': 'yes'}
```

### With Type Hints

```python
import zolo

data = zolo.loads('''
port(int): 8080
price(float): 19.99
enabled(bool): true
label: Welcome
''')

# Result (explicit types):
# {
#   'port': 8080,          # int
#   'price': 19.99,        # float
#   'enabled': True,       # bool
#   'label': 'Welcome'     # str (default)
# }
```

### Dump to File

```python
import zolo

data = {
    'port': 8080,
    'enabled': True,
    'label': 'My App'
}

# Dump to .zolo file
zolo.dump(data, 'output.zolo')

# Dump to .json file
zolo.dump(data, 'output.json')
```

### Dump to String

```python
import zolo

data = {'port': 8080, 'enabled': True}

# Dump as YAML (default)
print(zolo.dumps(data))
# Output:
# port: 8080
# enabled: true

# Dump as JSON
print(zolo.dumps(data, file_extension='.json'))
# Output:
# {
#   "port": 8080,
#   "enabled": true
# }
```

## Type Hints

Zolo supports explicit type hints using parentheses notation:

### Supported Types

| Type | Syntax | Example | Result |
|------|--------|---------|--------|
| **Integer** | `(int)` | `port(int): 8080` | `8080` |
| **Float** | `(float)` | `price(float): 19.99` | `19.99` |
| **Boolean** | `(bool)` | `enabled(bool): true` | `True` |
| **String** | `(str)` | `id(str): 123` | `"123"` |
| **List** | `(list)` | `tags(list): [a, b]` | `["a", "b"]` |
| **Dict** | `(dict)` | `config(dict): {...}` | `{...}` |
| **Null** | `(null)` | `value(null):` | `None` |
| **Raw** | `(raw)` | `regex(raw): \d+` | `"\\d+"` |
| **Date** | `(date)` | `created(date): 2024-01-01` | `"2024-01-01"` |
| **Time** | `(time)` | `start(time): 10:30:00` | `"10:30:00"` |
| **URL** | `(url)` | `endpoint(url): https://...` | `"https://..."` |
| **Path** | `(path)` | `file(path): /path/to/file` | `"/path/to/file"` |

### Boolean Values

The `(bool)` type hint accepts multiple representations:

```yaml
# True values
enabled(bool): true
enabled(bool): yes
enabled(bool): 1
enabled(bool): on

# False values
enabled(bool): false
enabled(bool): no
enabled(bool): 0
enabled(bool): off
```

## String-First Philosophy

### The Principle

**All values without type hints default to strings in `.zolo` files.**

This eliminates YAML's surprising type conversions and makes config files predictable.

### Comparison

| Value | YAML Result | Zolo Result |
|-------|-------------|-------------|
| `NO` | `False` (bool) ❌ | `"NO"` (str) ✅ |
| `yes` | `True` (bool) | `"yes"` (str) ✅ |
| `8080` | `8080` (int) | `"8080"` (str) ✅ |
| `1.0` | `1.0` (float) | `"1.0"` (str) ✅ |
| `00123` | `83` (octal!) ❌ | `"00123"` (str) ✅ |

### When to Use Type Hints

Use type hints **only when you need non-string types**:

```yaml
# Good: Explicit types for numeric config
port(int): 8080
timeout(int): 30
price(float): 19.99
enabled(bool): true

# Good: No hints for string values (DRY)
app_name: My App
country_code: NO
version: 1.0.0
```

## Backward Compatibility

Zolo is **100% backward compatible** with YAML:

```python
import zolo

# Load .yaml file (native YAML parsing)
data = zolo.load('config.yaml')
# YAML quirks preserved: NO → False, 8080 → int, etc.

# Load .zolo file (string-first)
data = zolo.load('config.zolo')
# String-first: NO → "NO", 8080 → "8080", etc.
```

## API Reference

### `load(fp, file_extension=None)`

Load data from a file.

**Args:**
- `fp`: File path (str/Path) or file-like object
- `file_extension`: Optional extension override (`.zolo`, `.yaml`, `.json`)

**Returns:** Parsed data (dict, list, or scalar)

**Raises:** `ZoloParseError`, `FileNotFoundError`

### `loads(s, file_extension=None)`

Load data from a string.

**Args:**
- `s`: String content to parse
- `file_extension`: Optional extension hint (defaults to `.zolo`)

**Returns:** Parsed data (dict, list, or scalar)

**Raises:** `ZoloParseError`

### `dump(data, fp, file_extension=None, **kwargs)`

Dump data to a file.

**Args:**
- `data`: Data to dump
- `fp`: File path (str/Path) or file-like object
- `file_extension`: Optional extension override
- `**kwargs`: Additional arguments for YAML/JSON dumper

**Raises:** `ZoloDumpError`

### `dumps(data, file_extension=None, **kwargs)`

Dump data to a string.

**Args:**
- `data`: Data to dump
- `file_extension`: Optional extension hint (defaults to `.zolo`)
- `**kwargs`: Additional arguments for YAML/JSON dumper

**Returns:** Formatted string

**Raises:** `ZoloDumpError`

## Exceptions

- `ZoloError`: Base exception
- `ZoloParseError`: Parsing failed
- `ZoloTypeError`: Type conversion failed
- `ZoloDumpError`: Dumping failed

## Examples

### Configuration File

```yaml
# config.zolo
app_name: My Application
version: 1.0.0

server:
  host: localhost
  port(int): 8080
  ssl(bool): true
  timeout(int): 30

database:
  url(url): postgres://localhost/mydb
  max_connections(int): 100
  retry(bool): true

features:
  analytics(bool): true
  debug(bool): false
  rate_limit(int): 1000
```

```python
import zolo

config = zolo.load('config.zolo')

# All types are correct:
assert config['app_name'] == 'My Application'        # str
assert config['server']['port'] == 8080              # int
assert config['server']['ssl'] is True               # bool
assert config['database']['max_connections'] == 100  # int
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## Links

- **Homepage:** https://github.com/ZoloAi/zolo
- **Documentation:** https://github.com/ZoloAi/zolo#readme
- **Bug Tracker:** https://github.com/ZoloAi/zolo/issues
