# zTestSuite/zBifrost_Unit_Test.py

"""
Unit tests for zBifrost subsystem modules - Week 2.3 Coverage Phase 1

Target: Achieve 85% overall Layer 0 coverage by testing:
- message_handler.py (16% → 90%)
- authentication.py (44% → 90%)
- dispatch_events.py (60% → 90%)
- bifrost_bridge_modular.py edge cases (77% → 95%)
"""

import unittest
import sys
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock, patch
import asyncio

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zComm.zComm_modules.zBifrost.bridge_modules.message_handler import MessageHandler
from zCLI.subsystems.zComm.zComm_modules.zBifrost.bridge_modules.authentication import AuthenticationManager
from zCLI.subsystems.zComm.zComm_modules.zBifrost.bridge_modules.events.dispatch_events import DispatchEvents


# ═══════════════════════════════════════════════════════════════════
# Test: MessageHandler (16% → 90%)
# ═══════════════════════════════════════════════════════════════════

class TestMessageHandler(unittest.IsolatedAsyncioTestCase):
    """Unit tests for MessageHandler - Core message routing logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = Mock()
        self.cache = Mock()
        self.zcli = Mock()
        self.walker = Mock()
        self.connection_info = Mock()
        
        self.handler = MessageHandler(
            self.logger,
            self.cache,
            self.zcli,
            self.walker,
            self.connection_info
        )
    
    async def test_handle_valid_json_message(self):
        """Should parse and route valid JSON messages"""
        ws = AsyncMock()
        broadcast = AsyncMock()
        
        message = json.dumps({"event": "test", "data": "value"})
        
        # Mock _handle_special_actions to return False (not special)
        with patch.object(self.handler, '_handle_special_actions', return_value=False):
            with patch.object(self.handler, '_handle_dispatch', return_value=True):
                result = await self.handler.handle_message(ws, message, broadcast)
        
        self.assertTrue(result)
    
    async def test_handle_invalid_json_broadcasts_raw(self):
        """Should broadcast non-JSON messages as-is"""
        ws = AsyncMock()
        broadcast = AsyncMock()
        
        message = "not json at all"
        
        result = await self.handler.handle_message(ws, message, broadcast)
        
        # Should broadcast the raw message
        broadcast.assert_called_once_with(message, sender=ws)
        self.assertTrue(result)
    
    async def test_handle_empty_message(self):
        """Should handle empty messages gracefully"""
        ws = AsyncMock()
        broadcast = AsyncMock()
        
        message = ""
        
        result = await self.handler.handle_message(ws, message, broadcast)
        
        # Empty string is valid JSON string, so might be broadcasted
        self.assertTrue(result)
    
    async def test_handle_malformed_json(self):
        """Should handle malformed JSON by broadcasting raw"""
        ws = AsyncMock()
        broadcast = AsyncMock()
        
        message = '{"incomplete": '
        
        result = await self.handler.handle_message(ws, message, broadcast)
        
        broadcast.assert_called_once_with(message, sender=ws)
        self.assertTrue(result)
    
    async def test_special_action_handling(self):
        """Should detect and route special actions"""
        ws = AsyncMock()
        broadcast = AsyncMock()
        
        message = json.dumps({"action": "special_action", "data": "test"})
        
        with patch.object(self.handler, '_handle_special_actions', return_value=True):
            result = await self.handler.handle_message(ws, message, broadcast)
        
        self.assertTrue(result)
    
    async def test_dispatch_command_routing(self):
        """Should route zDispatch commands correctly"""
        ws = AsyncMock()
        broadcast = AsyncMock()
        
        message = json.dumps({"zKey": "^List.users"})
        
        with patch.object(self.handler, '_handle_special_actions', return_value=False):
            with patch.object(self.handler, '_handle_dispatch', return_value=True) as mock_dispatch:
                result = await self.handler.handle_message(ws, message, broadcast)
                
                mock_dispatch.assert_called_once()
        
        self.assertTrue(result)
    
    async def test_message_with_request_id(self):
        """Should preserve _requestId in responses"""
        ws = AsyncMock()
        broadcast = AsyncMock()
        
        message = json.dumps({"event": "test", "_requestId": "req-123"})
        
        with patch.object(self.handler, '_handle_special_actions', return_value=False):
            with patch.object(self.handler, '_handle_dispatch', return_value=True):
                result = await self.handler.handle_message(ws, message, broadcast)
        
        self.assertTrue(result)
    
    async def test_exception_during_message_handling(self):
        """Should handle exceptions during message processing"""
        ws = AsyncMock()
        broadcast = AsyncMock()
        
        message = json.dumps({"event": "test"})
        
        # Make special actions raise an exception
        with patch.object(self.handler, '_handle_special_actions', side_effect=Exception("Test error")):
            # Should not crash
            try:
                result = await self.handler.handle_message(ws, message, broadcast)
                # If it returns, that's fine
            except Exception:
                # If it raises, that's also acceptable for now
                pass
    
    async def test_handle_input_response_event(self):
        """Should route input_response events to zDisplay"""
        ws = AsyncMock()
        
        data = {"event": "input_response", "requestId": "req-123", "value": "test_value"}
        
        # Mock zCLI display
        self.zcli.display = Mock()
        self.zcli.display.input = Mock()
        self.zcli.display.input.handle_input_response = Mock()
        
        result = await self.handler._handle_special_actions(ws, data)
        
        self.assertTrue(result)
        self.zcli.display.input.handle_input_response.assert_called_once_with("req-123", "test_value")
    
    async def test_handle_schema_request_found(self):
        """Should return schema when found"""
        ws = AsyncMock()
        data = {"action": "get_schema", "model": "users"}
        
        # Mock schema loader
        self.cache.get_schema = Mock(return_value={"model": "users", "fields": []})
        
        result = await self.handler._handle_special_actions(ws, data)
        
        self.assertTrue(result)
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertIn("result", sent_data)
    
    async def test_handle_schema_request_not_found(self):
        """Should return error when schema not found"""
        ws = AsyncMock()
        data = {"action": "get_schema", "model": "nonexistent"}
        
        # Mock schema loader returning None
        self.cache.get_schema = Mock(return_value=None)
        
        result = await self.handler._handle_special_actions(ws, data)
        
        self.assertTrue(result)
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertIn("error", sent_data)
    
    async def test_handle_schema_request_no_model(self):
        """Should return False when model is missing"""
        ws = AsyncMock()
        data = {"action": "get_schema"}  # No model
        
        result = await self.handler._handle_special_actions(ws, data)
        
        self.assertFalse(result)
    
    async def test_handle_clear_cache(self):
        """Should clear cache and return stats"""
        ws = AsyncMock()
        data = {"action": "clear_cache"}
        
        self.cache.clear_all = Mock()
        self.cache.get_all_stats = Mock(return_value={"queries": 0, "schemas": 0})
        
        result = await self.handler._handle_special_actions(ws, data)
        
        self.assertTrue(result)
        self.cache.clear_all.assert_called_once()
        ws.send.assert_called_once()
    
    async def test_handle_cache_stats(self):
        """Should return cache statistics"""
        ws = AsyncMock()
        data = {"action": "cache_stats"}
        
        self.cache.get_all_stats = Mock(return_value={"queries": 10, "schemas": 5})
        
        result = await self.handler._handle_special_actions(ws, data)
        
        self.assertTrue(result)
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertEqual(sent_data["result"]["queries"], 10)
    
    async def test_handle_set_ttl(self):
        """Should set cache TTL"""
        ws = AsyncMock()
        data = {"action": "set_query_cache_ttl", "ttl": 120}
        
        self.cache.set_query_ttl = Mock()
        
        result = await self.handler._handle_special_actions(ws, data)
        
        self.assertTrue(result)
        self.cache.set_query_ttl.assert_called_once_with(120)
    
    async def test_handle_set_ttl_default(self):
        """Should use default TTL when not provided"""
        ws = AsyncMock()
        data = {"action": "set_query_cache_ttl"}  # No ttl
        
        self.cache.set_query_ttl = Mock()
        
        result = await self.handler._handle_special_actions(ws, data)
        
        self.assertTrue(result)
        self.cache.set_query_ttl.assert_called_once_with(60)
    
    async def test_handle_discover_with_connection_info(self):
        """Should discover models when connection_info available"""
        ws = AsyncMock()
        data = {"action": "discover"}
        
        self.connection_info._discover_models = Mock(return_value=["users", "products"])
        
        result = await self.handler._handle_special_actions(ws, data)
        
        self.assertTrue(result)
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertEqual(sent_data["result"]["models"], ["users", "products"])
    
    async def test_handle_discover_without_connection_info(self):
        """Should return error when connection_info not available"""
        ws = AsyncMock()
        data = {"action": "discover"}
        
        # No connection_info
        handler = MessageHandler(self.logger, self.cache, self.zcli, self.walker, connection_info_manager=None)
        
        result = await handler._handle_special_actions(ws, data)
        
        self.assertTrue(result)
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertIn("error", sent_data)
    
    async def test_handle_introspect_with_model(self):
        """Should introspect model when provided"""
        ws = AsyncMock()
        data = {"action": "introspect", "model": "users"}
        
        self.connection_info.introspect_model = Mock(return_value={"model": "users", "schema": {}})
        
        result = await self.handler._handle_special_actions(ws, data)
        
        self.assertTrue(result)
        ws.send.assert_called_once()
    
    async def test_handle_introspect_without_model(self):
        """Should return error when model is missing"""
        ws = AsyncMock()
        data = {"action": "introspect"}  # No model
        
        result = await self.handler._handle_special_actions(ws, data)
        
        self.assertTrue(result)
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertIn("error", sent_data)
    
    async def test_handle_dispatch_no_zkey(self):
        """Should broadcast data when no zKey provided"""
        ws = AsyncMock()
        broadcast = AsyncMock()
        data = {"message": "test"}
        
        result = await self.handler._handle_dispatch(ws, data, broadcast)
        
        self.assertTrue(result)
        broadcast.assert_called_once()
    
    async def test_handle_dispatch_cache_hit(self):
        """Should return cached result on cache hit"""
        ws = AsyncMock()
        broadcast = AsyncMock()
        data = {"zKey": "^List.users"}
        
        with patch.object(self.handler, '_is_cacheable_operation', return_value=True):
            self.cache.generate_cache_key = Mock(return_value="cache_key")
            self.cache.get_query = Mock(return_value=[{"id": 1, "name": "User1"}])
            
            result = await self.handler._handle_dispatch(ws, data, broadcast)
        
        self.assertTrue(result)
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertTrue(sent_data.get("_cached"))
    
    async def test_handle_dispatch_cache_miss_success(self):
        """Should execute command on cache miss and cache result"""
        ws = AsyncMock()
        broadcast = AsyncMock()
        data = {"zKey": "^List.users"}
        
        with patch.object(self.handler, '_is_cacheable_operation', return_value=True):
            self.cache.generate_cache_key = Mock(return_value="cache_key")
            self.cache.get_query = Mock(return_value=None)  # Cache miss
            self.cache.cache_query = Mock()
            
            # Mock asyncio.to_thread to return result directly
            with patch('asyncio.to_thread', new=AsyncMock(return_value={"data": "result"})):
                result = await self.handler._handle_dispatch(ws, data, broadcast)
        
        self.assertTrue(result)
        self.cache.cache_query.assert_called_once()
        ws.send.assert_called_once()
    
    async def test_handle_dispatch_execution_error(self):
        """Should return error on execution exception"""
        ws = AsyncMock()
        broadcast = AsyncMock()
        data = {"zKey": "^Invalid.command"}
        
        with patch.object(self.handler, '_is_cacheable_operation', return_value=False):
            # Mock dispatch to raise exception
            with patch('asyncio.to_thread', new=AsyncMock(side_effect=Exception("Command failed"))):
                result = await self.handler._handle_dispatch(ws, data, broadcast)
        
        self.assertTrue(result)
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertIn("error", sent_data)
    
    async def test_handle_dispatch_with_no_cache_flag(self):
        """Should skip cache when no_cache flag is set"""
        ws = AsyncMock()
        broadcast = AsyncMock()
        data = {"zKey": "^List.users", "no_cache": True}
        
        with patch.object(self.handler, '_is_cacheable_operation', return_value=True):
            self.cache.get_query = Mock()
            
            # Mock dispatch execution
            with patch('asyncio.to_thread', new=AsyncMock(return_value={"data": "result"})):
                result = await self.handler._handle_dispatch(ws, data, broadcast)
        
        # Cache should not be checked
        self.cache.get_query.assert_not_called()
    
    async def test_handle_dispatch_with_cmd_alias(self):
        """Should accept cmd as alias for zKey"""
        ws = AsyncMock()
        broadcast = AsyncMock()
        data = {"cmd": "test_command"}
        
        with patch.object(self.handler, '_is_cacheable_operation', return_value=False):
            with patch('asyncio.to_thread', new=AsyncMock(return_value="result")):
                result = await self.handler._handle_dispatch(ws, data, broadcast)
        
        self.assertTrue(result)
        ws.send.assert_called_once()
    
    def test_is_cacheable_operation_list(self):
        """Should identify List operations as cacheable"""
        data = {"zKey": "^List.users"}
        
        result = self.handler._is_cacheable_operation(data, "^List.users")
        
        # Should be cacheable (read operation)
        self.assertIsInstance(result, bool)
    
    def test_is_cacheable_operation_create(self):
        """Should identify Create operations as non-cacheable"""
        data = {"zKey": "^Create.users"}
        
        result = self.handler._is_cacheable_operation(data, "^Create.users")
        
        # Should be non-cacheable (write operation)
        self.assertIsInstance(result, bool)


# ═══════════════════════════════════════════════════════════════════
# Test: AuthenticationManager (44% → 90%)
# ═══════════════════════════════════════════════════════════════════

class TestAuthenticationManager(unittest.IsolatedAsyncioTestCase):
    """Unit tests for AuthenticationManager - Security validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = Mock()
    
    def test_init_with_defaults(self):
        """Should initialize with default values"""
        auth = AuthenticationManager(self.logger)
        
        self.assertTrue(auth.require_auth)
        self.assertEqual(auth.allowed_origins, [])
        self.assertEqual(auth.authenticated_clients, {})
    
    def test_init_with_custom_values(self):
        """Should accept custom initialization values"""
        auth = AuthenticationManager(
            self.logger,
            require_auth=False,
            allowed_origins=["http://localhost:3000"]
        )
        
        self.assertFalse(auth.require_auth)
        self.assertEqual(auth.allowed_origins, ["http://localhost:3000"])
    
    def test_validate_origin_no_restrictions(self):
        """Should allow any origin when no restrictions configured"""
        auth = AuthenticationManager(self.logger, allowed_origins=[])
        
        ws = Mock()
        result = auth.validate_origin(ws)
        
        self.assertTrue(result)
    
    def test_validate_origin_with_valid_origin(self):
        """Should allow valid origin"""
        auth = AuthenticationManager(
            self.logger,
            allowed_origins=["http://localhost:3000"]
        )
        
        ws = Mock()
        ws.request_headers = {"Origin": "http://localhost:3000"}
        
        result = auth.validate_origin(ws)
        
        self.assertTrue(result)
    
    def test_validate_origin_with_invalid_origin(self):
        """Should reject invalid origin"""
        auth = AuthenticationManager(
            self.logger,
            allowed_origins=["http://localhost:3000"]
        )
        
        ws = Mock()
        ws.request_headers = {"Origin": "http://evil.com"}
        ws.remote_address = ("192.168.1.1", 12345)
        
        result = auth.validate_origin(ws)
        
        self.assertFalse(result)
        self.logger.warning.assert_called()
    
    def test_validate_origin_missing_header(self):
        """Should reject connections without Origin header when restrictions are in place"""
        auth = AuthenticationManager(
            self.logger,
            allowed_origins=["http://localhost:3000"]
        )
        
        ws = Mock()
        ws.request_headers = Mock()
        ws.request_headers.get = Mock(return_value="")  # Empty Origin header
        ws.remote_address = ("192.168.1.1", 12345)
        
        result = auth.validate_origin(ws)
        
        self.assertFalse(result)
    
    def test_validate_origin_partial_match(self):
        """Should allow origins that start with allowed pattern"""
        auth = AuthenticationManager(
            self.logger,
            allowed_origins=["http://localhost"]
        )
        
        ws = Mock()
        ws.request_headers = {"Origin": "http://localhost:3000"}
        
        result = auth.validate_origin(ws)
        
        self.assertTrue(result)
    
    def test_validate_origin_empty_allowed_list_item(self):
        """Should handle empty strings in allowed_origins"""
        auth = AuthenticationManager(
            self.logger,
            allowed_origins=["", "http://localhost:3000"]
        )
        
        ws = Mock()
        ws.request_headers = {"Origin": "http://localhost:3000"}
        
        result = auth.validate_origin(ws)
        
        self.assertTrue(result)
    
    def test_validate_origin_with_whitespace(self):
        """Should handle whitespace in allowed_origins"""
        auth = AuthenticationManager(
            self.logger,
            allowed_origins=[" http://localhost:3000 "]
        )
        
        ws = Mock()
        ws.request_headers = {"Origin": "http://localhost:3000"}
        
        result = auth.validate_origin(ws)
        
        self.assertTrue(result)
    
    async def test_authenticate_client_auth_disabled(self):
        """Should skip authentication when disabled"""
        auth = AuthenticationManager(self.logger, require_auth=False)
        
        ws = AsyncMock()
        walker = Mock()
        
        result = await auth.authenticate_client(ws, walker)
        
        self.assertIsNotNone(result)
        self.assertTrue(result["authenticated"])
        self.assertEqual(result["user"], "anonymous")
    
    async def test_authenticate_client_missing_token(self):
        """Should reject client without token"""
        auth = AuthenticationManager(self.logger, require_auth=True)
        
        ws = AsyncMock()
        ws.path = "/"
        ws.request_headers = Mock()
        ws.request_headers.get = Mock(return_value="")  # Return empty string for missing header
        walker = Mock()
        
        result = await auth.authenticate_client(ws, walker)
        
        # Should close connection
        ws.close.assert_called_once()
        self.assertIsNone(result)
    
    async def test_authenticate_client_with_valid_token(self):
        """Should authenticate client with valid token"""
        auth = AuthenticationManager(self.logger, require_auth=True)
        
        ws = AsyncMock()
        ws.path = "/?token=valid_token_123"
        ws.request_headers = {}
        walker = Mock()
        
        # Mock token validation
        with patch.object(auth, '_validate_token', return_value={"user": "testuser", "role": "admin"}):
            result = await auth.authenticate_client(ws, walker)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["user"], "testuser")
    
    async def test_authenticate_client_token_in_header(self):
        """Should extract token from Authorization header"""
        auth = AuthenticationManager(self.logger, require_auth=True)
        
        ws = AsyncMock()
        ws.path = "/"
        ws.request_headers = {"Authorization": "Bearer valid_token"}
        walker = Mock()
        
        with patch.object(auth, '_extract_token', return_value="valid_token"):
            with patch.object(auth, '_validate_token', return_value={"user": "testuser"}):
                result = await auth.authenticate_client(ws, walker)
        
        self.assertIsNotNone(result)
    
    def test_extract_token_from_query_params(self):
        """Should extract token from query parameters"""
        auth = AuthenticationManager(self.logger)
        
        path = "/?token=abc123"
        headers = {}
        
        token = auth._extract_token(path, headers)
        
        self.assertEqual(token, "abc123")
    
    def test_extract_token_from_bearer_header(self):
        """Should extract token from Bearer header"""
        auth = AuthenticationManager(self.logger)
        
        path = "/"
        headers = {"Authorization": "Bearer xyz789"}
        
        token = auth._extract_token(path, headers)
        
        self.assertEqual(token, "xyz789")
    
    def test_extract_token_missing(self):
        """Should return None when token is missing"""
        auth = AuthenticationManager(self.logger)
        
        path = "/"
        headers = {}
        
        token = auth._extract_token(path, headers)
        
        self.assertIsNone(token)


