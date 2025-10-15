# Test-Only Dependencies for zComm

⚠️ **IMPORTANT**: These dependencies are for TESTING ONLY and should NOT be in production!

## Test Dependencies

### Already in pyproject.toml (KEEP in production):
- ✅ `websockets>=15.0` - Core dependency for WebSocket server
- ✅ `pytest>=7.0` - Dev dependency for testing

### Additional Test Dependencies (REMOVE before production):
```bash
# Install these for testing zComm:
pip install pytest-asyncio>=0.21.0  # For async WebSocket tests
pip install aiohttp>=3.9.0          # For HTTP client testing
```

## How to Install for Testing

```bash
# From project root:
pip install pytest-asyncio aiohttp
```

## How to Remove Before Production

```bash
# Remove test-only packages:
pip uninstall pytest-asyncio aiohttp

# Or use a clean virtual environment for production
```

## Why These Are Test-Only

| Package | Purpose | Why Not Production |
|---------|---------|-------------------|
| `pytest-asyncio` | Test async WebSocket code | Only needed for running tests |
| `aiohttp` | Simulate HTTP/WS clients | Production code uses native websockets |

## Production Dependencies (Keep These)

| Package | Purpose | Required |
|---------|---------|----------|
| `websockets` | WebSocket server | ✅ Core |
| `PyYAML` | Config parsing | ✅ Core |
| `requests` | HTTP requests | ✅ Core |

---

**Last Updated**: October 15, 2025  
**Created By**: zComm test setup automation

