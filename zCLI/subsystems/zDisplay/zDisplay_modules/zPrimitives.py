# zCLI/subsystems/zDisplay/zDisplay_modules/primitives/zPrimitives.py

"""zPrimitives class - encapsulates raw I/O primitives for zDisplay_new."""

from zCLI import json, time, getpass, asyncio, uuid

class zPrimitives:
    """Primitive I/O operations container for streamlined display operations."""

    def __init__(self, display_instance):
        """Initialize zPrimitives with reference to parent display instance."""
        self.display = display_instance
        # Track pending input requests for GUI mode
        self.pending_input_requests = {}
        self.response_futures = {}

    def _is_gui_mode(self):
        """Check if running in zBifrost (non-interactive WebSocket) mode."""
        if not self.display or not hasattr(self.display, 'mode'):
            return False
        # Non-interactive modes: anything that's not Terminal or Walker
        return self.display.mode not in ("Terminal", "Walker", "")

    # Output primitives - terminal output with optional GUI support
    def write_raw(self, content):
        """Write raw content with no formatting or newline."""
        # Terminal output (always)
        print(content, end='', flush=True)

        # GUI output (if in GUI mode)
        if self._is_gui_mode():
            self._write_gui(content, "raw")

    def write_line(self, content):
        """Write single line, ensuring newline."""
        # Ensure content has newline for terminal
        terminal_content = content
        if not terminal_content.endswith('\n'):
            terminal_content = terminal_content + '\n'

        # Terminal output (always)
        print(terminal_content, end='', flush=True)

        # GUI output (if in GUI mode) - send without newline
        if self._is_gui_mode():
            self._write_gui(content.rstrip('\n'), "line")

    def write_block(self, content):
        """Write multi-line block, ensuring final newline."""
        # Ensure content has newline for terminal
        terminal_content = content
        if terminal_content and not terminal_content.endswith('\n'):
            terminal_content = terminal_content + '\n'

        # Terminal output (always)
        print(terminal_content, end='', flush=True)

        # GUI output (if in GUI mode) - send without trailing newlines
        if self._is_gui_mode():
            self._write_gui(content.rstrip('\n') if content else "", "block")

    # Common GUI primitive for all write commands
    def _write_gui(self, content, write_type):
        """Common GUI primitive - sends JSON event via bifrost/WebSocket for all write types."""
        # Access zcli through display instance to send via comm subsystem
        if not self.display or not hasattr(self.display, 'zcli'):
            return

        zcli = self.display.zcli
        if not zcli or not hasattr(zcli, 'comm'):
            return

        try:
            # Remove trailing newlines for JSON (consistent with WebSocket output)
            content = content.rstrip('\n') if content else ""

            # Create JSON event (same structure as WebSocket output adapter)
            event_data = {
                "event": "output",
                "type": write_type,
                "content": content,
                "timestamp": time.time()
            }

            # Send via zComm's WebSocket broadcast (same pattern as WebSocket output)
            if hasattr(zcli.comm, 'broadcast_websocket'):
                try:
                    loop = asyncio.get_running_loop()
                    asyncio.create_task(
                        zcli.comm.broadcast_websocket(json.dumps(event_data))
                    )
                except RuntimeError:
                    # No running event loop - for tests/initialization, skip broadcast
                    pass

        except Exception:
            # Silently ignore GUI send failures - terminal fallback handles the output
            pass

    def _generate_request_id(self):
        """Generate unique request ID for GUI input requests."""
        return str(uuid.uuid4())

    def _send_input_request(self, request_type, prompt="", **kwargs):
        """Common GUI input primitive - sends input request via bifrost/WebSocket."""
        # Access zcli through display instance to send via comm subsystem
        if not self.display or not hasattr(self.display, 'zcli'):
            return None

        zcli = self.display.zcli
        if not zcli or not hasattr(zcli, 'comm'):
            return None

        request_id = self._generate_request_id()

        try:
            # Create input request event (same structure as WebSocketInput)
            request_event = {
                "event": "input_request",
                "requestId": request_id,
                "type": request_type,
                "prompt": prompt,
                "timestamp": time.time(),
                **kwargs
            }

            # Create future for response
            try:
                loop = asyncio.get_running_loop()
                future = loop.create_future()
            except RuntimeError:
                # No running event loop - use asyncio.Future()
                future = asyncio.Future()

            self.response_futures[request_id] = future

            # Send request via zComm's WebSocket broadcast
            if hasattr(zcli.comm, 'broadcast_websocket'):
                try:
                    loop = asyncio.get_running_loop()
                    asyncio.create_task(
                        zcli.comm.broadcast_websocket(json.dumps(request_event))
                    )
                except RuntimeError:
                    # No running event loop - for tests, just log the request
                    pass

            return future

        except Exception:
            # Return None if GUI request fails - terminal fallback will handle input
            return None

    def handle_input_response(self, request_id, value):
        """Handle input response from GUI client."""
        if request_id in self.response_futures:
            future = self.response_futures.pop(request_id)
            if not future.done():
                future.set_result(value)

    def send_gui_event(self, event_name, data):
        """GUI primitive - send clean event object via bifrost (no terminal processing)."""
        # Only works in GUI mode
        if not self._is_gui_mode():
            return False

        if not self.display or not hasattr(self.display, 'zcli'):
            return False

        zcli = self.display.zcli
        if not zcli or not hasattr(zcli, 'comm'):
            return False

        try:
            event_data = {
                "event": "zdisplay",
                "display_event": event_name,
                "data": data,
                "timestamp": time.time()
            }

            if hasattr(zcli.comm, 'broadcast_websocket'):
                try:
                    loop = asyncio.get_running_loop()
                    asyncio.create_task(
                        zcli.comm.broadcast_websocket(json.dumps(event_data))
                    )
                    return True
                except RuntimeError:
                    # No running event loop - for tests/initialization, skip broadcast
                    pass
        except Exception:
            pass

        return False

    # Input primitives - terminal input with optional GUI support
    def read_string(self, prompt=""):
        """Read string input - terminal (synchronous) or GUI (async future)."""
        # Terminal input (always available as fallback)
        if not self._is_gui_mode():
            if prompt:
                return input(prompt).strip()
            return input().strip()

        # GUI input - return future that will be resolved by GUI response
        gui_future = self._send_input_request("string", prompt)

        # Fallback to terminal if GUI request fails
        if gui_future is None:
            if prompt:
                return input(prompt).strip()
            return input().strip()

        return gui_future

    def read_password(self, prompt=""):
        """Read password input - terminal (synchronous) or GUI (async future)."""
        # Terminal input (always available as fallback)
        if not self._is_gui_mode():
            if prompt:
                return getpass.getpass(prompt).strip()
            return getpass.getpass().strip()

        # GUI input - return future that will be resolved by GUI response
        gui_future = self._send_input_request("password", prompt, masked=True)

        # Fallback to terminal if GUI request fails
        if gui_future is None:
            if prompt:
                return getpass.getpass(prompt).strip()
            return getpass.getpass().strip()

        return gui_future

    # Convenience aliases for backward compatibility
    @property
    def raw(self):
        """Alias for write_raw."""
        return self.write_raw

    @property
    def line(self):
        """Alias for write_line."""
        return self.write_line

    @property
    def block(self):
        """Alias for write_block."""
        return self.write_block

    @property
    def read(self):
        """Alias for read_string."""
        return self.read_string
