<!-- 7cae187d-3854-4a90-a3fd-eb168085f6b6 ac953d09-cfbf-46ba-94da-10dd96846ad4 -->
# Streamline zBifrost Architecture

## Objectives

- Align zBifrost with zDisplay's event-driven pattern
- Standardize all messages to use "event" field
- Create organized event packages
- Remove duplicate implementations
- Establish single handler entry point

## Phase 1: Restructure Foundation

### 1.1 Adopt Modular Implementation

- Use `bifrost_bridge_modular.py` as base (better architecture)
- Update `zBifrost/__init__.py` to import from modular version
- Keep `bifrost_bridge.py` temporarily with deprecation notice

**Files:**

- `zBifrost/__init__.py` - Change import from bifrost_bridge to bifrost_bridge_modular
- Add deprecation comment to `bifrost_bridge.py`

### 1.2 Create Event Packages Structure

```
bridge_modules/
├── events/
│   ├── __init__.py
│   ├── client_events.py      # input_response, connection_info
│   ├── cache_events.py        # schema, cache operations
│   ├── discovery_events.py    # discover, introspect
│   └── dispatch_events.py     # zDispatch command routing
```

## Phase 2: Implement Event-Driven Architecture

### 2.1 Create Event Handler Classes

**File: `bridge_modules/events/client_events.py`**

```python
class ClientEvents:
    async def handle_input_response(self, ws, data):
        """Route input to zDisplay"""
        
    async def handle_connection_info(self, ws, data):
        """Send connection info to client"""
```

**File: `bridge_modules/events/cache_events.py`**

```python
class CacheEvents:
    async def handle_get_schema(self, ws, data):
        """Get schema from loader"""
        
    async def handle_clear_cache(self, ws, data):
        """Clear query cache"""
        
    async def handle_cache_stats(self, ws, data):
        """Return cache statistics"""
        
    async def handle_set_cache_ttl(self, ws, data):
        """Configure cache TTL"""
```

**File: `bridge_modules/events/discovery_events.py`**

```python
class DiscoveryEvents:
    async def handle_discover(self, ws, data):
        """Auto-discovery API"""
        
    async def handle_introspect(self, ws, data):
        """Schema introspection"""
```

**File: `bridge_modules/events/dispatch_events.py`**

```python
class DispatchEvents:
    async def handle_dispatch(self, ws, data):
        """Execute zDispatch commands"""
```

### 2.2 Add Event Map to zBifrost

**File: `bifrost_bridge_modular.py`**

Add in `__init__`:

```python
from .bridge_modules.events import ClientEvents, CacheEvents, DiscoveryEvents, DispatchEvents

self.events = {
    'client': ClientEvents(self),
    'cache': CacheEvents(self),
    'discovery': DiscoveryEvents(self),
    'dispatch': DispatchEvents(self)
}

self._event_map = {
    # Client events
    "input_response": self.events['client'].handle_input_response,
    "connection_info": self.events['client'].handle_connection_info,
    
    # Cache events
    "get_schema": self.events['cache'].handle_get_schema,
    "clear_cache": self.events['cache'].handle_clear_cache,
    "cache_stats": self.events['cache'].handle_cache_stats,
    "set_cache_ttl": self.events['cache'].handle_set_cache_ttl,
    
    # Discovery events
    "discover": self.events['discovery'].handle_discover,
    "introspect": self.events['discovery'].handle_introspect,
    
    # Dispatch events
    "dispatch": self.events['dispatch'].handle_dispatch,
}
```

### 2.3 Create Single Handler Entry Point

**File: `bifrost_bridge_modular.py`**

Replace message handling in `handle_client`:

```python
async def handle_message(self, ws, message):
    """Single entry point for all messages (mirrors zDisplay.handle)"""
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        await self.broadcast(message, sender=ws)
        return
    
    # Get event type
    event = data.get("event")
    
    # Backward compatibility: infer event from old formats
    if not event:
        event = self._infer_event_type(data)
    
    # Route to handler
    handler = self._event_map.get(event)
    if not handler:
        self.logger.warning(f"[zBifrost] Unknown event: {event}")
        await self.broadcast(json.dumps(data), sender=ws)
        return
    
    # Execute handler
    await handler(ws, data)

def _infer_event_type(self, data):
    """Backward compatibility: map old formats to new events"""
    if "action" in data:
        return data["action"]  # action becomes event
    if "zKey" in data or "cmd" in data:
        return "dispatch"
    return None
```

