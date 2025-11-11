/**
 * Navigation System - Bottom Tab Bar with Swipe Gestures
 * Mobile-first design inspired by TradingView + Binance
 */

class NavigationController {
    constructor() {
        this.currentTab = 'chart';
        this.tabs = ['chart', 'indicators', 'ai'];
        this.touchStartX = 0;
        this.touchEndX = 0;
        this.swipeThreshold = 50; // минимальное расстояние свайпа в пикселях
        
        this.init();
    }
    
    init() {
        this.createBottomNav();
        this.setupEventListeners();
        // this.setupSwipeGestures(); // DISABLED: Conflicts with chart zoom/pan/pinch gestures
        console.log('✅ Navigation system initialized (swipe gestures disabled)');
    }
    
    /**
     * Create bottom navigation bar HTML with sliding indicator
     */
    createBottomNav() {
        const nav = document.createElement('div');
        nav.className = 'bottom-nav safe-bottom';
        nav.innerHTML = `
            <div class="bottom-nav-container">
                <div class="nav-indicator"></div>
                <div class="nav-item active" data-tab="chart">
                    <div class="nav-item-icon">📊</div>
                    <div class="nav-item-label">Chart</div>
                </div>
                <div class="nav-item" data-tab="indicators">
                    <div class="nav-item-icon">📈</div>
                    <div class="nav-item-label">Indicators</div>
                </div>
                <div class="nav-item" data-tab="ai">
                    <div class="nav-item-icon">🤖</div>
                    <div class="nav-item-label">AI</div>
                </div>
            </div>
        `;
        
        document.body.appendChild(nav);
        this.navElement = nav;
        this.indicator = nav.querySelector('.nav-indicator');
        
        // Set initial indicator position
        setTimeout(() => this.updateIndicator(), 0);
    }
    
    /**
     * Update sliding indicator position
     */
    updateIndicator() {
        if (!this.indicator) return;
        
        const activeItem = this.navElement.querySelector('.nav-item.active');
        if (!activeItem) return;
        
        const container = this.navElement.querySelector('.bottom-nav-container');
        const containerRect = container.getBoundingClientRect();
        const itemRect = activeItem.getBoundingClientRect();
        
        const left = itemRect.left - containerRect.left;
        const width = itemRect.width;
        
        this.indicator.style.transform = `translateX(${left}px)`;
        this.indicator.style.width = `${width}px`;
    }
    
    /**
     * Setup click event listeners for tabs
     */
    setupEventListeners() {
        const navItems = this.navElement.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                this.switchTab(tab);
            });
        });
    }
    
    /**
     * Setup swipe gestures for tab navigation
     */
    setupSwipeGestures() {
        const contentArea = document.getElementById('content-container') || document.body;
        
        contentArea.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        contentArea.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe();
        }, { passive: true });
    }
    
    /**
     * Handle swipe gesture
     */
    handleSwipe() {
        const distance = this.touchEndX - this.touchStartX;
        
        // Swipe right → Previous tab
        if (distance > this.swipeThreshold) {
            this.navigateToPreviousTab();
        }
        // Swipe left → Next tab
        else if (distance < -this.swipeThreshold) {
            this.navigateToNextTab();
        }
    }
    
    /**
     * Navigate to previous tab
     */
    navigateToPreviousTab() {
        const currentIndex = this.tabs.indexOf(this.currentTab);
        if (currentIndex > 0) {
            this.switchTab(this.tabs[currentIndex - 1]);
        }
    }
    
    /**
     * Navigate to next tab
     */
    navigateToNextTab() {
        const currentIndex = this.tabs.indexOf(this.currentTab);
        if (currentIndex < this.tabs.length - 1) {
            this.switchTab(this.tabs[currentIndex + 1]);
        }
    }
    
    /**
     * Switch to specified tab
     * @param {string} tabName - Name of the tab to switch to
     */
    switchTab(tabName) {
        if (tabName === this.currentTab) return;
        
        // Update active state
        const navItems = this.navElement.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            if (item.dataset.tab === tabName) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
        
        // Update sliding indicator
        this.updateIndicator();
        
        // Hide/show content sections
        this.showTabContent(tabName);
        
        // Haptic feedback (iOS)
        this.hapticFeedback('light');
        
        // Update current tab
        this.currentTab = tabName;
        
        // Emit custom event for other components
        window.dispatchEvent(new CustomEvent('tab-changed', {
            detail: { tab: tabName }
        }));
        
        console.log(`📱 Switched to tab: ${tabName}`);
    }
    
    /**
     * Show content for specified tab
     * @param {string} tabName 
     */
    showTabContent(tabName) {
        // Hide all sections
        const sections = document.querySelectorAll('[data-tab-content]');
        sections.forEach(section => {
            section.style.display = 'none';
        });
        
        // Show selected section
        const activeSection = document.querySelector(`[data-tab-content="${tabName}"]`);
        if (activeSection) {
            activeSection.style.display = 'block';
            // Add slide-in animation
            activeSection.style.animation = 'fadeIn 0.3s ease-out';
        }
    }
    
    /**
     * Haptic feedback for iOS
     * @param {string} type - 'light', 'medium', 'heavy', 'success', 'error'
     */
    hapticFeedback(type = 'light') {
        if (typeof window.Telegram !== 'undefined' && window.Telegram.WebApp) {
            // Telegram WebApp haptic feedback
            window.Telegram.WebApp.HapticFeedback.impactOccurred(type);
        } else if (navigator.vibrate) {
            // Fallback to vibration API
            const patterns = {
                light: 10,
                medium: 20,
                heavy: 30,
                success: [10, 50, 10],
                error: [10, 100, 10, 100, 10]
            };
            navigator.vibrate(patterns[type] || 10);
        }
    }
    
    /**
     * Get current active tab
     * @returns {string}
     */
    getCurrentTab() {
        return this.currentTab;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NavigationController;
}