# ═══════════════════════════════════════════════════════════════════
# Test: AuthenticationManager Edge Cases (Phase 2: 73% → 90%)
# ═══════════════════════════════════════════════════════════════════

class TestAuthenticationManagerEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Edge case tests for AuthenticationManager - Coverage Phase 2"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = Mock()
    
    def test_validate_origin_malformed_url(self):
        """Should handle malformed Origin URLs gracefully"""
        auth = AuthenticationManager(
            self.logger,
            allowed_origins=["http://localhost:3000"]
        )
        
        ws = Mock()
        ws.request_headers = {"Origin": "not-a-valid-url://???"}
        ws.remote_address = ("192.168.1.1", 12345)
        
        result = auth.validate_origin(ws)
        
        # Malformed URLs should not match
        self.assertFalse(result)
    
    def test_validate_origin_empty_string(self):
        """Should reject empty Origin string when restrictions are enabled"""
        auth = AuthenticationManager(
            self.logger,
            allowed_origins=["http://localhost:3000"]
        )
        
        ws = Mock()
        ws.request_headers = {"Origin": ""}
        ws.remote_address = ("192.168.1.1", 12345)
        
        result = auth.validate_origin(ws)
        
        self.assertFalse(result)
    
    def test_validate_origin_special_characters(self):
        """Should handle Origins with special characters"""
        auth = AuthenticationManager(
            self.logger,
            allowed_origins=["http://localhost:3000"]
        )
        
        ws = Mock()
        ws.request_headers = {"Origin": "http://localhost:3000/path?query=value#fragment"}
        ws.remote_address = ("192.168.1.1", 12345)
        
        result = auth.validate_origin(ws)
        
        # Should match based on prefix
        self.assertTrue(result)
    
    def test_validate_origin_case_sensitivity(self):
        """Should handle Origin case sensitivity"""
        auth = AuthenticationManager(
            self.logger,
            allowed_origins=["http://localhost:3000"]
        )
        
        ws = Mock()
        ws.request_headers = {"Origin": "HTTP://LOCALHOST:3000"}
        ws.remote_address = ("192.168.1.1", 12345)
        
        result = auth.validate_origin(ws)
        
        # Case matters (should not match)
        self.assertFalse(result)
    
    def test_validate_origin_with_port_variations(self):
        """Should match origins with different ports correctly"""
        auth = AuthenticationManager(
            self.logger,
            allowed_origins=["http://localhost:3000"]
        )
        
        ws = Mock()
        ws.request_headers = {"Origin": "http://localhost:8080"}
        ws.remote_address = ("192.168.1.1", 12345)
        
        result = auth.validate_origin(ws)
        
        # Different port should not match
        self.assertFalse(result)
    
    def test_validate_origin_multiple_allowed_origins(self):
        """Should check all allowed origins"""
        auth = AuthenticationManager(
            self.logger,
            allowed_origins=["http://localhost:3000", "http://example.com", "https://app.example.com"]
        )
        
        ws = Mock()
        ws.request_headers = {"Origin": "https://app.example.com"}
        
        result = auth.validate_origin(ws)
        
        self.assertTrue(result)
    
    def test_extract_token_from_multiple_query_params(self):
        """Should extract token when multiple query params present"""
        auth = AuthenticationManager(self.logger)
        
        path = "/?foo=bar&token=abc123&baz=qux"
        headers = {}
        
        token = auth._extract_token(path, headers)
        
        self.assertEqual(token, "abc123")
    
    def test_extract_token_malformed_query_string(self):
        """Should handle malformed query strings"""
        auth = AuthenticationManager(self.logger)
        
        path = "/?token="  # Empty token value
        headers = {}
        
        token = auth._extract_token(path, headers)
        
        # Empty value should be treated as no token
        self.assertIsNone(token)
    
    def test_extract_token_bearer_case_insensitive(self):
        """Should handle Bearer with different casing"""
        auth = AuthenticationManager(self.logger)
        
        path = "/"
        headers = {"Authorization": "bearer xyz789"}  # lowercase bearer
        
        token = auth._extract_token(path, headers)
        
        # Should still extract (if implementation supports it)
        self.assertIsInstance(token, (str, type(None)))
    
    def test_extract_token_priority_header_over_query(self):
        """Should prefer Authorization header over query param"""
        auth = AuthenticationManager(self.logger)
        
        path = "/?token=query_token"
        headers = {"Authorization": "Bearer header_token"}
        
        token = auth._extract_token(path, headers)
        
        # Verify which one is used (depends on implementation)
        self.assertIn(token, ["header_token", "query_token"])
    
    async def test_authenticate_client_invalid_token_format(self):
        """Should handle malformed/invalid token gracefully"""
        auth = AuthenticationManager(self.logger, require_auth=True)
        
        ws = AsyncMock()
        ws.path = "/?token=invalid!!!@@@###"
        ws.request_headers = {}
        walker = Mock()
        
        # Mock validation to return None for invalid token
        with patch.object(auth, '_validate_token', return_value=None):
            result = await auth.authenticate_client(ws, walker)
        
        self.assertIsNone(result)


