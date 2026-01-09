# Level 3: Getting Started

[← Back to zBifrost Guide](../../../../Documentation/zBifrost_GUIDE.md) | [Next: Level 4 →](../Level_4_Templates/README.md)

## Flask Blog Tutorial Part 1: Getting Started

This level mirrors [Corey Schafer's Flask Blog Part 1](https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog/01-Getting-Started).

**Note**: Flask Part 1 has NO WebSocket - just HTTP! We'll add WebSocket (zBifrost) in later levels when we need real-time features.

### Flask Code (flaskblog.py):

```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return "<h1>Home Page</h1>"

@app.route("/about")
def about():
    return "<h1>About Page</h1>"

if __name__ == '__main__':
    app.run(debug=True)
```

**Flask**: ~17 lines of Python

### zKernel Equivalent:

**Backend** (`level3_backend.py`): ~10 lines of Python
**Routes** (`zServer.routes.yaml`): ~12 lines of YAML (declarative, with inline content!)

**Total**: ~22 lines (all declarative YAML, no separate HTML files!)

---

## What You'll Learn

- <span style="color:#F8961F">Run HTTP server</span> (zServer) - just like Flask dev server
- <span style="color:#F8961F">Define routes declaratively</span> using YAML (no decorators!)
- <span style="color:#F8961F">Serve inline HTML content</span> directly from routes (like Flask return strings!)

---

## Files

```
Level_3_Getting_Started/
├── level3_backend.py          # Python backend (HTTP + WebSocket)
├── zServer.routes.yaml         # Declarative routes with inline content
└── README.md                   # This file
```

---

## How to Run

```bash
cd Demos/Layer_0/zBifrost_Demo/Level_3_Getting_Started
python3 level3_backend.py
```

Then visit:
- http://127.0.0.1:8000/ → Home Page
- http://127.0.0.1:8000/home → Home Page
- http://127.0.0.1:8000/about → About Page

---

## Under the Hood

### Flask Approach:
```python
@app.route("/")
@app.route("/home")
def home():
    return "<h1>Home Page</h1>"
```

- **Imperative**: Decorators define routes in Python code
- **Coupled**: Routes and logic mixed together
- **Runtime**: Routes registered at import time

### zKernel Approach:
```yaml
routes:
  /:
    type: content
    content: "<h1>Home Page</h1>"
  /home:
    type: content
    content: "<h1>Home Page</h1>"
```

- **Declarative**: Routes defined in YAML (data, not code!)
- **Inline Content**: HTML strings directly in routes (like Flask!)
- **Flexible**: Easy to modify without touching Python code

---

## Success Criteria

- ✅ zServer (HTTP) starts without errors
- ✅ Visiting http://127.0.0.1:8000/ shows "Home Page"
- ✅ Visiting http://127.0.0.1:8000/home shows "Home Page"
- ✅ Visiting http://127.0.0.1:8000/about shows "About Page"
- ✅ No 404 errors in browser console

---

## Troubleshooting

**Port already in use?**
- Stop any other servers running on port 8000
- Or change port in `level3_backend.py`

**Routes not working?**
- Check that `zServer.routes.yaml` is in the same directory
- Check YAML syntax (indentation matters!)

**404 errors?**
- Make sure you're visiting the exact routes: `/`, `/home`, `/about`
- Check that `type: content` is set in routes

---

## Key Differences: Flask vs. zKernel

| Feature | Flask | zKernel |
|---------|-------|------|
| **Routes** | Python decorators | YAML file |
| **Server** | HTTP only | HTTP only (WebSocket comes later!) |
| **Content** | Return strings | Inline content in YAML |
| **Lines of Code** | ~17 | ~10 Python + ~12 YAML |
| **Flexibility** | Change routes = restart | Change YAML = hot reload (future) |

---

## What's Next?

**Level 4** will add Jinja2 templates for dynamic HTML rendering (Flask Part 2: Templates).

[← Back to zBifrost Guide](../../../../Documentation/zBifrost_GUIDE.md) | [Next: Level 4 →](../Level_4_Templates/README.md)

