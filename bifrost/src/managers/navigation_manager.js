/**
 * NavigationManager - Handles client-side navigation (SPA-style routing)
 * 
 * Responsibilities:
 * - Enable client-side navigation (intercept clicks on navbar links)
 * - Handle browser back/forward buttons (popstate)
 * - Navigate to routes via WebSocket (no page reload)
 * - Fetch route configuration from backend
 * - Send walker execution requests
 * - Update browser URL without reload
 * 
 * Extracted from bifrost_client.js (Phase 3.3)
 */

export class NavigationManager {
  constructor(client) {
    this.client = client;
    this.logger = client.logger;
  }

  /**
   * Enable client-side navigation (SPA-style routing)
   */
  enableClientSideNavigation() {
    if (typeof document === 'undefined') return;
    
    // Remove any existing listeners to avoid duplicates
    if (this.client._navClickHandler) {
      document.removeEventListener('click', this.client._navClickHandler, true);
    }
    
    // Create navigation click handler
    this.client._navClickHandler = async (e) => {
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
      await this.navigateToRoute(href);
    };
    
    // Use capture phase to ensure we intercept before other handlers
    document.addEventListener('click', this.client._navClickHandler, true);
    
    // Handle browser back/forward buttons
    if (!this.client._popstateHandler) {
      this.client._popstateHandler = async (e) => {
        console.log('[ClientNav] ⏪ Browser back/forward detected');
        const path = window.location.pathname;
        
        // Navigate to the new path via WebSocket
        await this.navigateToRoute(path, { skipHistory: true });
      };
      
      window.addEventListener('popstate', this.client._popstateHandler);
    }
    
    console.log('[ClientNav] ✅ Client-side navigation enabled');
  }

  /**
   * Navigate to a route via WebSocket (client-side navigation)
   * @param {string} routePath - Path to navigate to (e.g., '/zAbout', '/zAccount')
   * @param {Object} options - Navigation options
   */
  async navigateToRoute(routePath, options = {}) {
    const { skipHistory = false } = options;
    
    // Mark as client-side navigation to prevent beforeunload from triggering
    this.client._isClientSideNav = true;
    
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
      if (this.client._zVaFElement) {
        this.client._zVaFElement.innerHTML = '<div class="zText-center zp-4">Loading...</div>';
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
      this.client.connection.send(JSON.stringify(walkerRequest));
      
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
      this.client._isClientSideNav = false;
      
      // Show error in content area
      if (this.client._zVaFElement) {
        this.client._zVaFElement.innerHTML = `
          <div class="zAlert zAlert-danger zmt-4">
            <strong>Navigation Error:</strong> ${error.message}
          </div>
        `;
      }
    } finally {
      // Reset flag after navigation attempt (success or fail)
      setTimeout(() => {
        this.client._isClientSideNav = false;
      }, 100);
    }
  }
}

export default NavigationManager;