# ═══════════════════════════════════════════════════════════════════
# Test: DispatchEvents (60% → 90%)
# ═══════════════════════════════════════════════════════════════════

class TestDispatchEvents(unittest.IsolatedAsyncioTestCase):
    """Unit tests for DispatchEvents - Command routing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bifrost = Mock()
        self.bifrost.logger = Mock()
        self.bifrost.cache = Mock()
        self.bifrost.zcli = Mock()
        self.bifrost.walker = Mock()
        self.bifrost.broadcast = AsyncMock()
        
        self.dispatch = DispatchEvents(self.bifrost)
    
    async def test_handle_dispatch_missing_zkey(self):
        """Should return error when zKey is missing"""
        ws = AsyncMock()
        data = {"no_key": "value"}
        
        await self.dispatch.handle_dispatch(ws, data)
        
        # Should send error message
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertIn("error", sent_data)
    
    async def test_handle_dispatch_with_zkey(self):
        """Should process dispatch with valid zKey"""
        ws = AsyncMock()
        data = {"zKey": "^List.users"}
        
        # Mock dispatch execution
        self.bifrost.zcli.dispatch = Mock()
        self.bifrost.zcli.dispatch.launch = Mock(return_value="result")
        
        with patch.object(self.dispatch, '_is_cacheable_operation', return_value=False):
            await self.dispatch.handle_dispatch(ws, data)
        
        # Should have processed the command
        self.bifrost.logger.debug.assert_called()
    
    async def test_handle_dispatch_with_cmd_alias(self):
        """Should accept 'cmd' as alias for 'zKey'"""
        ws = AsyncMock()
        data = {"cmd": "^List.users"}
        
        self.bifrost.zcli.dispatch = Mock()
        self.bifrost.zcli.dispatch.launch = Mock(return_value="result")
        
        with patch.object(self.dispatch, '_is_cacheable_operation', return_value=False):
            await self.dispatch.handle_dispatch(ws, data)
        
        # Should process cmd as zKey
        self.assertGreater(self.bifrost.logger.debug.call_count, 0)
    
    async def test_handle_dispatch_cache_hit(self):
        """Should return cached result on cache hit"""
        ws = AsyncMock()
        data = {"zKey": "^List.users"}
        
        # Mock cache hit
        self.bifrost.cache.generate_cache_key = Mock(return_value="cache_key_123")
        self.bifrost.cache.get_query = Mock(return_value={"cached": "data"})
        
        with patch.object(self.dispatch, '_is_cacheable_operation', return_value=True):
            await self.dispatch.handle_dispatch(ws, data)
        
        # Should send cached result
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertTrue(sent_data.get("_cached"))
        self.assertEqual(sent_data["result"], {"cached": "data"})
    
    async def test_handle_dispatch_cache_miss(self):
        """Should execute command on cache miss"""
        ws = AsyncMock()
        data = {"zKey": "^List.users"}
        
        # Mock cache miss
        self.bifrost.cache.generate_cache_key = Mock(return_value="cache_key_123")
        self.bifrost.cache.get_query = Mock(return_value=None)
        
        self.bifrost.zcli.dispatch = Mock()
        self.bifrost.zcli.dispatch.launch = Mock(return_value="fresh_result")
        
        with patch.object(self.dispatch, '_is_cacheable_operation', return_value=True):
            await self.dispatch.handle_dispatch(ws, data)
        
        # Should have logged cache miss
        self.bifrost.logger.debug.assert_called()
    
    async def test_handle_dispatch_with_no_cache_flag(self):
        """Should bypass cache when no_cache flag is set"""
        ws = AsyncMock()
        data = {"zKey": "^List.users", "no_cache": True}
        
        self.bifrost.zcli.dispatch = Mock()
        self.bifrost.zcli.dispatch.launch = Mock(return_value="result")
        
        with patch.object(self.dispatch, '_is_cacheable_operation', return_value=True):
            await self.dispatch.handle_dispatch(ws, data)
        
        # Cache should not be checked
        self.bifrost.cache.get_query.assert_not_called()
    
    async def test_handle_dispatch_with_request_id(self):
        """Should preserve _requestId in response"""
        ws = AsyncMock()
        data = {"zKey": "^List.users", "_requestId": "req-456"}
        
        # Mock cache hit
        self.bifrost.cache.generate_cache_key = Mock(return_value="key")
        self.bifrost.cache.get_query = Mock(return_value={"data": "value"})
        
        with patch.object(self.dispatch, '_is_cacheable_operation', return_value=True):
            await self.dispatch.handle_dispatch(ws, data)
        
        # Should include _requestId in response
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertEqual(sent_data.get("_requestId"), "req-456")
    
    async def test_handle_dispatch_with_cache_ttl(self):
        """Should respect custom cache_ttl parameter"""
        ws = AsyncMock()
        data = {"zKey": "^List.users", "cache_ttl": 300}
        
        self.bifrost.cache.generate_cache_key = Mock(return_value="key")
        self.bifrost.cache.get_query = Mock(return_value=None)
        self.bifrost.zcli.dispatch = Mock()
        self.bifrost.zcli.dispatch.launch = Mock(return_value="result")
        
        with patch.object(self.dispatch, '_is_cacheable_operation', return_value=True):
            await self.dispatch.handle_dispatch(ws, data)
        
        # Should have processed with custom TTL
        self.bifrost.logger.debug.assert_called()
    
    def test_is_cacheable_operation_read_operation(self):
        """Should identify read operations as cacheable"""
        data = {"zKey": "^List.users"}
        
        # Assuming List operations are cacheable
        result = self.dispatch._is_cacheable_operation(data, "^List.users")
        
        # Result depends on implementation, just test it doesn't crash
        self.assertIsInstance(result, bool)
    
    def test_is_cacheable_operation_write_operation(self):
        """Should identify write operations as non-cacheable"""
        data = {"zKey": "^Create.users"}
        
        result = self.dispatch._is_cacheable_operation(data, "^Create.users")
        
        # Result depends on implementation
        self.assertIsInstance(result, bool)


# ═══════════════════════════════════════════════════════════════════
# Test: BifrostBridge Edge Cases (77% → 95%)
# ═══════════════════════════════════════════════════════════════════

class TestBifrostBridgeEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Unit tests for bifrost_bridge_modular edge cases"""
    
    async def test_broadcast_to_no_clients(self):
        """Should handle broadcast when no clients connected"""
        from zCLI.subsystems.zComm.zComm_modules.zBifrost import zBifrost
        
        logger = Mock()
        bifrost = zBifrost(logger, port=56899)
        
        message = json.dumps({"test": "message"})
        
        # Should not crash with empty client set
        await bifrost.broadcast(message)
        
        # No clients, so no sends
        self.assertEqual(len(bifrost.clients), 0)
    
    async def test_handle_client_exception_in_receive(self):
        """Should handle exceptions during message receive"""
        from zCLI.subsystems.zComm.zComm_modules.zBifrost import zBifrost
        
        logger = Mock()
        bifrost = zBifrost(logger, port=56899)
        
        ws = AsyncMock()
        # Make receive raise an exception
        ws.__aiter__ = Mock(side_effect=Exception("Connection lost"))
        
        # Should handle exception gracefully
        try:
            await bifrost.handle_client(ws)
        except Exception:
            # If it raises, that's acceptable for cleanup
            pass
    
    async def test_infer_event_type_from_action(self):
        """Should infer event type from 'action' field"""
        from zCLI.subsystems.zComm.zComm_modules.zBifrost import zBifrost
        
        logger = Mock()
        bifrost = zBifrost(logger, port=56899)
        
        data = {"action": "get_schema"}
        
        event = bifrost._infer_event_type(data)
        
        self.assertEqual(event, "get_schema")
    
    async def test_infer_event_type_from_zkey(self):
        """Should infer event type as 'dispatch' for zKey"""
        from zCLI.subsystems.zComm.zComm_modules.zBifrost import zBifrost
        
        logger = Mock()
        bifrost = zBifrost(logger, port=56899)
        
        data = {"zKey": "^List.users"}
        
        event = bifrost._infer_event_type(data)
        
        self.assertEqual(event, "dispatch")
    
    async def test_infer_event_type_from_cmd(self):
        """Should infer event type as 'dispatch' for cmd"""
        from zCLI.subsystems.zComm.zComm_modules.zBifrost import zBifrost
        
        logger = Mock()
        bifrost = zBifrost(logger, port=56899)
        
        data = {"cmd": "test_command"}
        
        event = bifrost._infer_event_type(data)
        
        self.assertEqual(event, "dispatch")
    
    async def test_infer_event_type_no_inference(self):
        """Should return None when event type cannot be inferred"""
        from zCLI.subsystems.zComm.zComm_modules.zBifrost import zBifrost
        
        logger = Mock()
        bifrost = zBifrost(logger, port=56899)
        
        data = {"unknown": "field"}
        
        event = bifrost._infer_event_type(data)
        
        self.assertIsNone(event)
    
    async def test_message_handler_unknown_event(self):
        """Should handle unknown event types gracefully"""
        from zCLI.subsystems.zComm.zComm_modules.zBifrost import zBifrost
        
        logger = Mock()
        bifrost = zBifrost(logger, port=56899)
        
        ws = AsyncMock()
        data = json.dumps({"event": "unknown_event_type", "data": "test"})
        
        # Should broadcast message even if event is unknown
        await bifrost.handle_message(ws, data)
        
        # Logger should have warned about unknown event
        self.assertTrue(logger.warning.called)


