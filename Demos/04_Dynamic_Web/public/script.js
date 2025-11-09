/**
 * zServer Demo - Interactive JavaScript
 * Proves JavaScript execution and DOM manipulation
 */

// ============================================
// Page Load Handler
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🌐 zServer Demo - JavaScript loaded successfully!');
    console.log('✅ Proof: JavaScript files are served and executed');
    
    initializeTestButton();
    displayPageInfo();
    addAnimations();
});

// ============================================
// Test Button Handler
// ============================================

function initializeTestButton() {
    const testBtn = document.getElementById('testBtn');
    
    if (!testBtn) return;
    
    testBtn.addEventListener('click', () => {
        // Create notification
        showNotification('✨ JavaScript is working!', 'success');
        
        // Log to console
        console.log('🎯 Test button clicked - JavaScript execution confirmed');
        
        // Add visual feedback
        testBtn.style.transform = 'scale(0.95)';
        setTimeout(() => {
            testBtn.style.transform = 'scale(1)';
        }, 100);
    });
}

// ============================================
// Notification System
// ============================================

function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '1rem 1.5rem',
        borderRadius: '0.5rem',
        background: type === 'success' ? '#10b981' : '#a855f7',
        color: 'white',
        fontWeight: '600',
        boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)',
        zIndex: '9999',
        animation: 'slideIn 0.3s ease-out',
        fontSize: '1rem'
    });
    
    // Add CSS animation
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Append to body
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ============================================
// Page Info Display
// ============================================

function displayPageInfo() {
    const pageInfo = {
        url: window.location.href,
        protocol: window.location.protocol,
        hostname: window.location.hostname,
        port: window.location.port,
        pathname: window.location.pathname,
        timestamp: new Date().toLocaleString()
    };
    
    console.log('📊 Page Information:', pageInfo);
    console.log('🔧 zServer Configuration:');
    console.log('   - Serving via HTTP protocol');
    console.log('   - Port: 8080 (default)');
    console.log('   - Host: 127.0.0.1 (localhost)');
    console.log('   - CORS: Enabled');
    console.log('   - Directory listing: Disabled');
}

// ============================================
// Animations
// ============================================

function addAnimations() {
    // Fade-in animation for content
    const content = document.querySelector('.content');
    if (content) {
        content.style.opacity = '0';
        content.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            content.style.transition = 'all 0.6s ease-out';
            content.style.opacity = '1';
            content.style.transform = 'translateY(0)';
        }, 100);
    }
    
    // Hover animations for features
    const features = document.querySelectorAll('.feature');
    features.forEach((feature, index) => {
        feature.style.opacity = '0';
        feature.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            feature.style.transition = 'all 0.5s ease-out';
            feature.style.opacity = '1';
            feature.style.transform = 'translateY(0)';
        }, 200 + (index * 100));
    });
}

// ============================================
// Console Art
// ============================================

console.log(`
╔══════════════════════════════════════════╗
║                                          ║
║       ⚡ zCLI - zServer Demo             ║
║                                          ║
║   🌐 HTTP Static File Server            ║
║   🧵 Background Threading                ║
║   🔒 CORS Enabled                        ║
║   📊 Health Check API                    ║
║                                          ║
║   Layer 3: Web Server - Demo #3.1       ║
║                                          ║
╚══════════════════════════════════════════╝
`);

