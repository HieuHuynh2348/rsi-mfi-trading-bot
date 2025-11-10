/**
 * Analysis History Module
 * Displays past AI analyses with filtering and statistics
 */

class AnalysisHistory {
    constructor(userId) {
        this.userId = userId;
        this.history = [];
        this.filteredHistory = [];
        this.stats = null;
    }

    /**
     * Load history from API
     */
    async loadHistory(symbol = null, days = 7) {
        try {
            const params = new URLSearchParams({
                user_id: this.userId,
                days: days
            });
            
            if (symbol) {
                params.append('symbol', symbol);
            }
            
            const response = await fetch(`/api/analysis-history?${params}`);
            const data = await response.json();
            
            if (data.success) {
                this.history = data.history || [];
                this.stats = data.stats;
                this.filteredHistory = [...this.history];
                this.render();
                return true;
            } else {
                console.error('Failed to load history:', data.error);
                this.showError(data.error);
                return false;
            }
        } catch (error) {
            console.error('Error loading history:', error);
            this.showError(error.message);
            return false;
        }
    }

    /**
     * Filter history by criteria
     */
    filterHistory(filters = {}) {
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
        
        this.render();
    }

    /**
     * Render history UI
     */
    render() {
        const container = document.getElementById('history-container');
        if (!container) return;
        
        // Clear container
        container.innerHTML = '';
        
        // Render stats if available
        if (this.stats) {
            container.appendChild(this.renderStats());
        }
        
        // Add Analytics Toggle Button
        container.appendChild(this.renderAnalyticsButton());
        
        // Render filters
        container.appendChild(this.renderFilters());
        
        // Add Export CSV button
        const exportBtn = document.createElement('button');
        exportBtn.className = 'export-csv-btn';
        exportBtn.innerHTML = '📥 Export CSV';
        exportBtn.onclick = () => this.exportToCSV();
        container.appendChild(exportBtn);
        
        // Render history list
        if (this.filteredHistory.length === 0) {
            container.appendChild(this.renderEmpty());
        } else {
            container.appendChild(this.renderList());
        }
    }

    /**
     * Export history to CSV
     */
    exportToCSV() {
        if (this.history.length === 0) {
            alert('No data to export');
            return;
        }
        
        // CSV headers
        const headers = [
            'Date', 'Symbol', 'Recommendation', 'Confidence', 
            'Entry', 'Stop Loss', 'TP1', 'TP2', 'TP3',
            'Result', 'PnL %', 'Exit Price', 'Exit Reason',
            'Manual Review'
        ];
        
        // CSV rows
        const rows = this.history.map(item => {
            const response = item.ai_full_response || {};
            const tracking = item.tracking_result || {};
            const tps = response.take_profit || [];
            
            return [
                new Date(item.created_at).toLocaleString(),
                item.symbol,
                response.recommendation || 'N/A',
                response.confidence || 0,
                response.entry_point || 0,
                response.stop_loss || 0,
                tps[0] || 0,
                tps[1] || 0,
                tps[2] || 0,
                tracking.result || 'PENDING',
                tracking.pnl_percent || 0,
                tracking.exit_price || 0,
                tracking.exit_reason || '',
                tracking.manual_review || ''
            ].map(v => `"${v}"`).join(',');
        });
        
        // Create CSV content
        const csv = [headers.join(','), ...rows].join('\n');
        
        // Download file
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `analysis-history-${Date.now()}.csv`;
        link.click();
        
        alert('✅ CSV exported successfully!');
    }

    /**
     * Render Analytics Toggle Button
     */
    renderAnalyticsButton() {
        const div = document.createElement('div');
        div.innerHTML = `
            <button class="analytics-toggle" onclick="historyModule.toggleAnalytics()">
                📊 Advanced Analytics
            </button>
            <div id="analytics-container" style="display: none;"></div>
        `;
        return div;
    }

    /**
     * Toggle Analytics View
     */
    toggleAnalytics() {
        const analyticsContainer = document.getElementById('analytics-container');
        const button = document.querySelector('.analytics-toggle');
        
        if (analyticsContainer.style.display === 'none') {
            // Show analytics
            analyticsContainer.style.display = 'block';
            button.textContent = '📋 Back to History';
            
            // Initialize analytics module
            if (!this.analyticsModule) {
                this.analyticsModule = new AnalyticsModule(this.history);
            } else {
                this.analyticsModule.updateHistory(this.history);
            }
            
            this.analyticsModule.renderAll('analytics-container');
        } else {
            // Hide analytics
            analyticsContainer.style.display = 'none';
            button.textContent = '📊 Advanced Analytics';
        }
    }

