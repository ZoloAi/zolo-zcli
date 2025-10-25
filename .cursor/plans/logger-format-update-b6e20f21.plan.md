<!-- b6e20f21-7362-4591-99a0-68dfad87b4d2 e3b10df6-c74d-4a13-80c8-1a4972af79c5 -->
# Logger Format Update Plan

## Overview

Enhance the logger to provide cleaner console output (no timestamps) and more detailed file logs (with timestamps and line numbers), plus hierarchical naming for better module identification.

## Changes Required

### 1. Update `_get_caller_info()` method in `config_logger.py`

**File:** `zCLI/subsystems/zConfig/zConfig_modules/config_logger.py` (lines 73-98)

**Current behavior:** Only shows subsystem name (e.g., "zComm") for all files in that subsystem

**New behavior:** Show hierarchical names (e.g., "zComm.service_manager") for better granularity

**Changes:**

- For subsystem files: Extract both subsystem and module filename
- If filename matches subsystem (e.g., `zComm.py`), return just subsystem name
- Otherwise return `subsystem.module` format
- Keep existing logic for core files and other files

### 2. Update `_setup_logging()` method in `config_logger.py`

**File:** `zCLI/subsystems/zConfig/zConfig_modules/config_logger.py` (lines 100-178)

**Current behavior:** Single formatter used for both console and file handlers

**New behavior:** Separate formatters for console (clean) and file (detailed)

**Changes:**

#### Console Formatters (no timestamp):

- **detailed:** `'%(name)s - %(levelname)s - %(message)s'`
- **simple:** `'%(levelname)s: %(message)s'` (unchanged)
- **json:** `'{"level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'`

#### File Formatters (with timestamp + line numbers):

- **detailed:** `'%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'`
- **simple:** `'%(asctime)s - %(levelname)s: %(message)s'`
- **json:** `'{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","file":"%(filename)s","line":%(lineno)d,"message":"%(message)s"}'`

**Implementation:**

- Create two separate formatter variables: `console_formatter` and `file_formatter`
- Apply `console_formatter` to console handler (line 158)
- Apply `file_formatter` to file handler (line 173)

### 3. Update redundant logger setup in `zConfig.py`

**File:** `zCLI/subsystems/zConfig/zConfig.py` (lines 47-53)

**Current issue:** Getting the same logger instance and copying handlers to itself (redundant)

**Changes:**

- Simplify to just assign the existing logger: `zcli.logger = session_logger._logger`
- Remove the handler copying loop (lines 51-53)
- Keep the info log message (line 56)

## Expected Outcomes

### Console Output (clean, no timestamp):

```
zComm - INFO - Communication subsystem ready
zComm.service_manager - INFO - ServiceManager initialized
zData.sqlite_adapter - ERROR - Connection failed
```

### File Output (detailed with timestamps):

```
2025-10-25 18:14:29 - zComm - INFO - [zComm.py:45] - Communication subsystem ready
2025-10-25 18:14:29 - zComm.service_manager - INFO - [service_manager.py:142] - ServiceManager initialized
2025-10-25 18:14:30 - zData.sqlite_adapter - ERROR - [sqlite_adapter.py:234] - Connection failed
```

## Testing

- Run all tests to ensure no regressions
- Verify console output has no timestamps
- Verify file logs include timestamps and line numbers
- Test hierarchical naming with subsystem modules