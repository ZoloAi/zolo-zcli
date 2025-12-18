/**
 * ═══════════════════════════════════════════════════════════════
 * BifrostClient - Production JavaScript Client for zBifrost
 * ═══════════════════════════════════════════════════════════════
 * 
 * A production-ready WebSocket client for zCLI's zBifrost bridge.
 * Modular architecture with lazy loading and automatic zTheme integration.
 * 
 * @version 1.5.5
 * @author Gal Nachshon
 * @license MIT
 * 
 * ───────────────────────────────────────────────────────────────
 * Quick Start
 * ───────────────────────────────────────────────────────────────
 * 
 * // Swiper-Style Elegance (One declaration, everything happens automatically):
 * const client = new BifrostClient('ws://localhost:8765', {
 *   autoConnect: true,        // Auto-connect on instantiation
 *   zTheme: true,             // Enable zTheme CSS & rendering
 *   // targetElement: 'zVaF', // Optional: default is 'zVaF' (zView and Function)
 *   autoRequest: 'show_hello',// Auto-send on connect
 *   onConnected: (info) => console.log('✅ Connected!', info)
 * });
 * 
 * // Traditional (More control):
 * const client = new BifrostClient('ws://localhost:8765', {
 *   zTheme: true,
 *   hooks: {
 *     onConnected: (info) => console.log('Connected!'),
 *     onDisconnected: (reason) => console.log('Disconnected:', reason),
 *     onMessage: (msg) => console.log('Message:', msg),
 *     onError: (error) => console.error('Error:', error)
 *   }
 * });
 * await client.connect();
 * client.send({event: 'my_event'});
 * const users = await client.read('users');
 * 
 * ───────────────────────────────────────────────────────────────
 * Lazy Loading Architecture
 * ───────────────────────────────────────────────────────────────
 * 
 * Modules are loaded dynamically only when needed:
 * - Logger/Hooks: Loaded immediately (lightweight)
 * - Connection: Loaded on connect()
 * - MessageHandler: Loaded on connect()
 * - Renderer: Loaded on first renderTable/renderMenu/etc call
 * - ThemeLoader: Loaded on connect() if zTheme enabled
 * 
 * Benefits:
 * - CDN-friendly (no import resolution at load time)
 * - Progressive loading (only load what you use)
 * - Stays modular (source files remain separate)
 * 
 * ───────────────────────────────────────────────────────────────
 */

