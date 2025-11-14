# Flask → zCLI Workflow Mapping (Levels 4-10)

This document outlines the step-by-step workflow for building a blog in Flask vs. zCLI, mapped to demo Levels 4-10.

## Complete Workflow Comparison

| Step | Flask Workflow | zCLI Workflow | zCLI Subsystems | Demo Level |
|------|----------------|---------------|-----------------|------------|
| **0-2** | Set up Flask routes, templates, static files | WebSocket server + BifrostClient | zBifrost, zDisplay | Levels 0-2 ✅ |
| **3** | Create Jinja2 templates for post cards | `z.display.json_data()` + auto-rendering | zDisplay, zTheme | Level 3 ✅ |
| **4** | Define SQLAlchemy models (`Post`, `User`) | Write zSchema YAML (declarative schema) | zData, zSchema | Level 4 |
| **5** | Write SQL queries (`SELECT * FROM posts`) | `z.data.select("posts")` (auto-query) | zData | Level 5 |
| **6** | Create HTML forms + Flask-WTF validation | `z.display.form()` (auto-rendered + validated) | zDisplay, zData | Level 6 |
| **7** | Write CRUD routes (`/post/edit/<id>`, `/post/delete/<id>`) | `z.display.table(posts, actions=["edit", "delete"])` | zDisplay, zData | Level 7 |
| **8** | Define foreign keys, write JOIN queries | zSchema foreign keys + `z.data.select(join=...)` | zData, zSchema | Level 8 |
| **9** | Implement Flask-Login, session management | `z.auth.login()` + RBAC rules in YAML | zAuth | Level 9 |
| **10** | Build admin panel (routes, templates, permissions) | `z.display.menu()` + `z.display.table()` + RBAC | zDisplay, zAuth, zData | Level 10 |

## Detailed Level Specifications

### Level 4: Database Schema
**Flask Equivalent**: Define SQLAlchemy models

**Files to Create**:
- `zSchema.blog.yaml` (declarative schema)
- `level4_backend.py` (load schema, create tables)
- `level4_client.html` (same as Level 3, no changes!)

**zSchema.blog.yaml Structure**:
```yaml
Meta:
  Data_Type: sqlite
  Data_Path: ~/.zMachine/data/zblog.db
  Data_Label: zBlog Database

posts:
  id:
    type: INTEGER
    primary_key: true
    auto_increment: true
  title:
    type: TEXT
    required: true
    rules:
      maxLength: 200
  author:
    type: TEXT
    required: true
    rules:
      maxLength: 100
  content:
    type: TEXT
    required: true
  excerpt:
    type: TEXT
    rules:
      maxLength: 500
  tags:
    type: TEXT
  date:
    type: DATE
    default: "CURRENT_DATE"
  status:
    type: TEXT
    default: "draft"
    rules:
      pattern: "^(draft|published|archived)$"
```

**Backend Code**:
```python
from zCLI import zCLI

z = zCLI({"zMode": "zBifrost", "websocket": {"port": 8765}})

# Load schema and create tables
z.data.load_schema("@.zSchema.blog")
z.data.create_table(["posts"])

z.display.success("Database schema created!")
z.walker.run()
```

**Key Learning**: Declarative schema definition, auto-table creation

---

### Level 5: Read Posts (Database)
**Flask Equivalent**: Write SQL queries or ORM code

**Files to Create**:
- `seed_data.py` (populate database with sample posts)
- `level5_backend.py` (query from database)
- `level5_client.html` (same as Level 3!)

**Backend Code**:
```python
async def handle_get_posts(websocket, message_data):
    # Query from database instead of hardcoded array
    posts = z.data.select("posts", where="status = 'published'", order_by="date DESC", limit=5)
    
    # Same zDisplay events as Level 3!
    z.display.header("zBlog Feed (from Database!)")
    z.display.success(f"Loaded {len(posts)} posts from SQLite")
    z.display.json_data(posts)
```

**Key Learning**: zData CRUD operations, WHERE/ORDER BY/LIMIT

---

### Level 6: Create Post Form
**Flask Equivalent**: Create HTML forms + Flask-WTF validation

**Backend Code**:
```python
async def handle_create_post_form(websocket, message_data):
    # Send form schema to client
    form_schema = {
        "title": {"type": "text", "label": "Post Title", "required": True, "maxLength": 200},
        "author": {"type": "text", "label": "Author", "required": True, "maxLength": 100},
        "content": {"type": "textarea", "label": "Content", "required": True, "rows": 10},
        "excerpt": {"type": "textarea", "label": "Excerpt", "maxLength": 500, "rows": 3},
        "tags": {"type": "text", "label": "Tags (comma-separated)"},
        "status": {"type": "select", "label": "Status", "options": ["draft", "published"], "default": "draft"}
    }
    z.display.form(form_schema, submit_event="submit_post")

async def handle_submit_post(websocket, message_data):
    # Validate and insert
    form_data = message_data.get("form_data")
    result = z.data.insert("posts", form_data)
    
    if result != "error":
        z.display.success("Post created successfully!")
        # Refresh feed
        handle_get_posts(websocket, {})
    else:
        z.display.error("Failed to create post")
```

**Key Learning**: `z.display.form()`, auto-validation, form submission

---

### Level 7: Edit/Delete (CRUD)
**Flask Equivalent**: Write CRUD routes for each action

