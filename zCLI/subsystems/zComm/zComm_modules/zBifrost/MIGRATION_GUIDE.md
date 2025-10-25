# zBifrost Event Migration Guide

The v2 refactor standardizes all WebSocket traffic on the `event` field. This
guide explains how to migrate existing integrations that relied on the legacy
`action` contract.

## 1. Update Client Payloads

| Legacy Payload                              | New Payload (event-based)                         |
|---------------------------------------------|---------------------------------------------------|
| `{ "action": "get_schema", "model": "User" }` | `{ "event": "get_schema", "model": "User" }` |
| `{ "action": "clear_cache" }`               | `{ "event": "clear_cache" }`                   |
| `{ "zKey": "^List.users" }`                 | `{ "event": "dispatch", "zKey": "^List.users" }` |
| `{ "cmd": "^List.users" }`                  | `{ "event": "dispatch", "cmd": "^List.users" }` |
| `{ "action": "read", "model": "User" }`   | `{ "event": "dispatch", "action": "read", "model": "User" }` |

> **Tip:** You can keep the `action` field when it conveys semantics for
> zDispatch. zBifrost will forward both `event` and `action` to the dispatcher.

## 2. Normalize Custom Hooks

If you emit custom messages from hooks or extensions, add the `event` key:

```javascript
// Before
client.emit('custom_message', { action: 'notify', payload: {...} });

// After
client.emit('custom_message', { event: 'notify', payload: {...} });
```

## 3. Server-Side Integrations

Python extensions that call `broadcast` or interact directly with the
WebSocket should send JSON containing `event`:

```python
await bifrost.broadcast(json.dumps({
    "event": "broadcast",
    "data": {"message": "Hello"}
}))
```

## 4. Test Checklist

1. Run automated tests: `pytest zTestSuite/zComm_Test.py`
2. Exercise GUI flows (zDisplay) to ensure input responses still round-trip.
3. Validate cache controls (`get_schema`, `clear_cache`, `cache_stats`).
4. Execute representative zDispatch commands via the client.

## 5. Deprecation Timeline

* `bifrost_bridge.py` remains temporarily for backwards compatibility but now
  issues a `DeprecationWarning`.
* Future releases will remove the legacy bridge once ecosystem clients have
  migrated to the event protocol.

## Resources

* [`MESSAGE_PROTOCOL.md`](MESSAGE_PROTOCOL.md) – Canonical event definitions.
* [`README.md`](README.md) – Architectural overview and component map.
* `Documentation/Bifrost_Modular_Architecture.md` – Historical context for the
  modular refactor.
