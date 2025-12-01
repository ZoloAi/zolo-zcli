[← Back to Level 1](../Level_1_Echo/README.md) | [Next: Level 3 →](../Level_3_Getting_Started/README.md)

# Level 2: Post Feed

**<span style="color:#8FBE6D">Display multiple posts as cards—build a real blog homepage!</span>**

## What You'll Build

A blog homepage that displays 5 posts in a responsive card grid. Each card shows the title, author, date, excerpt, and tags—just like Medium, Dev.to, or any modern blog!

Think of it like scrolling through your favorite blog's homepage.

## What You'll Learn

1. **<span style="color:#8FBE6D">How to work with arrays of data</span>** (lists of posts, not just one)
2. **<span style="color:#F8961F">How to loop through data and create elements</span>** (dynamic rendering)
3. **<span style="color:#00D4FF">How to build responsive card layouts</span>** (CSS Grid for modern UIs)

## Files

- **<span style="color:#F8961F">`level2_backend.py`</span>** - Python server with 5 hardcoded posts (87 lines)
- **<span style="color:#F8961F">`level2_client.html`</span>** - Web page that displays the feed (uses BifrostClient)
- **<span style="color:#F8961F">`styles.css`</span>** - Same purple gradient theme from previous levels

## How to Run

### Step 1: Start the Server

```bash
cd Demos/Layer_0/zBifrost_Demo/Level_2_Post_Feed
python3 level2_backend.py
```

You should see:

```
Starting zBlog Server (Level 2: Post Feed)...
Goal: Display 5 blog posts in a feed, like a real blog homepage

✓ Blog feed handler registered (5 posts available)!
zBlog server is running!
Open level2_client.html in your browser
Click 'Load Feed' to see all blog posts!
```

**Keep this terminal window open!**

### Step 2: Open the Web Page

Double-click **<span style="color:#F8961F">`level2_client.html`</span>** (or drag into browser).

**Note:** Like previous levels, BifrostClient automatically detects `file://` protocol and works without an HTTP server!

### Step 3: Load the Feed!

1. Click **<span style="color:#8FBE6D">"🚀 Connect to Server"</span>**
2. Wait for green status: **"✅ Connected to zBlog!"**
3. Click **<span style="color:#667eea">"📰 Load Feed"</span>**
4. Watch 5 blog posts appear as cards in a grid!

**That's a real blog homepage!** 📰

## What's Happening Under the Hood

### The Server (Python) - NEW: Array of Posts

```python
# Hardcoded blog posts (array of 5 posts)
BLOG_POSTS = [
    {
        "id": 1,
        "title": "Welcome to zBlog!",
        "author": "zCLI Team",
        "date": "2024-01-15",
        "excerpt": "Learn how to build...",
        "tags": ["tutorial", "welcome", "zCLI"]
    },
    {
        "id": 2,
        "title": "Understanding WebSockets",
        ...
    },
    # ... 3 more posts
]

async def handle_get_posts(websocket, message_data):
    """Handle requests for the blog post feed"""
    response = {
        "event": "posts_data",
        "posts": BLOG_POSTS,      # Send the entire array
        "count": len(BLOG_POSTS)  # Also send the count
    }
    await websocket.send(json.dumps(response))

# Register handler
z.comm.websocket._event_map['get_posts'] = handle_get_posts
```

**What's new:**
1. We have an **array** of posts (not just one)
2. The handler sends the entire array as JSON
3. We also send the count for display

### The Client (JavaScript) - NEW: Looping & Creating Cards

```javascript
function displayFeed(posts, count) {
    // Show count
    document.getElementById('postCount').textContent = `📚 ${count} Posts in Feed`;
    
    // Loop through each post and create a card
    posts.forEach(post => {
        const card = createPostCard(post);
        postsFeed.appendChild(card);
    });
}

function createPostCard(post) {
    // Create a div for the card
    const card = document.createElement('div');
    card.style.cssText = '...'; // Styling
    
    // Create title element
    const title = document.createElement('h3');
    title.textContent = post.title;
    card.appendChild(title);
    
    // Create metadata, excerpt, tags...
    // ...
    
    return card;
}
```

