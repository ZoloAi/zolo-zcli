/**
 * ═══════════════════════════════════════════════════════════════
 * Theme Loader Module - zTheme CSS Integration
 * ═══════════════════════════════════════════════════════════════
 * Version: 1.0.1 - Fixed path detection for /static/client/css/
 */

export class ThemeLoader {
  constructor(logger) {
    this.logger = logger;
    this.loaded = false;
  }

  /**
   * Load zTheme CSS files
   */
  load(baseUrl = null) {
    if (this.loaded) {
      this.logger.log('⚠️ zTheme already loaded, skipping...');
      return;
    }

    const themeUrl = baseUrl || this._detectBaseUrl();
    this.logger.log('🎨 Loading zTheme from:', themeUrl);
    this.logger.log('🔍 First CSS will be:', `${themeUrl}/css/css_vars.css`);

    const cssFiles = [
      'css/css_vars.css',
      'css/zMain.css',
      'css/zButtons.css',
      'css/zTables.css',
      'css/zInputs.css',
      'css/zContainers.css',
      'css/zTypography.css',
      'css/zAlerts.css',
      'css/zModal.css',
      'css/zNav.css',
      'css/zPanels.css',
      'css/zSpacing.css',
      'css/zEffects.css',
      'css/zDashboard.css',
      'css/zProgress.css',     // Week 4.2: Progress bar widgets
      'css/zSpinner.css'       // Week 4.2: Spinner widgets
    ];

    cssFiles.forEach(file => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = `${themeUrl}/${file}`;
      link.dataset.ztheme = 'true';
      link.onerror = () => {
        this.logger.log(`⚠️ Failed to load: ${file}`);
      };
      document.head.appendChild(link);
    });

    this.loaded = true;
    this.logger.log('✅ zTheme loaded');
  }

  /**
   * Detect base URL for zTheme CSS files
   * @private
   */
  _detectBaseUrl() {
    // Try to detect from current script location
    const scripts = document.getElementsByTagName('script');
    for (let script of scripts) {
      // Match both bifrost_client.js and bifrost_client_modular.js
      if (script.src && script.src.includes('bifrost_client')) {
        // Extract base path: /static/client/src/bifrost_client.js -> /static/client
        let scriptUrl = script.src;
        this.logger.log('🔍 Script URL:', scriptUrl);
        
        // Remove the filename to get directory
        let basePath = scriptUrl.substring(0, scriptUrl.lastIndexOf('/'));
        this.logger.log('🔍 After removing filename:', basePath);
        
        // If path ends with /src, go up one level to get /client/
        if (basePath.endsWith('/src')) {
          basePath = basePath.substring(0, basePath.length - 4);
          this.logger.log('🔍 After removing /src:', basePath);
        }
        
        // CSS files are in /static/client/css/
        return basePath;
      }
    }

    // No fallback - zTheme must be co-located with BifrostClient
    throw new Error('BifrostClient script not found - cannot auto-detect zTheme path');
  }

  /**
   * Check if theme is loaded
   */
  isLoaded() {
    return this.loaded;
  }
}

