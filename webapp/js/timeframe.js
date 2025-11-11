/**
 * Timeframe Switcher - Segmented Control Component
 * Binance-inspired design with sliding active indicator
 */

class TimeframeSwitcher {
    constructor(options = {}) {
        this.container = options.container || document.body;
        this.timeframes = options.timeframes || ['5m', '15m', '1h', '4h', '1d'];
        this.defaultTimeframe = options.defaultTimeframe || '1h';
        this.currentTimeframe = this.defaultTimeframe;
        this.onChange = options.onChange || (() => {});
        
        this.init();
    }
    
    init() {
        this.createSwitcher();
        this.setupEventListeners();
        this.updateIndicator(this.currentTimeframe, false); // No animation on init
        console.log('✅ Timeframe switcher initialized');
    }
    
    /**
     * Create timeframe switcher HTML
     */
    createSwitcher() {
        const switcher = document.createElement('div');
        switcher.className = 'timeframe-switcher';
        switcher.id = 'timeframe-switcher';
        
        // Create buttons
        const buttonsHTML = this.timeframes.map((tf, index) => `
            <button 
                class="timeframe-btn ${tf === this.currentTimeframe ? 'active' : ''}" 
                data-timeframe="${tf}"
                data-index="${index}"
            >
                ${tf}
            </button>
        `).join('');
        
        // Create sliding indicator
        switcher.innerHTML = `
            ${buttonsHTML}
            <div class="timeframe-indicator"></div>
        `;
        
        this.container.appendChild(switcher);
        this.element = switcher;
        this.indicator = switcher.querySelector('.timeframe-indicator');
        this.buttons = switcher.querySelectorAll('.timeframe-btn');
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        this.buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                const timeframe = e.currentTarget.dataset.timeframe;
                this.selectTimeframe(timeframe);
            });
        });
        
        // Keyboard navigation (optional)
        this.element.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                this.selectPrevious();
            } else if (e.key === 'ArrowRight') {
                this.selectNext();
            }
        });
    }
    
    /**
     * Select a timeframe
     * @param {string} timeframe 
     */
    selectTimeframe(timeframe) {
        if (timeframe === this.currentTimeframe) return;
        
        // Update button states
        this.buttons.forEach(btn => {
            if (btn.dataset.timeframe === timeframe) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Animate indicator to new position
        this.updateIndicator(timeframe, true);
        
        // Haptic feedback
        this.hapticFeedback('light');
        
        // Update current timeframe
        this.currentTimeframe = timeframe;
        
        // Trigger callback
        this.onChange(timeframe);
        
        console.log(`⏱️ Timeframe changed to: ${timeframe}`);
    }
    
    /**
     * Update sliding indicator position
     * @param {string} timeframe 
     * @param {boolean} animate - Whether to animate the transition
     */
    updateIndicator(timeframe, animate = true) {
        const button = Array.from(this.buttons).find(
            btn => btn.dataset.timeframe === timeframe
        );
        
        if (!button) return;
        
        // Calculate position and width
        const buttonRect = button.getBoundingClientRect();
        const switcherRect = this.element.getBoundingClientRect();
        
        const left = buttonRect.left - switcherRect.left;
        const width = buttonRect.width;
        
        // Apply transform (better performance than left/width)
        if (animate) {
            this.indicator.style.transition = 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
        } else {
            this.indicator.style.transition = 'none';
        }
        
        this.indicator.style.transform = `translateX(${left}px)`;
        this.indicator.style.width = `${width}px`;
        
        // Re-enable transition after initial position
        if (!animate) {
            setTimeout(() => {
                this.indicator.style.transition = 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
            }, 50);
        }
    }
    
    /**
     * Select previous timeframe
     */
    selectPrevious() {
        const currentIndex = this.timeframes.indexOf(this.currentTimeframe);
        if (currentIndex > 0) {
            this.selectTimeframe(this.timeframes[currentIndex - 1]);
        }
    }
    
    /**
     * Select next timeframe
     */
    selectNext() {
        const currentIndex = this.timeframes.indexOf(this.currentTimeframe);
        if (currentIndex < this.timeframes.length - 1) {
            this.selectTimeframe(this.timeframes[currentIndex + 1]);
        }
    }
    
    /**
     * Get current timeframe
     * @returns {string}
     */
    getCurrentTimeframe() {
        return this.currentTimeframe;
    }
    
    /**
     * Programmatically set timeframe (without triggering callback)
     * @param {string} timeframe 
     */
    setTimeframe(timeframe, triggerCallback = false) {
        if (!this.timeframes.includes(timeframe)) {
            console.warn(`Invalid timeframe: ${timeframe}`);
            return;
        }
        
        // Update UI
        this.buttons.forEach(btn => {
            if (btn.dataset.timeframe === timeframe) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        this.updateIndicator(timeframe, true);
        this.currentTimeframe = timeframe;
        
        // Optionally trigger callback
        if (triggerCallback) {
            this.onChange(timeframe);
        }
    }
    
    /**
     * Haptic feedback
     * @param {string} type 
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
     * Handle window resize (update indicator position)
     */
    handleResize() {
        this.updateIndicator(this.currentTimeframe, false);
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

// Auto-resize on window resize
window.addEventListener('resize', () => {
    if (window.timeframeSwitcher) {
        window.timeframeSwitcher.handleResize();
    }
});

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TimeframeSwitcher;
}