**Backend Code**:
```python
async def handle_get_posts_table(websocket, message_data):
    posts = z.data.select("posts", order_by="date DESC")
    
    # Auto-rendered table with action buttons
    z.display.table(
        data=posts,
        columns=["id", "title", "author", "date", "status"],
        actions=["edit", "delete"],
        action_events={"edit": "edit_post", "delete": "delete_post"}
    )

async def handle_edit_post(websocket, message_data):
    post_id = message_data.get("id")
    post = z.data.select("posts", where=f"id = {post_id}", limit=1)[0]
    
    # Pre-filled form
    z.display.form(form_schema, submit_event="update_post", initial_data=post)

async def handle_delete_post(websocket, message_data):
    post_id = message_data.get("id")
    
    # Confirmation dialog
    z.display.confirm(
        message=f"Delete post #{post_id}?",
        on_confirm="confirm_delete_post",
        confirm_data={"id": post_id}
    )

async def handle_confirm_delete_post(websocket, message_data):
    post_id = message_data.get("id")
    z.data.delete("posts", where=f"id = {post_id}")
    z.display.success("Post deleted!")
    # Refresh table
    handle_get_posts_table(websocket, {})
```

**Key Learning**: `z.display.table()`, CRUD actions, confirmation dialogs

---

### Level 8: Comments System
**Flask Equivalent**: Define foreign keys, write JOIN queries

**zSchema Update**:
```yaml
comments:
  id:
    type: INTEGER
    primary_key: true
    auto_increment: true
  post_id:
    type: INTEGER
    required: true
    foreign_key:
      table: posts
      column: id
      on_delete: CASCADE
  author:
    type: TEXT
    required: true
  content:
    type: TEXT
    required: true
  date:
    type: DATE
    default: "CURRENT_DATE"
```

**Backend Code**:
```python
async def handle_get_posts_with_comments(websocket, message_data):
    # JOIN query
    posts = z.data.select(
        "posts",
        join={
            "comments": {"on": "posts.id = comments.post_id", "type": "LEFT"}
        },
        order_by="posts.date DESC"
    )
    
    # Nested rendering (BifrostClient handles this!)
    z.display.json_data(posts)
```

**Key Learning**: Foreign keys, JOINs, nested data structures

---

### Level 9: User Authentication
**Flask Equivalent**: Implement Flask-Login, session management

**zAuth YAML**:
```yaml
roles:
  admin:
    permissions:
      - posts:create
      - posts:edit
      - posts:delete
      - users:manage
  author:
    permissions:
      - posts:create
      - posts:edit_own
  viewer:
    permissions:
      - posts:read

users:
  alice:
    password_hash: "..."
    role: admin
  bob:
    password_hash: "..."
    role: author
```

**Backend Code**:
```python
async def handle_login(websocket, message_data):
    username = message_data.get("username")
    password = message_data.get("password")
    
    if z.auth.login(username, password):
        z.display.success(f"Welcome, {username}!")
        # Send user role
        role = z.auth.get_user_role(username)
        z.display.json_data({"role": role})
    else:
        z.display.error("Invalid credentials")

async def handle_delete_post_protected(websocket, message_data):
    # Check permission
    if not z.auth.check_permission("posts:delete"):
        z.display.error("You don't have permission to delete posts")
        return
    
    # Proceed with delete
    handle_confirm_delete_post(websocket, message_data)
```

**Key Learning**: `z.auth.login()`, RBAC rules, permission checks

---

### Level 10: Admin Dashboard
**Flask Equivalent**: Build admin panel (routes, templates, permissions)

**Backend Code**:
```python
async def handle_admin_dashboard(websocket, message_data):
    # Check admin permission
    if not z.auth.check_permission("users:manage"):
        z.display.error("Admin access required")
        return
    
    # Navigation menu
    z.display.menu([
        {"label": "Posts", "event": "admin_posts"},
        {"label": "Users", "event": "admin_users"},
        {"label": "Analytics", "event": "admin_analytics"}
    ])

async def handle_admin_users(websocket, message_data):
    users = z.data.select("users")
    z.display.table(
        data=users,
        columns=["id", "username", "role", "created_at"],
        actions=["edit", "delete"],
        action_events={"edit": "edit_user", "delete": "delete_user"}
    )

async def handle_admin_analytics(websocket, message_data):
    post_count = z.data.select("posts", fields=["COUNT(*) as count"])[0]["count"]
    comment_count = z.data.select("comments", fields=["COUNT(*) as count"])[0]["count"]
    user_count = z.data.select("users", fields=["COUNT(*) as count"])[0]["count"]
    
    z.display.json_data({
        "posts": post_count,
        "comments": comment_count,
        "users": user_count
    })
```

**Key Learning**: `z.display.menu()`, multi-view navigation, analytics queries

---

## Code Reduction Summary

**Flask (Imperative)**:
- ~500-1000 lines total
  - 50-100 lines: Routes
  - 200-300 lines: Templates (Jinja2)
  - 100-150 lines: Forms (Flask-WTF)
  - 50-100 lines: SQL queries/ORM
  - 100-150 lines: Auth logic (Flask-Login)

**zCLI (Declarative)**:
- ~50-100 lines total
  - 30-50 lines: zSchema YAML
  - 20-30 lines: Python backend (zDisplay events)
  - 10-20 lines: zAuth YAML
  - 1 line: HTML (`<div id="zContainer"></div>`)

**Result**: **90% less code, same functionality!**

---

## Frontend (Single HTML File)

**All levels use the SAME HTML file** (after Level 3):

```html
<!DOCTYPE html>
<html>
<head>
    <title>zBlog</title>
    <link rel="stylesheet" href="path/to/zTheme.css">
</head>
<body>
    <div id="zContainer"></div>
    
    <script src="path/to/bifrost_client.js"></script>
    <script>
        const client = new BifrostClient('ws://127.0.0.1:8765', {
            onDisplay: (event) => {
                // BifrostClient auto-renders ALL zDisplay events!
                // No manual DOM manipulation needed!
            }
        });
        client.connect();
    </script>
</body>
</html>
```

**That's it!** No templates, no forms, no manual DOM. Just one container div and BifrostClient handles everything!

