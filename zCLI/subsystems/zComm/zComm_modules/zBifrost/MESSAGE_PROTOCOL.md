# zBifrost Message Protocol

zBifrost now follows the same event-driven contract as `zDisplay`. Every
message **must** include an `event` field that identifies which handler will
process the payload. This file documents the canonical events supported by the
bridge and the expected payload shape for each domain package.

## Envelope

```json
{
  "event": "<event-name>",
  "_requestId": 42,        // Optional: request/response correlation
  "data": { ... }          // Optional: structured payload for specific events
}
```

> **Backward compatibility** – Messages that still use the legacy `action`
> field are automatically translated to their corresponding `event` value when
> possible. New integrations should always set `event` explicitly.

## Client Events (`bridge_modules/events/client_events.py`)

| Event            | Description                                       | Payload Fields                               |
|------------------|---------------------------------------------------|-----------------------------------------------|
| `connection_info`| Request a fresh snapshot of server state.         | Optional `context` hint. Response includes `auth`, `cache_stats`, and session metadata. |
| `input_response` | Respond to a pending zDisplay input request.      | `requestId` (string), `value` (any).          |

### Examples

```json
{
  "event": "connection_info"
}
```

```json
{
  "event": "input_response",
  "requestId": "login.email",
  "value": "user@example.com"
}
```

## Cache Events (`bridge_modules/events/cache_events.py`)

| Event           | Description                                   | Payload Fields                               |
|-----------------|-----------------------------------------------|-----------------------------------------------|
| `get_schema`    | Retrieve schema definition for a model.       | `model` (string)                              |
| `clear_cache`   | Clear schema + query caches.                   | *(none)*                                      |
| `cache_stats`   | Inspect cache statistics.                      | *(none)*                                      |
| `set_cache_ttl` | Update default TTL (seconds) for query cache.  | `ttl` (int, defaults to `60`)                 |

### Example

```json
{
  "event": "set_cache_ttl",
  "ttl": 120
}
```

## Discovery Events (`bridge_modules/events/discovery_events.py`)

| Event        | Description                               | Payload Fields                |
|--------------|-------------------------------------------|-------------------------------|
| `discover`   | Enumerate discoverable models/resources.  | *(none)*                      |
| `introspect` | Inspect a specific model's schema.        | `model` (string)              |

### Example

```json
{
  "event": "introspect",
  "model": "@.zCloud.schemas.schema.zIndex.zUsers"
}
```

## Dispatch Events (`bridge_modules/events/dispatch_events.py`)

All command routing is consolidated under the `dispatch` event. The payload is
forwarded to zDispatch unchanged. Use the traditional `action`, `model`, `zKey`,
and `filters` keys as needed.

| Event      | Description                                        | Payload Fields                                |
|------------|----------------------------------------------------|-----------------------------------------------|
| `dispatch` | Execute a zDispatch command or declarative request.| `zKey` / `cmd`, optional `action`, `model`, etc. |

### Example

```json
{
  "event": "dispatch",
  "zKey": "^List.users",
  "action": "read",
  "filters": {"active": true}
}
```

## Error Handling

* Unknown events are logged and rebroadcast to connected clients for
  transparency.
* Non-JSON payloads are rebroadcast verbatim.
* Handlers may emit `{"error": "<message>"}` responses when an operation fails.

## Related Documents

* [`README.md`](README.md) – Architectural overview.
* [`MIGRATION_GUIDE.md`](MIGRATION_GUIDE.md) – Step-by-step guidance for
  upgrading from legacy `action` messages.
