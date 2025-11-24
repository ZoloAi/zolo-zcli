## Level 0: Hello zComm

The simplest possible introduction to zComm—zCLI's communication layer.

### What You'll Learn

- zComm auto-initializes when you create a `zCLI()` instance
- Check if a port is available with `z.comm.check_port()`
- Zero configuration required
- Uses PROD logger for clean output

### Demo

**`hello_comm.py`**
- Initialize zCLI
- Check port 8080 availability
- Print result

**Run:**
```bash
python Demos/Layer_0/zComm_Demo/Level_0_Hello/hello_comm.py
```

**Expected Output:**
```
=== Level 0: Hello zComm ===
Port 8080 : available

Tip: zComm auto-initializes with zCLI - zero setup!
```

### Key Takeaway

Just like zConfig, zComm is ready to use the moment you create a zCLI instance. No imports, no setup, no configuration files.

