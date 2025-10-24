# zTheme - zCLI's CSS Framework

**Location**: `zCLI/utils/zTheme/`  
**Version**: 1.0.0  
**Type**: Utility (not a subsystem)

## Overview

zTheme is zCLI's comprehensive CSS framework providing consistent styling across all zCLI applications, demos, and user interfaces. It uses CSS variables for easy customization and includes components for buttons, tables, forms, alerts, and more.

## Architecture

```
zCLI/utils/zTheme/
├── zTheme_loader.js          # Auto-loader for all CSS files
├── README.md                  # This file
├── css/
│   ├── css_vars.css          # CSS variables (colors, sizes, etc.)
│   ├── zMain.css             # Base styles and resets
│   ├── zTypography.css       # Font styles and text utilities
│   ├── zContainers.css       # Layout containers
│   ├── zSpacing.css          # Margin/padding utilities
│   ├── zButtons.css          # Button components
│   ├── zTables.css           # Table components
│   ├── zInputs.css           # Form inputs
│   ├── zAlerts.css           # Alert/message components
│   ├── zPanels.css           # Panel/card components
│   ├── zNav.css              # Navigation components
│   ├── zModal.css            # Modal dialogs
│   ├── zPagination.css       # Pagination controls
│   ├── zImages.css           # Image utilities
│   ├── zMedia.css            # Media queries and responsive
│   ├── zEffects.css          # Animations and transitions
│   ├── zDashboard.css        # Dashboard layouts
│   ├── zHome.css             # Homepage styles
│   ├── zLogin.css            # Login page styles
│   ├── zShop.css             # E-commerce styles
│   ├── zReviews.css          # Review components
│   ├── zAddToCart.css        # Shopping cart
│   ├── zFooter.css           # Footer styles
│   ├── zPage.css             # Page layouts
│   └── zDev.css              # Development utilities (optional)
└── fonts/                     # Custom fonts (Yarden, Kalam)
```

## Usage

### Option 1: Auto-Load (Recommended)

```html
<!DOCTYPE html>
<html>
<head>
    <!-- Load zTheme automatically -->
    <script src="/zCLI/utils/zTheme/zTheme_loader.js"></script>
</head>
<body>
    <div class="zContainer">
        <button class="zoloButton zBtnPrimary">Click Me</button>
    </div>
</body>
</html>
```

### Option 2: Manual Load (Specific Files)

```html
<head>
    <link rel="stylesheet" href="/zCLI/utils/zTheme/css/css_vars.css">
    <link rel="stylesheet" href="/zCLI/utils/zTheme/css/zMain.css">
    <link rel="stylesheet" href="/zCLI/utils/zTheme/css/zButtons.css">
    <!-- Add only the files you need -->
</head>
```

### Option 3: JavaScript API

```javascript
// Load with default settings
await zThemeLoader.load();

// Load with custom path
await zThemeLoader.load('/custom/path/to/zTheme');

// Load minimal (only core + essential components)
await zThemeLoader.load(null, { minimal: true });

// Load with dev utilities
await zThemeLoader.load(null, { includeDev: true });

// Check if loaded
if (zThemeLoader.isLoaded()) {
    console.log('Theme is ready!');
}

// Get loaded files
const files = zThemeLoader.getLoadedFiles();

// Reload theme (useful for development)
await zThemeLoader.reload();

// Unload theme
zThemeLoader.unload();
```

### Option 4: Disable Auto-Load

```html
<script>
    // Disable auto-load before loading zTheme_loader.js
    window.zThemeAutoLoad = false;
</script>
<script src="/zCLI/utils/zTheme/zTheme_loader.js"></script>
<script>
    // Manually load when ready
    zThemeLoader.load();
</script>
```

## Core Components

### Buttons

```html
<!-- Base button -->
<button class="zoloButton">Default</button>

<!-- Color variants -->
<button class="zoloButton zBtnPrimary">Primary</button>
<button class="zoloButton zBtnInfo">Info</button>
<button class="zoloButton zBtnWarning">Warning</button>
<button class="zoloButton zBtnDanger">Danger</button>

<!-- Sizes -->
<button class="zoloButton zBtn-sm">Small</button>
<button class="zoloButton zBtn-md">Medium</button>
<button class="zoloButton zBtn-lg">Large</button>

<!-- Tab buttons -->
<button class="zoloButton zBtnTab">Tab</button>
<button class="zoloButton zBtnTab active-tab">Active Tab</button>

<!-- Button group -->
<div class="button-group">
    <button class="zoloButton zBtnPrimary">Save</button>
    <button class="zoloButton zBtnInfo">Cancel</button>
</div>
```

### Tables

