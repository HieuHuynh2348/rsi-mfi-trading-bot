/**
 * Indicator Panel - Collapsible Panel with Drag Handle
 * Mobile-optimized with snap positions and spring animations
 */

class IndicatorPanel {
    constructor(options = {}) {
        this.container = options.container || document.body;
        this.indicators = options.indicators || [];
        this.snapPositions = {
            full: 0,              // Fully expanded
            half: 0.5,            // Half expanded
            mini: 0.85            // Minimized (showing handle only)
        };
        this.currentPosition = 'mini'; // Start minimized
        this.isDragging = false;
        this.startY = 0;
        this.startTranslateY = 0;
        this.currentTranslateY = 0;
        
        this.init();
    }
    
    init() {
        this.createPanel();
        this.calculateSnapPositions();
        this.setupEventListeners();
        this.snapToPosition('mini', false); // Start minimized
        console.log('✅ Indicator panel initialized');
    }
    
    /**
     * Create indicator panel HTML
     */
    createPanel() {
        const panel = document.createElement('div');
        panel.className = 'indicator-panel collapsed';
        panel.id = 'indicator-panel';
        
        panel.innerHTML = `
            <div class="indicator-panel-handle"></div>
            <div class="indicator-panel-content">
                <div class="indicator-panel-header">
                    <h3 style="color: var(--text-primary); font-size: var(--font-lg); font-weight: var(--weight-semibold); margin-bottom: var(--space-md);">
                        Technical Indicators
                    </h3>
                </div>
                <div class="indicator-cards" id="indicator-cards">
                    ${this.renderIndicators()}
                </div>
            </div>
        `;
        
        this.container.appendChild(panel);
        this.element = panel;
        this.handle = panel.querySelector('.indicator-panel-handle');
        this.content = panel.querySelector('.indicator-panel-content');
    }
    
    /**
     * Render indicator cards
     */
    renderIndicators() {
        if (this.indicators.length === 0) {
            return `
                <div style="text-align: center; padding: var(--space-xl); color: var(--text-secondary);">
                    <div style="font-size: 48px; margin-bottom: var(--space-md);">📊</div>
                    <div>No indicators loaded yet</div>
                    <div style="font-size: var(--font-sm); margin-top: var(--space-sm);">
                        Data will appear here when chart loads
                    </div>
                </div>
            `;
        }
        
        return this.indicators.map(indicator => `
            <div class="indicator-card">
                <div class="indicator-header">
                    <span class="indicator-title">${indicator.name}</span>
                    <label class="toggle-switch">
                        <input type="checkbox" ${indicator.enabled ? 'checked' : ''} data-indicator="${indicator.id}">
                        <span class="toggle-slider"></span>
                    </label>
                </div>
                <div class="indicator-value ${indicator.signal || 'neutral'}">
                    ${indicator.value}
                </div>
                ${indicator.description ? `
                    <div class="indicator-description">
                        ${indicator.description}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }
    
    /**
     * Calculate snap positions based on window height
     */
    calculateSnapPositions() {
        const windowHeight = window.innerHeight;
        const navHeight = 60; // Bottom nav height
        const safeAreaBottom = parseInt(getComputedStyle(document.documentElement)
            .getPropertyValue('--safe-area-inset-bottom')) || 0;
        
        const maxPanelHeight = windowHeight * 0.6; // 60% of screen max
        
        this.snapPositions.full = 0;
        this.snapPositions.half = maxPanelHeight * 0.5;
        this.snapPositions.mini = maxPanelHeight - 40; // Show only handle
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Touch events for drag
        this.handle.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
        this.handle.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        this.handle.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: false });
        
        // Mouse events for desktop testing
        this.handle.addEventListener('mousedown', this.handleMouseDown.bind(this));
        
        // Window resize
        window.addEventListener('resize', () => {
            this.calculateSnapPositions();
            this.snapToPosition(this.currentPosition, false);
        });
        
