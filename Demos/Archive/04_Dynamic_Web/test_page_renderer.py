#!/usr/bin/env python3
"""Test PageRenderer directly without server"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from zCLI import zCLI
from zCLI.subsystems.zServer.zServer_modules.page_renderer import PageRenderer

# Initialize zCLI
z = zCLI({
    'zSpace': os.path.dirname(os.path.abspath(__file__)),
    'zMode': 'Terminal'
})

# Load routes
routes_data = z.loader.handle('./zServer_routes.yaml')
routes = routes_data.get('routes', {})

print("="*60)
print("Testing PageRenderer with Dual-Mode Navigation")
print("="*60)
print(f"\nRoutes loaded: {len(routes)} routes")
for route_path in list(routes.keys())[:5]:
    print(f"  - {route_path}")

# Create renderer with routes
renderer = PageRenderer(z, routes=routes)

print(f"\nFile-to-Route mappings: {len(renderer._file_to_route_map)}")
for file_path, http_route in renderer._file_to_route_map.items():
    print(f"  {file_path} → {http_route}")

# Test rendering
print("\n" + "="*60)
print("Rendering Dashboard:")
print("="*60)

html = renderer.render_page('./zUI_web_dashboard.yaml', 'zVaF')

# Show first 1000 chars
print("\nHTML Output (first 1000 chars):")
print(html[:1000])

# Check for key elements
print("\n" + "="*60)
print("Validation:")
print("="*60)
print(f"✓ Has <h1> header: {'<h1>' in html}")
print(f"✓ Has dashboard title: {'Welcome to zCLI Dashboard' in html}")
print(f"✓ Has nav menu: {'<nav class=\"menu\">' in html}")
print(f"✓ Has User link: {'/users' in html or '@.zUI_web_users' in html}")
print(f"✓ Debug divs present: {'<div class=\\'debug\\'>' in html}")

if '<div class=\\'debug\\'>' in html:
    print("\n⚠️  DEBUG: Display events not rendering properly!")
    print("Looking for zDisplay in output:")
    import re
    debug_divs = re.findall(r"<div class='debug'><strong>(.*?):</strong>", html)
    for key in debug_divs[:5]:
        print(f"  - {key}")

