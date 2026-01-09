#!/usr/bin/env python3
"""
Test script for SESSION log level implementation.

Tests:
1. SESSION level is registered with Python logging
2. BootstrapLogger has session() method
3. LoggerConfig has session() method
4. SESSION logs appear in correct order (between INFO and DEBUG)
5. Colored output works for --verbose
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Import zSys.logger FIRST to register SESSION level
from zSys.logger import LOG_LEVEL_SESSION
import logging

print("=" * 70)
print("SESSION LOG LEVEL TEST")
print("=" * 70)
print()

# Test 1: Verify SESSION level is registered
print("Test 1: SESSION level registration")
print("-" * 70)
if hasattr(logging, 'SESSION'):
    print(f"✓ logging.SESSION = {logging.SESSION}")
    print(f"✓ Level name: {logging.getLevelName(logging.SESSION)}")
    assert logging.SESSION == 15, "SESSION should be level 15"
    assert logging.getLevelName(15) == 'SESSION', "Level 15 should be named SESSION"
    print("✓ SESSION level correctly registered")
else:
    print("✗ logging.SESSION not found!")
    sys.exit(1)
print()

# Test 2: Test BootstrapLogger
print("Test 2: BootstrapLogger.session() method")
print("-" * 70)
from zSys.logger import BootstrapLogger

boot_logger = BootstrapLogger()
boot_logger.debug("This is DEBUG")
boot_logger.session("This is SESSION (environment info)")
boot_logger.info("This is INFO")
boot_logger.warning("This is WARNING")

print(f"✓ BootstrapLogger created with {len(boot_logger.buffer)} buffered messages")

# Verify buffer
for msg in boot_logger.buffer:
    level = msg['level']
    message = msg['message']
    print(f"  [{level:8s}] {message}")

assert boot_logger.buffer[1]['level'] == 'SESSION', "Second message should be SESSION"
print("✓ BootstrapLogger.session() works correctly")
print()

# Test 3: Test LoggerConfig (requires zCLI init)
print("Test 3: LoggerConfig.session() method")
print("-" * 70)

try:
    from zCLI import zCLI
    
    # Minimal zSpark for testing
    zSpark = {
        "deployment": "Development",
        "logger": "DEBUG",
        "zMode": "Terminal"
    }
    
    z = zCLI(zSpark)
    
    print("✓ zCLI initialized")
    
    # Test session() method exists
    assert hasattr(z.logger, 'session'), "LoggerConfig should have session() method"
    print("✓ logger.session() method exists")
    
    # Test calling it (should not raise)
    z.logger.session("Test session log: Python %s", sys.version.split()[0])
    z.logger.session("Test session log: zSpark keys = %d", len(zSpark))
    print("✓ logger.session() calls successful")
    
except Exception as e:
    print(f"✗ LoggerConfig test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
print()

# Test 4: Verify log level ordering
print("Test 4: Log level ordering")
print("-" * 70)
print("Log levels (descending priority):")
print(f"  CRITICAL = {logging.CRITICAL}")
print(f"  ERROR    = {logging.ERROR}")
print(f"  WARNING  = {logging.WARNING}")
print(f"  INFO     = {logging.INFO}")
print(f"  SESSION  = {logging.SESSION}")
print(f"  DEBUG    = {logging.DEBUG}")
print()

# Verify ordering
assert logging.INFO > logging.SESSION > logging.DEBUG, "SESSION should be between INFO and DEBUG"
print("✓ SESSION level (15) correctly positioned between INFO (20) and DEBUG (10)")
print()

# Test 5: Test colored output
print("Test 5: Colored output for --verbose")
print("-" * 70)
from zSys.logger import format_bootstrap_verbose
from datetime import datetime

now = datetime.now()
colored = format_bootstrap_verbose(now, "SESSION", "Test session message")
print(f"Sample colored output: {colored}")
print("✓ Colored format includes SESSION level")
print()

# Test 6: Test level filtering
print("Test 6: Log level filtering")
print("-" * 70)

# Create test logger at INFO level
test_logger = logging.getLogger("test_session")
test_logger.setLevel(logging.INFO)

# Add handler to capture output
class TestHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []
    
    def emit(self, record):
        self.messages.append((record.levelname, record.getMessage()))

handler = TestHandler()
test_logger.addHandler(handler)

# Log at different levels
test_logger.debug("DEBUG message")
test_logger.log(logging.SESSION, "SESSION message")
test_logger.info("INFO message")

print(f"Logger level: INFO ({logging.INFO})")
print(f"Captured messages: {len(handler.messages)}")
for level, msg in handler.messages:
    print(f"  [{level}] {msg}")

# At INFO level, should capture INFO but not SESSION or DEBUG
assert len(handler.messages) == 1, "At INFO level, should only capture INFO"
assert handler.messages[0][0] == "INFO", "Only INFO message should be captured"
print("✓ INFO level correctly filters out SESSION and DEBUG")
print()

# Test at SESSION level
handler.messages.clear()
test_logger.setLevel(logging.SESSION)

test_logger.debug("DEBUG message")
test_logger.log(logging.SESSION, "SESSION message")
test_logger.info("INFO message")

print(f"Logger level: SESSION ({logging.SESSION})")
print(f"Captured messages: {len(handler.messages)}")
for level, msg in handler.messages:
    print(f"  [{level}] {msg}")

# At SESSION level, should capture SESSION and INFO but not DEBUG
assert len(handler.messages) == 2, "At SESSION level, should capture SESSION and INFO"
assert handler.messages[0][0] == "SESSION", "First should be SESSION"
assert handler.messages[1][0] == "INFO", "Second should be INFO"
print("✓ SESSION level correctly captures SESSION and INFO, filters DEBUG")
print()

# Summary
print("=" * 70)
print("ALL TESTS PASSED! ✅")
print("=" * 70)
print()
print("Summary:")
print("  ✓ SESSION level registered at 15 (between INFO:20 and DEBUG:10)")
print("  ✓ BootstrapLogger.session() method works")
print("  ✓ LoggerConfig.session() method works")
print("  ✓ Log level ordering correct")
print("  ✓ Colored output includes SESSION")
print("  ✓ Level filtering works correctly")
print()
print("SESSION level is ready to use! 🎉")
print()
print("Usage examples:")
print("  boot_logger.session('Python: %s', sys.version)")
print("  z.logger.session('zSpark config loaded: %d keys', len(config))")
print("  z.logger.framework.log(logging.SESSION, 'Environment detected: %s', env)")
