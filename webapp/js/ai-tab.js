/**
 * AI Analysis Tab Controller
 * Modern UI/UX with smooth animations and real-time feedback
 * Version: 2.0 - Complete Rebuild
 */

class AITabController {
    constructor() {
        this.state = {
            isAnalyzing: false,
            lastAnalysis: null,
            analysisCount: 0,
            symbol: null,
            timeframe: null
        };
        
        this.elements = {
            analyzeBtn: null,
            statusCard: null,
            loadingContainer: null,
            resultsContainer: null,
            historyPreview: null
        };
        
        this.tg = window.Telegram?.WebApp;
        
        console.log('🤖 AITabController initialized');
    }
    
    /**
     * Initialize AI tab functionality
     */
    init() {
        this.cacheElements();
        this.attachEventListeners();
        this.loadState();
        this.updateUI();
        
        console.log('✅ AI Tab ready');
    }
    
    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.elements.analyzeBtn = document.getElementById('ai-analyze-btn');
        this.elements.statusCard = document.getElementById('ai-status-card');
        this.elements.loadingContainer = document.getElementById('ai-loading-container');
        this.elements.resultsContainer = document.getElementById('ai-results');
        this.elements.historyPreview = document.getElementById('ai-history-preview');
        
        console.log('📦 AI Elements cached:', {
            button: !!this.elements.analyzeBtn,
            status: !!this.elements.statusCard,
            loading: !!this.elements.loadingContainer,
            results: !!this.elements.resultsContainer
        });
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        if (this.elements.analyzeBtn) {
            this.elements.analyzeBtn.addEventListener('click', () => this.handleAnalyzeClick());
        }
    }
    
    /**
     * Load saved state from localStorage
     */
    loadState() {
        try {
            const saved = localStorage.getItem('ai_tab_state');
            if (saved) {
                const data = JSON.parse(saved);
                this.state.lastAnalysis = data.lastAnalysis;
                this.state.analysisCount = data.analysisCount || 0;
            }
        } catch (error) {
            console.warn('⚠️ Could not load AI state:', error);
        }
    }
    
    /**
     * Save state to localStorage
     */
    saveState() {
        try {
            localStorage.setItem('ai_tab_state', JSON.stringify({
                lastAnalysis: this.state.lastAnalysis,
                analysisCount: this.state.analysisCount
            }));
        } catch (error) {
            console.warn('⚠️ Could not save AI state:', error);
        }
    }
    
    /**
     * Update current symbol and timeframe
     */
    setContext(symbol, timeframe) {
        this.state.symbol = symbol;
        this.state.timeframe = timeframe;
        this.updateUI();
    }
    
    /**
     * Handle analyze button click
     */
    async handleAnalyzeClick() {
        if (this.state.isAnalyzing) {
            console.log('⏳ Analysis already in progress');
            return;
        }
        
        // Get current context from global scope
        const symbol = this.state.symbol || window.currentSymbol || 'BTCUSDT';
        const timeframe = this.state.timeframe || window.currentTimeframe || '1h';
        
        console.log('🤖 Starting AI Analysis:', { symbol, timeframe });
        
        // Haptic feedback
        if (this.tg?.HapticFeedback) {
            this.tg.HapticFeedback.impactOccurred('medium');
        }
        
        this.state.isAnalyzing = true;
        this.showLoadingState();
        
        try {
            // Call AI analysis API
            const result = await window.triggerAIAnalysis(symbol, timeframe);
            
            console.log('✅ AI Analysis result:', result);
            
            // Update state
            this.state.lastAnalysis = {
                symbol,
                timeframe,
                timestamp: Date.now(),
                success: true,
                analysis: result.analysis || null
            };
            this.state.analysisCount++;
            this.saveState();
            
            // Show success with full analysis data
            this.showSuccessState(symbol, result);
            
            // Success haptic
            if (this.tg?.HapticFeedback) {
                this.tg.HapticFeedback.notificationOccurred('success');
            }
            
        } catch (error) {
            console.error('❌ AI Analysis failed:', error);
            
            // Show error
            this.showErrorState(error.message);
            
            // Error haptic
            if (this.tg?.HapticFeedback) {
                this.tg.HapticFeedback.notificationOccurred('error');
            }
        } finally {
            this.state.isAnalyzing = false;
            
            // Reset button after delay
            setTimeout(() => {
                this.updateUI();
            }, 3000);
        }
    }
    
    /**
     * Show loading state with animation
     */
    showLoadingState() {
        // Update button
        if (this.elements.analyzeBtn) {
            this.elements.analyzeBtn.disabled = true;
            this.elements.analyzeBtn.innerHTML = `
                <span class="ai-btn-content">
                    <span class="ai-spinner"></span>
                    <span>Analyzing...</span>
                </span>
            `;
            this.elements.analyzeBtn.classList.add('analyzing');
        }
        
        // Show loading animation
        if (this.elements.loadingContainer) {
            this.elements.loadingContainer.innerHTML = `
                <div class="ai-loading-card">
                    <div class="ai-loading-icon">
                        <div class="ai-pulse-ring"></div>
                        <div class="ai-brain-icon">🧠</div>
                    </div>
                    <div class="ai-loading-text">
                        <h3>Analyzing with Gemini AI</h3>
                        <div class="ai-loading-steps">
                            <div class="ai-step active">
                                <span class="ai-step-icon">📊</span>
                                <span>Collecting market data</span>
                            </div>
                            <div class="ai-step">
                                <span class="ai-step-icon">🔍</span>
                                <span>Analyzing indicators</span>
                            </div>
                            <div class="ai-step">
                                <span class="ai-step-icon">🧠</span>
                                <span>Processing with AI</span>
                            </div>
                            <div class="ai-step">
                                <span class="ai-step-icon">📱</span>
                                <span>Sending to Telegram</span>
                            </div>
                        </div>
                        <p class="ai-loading-note">This may take 10-20 seconds...</p>
                    </div>
                </div>
            `;
            this.elements.loadingContainer.style.display = 'block';
            
            // Animate steps
            this.animateLoadingSteps();
        }
        
        // Hide results
        if (this.elements.resultsContainer) {
            this.elements.resultsContainer.style.display = 'none';
        }
    }
    
    /**
     * Animate loading steps progressively
     */
    animateLoadingSteps() {
        const steps = this.elements.loadingContainer?.querySelectorAll('.ai-step');
        if (!steps || steps.length === 0) return;
        
        let currentStep = 0;
        const interval = setInterval(() => {
            if (currentStep < steps.length && this.state.isAnalyzing) {
                steps[currentStep].classList.add('active');
                currentStep++;
            } else {
                clearInterval(interval);
            }
        }, 2000);
    }
    
    /**
     * Show success state with analysis results
     */
    showSuccessState(symbol, analysis) {
        if (this.elements.loadingContainer) {
            // Check if we have full analysis data
            if (analysis && analysis.analysis) {
                const data = analysis.analysis;
                
                // Display full analysis
                this.elements.loadingContainer.innerHTML = `
                    <div class="ai-success-card">
                        <div class="ai-success-icon">
                            <div class="ai-checkmark">
                                <svg viewBox="0 0 52 52">
                                    <circle class="ai-checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
                                    <path class="ai-checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
                                </svg>
                            </div>
                        </div>
                        <div class="ai-success-content">
                            <h3>Analysis Complete!</h3>
                            
                            <!-- Recommendation -->
                            <div class="ai-recommendation">
                                <div class="ai-rec-badge ${data.recommendation?.toLowerCase() || 'neutral'}">
                                    ${data.recommendation === 'BUY' ? '🟢' : data.recommendation === 'SELL' ? '🔴' : '🟡'} 
                                    <strong>${data.recommendation || 'NEUTRAL'}</strong>
                                </div>
                                <div class="ai-confidence">
                                    Confidence: <strong>${data.confidence || 0}%</strong>
                                </div>
                            </div>
                            
                            <!-- Key Levels (only if valid numbers > 0) -->
                            ${(data.entry_point && data.entry_point > 0) || (data.stop_loss && data.stop_loss > 0) || (data.take_profit && data.take_profit.length > 0 && data.take_profit[0] > 0) ? `
                                <div class="ai-levels">
                                    <h4>📊 Key Levels</h4>
                                    ${data.entry_point && data.entry_point > 0 ? `<div class="ai-level">Entry: <strong>$${data.entry_point.toLocaleString()}</strong></div>` : ''}
                                    ${data.stop_loss && data.stop_loss > 0 ? `<div class="ai-level stop">Stop Loss: <strong>$${data.stop_loss.toLocaleString()}</strong></div>` : ''}
                                    ${data.take_profit && data.take_profit.length > 0 && data.take_profit[0] > 0 ? `
                                        <div class="ai-level profit">
                                            Take Profit: 
                                            ${data.take_profit.filter(tp => tp > 0).map((tp, i) => `<strong>TP${i+1}: $${tp.toLocaleString()}</strong>`).join(' • ')}
                                        </div>
                                    ` : ''}
                                </div>
                            ` : ''}
                            
                            <!-- Risk Level -->
                            ${data.risk_level && data.risk_level !== 'N/A' ? `
                                <div class="ai-risk">
                                    Risk Level: 
                                    <span class="ai-risk-badge ${data.risk_level.toLowerCase()}">
                                        ${data.risk_level}
                                    </span>
                                </div>
                            ` : ''}
                            
                            <!-- Summary Section (messages.summary) -->
                            ${data.messages && data.messages.summary ? `
                                <div class="ai-section">
                                    <div class="ai-section-header">
                                        <h4>📊 Tổng quan</h4>
                                    </div>
                                    <div class="ai-section-content">
                                        ${this.formatReasoning(data.messages.summary)}
                                    </div>
                                </div>
                            ` : ''}
                            
                            <!-- Technical Section (messages.technical) -->
                            ${data.messages && data.messages.technical ? `
                                <div class="ai-section">
                                    <div class="ai-section-header">
                                        <h4>🔧 Phân tích kỹ thuật</h4>
                                    </div>
                                    <div class="ai-section-content">
                                        ${this.formatReasoning(data.messages.technical)}
                                    </div>
                                </div>
                            ` : ''}
                            
                            <!-- Reasoning Section (messages.reasoning or reasoning field) -->
                            ${data.messages && data.messages.reasoning ? `
                                <div class="ai-section">
                                    <div class="ai-section-header">
                                        <h4>🧠 Lý do khuyến nghị</h4>
                                    </div>
                                    <div class="ai-section-content">
                                        ${this.formatReasoning(data.messages.reasoning)}
                                    </div>
                                </div>
                            ` : (data.reasoning ? `
                                <div class="ai-section">
                                    <div class="ai-section-header">
                                        <h4>🧠 Phân tích</h4>
                                    </div>
                                    <div class="ai-section-content">
                                        ${this.formatReasoning(data.reasoning)}
                                    </div>
                                </div>
                            ` : '')}
                            
                            <!-- Telegram Link -->
                            <div class="ai-success-action">
                                <span class="ai-telegram-icon">📱</span>
                                <span>Complete analysis also sent to Telegram</span>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                // Fallback to simple success message
                this.elements.loadingContainer.innerHTML = `
                    <div class="ai-success-card">
                        <div class="ai-success-icon">
                            <div class="ai-checkmark">
                                <svg viewBox="0 0 52 52">
                                    <circle class="ai-checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
                                    <path class="ai-checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
                                </svg>
                            </div>
                        </div>
                        <div class="ai-success-content">
                            <h3>Analysis Complete!</h3>
                            <p>AI analysis for <strong>${symbol}</strong> has been sent to your Telegram chat.</p>
                            <div class="ai-success-action">
                                <span class="ai-telegram-icon">📱</span>
                                <span>Check your Telegram for detailed results</span>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            this.elements.loadingContainer.style.display = 'block';
        }
        
        // Update status card
        this.updateStatusCard();
    }
    
    /**
     * Format reasoning text with line breaks
     */
    formatReasoning(text) {
        if (!text) return '';
        
        // Convert newlines to <br> - NO LENGTH LIMIT
        return text
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>');
    }
    
    /**
     * Show error state
     */
    showErrorState(message) {
        if (this.elements.loadingContainer) {
            this.elements.loadingContainer.innerHTML = `
                <div class="ai-error-card">
                    <div class="ai-error-icon">❌</div>
                    <div class="ai-error-content">
                        <h3>Analysis Failed</h3>
                        <p>${message || 'An error occurred. Please try again.'}</p>
                        <button class="ai-retry-btn" onclick="window.aiTab?.handleAnalyzeClick()">
                            🔄 Try Again
                        </button>
                    </div>
                </div>
            `;
            this.elements.loadingContainer.style.display = 'block';
        }
    }
    
    /**
     * Update UI based on current state
     */
    updateUI() {
        this.updateButton();
        this.updateStatusCard();
        this.updateHistoryPreview();
    }
    
    /**
     * Update analyze button
     */
    updateButton() {
        if (!this.elements.analyzeBtn) return;
        
        const symbol = this.state.symbol || window.currentSymbol || 'BTCUSDT';
        const timeframe = this.state.timeframe || window.currentTimeframe || '1h';
        
        this.elements.analyzeBtn.disabled = this.state.isAnalyzing;
        this.elements.analyzeBtn.classList.toggle('analyzing', this.state.isAnalyzing);
        
        if (!this.state.isAnalyzing) {
            this.elements.analyzeBtn.innerHTML = `
                <span class="ai-btn-content">
                    <span class="ai-btn-icon">🧠</span>
                    <span class="ai-btn-text">
                        <span class="ai-btn-title">Analyze with Gemini AI</span>
                        <span class="ai-btn-subtitle">${symbol} • ${timeframe}</span>
                    </span>
                </span>
            `;
        }
    }
    
    /**
     * Update status card
     */
    updateStatusCard() {
        if (!this.elements.statusCard) return;
        
        const hasHistory = this.state.analysisCount > 0;
        
        if (hasHistory) {
            const lastDate = this.state.lastAnalysis ? 
                new Date(this.state.lastAnalysis.timestamp).toLocaleString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                }) : 'Never';
            
            this.elements.statusCard.innerHTML = `
                <div class="ai-status-grid">
                    <div class="ai-status-item">
                        <span class="ai-status-label">Total Analyses</span>
                        <span class="ai-status-value">${this.state.analysisCount}</span>
                    </div>
                    <div class="ai-status-item">
                        <span class="ai-status-label">Last Analysis</span>
                        <span class="ai-status-value">${lastDate}</span>
                    </div>
                </div>
            `;
        } else {
            this.elements.statusCard.innerHTML = `
                <div class="ai-status-empty">
                    <span class="ai-status-empty-icon">📊</span>
                    <p>No analysis yet. Click the button above to get started!</p>
                </div>
            `;
        }
    }
    
    /**
     * Update history preview
     */
    updateHistoryPreview() {
        if (!this.elements.historyPreview) return;
        
        if (this.state.lastAnalysis) {
            this.elements.historyPreview.innerHTML = `
                <div class="ai-history-item">
                    <div class="ai-history-icon">✅</div>
                    <div class="ai-history-content">
                        <div class="ai-history-symbol">${this.state.lastAnalysis.symbol}</div>
                        <div class="ai-history-meta">
                            ${this.state.lastAnalysis.timeframe} • 
                            ${new Date(this.state.lastAnalysis.timestamp).toLocaleTimeString('en-US', {
                                hour: '2-digit',
                                minute: '2-digit'
                            })}
                        </div>
                    </div>
                </div>
            `;
        }
    }
}

// Initialize on load
if (typeof window !== 'undefined') {
    window.aiTab = new AITabController();
    console.log('✅ AI Tab module loaded');
}