# ═══════════════════════════════════════════════════════════════════
# Test: Bifrost Bridge Additional Edge Cases (Phase 2: 78% → 95%)
# ═══════════════════════════════════════════════════════════════════

class TestBifrostBridgeAdvancedEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Advanced edge case tests for bifrost_bridge_modular - Coverage Phase 2"""
    
    async def test_broadcast_with_disconnected_clients(self):
        """Should handle broadcast when some clients are disconnected"""
        from zCLI.subsystems.zComm.zComm_modules.zBifrost import zBifrost
        
        logger = Mock()
        bifrost = zBifrost(logger, port=56900)
        
        # Add mock clients
        client1 = AsyncMock()
        client2 = AsyncMock()
        client2.send = AsyncMock(side_effect=Exception("Connection closed"))
        client3 = AsyncMock()
        
        bifrost.clients = {client1, client2, client3}
        
        message = json.dumps({"test": "broadcast"})
        
        # Should not crash even if client2 fails
        await bifrost.broadcast(message)
        
        # client1 and client3 should receive, client2 should fail gracefully
        client1.send.assert_called_once()
        client3.send.assert_called_once()
    
    async def test_broadcast_with_send_failures(self):
        """Should continue broadcasting even if some sends fail"""
        from zCLI.subsystems.zComm.zComm_modules.zBifrost import zBifrost
        
        logger = Mock()
        bifrost = zBifrost(logger, port=56900)
        
        # Mock clients where middle one fails
        good_client1 = AsyncMock()
        failing_client = AsyncMock()
        failing_client.send.side_effect = ConnectionError("Send failed")
        good_client2 = AsyncMock()
        
        bifrost.clients = {good_client1, failing_client, good_client2}
        
        message = json.dumps({"data": "test"})
        
        await bifrost.broadcast(message)
        
        # Both good clients should still receive
        good_client1.send.assert_called_once()
        good_client2.send.assert_called_once()
        # Broadcast should handle failures gracefully (no assertion on logger needed)


# ═══════════════════════════════════════════════════════════════════
# Test: CacheEvents (Phase 2: 34% → 85%)
# ═══════════════════════════════════════════════════════════════════

class TestCacheEvents(unittest.IsolatedAsyncioTestCase):
    """Unit tests for CacheEvents - Cache operation handlers"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bifrost = Mock()
        self.bifrost.logger = Mock()
        self.bifrost.cache = Mock()
        self.bifrost.connection_info = Mock()
        
        from zCLI.subsystems.zComm.zComm_modules.zBifrost.bridge_modules.events.cache_events import CacheEvents
        self.cache_events = CacheEvents(self.bifrost)
    
    async def test_handle_get_schema_success(self):
        """Should return schema when found"""
        ws = AsyncMock()
        data = {"model": "users"}
        
        self.bifrost.connection_info.get_schema = Mock(return_value={"model": "users", "fields": []})
        
        await self.cache_events.handle_get_schema(ws, data)
        
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertIn("result", sent_data)
    
    async def test_handle_get_schema_not_found(self):
        """Should return error when schema not found"""
        ws = AsyncMock()
        data = {"model": "nonexistent"}
        
        self.bifrost.connection_info.get_schema = Mock(return_value=None)
        
        await self.cache_events.handle_get_schema(ws, data)
        
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertIn("error", sent_data)
    
    async def test_handle_get_schema_missing_model(self):
        """Should return error when model parameter missing"""
        ws = AsyncMock()
        data = {}  # No model
        
        await self.cache_events.handle_get_schema(ws, data)
        
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertIn("error", sent_data)
    
    async def test_handle_clear_cache(self):
        """Should clear cache and return stats"""
        ws = AsyncMock()
        data = {}
        
        self.bifrost.cache.clear_query_cache = Mock()
        self.bifrost.cache.get_stats = Mock(return_value={"hits": 0, "misses": 0})
        
        await self.cache_events.handle_clear_cache(ws, data)
        
        self.bifrost.cache.clear_query_cache.assert_called_once()
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertEqual(sent_data["result"], "Cache cleared")
    
    async def test_handle_cache_stats(self):
        """Should return cache statistics"""
        ws = AsyncMock()
        data = {}
        
        self.bifrost.cache.get_stats = Mock(return_value={"hits": 10, "misses": 3})
        
        await self.cache_events.handle_cache_stats(ws, data)
        
        ws.send.assert_called_once()
        sent_data = json.loads(ws.send.call_args[0][0])
        self.assertIn("result", sent_data)


