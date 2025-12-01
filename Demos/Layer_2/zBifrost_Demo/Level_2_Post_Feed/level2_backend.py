#!/usr/bin/env python3
"""
Level 2: Post Feed
Display multiple blog posts as cards - like a real blog homepage!
Goal: Show how to work with arrays of structured data
"""
from zCLI import zCLI
import asyncio
import json

print("Starting zBlog Server (Level 2: Post Feed)...")
print("Goal: Display 5 blog posts in a feed, like a real blog homepage\n")

z = zCLI({
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False  # Level 2: No auth required
    }
})

# Hardcoded blog posts (in a real app, this would come from a database)
BLOG_POSTS = [
    {
        "id": 1,
        "title": "Welcome to zBlog!",
        "author": "zCLI Team",
        "date": "2024-01-15",
        "excerpt": "Learn how to build a real-time blog platform using zCLI's zBifrost WebSocket bridge.",
        "tags": ["tutorial", "welcome", "zCLI"]
    },
    {
        "id": 2,
        "title": "Understanding WebSockets",
        "author": "Alice Developer",
        "date": "2024-01-14",
        "excerpt": "WebSockets enable real-time bidirectional communication between clients and servers. Here's how they work.",
        "tags": ["websockets", "networking", "tutorial"]
    },
    {
        "id": 3,
        "title": "Python Backend Best Practices",
        "author": "Bob Engineer",
        "date": "2024-01-13",
        "excerpt": "Building scalable Python backends requires following certain patterns. Let's explore the most important ones.",
        "tags": ["python", "backend", "best-practices"]
    },
    {
        "id": 4,
        "title": "Frontend Design Patterns",
        "author": "Carol Designer",
        "date": "2024-01-12",
        "excerpt": "Modern frontend development relies on proven design patterns. Discover the patterns that make UIs maintainable.",
        "tags": ["frontend", "design", "javascript"]
    },
    {
        "id": 5,
        "title": "Building Real-Time Apps",
        "author": "Dave Architect",
        "date": "2024-01-11",
        "excerpt": "Real-time applications are becoming the norm. Learn how to architect systems that scale with WebSocket connections.",
        "tags": ["real-time", "architecture", "scaling"]
    }
]

# Register custom message handler for getting all posts
async def handle_get_posts(websocket, message_data):
    """Handle requests for the blog post feed"""
    if isinstance(message_data, str):
        message_data = json.loads(message_data)
    
    # Send all blog posts back
    response = {
        "event": "posts_data",
        "posts": BLOG_POSTS,
        "count": len(BLOG_POSTS)
    }
    await websocket.send(json.dumps(response))

# Attach the handler to zBifrost's event map
if z.comm.websocket:
    z.comm.websocket._event_map['get_posts'] = handle_get_posts
    print(f"✓ Blog feed handler registered ({len(BLOG_POSTS)} posts available)!")
else:
    print("✗ Warning: Could not register blog feed handler")

print("zBlog server is running!")
print("Open level2_client.html in your browser")
print("Click 'Load Feed' to see all blog posts!\n")

z.walker.run()
