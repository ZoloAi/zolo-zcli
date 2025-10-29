# zBifrost Message Protocol

## Overview

zBifrost uses an **event-driven message protocol** aligned with zDisplay's architecture. All messages are JSON objects with a standardized `event` field that determines routing.

## Message Format

### Standard Format
```json
{
  "event": "event_name",
  "...": "additional parameters"
}
```

### Response Format
```json
{
  "result": "...",
  "_requestId": "optional_correlation_id"
}
```

### Error Format
```json
{
  "error": "error_message",
  "details": "additional_info"
}
```

---

## Event Types

### Client Events

#### `input_response`
User input from GUI client routed to zDisplay.

**Request:**
```json
{
  "event": "input_response",
  "requestId": "unique_id",
  "value": "user_input_value"
}
```

**Response:** None (routed internally to zDisplay)

#### `connection_info`
Request server connection information.

**Request:**
```json
{
  "event": "connection_info"
}
```

**Response:**
```json
{
  "event": "connection_info",
  "data": {
    "server_version": "1.5.4",
    "features": ["client_cache", "connection_info", "realtime_sync"],
    "auth": {...}
  }
}
```

---

### Cache Events

#### `get_schema`
Retrieve schema definition from server.

**Request:**
```json
{
  "event": "get_schema",
  "model": "@.zSchema.users"
}
```

**Response:**
```json
{
  "result": {
    "fields": [...],
    "...": "..."
  }
}
```

#### `clear_cache`
Clear query result cache.

**Request:**
```json
{
  "event": "clear_cache"
}
```

**Response:**
```json
{
  "result": "Cache cleared",
  "stats": {
    "hits": 100,
    "misses": 20,
    "expired": 5
  }
}
```

#### `cache_stats`
Get cache statistics.

**Request:**
```json
{
  "event": "cache_stats"
}
```

**Response:**
```json
{
  "result": {
    "query_cache": {
      "hits": 100,
      "misses": 20,
      "expired": 5
    }
  }
}
```

#### `set_cache_ttl`
Configure cache time-to-live.

**Request:**
```json
{
  "event": "set_cache_ttl",
  "ttl": 120
}
```

**Response:**
```json
{
  "result": "Query cache TTL set to 120s"
}
```

---

### Discovery Events

#### `discover`
Auto-discovery API - returns available schemas and operations.

**Request:**
```json
{
  "event": "discover"
}
```

**Response:**
```json
{
  "schemas": [...],
  "operations": [...]
}
```

#### `introspect`
Detailed schema introspection.

**Request:**
```json
{
  "event": "introspect",
  "model": "@.zSchema.users"
}
```

**Response:**
```json
{
  "model": "@.zSchema.users",
  "fields": [...],
  "relationships": [...],
  "operations": [...]
}
```

---

### Dispatch Events

#### `dispatch`
Execute zDispatch commands.

**Request:**
```json
{
  "event": "dispatch",
  "zKey": "^List.users",
  "zHorizontal": "^List.users",
  "_requestId": "optional_correlation_id",
  "cache_ttl": 60,
  "no_cache": false
}
```

**Response:**
```json
{
  "result": [...],
  "_requestId": "optional_correlation_id",
  "_cached": false
}
```

**Cache Options:**
- `cache_ttl`: Custom TTL in seconds (overrides default)
- `no_cache`: Set to `true` to bypass cache

---

## Backward Compatibility

The protocol supports legacy formats through automatic inference:

### Legacy Action Format
```json
{
  "action": "get_schema",
  "model": "..."
}
```
**Inferred as:** `event: "get_schema"`

### Legacy Command Format
```json
{
  "zKey": "^List.users",
  "cmd": "..."
}
```
**Inferred as:** `event: "dispatch"`

---

## Event Routing

All messages flow through a single entry point with an event map:

```python
self._event_map = {
    "input_response": handler_function,
    "get_schema": handler_function,
    "dispatch": handler_function,
    # ... etc
}
```

This mirrors zDisplay's event-driven architecture for consistency.

---

## Best Practices

1. **Always use `event` field** - Don't rely on backward compatibility inference for new code
2. **Include `_requestId`** - For correlation in async operations
3. **Handle errors gracefully** - Check for `error` field in responses
4. **Use cache wisely** - Set appropriate TTL for read operations
5. **Follow naming conventions** - Use lowercase_underscore for event names

---

## Migration from Old Format

### Before (Action-based)
```json
{"action": "get_schema", "model": "..."}
```

### After (Event-based)
```json
{"event": "get_schema", "model": "..."}
```

### Before (Command-based)
```json
{"zKey": "^List.users"}
```

### After (Event-based with dispatch)
```json
{"event": "dispatch", "zKey": "^List.users"}
```

---

## See Also

- `zDisplay` - Frontend display event system
- `zDispatch` - Command routing system
- `HOOKS_GUIDE.md` - WebSocket hooks and lifecycle

