/**
 * Navigation System - Bottom Tab Bar with Swipe Gestures
 * Mobile-first design inspired by TradingView + Binance
 */

class NavigationController {
    constructor() {
        this.currentTab = 'chart';
        this.tabs = ['chart', 'indicators', 'ai', 'history'];
        this.touchStartX = 0;
        this.touchEndX = 0;
        this.swipeThreshold = 50;
        this.historyModule = null;
        
        this.init();
    }
    
    init() {
        // Check if bottom nav already exists in HTML
        const existingNav = document.querySelector('.bottom-nav');
        
        if (existingNav) {
            // Use existing HTML nav from chart.html
            this.navElement = existingNav;
            this.indicator = existingNav.querySelector('.nav-indicator');
            console.log('✅ Using existing bottom-nav from HTML');
        } else {
            // Fallback: create nav dynamically
            this.createBottomNav();
        }
        
        this.setupEventListeners();
        // this.setupSwipeGestures(); // DISABLED: Conflicts with chart zoom/pan/pinch gestures
        console.log('✅ Navigation system initialized (4 tabs: chart, indicators, ai, history)');
    }
    
    /**
     * Create bottom navigation bar HTML with sliding indicator (fallback if not in HTML)
     */
    createBottomNav() {
        const nav = document.createElement('nav');
        nav.className = 'bottom-nav';
        nav.innerHTML = `
            <div class="bottom-nav-container">
                <div class="nav-indicator" id="nav-indicator"></div>
                <button class="nav-item active" data-tab="chart">
                    <span class="nav-item-icon">�</span>
                    <span class="nav-item-label">Chart</span>
                </button>
                <button class="nav-item" data-tab="indicators">
                    <span class="nav-item-icon">�</span>
                    <span class="nav-item-label">Indicators</span>
                </button>
                <button class="nav-item" data-tab="ai">
                    <span class="nav-item-icon">🤖</span>
                    <span class="nav-item-label">AI</span>
                </button>
                <button class="nav-item" data-tab="history">
                    <span class="nav-item-icon">📋</span>
                    <span class="nav-item-label">History</span>
                </button>
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
        const items = Array.from(container.querySelectorAll('.nav-item'));
        const index = items.indexOf(activeItem);
        const width = 100 / items.length;
        
        this.indicator.style.width = `calc(${width}% - 4px)`;
        this.indicator.style.left = `calc(${width * index}% + 2px)`;
    }
    
    /**
     * Setup click event listeners for tabs
     */
    setupEventListeners() {
        const navItems = this.navElement.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
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
        // Hide all tab content sections
        const sections = document.querySelectorAll('[data-tab-content]');
        sections.forEach(section => {
            section.style.display = 'none';
        });
        
        // Show selected section
        const activeSection = document.querySelector(`[data-tab-content="${tabName}"]`);
        if (activeSection) {
            activeSection.style.display = 'block';
            
            // Special handling for chart tab
            if (tabName === 'chart') {
                const chartContainer = document.getElementById('chartContainer');
                if (chartContainer) {
                    // Ensure chart container is visible
                    chartContainer.style.display = 'block';
                    
                    // CRITICAL: Resize chart after showing container
                    // Chart needs to recalculate dimensions when container becomes visible
                    setTimeout(() => {
                        if (typeof chart !== 'undefined' && chart) {
                            const width = chartContainer.clientWidth;
                            const height = chartContainer.clientHeight;
                            
                            console.log(`📊 Resizing chart on tab show: ${width}x${height}`);
                            
                            chart.applyOptions({
                                width: width,
                                height: height,
                            });
                            
                            // Trigger chart redraw
                            chart.timeScale().scrollToPosition(0, false);
                        }
                    }, 50); // Small delay to ensure container is fully visible
                }
            }
            
            // Special handling for indicators tab
            if (tabName === 'indicators' && window.indicatorsTab) {
                // Reload indicators when tab is shown
                if (typeof symbol !== 'undefined' && typeof currentTimeframe !== 'undefined') {
                    window.indicatorsTab.setContext(symbol, currentTimeframe);
                }
            }
            
            // Special handling for history tab
            if (tabName === 'history' && !this.historyModule) {
                this.initializeHistoryModule();
            }
        }
    }
    
    /**
     * Initialize History Module
     */
    initializeHistoryModule() {
        if (typeof AnalysisHistory === 'undefined') {
            console.error('❌ AnalysisHistory class not found');
            return;
        }
        
        // Use existing historyTab instance if available, or create new one
        if (window.historyTab) {
            this.historyModule = window.historyTab;
            console.log('✅ Using existing History Tab instance');
        } else {
            const tg = window.Telegram?.WebApp;
            const userId = tg?.initDataUnsafe?.user?.id || 6228875204;
            
            this.historyModule = new AnalysisHistory(userId);
            window.historyTab = this.historyModule;
            console.log('✅ Created new History Tab instance for user:', userId);
        }
        
        // Initialize the History Tab (triggers loading)
        this.historyModule.init();
        console.log('✅ History Tab initialized and loading data...');
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
