# Flask-like Folder Conventions in zServer (v1.5.5)

## ✅ Implementation Complete

zServer now supports **Flask-like folder conventions** for static files and templates!

---

## 📁 Folder Structure

```
your_app/
├── static/              # ← Auto-served at /static/*
│   ├── css/
│   ├── js/
│   │   └── hello.js
│   ├── images/
│   └── fonts/
│
├── templates/           # ← Jinja2 templates (NOT web-accessible)
│   ├── layout.html
│   ├── home.html
│   └── about.html
│
├── zServer.routes.yaml  # ← Declarative routes
└── level4a_backend.py   # ← Backend script
```

---

## 🚀 Usage

### **1. Default Behavior (Flask conventions)**

```python
z.server = z.comm.create_http_server(
    port=8000,
    serve_path=".",
    routes_file="zServer.routes.yaml"
)
# ✅ static/ folder auto-served at /static/*
# ✅ templates/ folder used for Jinja2 rendering
```

### **2. Custom Folders (override defaults)**

```python
z.server = z.comm.create_http_server(
    port=8000,
    serve_path=".",
    static_folder="assets",      # Custom static folder
    template_folder="views",     # Custom templates folder
    routes_file="zServer.routes.yaml"
)
# ✅ assets/ folder auto-served at /static/*
# ✅ views/ folder used for Jinja2 rendering
```

---

## 📝 Routes File (No Static Routes Needed!)

```yaml
# zServer.routes.yaml

Meta:
  base_path: "."
  default_route: "/"

routes:
  # ✅ No need to define /static/* routes!
  # They're auto-served from static/ folder
  
  /:
    type: template
    template: "home.html"
    context:
      title: "Home"
  
  /about:
    type: template
    template: "about.html"
    context:
      title: "About"
```

---

## 🌐 HTML Usage

```html
<!DOCTYPE html>
<html>
<head>
    <!-- Auto-served from static/ folder -->
    <link rel="stylesheet" href="/static/css/styles.css">
    <script src="/static/js/hello.js"></script>
</head>
<body>
    <img src="/static/images/logo.png" alt="Logo">
</body>
</html>
```

---

## 🔒 Security Features

1. **Directory Traversal Protection**: Prevents `../` attacks
2. **Directory Listing Disabled**: Returns 403 for directories
3. **MIME Type Detection**: Correct `Content-Type` headers
4. **Caching Headers**: 1 hour cache for static files

---

## 🎯 Test Results

**Test File**: `static/js/hello.js`

**Console Output**:
```
🎉 Hello from /static/js/hello.js!
✅ Flask-like static folder convention is working!
📁 File location: static/js/hello.js
🌐 URL: /static/js/hello.js
```

**Status**: ✅ **WORKING PERFECTLY**

---

## 📊 Comparison: Flask vs zKernel

| Feature | Flask | zKernel zServer |
|---------|-------|--------------|
| Static folder | `static/` | ✅ `static/` (default) |
| Static URL | `/static/*` | ✅ `/static/*` (auto) |
| Templates folder | `templates/` | ✅ `templates/` (default) |
| Custom folders | `static_folder=` | ✅ `static_folder=` |
| Auto-serving | ✅ Yes | ✅ Yes |
| MIME types | ✅ Yes | ✅ Yes |
| Security | ✅ Yes | ✅ Yes |

---

## 🎓 Key Differences from Flask

### **Flask** (Imperative):
```python
from flask import Flask, render_template

app = Flask(__name__)  # static_folder='static' by default

@app.route("/")
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
```

### **zKernel** (Declarative):
```python
# Backend: level4a_backend.py
z.server = z.comm.create_http_server(
    port=8000,
    serve_path=".",
    routes_file="zServer.routes.yaml"  # Declarative routing!
)
z.server.start()
```

```yaml
# Routes: zServer.routes.yaml
routes:
  /:
    type: template
    template: "home.html"
```

**Advantage**: No decorators, no code changes for routing! 🚀

---

## 🏆 What's Next?

- ✅ Static folder convention (DONE)
- ✅ Templates folder convention (DONE)
- 🔜 Level 4b: zDisplay Events (Multi-Zone Rendering)
- 🔜 Level 5: Forms and User Input
- 🔜 Level 6: Database Integration

---

**Version**: zKernel v1.5.5  
**Status**: Production Ready ✅  
**Test Date**: 2025-11-16

