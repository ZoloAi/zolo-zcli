/**
 * ═══════════════════════════════════════════════════════════════
 * List Renderer - Bullet and Numbered Lists
 * ═══════════════════════════════════════════════════════════════
 * 
 * Renders list events from zCLI backend (BasicData subsystem).
 * Supports bullet lists (ul) and numbered lists (ol).
 * 
 * @module rendering/list_renderer
 * @layer 3
 * @pattern Strategy (single event type)
 * 
 * Philosophy:
 * - "Terminal first" - lists are fundamental data display primitives
 * - Pure rendering (no interactivity, no sorting, no filtering)
 * - Semantic HTML (ul/ol tags)
 * - Uses Layer 2 utilities exclusively (no inline logic)
 * 
 * Dependencies:
 * - Layer 2: dom_utils.js
 * 
 * Exports:
 * - ListRenderer: Class for rendering list events
 * 
 * Example:
 * ```javascript
 * import { ListRenderer } from './list_renderer.js';
 * 
 * const renderer = new ListRenderer(logger);
 * renderer.render({
 *   items: ['Item 1', 'Item 2', 'Item 3'],
 *   style: 'bullet'
 * }, 'zVaF');
 * ```
 */

// ─────────────────────────────────────────────────────────────────
// Imports
// ─────────────────────────────────────────────────────────────────
import { createElement, setAttributes } from '../utils/dom_utils.js';

// ─────────────────────────────────────────────────────────────────
// List Renderer Class
// ─────────────────────────────────────────────────────────────────

/**
 * ListRenderer - Renders bullet and numbered lists
 * 
 * Handles the 'list' zDisplay event from BasicData subsystem.
 * Creates semantic HTML lists (ul or ol) based on style parameter.
 * 
 * Style Mapping:
 * - 'bullet' → <ul> (unordered list)
 * - 'number' → <ol> (ordered/numbered list)
 * - Default: bullet
 */
export class ListRenderer {
  /**
   * Create a ListRenderer instance
   * @param {Object} logger - Logger instance for debugging
   */
  constructor(logger) {
    this.logger = logger || console;
    this.logger.log('[ListRenderer] ✅ Initialized');
  }

  /**
   * Render a list event
   * 
   * @param {Object} data - List event data
   * @param {Array<string|Object>} data.items - List items (strings or objects with 'content' field)
   * @param {string} [data.style='bullet'] - List style ('bullet' or 'number')
   * @param {number} [data.indent=0] - Indentation level (0 = no indent)
   * @param {string} [data.class] - Custom CSS class (optional)
   * @param {string} zone - Target DOM element ID
   * @returns {HTMLElement|null} Created list element or null if failed
   * 
   * @example
   * renderer.render({ items: ['A', 'B', 'C'], style: 'bullet' }, 'zVaF');
   * renderer.render({ items: ['1st', '2nd', '3rd'], style: 'number' }, 'zVaF');
   */
  render(data, zone) {
    const { items, style = 'bullet', indent = 0, class: customClass } = data;
    
    // Validate required parameters
    if (!items || !Array.isArray(items)) {
      this.logger.error('[ListRenderer] ❌ Missing or invalid required parameter: items (must be array)');
      return null;
    }
    
    if (items.length === 0) {
      this.logger.warn('[ListRenderer] ⚠️ Empty items array');
      // Still render empty list (semantic HTML)
    }
    
    // Get target container
    const container = document.getElementById(zone);
    if (!container) {
      this.logger.error(`[ListRenderer] ❌ Zone not found: ${zone}`);
      return null;
    }

    // Determine list tag based on style
    const listTag = style === 'number' ? 'ol' : 'ul';
    
    // Build CSS classes array
    const classes = ['zList'];
    
    // Add custom class if provided (from YAML)
    if (customClass) {
      classes.push(customClass);
    }

    // Create list element (using Layer 2 utility)
    const listElement = createElement(listTag, classes);
    
    // Render list items
    items.forEach(item => {
      // Support both string items and object items with content field
      const content = typeof item === 'string' ? item : (item.content || '');
      
      const li = createElement('li');
      li.textContent = content; // Use textContent for XSS safety
      
      listElement.appendChild(li);
    });
    
    // Apply attributes
    const attributes = {};
    
    // Apply indent as inline style (zTheme doesn't have indent utilities)
    // Each indent level = 1rem left margin
    if (indent > 0) {
      attributes.style = `margin-left: ${indent}rem;`;
    }
    
    if (Object.keys(attributes).length > 0) {
      setAttributes(listElement, attributes);
    }
    
    // Append to container
    container.appendChild(listElement);
    
    // Log success
    this.logger.log(`[ListRenderer] ✅ Rendered ${listTag} with ${items.length} items (indent: ${indent})`);
    
    return listElement;
  }
}

// ─────────────────────────────────────────────────────────────────
// Default Export
// ─────────────────────────────────────────────────────────────────
export default ListRenderer;

