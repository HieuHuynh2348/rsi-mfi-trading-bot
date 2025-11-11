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

/**
 * Indicators Tab Controller
 * Modern multi-timeframe technical indicators display
 * Version: 2.0 - Complete Rebuild with Multi-Timeframe Support
 */

class IndicatorsTabController {
    constructor() {
        this.container = document.querySelector('[data-tab-content="indicators"]');
        this.currentSymbol = 'BTCUSDT';
        this.timeframes = ['1m', '5m', '15m', '1h', '4h', '1d'];
        this.selectedTimeframe = '1h';
        this.indicators = {};
        this.isLoading = false;
        
        console.log('📊 IndicatorsTabController initialized');
    }

    /**
     * Initialize the tab
     */
    init() {
        console.log('📊 Initializing Indicators Tab...');
        if (!this.container) {
            console.warn('⚠️ Indicators container not found');
            return;
        }
        // Don't call render() here, let setContext() handle it
    }

    /**
     * Set context (symbol and timeframe)
     */
    setContext(symbol, timeframe) {
        console.log(`📊 Indicators context: ${symbol} ${timeframe}`);
        this.currentSymbol = symbol;
        this.selectedTimeframe = timeframe;
        this.loadIndicators();
    }

    /**
     * Load indicators for all timeframes
     */
    async loadIndicators() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading();

