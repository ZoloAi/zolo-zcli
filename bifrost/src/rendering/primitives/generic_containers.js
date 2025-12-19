/**
 * ═══════════════════════════════════════════════════════════════
 * Generic Containers - RAWEST HTML Primitives (Block + Inline)
 * ═══════════════════════════════════════════════════════════════
 * 
 * The most atomic building blocks: <div> and <span>.
 * These are semantic-free containers used purely for layout and grouping.
 * 
 * @module rendering/generic_containers
 * @layer 0.0 (RAWEST - true bottom)
 * @pattern Pure Factory Functions
 * 
 * Philosophy:
 * - Block-level (<div>) for layout/structure
 * - Inline (<span>) for phrasing content
 * - NO styling, NO classes (dress up later)
 * - Accept raw HTML attributes only
 * 
 * Dependencies:
 * - utils/dom_utils.js (createElement, setAttributes)
 * 
 * Exports:
 * - createDiv(attributes) → HTMLDivElement
 * - createSpan(attributes) → HTMLSpanElement
 * 
 * Example:
 * ```javascript
 * import { createDiv, createSpan } from './generic_containers.js';
 * 
 * // Raw containers
 * const container = createDiv({ id: 'main' });
 * const badge = createSpan({ class: 'badge', 'data-count': '5' });
 * 
 * // Dress up later with utilities
 * container.classList.add('zContainer', 'zP-3');
 * badge.classList.add('zBadge', 'zBadge-primary');
 * ```
 */

import { createElement, setAttributes } from '../../utils/dom_utils.js';

// ─────────────────────────────────────────────────────────────────
// Block-Level Container
// ─────────────────────────────────────────────────────────────────

/**
 * Create a <div> element (block-level container)
 * 
 * The most generic block-level container, used for:
 * - Layout structure (rows, columns, grids)
 * - Grouping related content
 * - Wrapping components
 * - Semantic-free containers (when section/article/etc. don't apply)
 * 
 * @param {Object} [attributes={}] - HTML attributes (id, class, data-*, aria-*, etc.)
 * @returns {HTMLDivElement} The created div element
 * 
 * @example
 * // Basic div (no attributes)
 * const wrapper = createDiv();
 * 
 * // Div with ID and class
 * const card = createDiv({ id: 'card-1', class: 'card' });
 * 
 * // Div with data attributes
 * const item = createDiv({ 'data-item-id': '123', 'data-type': 'product' });
 * 
 * // Div with ARIA attributes for accessibility
 * const alert = createDiv({ role: 'alert', 'aria-live': 'polite' });
 */
export function createDiv(attributes = {}) {
  const div = createElement('div');
  
  if (Object.keys(attributes).length > 0) {
    setAttributes(div, attributes);
  }
  
  return div;
}

// ─────────────────────────────────────────────────────────────────
// Inline Container
// ─────────────────────────────────────────────────────────────────

/**
 * Create a <span> element (inline container)
 * 
 * The most generic inline container, used for:
 * - Wrapping phrasing content (text, icons)
 * - Badges, labels, tags
 * - Inline styling/scripting hooks
 * - Semantic-free inline containers (when <strong>, <em>, etc. don't apply)
 * 
 * @param {Object} [attributes={}] - HTML attributes (id, class, data-*, aria-*, etc.)
 * @returns {HTMLSpanElement} The created span element
 * 
 * @example
 * // Basic span (no attributes)
 * const highlight = createSpan();
 * highlight.textContent = 'Important';
 * 
 * // Span with class (for styling hook)
 * const badge = createSpan({ class: 'badge' });
 * 
 * // Span with data attributes
 * const tag = createSpan({ 'data-tag-id': '5', 'data-color': 'blue' });
 * 
 * // Span for icon wrapper
 * const iconWrapper = createSpan({ class: 'icon', 'aria-hidden': 'true' });
 */
export function createSpan(attributes = {}) {
  const span = createElement('span');
  
  if (Object.keys(attributes).length > 0) {
    setAttributes(span, attributes);
  }
  
  return span;
}

// ─────────────────────────────────────────────────────────────────
// Default Export (for convenience)
// ─────────────────────────────────────────────────────────────────
export default {
  createDiv,
  createSpan
};

