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
    this.defaultZone = 'zVaF'; // Default zCLI container (zView and Function)
  }

  /**
   * Render a zDisplay event to HTML
   * @param {Object} event - zDisplay event object
   * @param {string} targetZone - Target DOM element ID (default: 'zVaF')
   * @returns {HTMLElement|null} - Created element or null if flushed
   */
  render(event, targetZone = null) {
    try {
      // Normalize event format (support both old and new formats)
      // Old: {event: 'success', content: '...', indent: 0}
      // New: {display_event: 'success', data: {content: '...', indent: 0}}
      const eventType = event.display_event || event.event;
      const eventData = event.data || event;  // Use data if present, otherwise use event itself
      
      const zone = targetZone || eventData.target || this.defaultZone;
      const container = document.getElementById(zone);
      
      if (!container) {
        this.logger.error(`[ZDisplayRenderer] Target zone not found: ${zone}`);
        return null;
      }

      // Handle explicit flush event (not just indent 0)
      if (eventType === 'flush' || eventData.flush === true) {
        this._flush(container);
        this.logger.log(`[ZDisplayRenderer] Flushed zone: ${zone}`);
        return null;
      }

      // Route to appropriate renderer based on event type
      let element = null;
      
      switch (eventType) {
        case 'header':
          element = this._renderHeader(eventData);
          break;
        case 'text':
          element = this._renderText(eventData);
          break;
        case 'list':
          element = this._renderList(eventData);
          break;
        case 'error':
          element = this._renderAlert(eventData, 'danger');
          break;
        case 'warning':
          element = this._renderAlert(eventData, 'warning');
          break;
        case 'success':
          element = this._renderAlert(eventData, 'success');
          break;
        case 'info':
          element = this._renderAlert(eventData, 'info');
          break;
        default:
          this.logger.warn(`[ZDisplayRenderer] Unknown event type: ${eventType}`);
          element = this._renderText(eventData); // Fallback to text
      }

      if (element) {
        container.appendChild(element);
        this.logger.log(`[ZDisplayRenderer] Rendered ${eventType} to ${zone}`);
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
   * Render a header element (zTheme pure - NO Bootstrap!)
   * indent=0 → HERO (centered, large, prominent)
   * indent=1-6 → h1-h6 (semantic HTML headers)
   * @private
   */
  _renderHeader(event) {
    const indent = event.indent !== undefined ? event.indent : 1;
    
    // Python sends 'label' field for headers (not 'content')
    const content = event.label || event.content || '';
    
    // indent=0 → HERO header (special centered title)
    if (indent === 0) {
      const hero = document.createElement('div');
      hero.className = 'zHero';
      hero.innerHTML = this._sanitizeHTML(content);
      return hero;
    }
    
    // indent=1-6 → h1-h6 (semantic HTML headers)
    const level = Math.min(indent, 6);
    const tag = `h${level}`;
    
    const header = document.createElement(tag);
    header.innerHTML = this._sanitizeHTML(content);
    
    // Pure zTheme - all styling handled by zTypography.css (h1-h6 rules)
    // No inline styles needed! 🎨
    
    return header;
  }

  /**
   * Render a text element (pure zTheme - NO Bootstrap!)
   * @private
   */
  _renderText(event) {
    const p = document.createElement('p');
    p.innerHTML = this._sanitizeHTML(event.content);
    
    // Minimal inline styling (margin-bottom for spacing)
    p.style.marginBottom = '0.5rem';
    
    // Apply indent as left margin (1rem per indent level)
    if (event.indent && event.indent > 0) {
      p.style.marginLeft = `${event.indent}rem`;
    }
    
    return p;
  }

  /**
   * Render a list element (pure zTheme - NO Bootstrap!)
   * @private
   */
  _renderList(event) {
    const ul = document.createElement('ul');
    ul.className = 'zList';
    
    // Apply indent as left margin (minimal inline style for dynamic indentation)
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
   * Render a signal alert (error, warning, success, info)
   * Toast-style dismissible alerts - pure zTheme, beats Bootstrap! 🎨
   * Auto-fades after 5 seconds, but can be manually dismissed with ×
   * @private
   */
  _renderAlert(event, type) {
    const signal = document.createElement('div');
    
    // Map type to zSignal classes (Bootstrap compatibility layer)
    const classMap = {
      danger: 'error',    // danger → zSignal-error
      warning: 'warning', // warning → zSignal-warning
      success: 'success', // success → zSignal-success
      info: 'info'        // info → zSignal-info
    };
    
    const signalType = classMap[type] || 'info';
    signal.className = `zSignal zSignal-${signalType}`;
    signal.setAttribute('role', 'alert');
    
    // Add icon based on type
    const icons = {
      danger: '⚠️',
      warning: '⚡',
      success: '✅',
      info: 'ℹ️'
    };
    
    const icon = icons[type] || '';
    const content = this._sanitizeHTML(event.content);
    
    // Create content wrapper
    const contentDiv = document.createElement('div');
    contentDiv.innerHTML = icon ? `<strong style="margin-right: 0.5rem;">${icon}</strong>${content}` : content;
    
    // Create close button (dismissible like Bootstrap)
    const closeBtn = document.createElement('button');
    closeBtn.className = 'close';
    closeBtn.innerHTML = '×';
    closeBtn.setAttribute('aria-label', 'Close');
    closeBtn.onclick = () => {
      signal.style.animation = 'fadeOut 0.3s ease-out';
      setTimeout(() => signal.remove(), 300);
    };
    
    // Append content and close button
    signal.appendChild(contentDiv);
    signal.appendChild(closeBtn);
    
    // Apply indent as left margin (minimal inline style for dynamic indentation)
    if (event.indent && event.indent > 0) {
      signal.style.marginLeft = `${event.indent}rem`;
    }
    
    // Auto-dismiss after 5 seconds with fade-out animation
    setTimeout(() => {
      if (signal.parentElement) {  // Only fade if still in DOM (not manually closed)
        signal.style.animation = 'fadeOut 0.5s ease-out';
        setTimeout(() => signal.remove(), 500);
      }
    }, 5000);
    
    return signal;
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

