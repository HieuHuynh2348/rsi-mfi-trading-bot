/**
 * Analytics Module - Chart.js Visualizations for Trading History
 * Provides: Win Rate Chart, RSI/MFI Heatmap, Timing Analysis, PnL Distribution
 */

class AnalyticsModule {
    constructor(history = []) {
        this.history = history;
        this.charts = {};
    }

    /**
     * Update history data
     */
    updateHistory(history) {
        this.history = history;
    }

    /**
     * Render all analytics charts
     */
    renderAll(containerId = 'analytics-container') {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('Analytics container not found');
            return;
        }

        container.innerHTML = `
            <div class="analytics-grid">
                <div class="chart-card">
                    <h3>📈 Win Rate Over Time</h3>
                    <canvas id="win-rate-chart"></canvas>
                </div>
                
                <div class="chart-card">
                    <h3>🎯 RSI/MFI Heatmap</h3>
                    <canvas id="rsi-mfi-heatmap"></canvas>
                </div>
                
                <div class="chart-card">
                    <h3>⏰ Best Entry Times</h3>
                    <canvas id="timing-chart"></canvas>
                </div>
                
                <div class="chart-card">
                    <h3>💰 Profit/Loss Distribution</h3>
                    <canvas id="pnl-chart"></canvas>
                </div>
            </div>
        `;

