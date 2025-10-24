/**
 * ═══════════════════════════════════════════════════════════════
 * zTheme Loader - Centralized Theme Management
 * ═══════════════════════════════════════════════════════════════
 * 
 * Automatically loads all zTheme CSS files in the correct order.
 * Can be used by any JavaScript application (zBifrost, standalone apps, etc.)
 * 
 * @version 1.0.0
 * @author Gal Nachshon
 * 
 * Usage:
 *   // Auto-load (default path)
 *   zThemeLoader.load();
 * 
 *   // Custom base path
 *   zThemeLoader.load('/custom/path/to/zTheme');
 * 
 *   // Check if loaded
 *   if (zThemeLoader.isLoaded()) { ... }
 * 
 *   // Unload all theme CSS
 *   zThemeLoader.unload();
 */

(function(root) {
  'use strict';

  /**
   * zTheme CSS files in dependency order
   * Core files first, then components, then utilities
   */
  const THEME_FILES = [
    // 1. Core - Variables and base styles
    'css_vars.css',
    'zMain.css',
    'zTypography.css',
    
    // 2. Layout
    'zContainers.css',
    'zSpacing.css',
    'zPage.css',
    
    // 3. Components
    'zButtons.css',
    'zInputs.css',
    'zTables.css',
    'zAlerts.css',
    'zPanels.css',
    'zNav.css',
    'zModal.css',
    'zPagination.css',
    
    // 4. Specialized
    'zImages.css',
    'zMedia.css',
    'zEffects.css',
    'zDashboard.css',
    'zHome.css',
    'zLogin.css',
    'zShop.css',
    'zReviews.css',
    'zAddToCart.css',
    'zFooter.css',
    
    // 5. Development (optional - only in dev mode)
    // 'zDev.css'
  ];

  /**
   * Default base paths to try (in order)
   */
  const DEFAULT_PATHS = [
    '/zCLI/utils/zTheme',           // Absolute from web root
    '../zCLI/utils/zTheme',         // Relative (one level up)
    '../../zCLI/utils/zTheme',      // Relative (two levels up)
    '../../../zCLI/utils/zTheme'    // Relative (three levels up)
  ];

  class ZThemeLoader {
    constructor() {
      this.loadedFiles = [];
      this.basePath = null;
      this.isLoading = false;
    }

    /**
     * Check if zTheme is already loaded
     * @returns {boolean}
     */
    isLoaded() {
      return this.loadedFiles.length > 0;
    }

    /**
     * Auto-detect the correct base path by trying to load css_vars.css
     * @returns {Promise<string|null>} The working base path or null
     */
    async detectBasePath() {
      for (const path of DEFAULT_PATHS) {
        try {
          const testUrl = `${path}/css/css_vars.css`;
          const response = await fetch(testUrl, { method: 'HEAD' });
          if (response.ok) {
            console.log(`[zTheme] ✅ Detected base path: ${path}`);
            return path;
          }
        } catch (e) {
          // Continue to next path
        }
      }
      console.warn('[zTheme] ⚠️  Could not auto-detect base path');
      return null;
    }

    /**
     * Load a single CSS file
     * @param {string} href - Full path to CSS file
     * @param {string} id - Unique ID for the link element
     * @returns {Promise<void>}
     */
    loadCSSFile(href, id) {
      return new Promise((resolve, reject) => {
        // Check if already loaded
        if (document.getElementById(id)) {
          resolve();
          return;
        }

        const link = document.createElement('link');
        link.id = id;
        link.rel = 'stylesheet';
        link.href = href;
        
        link.onload = () => resolve();
        link.onerror = () => reject(new Error(`Failed to load: ${href}`));
        
        document.head.appendChild(link);
      });
    }

    /**
     * Load all zTheme CSS files
     * @param {string} [customBasePath] - Optional custom base path
     * @param {Object} [options] - Loading options
     * @param {boolean} [options.includeDev=false] - Include zDev.css
     * @param {boolean} [options.minimal=false] - Load only essential files
     * @returns {Promise<void>}
     */
    async load(customBasePath = null, options = {}) {
      // Prevent duplicate loading
      if (this.isLoading) {
        console.log('[zTheme] Already loading...');
        return;
      }

      if (this.isLoaded()) {
        console.log('[zTheme] Already loaded');
        return;
      }

      this.isLoading = true;

      try {
        // Determine base path
        this.basePath = customBasePath || await this.detectBasePath();
        
        if (!this.basePath) {
          throw new Error('Could not determine zTheme base path');
        }

        // Determine which files to load
        let filesToLoad = THEME_FILES;
        
        if (options.minimal) {
          // Minimal: Only core + essential components
          filesToLoad = [
            'css_vars.css',
            'zMain.css',
            'zTypography.css',
            'zContainers.css',
            'zButtons.css',
            'zTables.css',
            'zAlerts.css'
          ];
        }

        if (options.includeDev) {
          filesToLoad = [...filesToLoad, 'zDev.css'];
        }

        // Load all CSS files sequentially (to preserve order)
        console.log(`[zTheme] Loading ${filesToLoad.length} CSS files...`);
        
        for (const file of filesToLoad) {
          const href = `${this.basePath}/css/${file}`;
          const id = `zTheme-${file.replace('.css', '')}`;
          
          try {
            await this.loadCSSFile(href, id);
            this.loadedFiles.push(file);
          } catch (error) {
            console.warn(`[zTheme] ⚠️  Failed to load ${file}:`, error.message);
            // Continue loading other files even if one fails
          }
        }

        console.log(`[zTheme] ✅ Loaded ${this.loadedFiles.length}/${filesToLoad.length} files`);
        
      } catch (error) {
        console.error('[zTheme] ❌ Failed to load theme:', error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    }

    /**
     * Unload all zTheme CSS files
     */
    unload() {
      document.querySelectorAll('link[id^="zTheme-"]').forEach(link => {
        link.remove();
      });
      this.loadedFiles = [];
      this.basePath = null;
      console.log('[zTheme] Unloaded all theme files');
    }

    /**
     * Reload theme (useful for development)
     * @param {string} [customBasePath]
     * @param {Object} [options]
     */
    async reload(customBasePath = null, options = {}) {
      this.unload();
      await this.load(customBasePath, options);
    }

    /**
     * Get list of loaded files
     * @returns {Array<string>}
     */
    getLoadedFiles() {
      return [...this.loadedFiles];
    }

    /**
     * Get current base path
     * @returns {string|null}
     */
    getBasePath() {
      return this.basePath;
    }
  }

  // Create singleton instance
  const zThemeLoader = new ZThemeLoader();

  // Export to global scope
  root.zThemeLoader = zThemeLoader;

  // Also export class for advanced usage
  root.ZThemeLoader = ZThemeLoader;

  // Auto-load on DOMContentLoaded (can be disabled by setting window.zThemeAutoLoad = false)
  if (typeof window !== 'undefined' && typeof document !== 'undefined') {
    const autoLoad = () => {
      if (window.zThemeAutoLoad !== false) {
        zThemeLoader.load().catch(err => {
          console.warn('[zTheme] Auto-load failed:', err.message);
        });
      }
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', autoLoad);
    } else {
      autoLoad();
    }
  }

  // Log initialization
  console.log(`
╔═══════════════════════════════════════════════════════════════╗
║  zTheme Loader v1.0.0                                         ║
║  ───────────────────────────────────────────────────────────  ║
║  Auto-loading ${THEME_FILES.length} CSS files...                                ║
║  Disable: window.zThemeAutoLoad = false                      ║
╚═══════════════════════════════════════════════════════════════╝
  `);

})(typeof self !== 'undefined' ? self : this);