        try {
            // Load indicators for all timeframes in parallel
            const promises = this.timeframes.map(tf => 
                this.fetchIndicatorsForTimeframe(tf)
            );
            
            const results = await Promise.all(promises);
            
            // Store results
            results.forEach((data, index) => {
                this.indicators[this.timeframes[index]] = data;
            });
            
            this.renderIndicators();
            console.log('✅ Indicators loaded for all timeframes');
        } catch (error) {
            console.error('❌ Error loading indicators:', error);
            this.showError(error.message);
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Fetch indicators for a specific timeframe
     */
    async fetchIndicatorsForTimeframe(timeframe) {
        const response = await fetch(`/api/candles?symbol=${this.currentSymbol}&interval=${timeframe}&limit=100`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch data for ${timeframe}`);
        }
        
        const data = await response.json();
        return this.calculateIndicators(data.candles || []);
    }

    /**
     * Calculate technical indicators from candle data
     */
    calculateIndicators(candles) {
        if (!candles || candles.length === 0) {
            return {
                rsi: null,
                mfi: null,
                stochRSI: null,
                volumeRatio: null,
                ema20: null,
                price: 0
            };
        }

        return {
            rsi: this.calculateRSI(candles, 6),
            mfi: this.calculateMFI(candles, 6),
            stochRSI: this.calculateStochRSI(candles, 14),
            volumeRatio: this.calculateVolumeRatio(candles),
            ema20: this.calculateEMA(candles, 20),
            price: candles[candles.length - 1]?.close || 0
        };
    }

    /**
     * Calculate RSI
     */
    calculateRSI(candles, period = 14) {
        if (candles.length < period + 1) return null;

        let gains = 0;
        let losses = 0;

        for (let i = candles.length - period; i < candles.length; i++) {
            const change = candles[i].close - candles[i - 1].close;
            if (change > 0) gains += change;
            else losses += Math.abs(change);
        }

        const avgGain = gains / period;
        const avgLoss = losses / period;

        if (avgLoss === 0) return 100;
        const rs = avgGain / avgLoss;
        return 100 - (100 / (1 + rs));
    }

    /**
     * Calculate MFI (Money Flow Index)
     */
    calculateMFI(candles, period = 14) {
        if (candles.length < period + 1) return null;

        let positiveFlow = 0;
        let negativeFlow = 0;

        for (let i = candles.length - period; i < candles.length; i++) {
            const typicalPrice = (candles[i].high + candles[i].low + candles[i].close) / 3;
            const prevTypicalPrice = (candles[i - 1].high + candles[i - 1].low + candles[i - 1].close) / 3;
            const moneyFlow = typicalPrice * candles[i].volume;

            if (typicalPrice > prevTypicalPrice) {
                positiveFlow += moneyFlow;
            } else {
                negativeFlow += moneyFlow;
            }
        }

        if (negativeFlow === 0) return 100;
        const moneyFlowRatio = positiveFlow / negativeFlow;
        return 100 - (100 / (1 + moneyFlowRatio));
    }

    /**
     * Calculate Stochastic RSI
     */
    calculateStochRSI(candles, period = 14) {
        if (candles.length < period + 1) return null;

        const rsiValues = [];
        for (let i = period; i < candles.length; i++) {
            const slice = candles.slice(i - period, i + 1);
            const rsi = this.calculateRSI(slice, period);
            if (rsi !== null) rsiValues.push(rsi);
        }

        if (rsiValues.length === 0) return null;

        const currentRSI = rsiValues[rsiValues.length - 1];
        const minRSI = Math.min(...rsiValues);
        const maxRSI = Math.max(...rsiValues);

        if (maxRSI === minRSI) return 50;
        return ((currentRSI - minRSI) / (maxRSI - minRSI)) * 100;
    }

    /**
     * Calculate Volume Ratio
     */
    calculateVolumeRatio(candles) {
        if (candles.length < 20) return null;

        const recentVolume = candles[candles.length - 1].volume;
        const avgVolume = candles.slice(-20).reduce((sum, c) => sum + c.volume, 0) / 20;

        return avgVolume > 0 ? recentVolume / avgVolume : 0;
    }

    /**
     * Calculate EMA
     */
    calculateEMA(candles, period = 20) {
        if (candles.length < period) return null;

        const multiplier = 2 / (period + 1);
        let ema = candles.slice(0, period).reduce((sum, c) => sum + c.close, 0) / period;

        for (let i = period; i < candles.length; i++) {
            ema = (candles[i].close - ema) * multiplier + ema;
        }

        return ema;
    }

    /**
     * Get signal for indicator value
     */
    getSignal(indicator, value) {
        if (value === null) return 'neutral';

        switch (indicator) {
            case 'rsi':
                return value > 70 ? 'bearish' : value < 30 ? 'bullish' : 'neutral';
            case 'mfi':
                return value > 80 ? 'bearish' : value < 20 ? 'bullish' : 'neutral';
            case 'stochRSI':
                return value > 80 ? 'bearish' : value < 20 ? 'bullish' : 'neutral';
            case 'volumeRatio':
                return value > 2 ? 'bullish' : value < 0.5 ? 'bearish' : 'neutral';
            default:
                return 'neutral';
        }
    }

    /**
     * Show loading state
     */
    showLoading() {
        if (!this.container) return;
        
        const content = this.container.querySelector('#indicators-tab-content');
        if (content) {
            content.innerHTML = `
                <div class="indicators-loading">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">Đang tải indicators...</div>
                </div>
            `;
        }
    }

    /**
     * Show error state
     */
    showError(message) {
        if (!this.container) return;
        
        const content = this.container.querySelector('#indicators-tab-content');
        if (content) {
            content.innerHTML = `
                <div class="indicators-error">
                    <div class="error-icon">⚠️</div>
                    <div class="error-title">Lỗi Tải Dữ Liệu</div>
                    <div class="error-message">${message}</div>
                    <button class="error-retry-btn" onclick="window.indicatorsTab?.loadIndicators()">
                        <span>🔄</span> Thử Lại
                    </button>
                </div>
            `;
        }
    }

    /**
     * Render indicators for all timeframes
     */
    renderIndicators() {
        if (!this.container) {
            console.error('❌ Indicators container not found in renderIndicators()');
            return;
        }
        
        const content = this.container.querySelector('#indicators-tab-content');
        if (!content) {
            console.error('❌ #indicators-tab-content not found');
            return;
        }

        console.log('✅ Rendering indicators for', Object.keys(this.indicators).length, 'timeframes');

        const wrapper = document.createElement('div');
        wrapper.className = 'indicators-wrapper';

        // Create multi-timeframe view for RSI, MFI, Stoch RSI
        wrapper.innerHTML = `
            <div class="multi-timeframe-overview">
                <div class="overview-header">
                    <h3>📊 Multi-Timeframe Analysis</h3>
                    <div class="overview-symbol">${this.currentSymbol}</div>
                </div>
                
                <!-- RSI Multi-Timeframe -->
                <div class="indicator-multi-card">
                    <div class="indicator-multi-header">
                        <span class="indicator-icon">📈</span>
                        <span class="indicator-title">RSI (6)</span>
                        <span class="indicator-description">Relative Strength Index</span>
                    </div>
                    <div class="timeframe-values-grid">
                        ${this.timeframes.map(tf => {
                            const data = this.indicators[tf];
                            const value = data?.rsi;
                            const signal = this.getSignal('rsi', value);
                            return `
                                <div class="timeframe-value-item ${signal}">
                                    <div class="timeframe-label">${tf.toUpperCase()}</div>
                                    <div class="value ${signal}">${value !== null ? value.toFixed(1) : 'N/A'}</div>
                                    <div class="signal-indicator ${signal}">
                                        ${signal === 'bullish' ? '🟢 Oversold' : signal === 'bearish' ? '🔴 Overbought' : '⚪ Neutral'}
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>

                <!-- MFI Multi-Timeframe -->
                <div class="indicator-multi-card">
                    <div class="indicator-multi-header">
                        <span class="indicator-icon">💰</span>
                        <span class="indicator-title">MFI (6)</span>
                        <span class="indicator-description">Money Flow Index</span>
                    </div>
                    <div class="timeframe-values-grid">
                        ${this.timeframes.map(tf => {
                            const data = this.indicators[tf];
                            const value = data?.mfi;
                            const signal = this.getSignal('mfi', value);
                            return `
                                <div class="timeframe-value-item ${signal}">
                                    <div class="timeframe-label">${tf.toUpperCase()}</div>
                                    <div class="value ${signal}">${value !== null ? value.toFixed(1) : 'N/A'}</div>
                                    <div class="signal-indicator ${signal}">
                                        ${signal === 'bullish' ? '🟢 Oversold' : signal === 'bearish' ? '🔴 Overbought' : '⚪ Neutral'}
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>

                <!-- Stoch RSI Multi-Timeframe -->
                <div class="indicator-multi-card">
                    <div class="indicator-multi-header">
                        <span class="indicator-icon">📊</span>
                        <span class="indicator-title">Stochastic RSI</span>
                        <span class="indicator-description">Stoch RSI (14)</span>
                    </div>
                    <div class="timeframe-values-grid">
                        ${this.timeframes.map(tf => {
                            const data = this.indicators[tf];
                            const value = data?.stochRSI;
                            const signal = this.getSignal('stochRSI', value);
                            return `
                                <div class="timeframe-value-item ${signal}">
                                    <div class="timeframe-label">${tf.toUpperCase()}</div>
                                    <div class="value ${signal}">${value !== null ? value.toFixed(1) : 'N/A'}</div>
                                    <div class="signal-indicator ${signal}">
                                        ${signal === 'bullish' ? '🟢 Oversold' : signal === 'bearish' ? '🔴 Overbought' : '⚪ Neutral'}
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>

                <!-- Additional Indicators (Volume & EMA) -->
                <div class="additional-indicators-grid">
                    ${this.timeframes.map(tf => {
                        const data = this.indicators[tf];
                        const volumeSignal = this.getSignal('volumeRatio', data?.volumeRatio);
                        return `
                            <div class="additional-indicator-card">
                                <div class="card-header">${tf.toUpperCase()}</div>
                                <div class="additional-items">
                                    <div class="additional-item">
                                        <span class="item-label">Volume Ratio</span>
                                        <span class="item-value ${volumeSignal}">
                                            ${data?.volumeRatio !== null ? data.volumeRatio.toFixed(2) + 'x' : 'N/A'}
                                        </span>
                                    </div>
                                    <div class="additional-item">
                                        <span class="item-label">EMA (20)</span>
                                        <span class="item-value neutral">
                                            ${data?.ema20 !== null ? '$' + data.ema20.toFixed(2) : 'N/A'}
                                        </span>
                                    </div>
                                    <div class="additional-item">
                                        <span class="item-label">Price</span>
                                        <span class="item-value neutral">
                                            ${data?.price ? '$' + data.price.toFixed(2) : 'N/A'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;

        content.innerHTML = '';
        content.appendChild(wrapper);
    }
}