```html
<!-- Basic table -->
<table class="zTable">
    <thead>
        <tr><th>Name</th><th>Email</th></tr>
    </thead>
    <tbody>
        <tr><td>John</td><td>john@example.com</td></tr>
    </tbody>
</table>

<!-- Striped table -->
<table class="zTable zTable-striped">...</table>

<!-- Hoverable rows -->
<table class="zTable zTable-hover">...</table>

<!-- Bordered table -->
<table class="zTable zTable-bordered">...</table>

<!-- Small table -->
<table class="zTable zTable-sm">...</table>
```

### Containers

```html
<!-- Responsive container -->
<div class="zContainer">
    <h1>Content</h1>
</div>

<!-- Fluid container (full width) -->
<div class="zContainer-fluid">
    <h1>Full Width</h1>
</div>

<!-- Sized containers -->
<div class="zContainer-sm">Small</div>
<div class="zContainer-md">Medium</div>
<div class="zContainer-lg">Large</div>
<div class="zContainer-xl">Extra Large</div>
```

### Alerts

```html
<div id="flash-messages">
    <div class="alert alert-success">Success message!</div>
    <div class="alert alert-info">Info message</div>
    <div class="alert alert-warning">Warning message</div>
    <div class="alert alert-danger">Error message</div>
</div>
```

## CSS Variables

zTheme uses CSS variables for easy customization:

```css
/* Colors */
--mainBase: #ffffff;
--grayDark: #333333;
--mainBlue: #007bff;
--mainGreen: #28a745;
--mainOrange: #fd7e14;
--mainRed: #dc3545;
--mainPurple: #6f42c1;
--mainYellow: #ffc107;

/* Gradients */
--mainGrad: linear-gradient(to right, #667eea, #764ba2);
--blueGrad: linear-gradient(to right, #56ccf2, #2f80ed);
--orangeGrad: linear-gradient(to right, #f2994a, #f2c94c);
--purpleGrad: linear-gradient(to right, #a8edea, #fed6e3);

/* Typography */
--h1size: 2.5rem;
--h2size: 2rem;
--h3size: 1.75rem;
--h4size: 1.5rem;
--h5size: 1.25rem;
--h6size: 1rem;

/* Spacing */
--spacing-xs: 0.25rem;
--spacing-sm: 0.5rem;
--spacing-md: 1rem;
--spacing-lg: 1.5rem;
--spacing-xl: 2rem;
```

### Customizing Variables

```html
<style>
    :root {
        --mainBlue: #0056b3;  /* Custom blue */
        --h1size: 3rem;       /* Larger headings */
    }
</style>
```

## Integration with zBifrost

zBifrost automatically loads zTheme via `zTheme_loader.js`. If the loader is not found, it will attempt to load it dynamically.

```javascript
// BifrostClient detects zTheme_loader automatically
const client = new BifrostClient('ws://localhost:8765');
// Theme loads automatically!
```

## Best Practices

1. **Always load `css_vars.css` first** - Other files depend on CSS variables
2. **Load `zMain.css` second** - Provides base styles and resets
3. **Load component files as needed** - Only include what you use
4. **Use the loader for production** - Handles dependencies automatically
5. **Customize via CSS variables** - Don't modify theme files directly

## File Loading Order

The `zTheme_loader.js` loads files in this order:

1. **Core**: `css_vars.css`, `zMain.css`, `zTypography.css`
2. **Layout**: `zContainers.css`, `zSpacing.css`, `zPage.css`
3. **Components**: `zButtons.css`, `zInputs.css`, `zTables.css`, etc.
4. **Specialized**: `zDashboard.css`, `zShop.css`, etc.
5. **Development**: `zDev.css` (optional)

## Minimal Mode

For lightweight applications, use minimal mode:

```javascript
await zThemeLoader.load(null, { minimal: true });
```

Loads only:
- `css_vars.css`
- `zMain.css`
- `zTypography.css`
- `zContainers.css`
- `zButtons.css`
- `zTables.css`
- `zAlerts.css`

## Development Mode

Include development utilities:

```javascript
await zThemeLoader.load(null, { includeDev: true });
```

Adds `zDev.css` with debugging utilities and visual helpers.

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- IE11: ❌ Not supported (uses CSS variables)

## Migration from Old Path

**Old**: `zCLI/subsystems/zTheme/` ❌  
**New**: `zCLI/utils/zTheme/` ✅

Update all references:
```javascript
// Old
import '/zCLI/subsystems/zTheme/...'

// New
import '/zCLI/utils/zTheme/...'
```

## Related Documentation

- [zComm Guide](../../Documentation/zComm_GUIDE.md) - WebSocket communication
- [zDisplay Guide](../../Documentation/zDisplay_GUIDE.md) - Terminal UI
- [BifrostClient v2.0](../../Documentation/Release/RELEASE_1.5.4_BIFROST_REFACTOR_V2.md)

---

**Version**: 1.0.0  
**Last Updated**: October 24, 2025  
**Maintainer**: Gal Nachshon

