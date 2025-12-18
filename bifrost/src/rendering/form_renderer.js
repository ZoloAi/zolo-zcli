/**
 * FormRenderer - Async Form Rendering for zDialog in Bifrost Mode
 * 
 * This renderer handles the display and submission of zDialog forms in the browser.
 * Unlike Terminal mode (which collects input field-by-field), Bifrost displays the
 * entire form at once with all fields visible.
 * 
 * Key Differences from Terminal:
 * - Terminal: Blocking, field-by-field, synchronous
 * - Bifrost: Non-blocking, all-at-once, asynchronous
 * 
 * Flow:
 * 1. Backend sends zDialog event with form context
 * 2. FormRenderer displays full HTML form
 * 3. User fills and clicks Submit
 * 4. FormRenderer sends form_submit WebSocket message
 * 5. Backend validates and executes onSubmit
 * 6. Backend sends result back to frontend
 * 
 * @module FormRenderer
 */

export class FormRenderer {
  constructor(client) {
    this.client = client;
    this.logger = client.logger;
    this.currentForm = null;
  }

  /**
   * Render a zDialog form
   * @param {Object} eventData - Form context from backend
   * @param {string} eventData.title - Form title
   * @param {string} eventData.model - Schema model path (optional)
   * @param {Array} eventData.fields - Field definitions
   * @param {Object} eventData.onSubmit - Submit action to execute
   * @param {string} eventData._dialogId - Unique form identifier
   */
  renderForm(eventData) {
    console.log('[FormRenderer] 🎨 RENDERING FORM - Called with eventData:', eventData);
    
    const {
      title = 'Form',
      model,
      fields = [],
      onSubmit,
      _dialogId
    } = eventData;

    console.log('[FormRenderer] ✅ Extracted form data:', { 
      title, 
      model, 
      fieldsCount: fields.length, 
      fields,
      hasOnSubmit: !!onSubmit,
      _dialogId 
    });

    this.logger.log('[FormRenderer] Rendering form:', { title, fields: fields.length, _dialogId });

    // Store current form context for submission
    this.currentForm = {
      _dialogId,
      model,
      onSubmit,
      fields
    };

    // Create form container
    const formContainer = document.createElement('div');
    formContainer.className = 'zDialog-container zCard zp-4';
    formContainer.setAttribute('data-dialog-id', _dialogId);

    // Form title
    if (title) {
      const titleElement = document.createElement('h2');
      titleElement.className = 'zDialog-title zCard-title zmb-3';
      titleElement.textContent = title;
      formContainer.appendChild(titleElement);
    }

    // Create HTML form element
    const form = document.createElement('form');
    form.className = 'zDialog-form'; // Custom class for optional styling (not required by JS)
    form.setAttribute('data-dialog-id', _dialogId);

    // Render fields
    fields.forEach(fieldDef => {
      const fieldGroup = this._createFieldGroup(fieldDef);
      form.appendChild(fieldGroup);
    });

    // Error display area (hidden by default)
    // Note: 'zDialog-errors' is required by JS for querySelector, rest are zTheme styling
    const errorContainer = document.createElement('div');
    errorContainer.className = 'zDialog-errors zAlert zAlert-danger zmt-3';
    errorContainer.style.display = 'none';
    form.appendChild(errorContainer);

    // Submit button
    const submitButton = document.createElement('button');
    submitButton.type = 'submit';
    submitButton.className = 'zBtn zBtn-primary zmt-3';
    submitButton.textContent = 'Submit';
    form.appendChild(submitButton);

    // Handle form submission
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      this._handleSubmit(form, _dialogId);
    });

    formContainer.appendChild(form);
    return formContainer;
  }

  /**
   * Create a form field group (label + input)
   * @private
   */
  _createFieldGroup(fieldDef) {
    // Handle both string and object field definitions
    const fieldName = typeof fieldDef === 'string' ? fieldDef : fieldDef.name;
    
    // Auto-detect field type from field name if not explicitly provided
    let fieldType = 'text';
    if (typeof fieldDef === 'object' && fieldDef.type) {
      // Explicit type provided
      fieldType = fieldDef.type;
    } else {
      // Auto-detect based on field name
      const lowerName = fieldName.toLowerCase();
      if (lowerName === 'password' || lowerName.includes('password')) {
        fieldType = 'password';
      } else if (lowerName === 'email' || lowerName.includes('email')) {
        fieldType = 'email';
      } else if (lowerName === 'phone' || lowerName === 'tel' || lowerName.includes('phone')) {
        fieldType = 'tel';
      }
    }
    
    const fieldLabel = typeof fieldDef === 'object' ? (fieldDef.label || fieldName) : fieldName;
    const required = typeof fieldDef === 'object' ? (fieldDef.required !== false) : true;

    const fieldGroup = document.createElement('div');
    fieldGroup.className = 'zmb-3'; // zTheme margin-bottom spacing

    // Label
    const label = document.createElement('label');
    label.className = 'zLabel'; // zTheme form label
    label.textContent = this._formatLabel(fieldLabel);
    if (required) {
      const requiredMark = document.createElement('span');
      requiredMark.className = 'zText-danger';
      requiredMark.textContent = ' *';
      label.appendChild(requiredMark);
    }
    fieldGroup.appendChild(label);

    // Input field
    const input = this._createInput(fieldName, fieldType, required);
    fieldGroup.appendChild(input);

    return fieldGroup;
  }

  /**
   * Create an input element based on field type
   * @private
   */
  _createInput(fieldName, fieldType, required) {
    let input;

    if (fieldType === 'textarea') {
      input = document.createElement('textarea');
      input.rows = 4;
    } else {
      input = document.createElement('input');
      input.type = fieldType === 'password' ? 'password' : 'text';
      
      // Apply HTML5 validation attributes based on type
      if (fieldType === 'email') {
        input.type = 'email';
      } else if (fieldType === 'number') {
        input.type = 'number';
      } else if (fieldType === 'tel' || fieldType === 'phone') {
        input.type = 'tel';
      }
    }

    input.name = fieldName;
    input.className = 'zInput'; // zTheme form input
    input.required = required;
    input.placeholder = `Enter ${this._formatLabel(fieldName).toLowerCase()}`;

    return input;
  }

  /**
   * Format field name to human-readable label
   * @private
   */
  _formatLabel(fieldName) {
    // Convert snake_case or camelCase to Title Case
    return fieldName
      .replace(/_/g, ' ')
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, str => str.toUpperCase())
      .trim();
  }

  /**
   * Handle form submission
   * @private
   */
  async _handleSubmit(formElement, dialogId) {
    this.logger.log('[FormRenderer] Form submit triggered:', dialogId);

    // Clear previous errors
    const errorContainer = formElement.querySelector('.zDialog-errors');
    if (errorContainer) {
      errorContainer.style.display = 'none';
      errorContainer.innerHTML = '';
    }

    // Collect form data
    const formData = new FormData(formElement);
    const data = {};
    for (const [key, value] of formData.entries()) {
      data[key] = value;
    }

    this.logger.log('[FormRenderer] Collected form data:', Object.keys(data));
    this.logger.log('[FormRenderer] 📤 Sending form_submit event to backend');

    // Disable submit button during submission
    const submitButton = formElement.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Submitting...';

    try {
      // Send form submission to backend via proper message handler
      const response = await this.client.send({
        event: 'form_submit',
        dialogId: dialogId,
        data: data,
        onSubmit: this.currentForm.onSubmit,
        model: this.currentForm.model
      });

      this.logger.log('[FormRenderer] Submission response:', response);

      // Handle response
      if (response.success) {
        this._handleSuccess(formElement, response);
      } else {
        this._handleError(formElement, response);
      }

    } catch (error) {
      this.logger.error('[FormRenderer] Submission error:', error);
      this._handleError(formElement, {
        success: false,
        message: 'Failed to submit form. Please try again.',
        errors: [error.message]
      });
    } finally {
      // Re-enable submit button
      submitButton.disabled = false;
      submitButton.textContent = originalText;
    }
  }

  /**
   * Handle successful form submission
   * @private
   */
  _handleSuccess(formElement, response) {
    this.logger.log('[FormRenderer] Form submission successful');

    // Display success message
    const successContainer = document.createElement('div');
    successContainer.className = 'zAlert zAlert-success zmt-3';
    successContainer.innerHTML = `
      <strong>Success!</strong> ${response.message || 'Form submitted successfully.'}
    `;

    // Replace form with success message
    const formContainer = formElement.closest('.zDialog-container');
    if (formContainer) {
      formContainer.innerHTML = '';
      formContainer.appendChild(successContainer);
    }

    // Refresh navbar after successful submission (e.g., after login)
    // This ensures RBAC-filtered navbar items are updated
    if (this.client && typeof this.client._fetchAndPopulateNavBar === 'function') {
      this.logger.log('[FormRenderer] ✅ Form success - refreshing navbar for RBAC update');
      this.client._fetchAndPopulateNavBar().catch(err => {
        this.logger.error('[FormRenderer] Failed to refresh navbar:', err);
      });
    }

    // Clear current form context
    this.currentForm = null;
  }

  /**
   * Handle form submission error
   * @private
   */
  _handleError(formElement, response) {
    this.logger.error('[FormRenderer] Form submission failed:', response);

    const errorContainer = formElement.querySelector('.zDialog-errors');
    if (errorContainer) {
      errorContainer.style.display = 'block';
      
      const errorList = document.createElement('ul');
      errorList.className = 'zmb-0';
      
      // Display validation errors
      if (response.errors && Array.isArray(response.errors)) {
        response.errors.forEach(error => {
          const errorItem = document.createElement('li');
          errorItem.textContent = error;
          errorList.appendChild(errorItem);
        });
      } else {
        const errorItem = document.createElement('li');
        errorItem.textContent = response.message || 'Validation failed. Please check your input.';
        errorList.appendChild(errorItem);
      }
      
      errorContainer.innerHTML = '<strong>Error:</strong>';
      errorContainer.appendChild(errorList);
    }

    // Scroll to errors
    errorContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}
