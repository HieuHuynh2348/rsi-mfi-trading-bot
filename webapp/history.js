/**
 * Analysis History Tab Controller
 * Modern UI/UX with glassmorphism design
 * Version: 2.0 - Complete Rebuild
 */

class AnalysisHistory {
    constructor(userId) {
        this.userId = userId;
        this.history = [];
        this.filteredHistory = [];
        this.stats = null;
        this.isLoading = false;
        this.currentFilters = {};
        
        console.log('📜 AnalysisHistory initialized with userId:', userId);
    }
    
    /**
     * Initialize history tab
     */
    init() {
        console.log('📜 Initializing History Tab...');
        this.showLoading();
        this.loadHistory();
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        const container = document.getElementById('history-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="history-loading">
                <div class="loading-spinner"></div>
                <div class="loading-text">Đang tải lịch sử phân tích...</div>
            </div>
        `;
    }

    /**
     * Load history from API
     */
    async loadHistory(symbol = null, days = 7) {
        if (this.isLoading) {
            console.log('⏳ Already loading...');
            return;
        }
        
        this.isLoading = true;
        
        try {
            const params = new URLSearchParams({
                user_id: this.userId,
                days: days
            });
            
            if (symbol) {
                params.append('symbol', symbol);
            }
            
            console.log('📡 Fetching history:', `/api/analysis-history?${params}`);
            const response = await fetch(`/api/analysis-history?${params}`);
            const data = await response.json();
            
            console.log('📊 History data received:', data);
            
            if (data.success) {
                this.history = data.history || [];
                this.stats = data.stats || this.calculateStats();
                this.filteredHistory = [...this.history];
                this.render();
                this.isLoading = false;
                return true;
            } else {
                console.error('❌ Failed to load history:', data.error);
                this.showError(data.error || 'Không thể tải lịch sử');
                this.isLoading = false;
                return false;
            }
        } catch (error) {
            console.error('❌ Error loading history:', error);
            this.showError(error.message || 'Lỗi kết nối đến server');
            this.isLoading = false;
            return false;
        }
    }
    
    /**
     * Calculate stats if not provided by API
     */
    calculateStats() {
        const wins = this.history.filter(h => h.tracking_result?.result === 'WIN').length;
        const losses = this.history.filter(h => h.tracking_result?.result === 'LOSS').length;
        const total = wins + losses;
        const winRate = total > 0 ? (wins / total) * 100 : 0;
        
        const profits = this.history
            .filter(h => h.tracking_result?.result === 'WIN')
            .map(h => h.tracking_result?.pnl_percent || 0);
        const totalProfit = profits.length > 0 
            ? profits.reduce((a, b) => a + b, 0)
            : 0;
            
        const losses_ = this.history
            .filter(h => h.tracking_result?.result === 'LOSS')
            .map(h => h.tracking_result?.pnl_percent || 0);
        const totalLoss = losses_.length > 0
            ? losses_.reduce((a, b) => a + b, 0)
            : 0;
        
        return {
            total: this.history.length,
            wins,
            losses,
            win_rate: winRate,
            total_profit: totalProfit,
            total_loss: totalLoss
        };
    }

    /**
     * Filter history by criteria
     */
    filterHistory(filters = {}) {
        console.log('🔍 Filtering history with:', filters);
        this.currentFilters = filters;
        
        this.filteredHistory = this.history.filter(item => {
            // Filter by symbol
            if (filters.symbol && item.symbol !== filters.symbol) {
                return false;
            }
            
            // Filter by recommendation
            if (filters.recommendation && 
                item.ai_full_response?.recommendation !== filters.recommendation) {
                return false;
            }
            
            // Filter by result (WIN/LOSS)
            if (filters.result && 
                item.tracking_result?.result !== filters.result) {
                return false;
            }
            
            // Filter by status
            if (filters.status && item.status !== filters.status) {
                return false;
            }
            
            return true;
        });
        
        console.log(`✅ Filtered: ${this.filteredHistory.length}/${this.history.length} items`);
        this.render();
    }

    /**
     * Render history UI
     */
    render() {
        const container = document.getElementById('history-container');
        if (!container) {
            console.warn('⚠️ history-container not found');
            return;
        }
        
        console.log('🎨 Rendering history UI...');
        
        // Clear container
        container.innerHTML = '';
        
        // Create modern wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'history-wrapper';
        
        // Render stats if available
        if (this.stats && this.history.length > 0) {
            wrapper.appendChild(this.renderStats());
        }
        
        // Render filters if history exists
        if (this.history.length > 0) {
            wrapper.appendChild(this.renderFilters());
        }
        
        // Render history list or empty state
        if (this.filteredHistory.length === 0 && this.history.length === 0) {
            wrapper.appendChild(this.renderEmpty());
        } else if (this.filteredHistory.length === 0) {
            wrapper.appendChild(this.renderNoResults());
        } else {
            wrapper.appendChild(this.renderList());
        }
        
        container.appendChild(wrapper);
        console.log('✅ History UI rendered');
    }

    /**
     * Render statistics card
     */
    renderStats() {
        const stats = this.stats;
        const div = document.createElement('div');
        div.className = 'history-stats-card';
        
        const winRate = stats.win_rate || 0;
        const winRateColor = winRate >= 60 ? '#4CAF50' : winRate >= 40 ? '#FFC107' : '#F44336';
        
        div.innerHTML = `
            <div class="stats-header">
                <h3>📊 Thống Kê Tổng Quan</h3>
                <div class="stats-period">Last 7 days</div>
            </div>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-icon">📝</div>
                    <div class="stat-content">
                        <div class="stat-value">${stats.total || 0}</div>
                        <div class="stat-label">Tổng Phân Tích</div>
                    </div>
                </div>
                <div class="stat-item success">
                    <div class="stat-icon">✅</div>
                    <div class="stat-content">
                        <div class="stat-value">${stats.wins || 0}</div>
                        <div class="stat-label">Thắng</div>
                    </div>
                </div>
                <div class="stat-item danger">
                    <div class="stat-icon">❌</div>
                    <div class="stat-content">
                        <div class="stat-value">${stats.losses || 0}</div>
                        <div class="stat-label">Thua</div>
                    </div>
                </div>
                <div class="stat-item primary" style="--win-rate-color: ${winRateColor}">
                    <div class="stat-icon">🎯</div>
                    <div class="stat-content">
                        <div class="stat-value">${winRate.toFixed(1)}%</div>
                        <div class="stat-label">Tỷ Lệ Thắng</div>
                        <div class="stat-progress">
                            <div class="stat-progress-bar" style="width: ${winRate}%; background: ${winRateColor}"></div>
                        </div>
                    </div>
                </div>
                <div class="stat-item success">
                    <div class="stat-icon">📈</div>
                    <div class="stat-content">
                        <div class="stat-value">+${(stats.total_profit || 0).toFixed(2)}%</div>
                        <div class="stat-label">Tổng Lãi</div>
                    </div>
                </div>
                <div class="stat-item danger">
                    <div class="stat-icon">📉</div>
                    <div class="stat-content">
                        <div class="stat-value">${(stats.total_loss || 0).toFixed(2)}%</div>
                        <div class="stat-label">Tổng Lỗ</div>
                    </div>
                </div>
            </div>
        `;
        return div;
    }

    /**
     * Render filter controls
     */
    renderFilters() {
        const div = document.createElement('div');
        div.className = 'history-filters-card';
        
        // Get unique symbols
        const symbols = [...new Set(this.history.map(item => item.symbol))].sort();
        
        div.innerHTML = `
            <div class="filters-header">
                <h4>🔍 Bộ Lọc</h4>
                <button class="filter-reset-btn" onclick="window.historyTab?.resetFilters()">
                    <span class="btn-icon">🔄</span> Reset
                </button>
            </div>
            <div class="filters-grid">
                <div class="filter-group">
                    <label class="filter-label">Symbol</label>
                    <select class="history-filter-select" data-filter="symbol">
                        <option value="">Tất cả</option>
                        ${symbols.map(s => `<option value="${s}">${s}</option>`).join('')}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label class="filter-label">Khuyến Nghị</label>
                    <select class="history-filter-select" data-filter="recommendation">
                        <option value="">Tất cả</option>
                        <option value="BUY">🟢 BUY</option>
                        <option value="SELL">🔴 SELL</option>
                        <option value="WAIT">⚪ WAIT</option>
                        <option value="HOLD">🟡 HOLD</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label class="filter-label">Kết Quả</label>
                    <select class="history-filter-select" data-filter="result">
                        <option value="">Tất cả</option>
                        <option value="WIN">✅ WIN</option>
                        <option value="LOSS">❌ LOSS</option>
                        <option value="EXPIRED">⏱️ EXPIRED</option>
                    </select>
                </div>
            </div>
        `;
        
        // Add event listeners after render
        setTimeout(() => {
            div.querySelectorAll('.history-filter-select').forEach(select => {
                select.addEventListener('change', () => {
                    const filters = {};
                    div.querySelectorAll('.history-filter-select').forEach(s => {
                        if (s.value) {
                            filters[s.dataset.filter] = s.value;
                        }
                    });
                    this.filterHistory(filters);
                });
            });
        }, 100);
        
        return div;
    }

    /**
     * Render empty state
     */
    renderEmpty() {
        const div = document.createElement('div');
        div.className = 'history-empty-state';
        div.innerHTML = `
            <div class="empty-illustration">
                <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
                    <circle cx="60" cy="60" r="50" stroke="rgba(102, 126, 234, 0.3)" stroke-width="2" stroke-dasharray="5 5"/>
                    <path d="M40 60 L50 70 L80 40" stroke="rgba(102, 126, 234, 0.5)" stroke-width="3" stroke-linecap="round" fill="none"/>
                </svg>
            </div>
            <h3 class="empty-title">Chưa Có Lịch Sử Phân Tích</h3>
            <p class="empty-text">
                Thực hiện phân tích AI đầu tiên để bắt đầu theo dõi lịch sử và thống kê.
            </p>
            <div class="empty-hint">
                💡 <strong>Mẹo:</strong> Chuyển sang tab AI để phân tích coin
            </div>
        `;
        return div;
    }
    
    /**
     * Render no results state (after filtering)
     */
    renderNoResults() {
        const div = document.createElement('div');
        div.className = 'history-empty-state';
        div.innerHTML = `
            <div class="empty-icon">🔍</div>
            <h3 class="empty-title">Không Tìm Thấy Kết Quả</h3>
            <p class="empty-text">
                Không có phân tích nào khớp với bộ lọc hiện tại.
            </p>
            <button class="empty-action-btn" onclick="window.historyTab?.resetFilters()">
                🔄 Xóa Bộ Lọc
            </button>
        `;
        return div;
    }
    
    /**
     * Reset all filters
     */
    resetFilters() {
        this.currentFilters = {};
        this.filteredHistory = [...this.history];
        
        // Reset filter UI
        const selects = document.querySelectorAll('.history-filter-select');
        selects.forEach(select => select.value = '');
        
        this.render();
    }

    /**
     * Render history list
     */
    renderList() {
        const div = document.createElement('div');
        div.className = 'history-list';
        
        this.filteredHistory.forEach(item => {
            div.appendChild(this.renderItem(item));
        });
        
        return div;
    }

    /**
     * Render single history item
     */
    renderItem(item) {
        const response = item.ai_full_response || {};
        const tracking = item.tracking_result || {};
        const snapshot = item.market_snapshot || {};
        
        const recommendation = response.recommendation || 'N/A';
        const confidence = response.confidence || 0;
        const entry = response.entry_point || 0;
        const sl = response.stop_loss || 0;
        const tps = response.take_profit || [];
        
        const result = tracking.result || 'PENDING';
        const pnl = tracking.pnl_percent || 0;
        const exitPrice = tracking.exit_price || 0;
        const exitReason = tracking.exit_reason || '';
        const manualReview = tracking.manual_review || null;
        
        const createdAt = new Date(item.created_at);
        const timeStr = createdAt.toLocaleString('vi-VN');
        
        // Recommendation emoji
        let recEmoji = '⚪';
        if (recommendation === 'BUY') recEmoji = '🟢';
        else if (recommendation === 'SELL') recEmoji = '🔴';
        else if (recommendation === 'HOLD') recEmoji = '🟡';
        
        // Result badge
        let resultBadge = '';
        if (result === 'WIN') {
            resultBadge = `<span class="badge badge-success">✅ WIN (+${pnl.toFixed(2)}%)</span>`;
        } else if (result === 'LOSS') {
            resultBadge = `<span class="badge badge-danger">❌ LOSS (${pnl.toFixed(2)}%)</span>`;
        } else if (result === 'EXPIRED') {
            resultBadge = `<span class="badge badge-warning">⏱️ EXPIRED</span>`;
        } else if (item.status === 'PENDING_TRACKING') {
            resultBadge = `<span class="badge badge-info">🔄 Tracking...</span>`;
        } else {
            resultBadge = `<span class="badge badge-secondary">⏳ Pending</span>`;
        }
        
        // Review buttons (only show if not reviewed yet)
        let reviewButtons = '';
        if (!manualReview) {
            reviewButtons = `
                <div class="review-buttons">
                    <button class="btn-review btn-good" data-id="${item.analysis_id}" data-review="good">
                        👍 Good
                    </button>
                    <button class="btn-review btn-bad" data-id="${item.analysis_id}" data-review="bad">
                        👎 Bad
                    </button>
                </div>
            `;
        } else {
            const reviewEmoji = manualReview === 'good' ? '👍' : '👎';
            reviewButtons = `<div class="review-status">${reviewEmoji} Reviewed</div>`;
        }
        
        const div = document.createElement('div');
        div.className = 'history-item';
        div.innerHTML = `
            <div class="item-header">
                <div class="item-symbol">${recEmoji} ${item.symbol}</div>
                <div class="item-time">${timeStr}</div>
            </div>
            
            <div class="item-body">
                <div class="item-row">
                    <span class="label">Khuyến Nghị:</span>
                    <span class="value">${recommendation} (${confidence}%)</span>
                </div>
                <div class="item-row">
                    <span class="label">Entry:</span>
                    <span class="value">$${entry.toFixed(2)}</span>
                </div>
                <div class="item-row">
                    <span class="label">Stop Loss:</span>
                    <span class="value">$${sl.toFixed(2)}</span>
                </div>
                <div class="item-row">
                    <span class="label">Take Profit:</span>
                    <span class="value">
                        ${tps.map((tp, i) => `TP${i+1}: $${tp.toFixed(2)}`).join(' | ')}
                    </span>
                </div>
                ${exitPrice > 0 ? `
                <div class="item-row">
                    <span class="label">Exit:</span>
                    <span class="value">$${exitPrice.toFixed(2)} (${exitReason})</span>
                </div>
                ` : ''}
            </div>
            
            <div class="item-footer">
                ${resultBadge}
                ${reviewButtons}
                <button class="btn-details" data-id="${item.analysis_id}">
                    📄 Chi Tiết
                </button>
            </div>
        `;
        
        // Add click handler for details button
        setTimeout(() => {
            div.querySelector('.btn-details')?.addEventListener('click', () => {
                this.showDetails(item);
            });
            
            // Add click handlers for review buttons
            div.querySelectorAll('.btn-review').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const review = btn.dataset.review;
                    const analysisId = btn.dataset.id;
                    await this.submitReview(analysisId, review);
                });
            });
        }, 100);
        
        return div;
    }

    /**
     * Submit manual review
     */
    async submitReview(analysisId, review) {
        try {
            const response = await fetch('/api/review-analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    analysis_id: analysisId,
                    review: review,
                    comment: ''
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert(`✅ Thank you for your feedback!`);
                // Reload history to show updated review status
                this.loadHistory();
            } else {
                alert(`❌ Failed to submit review: ${data.error}`);
            }
        } catch (error) {
            console.error('Review submission error:', error);
            alert(`❌ Error submitting review: ${error.message}`);
        }
    }

    /**
     * Show analysis details in modal
     */
    showDetails(item) {
        const response = item.ai_full_response || {};
        const tracking = item.tracking_result || {};
        const snapshot = item.market_snapshot || {};
        
        const modal = document.createElement('div');
        modal.className = 'history-modal';
        modal.innerHTML = `
            <div class="modal-overlay"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>📊 Chi Tiết Phân Tích: ${item.symbol}</h3>
                    <button class="modal-close">✕</button>
                </div>
                <div class="modal-body">
                    <div class="detail-section">
                        <h4>🤖 AI Analysis</h4>
                        <pre>${JSON.stringify(response, null, 2)}</pre>
                    </div>
                    <div class="detail-section">
                        <h4>📈 Market Snapshot</h4>
                        <pre>${JSON.stringify(snapshot, null, 2)}</pre>
                    </div>
                    ${Object.keys(tracking).length > 0 ? `
                    <div class="detail-section">
                        <h4>🎯 Tracking Result</h4>
                        <pre>${JSON.stringify(tracking, null, 2)}</pre>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close handlers
        modal.querySelector('.modal-close')?.addEventListener('click', () => {
            modal.remove();
        });
        modal.querySelector('.modal-overlay')?.addEventListener('click', () => {
            modal.remove();
        });
    }

    /**
     * Show error message
     */
    showError(message) {
        const container = document.getElementById('history-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="history-error-state">
                <div class="error-illustration">
                    <svg width="100" height="100" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="40" fill="none" stroke="#F44336" stroke-width="3"/>
                        <line x1="35" y1="35" x2="65" y2="65" stroke="#F44336" stroke-width="3" stroke-linecap="round"/>
                        <line x1="65" y1="35" x2="35" y2="65" stroke="#F44336" stroke-width="3" stroke-linecap="round"/>
                    </svg>
                </div>
                <h3 class="error-title">Lỗi Tải Lịch Sử</h3>
                <p class="error-message">${message}</p>
                <button class="error-retry-btn" onclick="window.historyTab?.loadHistory()">
                    <span class="btn-icon">🔄</span> Thử Lại
                </button>
            </div>
        `;
    }
}

// Export for use in chart.html
window.AnalysisHistory = AnalysisHistory;
