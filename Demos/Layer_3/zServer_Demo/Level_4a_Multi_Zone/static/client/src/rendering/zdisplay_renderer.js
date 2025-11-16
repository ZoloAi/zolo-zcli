/**
 * ═══════════════════════════════════════════════════════════════
 * zDisplay Event Renderer - Convert zDisplay Events to HTML
 * ═══════════════════════════════════════════════════════════════
 * 
 * Renders zDisplay events from the Python backend into HTML elements.
 * Supports: header, text, list, error, warning, success, info
 * 
 * Special indent behavior:
 * - indent 0: Flush (clear the zone)
 * - indent 1: h1
 * - indent 2: h2
 * - indent 3: h3
 * - indent 4+: h4 (capped)
 */

export class ZDisplayRenderer {
  constructor(logger = null) {
    this.logger = logger || console;
    this.defaultZone = 'zui-content'; // Default target zone
  }

  /**
   * Render a zDisplay event to HTML
   * @param {Object} event - zDisplay event object
   * @param {string} targetZone - Target DOM element ID (default: 'zui-content')
   * @returns {HTMLElement|null} - Created element or null if flushed
   */
  render(event, targetZone = null) {
    try {
      const zone = targetZone || event.target || this.defaultZone;
      const container = document.getElementById(zone);
      
      if (!container) {
        this.logger.error(`[ZDisplayRenderer] Target zone not found: ${zone}`);
        return null;
      }

      // Handle indent 0 as flush (clear zone)
      if (event.indent === 0) {
        this._flush(container);
        this.logger.log(`[ZDisplayRenderer] Flushed zone: ${zone}`);
        return null;
      }

      // Route to appropriate renderer based on event type
      let element = null;
      
      switch (event.event) {
        case 'header':
          element = this._renderHeader(event);
          break;
        case 'text':
          element = this._renderText(event);
          break;
        case 'list':
          element = this._renderList(event);
          break;
        case 'error':
          element = this._renderAlert(event, 'danger');
          break;
        case 'warning':
          element = this._renderAlert(event, 'warning');
          break;
        case 'success':
          element = this._renderAlert(event, 'success');
          break;
        case 'info':
          element = this._renderAlert(event, 'info');
          break;
        default:
          this.logger.warn(`[ZDisplayRenderer] Unknown event type: ${event.event}`);
          element = this._renderText(event); // Fallback to text
      }

      if (element) {
        container.appendChild(element);
        this.logger.log(`[ZDisplayRenderer] Rendered ${event.event} to ${zone}`);
      }

      return element;
    } catch (error) {
      this.logger.error('[ZDisplayRenderer] Render error:', error);
      throw error; // Let error boundaries handle it
    }
  }

  /**
   * Flush (clear) a zone
   * @private
   */
  _flush(container) {
    container.innerHTML = '';
  }

  /**
   * Render a header element
   * @private
   */
  _renderHeader(event) {
    const indent = event.indent || 1;
    
    // Map indent to header level: indent 1 = h1, indent 2 = h2, etc.
    // Cap at h4 for indent 4+
    const level = Math.min(indent, 4);
    const tag = `h${level}`;
    
    const header = document.createElement(tag);
    header.innerHTML = this._sanitizeHTML(event.content);
    
    // Add Bootstrap classes for styling
    header.className = 'mt-3 mb-2';
    
    return header;
  }

  /**
   * Render a text element
   * @private
   */
  _renderText(event) {
    const p = document.createElement('p');
    p.innerHTML = this._sanitizeHTML(event.content);
    
    // Add Bootstrap classes
    p.className = 'mb-2';
    
    // Apply indent as left margin (1rem per indent level)
    if (event.indent && event.indent > 0) {
      p.style.marginLeft = `${event.indent}rem`;
    }
    
    return p;
  }

  /**
   * Render a list element
   * @private
   */
  _renderList(event) {
    const ul = document.createElement('ul');
    ul.className = 'mb-3';
    
    // Apply indent as left margin
    if (event.indent && event.indent > 0) {
      ul.style.marginLeft = `${event.indent}rem`;
    }
    
    // Render list items
    const items = event.items || [];
    items.forEach(item => {
      const li = document.createElement('li');
      
      // Support both string items and object items with content field
      const content = typeof item === 'string' ? item : (item.content || '');
      li.innerHTML = this._sanitizeHTML(content);
      
      ul.appendChild(li);
    });
    
    return ul;
  }

  /**
   * Render an alert element (error, warning, success, info)
   * @private
   */
  _renderAlert(event, type) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} mb-3`;
    alert.setAttribute('role', 'alert');
    
    // Add icon based on type
    const icons = {
      danger: '⚠️',
      warning: '⚡',
      success: '✅',
      info: 'ℹ️'
    };
    
    const icon = icons[type] || '';
    const content = this._sanitizeHTML(event.content);
    
    alert.innerHTML = icon ? `<strong>${icon}</strong> ${content}` : content;
    
    // Apply indent as left margin
    if (event.indent && event.indent > 0) {
      alert.style.marginLeft = `${event.indent}rem`;
    }
    
    return alert;
  }

  /**
   * Sanitize HTML to prevent XSS while allowing safe tags
   * @private
   */
  _sanitizeHTML(html) {
    if (!html) return '';
    
    // Allow common safe tags: <strong>, <em>, <code>, <a>, <br>
    // This is a basic sanitizer - for production, consider using DOMPurify
    const allowedTags = ['strong', 'em', 'code', 'a', 'br', 'span'];
    
    // Create a temporary div to parse HTML
    const temp = document.createElement('div');
    temp.innerHTML = html;
    
    // Remove script tags and event handlers
    const scripts = temp.querySelectorAll('script');
    scripts.forEach(script => script.remove());
    
    // Remove event handler attributes (onclick, onerror, etc.)
    const allElements = temp.querySelectorAll('*');
    allElements.forEach(el => {
      Array.from(el.attributes).forEach(attr => {
        if (attr.name.startsWith('on')) {
          el.removeAttribute(attr.name);
        }
      });
      
      // Remove elements not in allowed list (except text nodes)
      if (!allowedTags.includes(el.tagName.toLowerCase())) {
        // Keep the text content but remove the tag
        const textContent = el.textContent;
        const textNode = document.createTextNode(textContent);
        el.parentNode.replaceChild(textNode, el);
      }
    });
    
    return temp.innerHTML;
  }

  /**
   * Render multiple events in sequence
   * @param {Array} events - Array of zDisplay events
   * @param {string} targetZone - Target DOM element ID
   */
  renderBatch(events, targetZone = null) {
    if (!Array.isArray(events)) {
      this.logger.error('[ZDisplayRenderer] renderBatch expects an array');
      return;
    }
    
    events.forEach(event => {
      try {
        this.render(event, targetZone);
      } catch (error) {
        this.logger.error('[ZDisplayRenderer] Error rendering event:', error, event);
        // Continue with next event
      }
    });
  }

  /**
   * Clear all content from a zone
   * @param {string} targetZone - Target DOM element ID
   */
  clear(targetZone = null) {
    const zone = targetZone || this.defaultZone;
    const container = document.getElementById(zone);
    
    if (container) {
      this._flush(container);
      this.logger.log(`[ZDisplayRenderer] Cleared zone: ${zone}`);
    } else {
      this.logger.error(`[ZDisplayRenderer] Zone not found: ${zone}`);
    }
  }
}

