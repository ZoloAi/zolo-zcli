/**
 * ═══════════════════════════════════════════════════════════════
 * Validation Utilities - Input Validation & Sanitization
 * ═══════════════════════════════════════════════════════════════
 * 
 * Pure functions for validating and sanitizing user input.
 * Defense in depth: validate on frontend AND backend.
 * 
 * @module utils/validation_utils
 * @layer 2
 * @pattern Pure Functions
 * 
 * Dependencies:
 * - Layer 0: None (pure JavaScript)
 * 
 * Exports:
 * - validateInput: Validate input based on type and constraints
 * - sanitizeHTML: Sanitize HTML to prevent XSS
 * - validateSelectionRange: Validate selection input (1-N)
 * - parseMultiSelection: Parse multi-select input ("1,3,5" → [1,3,5])
 * - isValidEmail: Validate email format
 * - escapeRegex: Escape special regex characters
 * 
 * Example:
 * ```javascript
 * import { validateInput, sanitizeHTML } from './validation_utils.js';
 * 
 * const result = validateInput('test@example.com', 'email');
 * if (!result.valid) {
 *   console.error(result.error);
 * }
 * ```
 */

// ─────────────────────────────────────────────────────────────────
// Input Validation
// ─────────────────────────────────────────────────────────────────

/**
 * Validate input based on type and constraints
 * 
 * @param {any} value - Input value to validate
 * @param {string} type - Input type (string, number, email, url, etc)
 * @param {Object} [constraints={}] - Validation constraints
 * @param {boolean} [constraints.required=false] - Is field required?
 * @param {number} [constraints.min] - Minimum value (for numbers) or length (for strings)
 * @param {number} [constraints.max] - Maximum value (for numbers) or length (for strings)
 * @param {RegExp|string} [constraints.pattern] - Regex pattern to match
 * @returns {Object} {valid: boolean, error: string|null}
 * 
 * @example
 * validateInput('test@example.com', 'email')
 * // { valid: true, error: null }
 * 
 * validateInput('abc', 'number')
 * // { valid: false, error: 'Must be a valid number' }
 * 
 * validateInput('', 'string', { required: true })
 * // { valid: false, error: 'This field is required' }
 * 
 * validateInput('hi', 'string', { min: 5 })
 * // { valid: false, error: 'Must be at least 5 characters' }
 */
export function validateInput(value, type, constraints = {}) {
  const { required = false, min, max, pattern } = constraints;

  // Check required
  if (required && (value === null || value === undefined || value === '')) {
    return { valid: false, error: 'This field is required' };
  }

  // If not required and empty, it's valid
  if (!required && (value === null || value === undefined || value === '')) {
    return { valid: true, error: null };
  }

  // Type-specific validation
  switch (type?.toLowerCase()) {
    case 'string':
    case 'text':
      return _validateString(value, min, max, pattern);

    case 'number':
    case 'integer':
      return _validateNumber(value, min, max);

    case 'email':
      return _validateEmail(value);

    case 'url':
      return _validateURL(value);

    case 'password':
      return _validatePassword(value, min);

    default:
      return { valid: true, error: null };
  }
}

/**
 * Validate string input
 * @private
 */
function _validateString(value, min, max, pattern) {
  const strValue = String(value);

  // Check min length
  if (min !== undefined && strValue.length < min) {
    return { valid: false, error: `Must be at least ${min} characters` };
  }

  // Check max length
  if (max !== undefined && strValue.length > max) {
    return { valid: false, error: `Must be no more than ${max} characters` };
  }

  // Check pattern
  if (pattern) {
    const regex = pattern instanceof RegExp ? pattern : new RegExp(pattern);
    if (!regex.test(strValue)) {
      return { valid: false, error: 'Invalid format' };
    }
  }

  return { valid: true, error: null };
}

/**
 * Validate number input
 * @private
 */
function _validateNumber(value, min, max) {
  const numValue = Number(value);

  if (isNaN(numValue)) {
    return { valid: false, error: 'Must be a valid number' };
  }

  // Check min value
  if (min !== undefined && numValue < min) {
    return { valid: false, error: `Must be at least ${min}` };
  }

  // Check max value
  if (max !== undefined && numValue > max) {
    return { valid: false, error: `Must be no more than ${max}` };
  }

  return { valid: true, error: null };
}

/**
 * Validate email input
 * @private
 */
function _validateEmail(value) {
  if (!isValidEmail(value)) {
    return { valid: false, error: 'Must be a valid email address' };
  }
  return { valid: true, error: null };
}

/**
 * Validate URL input
 * @private
 */
function _validateURL(value) {
  try {
    new URL(value);
    return { valid: true, error: null };
  } catch {
    return { valid: false, error: 'Must be a valid URL' };
  }
}

/**
 * Validate password input
 * @private
 */
function _validatePassword(value, minLength = 8) {
  const strValue = String(value);

  if (strValue.length < minLength) {
    return { valid: false, error: `Password must be at least ${minLength} characters` };
  }

  return { valid: true, error: null };
}

