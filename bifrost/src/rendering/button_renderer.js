/**
 * ═══════════════════════════════════════════════════════════════
 * Button Renderer - Interactive Button Input Events
 * ═══════════════════════════════════════════════════════════════
 * 
 * Terminal-First Design (Refactored Micro-Step 8):
 * - Backend sends semantic color (danger, success, warning, etc.)
 * - Terminal displays colored prompts matching semantic meaning
 * - Bifrost renders styled buttons with same semantic colors
 * 
 * Renders button input events from zCLI backend. Creates interactive
 * button elements with zTheme styling and WebSocket response handling.
 * 
 * @module rendering/button_renderer
 * @layer 3
 * @pattern Strategy (single event type)
 * 
 * Dependencies:
 * - Layer 0: primitives/interactive_primitives.js (createButton)
 * - Layer 2: dom_utils.js (createElement, replaceElement)
 * 
 * Exports:
 * - ButtonRenderer: Class for rendering button events
 * 
 * Example:
 * ```javascript
 * import ButtonRenderer from './button_renderer.js';
 * 
 * const renderer = new ButtonRenderer(logger, client);
 * renderer.render({
 *   label: 'Submit',
 *   action: 'process_form',
 *   color: 'primary',
 *   requestId: '123'
 * }, 'zVaF');
 * ```
 */

// ─────────────────────────────────────────────────────────────────
// Imports
// ─────────────────────────────────────────────────────────────────
import { createButton } from './primitives/interactive_primitives.js';
import { applyColorScheme, getBackgroundClass } from '../utils/color_utils.js';
import { 
  createElement, 
  appendChildren,
  replaceElement
} from '../utils/dom_utils.js';

// ─────────────────────────────────────────────────────────────────
// Main Implementation
// ─────────────────────────────────────────────────────────────────

/**
 * Renders button input events for zDisplay
 * 
 * Handles the 'button' event type from zCLI backend, creating
 * interactive button elements with zTheme styling and WebSocket
 * response handling.
 * 
 * @class
 */
export default class ButtonRenderer {
  /**
   * Create a button renderer
   * @param {Object} logger - Logger instance for debugging
   * @param {Object} client - BifrostClient instance for sending responses
   */
  constructor(logger, client = null) {
    if (!logger) {
      throw new Error('[ButtonRenderer] logger is required');
    }
    
    this.logger = logger;
    this.client = client;
    this.defaultZone = 'zVaF-content';
  }

  /**
   * Render a button input request
   * 
   * Terminal-First Design:
   * - Backend sends semantic color (danger, success, warning, primary, info, secondary)
   * - Bifrost renders button with matching zTheme color class
   * 
   * @param {Object} data - Button configuration
   * @param {string} data.label - Button label text (or 'prompt')
   * @param {string} data.action - Action identifier (or '#' for placeholder)
   * @param {string} [data.color='primary'] - Button semantic color
   *   - primary: Default action (blue)
   *   - danger: Destructive action (red)
   *   - success: Positive action (green)
   *   - warning: Cautious action (yellow)
   *   - info: Informational (cyan)
   *   - secondary: Neutral (gray)
   * @param {string} data.requestId - Request ID for response correlation
   * @param {string} zone - Target DOM element ID
   * @returns {HTMLElement|null} Created button container, or null if zone not found
   */
  render(data, zone) {
    // Validate inputs
    if (!data) {
      this.logger.error('[ButtonRenderer] data is required');
      return null;
    }

    // Extract data (support both direct and nested formats)
    const requestId = data.requestId || data.data?.requestId;
    const label = data.label || data.prompt || data.data?.prompt || 'Click Me';
    const action = data.action || data.data?.action || null;
    const color = data.color || data.data?.color || 'primary';
    
    // Resolve target zone
    const targetZone = zone || data.target || this.defaultZone;
    const container = document.getElementById(targetZone);
    
    if (!container) {
      this.logger.error(`[ButtonRenderer] Zone not found: ${targetZone}`);
      return null;
    }

    this.logger.log('[ButtonRenderer] Rendering button:', { requestId, label, action, color });

    // Create button container
    const buttonContainer = this._createButtonContainer();
    
    // Create primary button with semantic color
    const primaryButton = this._createButton(label, color);
    this._attachClickHandler(primaryButton, requestId, label, true, buttonContainer);
    
    // ✅ NO cancel button in Bifrost! (Terminal-first: y/n, GUI: click or ignore)
    // In terminal, button is y/n prompt. In GUI, button is click or don't click.
    // We're asynchronous - user can just ignore the button.
    
    // Append button to container
    buttonContainer.appendChild(primaryButton);
    
    // Add to page
    container.appendChild(buttonContainer);
    
    this.logger.log('[ButtonRenderer] Button rendered successfully');
    return buttonContainer;
  }

