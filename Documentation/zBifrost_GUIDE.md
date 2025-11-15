[← Back to zComm](zComm_GUIDE.md) | [Next: zDisplay Guide →](zDisplay_GUIDE.md)

# zBifrost Guide

> **<span style="color:#F8961F">Real-time bidirectional communication</span>** between Python backends and JavaScript frontends via WebSocket bridge.

**<span style="color:#8FBE6D">Every modern app needs real-time communication.</span>** WebSocket servers, message routing, event handling—the real struggle is keeping your Python backend's JSON in sync with your JavaScript frontecdnd, let alone setting it up. **One schema change breaks everything.**

**<span style="color:#8FBE6D">zBifrost</span>** is zCLI's **<span style="color:#F8961F">Layer 0 WebSocket bridge</span>**, providing a **production-ready server** (Python) and **standalone JavaScript client**. Don't need the full framework? Import zCLI, use just the server. Or use the JavaScript client standalone with any WebSocket backend.

Get **<span style="color:#F8961F">event-driven architecture</span>**, **<span style="color:#F8961F">CRUD operations via WebSocket</span>**, **<span style="color:#F8961F">auto-rendering with zTheme</span>**, and **<span style="color:#F8961F">hooks for customization</span>** in one unified bridge. **No websockets library, no message juggling, no boilerplate.**

## Architecture

zBifrost uses an **<span style="color:#8FBE6D">event-driven architecture</span>** that mirrors zDisplay's clean design pattern. Messages flow through a single entry point, routed via an event map to domain-specific handlers.

<div style="display:flex; flex-direction:column; gap:1rem; max-width:700px;">

  <div style="border-left:4px solid #8FBE6D; padding:1rem; background:rgba(143,190,109,0.08);">
    <strong style="color:#8FBE6D;">Server (Python)</strong><br>
    Event-driven WebSocket server with authentication, caching, and command dispatch<br>
    <code style="color:#999;">zCLI/subsystems/zComm/zComm_modules/bifrost/</code>
  </div>

  <div style="border-left:4px solid #F8961F; padding:1rem; background:rgba(248,150,31,0.08);">
    <strong style="color:#F8961F;">Client (JavaScript)</strong><br>
    Standalone library with lazy loading, auto-rendering, and zTheme integration<br>
    <code style="color:#999;">bifrost_client_modular.js (CDN-ready)</code>
  </div>

  <div style="border-left:4px solid #00D4FF; padding:1rem; background:rgba(0,212,255,0.08);">
    <strong style="color:#00D4FF;">Event Protocol</strong><br>
    Standardized message format with backward compatibility for legacy formats<br>
    <code style="color:#999;">{event: "dispatch", data: {...}}</code>
  </div>

</div>

## Progressive Tutorial Demos

> **<span style="color:#8FBE6D">Learn zBifrost step-by-step.</span>**<br>Each level builds on the previous, adding complexity gradually. All demos live in [`Demos/Layer_0/zBifrost_Demo`](../Demos/Layer_0/zBifrost_Demo).

**End Goal:** Build **<span style="color:#F8961F">zBlog</span>**—a complete blog platform with real-time updates and multi-user support. Each level adds exactly one feature, starting from "Hello World" and ending with a production-ready blog.

**Demo Roadmap:**