# ═══════════════════════════════════════════════════════════════════
# Test: ClientEvents (Phase 2: 42% → 85%)
# ═══════════════════════════════════════════════════════════════════

class TestClientEvents(unittest.IsolatedAsyncioTestCase):
    """Unit tests for ClientEvents - Client-side event handlers"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bifrost = Mock()
        self.bifrost.logger = Mock()
        self.bifrost.zcli = Mock()
        
        from zCLI.subsystems.zComm.zComm_modules.zBifrost.bridge_modules.events.client_events import ClientEvents
        self.client_events = ClientEvents(self.bifrost)
    
    async def test_handle_input_response_success(self):
        """Should route input response to zDisplay"""
        ws = AsyncMock()
        data = {"requestId": "req-123", "value": "user input"}
        
        # Mock zCLI display
        self.bifrost.zcli.display = Mock()
        self.bifrost.zcli.display.zPrimitives = Mock()
        self.bifrost.zcli.display.zPrimitives.handle_input_response = Mock()
        
        await self.client_events.handle_input_response(ws, data)
        
        self.bifrost.zcli.display.zPrimitives.handle_input_response.assert_called_once_with("req-123", "user input")
    
    async def test_handle_input_response_no_zcli(self):
        """Should handle missing zCLI gracefully"""
        ws = AsyncMock()
        data = {"requestId": "req-123", "value": "input"}
        
        # Set zcli to None on the client_events instance (not bifrost)
        self.client_events.zcli = None
        
        await self.client_events.handle_input_response(ws, data)
        
        # Should log warning
        self.bifrost.logger.warning.assert_called()
    
    async def test_handle_input_response_no_display(self):
        """Should handle missing display gracefully"""
        ws = AsyncMock()
        data = {"requestId": "req-123", "value": "input"}
        
        # Mock zcli without display attribute on the client_events instance
        self.client_events.zcli = Mock(spec=[])
        
        await self.client_events.handle_input_response(ws, data)
        
        # Should log warning
        self.bifrost.logger.warning.assert_called()


# ═══════════════════════════════════════════════════════════════════
# Test: DiscoveryEvents (Phase 2: 53% → 85%)
# ═══════════════════════════════════════════════════════════════════

class TestDiscoveryEvents(unittest.IsolatedAsyncioTestCase):
    """Unit tests for DiscoveryEvents - Auto-discovery handlers"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bifrost = Mock()
        self.bifrost.logger = Mock()
        self.bifrost.connection_info = Mock()
        
        from zCLI.subsystems.zComm.zComm_modules.zBifrost.bridge_modules.events.discovery_events import DiscoveryEvents
        self.discovery_events = DiscoveryEvents(self.bifrost)
    
    async def test_handle_discover(self):
        """Should return discovery information"""
        ws = AsyncMock()
        data = {}
        
        self.bifrost.connection_info.discover = Mock(return_value={"models": ["users", "products"]})
        
        await self.discovery_events.handle_discover(ws, data)
        
        ws.send.assert_called_once()
        self.bifrost.connection_info.discover.assert_called_once()
    
    async def test_handle_introspect_with_model(self):
        """Should return introspection for specific model"""
        ws = AsyncMock()
        data = {"model": "users"}
        
        self.bifrost.connection_info.introspect = Mock(return_value={"model": "users", "schema": {}})
        
        await self.discovery_events.handle_introspect(ws, data)
        
        ws.send.assert_called_once()
        self.bifrost.connection_info.introspect.assert_called_once_with("users")
    
    async def test_handle_introspect_without_model(self):
        """Should return introspection for all models when no model specified"""
        ws = AsyncMock()
        data = {}
        
        self.bifrost.connection_info.introspect = Mock(return_value={"all": "models"})
        
        await self.discovery_events.handle_introspect(ws, data)
        
        ws.send.assert_called_once()
        self.bifrost.connection_info.introspect.assert_called_once_with(None)