        this.renderWinRateChart();
        this.renderRSIMFIHeatmap();
        this.renderTimingChart();
        this.renderPnLChart();
    }

    /**
     * 1. Win Rate Line Chart Over Time
     */
    renderWinRateChart() {
        const ctx = document.getElementById('win-rate-chart');
        if (!ctx) return;

        // Group by date and calculate rolling win rate
        const dateGroups = this.groupByDate();
        const dates = Object.keys(dateGroups).sort();
        const winRates = dates.map(date => {
            const analyses = dateGroups[date];
            const wins = analyses.filter(a => a.tracking_result?.result === 'WIN').length;
            const completed = analyses.filter(a => 
                a.tracking_result?.result === 'WIN' || 
                a.tracking_result?.result === 'LOSS'
            ).length;
            return completed > 0 ? (wins / completed * 100).toFixed(1) : 0;
        });

        // Destroy existing chart
        if (this.charts.winRate) {
            this.charts.winRate.destroy();
        }

        this.charts.winRate = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates.map(d => new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
                datasets: [{
                    label: 'Win Rate %',
                    data: winRates,
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => `Win Rate: ${context.parsed.y}%`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: (value) => value + '%' }
                    }
                }
            }
        });
    }

    /**
     * 2. RSI/MFI Heatmap - Win Rate by RSI and MFI Zones
     */
    renderRSIMFIHeatmap() {
        const ctx = document.getElementById('rsi-mfi-heatmap');
        if (!ctx) return;

        // Group analyses by RSI/MFI zones
        const zones = this.calculateRSIMFIZones();
        
        // Create bubble chart (simulates heatmap)
        const bubbleData = [];
        Object.keys(zones).forEach(key => {
            const [rsiZone, mfiZone] = key.split('-');
            const data = zones[key];
            if (data.total > 0) {
                bubbleData.push({
                    x: this.getZoneValue(rsiZone),
                    y: this.getZoneValue(mfiZone),
                    r: Math.sqrt(data.total) * 5, // Bubble size
                    winRate: data.winRate,
                    total: data.total
                });
            }
        });

        if (this.charts.heatmap) {
            this.charts.heatmap.destroy();
        }

        this.charts.heatmap = new Chart(ctx, {
            type: 'bubble',
            data: {
                datasets: [{
                    label: 'Win Rate by RSI/MFI',
                    data: bubbleData,
                    backgroundColor: bubbleData.map(d => 
                        d.winRate >= 60 ? 'rgba(76, 175, 80, 0.7)' :
                        d.winRate >= 40 ? 'rgba(255, 193, 7, 0.7)' :
                        'rgba(244, 67, 54, 0.7)'
                    )
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const d = context.raw;
                                return [
                                    `Win Rate: ${d.winRate.toFixed(1)}%`,
                                    `Total Trades: ${d.total}`,
                                    `RSI: ${this.getZoneLabel(d.x)}`,
                                    `MFI: ${this.getZoneLabel(d.y)}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'RSI Zone' },
                        ticks: {
                            callback: (value) => this.getZoneLabel(value)
                        }
                    },
                    y: {
                        title: { display: true, text: 'MFI Zone' },
                        ticks: {
                            callback: (value) => this.getZoneLabel(value)
                        }
                    }
                }
            }
        });
    }

    /**
     * 3. Entry Timing Analysis - Best Hours/Days to Trade
     */
    renderTimingChart() {
        const ctx = document.getElementById('timing-chart');
        if (!ctx) return;

        const timingStats = this.calculateTimingStats();
        
        if (this.charts.timing) {
            this.charts.timing.destroy();
        }

        this.charts.timing = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
                datasets: [{
                    label: 'Win Rate %',
                    data: timingStats.daily,
                    backgroundColor: timingStats.daily.map(wr => 
                        wr >= 60 ? '#4CAF50' : wr >= 40 ? '#FFC107' : '#F44336'
                    )
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => `Win Rate: ${context.parsed.y.toFixed(1)}%`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: (value) => value + '%' }
                    }
                }
            }
        });
    }

    /**
     * 4. Profit/Loss Distribution Histogram
     */
    renderPnLChart() {
        const ctx = document.getElementById('pnl-chart');
        if (!ctx) return;

        const pnlData = this.history
            .filter(a => a.tracking_result?.pnl_percent)
            .map(a => a.tracking_result.pnl_percent);

        if (pnlData.length === 0) {
            ctx.getContext('2d').clearRect(0, 0, ctx.width, ctx.height);
            return;
        }

        // Create bins: [-10 to -5], [-5 to 0], [0 to 5], [5 to 10], [10+]
        const bins = {
            '<-5%': 0, '-5 to 0%': 0, '0 to 5%': 0, '5 to 10%': 0, '>10%': 0
        };

        pnlData.forEach(pnl => {
            if (pnl < -5) bins['<-5%']++;
            else if (pnl < 0) bins['-5 to 0%']++;
            else if (pnl < 5) bins['0 to 5%']++;
            else if (pnl < 10) bins['5 to 10%']++;
            else bins['>10%']++;
        });

        if (this.charts.pnl) {
            this.charts.pnl.destroy();
        }

        this.charts.pnl = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(bins),
                datasets: [{
                    label: 'Number of Trades',
                    data: Object.values(bins),
                    backgroundColor: ['#F44336', '#FF9800', '#FFC107', '#8BC34A', '#4CAF50']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
    }

    /**
     * Helper: Group history by date
     */
    groupByDate() {
        const groups = {};
        this.history.forEach(analysis => {
            const date = new Date(analysis.created_at).toISOString().split('T')[0];
            if (!groups[date]) groups[date] = [];
            groups[date].push(analysis);
        });
        return groups;
    }

    /**
     * Helper: Calculate RSI/MFI zone win rates
     */
    calculateRSIMFIZones() {
        const zones = {};
        
        this.history.forEach(analysis => {
            const snapshot = analysis.market_snapshot;
            if (!snapshot?.rsi || !snapshot?.mfi) return;

            const rsiZone = this.getRSIZone(snapshot.rsi);
            const mfiZone = this.getMFIZone(snapshot.mfi);
            const key = `${rsiZone}-${mfiZone}`;

            if (!zones[key]) {
                zones[key] = { wins: 0, losses: 0, total: 0, winRate: 0 };
            }

            const result = analysis.tracking_result?.result;
            if (result === 'WIN') zones[key].wins++;
            if (result === 'LOSS') zones[key].losses++;
            if (result === 'WIN' || result === 'LOSS') {
                zones[key].total++;
                zones[key].winRate = (zones[key].wins / zones[key].total) * 100;
            }
        });

        return zones;
    }

    /**
     * Helper: Calculate timing statistics
     */
    calculateTimingStats() {
        const daily = [0, 0, 0, 0, 0, 0, 0]; // Win rate by day of week
        const dayCounts = [0, 0, 0, 0, 0, 0, 0];
        const dayWins = [0, 0, 0, 0, 0, 0, 0];

        this.history.forEach(analysis => {
            const result = analysis.tracking_result?.result;
            if (result !== 'WIN' && result !== 'LOSS') return;

            const date = new Date(analysis.created_at);
            const dayOfWeek = date.getDay();

            dayCounts[dayOfWeek]++;
            if (result === 'WIN') dayWins[dayOfWeek]++;
        });

        for (let i = 0; i < 7; i++) {
            daily[i] = dayCounts[i] > 0 ? (dayWins[i] / dayCounts[i]) * 100 : 0;
        }

        return { daily };
    }

    /**
     * Zone helpers
     */
    getRSIZone(rsi) {
        if (rsi <= 20) return 'OVERSOLD';
        if (rsi <= 40) return 'LOW';
        if (rsi <= 60) return 'NEUTRAL';
        if (rsi <= 80) return 'HIGH';
        return 'OVERBOUGHT';
    }

    getMFIZone(mfi) {
        if (mfi <= 20) return 'OVERSOLD';
        if (mfi <= 40) return 'LOW';
        if (mfi <= 60) return 'NEUTRAL';
        if (mfi <= 80) return 'HIGH';
        return 'OVERBOUGHT';
    }

    getZoneValue(zone) {
        const map = { 'OVERSOLD': 10, 'LOW': 30, 'NEUTRAL': 50, 'HIGH': 70, 'OVERBOUGHT': 90 };
        return map[zone] || 50;
    }

    getZoneLabel(value) {
        if (value <= 20) return 'OVERSOLD';
        if (value <= 40) return 'LOW';
        if (value <= 60) return 'NEUTRAL';
        if (value <= 80) return 'HIGH';
        return 'OVERBOUGHT';
    }

    /**
     * Destroy all charts (cleanup)
     */
    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AnalyticsModule;
}