        // Click handle to toggle between mini and half
        this.handle.addEventListener('click', (e) => {
            if (!this.isDragging) {
                const newPosition = this.currentPosition === 'mini' ? 'half' : 'mini';
                this.snapToPosition(newPosition, true);
            }
        });
    }
    
    /**
     * Handle touch start
     */
    handleTouchStart(e) {
        this.isDragging = true;
        this.startY = e.touches[0].clientY;
        this.startTranslateY = this.currentTranslateY;
        
        // Remove transition for smooth dragging
        this.element.style.transition = 'none';
        
        // Haptic feedback
        this.hapticFeedback('light');
    }
    
    /**
     * Handle touch move
     */
    handleTouchMove(e) {
        if (!this.isDragging) return;
        
        e.preventDefault(); // Prevent scrolling
        
        const currentY = e.touches[0].clientY;
        const deltaY = currentY - this.startY;
        const newTranslateY = this.startTranslateY + deltaY;
        
        // Constrain to bounds
        const maxTranslate = this.snapPositions.mini;
        const minTranslate = this.snapPositions.full;
        
        this.currentTranslateY = Math.max(minTranslate, Math.min(maxTranslate, newTranslateY));
        this.element.style.transform = `translateY(${this.currentTranslateY}px)`;
    }
    
    /**
     * Handle touch end
     */
    handleTouchEnd(e) {
        if (!this.isDragging) return;
        
        this.isDragging = false;
        
        // Determine closest snap position
        const snapPosition = this.findClosestSnapPosition();
        this.snapToPosition(snapPosition, true);
    }
    
    /**
     * Handle mouse down (for desktop testing)
     */
    handleMouseDown(e) {
        this.isDragging = true;
        this.startY = e.clientY;
        this.startTranslateY = this.currentTranslateY;
        this.element.style.transition = 'none';
        
        const handleMouseMove = (e) => {
            if (!this.isDragging) return;
            
            const currentY = e.clientY;
            const deltaY = currentY - this.startY;
            const newTranslateY = this.startTranslateY + deltaY;
            
            const maxTranslate = this.snapPositions.mini;
            const minTranslate = this.snapPositions.full;
            
            this.currentTranslateY = Math.max(minTranslate, Math.min(maxTranslate, newTranslateY));
            this.element.style.transform = `translateY(${this.currentTranslateY}px)`;
        };
        
        const handleMouseUp = () => {
            if (!this.isDragging) return;
            
            this.isDragging = false;
            const snapPosition = this.findClosestSnapPosition();
            this.snapToPosition(snapPosition, true);
            
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
        
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    }
    
    /**
     * Find closest snap position
     */
    findClosestSnapPosition() {
        const positions = Object.entries(this.snapPositions);
        let closestPosition = 'mini';
        let minDistance = Infinity;
        
        positions.forEach(([name, value]) => {
            const distance = Math.abs(this.currentTranslateY - value);
            if (distance < minDistance) {
                minDistance = distance;
                closestPosition = name;
            }
        });
        
        return closestPosition;
    }
    
    /**
     * Snap to a specific position
     * @param {string} position - 'full', 'half', or 'mini'
     * @param {boolean} animate - Whether to animate
     */
    snapToPosition(position, animate = true) {
        const translateY = this.snapPositions[position];
        
        if (animate) {
            // Spring animation
            this.element.style.transition = 'transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)';
        } else {
            this.element.style.transition = 'none';
        }
        
        this.element.style.transform = `translateY(${translateY}px)`;
        this.currentTranslateY = translateY;
        this.currentPosition = position;
        
        // Update collapsed class
        if (position === 'mini') {
            this.element.classList.add('collapsed');
        } else {
            this.element.classList.remove('collapsed');
        }
        
        // Haptic feedback
        if (animate) {
            this.hapticFeedback('medium');
        }
        
        console.log(`📊 Panel snapped to: ${position}`);
    }
    
    /**
     * Update indicators data
     * @param {Array} indicators 
     */
    updateIndicators(indicators) {
        this.indicators = indicators;
        const cardsContainer = document.getElementById('indicator-cards');
        if (cardsContainer) {
            cardsContainer.innerHTML = this.renderIndicators();
        }
    }
    
    /**
     * Haptic feedback
     */
    hapticFeedback(type = 'light') {
        if (typeof window.Telegram !== 'undefined' && window.Telegram.WebApp) {
            window.Telegram.WebApp.HapticFeedback.impactOccurred(type);
        } else if (navigator.vibrate) {
            const patterns = {
                light: 10,
                medium: 20,
                heavy: 30
            };
            navigator.vibrate(patterns[type] || 10);
        }
    }
    
    /**
     * Destroy instance
     */
    destroy() {
        if (this.element && this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IndicatorPanel;
}
