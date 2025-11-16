# Level 4: Templates - Jinja2 Base Layout + Bootstrap

[← Back to zBifrost Guide](../../../../Documentation/zBifrost_GUIDE.md) | [Next: Level 5 →](../Level_5_Forms/README.md)

## <span style="color:#8FBE6D">Goal</span>

Use **Jinja2 templates** with **Bootstrap CSS** for server-side rendering, matching [Corey Schafer's Flask Blog Tutorial Part 2](https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog/02-Templates).

## What You'll Learn

- **<span style="color:#F8961F">Jinja2 template inheritance</span>**: Create a base `layout.html` and extend it in `home.html` and `about.html`
- **<span style="color:#8FBE6D">Bootstrap 4 integration</span>**: Use Bootstrap's navbar, container, and responsive grid
- **<span style="color:#00D4FF">Template context variables</span>**: Pass data from YAML routes to templates (e.g., `title`)
- **<span style="color:#EA7171">Declarative routing</span>**: Define routes with `type: template` in YAML

## Files

- **`level4_backend.py`**: Python backend that runs zServer (HTTP) with Jinja2 template rendering
- **`zServer.routes.yaml`**: Declarative routes configuration (`type: template`)
- **`templates/layout.html`**: Base Jinja2 template with Bootstrap navbar
- **`templates/home.html`**: Home page (extends `layout.html`)
- **`templates/about.html`**: About page (extends `layout.html`)

## How to Run

```bash
cd /Users/galnachshon/Projects/zolo-zcli/Demos/Layer_0/zBifrost_Demo/Level_4_Templates
python3 level4_backend.py
```

Then open your browser to:
```
http://127.0.0.1:8000/
```

## Success Checklist

- Bootstrap navbar appears at the top (dark background)
- "zBlog" brand link in navbar
- "Home" and "About" navigation links
- Home page displays welcome content
- About page displays about content
- Responsive layout (try resizing browser)

## Under the Hood

### 1. **zServer Template Rendering**

The backend uses zServer's new `type: template` route type:

```yaml
routes:
  /:
    type: template
    template: "home.html"
    context:
      title: "Home"
```

This tells zServer to:
1. Load `templates/home.html` using Jinja2
2. Pass `context` variables to the template
3. Render the template and return HTML

### 2. **Jinja2 Template Inheritance**

**`layout.html`** (base template):
```html
<!DOCTYPE html>
<html>
<head>
    <title>zBlog - {{ title }}</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <!-- navbar content -->
    </nav>
    
    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

**`home.html`** (extends base):
```html
{% extends "layout.html" %}
{% block content %}
    <h2>Home Page</h2>
    <p>Welcome to zBlog!</p>
{% endblock content %}
```

### 3. **Bootstrap Integration**

Level 4 uses **pure Bootstrap 4.0.0** (no custom CSS):
- `navbar navbar-expand-lg navbar-dark bg-dark` - Dark navbar
- `container` - Responsive centered container
- `mt-4` - Margin-top utility class

This matches Corey Schafer's Flask tutorial exactly!

## Flask vs. zCLI Comparison

### Flask (Part 2)

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

if __name__ == '__main__':
    app.run(debug=True)
```

**Lines of code**: ~15 lines Python + ~50 lines HTML templates = **~65 lines**

### zCLI (Level 4)

```yaml
# zServer.routes.yaml
routes:
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

```python
# level4_backend.py (simplified)
from zCLI import zCLI

z = zCLI({"zWorkspace": current_dir, "zMode": "Terminal"})
z.server = z.comm.create_http_server(port=8000, routes_file="zServer.routes.yaml")
z.server.start()
```

**Lines of code**: ~10 lines Python + ~12 lines YAML + ~40 lines HTML templates = **~62 lines**

**Code Reduction**: ~5% (minimal at this stage, but declarative routing is cleaner!)

## Troubleshooting

**Port already in use:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Templates not found:**
- Ensure `templates/` directory exists in the same folder as `level4_backend.py`
- Check that `zServer.routes.yaml` uses correct template names

**Bootstrap not loading:**
- Check internet connection (Bootstrap is loaded from CDN)
- Open browser console (F12) to see any errors

## What's Next?

**Level 5** will add **forms** with validation, matching Flask Part 3 (Flask-WTF). We'll use Bootstrap forms and eventually transition to zCLI's declarative `z.display.form()` for auto-generated forms!

---

**Key Takeaway**: Level 4 proves that zCLI's `zServer` can handle Jinja2 templates just like Flask, but with **declarative YAML routing** instead of Python decorators. The real magic starts in Level 5+ when we introduce zCLI's auto-rendering!

