/**
 * ═══════════════════════════════════════════════════════════════
 * Navigation Renderer - zTheme Navigation Components
 * ═══════════════════════════════════════════════════════════════
 * 
 * Renders navigation components aligned with zTheme:
 * - zNav (navigation bars)
 * - zNavbar (top navigation)
 * - zBreadcrumb (breadcrumb trails)
 * - zTabs (tabbed navigation)
 * - zPagination (page navigation)
 * - Sidebar navigation
 * - Dropdown menus
 * 
 * ✨ REFACTORED: Uses Layer 0 primitives
 * 
 * @module rendering/navigation_renderer
 * @layer 3
 * @pattern Strategy (navigation components)
 * 
 * @see https://github.com/ZoloAi/zTheme - zTheme Navigation
 */

// ─────────────────────────────────────────────────────────────────
// Imports
// ─────────────────────────────────────────────────────────────────
import { createNav } from './primitives/document_structure_primitives.js';
import { createList, createListItem } from './primitives/lists_primitives.js';
import { createLink, createButton } from './primitives/interactive_primitives.js';
import { createDiv, createSpan } from './primitives/generic_containers.js';

export class NavigationRenderer {
  constructor(logger = null) {
    this.logger = logger || console;
  }

  /**
   * Render a navigation bar from menu items (zTheme zNavbar component)
   * @param {Array<string|Object>} items - Array of navigation items (strings or {label, href})
   * @param {Object} options - Rendering options
   * @returns {HTMLElement} - Navigation element with zNavbar classes
   * @see https://github.com/ZoloAi/zTheme/blob/main/src/css/zNavbar.css
   */
  renderNavBar(items, options = {}) {
    if (!Array.isArray(items) || items.length === 0) {
      this.logger.warn('[NavigationRenderer] No items provided for navbar');
      return null;
    }

    const {
      className = 'zcli-navbar-meta',
      theme = 'light',
      activeIndex = null,
      href = '#',
      brand = null
    } = options;

    // Generate unique ID for collapse target
    const collapseId = `navbar-collapse-${Math.random().toString(36).substr(2, 9)}`;

    // Create nav container with zNavbar component classes (using primitive)
    const nav = createNav({ 
      class: `zNavbar zNavbar-${theme} ${className}`,
      role: 'navigation'
    });

    // Add brand/logo if provided (using primitive)
    if (brand) {
      const brandLink = createLink('/', { class: 'zNavbar-brand' });
      brandLink.textContent = brand;
      nav.appendChild(brandLink);
    }

    // Create mobile hamburger toggle button (using primitive)
    const toggleButton = createButton('button', {
      class: 'zNavbar-toggler',
      'data-bs-toggle': 'collapse',
      'data-bs-target': `#${collapseId}`,
      'aria-controls': collapseId,
      'aria-expanded': 'false',
      'aria-label': 'Toggle navigation'
    });

    // Add Bootstrap Icon (hamburger menu)
    toggleButton.innerHTML = `
      <i class="bi bi-list" style="font-size: 1.5rem;"></i>
    `;
    nav.appendChild(toggleButton);

    // Create navbar collapse wrapper (using primitive)
    const collapseDiv = createDiv({ 
      class: 'zNavbar-collapse',
      id: collapseId
    });

    // Create navigation list (using primitive)
    const ul = createList(false, { class: 'zNavbar-nav' });

    // Create nav items with zNav-item and zNav-link classes
    items.forEach((item, index) => {
      const li = createListItem({ class: 'zNav-item' });

      const a = createLink('#');
      
      // Handle item as string or object {label, href}
      let itemLabel, itemHref;
      if (typeof item === 'string') {
        // Strip navigation prefixes for clean display
        // $ (delta link), ^ (bounce-back), ~ (anchor)
        // Example: "$^zLogin" → "zLogin"
        itemLabel = item.replace(/^[\$\^~]+/, '');
        // Convert delta links ($zBlock) to web routes (/zBlock)
        itemHref = this._convertDeltaLinkToHref(item);
      } else if (typeof item === 'object' && item !== null) {
        itemLabel = item.label || item.text || '';
        // Strip navigation prefixes for clean display
        itemLabel = itemLabel.replace(/^[\$\^~]+/, '');
        itemHref = item.href || this._convertDeltaLinkToHref(itemLabel);
      } else {
        itemLabel = String(item);
        itemHref = href;
      }
      
      a.href = itemHref;
      a.textContent = itemLabel;
      a.classList.add('zNav-link');
      
      // Add active state if specified
      if (activeIndex === index) {
        a.classList.add('active');
      }

      li.appendChild(a);
      ul.appendChild(li);
    });

    // Assemble: ul -> collapseDiv -> nav
    collapseDiv.appendChild(ul);
    nav.appendChild(collapseDiv);
    
    return nav;
  }

