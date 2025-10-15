"""
zBifrost - WebSocket Client Bridge
🌈 The rainbow bridge connecting clients to zCLI server

Named after Bifröst from Norse mythology - the burning rainbow bridge
that connects Midgard (Earth) to Asgard (realm of the gods).

zBifrost connects your applications to the zCLI backend, enabling:
- Real-time CRUD operations
- Command dispatch (zFunc, zLink, zOpen, etc.)
- Broadcast message listening
- Authentication handling
- Request/response correlation

Usage:
    from zCLI.subsystems.zComm.zComm_modules.zBifrost import zBifrost
    
    async def main():
        client = zBifrost(url="ws://127.0.0.1:56891", token="your-token")
        await client.connect()
        
        # CRUD operations
        user = await client.create("Users", {"name": "Alice"})
        users = await client.read("Users", {"active": True})
        await client.update("Users", user["id"], {"name": "Alice Smith"})
        await client.delete("Users", user["id"])
        
        # Listen to broadcasts
        def on_message(msg):
            print(f"Broadcast: {msg}")
        client.on_broadcast(on_message)
        
        await client.close()
    
    asyncio.run(main())
"""

import asyncio
import json
from typing import Any, Callable, Dict, List, Optional, Union
from logger import Logger

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
except ImportError as exc:
    raise ImportError(
        "websockets package required for zBifrost client.\n"
        "Install with: pip install websockets"
    ) from exc

# Logger instance
logger = Logger.get_logger(__name__)