(function(root, factory) {
  // UMD (Universal Module Definition) for maximum compatibility
  if (typeof define === 'function' && define.amd) {
    // AMD
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    // CommonJS
    module.exports = factory();
  } else {
    // Browser globals
    root.BifrostClient = factory();
  }
}(typeof self !== 'undefined' ? self : this, function() {
  'use strict';

  /**
   * Get base URL for module imports
   */
  function getBaseUrl() {
    if (typeof document !== 'undefined') {
      const scripts = document.querySelectorAll('script[src*="bifrost_client"]');
      if (scripts.length > 0) {
        const src = scripts[scripts.length - 1].src;
        return src.substring(0, src.lastIndexOf('/') + 1);
      }
    }
    return './';
  }

  /**
   * BifrostClient - Main class for WebSocket communication with zBifrost
   */
  class BifrostClient {
    /**
     * Create a new BifrostClient instance
     * @param {string} url - WebSocket server URL (e.g., 'ws://localhost:8765')
     * @param {Object} options - Configuration options
     * @param {boolean} options.autoConnect - Auto-connect on instantiation (default: false)
     * @param {boolean} options.zTheme - Load zTheme CSS + JS from CDN (default: false)
     * @param {string} options.zThemeCDN - CDN base URL for zTheme (default: jsdelivr ZoloAi/zTheme)
     * Note: Bootstrap Icons are ALWAYS loaded automatically (unchangeable default)
     * @param {string} options.targetElement - Target DOM selector for rendering (default: 'zVaF')
     * @param {string|Object} options.autoRequest - Auto-send request on connect (event name or full request object)
     * @param {boolean} options.autoReconnect - Auto-reconnect on disconnect (default: true)
     * @param {number} options.reconnectDelay - Delay between reconnect attempts in ms (default: 3000)
     * @param {number} options.timeout - Request timeout in ms (default: 30000)
     * @param {boolean} options.debug - Enable debug logging (default: false)
     * @param {string} options.token - Authentication token (optional)
     * @param {Object} options.hooks - Event hooks for customization
     */
    constructor(url, options = {}) {
      // Read zUI config from page FIRST (server-injected WebSocket SSL config)
      let zuiConfigEarly = {};
      if (typeof document !== 'undefined' && !url) {
        const zuiConfigEl = document.getElementById('zui-config');
        if (zuiConfigEl) {
          try {
            zuiConfigEarly = JSON.parse(zuiConfigEl.textContent);
          } catch (e) {
            console.warn('[BifrostClient] Failed to parse zui-config:', e);
          }
        }
      }
      
      // Auto-construct WebSocket URL from backend config (respects .zEnv SSL settings)
      if (!url) {
        const wsConfig = zuiConfigEarly.websocket || {};
        const protocol = wsConfig.ssl_enabled ? 'wss:' : 'ws:';
        const wsHost = wsConfig.host || '127.0.0.1';
        const wsPort = wsConfig.port || 8765;
        url = `${protocol}//${wsHost}:${wsPort}`;
        console.log(`[BifrostClient] Auto-constructed WebSocket URL from backend config: ${url} (SSL: ${wsConfig.ssl_enabled})`);
      }
      
      // Validate URL
      if (typeof url !== 'string' || url.trim() === '') {
        throw new Error('BifrostClient: URL must be a non-empty string');
      }
      if (!url.startsWith('ws://') && !url.startsWith('wss://')) {
        throw new Error('BifrostClient: URL must start with ws:// or wss://');
      }

      this.url = url;

      // Validate and set options
      const reconnectDelay = options.reconnectDelay || 3000;
      const timeout = options.timeout || 30000;

      if (typeof reconnectDelay !== 'number' || reconnectDelay <= 0) {
        throw new Error('BifrostClient: reconnectDelay must be a positive number');
      }
      if (typeof timeout !== 'number' || timeout <= 0) {
        throw new Error('BifrostClient: timeout must be a positive number');
      }

      // Auto-read zUI config from page (server-injected zSession values)
      let zuiConfig = {};
      if (typeof document !== 'undefined') {
        const zuiConfigEl = document.getElementById('zui-config');
        if (zuiConfigEl) {
          try {
            zuiConfig = JSON.parse(zuiConfigEl.textContent);
            if (this.logger) {
              console.log('[BifrostClient] Auto-loaded zUI config from page:', zuiConfig);
            }
          } catch (e) {
            console.warn('[BifrostClient] Failed to parse zui-config:', e);
          }
        }
      }
      
      // Store zuiConfig on instance for later access (e.g., navbar resolution)
      this.zuiConfig = zuiConfig;

      // Determine autoRequest based on zui-config
      let autoRequest = options.autoRequest || null;
      
      // If zBlock is specified (from zui-config or options), auto-generate walker execution request
      const zBlock = options.zBlock || zuiConfig.zBlock || null;
      const zVaFile = options.zVaFile || zuiConfig.zVaFile || null;
      const zVaFolder = options.zVaFolder || zuiConfig.zVaFolder || null;
      
      if (zBlock && !autoRequest) {
        autoRequest = {
          event: 'execute_walker',
          zBlock: zBlock,
          zVaFile: zVaFile,
          zVaFolder: zVaFolder
        };
        console.log('[BifrostClient] 🚀 Auto-generated walker execution request from zui-config:', autoRequest);
      }

      this.options = {
        autoConnect: options.autoConnect || false, // Default false
        zTheme: options.zTheme || false, // Load zTheme from CDN (CSS + JS)
        zIcons: options.zIcons || false, // Load zTheme icons from CDN (SVG sprite)
        targetElement: options.targetElement || 'zVaF', // Default zCLI parent tag (zView and Function)
        autoRequest: autoRequest, // Auto-send on connect (generated or explicit)
        autoReconnect: options.autoReconnect !== false, // Default true
        reconnectDelay: reconnectDelay,
        timeout: timeout,
        debug: options.debug || false,
        token: options.token || null,
        hooks: options.hooks || {},
        zThemeCDN: options.zThemeCDN || 'https://cdn.jsdelivr.net/gh/ZoloAi/zTheme@c687707/dist', // CDN base URL (commit hash bypasses cache)
        // Full declarative mode - auto-read from page config, fallback to explicit options
        zVaFile: zVaFile,   // YAML file to load
        zVaFolder: zVaFolder, // Folder path
        zBlock: zBlock,      // Block to render
        title: options.title || zuiConfig.title || null          // zSpark title for navbar brand
      };

      // Module cache (lazy loaded)
      this._modules = {};
      this._baseUrl = getBaseUrl();
      
      // Pre-initialize lightweight modules synchronously (MUST BE FIRST - initializes logger)
      this._initLightweightModules();
      
      // v1.6.0: Initialize cache system (async, must complete before connect)
      this.cache = null;
      this.session = null;
      this.storage = null;
      this._cacheReady = this._initCacheSystem().then(() => {
        // Register hooks after cache is initialized
        this._registerCacheHooks();
        this.logger.log('[Cache] ✅ Ready for connection');
      }).catch(err => {
        this.logger.error('[Cache] Initialization failed:', err);
        // Non-fatal: allow connection without cache
      });

      // Debug: confirm which declarative UI options were actually received
      this.logger.log('[BifrostClient] init options:', {
        targetElement: this.options.targetElement,
        zVaFile: this.options.zVaFile,
        zVaFolder: this.options.zVaFolder,
        zBlock: this.options.zBlock
      });
      
      // Load zTheme from CDN if enabled
      if (this.options.zTheme) {
        this._loadZThemeCDN();
      }
      
      // Bootstrap Icons are ALWAYS loaded (unchangeable default for zBifrost)
      this._loadBootstrapIcons();
      
      // v1.6.0: Initialize zVaF elements (now synchronous - elements exist in HTML)
      // Just populate content, don't create structure
      this._initZVaFElements();
      
      // Auto-load declarative UI if zVaFile is provided
      // SKIP for walker-based pages (progressive chunk rendering from backend)
      const isWalkerMode = autoRequest && autoRequest.event === 'execute_walker';
      if (this.options.zVaFile && !isWalkerMode) {
        this._loadDeclarativeUI().catch(err => {
          this.logger.error('Failed to load declarative UI:', err);
        });
      } else if (isWalkerMode) {
        this.logger.log('🎬 Walker mode detected - waiting for progressive chunks from backend');
        // v1.6.0: Navbar is now fetched by _initZVaFElements (no need for redundant call)
      }
      
      // Auto-connect if requested (Swiper-style elegance!)
      // v1.6.0: Wait for cache initialization before connecting (zVaF elements are now sync)
      if (this.options.autoConnect) {
        this._cacheReady.finally(() => {
          console.log('[BifrostClient] ✅ Cache ready - connecting...');
          this.connect().catch(err => {
            this.logger.error('Auto-connect failed:', err);
            this.hooks.call('onError', { type: 'autoconnect_failed', error: err });
          });
        });
      }
      
      // Part 2: Browser lifecycle awareness - cleanup on page unload
      // Track if we're doing client-side navigation (to avoid false page_unload events)
      this._isClientSideNav = false;
      
      window.addEventListener('beforeunload', (e) => {
        // Only send page_unload if this is a real page unload (not client-side nav)
        if (this._isClientSideNav) {
          console.log('[BifrostClient] Client-side navigation detected - skipping page_unload');
          this._isClientSideNav = false;
          return;
        }
        
        console.log('[BifrostClient] 🔄 Page unloading (leaving site) - notifying backend');
        // Send cleanup notification (best effort - may not complete if page closes quickly)
        if (this.connection && this.connection.isConnected()) {
          try {
            this.connection.send(JSON.stringify({
              event: 'page_unload',
              reason: 'navigation',
              timestamp: Date.now()
            }));
          } catch (err) {
            // Ignore errors during unload (connection might already be closing)
            console.warn('[BifrostClient] Could not send page_unload message:', err);
          }
        }
      });
    }

    /**
     * Initialize lightweight modules that don't require imports
     */
    _initLightweightModules() {
      // Inline Logger (lightweight, no dependencies)
      this.logger = {
        debug: this.options.debug,
        log: (message, ...args) => {
          if (this.logger.debug) {
            console.log(`[BifrostClient] ${message}`, ...args);
          }
        },
        error: (message, ...args) => {
          // Always show errors, regardless of debug mode
          console.error(`[BifrostClient ERROR] ${message}`, ...args);
        },
        warn: (message, ...args) => {
          if (this.logger.debug) {
            console.warn(`[BifrostClient WARN] ${message}`, ...args);
          }
        },
        enable: () => {
          this.logger.debug = true;
        },
        disable: () => {
          this.logger.debug = false;
        },
        isEnabled: () => {
          return this.logger.debug;
        }
      };

      // Inline HookManager (lightweight, no dependencies)
      this.hooks = {
        hooks: this.options.hooks || {},
        errorHandler: null, // Set by _initErrorDisplay()
        call: (hookName, ...args) => {
          const hook = this.hooks.hooks[hookName];
          console.log(`[Hooks] 🎣 Calling hook: ${hookName}, exists: ${typeof hook === 'function'}`);
          if (typeof hook === 'function') {
            try {
              return hook(...args);
            } catch (error) {
              // Log to console
              console.error(`[BifrostClient] Error in ${hookName} hook:`, error);
              
              // Log via logger
              this.logger.error(`Error in ${hookName} hook:`, error);
              
              // Display in UI if error handler is set
              if (this.hooks.errorHandler) {
                try {
                  this.hooks.errorHandler({
                    type: 'hook_error',
                    hookName,
                    error,
                    message: error.message,
                    stack: error.stack
                  });
                } catch (displayError) {
                  console.error('[BifrostClient] Error handler itself failed:', displayError);
                }
              }
              
              // Call onError hook if it exists and isn't the one that failed
              if (hookName !== 'onError' && this.hooks.hooks.onError) {
                try {
                  this.hooks.hooks.onError(error);
                } catch (onErrorError) {
                  console.error('[BifrostClient] onError hook failed:', onErrorError);
                }
              }
            }
          }
        },
        has: (hookName) => {
          return typeof this.hooks.hooks[hookName] === 'function';
        },
        register: (hookName, fn) => {
          if (typeof fn === 'function') {
            this.hooks.hooks[hookName] = fn;
            console.log(`[Hooks] ✅ Registered hook: ${hookName}`);
          } else {
            console.error(`[Hooks] ❌ Failed to register hook ${hookName}: not a function`);
          }
        },
        unregister: (hookName) => {
          delete this.hooks.hooks[hookName];
        },
        list: () => Object.keys(this.hooks.hooks),
        
        // Dark mode utilities
        initBuiltInHooks: () => {
          // Initialize dark mode from localStorage
          const savedTheme = localStorage.getItem('zTheme-mode');
          if (savedTheme === 'dark') {
            this.hooks._applyDarkMode(true);
          }
        },
        
        _applyDarkMode: (isDark) => {
          const body = document.body;
          const navbars = document.querySelectorAll('.zNavbar');
          const togglers = document.querySelectorAll('.zNavbar-toggler');
          
          console.log(`[DarkMode] Applying ${isDark ? 'DARK' : 'LIGHT'} mode`);
          console.log(`[DarkMode] Found ${navbars.length} navbar(s), ${togglers.length} toggler(s)`);
          
          if (isDark) {
            // Apply dark background to body
            body.classList.add('zBg-dark');
            // Apply white text ONLY to direct children of body that need it (not cards)
            // Cards keep their light background and dark text for readability
            const contentArea = this._zVaFElement;
            if (contentArea) {
              // Apply white text to headers/titles outside cards
              contentArea.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(header => {
                // Only if not inside a card
                if (!header.closest('.zCard')) {
                  header.classList.add('zText-light');
                }
              });
              // Apply white text to paragraphs outside cards
              contentArea.querySelectorAll('p').forEach(p => {
                // Only if not inside a card
                if (!p.closest('.zCard')) {
                  p.classList.add('zText-light');
                }
              });
            }
            body.style.backgroundColor = 'var(--color-dark)';
            // DON'T set body.style.color - let it cascade properly to preserve card readability
            navbars.forEach(nav => {
              nav.classList.remove('zNavbar-light');
              nav.classList.add('zNavbar-dark');
              console.log(`[DarkMode] Navbar classes:`, nav.className);
            });
            // Apply dark mode to hamburger icon (makes it white)
            togglers.forEach((toggler, idx) => {
              toggler.classList.add('zNavbar-toggler-dark');
              // Bootstrap Icons inherit color from parent, set explicitly to white
              const icon = toggler.querySelector('i.bi');
              if (icon) {
                icon.style.color = '#ffffff';  // Direct color value instead of CSS var
              }
              const computedColor = icon ? window.getComputedStyle(icon).color : 'not found';
              console.log(`[DarkMode] Toggler ${idx} classes:`, toggler.className);
              console.log(`[DarkMode] Toggler ${idx} icon color (after):`, computedColor);
              console.log(`[DarkMode] Toggler ${idx} icon element:`, icon);
            });
            
            // Apply dark mode to theme toggle button icon (sun icon should be white)
            const themeToggleBtn = document.querySelector('.zTheme-toggle');
            if (themeToggleBtn) {
              const icon = themeToggleBtn.querySelector('i.bi');
              if (icon) {
                icon.style.color = '#ffffff';  // Direct color value instead of CSS var
                console.log(`[DarkMode] Theme toggle icon color set to white`);
              }
            } else {
              console.log(`[DarkMode] Theme toggle button not found yet`);
            }
          } else {
            // Remove dark background from body
            body.classList.remove('zBg-dark');
            // Remove white text from all elements
            const contentArea = this._zVaFElement;
            if (contentArea) {
              contentArea.querySelectorAll('.zText-light').forEach(el => {
                el.classList.remove('zText-light');
              });
            }
            body.style.backgroundColor = '';
            body.style.color = '';
            navbars.forEach(nav => {
              nav.classList.remove('zNavbar-dark');
              nav.classList.add('zNavbar-light');
              console.log(`[DarkMode] Navbar classes:`, nav.className);
            });
            // Remove dark mode from hamburger icon
            togglers.forEach((toggler, idx) => {
              toggler.classList.remove('zNavbar-toggler-dark');
              // Clear inline styles to restore default color
              const icon = toggler.querySelector('i.bi');
              if (icon) {
                icon.style.color = '';
              }
              const computedColor = icon ? window.getComputedStyle(icon).color : 'not found';
              console.log(`[DarkMode] Toggler ${idx} classes:`, toggler.className);
              console.log(`[DarkMode] Toggler ${idx} icon color (after):`, computedColor);
            });
            
            // Clear theme toggle button icon color
            const themeToggleBtn = document.querySelector('.zTheme-toggle');
            if (themeToggleBtn) {
              const icon = themeToggleBtn.querySelector('i.bi');
              if (icon) {
                icon.style.color = '';
                console.log(`[DarkMode] Theme toggle icon color cleared`);
              }
            }
          }
        },
        
        addDarkModeToggle: (navElement) => {
          if (!navElement) {
            console.warn('[HookManager] No navbar element provided for dark mode toggle');
            return;
          }

          // Check if toggle already exists
          if (navElement.querySelector('.zTheme-toggle')) {
            return;
          }

          // Create toggle button
          const toggleBtn = document.createElement('button');
          toggleBtn.className = 'zBtn zBtn-sm zBtn-outline-secondary zTheme-toggle';
          toggleBtn.setAttribute('aria-label', 'Toggle dark mode');
          toggleBtn.style.marginLeft = 'auto'; // Push to the right
          
          // Get current theme
          const isDark = localStorage.getItem('zTheme-mode') === 'dark';
          const iconColor = isDark ? 'color: #ffffff;' : '';  // White in dark mode
          toggleBtn.innerHTML = isDark 
            ? `<i class="bi bi-sun-fill" style="font-size: 1.2rem; ${iconColor}"></i>` 
            : `<i class="bi bi-moon-fill" style="font-size: 1.2rem; ${iconColor}"></i>`;
          
          // Add click handler
          toggleBtn.addEventListener('click', () => {
            const currentTheme = localStorage.getItem('zTheme-mode');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Save preference
            localStorage.setItem('zTheme-mode', newTheme);
            
            // Apply theme
            this.hooks._applyDarkMode(newTheme === 'dark');
            
            // Update button icon with correct color
            const iconColor = newTheme === 'dark' ? 'color: #ffffff;' : '';
            toggleBtn.innerHTML = newTheme === 'dark'
              ? `<i class="bi bi-sun-fill" style="font-size: 1.2rem; ${iconColor}"></i>`
              : `<i class="bi bi-moon-fill" style="font-size: 1.2rem; ${iconColor}"></i>`;
            
            // Call onThemeChange hook if registered
            this.hooks.call('onThemeChange', newTheme);
            
            this.logger.log(`[HookManager] Theme switched to: ${newTheme}`);
          });

          // Find the navbar-nav ul and append toggle next to it
          const navCollapse = navElement.querySelector('.zNavbar-collapse');
          if (navCollapse) {
            // Create a container for the toggle (follows zTheme navbar structure)
            const toggleContainer = document.createElement('div');
            toggleContainer.className = 'zNavbar-nav zms-auto';
            toggleContainer.appendChild(toggleBtn);
            navCollapse.appendChild(toggleContainer);
          } else {
            // Fallback: just append to navbar
            navElement.appendChild(toggleBtn);
          }

          this.logger.log('[HookManager] Added dark mode toggle to navbar');
        }
      };

      // Initialize built-in hooks (dark mode)
      this.hooks.initBuiltInHooks();

      // Register default widget hooks (Week 4.2)
      this._registerDefaultWidgetHooks();

      this.logger.log('BifrostClient initialized', { url: this.url, options: this.options });
    }

    /**
     * Register default hooks for widget events
     * 
     * NOTE: Progress bar and spinner hooks removed as the renderer methods
     * (renderProgressBar, updateProgress, removeProgress, renderSpinner, removeSpinner)
     * are not yet implemented. These will be added back in Task 9 when we implement
     * and test the auto-rendering methods.
     * 
     * For now, users can implement these hooks manually if needed.
     */
    _registerDefaultWidgetHooks() {
      // Placeholder for future widget hooks
      // Will be implemented in Task 9: Test Auto-Rendering Methods
    }
    
    _registerCacheHooks() {
      // v1.6.0: Register hook to populate session from connection_info
      this.hooks.register('onConnectionInfo', async (data) => {
        try {
          if (!this.session) {
            this.logger.log('[Cache] Session not initialized yet, skipping');
            return;
          }
          
          const sessionData = data.session;
          if (!sessionData) {
            this.logger.log('[Cache] No session data in connection_info');
            return;
          }
          
          // Get OLD auth state before updating
          const wasAuthenticated = this.session.isAuthenticated();
          const oldSessionHash = this.session.getHash();
          
          // Populate session with backend data
          if (sessionData.authenticated && sessionData.session_hash) {
            await this.session.setPublicData({
              username: sessionData.username,
              role: sessionData.role,
              session_hash: sessionData.session_hash,
              app: sessionData.active_app
            });
            this.logger.log(`[Cache] ✅ Session populated: ${sessionData.username} (${sessionData.role})`);
          } else {
            this.logger.log('[Cache] User not authenticated, session remains anonymous');
          }
          
          // Get NEW auth state after updating
          const isNowAuthenticated = this.session.isAuthenticated();
          const newSessionHash = this.session.getHash();
          
          // v1.6.0: If auth state changed or session_hash changed, fetch fresh navbar (RBAC-aware)
          if (wasAuthenticated !== isNowAuthenticated || oldSessionHash !== newSessionHash) {
            console.log('[NavBar] Auth state changed - fetching fresh navbar from API');
            await this._fetchAndPopulateNavBar();
            console.log('[NavBar] ✅ Navbar updated after auth change');
          }
        } catch (error) {
          this.logger.error('[Cache] Error populating session:', error);
        }
      });
      
      // v1.6.0: Offline-first - Handle disconnect + Badge update (combined hook)
      this.hooks.register('onDisconnected', async (reason) => {
        try {
          console.log('[Cache] Connection lost, entering offline mode');
          
          // Update badge (v1.6.0: Combined with cache hook to avoid conflicts)
          this._updateBadgeState('disconnected');
          
          // Cache zVaF content for offline access (badge/navbar are dynamic, re-populated on page load)
          if (this.cache && typeof document !== 'undefined') {
            const currentPage = window.location.pathname;
            const contentArea = this._zVaFElement;
            if (contentArea) {
              await this.cache.set(currentPage, contentArea.outerHTML, 'rendered');
              console.log(`[Cache] ✅ Cached content for offline: ${currentPage}`);
            }
          }
          
          // Disable forms (prevent data loss)
          this._disableForms();
          
        } catch (error) {
          this.logger.error('[Cache] Error handling disconnect:', error);
        }
      });
      
      // v1.6.0: Offline-first - Handle reconnect + Badge update (combined hook)
      this.hooks.register('onConnected', async (data) => {
        try {
          console.log('[Cache] Connection restored, exiting offline mode');
          
          // Update badge (v1.6.0: Combined with cache hook to avoid conflicts)
          this._updateBadgeState('connected');
          
          // Re-enable forms
          this._enableForms();
          
        } catch (error) {
          console.error('[Cache] Error handling reconnect:', error);
        }
      });
    }
    
    /**
     * Disable all forms during offline mode (v1.6.0)
     * @private
     */
    _disableForms() {
      if (typeof document === 'undefined') return;
      
      const forms = document.querySelectorAll('form');
      forms.forEach(form => {
        form.setAttribute('data-offline-disabled', 'true');
        const inputs = form.querySelectorAll('input, textarea, select, button');
        inputs.forEach(input => input.disabled = true);
      });
      
      this.logger.log('[Offline] ⚠️  Forms disabled (offline mode)');
    }
    
    /**
     * Re-enable forms after reconnecting (v1.6.0)
     * @private
     */
    _enableForms() {
      if (typeof document === 'undefined') return;
      
      const forms = document.querySelectorAll('form[data-offline-disabled]');
      forms.forEach(form => {
        form.removeAttribute('data-offline-disabled');
        const inputs = form.querySelectorAll('input, textarea, select, button');
        inputs.forEach(input => input.disabled = false);
      });
      
      this.logger.log('[Offline] ✅ Forms re-enabled (online mode)');
    }
    
    /**
     * Initialize cache system (v1.6.0)
     * Loads StorageManager, SessionManager, and CacheOrchestrator
     * @private
     */
    async _initCacheSystem() {
      try {
        // Check if running in browser
        if (typeof window === 'undefined') {
          this.logger.log('[Cache] Skipping (not in browser)');
          return;
        }
        
        this.logger.log('[Cache] Loading cache modules...');
        
        // Dynamically load cache modules (maintains single-import philosophy)
        await this._loadScript(`${this._baseUrl}core/storage_manager.js`);
        await this._loadScript(`${this._baseUrl}core/session_manager.js`);
        await this._loadScript(`${this._baseUrl}core/cache_orchestrator.js`);
        
        // Verify modules loaded
        if (typeof window.StorageManager === 'undefined' || 
            typeof window.SessionManager === 'undefined' || 
            typeof window.CacheOrchestrator === 'undefined') {
          this.logger.log('[Cache] Module loading failed, cache disabled');
          return;
        }
        
        this.logger.log('[Cache] ✅ Cache modules loaded');
        
        // Initialize storage
        this.storage = new window.StorageManager('zBifrost');
        await this.storage.init();
        this.logger.log('[Cache] ✅ Storage initialized');
        
        // Initialize session
        this.session = new window.SessionManager(this.storage);
        await this.session.init();
        this.logger.log('[Cache] ✅ Session initialized');
        
        // Initialize cache orchestrator
        this.cache = new window.CacheOrchestrator(this.storage, this.session);
        await this.cache.init();
        this.logger.log('[Cache] ✅ Cache orchestrator initialized (5 tiers)');
        
      } catch (error) {
        this.logger.error('[Cache] Initialization error:', error);
        // Non-fatal: cache is optional, BifrostClient will work without it
      }
    }
    
    /**
     * Dynamically load a script (v1.6.0)
     * @private
     */
    _loadScript(src) {
      return new Promise((resolve, reject) => {
        // Check if already loaded
        if (document.querySelector(`script[src="${src}"]`)) {
          resolve();
          return;
        }
        
        const script = document.createElement('script');
        script.src = src;
        script.onload = () => resolve();
        script.onerror = () => reject(new Error(`Failed to load ${src}`));
        document.head.appendChild(script);
      });
    }

    /**
     * Initialize zVaF elements (connection badges, dynamic content)
     * 
     * DECLARATIVE APPROACH: The zVaF element is an empty canvas.
     * This method populates it entirely, including connection badge and content area.
     */
    /**
     * Load zTheme CSS and JS from CDN
     * @private
     */
    _loadZThemeCDN() {
      if (typeof document === 'undefined') return;
      
      const cdnBase = this.options.zThemeCDN;
      
      // Check if CSS already loaded
      if (!document.querySelector(`link[href="${cdnBase}/ztheme.css"]`)) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = `${cdnBase}/ztheme.css`;
        document.head.appendChild(link);
        this.logger.log('✅ zTheme CSS loaded from CDN');
      }
      
      // Check if JS already loaded
      if (!document.querySelector(`script[src="${cdnBase}/ztheme.js"]`)) {
        const script = document.createElement('script');
        script.src = `${cdnBase}/ztheme.js`;
        document.head.appendChild(script);
        this.logger.log('✅ zTheme JS loaded from CDN');
      }
    }

    /**
     * Load Bootstrap Icons from CDN (ALWAYS loaded, unchangeable default)
     * @private
     */
    _loadBootstrapIcons() {
      if (typeof document === 'undefined') return;
      
      const bootstrapIconsCDN = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css';
      
      // Check if Bootstrap Icons already loaded
      if (!document.querySelector(`link[href="${bootstrapIconsCDN}"]`)) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = bootstrapIconsCDN;
        document.head.appendChild(link);
        this.logger.log('✅ Bootstrap Icons loaded from CDN (v1.11.3)');
      }
    }

    /**
     * Load and render declarative UI from zVaFile (client-side YAML parsing)
     * @private
     */
    async _loadDeclarativeUI() {
      try {
        this.logger.log('🎨 Loading declarative UI...');
        
        // Construct URL from zVaFolder and zVaFile
        const folder = this.options.zVaFolder || 'UI';
        const file = this.options.zVaFile;
        const block = this.options.zBlock || 'zVaF';
        
        // Convert zPath (@.UI) to URL path
        const urlPath = folder.startsWith('@.') ? folder.substring(2) : folder;
        const yamlUrl = `/${urlPath}/${file}.yaml`;
        
        this.logger.log(`📥 Fetching: ${yamlUrl}`);
        
        // Fetch YAML file
        const response = await fetch(yamlUrl);
        if (!response.ok) {
          throw new Error(`Failed to fetch ${yamlUrl}: ${response.status} ${response.statusText}`);
        }
        
        const yamlText = await response.text();
        this.logger.log('✅ YAML fetched, parsing...');
        
        // Parse YAML (using js-yaml from CDN)
        if (typeof jsyaml === 'undefined') {
          throw new Error('js-yaml library not loaded');
        }
        
        const yamlData = jsyaml.load(yamlText);
        this.logger.log('✅ YAML parsed:', yamlData);
        
        // Check for meta.zNavBar and render it at the top (website-style navigation)
        if (yamlData.meta && yamlData.meta.zNavBar) {
          this.logger.log('🔗 Resolving meta.zNavBar...');
          
          // Resolve navbar: true → global, array → local override
          let navbarItems = yamlData.meta.zNavBar;
          
          if (navbarItems === true) {
            // Opt-in to global navbar from zuiConfig
            console.log('[BifrostClient] 🎯 meta.zNavBar: true, checking zuiConfig...');
            console.log('[BifrostClient] 🎯 this.zuiConfig:', this.zuiConfig);
            
            if (this.zuiConfig && this.zuiConfig.zNavBar) {
              navbarItems = this.zuiConfig.zNavBar;
              console.log('[BifrostClient] ✅ Using global navbar from config:', navbarItems);
              this.logger.log('✅ Using global navbar from config:', navbarItems);
            } else {
              console.warn('[BifrostClient] ⚠️ meta.zNavBar: true but no global navbar in zuiConfig');
              this.logger.warn('[BifrostClient] meta.zNavBar: true but no global navbar in zuiConfig');
              navbarItems = null;
            }
          } else if (Array.isArray(navbarItems)) {
            console.log('[BifrostClient] ✅ Using local navbar override:', navbarItems);
            this.logger.log('✅ Using local navbar override:', navbarItems);
          } else {
            console.warn('[BifrostClient] ⚠️ Invalid meta.zNavBar value:', navbarItems);
            this.logger.warn('[BifrostClient] Invalid meta.zNavBar value:', navbarItems);
            navbarItems = null;
          }
          
          if (navbarItems && Array.isArray(navbarItems)) {
            await this._renderMetaNavBar(navbarItems);
          }
        }
        
        // Extract the specified block
        const blockData = yamlData[block];
        if (!blockData) {
          throw new Error(`Block "${block}" not found in ${yamlUrl}`);
        }
        
        this.logger.log(`✅ Rendering block: ${block}`);
        
        // Render the block declaratively (preserves _zClass and all styling)
        await this._renderBlock(blockData);
        
        this.logger.log('✅ Declarative UI loaded successfully');
        
      } catch (error) {
        this.logger.error('Failed to load declarative UI:', error);
        throw error;
      }
    }

    /**
     * Render a zVaF block declaratively (convert YAML to DOM)
     * @private
     */
    async _renderBlock(blockData) {
      // Use stored reference (set by _initZVaFElements)
      const contentElement = this._zVaFElement;
      if (!contentElement) {
        throw new Error('zVaF element not initialized');
      }
      
      // Clear existing content
      contentElement.innerHTML = '';
      
      // Check if blockData has block-level metadata (_zClass) for cascading
      let blockWrapper = contentElement;
      if (blockData && typeof blockData === 'object' && blockData._zClass) {
        // Create wrapper div for the entire block with block-level classes
        const blockLevelDiv = document.createElement('div');
        const blockName = this.options.zBlock || 'zBlock';
        
        // Apply block-level classes
        const classes = Array.isArray(blockData._zClass)
          ? blockData._zClass
          : blockData._zClass.split(',').map(c => c.trim());
        blockLevelDiv.className = classes.join(' ');
        blockLevelDiv.setAttribute('data-zblock', blockName);
        
        contentElement.appendChild(blockLevelDiv);
        blockWrapper = blockLevelDiv;  // Children render inside the block wrapper
        
        this.logger.log(`[BifrostClient] Created block-level wrapper with classes: ${blockData._zClass}`);
      }
      
      // Recursively render all items (await for navigation renderer loading)
      await this._renderItems(blockData, blockWrapper);
      
      // Enhance block-level zCard if present
      if (blockWrapper !== contentElement && blockWrapper.classList.contains('zCard')) {
        const cardRenderer = await this._ensureCardRenderer();
        cardRenderer.enhanceCard(blockWrapper);
        this.logger.log('[BifrostClient] Enhanced block-level zCard');
      }
    }

    /**
     * Progressive chunk rendering (Option A: Terminal First philosophy)
     * Appends chunks from backend as they arrive, stops at failed gates
     * @private
     */
    async _renderChunkProgressive(message) {
      try {
        console.log('[BifrostClient] 🎬 _renderChunkProgressive called with:', message);
        const {chunk_num, keys, data, is_gate} = message;
        
        console.log(`[BifrostClient] 📦 Rendering chunk #${chunk_num}: ${keys.join(', ')}`);
        this.logger.log(`[BifrostClient] 📦 Rendering chunk #${chunk_num}: ${keys.join(', ')}`);
        if (is_gate) {
          this.logger.log(`[BifrostClient] 🚪 Chunk contains gate - backend will stop if gate fails`);
        }
        
        // Check if we're rendering into a dashboard panel (zDash context)
        const dashboardPanelContent = document.getElementById('dashboard-panel-content');
        const contentDiv = dashboardPanelContent || this._zVaFElement;
        
        if (!contentDiv) {
          throw new Error('zVaF element not initialized. Ensure _initZVaFElements() was called.');
        }
        
        // Check if data has block-level metadata (_zClass, _zStyle, etc.)
        const hasBlockMetadata = data && Object.keys(data).some(k => k.startsWith('_'));
        
        // Determine the target container for rendering
        let targetContainer = contentDiv;
        
        // ALWAYS clear loading state on first chunk (regardless of metadata)
        if (chunk_num === 1) {
          contentDiv.innerHTML = '';
          this.logger.log(`[BifrostClient] 📦 Cleared loading state for chunk #1`);
        }
        
        if (hasBlockMetadata && chunk_num === 1) {
          // First chunk with block metadata: create a wrapper for the entire block
          const blockWrapper = document.createElement('div');
          blockWrapper.setAttribute('data-zblock', 'progressive');
          
          // Apply block-level metadata to wrapper
          for (const [key, value] of Object.entries(data)) {
            if (key === '_zClass' && value) {
              blockWrapper.className = value;
            } else if (key === '_zStyle' && value) {
              blockWrapper.setAttribute('style', value);
            }
          }
          
          contentDiv.appendChild(blockWrapper);
          targetContainer = blockWrapper;
          this.logger.log(`[BifrostClient] 📦 Created block wrapper with metadata for progressive rendering`);
        } else if (hasBlockMetadata && chunk_num > 1) {
          // Subsequent chunks: find existing block wrapper
          const existingWrapper = contentDiv.querySelector('[data-zblock="progressive"]');
          if (existingWrapper) {
            targetContainer = existingWrapper;
            this.logger.log(`[BifrostClient] 📦 Using existing block wrapper for chunk #${chunk_num}`);
          }
        }
        
        // Render YAML data using existing rendering pipeline
        // This preserves all styling, forms, zDisplay events, etc.
        if (data && typeof data === 'object') {
          await this._renderItems(data, targetContainer);
          this.logger.log(`[BifrostClient] ✅ Chunk #${chunk_num} rendered from YAML (${keys.length} keys)`);
        } else {
          this.logger.warn(`[BifrostClient] ⚠️ Chunk #${chunk_num} has no YAML data to render`);
        }
        
        // If this is a gate chunk, log that we're waiting for backend
        if (is_gate) {
          this.logger.log('[BifrostClient] ⏸️  Waiting for gate completion (backend controls flow)');
        }
        
      } catch (error) {
        this.logger.error('Failed to render chunk:', error);
        throw error;
      }
    }

    /**
     * Recursively render YAML items (handles nested structures like implicit wizards)
     * @private
     */
    async _renderItems(data, parentElement) {
      if (!data || typeof data !== 'object') {
        return;
      }
      
      // Check if parent already has block-level metadata applied (data-zblock attribute)
      const parentIsBlockWrapper = parentElement.hasAttribute && parentElement.hasAttribute('data-zblock');
      
      // Extract metadata first (underscore-prefixed keys like _zClass)
      const metadata = {};
      for (const [key, value] of Object.entries(data)) {
        if (key.startsWith('_')) {
          metadata[key] = value;
        }
      }
      
      // Iterate through all keys in this level
      for (const [key, value] of Object.entries(data)) {
        // Handle metadata keys BEFORE skipping
        if (key.startsWith('~')) {
          // Navigation metadata: ~zNavBar*
          if (key.startsWith('~zNavBar')) {
            await this._renderNavBar(value, parentElement);
            continue;
          }
          // Other metadata keys - skip for now
          continue;
        }
        
        // Skip internal metadata keys (underscore prefix)
        if (key.startsWith('_')) {
          continue;
        }
        
        this.logger.log(`Rendering item: ${key}`, value);
        
        // Check if this value has its own metadata (for nested _zClass support)
        let itemMetadata = {};
        
        // Only apply parent metadata if parent is NOT a block wrapper (avoids double-applying)
        if (!parentIsBlockWrapper && Object.keys(metadata).length > 0) {
          itemMetadata = metadata;
        }
        
        // Value's own metadata always takes precedence
        if (value && typeof value === 'object' && !Array.isArray(value)) {
          if (value._zClass) {
            itemMetadata = { _zClass: value._zClass };
            this.logger.log(`  Found nested metadata for ${key}:`, itemMetadata);
          }
        }
        
        // Create container wrapper for this zKey (zTheme responsive layout)
        const containerDiv = this._createContainer(key, itemMetadata);
        
        // Give container a data attribute for debugging
        containerDiv.setAttribute('data-zkey', key);
        
        // Handle list/array values (sequential zDisplay events or zDialog forms)
        if (Array.isArray(value)) {
          this.logger.log(`✅ Detected list/array for key: ${key}, items: ${value.length}`);
          // Iterate through list items and render each one
          for (const item of value) {
            if (item && item.zDisplay) {
              this.logger.log(`  ✅ Rendering zDisplay from list item:`, item.zDisplay);
              const element = await this._renderZDisplayEvent(item.zDisplay);
              if (element) {
                this.logger.log(`  ✅ Appended element to container`);
                containerDiv.appendChild(element);
              }
            } else if (item && item.zDialog) {
              this.logger.log(`  ✅ Rendering zDialog from list item:`, item.zDialog);
              const formRenderer = await this._ensureFormRenderer();
              const formElement = formRenderer.renderForm(item.zDialog);
              if (formElement) {
                this.logger.log(`  ✅ Appended zDialog form to container`);
                containerDiv.appendChild(formElement);
              }
            } else if (item && typeof item === 'object') {
              // Nested object in list - recurse
              await this._renderItems(item, containerDiv);
            }
          }
        }
        // Check if this has a direct zDisplay event
        else if (value && value.zDisplay) {
          const element = await this._renderZDisplayEvent(value.zDisplay);
          if (element) {
            containerDiv.appendChild(element);
          }
        }
        // Check if this has a direct zDialog form
        else if (value && value.zDialog) {
          this.logger.log(`  ✅ Rendering zDialog from direct value:`, value.zDialog);
          const formRenderer = await this._ensureFormRenderer();
          const formElement = formRenderer.renderForm(value.zDialog);
          if (formElement) {
            containerDiv.appendChild(formElement);
          }
        }
        // If it's an object with nested keys (implicit wizard), recurse
        else if (value && typeof value === 'object') {
          // Nested structure - render children recursively
          await this._renderItems(value, containerDiv);
        }
        
        // Enhance zCard containers with proper zTheme structure
        if (containerDiv.children.length > 0) {
          if (containerDiv.classList.contains('zCard')) {
            const cardRenderer = await this._ensureCardRenderer();
            cardRenderer.enhanceCard(containerDiv);
          }
          
          // Append container to parent
          parentElement.appendChild(containerDiv);
        }
      }
    }

    /**
     * Create container wrapper for a zKey with zTheme responsive classes
     * Supports _zClass metadata for customization
     * @private
     */
    _createContainer(zKey, metadata) {
      const container = document.createElement('div');
      
      // Check for custom classes in metadata
      if (metadata._zClass !== undefined) {
        if (metadata._zClass === '' || metadata._zClass === null) {
          // Empty string or null = no container classes (opt-out)
          container.className = '';
        } else if (Array.isArray(metadata._zClass)) {
          // Array of classes
          container.className = metadata._zClass.join(' ');
        } else if (typeof metadata._zClass === 'string') {
          // String: comma-separated or space-separated classes
          const classes = metadata._zClass.includes(',') 
            ? metadata._zClass.split(',').map(c => c.trim())
            : metadata._zClass.split(' ').filter(c => c.trim());
          container.className = classes.join(' ');
        }
      } else {
        // Default: zContainer for responsive layout
        container.className = 'zContainer';
      }
      
      // Add data attribute for debugging/testing
      container.setAttribute('data-zkey', zKey);
      
      return container;
    }

    /**
     * Render meta.zNavBar at the top of zVaF (website-style main navigation)
     * @private
     */
    /**
     * Render navbar HTML string (v1.6.0: Returns HTML, doesn't inject into DOM)
     * @param {Array} items - Navbar items (e.g., ['zVaF', 'zAbout', '^zLogin'])
     * @returns {Promise<string>} Navbar HTML
     */
    async _renderMetaNavBarHTML(items) {
      console.log('[BifrostClient] 🎯 _renderMetaNavBarHTML called with items:', items);
      
      if (!Array.isArray(items) || items.length === 0) {
        console.warn('[BifrostClient] ⚠️ No navbar items provided');
        return '';
      }

      try {
        // Load navigation renderer
        const navRenderer = await this._ensureNavigationRenderer();
        
        // Render navbar element
        const navElement = navRenderer.renderNavBar(items, {
          className: 'zcli-navbar-meta',
          theme: 'light',
          href: (item) => {
            // Strip modifiers (^ for bounce-back, ~ for anchor) from URL
            const cleanItem = item.replace(/^[\^~]+/, '');
            return `/${cleanItem}`;
          },
          brand: this.options.title
        });
        
        // Return outerHTML (will be set as innerHTML on <zNavBar> element)
        return navElement ? navElement.outerHTML : '';
      } catch (error) {
        console.error('[BifrostClient] Failed to render navbar HTML:', error);
        return '';
      }
    }

    /**
     * Render navigation bar from metadata (~zNavBar* in content)
     * @private
     */
    async _renderNavBar(items, parentElement) {
      if (!Array.isArray(items) || items.length === 0) {
        this.logger.warn('[BifrostClient] ~zNavBar* has no items or is not an array');
        return;
      }

      try {
        // Load navigation renderer
        const navRenderer = await this._ensureNavigationRenderer();
        
        // Render navbar with zTheme zNavbar component
        const navElement = navRenderer.renderNavBar(items, {
          theme: 'light'
        });

        if (navElement) {
          parentElement.appendChild(navElement);
          
          // Re-initialize zTheme collapse now that navbar is in DOM
          if (window.zTheme && typeof window.zTheme.initCollapse === 'function') {
            window.zTheme.initCollapse();
            this.logger.log('[BifrostClient] Re-initialized zTheme collapse for navbar');
          }
          
          this.logger.log('[BifrostClient] Rendered navigation bar with items:', items);
        }
      } catch (error) {
        this.logger.error('[BifrostClient] Failed to render navigation bar:', error);
      }
    }

    /**
     * Render a single zDisplay event as DOM element
     * @private
     */
    async _renderZDisplayEvent(eventData) {
      const event = eventData.event;
      this.logger.log(`[_renderZDisplayEvent] Rendering event: ${event}`, eventData);
      let element;
      
      switch (event) {
        case 'text':
          // Use modular TypographyRenderer for text
          const textRenderer = await this._ensureTypographyRenderer();
          element = textRenderer.renderText(eventData);
          this.logger.log(`[_renderZDisplayEvent] Rendered text element`);
          break;
          
        case 'header':
          // Use modular TypographyRenderer for headers
          const headerRenderer = await this._ensureTypographyRenderer();
          element = headerRenderer.renderHeader(eventData);
          this.logger.log(`[_renderZDisplayEvent] Rendered header element with level: ${eventData.level || 1}`);
          break;
          
        case 'divider':
          // Use modular TypographyRenderer for dividers
          const dividerRenderer = await this._ensureTypographyRenderer();
          element = dividerRenderer.renderDivider(eventData);
          break;
          
        default:
          this.logger.warn(`Unknown zDisplay event: ${event}`);
          element = document.createElement('div');
          element.textContent = `[${event}] ${eventData.content || ''}`;
          element.className = 'zDisplay-unknown';
      }
      
      return element;
    }

    /**
     * Initialize zVaF-specific DOM elements (connection badges, etc.)
     * @private
     */
    /**
     * Initialize zVaF elements (v1.6.0: Simplified - elements exist in HTML, just populate)
     * 
     * HTML structure (declared in zVaF.html):
     *   <zBifrostBadge></zBifrostBadge>  ← Dynamic, always fresh
     *   <zNavBar></zNavBar>              ← Dynamic, RBAC-aware
     *   <zVaF>...</zVaF>                 ← Cacheable content area
     */
    _initZVaFElements() {
      console.log('[_initZVaFElements] 🔧 Starting initialization...');
      
      if (typeof document === 'undefined') {
        console.warn('[_initZVaFElements] Not in browser environment');
        return;
      }

      // Step 1: Find badge element (created by template)
      const badgeElement = document.querySelector('zBifrostBadge');
      if (badgeElement) {
        this._zConnectionBadge = badgeElement;
        this._populateConnectionBadge();
        console.log('[_initZVaFElements] ✅ Badge element found and populated');
      } else {
        console.error('[_initZVaFElements] ❌ <zBifrostBadge> not found in DOM');
      }

      // Step 2: Find navbar element (created by template)
      const navElement = document.querySelector('zNavBar');
      if (navElement) {
        this._zNavBarElement = navElement;
        // Fetch and populate navbar asynchronously (don't block initialization)
        this._populateNavBar().catch(err => {
          console.error('[_initZVaFElements] Failed to populate navbar:', err);
        });
        console.log('[_initZVaFElements] ✅ NavBar element found, populating...');
      } else {
        console.error('[_initZVaFElements] ❌ <zNavBar> not found in DOM');
      }

      // Step 3: Find zVaF element (content renders directly into it)
      const zVaFElement = document.querySelector(this.options.targetElement) || 
                          document.getElementById(this.options.targetElement);
      if (zVaFElement) {
        this._zVaFElement = zVaFElement;
        console.log('[_initZVaFElements] ✅ zVaF element found (content will render here)');
      } else {
        console.error(`[_initZVaFElements] ❌ <${this.options.targetElement}> not found in DOM`);
      }

      console.log('[_initZVaFElements] ✅ All elements initialized (badge will be updated by onConnected hook)');
    }

    /**
     * Populate connection badge content (v1.6.0: Simplified - element exists, just set content)
     */
    _populateConnectionBadge() {
      if (!this._zConnectionBadge) return;
      
      // Set initial badge content (will be updated by connection hooks)
      this._zConnectionBadge.className = 'zConnection zBadge zBadge-connection zBadge-pending';
      this._zConnectionBadge.innerHTML = `
        <svg class="zIcon zIcon-sm zBadge-dot" aria-hidden="true">
          <use xlink:href="#icon-circle-fill"></use>
        </svg>
        <span class="zBadge-text">Connecting...</span>
      `;
      
      console.log('[ConnectionBadge] ✅ Badge populated with initial state');
    }

    /**
     * Update badge state (v1.6.0: Helper method called from hooks)
     * @param {string} state - 'connecting', 'connected', 'disconnected', 'error'
     */
    _updateBadgeState(state) {
      if (!this._zConnectionBadge) {
        console.warn('[ConnectionBadge] Cannot update - badge element not found');
        return;
      }

      const badge = this._zConnectionBadge;
      const badgeText = badge.querySelector('.zBadge-text');
      
      if (!badgeText) {
        console.warn('[ConnectionBadge] Cannot update - badge text element not found');
        return;
      }

      console.log(`[ConnectionBadge] 🔧 Updating badge to: ${state}`);

      // Remove all state classes
      badge.classList.remove('zBadge-pending', 'zBadge-success', 'zBadge-error');

      // Apply new state
      switch (state) {
        case 'connected':
          badge.classList.add('zBadge-success');
          badgeText.textContent = 'Connected';
          console.log('[ConnectionBadge] ✅ Badge updated to Connected');
          break;
        case 'disconnected':
          badge.classList.add('zBadge-pending');
          badgeText.textContent = 'Disconnected';
          console.log('[ConnectionBadge] ⚠️ Badge updated to Disconnected');
          break;
        case 'error':
          badge.classList.add('zBadge-error');
          badgeText.textContent = 'Error';
          console.log('[ConnectionBadge] ❌ Badge updated to Error');
          break;
        case 'connecting':
        default:
          badge.classList.add('zBadge-pending');
          badgeText.textContent = 'Connecting...';
          console.log('[ConnectionBadge] 🔄 Badge updated to Connecting');
          break;
      }
    }

    /**
     * Populate navbar from embedded config (v1.6.0: Use zuiConfig from server, fetch fresh on auth change)
     */
    async _populateNavBar() {
      if (!this._zNavBarElement) return;
      
      try {
        // Use embedded zuiConfig (already RBAC-filtered by backend on page load)
        if (this.zuiConfig && this.zuiConfig.zNavBar) {
          const navHTML = await this._renderMetaNavBarHTML(this.zuiConfig.zNavBar);
          this._zNavBarElement.innerHTML = navHTML;
          console.log('[NavBar] ✅ NavBar populated from embedded config:', this.zuiConfig.zNavBar);
          
          // Enable client-side navigation after navbar is rendered
          this._enableClientSideNavigation();
        } else {
          console.warn('[NavBar] No zNavBar in embedded zuiConfig, navbar will be empty');
        }
      } catch (error) {
        console.error('[NavBar] Failed to populate:', error);
      }
    }

    /**
     * Fetch fresh navbar from API and populate (used after auth state changes)
     */
    async _fetchAndPopulateNavBar() {
      if (!this._zNavBarElement) return;
      
      try {
        // Fetch fresh navbar config from backend (RBAC-filtered!)
        const response = await fetch('/api/zui/config');
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const freshConfig = await response.json();
        console.log('[NavBar] ✅ Fetched fresh config from API:', freshConfig);
        
        // Update zuiConfig with fresh navbar
        if (freshConfig.zNavBar) {
          this.zuiConfig.zNavBar = freshConfig.zNavBar;
          
          // Render navbar HTML and set it on the element
          const navHTML = await this._renderMetaNavBarHTML(freshConfig.zNavBar);
          this._zNavBarElement.innerHTML = navHTML;
          console.log('[NavBar] ✅ NavBar populated with fresh RBAC-filtered items');
          
          // Re-enable client-side navigation after navbar is re-rendered
          this._enableClientSideNavigation();
        } else {
          console.warn('[NavBar] No zNavBar in API response, skipping');
        }
      } catch (error) {
        console.error('[NavBar] Failed to fetch from API:', error);
      }
    }

    /**
     * Enable client-side navigation (SPA-style) for navbar links
     * Intercepts clicks to prevent full page reloads and uses WebSocket instead
     */
    _enableClientSideNavigation() {
      if (typeof document === 'undefined') return;
      
      // Remove any existing listeners to avoid duplicates
      if (this._navClickHandler) {
        document.removeEventListener('click', this._navClickHandler, true);
      }
      
      // Create navigation click handler
      this._navClickHandler = async (e) => {
        // Find if click target is within a navbar link OR brand link
        const link = e.target.closest('.zNavbar-nav .zNav-link, .zNavbar-brand');
        if (!link) return;
        
        // Prevent default HTTP navigation
        e.preventDefault();
        e.stopPropagation();
        
        const href = link.getAttribute('href');
        if (!href || href === '#') return;
        
        console.log('[ClientNav] 🔗 Intercepted navigation to:', href);
        
        // Navigate via WebSocket (no page reload!)
        await this._navigateToRoute(href);
      };
      
      // Use capture phase to ensure we intercept before other handlers
      document.addEventListener('click', this._navClickHandler, true);
      
      // Handle browser back/forward buttons
      if (!this._popstateHandler) {
        this._popstateHandler = async (e) => {
          console.log('[ClientNav] ⏪ Browser back/forward detected');
          const path = window.location.pathname;
          
          // Navigate to the new path via WebSocket
          await this._navigateToRoute(path, { skipHistory: true });
        };
        
        window.addEventListener('popstate', this._popstateHandler);
      }
      
      console.log('[ClientNav] ✅ Client-side navigation enabled');
    }

    /**
     * Navigate to a route via WebSocket (client-side navigation)
     * @param {string} routePath - Path to navigate to (e.g., '/zAbout', '/zAccount')
     * @param {Object} options - Navigation options
     */
    async _navigateToRoute(routePath, options = {}) {
      const { skipHistory = false } = options;
      
      // Mark as client-side navigation to prevent beforeunload from triggering
      this._isClientSideNav = true;
      
      try {
        // Extract route name from path (e.g., '/zAbout' -> 'zAbout')
        const routeName = routePath.replace(/^\//, '') || 'zVaF';
        
        console.log('[ClientNav] 🚀 Navigating to route:', routeName);
        
        // Fetch route configuration from backend
        const response = await fetch('/api/zui/config');
        if (!response.ok) {
          throw new Error(`Failed to fetch route config: ${response.status}`);
        }
        
        const config = await response.json();
        
        // Determine zBlock, zVaFile, zVaFolder for this route
        // For now, use simple convention: route name matches zUI file name
        const zVaFile = `zUI.${routeName}`;
        const zVaFolder = config.zVaFolder || '@.UI';
        let zBlock = routeName;
        
        // Check if this route has special modifiers (^ for bounce-back)
        const navBarItem = config.zNavBar?.find(item => {
          const cleanItem = item.replace(/^[\^~\$]+/, '');
          return cleanItem === routeName;
        });
        
        if (navBarItem) {
          // Use the full item with modifiers as zBlock
          zBlock = navBarItem;
        }
        
        console.log('[ClientNav] 📋 Route config:', { zVaFile, zVaFolder, zBlock });
        
        // Clear current content
        if (this._zVaFElement) {
          this._zVaFElement.innerHTML = '<div class="zText-center zp-4">Loading...</div>';
        }
        
        // Send walker execution request via WebSocket
        // NOTE: Walker execution is asynchronous - we don't wait for a response
        // The backend will send render_chunk events instead of a direct response
        const walkerRequest = {
          event: 'execute_walker',
          zBlock: zBlock,
          zVaFile: zVaFile,
          zVaFolder: zVaFolder
        };
        
        console.log('[ClientNav] 📤 Sending walker request (fire-and-forget):', walkerRequest);
        this.connection.send(JSON.stringify(walkerRequest));
        
        // Update browser URL without reload (unless skipHistory is true for popstate)
        if (!skipHistory) {
          const newUrl = routePath.startsWith('/') ? routePath : `/${routePath}`;
          history.pushState({ route: routeName }, '', newUrl);
          console.log('[ClientNav] ✅ Updated URL to:', newUrl);
        }
        
        console.log('[ClientNav] ✅ Navigation complete');
      } catch (error) {
        console.error('[ClientNav] ❌ Navigation failed:', error);
        
        // Reset flag on error
        this._isClientSideNav = false;
        
        // Show error in content area
        if (this._zVaFElement) {
          this._zVaFElement.innerHTML = `
            <div class="zAlert zAlert-danger zmt-4">
              <strong>Navigation Error:</strong> ${error.message}
            </div>
          `;
        }
      } finally {
        // Reset flag after navigation attempt (success or fail)
        setTimeout(() => {
          this._isClientSideNav = false;
        }, 100);
      }
    }


    /**
     * Lazy load a module
     * @param {string} moduleName - Name of the module (connection, message_handler, renderer, zdisplay_renderer)
     * @returns {Promise<any>}
     */
    async _loadModule(moduleName) {
      if (this._modules[moduleName]) {
        return this._modules[moduleName];
      }

      // Determine module subfolder based on module type
      const coreModules = ['connection', 'hooks', 'logger', 'message_handler', 'error_display'];
      const renderingModules = ['renderer', 'zdisplay_renderer', 'navigation_renderer', 'form_renderer'];
      
      let subfolder = '';
      if (coreModules.includes(moduleName)) {
        subfolder = 'core/';
      } else if (renderingModules.includes(moduleName)) {
        subfolder = 'rendering/';
      }

      const modulePath = `${this._baseUrl}${subfolder}${moduleName}.js`;
      this.logger.log(`Loading module: ${moduleName} from ${modulePath}`);

      try {
        const module = await import(modulePath);
        this._modules[moduleName] = module;
        return module;
      } catch (error) {
        this.logger.error(`Failed to load module ${moduleName}:`, error);
        throw new Error(`Failed to load BifrostClient module: ${moduleName}`);
      }
    }

    /**
     * Ensure connection module is loaded
     */
    async _ensureConnection() {
      if (!this.connection) {
        const { BifrostConnection } = await this._loadModule('connection');
        this.connection = new BifrostConnection(
          this.url,
          this.options,
          this.logger,
          this.hooks
        );
      }
      return this.connection;
    }

    /**
     * Ensure message handler module is loaded
     */
    async _ensureMessageHandler() {
      if (!this.messageHandler) {
        const { MessageHandler } = await this._loadModule('message_handler');
        this.messageHandler = new MessageHandler(this.logger, this.hooks, this);
        this.messageHandler.setTimeout(this.options.timeout);
      }
      return this.messageHandler;
    }

    /**
     * Ensure renderer module is loaded
     */
    async _ensureRenderer() {
      if (!this.renderer) {
        const { Renderer } = await this._loadModule('renderer');
        this.renderer = new Renderer(this.logger);
      }
      return this.renderer;
    }

    /**
     * Ensure navigation renderer module is loaded
     */
    async _ensureNavigationRenderer() {
      if (!this.navigationRenderer) {
        const { NavigationRenderer } = await this._loadModule('navigation_renderer');
        this.navigationRenderer = new NavigationRenderer(this.logger);
      }
      return this.navigationRenderer;
    }

    /**
     * Ensure TypographyRenderer module is loaded
     */
    async _ensureTypographyRenderer() {
      if (!this.typographyRenderer) {
        const module = await import('./rendering/typography_renderer.js');
        const TypographyRenderer = module.default;
        this.typographyRenderer = new TypographyRenderer(this.logger);
        this.logger.log('[BifrostClient] TypographyRenderer loaded and initialized');
      }
      return this.typographyRenderer;
    }

    /**
     * Ensure CardRenderer module is loaded
     */
    async _ensureCardRenderer() {
      if (!this.cardRenderer) {
        const module = await import('./rendering/card_renderer.js');
        const CardRenderer = module.default;
        this.cardRenderer = new CardRenderer(this.logger);
        this.logger.log('[BifrostClient] CardRenderer loaded and initialized');
      }
      return this.cardRenderer;
    }

    /**
     * Ensure zDisplay renderer module is loaded
     */
    async _ensureZDisplayRenderer() {
      if (!this.zDisplayRenderer) {
        const { ZDisplayRenderer } = await this._loadModule('zdisplay_renderer');
        this.zDisplayRenderer = new ZDisplayRenderer(this.logger);
        
        // Pass client reference for interactive features (navigation buttons, etc.)
        this.zDisplayRenderer.client = this;
        
        // Set target element - render directly into zVaF (no nested wrapper)
        this.zDisplayRenderer.defaultZone = this.options.targetElement;
        
        this.logger.log(`[BifrostClient] zDisplay target set to: ${this.zDisplayRenderer.defaultZone}`);
        
        // Register default onDisplay hook if not already set
        if (!this.hooks.has('onDisplay')) {
          this.hooks.register('onDisplay', async (event) => {
            console.log('[BifrostClient] 📨 onDisplay hook triggered with event:', event);
            console.log('[BifrostClient] 🔍 Event type check:', {
              'event.event': event.event,
              'event.display_event': event.display_event,
              'event.data': event.data
            });
            
            this.logger.log('[BifrostClient] Auto-rendering zDisplay event:', event);
            
            // Check if this is a zDialog event (form)
            if (event.event === 'zDialog' || event.display_event === 'zDialog') {
              console.log('[BifrostClient] ✅ DETECTED zDialog event - routing to FormRenderer');
              this.logger.log('[BifrostClient] Detected zDialog event, routing to FormRenderer');
              await this._ensureFormRenderer();
              
              // Extract form data from event.data (backend sends context as data payload)
              const formData = event.data || event;
              console.log('[BifrostClient] 📋 Form data to render:', formData);
              const formElement = this.formRenderer.renderForm(formData);
              
              // Append form to appropriate container
              // Try to find the last zContainer (for nested forms), otherwise use root
              const rootZone = document.getElementById(this.zDisplayRenderer.defaultZone);
              const containers = rootZone ? rootZone.querySelectorAll('.zContainer') : [];
              const targetZone = containers.length > 0 ? containers[containers.length - 1] : rootZone;
              
              console.log('[BifrostClient] 🎯 Target zone:', targetZone ? 'FOUND' : 'NOT FOUND', 
                          `(${containers.length} containers found, using ${containers.length > 0 ? 'last container' : 'root'})`);
              if (targetZone) {
                targetZone.appendChild(formElement);
                console.log('[BifrostClient] ✅ Form appended to DOM');
              }
            } else {
              console.log('[BifrostClient] ℹ️  Regular zDisplay event - routing to zDisplayRenderer');
              // Regular zDisplay event
              this.zDisplayRenderer.render(event);
            }
          });
          this.logger.log('[BifrostClient] Registered default onDisplay hook for auto-rendering');
        }
        
        // Register default onRenderChunk hook for progressive chunk rendering (walker mode)
        if (!this.hooks.has('onRenderChunk')) {
          this.hooks.register('onRenderChunk', async (message) => {
            console.log('[BifrostClient] 📦 onRenderChunk hook triggered:', message);
            this.logger.log('[BifrostClient] Processing chunk:', message);
            
            // Progressive chunk rendering (backend sends chunks via zWizard generator)
            await this._renderChunkProgressive(message);
            
            // v1.6.0: Cache ONLY content area after render completes (debounced)
            // Badge and navbar are dynamic and should never be cached
            if (this._cachePageTimeout) {
              clearTimeout(this._cachePageTimeout);
            }
            
            this._cachePageTimeout = setTimeout(async () => {
              if (this.cache && typeof document !== 'undefined') {
                try {
                  const currentPage = window.location.pathname;
                  // Cache zVaF content (badge/navbar are dynamic, re-populated on page load)
                  const contentArea = this._zVaFElement;
                  if (contentArea) {
                    await this.cache.set(currentPage, contentArea.outerHTML, 'rendered');
                    this.logger.log(`[Cache] ✅ Cached content: ${currentPage}`);
                  } else {
                    this.logger.warn('[Cache] No zVaF element found, skipping cache');
                  }
                } catch (error) {
                  this.logger.error('[Cache] Error caching content:', error);
                }
              }
            }, 500);
          });
          console.log('[BifrostClient] ✅ Registered onRenderChunk hook for progressive rendering');
          this.logger.log('[BifrostClient] Registered default onRenderChunk hook for progressive rendering');
        } else {
          console.log('[BifrostClient] ⚠️ onRenderChunk hook already registered');
        }
        
        // Register default onInput hook if not already set
        if (!this.hooks.has('onInput')) {
          this.hooks.register('onInput', (inputRequest) => {
            this.logger.log('[BifrostClient] Rendering input request:', inputRequest);
            const inputType = inputRequest.type || inputRequest.data?.type || 'string';
            
            // Route to appropriate renderer based on type
            if (inputType === 'selection') {
              this.zDisplayRenderer.renderSelectionRequest(inputRequest);
            } else if (inputType === 'button') {
              this.zDisplayRenderer.renderButtonRequest(inputRequest);
            } else {
              this.zDisplayRenderer.renderInputRequest(inputRequest);
            }
          });
          this.logger.log('[BifrostClient] Registered default onInput hook for input rendering');
        }
        
        // Register default onSpinnerStart hook if not already set
        if (!this.hooks.has('onSpinnerStart')) {
          this.hooks.register('onSpinnerStart', (event) => {
            this.logger.log('[BifrostClient] Spinner start:', event);
            this.zDisplayRenderer.renderSpinnerStart(event);
          });
          this.logger.log('[BifrostClient] Registered default onSpinnerStart hook');
        }
        
        // Register default onSpinnerStop hook if not already set
        if (!this.hooks.has('onSpinnerStop')) {
          this.hooks.register('onSpinnerStop', (event) => {
            this.logger.log('[BifrostClient] Spinner stop:', event);
            this.zDisplayRenderer.renderSpinnerStop(event);
          });
          this.logger.log('[BifrostClient] Registered default onSpinnerStop hook');
        }
        
        // Register default onSwiperInit hook if not already set
        if (!this.hooks.has('onSwiperInit')) {
          this.hooks.register('onSwiperInit', (event) => {
            this.logger.log('[BifrostClient] Swiper init:', event);
            this.zDisplayRenderer.renderSwiperInit(event);
          });
          this.logger.log('[BifrostClient] Registered default onSwiperInit hook');
        }
        
        // Register default onZDash hook if not already set
        if (!this.hooks.has('onZDash')) {
          this.hooks.register('onZDash', async (dashConfig) => {
            this.logger.log('[BifrostClient] 📊 onZDash hook triggered:', dashConfig);
            await this._renderDashboard(dashConfig);
          });
          this.logger.log('[BifrostClient] ✅ Registered onZDash hook for dashboard rendering');
        }
      }
      return this.zDisplayRenderer;
    }

    /**
     * Ensure form renderer module is loaded
     */
    async _ensureFormRenderer() {
      if (!this.formRenderer) {
        const { FormRenderer } = await this._loadModule('form_renderer');
        this.formRenderer = new FormRenderer(this);
        this.logger.log('[BifrostClient] FormRenderer loaded and initialized');
      }
      return this.formRenderer;
    }


    // ═══════════════════════════════════════════════════════════
    // Connection Management
    // ═══════════════════════════════════════════════════════════

    /**
     * Initialize error display (if not disabled)
     */
    async _ensureErrorDisplay() {
      if (this.options.showErrors === false) return; // Allow disabling
      
      if (!this.errorDisplay) {
        const { ErrorDisplay } = await this._loadModule('error_display');
        this.errorDisplay = new ErrorDisplay({
          position: this.options.errorPosition || 'top-right',
          maxErrors: this.options.maxErrors || 5,
          autoDismiss: this.options.autoDismiss || 10000
        });
        
        // Set error handler for hooks
        this.hooks.errorHandler = (errorInfo) => {
          this.errorDisplay.show(errorInfo);
        };
        
        this.logger.log('Error display initialized');
      }
      return this.errorDisplay;
    }

    /**
     * Check if running on file:// protocol (which doesn't support ES6 module imports)
     * @private
     */
    _isFileProtocol() {
      return typeof window !== 'undefined' && window.location.protocol === 'file:';
    }

    /**
     * Connect to the WebSocket server
     * @returns {Promise<void>}
     */
    async connect() {
      // Skip module loading for file:// protocol (ES6 imports not supported)
      const isFileProtocol = this._isFileProtocol();
      
      if (isFileProtocol) {
        this.logger.log('[BifrostClient] Running on file:// protocol - skipping module loading');
        this.logger.log('[BifrostClient] Error display and auto-rendering disabled (use HTTP server to enable)');
      }
      
      // Initialize error display (for visual error boundaries) - skip on file://
      if (!isFileProtocol && this.options.showErrors !== false) {
        try {
          await this._ensureErrorDisplay();
        } catch (error) {
          this.logger.warn('[BifrostClient] Error display failed to load:', error.message);
        }
      }
      
      // Initialize zDisplay renderer (for auto-rendering zDisplay events) - skip on file://
      if (!isFileProtocol) {
        try {
          await this._ensureZDisplayRenderer();
        } catch (error) {
          this.logger.warn('[BifrostClient] zDisplay renderer failed to load:', error.message);
        }
      }
      
      // Load theme BEFORE connecting to prevent FOUC (Flash of Unstyled Content)
      // Load required modules
      await this._ensureConnection();
      await this._ensureMessageHandler();
      
      await this.connection.connect();
      
      // Set up message handler
      this.connection.onMessage((event) => {
        this.messageHandler.handleMessage(event.data);
      });
      
      // Auto-send request if specified (Swiper-style elegance!)
      if (this.options.autoRequest) {
        const request = typeof this.options.autoRequest === 'string'
          ? { event: this.options.autoRequest }
          : this.options.autoRequest;
        
        // For execute_walker requests, use fire-and-forget (chunks come asynchronously)
        // For other requests, use send() to wait for response
        if (request.event === 'execute_walker') {
          this.logger.log('📤 Auto-sending walker request (fire-and-forget):', request);
          this.connection.send(JSON.stringify(request));
        } else {
          this.logger.log('📤 Auto-sending request:', request);
          this.send(request);
        }
      }
    }

    /**
     * Disconnect from the server
     */
    disconnect() {
      if (this.connection) {
        this.connection.disconnect();
      }
    }

    /**
     * Check if connected
     * @returns {boolean}
     */
    isConnected() {
      return this.connection ? this.connection.isConnected() : false;
    }

    // ═══════════════════════════════════════════════════════════
    // Message Sending
    // ═══════════════════════════════════════════════════════════

    /**
     * Send a message and wait for response
     * @param {Object} payload - Message payload
     * @param {number} timeout - Custom timeout (optional)
     * @returns {Promise<any>}
     */
    async send(payload, timeout = null) {
      if (!this.isConnected()) {
        throw new Error('Not connected to server. Call connect() first.');
      }

      await this._ensureMessageHandler();
      
      return this.messageHandler.send(
        payload,
        (msg) => this.connection.send(msg),
        timeout
      );
    }

    /**
     * Send input response to server
     * @param {string} requestId - Request ID from input event
     * @param {any} value - Input value
     */
    sendInputResponse(requestId, value) {
      if (!this.isConnected()) {
        this.logger.log('❌ Cannot send input response: not connected');
        return;
      }

      // Use new event protocol
      const message = JSON.stringify({
        event: 'input_response',
        requestId: requestId,
        value: value
      });
      
      this.connection.send(message);
    }

    // ═══════════════════════════════════════════════════════════
    // CRUD Operations
    // ═══════════════════════════════════════════════════════════

    /**
     * Create a new record
     * @param {string} model - Table/model name
     * @param {Object} data - Field values
     * @returns {Promise<Object>}
     */
    async create(model, data) {
      return this.send({
        event: 'dispatch',
        zKey: `^Create ${model}`,
        model: model,
        data: data
      });
    }

    /**
     * Read records
     * @param {string} model - Table/model name
     * @param {Object} filters - WHERE conditions (optional)
     * @param {Object} options - Additional options (fields, order_by, limit, offset)
     * @returns {Promise<Array>}
     */
    async read(model, filters = null, options = {}) {
      const payload = {
        event: 'dispatch',
        zKey: `^List ${model}`,
        model: model
      };

      if (filters) payload.where = filters;
      if (options.fields) payload.fields = options.fields;
      if (options.order_by) payload.order_by = options.order_by;
      if (options.limit !== undefined) payload.limit = options.limit;
      if (options.offset !== undefined) payload.offset = options.offset;

      return this.send(payload);
    }

    /**
     * Update record(s)
     * @param {string} model - Table/model name
     * @param {Object|number} filters - WHERE conditions or ID
     * @param {Object} data - Fields to update
     * @returns {Promise<Object>}
     */
    async update(model, filters, data) {
      if (typeof filters === 'number') {
        filters = { id: filters };
      }

      return this.send({
        event: 'dispatch',
        zKey: `^Update ${model}`,
        model: model,
        where: filters,
        data: data
      });
    }

    /**
     * Delete record(s)
     * @param {string} model - Table/model name
     * @param {Object|number} filters - WHERE conditions or ID
     * @returns {Promise<Object>}
     */
    async delete(model, filters) {
      if (typeof filters === 'number') {
        filters = { id: filters };
      }

      return this.send({
        event: 'dispatch',
        zKey: `^Delete ${model}`,
        model: model,
        where: filters
      });
    }

    // ═══════════════════════════════════════════════════════════
    // zCLI Operations
    // ═══════════════════════════════════════════════════════════

    /**
     * Execute a zFunc command
     * @param {string} command - zFunc command string
     * @returns {Promise<any>}
     */
    async zFunc(command) {
      return this.send({
        zKey: 'zFunc',
        zHorizontal: command
      });
    }

    /**
     * Navigate to a zLink path
     * @param {string} path - zLink navigation path
     * @returns {Promise<any>}
     */
    async zLink(path) {
      return this.send({
        zKey: 'zLink',
        zHorizontal: `zLink(${path})`
      });
    }

    /**
     * Execute a zOpen command
     * @param {string} command - zOpen command string
     * @returns {Promise<any>}
     */
    async zOpen(command) {
      return this.send({
        zKey: 'zOpen',
        zHorizontal: `zOpen(${command})`
      });
    }


    // ═══════════════════════════════════════════════════════════
    // Auto-Rendering Methods (Using zTheme)
    // ═══════════════════════════════════════════════════════════

    /**
     * Render data as a table with zTheme styling
     * @param {Array} data - Array of objects to render
     * @param {string|HTMLElement} container - Container selector or element
     * @param {Object} options - Rendering options
     */
    async renderTable(data, container, options = {}) {
      await this._ensureRenderer();
      this.renderer.renderTable(data, container, options);
    }

    /**
     * Render a menu with buttons
     * @param {Array} items - Array of menu items {label, action, icon, variant}
     * @param {string|HTMLElement} container - Container selector or element
     */
    async renderMenu(items, container) {
      await this._ensureRenderer();
      this.renderer.renderMenu(items, container);
    }

    /**
     * Render a form with zTheme styling
     * @param {Array} fields - Array of field definitions
     * @param {string|HTMLElement} container - Container selector or element
     * @param {Function} onSubmit - Submit handler
     */
    async renderForm(fields, container, onSubmit) {
      await this._ensureRenderer();
      this.renderer.renderForm(fields, container, onSubmit);
    }

    /**
     * Render a message/alert
     * @param {string} text - Message text
     * @param {string} type - Message type (success, error, warning, info)
     * @param {string|HTMLElement} container - Container selector or element
     * @param {number} duration - Auto-hide duration in ms (0 = no auto-hide)
     */
    async renderMessage(text, type = 'info', container, duration = 5000) {
      await this._ensureRenderer();
      this.renderer.renderMessage(text, type, container, duration);
    }

    // ═══════════════════════════════════════════════════════════
    // Dashboard Rendering (zDash Event)
    // ═══════════════════════════════════════════════════════════

    /**
     * Render dashboard with sidebar navigation (uses zTheme classes)
     * @param {Object} config - Dashboard configuration
     * @param {string} config.folder - Base folder for panel discovery
     * @param {Array<string>} config.sidebar - List of panel names
     * @param {string} config.default - Default panel to load
     */
    async _renderDashboard(config) {
      const { folder, sidebar, default: defaultPanel } = config;
      
      console.log('[Dashboard] Rendering with config:', config);
      
      // Load panel metadata to get icons/labels
      const panelMeta = await this._loadPanelMetadata(folder, sidebar);
      
      // Create dashboard using zTheme vertical navigation classes
      // Reference: /Users/galnachshon/Projects/zTheme/Manual/ztheme-navs.html (line 240+)
      const dashboardHTML = `
        <div class="zContainer">
          <div class="zVertical-layout">
            <ul class="zNav zNav-pills zFlex-column zDash-sidebar" role="tablist">
              ${sidebar.map(panel => {
                const meta = panelMeta[panel] || { icon: 'bi-file-text', label: panel };
                // Render Bootstrap Icon if icon class provided
                const iconHTML = meta.icon ? `<i class="bi ${meta.icon}"></i> ` : '';
                return `
                  <li class="zNav-item" role="presentation">
                    <a href="#" 
                       data-panel="${panel}" 
                       class="zNav-link ${panel === defaultPanel ? 'zActive' : ''}"
                       role="tab"
                       aria-selected="${panel === defaultPanel ? 'true' : 'false'}">
                      ${iconHTML}${meta.label}
                    </a>
                  </li>
                `;
              }).join('')}
            </ul>
            <div class="zTab-content" id="dashboard-panel-content">
              <!-- Panel content loads here -->
            </div>
          </div>
        </div>
      `;
      
      // 🔧 IMPROVED: Preserve existing content from chunk (like ProfileCard)
      // This allows multiple zKeys to render before special events (e.g., ProfileCard + Dashboard)
      if (this._zVaFElement) {
        // Check if there's pre-rendered content (from same chunk render cycle)
        const existingContent = this._zVaFElement.innerHTML.trim();
        const hasLoadingSpinner = existingContent.includes('zSpinner');
        
        // If there's real content (not just loading state), preserve it
        if (existingContent && !hasLoadingSpinner) {
          console.log('[Dashboard] 🎨 Preserving existing content before dashboard');
          this.logger.log('[Dashboard] Preserving existing content from chunk');
          // Append dashboard AFTER existing content
          this._zVaFElement.insertAdjacentHTML('beforeend', dashboardHTML);
        } else {
          // No existing content or only spinner, replace normally
          this._zVaFElement.innerHTML = dashboardHTML;
        }
      }
      
      // Set up click handlers (scoped to dashboard sidebar only)
      const links = document.querySelectorAll('.zDash-sidebar .zNav-link');
      links.forEach(link => {
        link.addEventListener('click', async (e) => {
          e.preventDefault();
          const panelName = link.dataset.panel;
          
          // Update active state
          links.forEach(l => {
            l.classList.remove('zActive');
            l.setAttribute('aria-selected', 'false');
          });
          link.classList.add('zActive');
          link.setAttribute('aria-selected', 'true');
          
          // Load panel content
          await this._loadDashboardPanel(folder, panelName);
        });
      });
      
      // Auto-load default panel
      await this._loadDashboardPanel(folder, defaultPanel);
    }

    /**
     * Load panel metadata (icons, labels) from backend
     * @param {string} folder - Base folder path
     * @param {Array<string>} sidebar - Panel names
     * @returns {Object} Metadata keyed by panel name
     */
    async _loadPanelMetadata(folder, sidebar) {
      const metadata = {};
      
      for (const panelName of sidebar) {
        try {
          // Request panel metadata from backend
          const zPath = `${folder}.zUI.${panelName}`;
          const response = await fetch(`/api/dashboard/panel/meta?zPath=${encodeURIComponent(zPath)}`);
          const data = await response.json();
          
          if (data.success && data.meta) {
            metadata[panelName] = {
              icon: data.meta.panel_icon || 'bi-file-text',
              label: data.meta.panel_label || panelName
            };
          }
        } catch (e) {
          console.warn(`[Dashboard] Could not load metadata for ${panelName}:`, e);
          metadata[panelName] = { icon: 'bi-file-text', label: panelName };
        }
      }
      
      return metadata;
    }

    /**
     * Load and render a dashboard panel
     * @param {string} folder - Base folder path
     * @param {string} panelName - Panel name to load
     */
    async _loadDashboardPanel(folder, panelName) {
      console.log(`[Dashboard] Loading panel: ${panelName}`);
      
      const contentArea = document.getElementById('dashboard-panel-content');
      if (!contentArea) return;
      
      // Show loading state
      contentArea.innerHTML = '<div class="zSpinner-border" role="status"><span class="zVisually-hidden">Loading...</span></div>';
      
      try {
        // Request walker execution for the panel
        const requestData = {
          event: 'execute_walker',
          zBlock: panelName,
          zVaFile: `zUI.${panelName}`,
          zVaFolder: folder,
          _renderTarget: 'dashboard-panel-content' // Tell backend where to render
        };
        
        // Clear the panel content area to prepare for new chunk rendering
        contentArea.innerHTML = '';
        
        // Send the walker execution request (must be JSON string)
        await this.connection.send(JSON.stringify(requestData));
        
      } catch (error) {
        console.error(`[Dashboard] Error loading panel ${panelName}:`, error);
        contentArea.innerHTML = '<div class="zAlert zAlert-danger">Failed to load panel</div>';
      }
    }

    // ═══════════════════════════════════════════════════════════
    // Hook Management
    // ═══════════════════════════════════════════════════════════

    /**
     * Register a new hook at runtime
     * @param {string} hookName - Name of the hook
     * @param {Function} fn - Hook function
     */
    registerHook(hookName, fn) {
      this.hooks.register(hookName, fn);
    }

    /**
     * Unregister a hook
     * @param {string} hookName - Name of the hook
     */
    unregisterHook(hookName) {
      this.hooks.unregister(hookName);
    }

    /**
     * List all registered hooks
     * @returns {Array<string>}
     */
    listHooks() {
      return this.hooks.list();
    }
  }

  // ═══════════════════════════════════════════════════════════
  // Export
  // ═══════════════════════════════════════════════════════════

  return BifrostClient;
}));