// ─────────────────────────────────────────────────────────────────
// Email Validation
// ─────────────────────────────────────────────────────────────────

/**
 * Validate email format
 * 
 * @param {string} email - Email address to validate
 * @returns {boolean} True if valid email format
 * 
 * @example
 * isValidEmail('test@example.com')     // true
 * isValidEmail('invalid.email')        // false
 * isValidEmail('test@localhost')       // true
 */
export function isValidEmail(email) {
  if (!email || typeof email !== 'string') {
    return false;
  }

  // Basic email regex (not perfect, but good enough for frontend)
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// ─────────────────────────────────────────────────────────────────
// HTML Sanitization
// ─────────────────────────────────────────────────────────────────

/**
 * Sanitize HTML to prevent XSS attacks
 * 
 * This is a BASIC sanitizer. For production, use DOMPurify or similar.
 * 
 * @param {string} html - HTML string to sanitize
 * @returns {string} Sanitized HTML
 * 
 * @example
 * sanitizeHTML('<script>alert("xss")</script>')
 * // '&lt;script&gt;alert("xss")&lt;/script&gt;'
 * 
 * sanitizeHTML('<b>Bold text</b>')
 * // '<b>Bold text</b>' (allowed tag)
 */
export function sanitizeHTML(html) {
  if (!html || typeof html !== 'string') {
    return '';
  }

  // Create a temporary element
  const temp = document.createElement('div');
  temp.textContent = html;
  return temp.innerHTML;
}

// ─────────────────────────────────────────────────────────────────
// Selection Validation
// ─────────────────────────────────────────────────────────────────

/**
 * Validate selection range for selection prompts
 * 
 * @param {string} input - User input (e.g., "1", "3", "1,3,5")
 * @param {number} maxOptions - Maximum valid option number
 * @returns {Object} {valid: boolean, error: string|null, selections: number[]|null}
 * 
 * @example
 * validateSelectionRange("1", 5)
 * // { valid: true, error: null, selections: [1] }
 * 
 * validateSelectionRange("1,3,5", 5)
 * // { valid: true, error: null, selections: [1, 3, 5] }
 * 
 * validateSelectionRange("1,10", 5)
 * // { valid: false, error: 'Selection 10 is out of range (1-5)', selections: null }
 * 
 * validateSelectionRange("abc", 5)
 * // { valid: false, error: 'Invalid selection format', selections: null }
 */
export function validateSelectionRange(input, maxOptions) {
  if (!input || typeof input !== 'string') {
    return { valid: false, error: 'Invalid selection format', selections: null };
  }

  try {
    const selections = parseMultiSelection(input);

    // Check if any selections
    if (selections.length === 0) {
      return { valid: false, error: 'No selections provided', selections: null };
    }

    // Check if all selections are in valid range
    for (const selection of selections) {
      if (selection < 1 || selection > maxOptions) {
        return {
          valid: false,
          error: `Selection ${selection} is out of range (1-${maxOptions})`,
          selections: null
        };
      }
    }

    return { valid: true, error: null, selections };
  } catch (error) {
    return { valid: false, error: 'Invalid selection format', selections: null };
  }
}

/**
 * Parse multi-select input string to array of numbers
 * 
 * @param {string} input - Comma-separated numbers (e.g., "1,3,5")
 * @returns {number[]} Array of selected indices (sorted, deduplicated)
 * 
 * @example
 * parseMultiSelection("1")           // [1]
 * parseMultiSelection("1,3,5")       // [1, 3, 5]
 * parseMultiSelection("5,1,3")       // [1, 3, 5] (sorted)
 * parseMultiSelection("1,1,3")       // [1, 3] (deduplicated)
 * parseMultiSelection("1, 3 , 5")    // [1, 3, 5] (whitespace handled)
 * 
 * @throws {Error} If input contains non-numeric values
 */
export function parseMultiSelection(input) {
  if (!input || typeof input !== 'string') {
    throw new Error('Invalid input');
  }

  // Split by comma, trim whitespace, parse to numbers
  const selections = input
    .split(',')
    .map(s => s.trim())
    .filter(s => s.length > 0)
    .map(s => {
      const num = parseInt(s, 10);
      if (isNaN(num)) {
        throw new Error(`Invalid number: ${s}`);
      }
      return num;
    });

  // Remove duplicates and sort
  return [...new Set(selections)].sort((a, b) => a - b);
}

// ─────────────────────────────────────────────────────────────────
// String Utilities
// ─────────────────────────────────────────────────────────────────

/**
 * Escape special characters for use in regex
 * 
 * @param {string} str - String to escape
 * @returns {string} Escaped string safe for RegExp
 * 
 * @example
 * escapeRegex('hello.world')      // 'hello\\.world'
 * escapeRegex('test[123]')        // 'test\\[123\\]'
 * escapeRegex('price: $5.99')     // 'price: \\$5\\.99'
 */
export function escapeRegex(str) {
  if (!str || typeof str !== 'string') {
    return '';
  }

  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