  /**
   * Create button container element
   * @private
   * @returns {HTMLElement} Container div
   */
  _createButtonContainer() {
    // ✅ Use ONLY zTheme classes - NO inline styles!
    const container = createElement('div', ['zD-flex', 'zFlex-items-center', 'zGap-3', 'zmy-3', 'zp-3']);
    
    return container;
  }

  /**
   * Create a single button element from primitives + color utilities
   * 
   * Architecture:
   * - Layer 0.0: createButton() - Raw <button> element
   * - Layer 0.3: applyColorScheme() - Semantic colors
   * - Layer 3 (here): Compose primitives + add button styling
   * 
   * Terminal-First Design:
   * - Uses semantic color from backend (matches terminal prompt color)
   * - Composes from raw primitives instead of pre-built zTheme components
   * 
   * @private
   * @param {string} label - Button text
   * @param {string} color - Button semantic color (primary, danger, success, warning, info, secondary)
   * @returns {HTMLElement} Button element
   */
  _createButton(label, color) {
    this.logger.log(`[ButtonRenderer] Creating button "${label}" with color: ${color}`);
    
    // ✅ Layer 0.0: Create raw button primitive
    const button = createButton('button', {
      class: 'zBtn' // Base button styling only (padding, border, etc.)
    });
    
    button.textContent = label;
    
    // ✅ Layer 0.3: Apply semantic color using color utilities
    // Map zCLI semantic colors to appropriate zTheme background classes
    const colorMap = {
      'primary': 'primary',     // Green (zCLI brand)
      'danger': 'error',        // Red (use error, not danger)
      'success': 'success',     // Green (darker)
      'warning': 'warning',     // Orange
      'info': 'info',           // Blue
      'secondary': 'secondary'  // Purple
    };
    
    const bgColor = colorMap[color] || 'primary';
    const bgClass = getBackgroundClass(bgColor);
    
    if (bgClass) {
      button.classList.add(bgClass);
      this.logger.log(`[ButtonRenderer] Applied color class: ${bgClass}`);
    }
    
    // ✅ Proper composition: Primitive + Color Utility = Styled Button
    // NO pre-built component classes like .zBtn-primary
    
    return button;
  }

  /**
   * Attach click handler to button
   * @private
   * @param {HTMLElement} button - Button element
   * @param {string} requestId - Request ID for response
   * @param {string} originalLabel - Original button label
   * @param {boolean} value - Response value (true for primary, false for cancel)
   * @param {HTMLElement} container - Button container to replace
   */
  _attachClickHandler(button, requestId, originalLabel, value, container) {
    button.addEventListener('click', () => {
      this.logger.log(`[ButtonRenderer] Button clicked: ${button.textContent} (value: ${value})`);
      
      // Send response to backend via WebSocket
      this._sendResponse(requestId, value);
      
      // Show confirmation message
      const confirmation = this._createConfirmation(originalLabel, value);
      replaceElement(container, confirmation);
    });
  }

  /**
   * Send button response to backend
   * @private
   * @param {string} requestId - Request ID
   * @param {boolean} value - Response value
   */
  _sendResponse(requestId, value) {
    // Try to get connection from client or global window object
    const connection = this.client?.connection || window.bifrostClient?.connection;
    
    if (!connection) {
      this.logger.error('[ButtonRenderer] No WebSocket connection available');
      return;
    }
    
    try {
      connection.send(JSON.stringify({
        event: 'input_response',
        requestId: requestId,
        value: value
      }));
      
      this.logger.log('[ButtonRenderer] Response sent:', { requestId, value });
    } catch (error) {
      this.logger.error('[ButtonRenderer] Failed to send response:', error);
    }
  }

  /**
   * Create confirmation message after button click
   * @private
   * @param {string} label - Original button label
   * @param {boolean} value - Response value (true = clicked, false = cancelled)
   * @returns {HTMLElement} Confirmation paragraph
   */
  _createConfirmation(label, value) {
    // Get appropriate text color class
    const colorClass = value ? 'zText-success' : 'zText-info';
    
    // ✅ Use ONLY zTheme classes - NO inline styles!
    const confirmation = createElement('p', [colorClass, 'zm-0', 'zpy-2', 'zpx-3', 'zFw-bold']);
    
    // Set confirmation text
    const icon = value ? '✓' : '○';
    const action = value ? 'clicked' : 'cancelled';
    confirmation.textContent = `${icon} ${label} ${action}!`;
    
    return confirmation;
  }
}