    /**
     * Render statistics card
     */
    renderStats() {
        const stats = this.stats;
        const div = document.createElement('div');
        div.className = 'history-stats';
        div.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${stats.total || 0}</div>
                    <div class="stat-label">Tổng Phân Tích</div>
                </div>
                <div class="stat-card success">
                    <div class="stat-value">${stats.wins || 0}</div>
                    <div class="stat-label">Thắng</div>
                </div>
                <div class="stat-card danger">
                    <div class="stat-value">${stats.losses || 0}</div>
                    <div class="stat-label">Thua</div>
                </div>
                <div class="stat-card primary">
                    <div class="stat-value">${(stats.win_rate || 0).toFixed(1)}%</div>
                    <div class="stat-label">Tỷ Lệ Thắng</div>
                </div>
                <div class="stat-card success">
                    <div class="stat-value">+${(stats.avg_profit || 0).toFixed(2)}%</div>
                    <div class="stat-label">Lãi TB</div>
                </div>
                <div class="stat-card danger">
                    <div class="stat-value">${(stats.avg_loss || 0).toFixed(2)}%</div>
                    <div class="stat-label">Lỗ TB</div>
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
        div.className = 'history-filters';
        
        // Get unique symbols
        const symbols = [...new Set(this.history.map(item => item.symbol))].sort();
        
        div.innerHTML = `
            <div class="filter-row">
                <select id="filter-symbol" class="filter-select">
                    <option value="">Tất cả Symbols</option>
                    ${symbols.map(s => `<option value="${s}">${s}</option>`).join('')}
                </select>
                
                <select id="filter-recommendation" class="filter-select">
                    <option value="">Tất cả Khuyến Nghị</option>
                    <option value="BUY">🟢 BUY</option>
                    <option value="SELL">🔴 SELL</option>
                    <option value="WAIT">⚪ WAIT</option>
                    <option value="HOLD">🟡 HOLD</option>
                </select>
                
                <select id="filter-result" class="filter-select">
                    <option value="">Tất cả Kết Quả</option>
                    <option value="WIN">✅ WIN</option>
                    <option value="LOSS">❌ LOSS</option>
                    <option value="EXPIRED">⏱️ EXPIRED</option>
                </select>
                
                <button id="filter-reset" class="btn-reset">🔄 Reset</button>
            </div>
        `;
        
        // Add event listeners
        setTimeout(() => {
            document.getElementById('filter-symbol')?.addEventListener('change', (e) => {
                this.filterHistory({
                    symbol: e.target.value || undefined,
                    recommendation: document.getElementById('filter-recommendation')?.value || undefined,
                    result: document.getElementById('filter-result')?.value || undefined
                });
            });
            
            document.getElementById('filter-recommendation')?.addEventListener('change', (e) => {
                this.filterHistory({
                    symbol: document.getElementById('filter-symbol')?.value || undefined,
                    recommendation: e.target.value || undefined,
                    result: document.getElementById('filter-result')?.value || undefined
                });
            });
            
            document.getElementById('filter-result')?.addEventListener('change', (e) => {
                this.filterHistory({
                    symbol: document.getElementById('filter-symbol')?.value || undefined,
                    recommendation: document.getElementById('filter-recommendation')?.value || undefined,
                    result: e.target.value || undefined
                });
            });
            
            document.getElementById('filter-reset')?.addEventListener('click', () => {
                document.getElementById('filter-symbol').value = '';
                document.getElementById('filter-recommendation').value = '';
                document.getElementById('filter-result').value = '';
                this.filteredHistory = [...this.history];
                this.render();
            });
        }, 100);
        
        return div;
    }

    /**
     * Render empty state
     */
    renderEmpty() {
        const div = document.createElement('div');
        div.className = 'history-empty';
        div.innerHTML = `
            <div class="empty-icon">📊</div>
            <div class="empty-title">Chưa Có Lịch Sử Phân Tích</div>
            <div class="empty-text">
                Thực hiện phân tích AI đầu tiên để bắt đầu lưu lịch sử.
            </div>
        `;
        return div;
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
            <div class="history-error">
                <div class="error-icon">❌</div>
                <div class="error-title">Lỗi Tải Lịch Sử</div>
                <div class="error-text">${message}</div>
            </div>
        `;
    }
}

// Export for use in chart.html
window.AnalysisHistory = AnalysisHistory;
