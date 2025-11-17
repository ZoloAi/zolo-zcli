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
        case 'table':
        case 'zTable':  // Backend sends 'zTable' (camelCase)
          element = this._renderTable(eventData);
          break;
        case 'json':
        case 'json_data':  // Backend sends 'json' or 'json_data'
          element = this._renderJSON(eventData);
          break;
        case 'progress_bar':
          element = this._renderProgressBar(eventData);
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
   * Render a table element (pure zTheme - NO Bootstrap!)
   * Uses zTheme's .zTable classes with automatic striping and hover effects
   * Implements client-side pagination (backend sends all rows + metadata)
   * @private
   */
  _renderTable(event) {
    // Extract table data and pagination metadata
    const title = event.title || '';
    const columns = event.columns || [];
    const allRows = event.rows || [];
    const limit = event.limit;  // Can be null/undefined (show all)
    const offset = event.offset || 0;
    
    // Apply pagination if limit is specified
    let rows = allRows;
    let hasMore = false;
    let moreCount = 0;
    
    if (limit !== null && limit !== undefined && limit > 0) {
      // Slice rows: from offset to offset+limit
      rows = allRows.slice(offset, offset + limit);
      hasMore = (offset + limit) < allRows.length;
      moreCount = allRows.length - (offset + limit);
    }
    
    // Create container wrapper
    const container = document.createElement('div');
    container.style.marginBottom = '1.5rem';
    
    // Apply indent as left margin (minimal inline style for dynamic indentation)
    if (event.indent && event.indent > 0) {
      container.style.marginLeft = `${event.indent}rem`;
    }
    
    // Add title with pagination info if provided
    if (title) {
      const titleElement = document.createElement('h4');
      
      // Show pagination range in title if limited
      if (limit !== null && limit !== undefined && limit > 0 && allRows.length > 0) {
        const showingStart = offset + 1;
        const showingEnd = Math.min(offset + rows.length, allRows.length);
        titleElement.textContent = `${title} (showing ${showingStart}-${showingEnd} of ${allRows.length})`;
      } else {
        titleElement.textContent = title;
      }
      
      titleElement.style.marginBottom = '0.75rem';
      titleElement.style.color = 'var(--color-darkgray)';
      container.appendChild(titleElement);
    }
    
    // Create table wrapper for responsiveness
    const tableWrapper = document.createElement('div');
    tableWrapper.className = 'zTable-responsive';
    
    // Create table
    const table = document.createElement('table');
    table.className = 'zTable zTable-striped zTable-hover zTable-bordered';
    
    // Create thead with columns
    if (columns.length > 0) {
      const thead = document.createElement('thead');
      const headerRow = document.createElement('tr');
      
      columns.forEach(column => {
        const th = document.createElement('th');
        th.textContent = column;
        headerRow.appendChild(th);
      });
      
      thead.appendChild(headerRow);
      table.appendChild(thead);
    }
    
    // Create tbody with (paginated) rows
    if (rows.length > 0) {
      const tbody = document.createElement('tbody');
      
      rows.forEach(row => {
        const tr = document.createElement('tr');
        
        // Handle both array and object rows
        if (Array.isArray(row)) {
          // Array row: [val1, val2, val3]
          row.forEach(value => {
            const td = document.createElement('td');
            td.innerHTML = this._sanitizeHTML(this._formatCellValue(value));
            tr.appendChild(td);
          });
        } else {
          // Object row: {col1: val1, col2: val2, ...}
          columns.forEach(column => {
            const td = document.createElement('td');
            const value = row[column];
            td.innerHTML = this._sanitizeHTML(this._formatCellValue(value));
            tr.appendChild(td);
          });
        }
        
        tbody.appendChild(tr);
      });
      
      table.appendChild(tbody);
    }
    
    tableWrapper.appendChild(table);
    container.appendChild(tableWrapper);
    
    // Add "... N more rows" footer if there are more rows
    if (hasMore && moreCount > 0) {
      const footer = document.createElement('p');
      footer.style.color = 'var(--color-info)';
      footer.style.marginTop = '0.5rem';
      footer.style.marginLeft = '1rem';
      footer.style.fontStyle = 'italic';
      footer.textContent = `... ${moreCount} more rows`;
      container.appendChild(footer);
    }
    
    return container;
  }

  /**
   * Format cell value for display (handles booleans, nulls, etc.)
   * @private
   */
  _formatCellValue(value) {
    if (value === null || value === undefined) {
      return '<span style="color: var(--color-gray);">—</span>';
    }
    if (typeof value === 'boolean') {
      return value 
        ? '<span style="color: var(--color-success);">✓</span>' 
        : '<span style="color: var(--color-error);">✗</span>';
    }
    return String(value);
  }

  /**
   * Render JSON data (pretty-printed)
   * @private
   */
  _renderJSON(event) {
    // Extract JSON data
    const data = event.data || event.content || {};
    
    // Create container
    const container = document.createElement('div');
    container.style.marginBottom = '1rem';
    
    // Apply indent as left margin
    if (event.indent && event.indent > 0) {
      container.style.marginLeft = `${event.indent}rem`;
    }
    
    // Create pre element for JSON
    const pre = document.createElement('pre');
    pre.style.backgroundColor = 'var(--color-base)';
    pre.style.border = '1px solid var(--color-gray)';
    pre.style.borderRadius = '4px';
    pre.style.padding = '1rem';
    pre.style.overflow = 'auto';
    pre.style.fontFamily = 'monospace';
    pre.style.fontSize = '0.9em';
    pre.style.color = 'var(--color-darkgray)';
    
    // Pretty-print JSON
    try {
      pre.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
      pre.textContent = String(data);
    }
    
    container.appendChild(pre);
    return container;
  }

  /**
   * Render progress bar (simple text-based for now)
   * TODO: Implement CSS animated progress bar
   * @private
   */
  _renderProgressBar(event) {
    // Extract progress data
    const current = event.current || 0;
    const total = event.total || 100;
    const label = event.label || '';
    const percentage = Math.round((current / total) * 100);
    
    // Create container
    const container = document.createElement('div');
    container.style.marginBottom = '0.5rem';
    
    // Apply indent as left margin
    if (event.indent && event.indent > 0) {
      container.style.marginLeft = `${event.indent}rem`;
    }
    
    // For now, render as text (CSS animation coming soon!)
    const text = document.createElement('span');
    text.textContent = `${label} [${percentage}%]`;
    text.style.color = 'var(--color-info)';
    text.style.fontFamily = 'monospace';
    
    container.appendChild(text);
    return container;
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