class zBifrost:
    """
    🌈 zBifrost - WebSocket Client Bridge to zCLI Server
    
    The rainbow bridge connecting your application to the zCLI backend.
    Provides simplified API for CRUD operations, command dispatch, and real-time messaging.
    """
    
    def __init__(
        self, 
        url: str = "ws://127.0.0.1:56891",
        token: Optional[str] = None,
        auto_reconnect: bool = False,
        debug: bool = False
    ):
        """
        Initialize zBifrost client.
        
        Args:
            url: WebSocket server URL
            token: Authentication token (if required)
            auto_reconnect: Automatically reconnect on disconnection
            debug: Enable debug logging
        """
        self.url = url
        self.token = token
        self.auto_reconnect = auto_reconnect
        self.debug = debug
        
        self.ws: Optional[WebSocketClientProtocol] = None
        self.connected = False
        self.callbacks: Dict[int, Dict[str, Callable]] = {}
        self.broadcast_listeners: List[Callable] = []
        self.request_id = 0
        self._listen_task: Optional[asyncio.Task] = None
        
        self.logger = logger
    
    async def connect(self) -> bool:
        """
        Connect to zCLI WebSocket server.
        
        Returns:
            bool: True if connected successfully
        
        Raises:
            ConnectionRefusedError: If server is not available
            websockets.exceptions.InvalidStatusCode: If authentication fails
        """
        try:
            # Add token to URL if provided
            connect_url = self.url
            if self.token:
                separator = "&" if "?" in self.url else "?"
                connect_url = f"{self.url}{separator}token={self.token}"
            
            self.logger.info(f"[zBifrost] 🌈 Connecting to {self.url}...")
            self.ws = await websockets.connect(connect_url)
            self.connected = True
            
            # Start listening for messages
            self._listen_task = asyncio.create_task(self._message_listener())
            
            self.logger.info("[zBifrost] ✅ Connected to zCLI server")
            return True
            
        except ConnectionRefusedError:
            self.logger.error("[zBifrost] ❌ Connection refused - is the server running?")
            raise
        except Exception as e:
            self.logger.error(f"[zBifrost] ❌ Connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from server."""
        self.connected = False
        if self._listen_task:
            self._listen_task.cancel()
        if self.ws:
            await self.ws.close()
            self.logger.info("[zBifrost] 🚪 Disconnected from server")
    
    async def close(self):
        """Alias for disconnect()."""
        await self.disconnect()
    
    # ═══════════════════════════════════════════════════════════
    # CRUD Operations - Simplified API
    # ═══════════════════════════════════════════════════════════
    
    async def create(self, model: str, values: Dict[str, Any]) -> Any:
        """
        Create a new record.
        
        Args:
            model: Table/model name (e.g., "Users", "Products")
            values: Dictionary of field values
        
        Returns:
            Created record (usually with ID)
        
        Example:
            user = await client.create("Users", {
                "name": "Alice",
                "email": "alice@example.com"
            })
        """
        return await self.send({
            "zKey": f"create_{model}",
            "zHorizontal": {
                "action": "create",
                "model": model,
                "values": values
            }
        })
    
    async def read(
        self, 
        model: str, 
        filters: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Read records from database.
        
        Args:
            model: Table/model name
            filters: WHERE conditions (e.g., {"active": True, "age__gte": 18})
            fields: List of fields to return
            order_by: Sort order (e.g., "created_at DESC")
            limit: Maximum number of records
            offset: Number of records to skip
        
        Returns:
            List of records
        
        Example:
            users = await client.read("Users", 
                filters={"active": True, "age__gte": 18},
                fields=["id", "name", "email"],
                order_by="created_at DESC",
                limit=10
            )
        """
        horizontal = {
            "action": "read",
            "model": model
        }
        
        if filters:
            horizontal["where"] = filters
        if fields:
            horizontal["fields"] = fields
        if order_by:
            horizontal["order_by"] = order_by
        if limit is not None:
            horizontal["limit"] = limit
        if offset is not None:
            horizontal["offset"] = offset
        
        return await self.send({
            "zKey": f"read_{model}",
            "zHorizontal": horizontal
        })
    
    async def update(
        self, 
        model: str, 
        filters: Union[int, Dict[str, Any]], 
        values: Dict[str, Any]
    ) -> Any:
        """
        Update record(s).
        
        Args:
            model: Table/model name
            filters: Either an ID (int) or WHERE conditions (dict)
            values: Dictionary of fields to update
        
        Returns:
            Update result (affected rows count or updated record)
        
        Example:
            # Update by ID
            await client.update("Users", 123, {"name": "Alice Smith"})
            
            # Update by filters
            await client.update("Users", 
                {"email": "alice@example.com"}, 
                {"active": True}
            )
        """
        # Convert ID to filter dict
        if isinstance(filters, int):
            filters = {"id": filters}
        
        return await self.send({
            "zKey": f"update_{model}",
            "zHorizontal": {
                "action": "update",
                "model": model,
                "where": filters,
                "values": values
            }
        })
    
    async def delete(
        self, 
        model: str, 
        filters: Union[int, Dict[str, Any]]
    ) -> Any:
        """
        Delete record(s).
        
        Args:
            model: Table/model name
            filters: Either an ID (int) or WHERE conditions (dict)
        
        Returns:
            Delete result (affected rows count)
        
        Example:
            # Delete by ID
            await client.delete("Users", 123)
            
            # Delete by filters
            await client.delete("Users", {"active": False, "created_at__lt": "2020-01-01"})
        """
        # Convert ID to filter dict
        if isinstance(filters, int):
            filters = {"id": filters}
        
        return await self.send({
            "zKey": f"delete_{model}",
            "zHorizontal": {
                "action": "delete",
                "model": model,
                "where": filters
            }
        })
    
    async def upsert(
        self,
        model: str,
        values: Dict[str, Any],
        conflict_fields: Optional[List[str]] = None
    ) -> Any:
        """
        Upsert (insert or update) a record.
        
        Args:
            model: Table/model name
            values: Dictionary of field values
            conflict_fields: Fields to check for conflicts (defaults to primary key)
        
        Returns:
            Upserted record
        
        Example:
            user = await client.upsert("Users",
                {"email": "alice@example.com", "name": "Alice"},
                conflict_fields=["email"]
            )
        """
        horizontal = {
            "action": "upsert",
            "model": model,
            "values": values
        }
        
        if conflict_fields:
            horizontal["conflict_fields"] = conflict_fields
        
        return await self.send({
            "zKey": f"upsert_{model}",
            "zHorizontal": horizontal
        })
    
    # ═══════════════════════════════════════════════════════════
    # Advanced Operations
    # ═══════════════════════════════════════════════════════════
    
    async def zFunc(self, func_call: str) -> Any:
        """
        Execute a zFunc command on the server.
        
        Args:
            func_call: zFunc command string (e.g., "zFunc(myFunction, {...})")
        
        Returns:
            Function execution result
        
        Example:
            result = await client.zFunc("zFunc(calculateTotal, {'cart_id': 123})")
        """
        return await self.send({
            "zKey": "zFunc",
            "zHorizontal": func_call
        })
    
    async def zLink(self, link_path: str) -> Any:
        """
        Navigate to a zLink path.
        
        Args:
            link_path: zLink navigation path
        
        Returns:
            Navigation result
        """
        return await self.send({
            "zKey": "zLink",
            "zHorizontal": f"zLink({link_path})"
        })
    
    async def zOpen(self, open_command: str) -> Any:
        """
        Execute a zOpen command.
        
        Args:
            open_command: zOpen command string
        
        Returns:
            Command execution result
        """
        return await self.send({
            "zKey": "zOpen",
            "zHorizontal": f"zOpen({open_command})"
        })
    
    # ═══════════════════════════════════════════════════════════
    # Raw Send/Receive
    # ═══════════════════════════════════════════════════════════
    
    async def send(self, payload: Dict[str, Any], timeout: float = 30.0) -> Any:
        """
        Send a message and wait for response.
        
        Args:
            payload: Message payload (must include zKey and zHorizontal)
            timeout: Response timeout in seconds
        
        Returns:
            Server response result
        
        Raises:
            ConnectionError: If not connected
            asyncio.TimeoutError: If response timeout
            Exception: If server returns error
        """
        if not self.connected or not self.ws:
            raise ConnectionError("Not connected to server. Call connect() first.")
        
        # Add request ID for correlation
        request_id = self.request_id
        self.request_id += 1
        payload["_requestId"] = request_id
        
        # Create response future
        future = asyncio.Future()
        self.callbacks[request_id] = {"future": future}
        
        try:
            # Send message
            message = json.dumps(payload)
            if self.debug:
                self.logger.debug(f"[zBifrost] 📤 Sending: {message}")
            await self.ws.send(message)
            
            # Wait for response with timeout
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
            
        except asyncio.TimeoutError:
            self.callbacks.pop(request_id, None)
            self.logger.error(f"[zBifrost] ⏱️ Request timeout after {timeout}s")
            raise
        except Exception as e:
            self.callbacks.pop(request_id, None)
            self.logger.error(f"[zBifrost] ❌ Send error: {e}")
            raise
    
    # ═══════════════════════════════════════════════════════════
    # Broadcast Listening
    # ═══════════════════════════════════════════════════════════
    
    def on_broadcast(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Register a callback for broadcast messages.
        
        Args:
            callback: Function to call when broadcast received
        
        Example:
            def handle_update(message):
                print(f"Update: {message}")
            
            client.on_broadcast(handle_update)
        """
        self.broadcast_listeners.append(callback)
        self.logger.debug("[zBifrost] 📻 Broadcast listener registered")
    
    def remove_broadcast_listener(self, callback: Callable):
        """Remove a broadcast listener."""
        if callback in self.broadcast_listeners:
            self.broadcast_listeners.remove(callback)
    
    # ═══════════════════════════════════════════════════════════
    # Internal Methods
    # ═══════════════════════════════════════════════════════════
    
    async def _message_listener(self):
        """Background task to listen for incoming messages."""
        try:
            async for message in self.ws:
                if self.debug:
                    self.logger.debug(f"[zBifrost] 📥 Received: {message}")
                await self._handle_message(message)
        except asyncio.CancelledError:
            self.logger.debug("[zBifrost] Message listener cancelled")
        except Exception as e:
            self.logger.error(f"[zBifrost] ❌ Listener error: {e}")
            if self.auto_reconnect:
                await self._reconnect()
    
    async def _handle_message(self, message: str):
        """Process incoming message."""
        try:
            data = json.loads(message)
            
            # Check if it's a response to our request
            request_id = data.get("_requestId")
            if request_id is not None and request_id in self.callbacks:
                callback = self.callbacks.pop(request_id)
                future = callback["future"]
                
                if "error" in data:
                    future.set_exception(Exception(data["error"]))
                else:
                    future.set_result(data.get("result"))
            else:
                # It's a broadcast message
                self._handle_broadcast(data)
                
        except json.JSONDecodeError:
            self.logger.warning(f"[zBifrost] ⚠️ Non-JSON message: {message}")
        except Exception as e:
            self.logger.error(f"[zBifrost] ❌ Message handling error: {e}")
    
    def _handle_broadcast(self, message: Dict[str, Any]):
        """Handle broadcast message."""
        if self.debug:
            self.logger.debug(f"[zBifrost] 📻 Broadcast: {message}")
        
        for listener in self.broadcast_listeners:
            try:
                listener(message)
            except Exception as e:
                self.logger.error(f"[zBifrost] ❌ Broadcast listener error: {e}")
    
    async def _reconnect(self):
        """Attempt to reconnect."""
        self.logger.info("[zBifrost] 🔄 Attempting to reconnect...")
        await asyncio.sleep(2)
        try:
            await self.connect()
        except Exception as e:
            self.logger.error(f"[zBifrost] ❌ Reconnection failed: {e}")
            if self.auto_reconnect:
                await self._reconnect()
    
    # ═══════════════════════════════════════════════════════════
    # Context Manager Support
    # ═══════════════════════════════════════════════════════════
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# ═══════════════════════════════════════════════════════════
# Convenience Functions
# ═══════════════════════════════════════════════════════════

async def create_client(
    url: str = "ws://127.0.0.1:56891",
    token: Optional[str] = None,
    **kwargs
) -> zBifrost:
    """
    Create and connect a zBifrost client.
    
    Args:
        url: WebSocket server URL
        token: Authentication token
        **kwargs: Additional client options
    
    Returns:
        Connected zBifrost client
    
    Example:
        client = await create_client("ws://localhost:56891", token="abc123")
        users = await client.read("Users")
        await client.close()
    """
    client = zBifrost(url=url, token=token, **kwargs)
    await client.connect()
    return client