**What's new:**
1. We use `forEach()` to loop through the array
2. For each post, we call `createPostCard()`
3. `createPostCard()` builds the HTML elements dynamically
4. We use CSS Grid to display cards in a responsive layout

### The Flow

```
Browser                          Server
   |                               |
   |  1. Connect                   |
   |------------------------------>|
   |                               |
   |  2. {event: 'get_posts'}      |
   |------------------------------>|
   |                               |
   |  3. {event: 'posts_data',     |
   |      posts: [...],            |
   |      count: 5}                |
   |<------------------------------|
   |                               |
   |  4. Loop & render 5 cards     |
   |                               |
```

**Key Difference from Level 1:**
- Level 1: Simple echo (strings)
- Level 2: **Multiple structured posts** (array of objects)

## Success Checklist

- **<span style="color:#8FBE6D">Server starts</span>** without errors
- **<span style="color:#8FBE6D">Browser connects</span>** (green status)
- **<span style="color:#F8961F">"Load Feed" button appears</span>** after connecting
- **<span style="color:#00D4FF">Post count shows</span>** "📚 5 Posts in Feed"
- **<span style="color:#667eea">5 cards appear</span>** in a responsive grid
- **<span style="color:#EA7171">Cards have hover effect</span>** (lift up when you hover)
- **<span style="color:#8FBE6D">Each card shows</span>** title, author, date, excerpt, tags

## Troubleshooting

### "Not connected to server!" alert

**Problem:** Trying to load feed before connecting.

**Solution:** Click "Connect to Server" first, wait for green status, then click "Load Feed".

### Feed doesn't appear

**Problem:** Server might not be sending the response.

**Solution:**
1. Check terminal for errors
2. Look for `[zBifrost] [RECV] Received: {"event":"get_posts"...}` in terminal
3. Check browser console (F12) for the `posts_data` message
4. Restart `level3_backend.py`

### Cards look broken or overlap

**Problem:** CSS Grid might not be working.

**Solution:**
1. Make sure you're using a modern browser (Chrome, Firefox, Safari, Edge)
2. Try resizing the window to see the responsive layout
3. Check browser console for errors

### Only some cards appear

**Problem:** JavaScript error while creating cards.

**Solution:**
1. Open browser console (F12)
2. Look for red error messages
3. Check if all 5 posts have the required fields (title, author, date, excerpt, tags)

## Imperative Foundation Complete! 🎉

**<span style="color:#8FBE6D">Congratulations!</span>** With Levels 0-2, you now have **everything needed to build ANY web app imperatively** using zBifrost WebSocket:

- ✅ Connection lifecycle (Level 0)
- ✅ Custom event handlers (Level 1)
- ✅ Complex data structures & manual rendering (Level 2)

**You could build a full WordPress-like blog, e-commerce site, or any complex application** using these patterns:
- Custom events for CRUD operations
- Manual DOM manipulation (or React/Vue/Svelte)
- Full control over WebSocket communication
- Mix and match patterns as needed

**However**, showing the entire structure of such a demo would be redundant—the concepts are all here in these fundamentals.

## What's Next?

In **<span style="color:#F8961F">Level 3</span>**, you'll see **THE GAME CHANGER**! The same blog feed, but using zDisplay events with zTheme auto-rendering. You'll discover the **proper declarative way** to build such apps - 90% less code for the same result!

**Key Concept:** Level 2 is imperative (manual, full control). Level 3 is declarative (describe what you want, zDisplay + zTheme handle how).

---

**Version**: 1.5.5  
**Difficulty**: Beginner  
**Time**: 15 minutes  
**Builds On**: Level 1 (two-way communication)
