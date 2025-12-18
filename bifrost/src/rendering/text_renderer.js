/**
 * ═══════════════════════════════════════════════════════════════
 * Text Renderer - Plain Text Display (Simplest Primitive)
 * ═══════════════════════════════════════════════════════════════
 * 
 * Renders plain text events from zCLI backend. This is the SIMPLEST
 * zDisplay event - pure content rendering with NO interactivity.
 * 
 * @module rendering/text_renderer
 * @layer 3
 * @pattern Strategy (single event type)
 * 
 * Philosophy:
 * - "Terminal first" - text is the foundation of all zCLI output
 * - Pure rendering (no WebSocket, no state, no side effects)
 * - Uses Layer 2 utilities exclusively (no inline logic)
 * 
 * Dependencies:
 * - Layer 2: dom_utils.js, ztheme_utils.js
 * 
 * Exports:
 * - TextRenderer: Class for rendering text events
 * 
 * Example:
 * ```javascript
 * import { TextRenderer } from './text_renderer.js';
 * 
 * const renderer = new TextRenderer(logger);
 * renderer.render({
 *   content: 'Hello, zCLI!',
 *   color: 'primary',
 *   indent: 1
 * }, 'zVaF');
 * ```
 */

// ─────────────────────────────────────────────────────────────────
// Imports
// ─────────────────────────────────────────────────────────────────
import { createElement, setAttributes } from '../utils/dom_utils.js';
import { getTextColorClass } from '../utils/ztheme_utils.js';

// ─────────────────────────────────────────────────────────────────
// Text Renderer Class
// ─────────────────────────────────────────────────────────────────

/**
 * TextRenderer - Renders plain text events
 * 
 * Handles the 'text' zDisplay event, which is the most basic
 * output primitive in zCLI. Renders a paragraph element with
 * optional color and indentation.
 */
export class TextRenderer {
  /**
   * Create a TextRenderer instance
   * @param {Object} logger - Logger instance for debugging
   */
  constructor(logger) {
    this.logger = logger || console;
    this.logger.log('[TextRenderer] ✅ Initialized');
  }

  /**
   * Render a text event
   * 
   * @param {Object} data - Text event data
   * @param {string} data.content - Text content to display
   * @param {string} [data.color] - Text color (primary, secondary, info, success, warning, error)
   * @param {number} [data.indent=0] - Indentation level (0 = no indent)
   * @param {string} [data.class] - Custom CSS class (optional)
   * @param {string} zone - Target DOM element ID
   * @returns {HTMLElement|null} Created paragraph element or null if failed
   * 
   * @example
   * renderer.render({ content: 'Hello!' }, 'zVaF');
   * renderer.render({ content: 'Success!', color: 'success' }, 'zVaF');
   * renderer.render({ content: 'Indented', indent: 2 }, 'zVaF');
   */
  render(data, zone) {
    const { content, color, indent = 0, class: customClass } = data;
    
    // Validate required parameters
    if (!content) {
      this.logger.error('[TextRenderer] ❌ Missing required parameter: content');
      return null;
    }
    
    // Get target container
    const container = document.getElementById(zone);
    if (!container) {
      this.logger.error(`[TextRenderer] ❌ Zone not found: ${zone}`);
      return null;
    }

    // Build CSS classes array
    const classes = [];
    
    // Add custom class if provided (from YAML)
    if (customClass) {
      classes.push(customClass);
    }
    
    // Add color class if provided (uses Layer 2 utility)
    if (color) {
      const colorClass = getTextColorClass(color);
      if (colorClass) {
        classes.push(colorClass);
      }
    }

    // Create paragraph element (using Layer 2 utility)
    const p = createElement('p', classes);
    p.textContent = content; // Use textContent for XSS safety
    
    // Apply attributes
    const attributes = {};
    
    // Apply indent as inline style (zTheme doesn't have indent utilities)
    // Each indent level = 1rem left margin
    if (indent > 0) {
      attributes.style = `margin-left: ${indent}rem;`;
    }
    
    if (Object.keys(attributes).length > 0) {
      setAttributes(p, attributes);
    }
    
    // Append to container
    container.appendChild(p);
    
    // Log success
    this.logger.log(`[TextRenderer] ✅ Rendered text (${content.length} chars, indent: ${indent})`);
    
    return p;
  }
}

// ─────────────────────────────────────────────────────────────────
// Default Export
// ─────────────────────────────────────────────────────────────────
export default TextRenderer;

