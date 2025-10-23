/**
 * ═══════════════════════════════════════════════════════════════
 * Renderer Module - Auto-Rendering with zTheme
 * ═══════════════════════════════════════════════════════════════
 */

export class Renderer {
  constructor(logger) {
    this.logger = logger;
  }

  /**
   * Render data as a table with zTheme styling
   */
  renderTable(data, container, options = {}) {
    const element = this._getElement(container);
    if (!element) return;

    if (!Array.isArray(data) || data.length === 0) {
      element.innerHTML = '<p class="zEmpty">No data to display</p>';
      return;
    }

    const columns = Object.keys(data[0]);
    let html = '<table class="zTable zTable-striped zTable-hover">';
    
    // Table header
    html += '<thead><tr>';
    columns.forEach(col => {
      html += `<th>${this._formatColumnName(col)}</th>`;
    });
    html += '</tr></thead>';

    // Table body
    html += '<tbody>';
    data.forEach(row => {
      html += '<tr>';
      columns.forEach(col => {
        html += `<td>${this._escapeHtml(row[col])}</td>`;
      });
      html += '</tr>';
    });
    html += '</tbody></table>';

    element.innerHTML = html;
    this.logger.log('✅ Table rendered', { rows: data.length, columns: columns.length });
  }

  /**
   * Render a menu with buttons
   */
  renderMenu(items, container) {
    const element = this._getElement(container);
    if (!element) return;

    let html = '<div class="zMenu">';
    items.forEach((item, index) => {
      const icon = item.icon || '';
      const variant = item.variant || '';
      html += `<button class="zoloButton ${variant}" data-action="${index}">
        ${icon} ${item.label}
      </button>`;
    });
    html += '</div>';

    element.innerHTML = html;

    // Attach event listeners
    element.querySelectorAll('button[data-action]').forEach((btn, index) => {
      btn.addEventListener('click', () => {
        if (items[index].action) {
          items[index].action();
        }
      });
    });

    this.logger.log('✅ Menu rendered', { items: items.length });
  }

  /**
   * Render a form with zTheme styling
   */
  renderForm(fields, container, onSubmit) {
    const element = this._getElement(container);
    if (!element) return;

    let html = '<form class="zForm">';
    
    fields.forEach(field => {
      html += '<div class="zForm-group">';
      html += `<label for="${field.name}">${field.label}</label>`;
      
      if (field.type === 'textarea') {
        html += `<textarea id="${field.name}" name="${field.name}" 
                  class="zInput" ${field.required ? 'required' : ''}
                  placeholder="${field.placeholder || ''}"></textarea>`;
      } else {
        html += `<input type="${field.type || 'text'}" id="${field.name}" 
                 name="${field.name}" class="zInput" 
                 ${field.required ? 'required' : ''}
                 placeholder="${field.placeholder || ''}">`;
      }
      
      html += '</div>';
    });

    html += '<button type="submit" class="zoloButton zBtn-primary">Submit</button>';
    html += '</form>';

    element.innerHTML = html;

    // Attach submit handler
    const form = element.querySelector('form');
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());
      if (onSubmit) {
        onSubmit(data);
      }
    });

    this.logger.log('✅ Form rendered', { fields: fields.length });
  }

  /**
   * Render a message/alert
   */
  renderMessage(text, type = 'info', container, duration = 5000) {
    const element = this._getElement(container);
    if (!element) return;

    const typeClass = {
      'success': 'zAlert-success',
      'error': 'zAlert-danger',
      'warning': 'zAlert-warning',
      'info': 'zAlert-info'
    }[type] || 'zAlert-info';

    const msgDiv = document.createElement('div');
    msgDiv.className = `zAlert ${typeClass}`;
    msgDiv.textContent = text;

    element.insertBefore(msgDiv, element.firstChild);

    if (duration > 0) {
      setTimeout(() => msgDiv.remove(), duration);
    }

    this.logger.log('✅ Message rendered', { type, text });
  }

  /**
   * Get element from selector or element
   * @private
   */
  _getElement(container) {
    const element = typeof container === 'string' 
      ? document.querySelector(container) 
      : container;

    if (!element) {
      this.logger.log('❌ Container not found:', container);
    }

    return element;
  }

  /**
   * Format column name for display
   * @private
   */
  _formatColumnName(name) {
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  }

  /**
   * Escape HTML to prevent XSS
   * @private
   */
  _escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
  }
}

