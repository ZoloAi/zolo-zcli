/**
 * TypographyRenderer - Renders text, headers, and dividers
 * 
 * Uses typography primitives for DOM creation
 */

import { createHeading, createParagraph } from './primitives/typography_primitives.js';

export class TypographyRenderer {
  constructor(logger) {
    this.logger = logger;
  }

  /**
   * Render text element
   * @param {Object} eventData - Event data with content, color, indent, etc.
   * @returns {HTMLElement}
   */
  renderText(eventData) {
    const classes = this._buildTextClasses(eventData);
    const p = createParagraph(classes ? { class: classes } : {});
    p.textContent = eventData.content || '';
    return p;
  }

  /**
   * Render header element
   * @param {Object} eventData - Event data with label, level, etc.
   * @returns {HTMLElement}
   */
  renderHeader(eventData) {
    const level = eventData.level || 1;
    const classes = this._buildTextClasses(eventData);
    const h = createHeading(level, classes ? { class: classes } : {});
    h.textContent = eventData.label || eventData.content || '';
    return h;
  }

  /**
   * Render divider element
   * @param {Object} eventData - Event data
   * @returns {HTMLElement}
   */
  renderDivider(eventData) {
    const hr = document.createElement('hr');
    const classes = ['zDivider'];
    if (eventData.color) classes.push(`zBorder-${eventData.color}`);
    hr.className = classes.join(' ');
    return hr;
  }

  /**
   * Build text classes from event data
   * @private
   */
  _buildTextClasses(eventData) {
    const classes = [];
    
    // Color: normalize to lowercase for zTheme consistency
    if (eventData.color) {
      const color = eventData.color.toLowerCase();
      classes.push(`zText-${color}`);
    }
    
    // Indent: use margin-start (zms) for text indentation
    if (eventData.indent) {
      classes.push(`zms-${eventData.indent}`);
    }
    
    return classes.length > 0 ? classes.join(' ') : '';
  }
}

export default TypographyRenderer;

