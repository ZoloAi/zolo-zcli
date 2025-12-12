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
      // Core Variables & Base Styles
      'css/css_vars.css',
      'css/zReboot.css',
      'css/zMain.css',
      'css/zTypography.css',
      
      // Layout & Structure
      'css/zContainers.css',
      'css/zSpacing.css',
      
      // Components
      'css/zAccordion.css',
      'css/zAlerts.css',
      'css/zBadges.css',
      'css/zBreadcrumb.css',
      'css/zButtons.css',
      'css/zButtonGroup.css',
      'css/zCards.css',
      'css/zCarousel.css',
      'css/zCollapse.css',
      'css/zDropdown.css',
      'css/zFigures.css',
      'css/zForms.css',       // Modern form controls (replaces zInputs.css)
      'css/zListGroup.css',
      'css/zModal.css',
      'css/zOffcanvas.css',
      'css/zPagination.css',
      'css/zPopover.css',
      'css/zScrollspy.css',
      'css/zToast.css',
      'css/zTooltip.css',
      'css/zLinks.css',
      'css/zRatio.css',
      'css/zVisually.css',
      'css/zBackground.css',
      'css/zBorders.css',
      'css/zColors.css',
      'css/zDisplay.css',
      'css/zFlex.css',
      'css/zIcons.css',
      'css/zInteractions.css',
      'css/zOverflow.css',
      'css/zPosition.css',
      'css/zShadows.css',
      'css/zSizing.css',
      'css/zText.css',
      'css/zVerticalAlign.css',
      'css/zNav.css',
      'css/zNavbar.css',
      'css/zPanels.css',
      'css/zTables.css',
      'css/zFooter.css',
      
      // Widgets
      'css/zProgress.css',
      'css/zSpinner.css',
      
      // Effects & Utilities
      'css/zEffects.css',
      'css/zMedia.css',
      'css/zImages.css',
      
      // E-commerce (Optional)
      'css/zShop.css',
      'css/zAddToCart.css',
      
      // Authentication
      'css/zLogin.css',
      
      // Development Tools
      'css/zDev.css'
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
        return basePath.replace(
          '/zComm/zComm_modules/zBifrost',
          '/zTheme'
        );
      }
    }

    // Fallback to GitHub CDN
    return 'https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@v1.5.4/zCLI/subsystems/zTheme';
  }

  /**
   * Check if theme is loaded
   */
  isLoaded() {
    return this.loaded;
  }
}