> **End Goal**: Build a complete WordPress-style blog ("zBlog") following the exact workflow of [Corey Schafer's Flask Blog Tutorial](https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog), but using zCLI instead of Flask—resulting in 90% less code!

**Phase 1: Foundation (Imperative Usage)** — Levels 0-2
- **Level 0**: Hello zBlog - Connect to server, see welcome message, disconnect
- **Level 1**: Echo Test - Type message, send it, get echo back (proves two-way communication)
- **Level 2**: Post Feed - Show 5 hardcoded posts as cards (manual DOM, imperative JavaScript)

**Phase 2: Declarative zCLI (Following Flask Blog Tutorial Structure)** — Levels 3-16

- **Level 3**: Getting Started - HTTP + WebSocket Together
  - **zCLI**: Add zServer (HTTP) + zBifrost (WebSocket) in same Python script
  - **NEW**: Run both HTTP (port 8000) and WebSocket (port 8765) together

- **Level 4**: Templates - Jinja2 Base Layout + Bootstrap
  - **zCLI**: Jinja2 layout with Bootstrap navbar and container
  - **NEW**: Server-side rendering for page structure (header, nav, footer) + Bootstrap styling

- **Level 4a**: zUI Basics - Multi-Zone Layout
  - **zCLI**: Add `<div id="zui-content">` and `<div id="zui-sidebar">` to Jinja2 layout
  - **NEW**: Prepare HTML for zDisplay event routing (zone-based rendering)

- **Level 4b**: First zDisplay Event - Hello from Backend
  - **zCLI**: Send `z.display.text()` event via zBifrost to render in `zui-content` zone
  - **NEW**: Backend → Frontend communication (Python sends, JavaScript renders)

- **Level 4c**: zUI File Execution - Menu Navigation
  - **zCLI**: Load and execute a simple zUI YAML file with menu options
  - **NEW**: zWalker integration (execute zUI files in zBifrost mode)

- **Level 5**: Forms and User Input - Registration Form
  - **Flask Part 3**: Flask-WTF forms, validation, flash messages
  - **zCLI**: `z.display.form()` with zSchema validation (auto-rendered + validated)
  - **NEW**: Form schema → HTML form (no manual HTML!)

- **Level 6**: Database - SQLAlchemy Models
  - **Flask Part 4**: Define User and Post models with SQLAlchemy
  - **zCLI**: Write zSchema YAML (declarative schema for User, Post)
  - **NEW**: YAML schema → SQLite tables (no Python ORM code!)

- **Level 7**: User Authentication - Login/Logout
  - **Flask Part 5**: Flask-Login, bcrypt, login_required decorator
  - **zCLI**: `z.auth.login()` + RBAC rules in YAML (auth.yaml)
  - **NEW**: `z.display.login_form()` + session token management

- **Level 8**: User Account - Profile Page
  - **Flask Part 6**: User profile, update account info, profile picture upload
  - **zCLI**: `z.display.form(schema="update_profile")` + file upload via zBifrost
  - **NEW**: File upload over WebSocket + `z.data.update("users")`

- **Level 9**: Create Posts - New Post Form
  - **Flask Part 7**: Create post route, form, save to database
  - **zCLI**: `z.display.form(schema="create_post")` + `z.data.insert("posts")`
  - **NEW**: Form submission → database (declarative, no routes!)

- **Level 10**: Update and Delete Posts - CRUD Operations
  - **Flask Part 8**: Edit/delete routes, authorization checks
  - **zCLI**: `z.display.table(posts, actions=["edit", "delete"])` + RBAC
  - **NEW**: `z.display.table()` with action buttons + `z.display.confirm()`

- **Level 11**: Pagination - Post List Pagination
  - **Flask Part 9**: SQLAlchemy pagination, page parameter
  - **zCLI**: `z.data.select("posts", limit=10, offset=page*10)` + `z.display.pagination()`
  - **NEW**: `z.display.pagination()` auto-renders pagination controls

- **Level 12**: Email and Password Reset
  - **Flask Part 10**: Flask-Mail, password reset tokens, email templates
  - **zCLI**: `z.comm.send_email()` + `z.auth.reset_password_token()`
  - **NEW**: Email via zComm + token-based password reset

- **Level 13**: Blueprints - Application Structure
  - **Flask Part 11**: Organize app into blueprints (users, posts, main)
  - **zCLI**: Organize zCLI commands into modules (users.py, posts.py, main.py)
  - **NEW**: Modular zCLI structure (same as Flask blueprints)

- **Level 14**: Custom Error Pages - 404, 403, 500
  - **Flask Part 12**: Custom error handlers, error templates
  - **zCLI**: `z.display.error(404, message="Page not found")` + custom error zones
  - **NEW**: Error events routed to specific divs

- **Level 15**: Comments System - Nested Data
  - **Flask Extension**: Add Comment model, foreign keys, nested rendering
  - **zCLI**: zSchema foreign keys + `z.data.select(join="comments")` + nested rendering
  - **NEW**: BifrostClient nested rendering (posts with comments array)

- **Level 16**: Real-Time Updates - WebSocket Broadcasts
  - **Flask Extension**: Would require Flask-SocketIO (complex setup)
  - **zCLI**: `z.comm.websocket.broadcast()` (already built-in!)
  - **NEW**: Multi-user real-time updates (new posts appear instantly for all users)

**Optional Advanced Levels:**
- **Level 17**: Deployment - Production Setup (Gunicorn, Nginx, SSL)
- **Level 18**: Terminal Mode - Same zDisplay events work in Terminal (dual-mode!)

---

### Backend Enhancement Notes (Not Part of Demos)

**These backend features may need implementation/enhancement before building certain levels:**

**For Level 3:**
- ✅ zServer HTTP server - Already exists
- ✅ Inline content routes (`type: content`) - Implemented
- ✅ Declarative routing via YAML - Already exists

**For Level 4:**
- ✅ Jinja2 integration in zServer - Implemented (`type: template`)
- ✅ Template directory structure - Implemented
- ✅ Pass context to Jinja2 templates - Implemented
- ✅ Bootstrap CSS integration - Complete

**For Level 5:**
- ✅ zData schema loading - Already exists
- ✅ `z.data.create_table()` - Already exists
- ✅ zSchema YAML parsing - Already exists

**For Level 6:**
- ✅ `z.data.select()` with WHERE/ORDER BY/LIMIT - Already exists
- ✅ SQLite adapter - Already exists
- ✅ `z.display.json_data()` - Already exists
- ✅ BifrostClient `onDisplay` hook - Already exists
- ⏳ **NEEDED**: Auto-rendering logic in BifrostClient for structured data (posts array)
- ⏳ **NEEDED**: `target` parameter in zDisplay events (route to specific div)

**For Level 7:**
- ⏳ **NEEDED**: `z.display.form()` - Send form schema as zDisplay event
- ⏳ **NEEDED**: BifrostClient auto-form rendering (from schema → HTML form)
- ✅ zData validator (5-layer validation) - Already exists

**For Level 8:**
- ⏳ **NEEDED**: `z.display.table()` - Send table data + actions as zDisplay event
- ⏳ **NEEDED**: BifrostClient auto-table rendering (with action buttons)
- ⏳ **NEEDED**: `z.display.confirm()` - Confirmation dialog event
- ✅ `z.data.update()` / `z.data.delete()` - Already exists

**For Level 9:**
- ✅ Foreign keys in zSchema - Already exists
- ✅ `z.data.select()` with JOIN - Already exists
- ⏳ **NEEDED**: BifrostClient nested rendering (posts with comments array)

**For Level 10:**
- ✅ zAuth subsystem - Already exists
- ✅ `z.auth.login()` / `z.auth.check_permission()` - Already exists
- ⏳ **NEEDED**: `z.display.login_form()` - Auto-rendered login UI
- ⏳ **NEEDED**: Session token management in BifrostClient
- ⏳ **NEEDED**: Zone-level RBAC (hide/show divs based on role)

**Priority Implementation Order:**
1. **Level 3**: Run HTTP + WebSocket servers together, static file serving
2. **Level 4**: Jinja2 integration in zServer (template rendering)
3. **Level 6**: BifrostClient auto-rendering for arrays + `target` parameter
4. **Level 7**: `z.display.form()` + auto-form rendering
5. **Level 8**: `z.display.table()` + auto-table rendering + `z.display.confirm()`
6. **Level 10**: `z.display.login_form()` + session token management + zone RBAC

---

**Current Status:**
- ✅ **Phase 1 (Levels 0-2)**: Complete - Imperative foundation established
- ✅ **Level 3**: Complete - HTTP server (inline content routes)
- ✅ **Level 4**: Complete - Jinja2 templates + Bootstrap styling
- ⏳ **Phase 2 (Levels 5-16)**: Ready to build (following [Corey Schafer's Flask Blog Tutorial](https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog))
- 📦 **Old demos**: Level_1_Menu and Level_2_Widgets archived (not aligned with Flask tutorial structure)

**Key Insight:** Phase 1 teaches raw WebSocket mechanics (imperative). Phase 2 reveals zBifrost's declarative magic, following the **exact same workflow** as the famous Flask blog tutorial—but with **91% less code**!

**Why This Structure?**

1. **Phase 1 (Imperative)**: You need to understand WebSocket fundamentals before appreciating the abstractions. Manual DOM manipulation shows what zCLI automates for you. By the end, you'll have a complete imperative toolkit for building ANY web app.

2. **Phase 2 (Declarative)**: Levels 3-16 follow the **exact structure of [Corey Schafer's Flask Blog Tutorial](https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog)**, part-by-part:
   - **Level 3**: Part 1 - Getting Started (Flask app → zServer + zBifrost)
   - **Level 4**: Part 2 - Templates (Jinja2 layout)
   - **Level 5**: Part 3 - Forms (Flask-WTF → `z.display.form()`)
   - **Level 6**: Part 4 - Database (SQLAlchemy → zSchema YAML)
   - **Level 7**: Part 5 - User Auth (Flask-Login → zAuth YAML)
   - **Level 8**: Part 6 - User Account (profile, upload)
   - **Level 9**: Part 7 - Create Posts (form, save)
   - **Level 10**: Part 8 - Update/Delete (CRUD routes → `z.display.table()`)
   - **Level 11**: Part 9 - Pagination (SQLAlchemy pagination → `z.display.pagination()`)
   - **Level 12**: Part 10 - Email/Reset (Flask-Mail → `z.comm.send_email()`)
   - **Level 13**: Part 11 - Blueprints (modular structure)
   - **Level 14**: Part 12 - Error Pages (custom handlers → `z.display.error()`)
   - **Level 15**: Extension - Comments (foreign keys, JOIN)
   - **Level 16**: Extension - Real-Time (Flask-SocketIO → built-in WebSocket!)
   - **Result**: Same blog, **91% less code**, plus real-time updates!

---

### Flask → zCLI Workflow Mapping

**How we'd build a blog in Flask** (imperative, 16 parts) **vs. zCLI** (declarative, same 16 levels):

| Level | Flask Blog Tutorial | zCLI Workflow | Code Reduction |
|-------|---------------------|---------------|----------------|
| **0-2** | N/A (Flask assumes HTTP) | WebSocket fundamentals (imperative) | N/A (teaching phase) |
| **3** | Part 1: Getting Started (Flask app, routes) | zServer (HTTP) + zBifrost (WebSocket) together | ~50 lines → 10 lines |
| **4** | Part 2: Templates (Jinja2 layout.html + Bootstrap) | Jinja2 layout with Bootstrap navbar | ~100 lines → 40 lines |
| **4a** | N/A (Flask doesn't have zones) | Add multi-zone divs to layout | ~5 lines HTML |
| **4b** | N/A (Flask doesn't have zDisplay) | Send `z.display.text()` via zBifrost | ~3 lines Python |
| **4c** | N/A (Flask doesn't have zUI) | Execute zUI YAML file with zWalker | ~10 lines YAML |
| **5** | Part 3: Forms (Flask-WTF, validation) | `z.display.form()` + zSchema validation | ~150 lines → 20 lines |
| **6** | Part 4: Database (SQLAlchemy models) | zSchema YAML (declarative schema) | ~80 lines Python → 15 lines YAML |
| **7** | Part 5: User Auth (Flask-Login, bcrypt) | `z.auth.login()` + RBAC YAML | ~200 lines → 10 lines Python + 10 lines YAML |
| **8** | Part 6: User Account (profile, upload) | `z.display.form()` + file upload | ~120 lines → 15 lines |
| **9** | Part 7: Create Posts (form, save) | `z.display.form()` + `z.data.insert()` | ~100 lines → 10 lines |
| **10** | Part 8: Update/Delete (CRUD routes) | `z.display.table()` with actions | ~150 lines → 5 lines |
| **11** | Part 9: Pagination (SQLAlchemy pagination) | `z.display.pagination()` | ~80 lines → 5 lines |
| **12** | Part 10: Email/Reset (Flask-Mail, tokens) | `z.comm.send_email()` + `z.auth.reset_password_token()` | ~150 lines → 10 lines |
| **13** | Part 11: Blueprints (app structure) | Modular zCLI commands | ~200 lines refactor → 0 lines (same structure) |
| **14** | Part 12: Error Pages (custom handlers) | `z.display.error()` events | ~60 lines → 5 lines |
| **15** | Extension: Comments (foreign keys, JOIN) | zSchema foreign keys + nested rendering | ~100 lines → 10 lines YAML + 5 lines Python |
| **16** | Extension: Real-Time (Flask-SocketIO setup) | `z.comm.websocket.broadcast()` (built-in!) | ~300 lines → 1 line |
| **Total** | **~1,840 lines of Python + HTML** | **~155 lines of Python + YAML** | **~91% reduction!** |

**Key Differences:**

**Flask (Imperative):**
- Write routes for every action (`@app.route('/post/create', methods=['POST'])`)
- Write HTML templates for every view (`post_list.html`, `post_edit.html`)
- Write SQL queries or ORM code for every operation
- Manually handle form validation, CSRF tokens, error messages
- Manually implement authentication logic (sessions, cookies, decorators)

**zCLI (Declarative):**
- **One HTML file** with `<div id="zContainer"></div>` (BifrostClient auto-renders everything)
- **One Python backend** with zDisplay events (`z.display.json_data()`, `z.display.form()`, `z.display.table()`)
- **One zSchema YAML** for database models (auto-creates tables, validates data)
- **One zAuth YAML** for RBAC rules (auto-enforces permissions)
- **Zero routes, zero templates, zero SQL** — just describe what you want!

**Code Reduction:**
- **Flask**: ~500-1000 lines (routes, templates, forms, queries, auth logic)
- **zCLI**: ~50-100 lines (schema YAML + Python backend with zDisplay events)
- **Result**: **90% less code, same functionality!**

---

### Level 0: Hello zBlog

**<span style="color:#8FBE6D">Goal</span>**: Connect to server, see welcome message, disconnect. That's it!

**Location**: [`Level_0_Connection/`](../Demos/Layer_0/zBifrost_Demo/Level_0_Connection) | [README](../Demos/Layer_0/zBifrost_Demo/Level_0_Connection/README.md)

**What you'll learn:**
- **<span style="color:#F8961F">Start a WebSocket server</span>** in Python (10 lines!)
- **<span style="color:#8FBE6D">Connect from browser</span>** (just click a button)
- **<span style="color:#00D4FF">See messages flow</span>** between server and browser

**Run:**
```bash
cd Demos/Layer_0/zBifrost_Demo/Level_0_Connection
python3 level0_backend.py
# Open level0_client.html in browser, click "Connect"
```

**Success**: You see "🎉 Hello from zBlog!" in your browser

---

### Level 1: Echo Test

**<span style="color:#8FBE6D">Goal</span>**: Type message, send it, get echo back (proves two-way communication).

**Location**: [`Level_1_Echo/`](../Demos/Layer_0/zBifrost_Demo/Level_1_Echo) | [README](../Demos/Layer_0/zBifrost_Demo/Level_1_Echo/README.md)

**What you'll learn:**
- **<span style="color:#F8961F">Production BifrostClient</span>** (lazy loading architecture)
- **<span style="color:#8FBE6D">Custom event handlers</span>** (register `echo` event)
- **<span style="color:#00D4FF">Two-way communication</span>** (client → server → client)

**Run:**
```bash
cd Demos/Layer_0/zBifrost_Demo/Level_1_Echo
python3 level1_backend.py
# Open level1_client.html in browser, type a message, click "Send"
```

**Success**: Your message is echoed back with timestamp

---

### Level 2: Post Feed

**<span style="color:#8FBE6D">Goal</span>**: Show 5 hardcoded posts as cards (like a real blog homepage).

**Location**: [`Level_2_Post_Feed/`](../Demos/Layer_0/zBifrost_Demo/Level_2_Post_Feed) | [README](../Demos/Layer_0/zBifrost_Demo/Level_2_Post_Feed/README.md)

**What you'll learn:**
- **<span style="color:#F8961F">Arrays of structured data</span>** (posts with title, author, excerpt, tags)
- **<span style="color:#8FBE6D">Dynamic element creation</span>** (manual `createPostCard()` function)
- **<span style="color:#00D4FF">CSS Grid layout</span>** (responsive post cards)

**Run:**
```bash
cd Demos/Layer_0/zBifrost_Demo/Level_2_Post_Feed
python3 level2_backend.py
# Open level2_client.html in browser, click "Load Feed"
```

**Success**: 5 blog posts appear as styled cards

---

### Level 3: HTTP + WebSocket Together

**<span style="color:#8FBE6D">Goal</span>**: Run both HTTP server (zServer) and WebSocket server (zBifrost) in the same Python script.

**Location**: [`Level_3_HTTP_WebSocket/`](../Demos/Layer_0/zBifrost_Demo/Level_3_HTTP_WebSocket) | [README](../Demos/Layer_0/zBifrost_Demo/Level_3_HTTP_WebSocket/README.md)

**What you'll learn:**
- **<span style="color:#F8961F">zServer (HTTP server)</span>** - Serve static files via HTTP
- **<span style="color:#8FBE6D">Dual-server architecture</span>** - HTTP (port 8000) + WebSocket (port 8765)
- **<span style="color:#00D4FF">Production environment</span>** - Move from `file://` to `http://` URLs

**Run:**
```bash
cd Demos/Layer_0/zBifrost_Demo/Level_3_HTTP_WebSocket
python3 level3_backend.py
# Open http://127.0.0.1:8000/level3_client.html in browser (NOT file://)
```

**Success**: Same blog feed as Level 2, but served via HTTP!

**Why this matters**: Enables CORS, cookies, sessions (needed for auth), and Jinja2 templates (Level 4)

---

### Level 4: Templates - Jinja2 Base Layout + Bootstrap

**<span style="color:#8FBE6D">Goal</span>**: Use Jinja2 templates with Bootstrap CSS for server-side rendering (matching Corey Schafer's Flask Part 2).

**Location**: [`Level_4_Templates/`](../Demos/Layer_0/zBifrost_Demo/Level_4_Templates) | [README](../Demos/Layer_0/zBifrost_Demo/Level_4_Templates/README.md)

**What you'll learn:**
- **<span style="color:#F8961F">Jinja2 template inheritance</span>** (`layout.html` → `home.html`, `about.html`)
- **<span style="color:#8FBE6D">Bootstrap 4 integration</span>** (navbar, container, responsive grid)
- **<span style="color:#00D4FF">Template context variables</span>** (pass data from YAML routes to templates)

**Run:**
```bash
cd Demos/Layer_0/zBifrost_Demo/Level_4_Templates
python3 level4_backend.py
# Open http://127.0.0.1:8000/ in browser
```

**Success**: Bootstrap-styled blog with navbar, home page, and about page

**Key Files:**
- `zServer.routes.yaml` - Declarative routes with `type: template`
- `templates/layout.html` - Base template with Bootstrap navbar
- `templates/home.html` - Extends layout, shows home content
- `templates/about.html` - Extends layout, shows about content

**Flask Comparison:**
```python
# Flask Part 2 (Corey Schafer)
from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

app.run(debug=True)
```

```yaml
# zCLI (Declarative YAML)
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

**Code Reduction**: ~100 lines Flask → ~40 lines zCLI (60% reduction)

---

### Level 5: Custom Hooks & Real-Time (Coming Soon)
**Goal**: Handle broadcasts and custom events without zTheme.

**What you'll build:**
- Multi-user chat or collaborative app
- Custom rendering (React/Vue/vanilla JS)
- Real-time notifications when other users make changes

**Concepts**: `onBroadcast` hook, `onDisplay` custom rendering, `autoTheme: false`

**Backend features**: Broadcast to all clients, connection tracking

---

### Level 6: zUI Dual-Mode Navigation (Coming Soon)
**Goal**: Execute the same zUI YAML file in both Terminal and Web GUI modes with navigation.

**What you'll build:**
- zUI file that defines menus, forms, tables
- Python script that runs in Terminal mode
- Web page that executes same zUI via zBifrost
- Navigation via `zLink`, `zDelta`

**Concepts**: `zMode: "zBifrost"`, zWalker integration, zDisplay event routing, zUI execution

**Backend features**: zWalker, zUI loader, zDisplay subsystem, dispatch events

**⚠️ Missing Feature**: `execute_ui` command to trigger zWalker from client (needs implementation)

---

### Level 7: Authentication & RBAC (Coming Soon)
**Goal**: Secure WebSocket connections with user authentication.

**What you'll build:**
- Login flow via WebSocket
- Role-based access control (admin vs user)
- Protected routes and operations

**Concepts**: Three-tier auth (zSession, app, dual), token-based auth, RBAC

**Backend features**: zAuth subsystem, origin validation, session management

---

### Level 8: Service Orchestration (Coming Soon)
**Goal**: Start/stop local services (PostgreSQL, Redis) via WebSocket.

**What you'll build:**
- Admin dashboard to manage services
- Service status monitoring
- Connection info display

**Concepts**: `client.zFunc()` for service commands, service lifecycle

**Backend features**: zComm service orchestration, PostgreSQL service, health checks

---

### Current Status
- ✅ **Levels 0-2**: Complete with working demos
- 🚧 **Levels 3-5**: Backend ready, demos need creation
- ⏳ **Level 6**: Requires `execute_ui` command implementation
- 🚧 **Levels 7-8**: Backend exists, demos need creation


## Server-Side (Python)

zBifrost server auto-starts when `zMode: "zBifrost"` is set, or can be created programmatically via zComm.

### Auto-Start (Recommended)

```python
from zCLI import zCLI

# Set zMode to zBifrost - server auto-starts
z = zCLI({
    "zMode": "zBifrost",
    "websocket": {
        "port": 8765,
        "host": "127.0.0.1",
        "require_auth": False
    }
})

# Server is running on ws://127.0.0.1:8765
z.walker.run()  # Your YAML now renders in browser via WebSocket
```

### Programmatic Control

```python
import asyncio
from zCLI import zCLI

z = zCLI()

# Create WebSocket server
websocket = z.comm.create_websocket(port=8765, host="127.0.0.1")

# Start server (requires asyncio.Event for readiness signaling)
socket_ready = asyncio.Event()
await z.comm.start_websocket(socket_ready)
await socket_ready.wait()  # Wait for server to be ready

# Broadcast to all connected clients
await z.comm.broadcast_websocket({
    "event": "data_updated",
    "model": "users",
    "action": "create"
})
```

### Event Handlers

Server routes messages via event map to domain-specific handlers:

- **<span style="color:#8FBE6D">client_events</span>**: Input responses, connection info
- **<span style="color:#F8961F">cache_events</span>**: Schema retrieval, cache operations
- **<span style="color:#00D4FF">discovery_events</span>**: Auto-discovery, introspection
- **<span style="color:#EA7171">dispatch_events</span>**: zDispatch command execution

### Authentication

Three-tier authentication system (configured via zConfig):

- **<span style="color:#8FBE6D">zSession</span>**: Platform-level authentication
- **<span style="color:#F8961F">Application</span>**: App-specific authentication
- **<span style="color:#00D4FF">Dual</span>**: Both zSession and application

```python
# Configure via zConfig
z.config.persistence.persist_environment("websocket.require_auth", True)
z.config.persistence.persist_environment("websocket.allowed_origins", "http://localhost:8080,https://example.com")
```

## Client-Side (JavaScript)

The BifrostClient is a **<span style="color:#8FBE6D">standalone JavaScript library</span>** that works with any WebSocket server. It uses **<span style="color:#F8961F">lazy loading</span>** for CDN compatibility and provides **<span style="color:#00D4FF">auto-rendering</span>** with optional zTheme integration.

### Installation

**Option 1: CDN (Recommended)**

```html
<script src="https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@v1.5.5/zCLI/subsystems/zComm/zComm_modules/bifrost/bifrost_client_modular.js"></script>
```

**Option 2: ES6 Module**

```html
<script type="module">
  import { BifrostClient } from './bifrost_client_modular.js';
</script>
```

**Option 3: Local Copy**

Copy `bifrost_client_modular.js` and `_modules/` directory to your project.

### Basic Usage

```javascript
// Initialize client
const client = new BifrostClient('ws://localhost:8765', {
    autoTheme: true,  // Auto-load zTheme CSS
    autoReconnect: true,
    hooks: {
        onConnected: (info) => console.log('Connected!', info),
        onDisconnected: (reason) => console.log('Disconnected:', reason),
        onMessage: (msg) => console.log('Message:', msg),
        onError: (error) => console.error('Error:', error)
    }
});

// Connect
await client.connect();

// Use immediately
const users = await client.read('users');
client.renderTable(users, '#container');
```

### Configuration Options

```javascript
new BifrostClient(url, {
    // Theme
    autoTheme: true,           // Auto-load zTheme CSS (default: true)
    
    // Connection
    autoReconnect: true,         // Auto-reconnect on disconnect (default: true)
    reconnectDelay: 3000,       // Delay between reconnects in ms (default: 3000)
    timeout: 30000,              // Request timeout in ms (default: 30000)
    
    // Authentication
    token: 'your-api-key',       // Authentication token (optional)
    
    // Debugging
    debug: false,                // Enable console logging (default: false)
    
    // Hooks (see Hooks System section)
    hooks: {
        onConnected: (info) => {},
        onDisconnected: (reason) => {},
        onMessage: (msg) => {},
        onError: (error) => {},
        onBroadcast: (msg) => {},
        onDisplay: (data) => {},
        onInput: (request) => {}
    }
});
```

## CRUD Operations

BifrostClient provides high-level CRUD methods that communicate with zCLI's zData subsystem via WebSocket.

```javascript
// Create
await client.create('users', {
    name: 'John Doe',
    email: 'john@example.com',
    age: 30
});

// Read
const users = await client.read('users');
const filtered = await client.read('users', {
    where: 'age > 18',
    orderBy: 'name',
    limit: 10
});

// Update
await client.update('users', 
    { email: 'john@example.com' },  // filters
    { age: 31 }                      // data
);

// Delete
await client.delete('users', {
    email: 'john@example.com'
});
```

## Auto-Rendering

BifrostClient can automatically render data using zTheme CSS (if `autoTheme: true`). Render methods work with any container selector.

```javascript
// Render table
client.renderTable(users, '#users-container');

// Render form
client.renderForm(
    [
        { name: 'email', type: 'email', required: true },
        { name: 'password', type: 'password', required: true }
    ],
    '#form-container',
    async (data) => {
        await client.create('users', data);
    }
);

// Render menu
client.renderMenu([
    { label: 'Users', action: () => loadUsers() },
    { label: 'Settings', action: () => loadSettings() }
], '#menu-container');

// Render message
client.renderMessage('User created successfully!', 'success', '#message-container');
```

### Custom Rendering (No zTheme)

Disable auto-theme and use your own rendering logic:

```javascript
const client = new BifrostClient('ws://localhost:8765', {
    autoTheme: false,  // Don't load zTheme CSS
    hooks: {
        onDisplay: (data) => {
            // Use React, Vue, or vanilla JS
            if (Array.isArray(data)) {
                ReactDOM.render(<MyTable data={data} />, container);
            }
        }
    }
});
```

## Hooks System

Hooks allow you to customize BifrostClient behavior at key lifecycle points.

**Available Hooks:**

- **<span style="color:#8FBE6D">onConnected</span>**: Fires when WebSocket connection is established
- **<span style="color:#F8961F">onDisconnected</span>**: Fires when connection is lost
- **<span style="color:#00D4FF">onMessage</span>**: Fires for every message received
- **<span style="color:#EA7171">onError</span>**: Fires on connection or message errors
- **<span style="color:#8FBE6D">onBroadcast</span>**: Fires for broadcast messages from server
- **<span style="color:#F8961F">onDisplay</span>**: Fires when display events are received (tables, forms, etc.)
- **<span style="color:#00D4FF">onInput</span>**: Fires when server requests user input

```javascript
const client = new BifrostClient('ws://localhost:8765', {
    hooks: {
        onConnected: (info) => {
            console.log('Connected to zBifrost:', info);
            updateStatus('Connected');
        },
        
        onDisconnected: (reason) => {
            console.log('Disconnected:', reason);
            updateStatus('Disconnected');
        },
        
        onBroadcast: (msg) => {
            if (msg.event === 'data_updated') {
                refreshData();
            }
        },
        
        onDisplay: (data) => {
            // Custom rendering logic
            if (data.type === 'table') {
                renderCustomTable(data.rows);
            }
        },
        
        onInput: (request) => {
            const answer = prompt(request.message);
            client.sendInputResponse(request.id, answer);
        }
    }
});
```

## zCLI Integration Methods

BifrostClient provides convenience methods for zCLI-specific operations:

```javascript
// Execute zFunc
const result = await client.zFunc('&myapp.send_email', {
    to: 'user@example.com',
    subject: 'Welcome'
});

// Navigate zLink
await client.zLink('@.zUI.reports');

// Open resource
await client.zOpen('https://example.com');
```

## Environment Variables

Configure zBifrost server via environment variables (loaded by zConfig):

- **<span style="color:#00D4FF">WEBSOCKET_HOST</span>**: Server host (default: 127.0.0.1)
- **<span style="color:#00D4FF">WEBSOCKET_PORT</span>**: Server port (default: 8765)
- **<span style="color:#00D4FF">WEBSOCKET_REQUIRE_AUTH</span>**: Require authentication (true/false)
- **<span style="color:#00D4FF">WEBSOCKET_ALLOWED_ORIGINS</span>**: Comma-separated CORS origins

```bash
# Example .zEnv file
WEBSOCKET_HOST=127.0.0.1
WEBSOCKET_PORT=8765
WEBSOCKET_REQUIRE_AUTH=false
WEBSOCKET_ALLOWED_ORIGINS=http://localhost:8080,https://example.com
```

## Event-Driven Message Protocol

All messages follow a standard event-driven format:

```javascript
// Client → Server
{
    "event": "dispatch",
    "data": {
        "zKey": "zData",
        "action": "read",
        "table": "users"
    }
}

// Server → Client
{
    "event": "display",
    "data": {
        "type": "table",
        "rows": [...],
        "headers": ["Name", "Email"]
    }
}
```

**Backward Compatibility:** Legacy message formats (without `event` field) are automatically converted.

## Performance

- **Connection**: < 100ms to establish
- **Message**: < 10ms round-trip
- **Rendering**: < 50ms for 1000 rows
- **Memory**: ~2MB for client library
- **Bundle Size**: 26KB (minified), 8KB (gzipped)

## Browser Compatibility

- ✅ Chrome/Edge 88+
- ✅ Firefox 78+
- ✅ Safari 14+
- ✅ All browsers with WebSocket and ES6 support

---

**Version**: 1.5.5  
**Layer**: 0 (Foundation)  
**See Also**: [zComm Guide](zComm_GUIDE.md) for HTTP client and service orchestration