## Phase 3: Standardize Message Protocol

### 3.1 Update MessageHandler to Use Event Field

**File: `bridge_modules/message_handler.py`**

Refactor `_handle_special_actions` to use event field:

```python
async def _handle_special_actions(self, ws, data):
    event = data.get("event")
    
    if event == "input_response":
        return await self._handle_input_response(data)
    elif event == "get_schema":
        return await self._handle_schema_request(ws, data)
    # ... etc
```

### 3.2 Update Client-Side Code

**File: `bifrost_client.js`** (lines 199-220)

Ensure all outgoing messages use "event" field:

```javascript
// OLD: {action: "get_schema", model: "..."}
// NEW: {event: "get_schema", model: "..."}

// OLD: {zKey: "^List.users"}
// NEW: {event: "dispatch", zKey: "^List.users"}
```

### 3.3 Document Message Protocol

**File: `zBifrost/MESSAGE_PROTOCOL.md`** (NEW)

Create comprehensive documentation of all event types and their payloads.

## Phase 4: Cleanup and Consolidation

### 4.1 Remove Duplicated Logic

- Remove inline message handling from `bifrost_bridge_modular.py` lines 100-150
- Consolidate all routing through `handle_message()`
- Delete redundant if/elif chains

### 4.2 Update Tests

**File: `zTestSuite/zComm_Test.py`**

Update test messages to use new event format:

```python
# OLD: {"action": "get_schema", ...}
# NEW: {"event": "get_schema", ...}
```

### 4.3 Deprecate Old Implementation

**File: `bifrost_bridge.py`**

Add deprecation warning at top:

```python
"""
DEPRECATED: This implementation is being phased out.
Use bifrost_bridge_modular.py instead.
"""
import warnings
warnings.warn("bifrost_bridge.py is deprecated", DeprecationWarning)
```

## Phase 5: Integration and Documentation

### 5.1 Update BifrostManager

**File: `bifrost_manager.py`**

Ensure it works with new modular implementation.

### 5.2 Update Documentation

**Files to update:**

- `zBifrost/README.md` - Document new event architecture
- `zBifrost/HOOKS_GUIDE.md` - Update with event format
- `zComm/README_REFACTORING.md` - Add zBifrost section

### 5.3 Create Migration Guide

**File: `zBifrost/MIGRATION_GUIDE.md`** (NEW)

Document how to migrate from old message format to new event-based format.

## Phase 6: Remove Old Implementation

### 6.1 Delete Deprecated Files

After testing confirms everything works:

- Delete `bifrost_bridge.py`
- Rename `bifrost_bridge_modular.py` to `bifrost_bridge.py`

### 6.2 Clean Up Imports

Update all imports throughout codebase to reference new structure.

## Success Criteria

- All messages use standardized "event" field
- Event map contains all handler registrations
- No duplicate message handling logic
- All tests passing with new format
- Single handler entry point (like zDisplay)
- Event packages organized by domain
- Documentation complete

## Files Modified

- `zBifrost/__init__.py`
- `zBifrost/bifrost_bridge_modular.py`
- `zBifrost/bridge_modules/message_handler.py`
- `zBifrost/bridge_modules/events/` (NEW directory)
- `zBifrost/bifrost_client.js`
- `zTestSuite/zComm_Test.py`
- Documentation files

## Estimated Effort

6-8 hours for complete implementation and testing

### To-dos

- [ ] Restructure zBifrost foundation - adopt modular implementation and create event packages structure
- [ ] Implement event-driven architecture - create event handler classes, add event map, create single handler entry point
- [ ] Standardize message protocol - update to use 'event' field everywhere, update client-side code, document protocol
- [ ] Cleanup and consolidation - remove duplicated logic, update tests, deprecate old implementation
- [ ] Integration and documentation - update BifrostManager, update all docs, create migration guide
- [ ] Remove old implementation - delete deprecated files, clean up imports