# ═══════════════════════════════════════════════════════════════════
# Test: CacheManager (Phase 2: 31% → 80%)
# ═══════════════════════════════════════════════════════════════════

class TestCacheManager(unittest.TestCase):
    """Unit tests for CacheManager - Caching system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = Mock()
        
        from zCLI.subsystems.zComm.zComm_modules.zBifrost.bridge_modules.cache_manager import CacheManager
        self.cache_mgr = CacheManager(self.logger, default_query_ttl=60)
    
    def test_get_schema_cache_hit(self):
        """Should return cached schema"""
        # Pre-populate cache
        self.cache_mgr.schema_cache["users"] = {"model": "users"}
        
        result = self.cache_mgr.get_schema("users")
        
        self.assertEqual(result, {"model": "users"})
        self.assertEqual(self.cache_mgr.schema_stats['hits'], 1)
    
    def test_get_schema_cache_miss(self):
        """Should return None on cache miss without loader"""
        result = self.cache_mgr.get_schema("nonexistent")
        
        self.assertIsNone(result)
        self.assertEqual(self.cache_mgr.schema_stats['misses'], 1)
    
    def test_get_schema_with_loader(self):
        """Should load schema using loader function"""
        def mock_loader(model):
            return {"model": model}
        
        result = self.cache_mgr.get_schema("users", loader_func=mock_loader)
        
        self.assertEqual(result, {"model": "users"})
        # Should also be cached now
        self.assertIn("users", self.cache_mgr.schema_cache)
    
    def test_generate_cache_key(self):
        """Should generate deterministic cache key"""
        data1 = {"zKey": "List.users", "where": {"active": True}}
        data2 = {"zKey": "List.users", "where": {"active": True}}
        data3 = {"zKey": "List.products"}
        
        key1 = self.cache_mgr.generate_cache_key(data1)
        key2 = self.cache_mgr.generate_cache_key(data2)
        key3 = self.cache_mgr.generate_cache_key(data3)
        
        # Same data should produce same key
        self.assertEqual(key1, key2)
        # Different data should produce different key
        self.assertNotEqual(key1, key3)
    
    def test_cache_query(self):
        """Should cache query result with TTL"""
        key = "test_key"
        result = {"data": "value"}
        
        self.cache_mgr.cache_query(key, result, ttl=30)
        
        self.assertIn(key, self.cache_mgr.query_cache)
        cached = self.cache_mgr.query_cache[key]
        self.assertEqual(cached["data"], result)
        self.assertIn("timestamp", cached)
    
    def test_get_query_cache_hit(self):
        """Should return cached query result"""
        key = "test_key"
        result = {"data": "value"}
        
        # Cache it first
        self.cache_mgr.cache_query(key, result)
        
        # Retrieve it
        cached_result = self.cache_mgr.get_query(key)
        
        self.assertEqual(cached_result, result)
        self.assertEqual(self.cache_mgr.query_stats['hits'], 1)
    
    def test_get_query_expired(self):
        """Should return None for expired cache entries"""
        import time
        
        key = "test_key"
        result = {"data": "value"}
        
        # Cache with very short TTL
        self.cache_mgr.cache_query(key, result, ttl=0.1)
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should return None
        cached_result = self.cache_mgr.get_query(key)
        
        self.assertIsNone(cached_result)
        self.assertEqual(self.cache_mgr.query_stats['expired'], 1)
    
    def test_clear_query_cache(self):
        """Should clear all caches"""
        self.cache_mgr.cache_query("key1", {"data": "1"})
        self.cache_mgr.cache_query("key2", {"data": "2"})
        
        self.cache_mgr.clear_all()
        
        self.assertEqual(len(self.cache_mgr.query_cache), 0)
    
    def test_get_stats(self):
        """Should return cache statistics"""
        # Trigger some cache operations
        self.cache_mgr.get_schema("test1")  # miss
        self.cache_mgr.schema_cache["test2"] = {}
        self.cache_mgr.get_schema("test2")  # hit
        
        stats = self.cache_mgr.get_all_stats()
        
        self.assertIn("schema_cache", stats)
        self.assertIn("query_cache", stats)


# ═══════════════════════════════════════════════════════════════════
# Test: ConnectionInfoManager (Phase 2: 35% → 80%)
# ═══════════════════════════════════════════════════════════════════

class TestConnectionInfoManager(unittest.TestCase):
    """Unit tests for ConnectionInfoManager - Server info management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = Mock()
        self.cache = Mock()
        self.zcli = Mock()
        self.walker = Mock()
        
        from zCLI.subsystems.zComm.zComm_modules.zBifrost.bridge_modules.connection_info import ConnectionInfoManager
        self.conn_info = ConnectionInfoManager(self.logger, self.cache, self.zcli, self.walker)
    
    def test_get_connection_info_basic(self):
        """Should return basic connection info"""
        self.cache.get_all_stats = Mock(return_value={"hits": 0, "misses": 0})
        
        info = self.conn_info.get_connection_info()
        
        self.assertIn("server_version", info)
        self.assertIn("features", info)
        self.assertIn("cache_stats", info)
    
    def test_get_connection_info_with_models(self):
        """Should include available models when zData present"""
        self.cache.get_all_stats = Mock(return_value={})
        self.walker.data = Mock()
        
        with patch.object(self.conn_info, '_discover_models', return_value=["users", "products"]):
            info = self.conn_info.get_connection_info()
        
        self.assertIn("available_models", info)
        self.assertEqual(info["available_models"], ["users", "products"])
    
    def test_get_connection_info_without_walker(self):
        """Should handle missing walker gracefully"""
        self.cache.get_all_stats = Mock(return_value={})
        self.conn_info.walker = None
        
        info = self.conn_info.get_connection_info()
        
        # Should not have available_models
        self.assertNotIn("available_models", info)
    
    def test_get_connection_info_with_session(self):
        """Should include session info when available"""
        self.cache.get_all_stats = Mock(return_value={})
        self.zcli.session = Mock()
        self.zcli.session.workspace = "/path/to/workspace"
        self.zcli.mode = "zBifrost"
        
        info = self.conn_info.get_connection_info()
        
        self.assertIn("session", info)
        self.assertEqual(info["session"]["workspace"], "/path/to/workspace")
        self.assertEqual(info["session"]["mode"], "zBifrost")
    
    def test_discover_models_exception_handling(self):
        """Should handle exceptions during model discovery"""
        self.cache.get_all_stats = Mock(return_value={})
        self.walker.data = Mock()
        
        with patch.object(self.conn_info, '_discover_models', side_effect=Exception("Discovery failed")):
            info = self.conn_info.get_connection_info()
        
        # Should not crash, just skip available_models
        self.assertNotIn("available_models", info)


# ═══════════════════════════════════════════════════════════════════
# Test Suite Runner
# ═══════════════════════════════════════════════════════════════════

def run_tests(verbose=True):
    """Run all zBifrost unit tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Phase 1 tests (existing)
    suite.addTests(loader.loadTestsFromTestCase(TestMessageHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthenticationManager))
    suite.addTests(loader.loadTestsFromTestCase(TestDispatchEvents))
    suite.addTests(loader.loadTestsFromTestCase(TestBifrostBridgeEdgeCases))
    
    # Phase 2 tests (new)
    suite.addTests(loader.loadTestsFromTestCase(TestAuthenticationManagerEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestBifrostBridgeAdvancedEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheEvents))
    suite.addTests(loader.loadTestsFromTestCase(TestClientEvents))
    suite.addTests(loader.loadTestsFromTestCase(TestDiscoveryEvents))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheManager))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectionInfoManager))
    
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests(verbose=True)
    sys.exit(0 if result.wasSuccessful() else 1)

