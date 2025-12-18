/**
 * TypographyRenderer - Modular Typography Rendering for zDisplay Events
 * =====================================================================
 * 
 * Handles all text and heading rendering with semantic HTML and zTheme styling.
 * 
 * Features:
 * - Semantic heading levels (h1-h6) based on indent
 * - zTheme typography classes (.zDisplay-header, .zDisplay-h1, etc.)
 * - Color variants (primary, secondary, success, warning, error, info)
 * - Responsive text rendering with proper spacing
 * 
 * Architecture:
 * - Part of the client-side rendering module system
 * - Used by BifrostClient for zDisplay event rendering
 * - Lazy-loaded when needed
 * 
 * @module TypographyRenderer
 */

export default class TypographyRenderer {
  /**
   * Create a TypographyRenderer instance
   * @param {Object} logger - Logger instance for debugging
   */
  constructor(logger) {
    this.logger = logger || console;
    this.logger.log('[TypographyRenderer] Initialized');
  }

  /**
   * Render a header element with semantic heading level
   * 
   * Maps backend indent to semantic HTML heading level:
   * - indent 0 → h1
   * - indent 1 → h1
   * - indent 2 → h2
   * - indent 3 → h3
   * - indent 4 → h4
   * - indent 5 → h5
   * - indent 6 → h6
   * 
   * @param {Object} eventData - Header event data
   * @param {string} eventData.label - Header text content (Python backend sends 'label' for headers)
   * @param {string} [eventData.color] - Color variant (PRIMARY, SECONDARY, etc.)
   * @param {number} [eventData.indent=0] - Backend indent level (maps to heading level)
   * @param {string} [eventData.style] - Header style (full, single, wave)
   * @returns {HTMLElement} Heading element (h1-h6)
   */
  renderHeader(eventData) {
    // Python sends 'label' field for headers (not 'content')
    const label = eventData.label || eventData.content || '';
    const color = eventData.color || null;
    const indent = eventData.indent !== undefined ? eventData.indent : 0;
    const style = eventData.style || 'full';
    const customClass = eventData.class || null;

    // Map indent to semantic heading level
    // indent 0 or 1 → h1, indent 2 → h2, indent 3 → h3, etc.
    let headingLevel = indent === 0 ? 1 : indent;
    headingLevel = Math.max(1, Math.min(6, headingLevel)); // Clamp to 1-6
    
    // Create semantic HTML heading element
    const element = document.createElement(`h${headingLevel}`);
    element.textContent = label;
    
    // Add zTheme typography classes
    element.className = `zDisplay-header zDisplay-h${headingLevel}`;
    
    // Apply custom classes if provided (from YAML `class` parameter)
    if (customClass) {
      element.className += ` ${customClass}`;
    }
    
    // Apply color variant class
    if (color) {
      const colorClass = this._getColorClass(color);
      if (colorClass) {
        element.classList.add(colorClass);
      }
    }
    
    // Add data attributes for debugging/styling
    element.setAttribute('data-heading-level', headingLevel);
    element.setAttribute('data-indent', indent);
    element.setAttribute('data-style', style);
    
    this.logger.log(`[TypographyRenderer] Rendered <h${headingLevel}> (indent: ${indent}) with color: ${color || 'default'}`);
    
    return element;
  }

  /**
   * Render a text paragraph element
   * 
   * @param {Object} eventData - Text event data
   * @param {string} eventData.content - Text content
   * @param {string} [eventData.color] - Color variant
   * @param {number} [eventData.indent=0] - Visual indentation level
   * @returns {HTMLElement} Paragraph element
   */
  renderText(eventData) {
    const {
      content = '',
      color = null,
      indent = 0,
      class: customClass = null  // New: Accept custom CSS classes from YAML
    } = eventData;

    const element = document.createElement('p');
    element.textContent = content;
    element.className = 'zDisplay-text';
    
    // Apply custom classes if provided (from YAML `class` parameter)
    if (customClass) {
      element.className += ` ${customClass}`;
    }
    
    // Apply color variant class
    if (color) {
      const colorClass = this._getColorClass(color);
      if (colorClass) {
        element.classList.add(colorClass);
      }
    }
    
    // Apply visual indentation
    if (indent > 0) {
      element.style.marginLeft = `${indent * 20}px`;
    }
    
    return element;
  }

  /**
   * Render a divider element
   * 
   * @param {Object} [eventData={}] - Optional divider styling data
   * @returns {HTMLElement} HR element
   */
  renderDivider(eventData = {}) {
    const element = document.createElement('hr');
    element.className = 'zDisplay-divider';
    
    // Optional: Add style variants
    if (eventData.style) {
      element.setAttribute('data-style', eventData.style);
    }
    
    return element;
  }

  /**
   * Get zTheme color class from color name
   * 
   * @private
   * @param {string} color - Color name (case-insensitive)
   * @returns {string|null} zTheme color class or null
   */
  _getColorClass(color) {
    const colorMap = {
      'primary': 'zText-primary',
      'secondary': 'zText-secondary',
      'success': 'zText-success',
      'zsuccess': 'zText-success',
      'warning': 'zText-warning',
      'zwarning': 'zText-warning',
      'error': 'zText-danger',
      'zerror': 'zText-danger',
      'danger': 'zText-danger',
      'info': 'zText-info',
      'zinfo': 'zText-info',
      'muted': 'zText-muted'
    };
    
    const normalizedColor = color.toLowerCase();
    return colorMap[normalizedColor] || null;
  }

  /**
   * Render a heading with automatic sizing based on context
   * (Future: Could analyze document structure for automatic sizing)
   * 
   * @param {string} label - Heading text
   * @param {Object} [options={}] - Rendering options
   * @returns {HTMLElement} Heading element
   */
  renderAutoHeading(label, options = {}) {
    // For now, delegate to renderHeader with defaults
    // Future: Could implement automatic level detection based on document structure
    return this.renderHeader({
      label,
      level: options.level || 2,
      color: options.color || null,
      indent: options.indent || 0
    });
  }
}
