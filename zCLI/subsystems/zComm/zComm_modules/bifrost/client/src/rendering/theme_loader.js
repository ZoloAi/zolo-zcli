/**
 * ═══════════════════════════════════════════════════════════════
 * Theme Loader Module - zTheme CSS Integration
 * ═══════════════════════════════════════════════════════════════
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
        // Extract base path and navigate to zTheme
        const basePath = script.src.substring(0, script.src.lastIndexOf('/'));
        // Handle both local and CDN paths
        // Local: .../zCLI/subsystems/zComm/zComm_modules/bifrost -> .../zCLI/subsystems/zTheme
        // CDN: .../zComm/zComm_modules/bifrost -> .../zTheme
        return basePath.replace(
          /\/zComm\/zComm_modules\/bifrost$/,
          '/zTheme'
        );
      }
    }

    // Fallback to GitHub CDN
    return 'https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@main/zCLI/subsystems/zTheme';
  }

  /**
   * Check if theme is loaded
   */
  isLoaded() {
    return this.loaded;
  }
}