  /**
   * Convert delta link notation ($zBlock) to web route (/zBlock)
   * 
   * Delta links ($) are used in YAML for intra-file navigation.
   * Navigation modifiers (^, ~) are stripped for clean URLs.
   * In Bifrost mode, these are converted to web routes for proper navigation.
   * 
   * @param {string} item - Item text (may contain $^zBlock notation with modifiers)
   * @returns {string} - Web-friendly href
   * @private
   */
  _convertDeltaLinkToHref(item) {
    if (typeof item !== 'string') {
      return '#';
    }
    
    // Strip all navigation prefixes: $ (delta), ^ (bounce-back), ~ (anchor)
    // Example: "$^zLogin" → "zLogin" → "/zLogin"
    const cleanBlock = item.replace(/^[\$\^~]+/, '');
    
    // Check if original item had $ (delta link) or other navigation prefixes
    if (item !== cleanBlock) {
      // Had navigation prefixes - convert to web route
      return `/${cleanBlock}`;
    }
    
    // Default: use item as-is (for explicit /path or # links)
    return item.startsWith('/') || item.startsWith('#') ? item : `/${item}`;
  }

  /**
   * Render breadcrumb navigation (zTheme-styled)
   * @param {Array<string>} trail - Breadcrumb trail items
   * @param {Object} options - Rendering options
   * @returns {HTMLElement} - Breadcrumb element with zTheme classes
   */
  renderBreadcrumb(trail, options = {}) {
    if (!Array.isArray(trail) || trail.length === 0) {
      return null;
    }

    const {
      separator = '>',
      className = 'zcli-breadcrumb'
    } = options;

    const nav = createNav({ 
      class: `${className} zmb-3`,
      'aria-label': 'breadcrumb'
    });

    const ol = createList(true, { 
      class: 'zD-flex zFlex-row zFlex-items-center zGap-2'
    });
    ol.style.listStyle = 'none';
    ol.style.padding = '0';
    ol.style.margin = '0';

    trail.forEach((item, index) => {
      const li = createListItem({ class: 'breadcrumb-item' });
      
      if (index === trail.length - 1) {
        // Last item (current page) - use muted text, bold weight (using primitive)
        const span = createSpan({ 
          class: 'zText-muted zFw-bold',
          'aria-current': 'page'
        });
        span.textContent = item;
        li.appendChild(span);
      } else {
        // Link to parent pages - use primary color (using primitive)
        const a = createLink('#', { class: 'zText-primary zText-decoration-none' });
        a.textContent = item;
        li.appendChild(a);
      }

      ol.appendChild(li);

      // Add separator (except after last item) (using primitive)
      if (index < trail.length - 1) {
        const sep = createSpan({ class: 'breadcrumb-separator zText-muted' });
        sep.textContent = ` ${separator} `;
        ol.appendChild(sep);
      }
    });

    nav.appendChild(ol);
    return nav;
  }

  /**
   * Render vertical sidebar navigation (zTheme-styled)
   * @param {Array<string>} items - Navigation item labels
   * @param {Object} options - Rendering options
   * @returns {HTMLElement} - Sidebar nav element with zTheme classes
   */
  renderSidebarNav(items, options = {}) {
    if (!Array.isArray(items) || items.length === 0) {
      return null;
    }

    const {
      className = 'zcli-sidebar-nav',
      activeIndex = null
    } = options;

    // Sidebar container with zTheme utilities (using primitive)
    const nav = createNav({ class: `${className} zBg-light zP-3 zRounded` });
    nav.style.width = '200px';

    const ul = createList(false, { class: 'zD-flex zFlex-column zGap-2' });
    ul.style.listStyle = 'none';
    ul.style.padding = '0';
    ul.style.margin = '0';

    items.forEach((item, index) => {
      const li = createListItem({ class: 'sidebar-item' });

      const a = createLink('#');
      a.textContent = item;
      
      // zTheme sidebar link: padding, display block, rounded
      a.className = `sidebar-link zText-dark zText-decoration-none zP-2 zD-block zRounded`;

      // Active state with zTheme classes
      if (activeIndex === index) {
        a.classList.add('zBg-primary', 'zText-white', 'zFw-bold');
      }

      // Hover effect via zTheme classes
      a.addEventListener('mouseenter', () => {
        if (activeIndex !== index) {
          a.classList.add('zBg-white');
        }
      });
      a.addEventListener('mouseleave', () => {
        if (activeIndex !== index) {
          a.classList.remove('zBg-white');
        }
      });

      li.appendChild(a);
      ul.appendChild(li);
    });

    nav.appendChild(ul);
    return nav;
  }
}

