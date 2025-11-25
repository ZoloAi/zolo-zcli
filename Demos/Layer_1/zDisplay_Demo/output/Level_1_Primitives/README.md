# Level 1: zDisplay Primitives (Raw Output)

**<span style="color:#8FBE6D">Fastest possible path from "nothing" to on-screen text.</span>**

These micro-step tutorials mirror the style of **zConfig** and **zComm**: each file teaches **one tiny concept** you can copy/paste into your own code.

## Files
- **`write_raw.py`** — Raw output with **no newline**. Perfect for inline status like `Loading...`.
- **`write_line.py`** — Adds the newline for you. Great for log-style output.
- **`write_block.py`** — Sends **multiple lines at once** while preserving your formatting.

## How to Run
```bash
cd Demos/Layer_1/zDisplay_Demo/output/Level_1_Primitives
python write_raw.py
python write_line.py
python write_block.py
```

## Micro-Steps

> <span style="color:#8FBE6D">**Step 1: write_raw()**</span>
- Create `z = zCLI({"logger": "PROD"})`
- Call `z.display.write_raw("Downloading...")`
- **What you see:** Text streams on the same line—no newline added.

> <span style="color:#8FBE6D">**Step 2: write_line()**</span>
- Reuse the same zCLI instance
- Call `z.display.write_line("Each call is a new line")`
- **What you see:** Every call ends cleanly with a newline—no manual `\n` required.

> <span style="color:#8FBE6D">**Step 3: write_block()**</span>
- Build a multi-line string
- Call `z.display.write_block(block_text)`
- **What you see:** Your block prints exactly as written, with a trailing newline handled for you.

## Why Start Here?
- These primitives are the **foundation** for all higher-level zDisplay events (signals, tables, progress).
- They work in **Terminal** and **zBifrost** (browser) modes automatically—no extra setup.
- Keeping logger set to **`PROD`** keeps the output focused on the demo itself.

## Next Steps
- Move to **Level 1: Basic Outputs & Signals** in `../Level_1_Outputs_Signals` once you’re comfortable with the primitives.
- Use these primitives alongside headers, signals, and tables to build richer output flows.

---
**Time:** ~5 minutes total (1 minute per micro-step)  
**Difficulty:** Beginner  
**Version:** 1.5.5
