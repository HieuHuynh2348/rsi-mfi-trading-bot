"""
Chart Generator Module
Creates technical analysis charts with candlesticks, RSI, and MFI
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np
import io
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ChartGenerator:
    def __init__(self, style='default', dpi=100, width=12, height=8):
        """Initialize chart generator"""
        self.style = style
        self.dpi = dpi
        self.width = width
        self.height = height
        
        # Color scheme
        self.colors = {
            'up': '#26A69A',      # Green for bullish candles
            'down': '#EF5350',    # Red for bearish candles
            'rsi': '#2962FF',     # Blue for RSI
            'mfi': '#FF6D00',     # Orange for MFI
            'volume': '#78909C',  # Gray for volume
            'grid': '#E0E0E0'     # Light gray for grid
        }
        
        # Set style
        if style == 'dark':
            plt.style.use('dark_background')
            self.colors['grid'] = '#424242'
        elif style == 'light':
            plt.style.use('default')
    
    def plot_candlestick(self, ax, df, width=0.6):
        """
        Plot candlestick chart
        
        Args:
            ax: Matplotlib axis
            df: DataFrame with OHLC data
            width: Candle width
        """
        for idx in range(len(df)):
            row = df.iloc[idx]
            
            # Determine color
            if row['close'] >= row['open']:
                color = self.colors['up']
                body_color = self.colors['up']
            else:
                color = self.colors['down']
                body_color = self.colors['down']
            
            # Draw high-low line (wick)
            ax.plot([idx, idx], [row['low'], row['high']], 
                   color=color, linewidth=1, alpha=0.8)
            
            # Draw open-close rectangle (body)
            height = abs(row['close'] - row['open'])
            bottom = min(row['open'], row['close'])
            
            rect = Rectangle((idx - width/2, bottom), width, height,
                           facecolor=body_color, edgecolor=color,
                           linewidth=1, alpha=0.9)
            ax.add_patch(rect)
    
    def create_rsi_mfi_chart(self, symbol, df, rsi_series, mfi_series, 
                            rsi_lower=20, rsi_upper=80, mfi_lower=20, mfi_upper=80,
                            timeframe='5m'):
        """
        Create a professional chart with candlesticks, RSI, and MFI
        
        Args:
            symbol: Trading symbol
            df: DataFrame with OHLCV data
            rsi_series: RSI values
            mfi_series: MFI values
            rsi_lower/upper: RSI thresholds
            mfi_lower/upper: MFI thresholds
            timeframe: Timeframe string
        
        Returns:
            BytesIO object containing PNG image
        """
        try:
            # Create figure with subplots
            fig = plt.figure(figsize=(self.width, self.height), dpi=self.dpi)
            gs = GridSpec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.05)
            
            # Limit to last 100 candles for better visibility
            display_length = min(100, len(df))
            df_display = df.iloc[-display_length:].reset_index(drop=True)
            rsi_display = rsi_series.iloc[-display_length:].reset_index(drop=True)
            mfi_display = mfi_series.iloc[-display_length:].reset_index(drop=True)
            
            # === CANDLESTICK CHART ===
            ax1 = fig.add_subplot(gs[0])
            self.plot_candlestick(ax1, df_display)
            
            # Add current price line
            current_price = df_display['close'].iloc[-1]
            ax1.axhline(y=current_price, color='blue', linestyle='--', 
                       linewidth=1, alpha=0.7, label=f'Current: ${current_price:,.4f}')
            
            # Title and labels
            price_change = ((df_display['close'].iloc[-1] - df_display['open'].iloc[0]) / 
                          df_display['open'].iloc[0] * 100)
            change_color = 'green' if price_change >= 0 else 'red'
            
            ax1.set_title(
                f'{symbol} | {timeframe.upper()} | {datetime.now().strftime("%Y-%m-%d %H:%M")}\n'
                f'Price: ${current_price:,.4f} ({price_change:+.2f}%)',
                fontsize=13, fontweight='bold', pad=10
            )
            ax1.set_ylabel('Price (USDT)', fontsize=10, fontweight='bold')
            ax1.legend(loc='upper left', fontsize=9)
            ax1.grid(True, alpha=0.3, color=self.colors['grid'])
            ax1.set_xlim(-0.5, len(df_display) - 0.5)
            
            # Format y-axis
            ax1.ticklabel_format(style='plain', axis='y')
            
            # Remove x-axis labels (will show on bottom chart)
            ax1.set_xticklabels([])
            
            # === VOLUME CHART ===
            ax_vol = fig.add_subplot(gs[1], sharex=ax1)
            
            # Color volume bars
            colors_vol = [self.colors['up'] if df_display['close'].iloc[i] >= df_display['open'].iloc[i] 
                         else self.colors['down'] for i in range(len(df_display))]
            
            ax_vol.bar(range(len(df_display)), df_display['volume'], 
                      color=colors_vol, alpha=0.6, width=0.8)
            ax_vol.set_ylabel('Volume', fontsize=9, fontweight='bold')
            ax_vol.grid(True, alpha=0.3, color=self.colors['grid'], axis='y')
            ax_vol.set_xticklabels([])
            
            # Format volume numbers
            ax_vol.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
            
            # === RSI CHART ===
            ax2 = fig.add_subplot(gs[2], sharex=ax1)
            ax2.plot(range(len(rsi_display)), rsi_display, 
                    label='RSI', color=self.colors['rsi'], linewidth=2)
            
            # RSI levels
            ax2.axhline(y=rsi_upper, color='#EF5350', linestyle='--', 
                       alpha=0.7, linewidth=1, label=f'Overbought ({rsi_upper})')
            ax2.axhline(y=50, color='gray', linestyle=':', alpha=0.5, linewidth=1)
            ax2.axhline(y=rsi_lower, color='#26A69A', linestyle='--', 
                       alpha=0.7, linewidth=1, label=f'Oversold ({rsi_lower})')
            
            # Fill areas
            ax2.fill_between(range(len(rsi_display)), rsi_lower, rsi_display, 
                            where=(rsi_display <= rsi_lower), 
                            alpha=0.3, color='#26A69A', interpolate=True)
            ax2.fill_between(range(len(rsi_display)), rsi_upper, rsi_display, 
                            where=(rsi_display >= rsi_upper), 
                            alpha=0.3, color='#EF5350', interpolate=True)
            
            # Current RSI value
            current_rsi = rsi_display.iloc[-1]
            rsi_status = "🟢 Oversold" if current_rsi <= rsi_lower else ("🔴 Overbought" if current_rsi >= rsi_upper else "⚪ Neutral")
            
            ax2.set_ylabel(f'RSI: {current_rsi:.1f}\n{rsi_status.split()[1]}', 
                          fontsize=9, fontweight='bold')
            ax2.set_ylim(0, 100)
            ax2.legend(loc='upper left', fontsize=8, ncol=3)
            ax2.grid(True, alpha=0.3, color=self.colors['grid'])
            ax2.set_xticklabels([])
            
            # === MFI CHART ===
            ax3 = fig.add_subplot(gs[3], sharex=ax1)
            ax3.plot(range(len(mfi_display)), mfi_display, 
                    label='MFI', color=self.colors['mfi'], linewidth=2)
            
            # MFI levels
            ax3.axhline(y=mfi_upper, color='#EF5350', linestyle='--', 
                       alpha=0.7, linewidth=1, label=f'Overbought ({mfi_upper})')
            ax3.axhline(y=50, color='gray', linestyle=':', alpha=0.5, linewidth=1)
            ax3.axhline(y=mfi_lower, color='#26A69A', linestyle='--', 
                       alpha=0.7, linewidth=1, label=f'Oversold ({mfi_lower})')
            
            # Fill areas
            ax3.fill_between(range(len(mfi_display)), mfi_lower, mfi_display, 
                            where=(mfi_display <= mfi_lower), 
                            alpha=0.3, color='#26A69A', interpolate=True)
            ax3.fill_between(range(len(mfi_display)), mfi_upper, mfi_display, 
                            where=(mfi_display >= mfi_upper), 
                            alpha=0.3, color='#EF5350', interpolate=True)
            
            # Current MFI value
            current_mfi = mfi_display.iloc[-1]
            mfi_status = "🟢 Oversold" if current_mfi <= mfi_lower else ("🔴 Overbought" if current_mfi >= mfi_upper else "⚪ Neutral")
            
            ax3.set_ylabel(f'MFI: {current_mfi:.1f}\n{mfi_status.split()[1]}', 
                          fontsize=9, fontweight='bold')
            ax3.set_xlabel('Candles (Most Recent →)', fontsize=10)
            ax3.set_ylim(0, 100)
            ax3.legend(loc='upper left', fontsize=8, ncol=3)
            ax3.grid(True, alpha=0.3, color=self.colors['grid'])
            
            # X-axis: Show only a few labels
            tick_spacing = max(1, len(df_display) // 6)
            ax3.set_xticks(range(0, len(df_display), tick_spacing))
            ax3.set_xticklabels([f'{i}' for i in range(0, len(df_display), tick_spacing)], 
                               rotation=0, fontsize=8)
            
            # Add consensus indicator
            avg_indicator = (current_rsi + current_mfi) / 2
            if avg_indicator <= 20:
                consensus = "🟢 STRONG BUY"
                consensus_color = '#26A69A'
            elif avg_indicator >= 80:
                consensus = "🔴 STRONG SELL"
                consensus_color = '#EF5350'
            elif avg_indicator <= 30:
                consensus = "🟢 BUY"
                consensus_color = '#66BB6A'
            elif avg_indicator >= 70:
                consensus = "🔴 SELL"
                consensus_color = '#FF7043'
            else:
                consensus = "⚪ NEUTRAL"
                consensus_color = 'gray'
            
            # Add text box with consensus
            fig.text(0.99, 0.01, f'Consensus: {consensus}', 
                    fontsize=11, fontweight='bold',
                    ha='right', va='bottom',
                    bbox=dict(boxstyle='round,pad=0.5', 
                            facecolor=consensus_color, 
                            edgecolor='black', 
                            alpha=0.7),
                    color='white')
            
            # Save to BytesIO
            buf = io.BytesIO()
            plt.tight_layout(rect=[0, 0.02, 1, 1])  # Leave space for consensus box
            plt.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            buf.seek(0)
            plt.close(fig)
            
            logger.info(f"Enhanced chart created for {symbol} - {timeframe}")
            return buf
            
        except Exception as e:
            logger.error(f"Error creating chart: {e}", exc_info=True)
            return None
    
    def create_multi_timeframe_chart(self, symbol, timeframe_data, price=None):
        """
        Create an enhanced summary chart showing all timeframes with better visualization
        
        Args:
            symbol: Trading symbol
            timeframe_data: Dictionary of {timeframe: analysis_data}
            price: Current price
        
        Returns:
            BytesIO object containing PNG image
        """
        try:
            fig = plt.figure(figsize=(self.width, 6), dpi=self.dpi)
            gs = GridSpec(2, 1, height_ratios=[3, 1], hspace=0.3)
            
            timeframes = sorted(list(timeframe_data.keys()), 
                              key=lambda x: {'5m': 1, '1h': 2, '3h': 3, '4h': 3.5, '1d': 4}.get(x, 5))
            n_tf = len(timeframes)
            
            if n_tf == 0:
                plt.close(fig)
                return None
            
            # Prepare data
            rsi_values = [timeframe_data[tf]['rsi'] for tf in timeframes]
            mfi_values = [timeframe_data[tf]['mfi'] for tf in timeframes]
            signals = [timeframe_data[tf]['signal'] for tf in timeframes]
            avg_values = [(rsi_values[i] + mfi_values[i]) / 2 for i in range(n_tf)]
            
            # === MAIN CHART: RSI vs MFI Bars ===
            ax1 = fig.add_subplot(gs[0, :])
            
            x = np.arange(n_tf)
            width = 0.35
            
            # Create bars with gradient colors
            bars_rsi = ax1.bar(x - width/2, rsi_values, width, 
                             label='RSI', color=self.colors['rsi'], 
                             alpha=0.8, edgecolor='black', linewidth=0.5)
            bars_mfi = ax1.bar(x + width/2, mfi_values, width, 
                             label='MFI', color=self.colors['mfi'], 
                             alpha=0.8, edgecolor='black', linewidth=0.5)
            
            # Add value labels on bars
            for i, (rsi, mfi) in enumerate(zip(rsi_values, mfi_values)):
                ax1.text(i - width/2, rsi + 2, f'{rsi:.1f}', 
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
                ax1.text(i + width/2, mfi + 2, f'{mfi:.1f}', 
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            # Add signal markers
            for i, signal in enumerate(signals):
                if signal == 1:  # BUY
                    ax1.scatter(i, 10, marker='^', s=200, color='#26A69A', 
                              edgecolors='black', linewidths=2, zorder=5,
                              label='BUY Signal' if i == signals.index(1) else '')
                    ax1.text(i, 5, '🟢', ha='center', fontsize=16)
                elif signal == -1:  # SELL
                    ax1.scatter(i, 90, marker='v', s=200, color='#EF5350', 
                              edgecolors='black', linewidths=2, zorder=5,
                              label='SELL Signal' if i == signals.index(-1) else '')
                    ax1.text(i, 95, '🔴', ha='center', fontsize=16)
            
            # Reference lines
            ax1.axhline(y=80, color='#EF5350', linestyle='--', alpha=0.6, 
                       linewidth=2, label='Overbought (80)')
            ax1.axhline(y=50, color='gray', linestyle=':', alpha=0.5, linewidth=1.5)
            ax1.axhline(y=20, color='#26A69A', linestyle='--', alpha=0.6, 
                       linewidth=2, label='Oversold (20)')
            
            # Fill zones
            ax1.fill_between([-0.5, n_tf-0.5], 80, 100, alpha=0.1, color='#EF5350')
            ax1.fill_between([-0.5, n_tf-0.5], 0, 20, alpha=0.1, color='#26A69A')
            
            # Labels and title
            ax1.set_ylabel('Indicator Value', fontsize=11, fontweight='bold')
            title_text = f'{symbol} - Multi-Timeframe Analysis'
            if price:
                title_text += f'\nCurrent Price: ${price:,.4f}'
            ax1.set_title(title_text, fontsize=14, fontweight='bold', pad=15)
            ax1.set_xticks(x)
            ax1.set_xticklabels([tf.upper() for tf in timeframes], fontsize=11, fontweight='bold')
            ax1.legend(loc='upper right', fontsize=9, ncol=2)
            ax1.set_ylim(0, 105)
            ax1.grid(True, alpha=0.3, axis='y', color=self.colors['grid'])
            ax1.set_xlim(-0.5, n_tf - 0.5)
            
            # === BOTTOM: TradingView Link Info ===
            # Instead of Combined Signal chart, show TradingView link info
            ax2 = fig.add_subplot(gs[1, :])
            ax2.axis('off')
            
            # Count signals for summary
            buy_count = signals.count(1)
            sell_count = signals.count(-1)
            neutral_count = signals.count(0)
            
            # Determine overall consensus
            if buy_count > sell_count and buy_count > neutral_count:
                overall = f"🟢 BUY"
                consensus_color = '#26A69A'
                strength_emoji = '🚀'
            elif sell_count > buy_count and sell_count > neutral_count:
                overall = f"🔴 SELL"
                consensus_color = '#EF5350'
                strength_emoji = '⚠️'
            else:
                overall = f"⚪ NEUTRAL"
                consensus_color = 'gray'
                strength_emoji = '➡️'
            
            # Calculate strength
            max_signal = max(buy_count, sell_count, neutral_count)
            if max_signal >= n_tf * 0.75:
                strength = 'STRONG'
            elif max_signal >= n_tf * 0.5:
                strength = 'MODERATE'
            else:
                strength = 'WEAK'
            
            # Create TradingView link
            base_symbol = symbol.replace('USDT', '').replace('BUSD', '').replace('BTC', '')
            tv_link = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}"
            
            # Create summary with TradingView info
            summary_text = f"""
{strength_emoji} SIGNAL CONSENSUS: {overall} ({strength})

📊 Breakdown: 🟢 {buy_count} BUY  |  🔴 {sell_count} SELL  |  ⚪ {neutral_count} NEUTRAL  (Total: {n_tf} timeframes)

📈 View detailed TradingView chart:
{tv_link}

⏰ Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            """
            
            ax2.text(0.5, 0.5, summary_text.strip(), 
                    fontsize=10, ha='center', va='center',
                    family='monospace',
                    bbox=dict(boxstyle='round,pad=1.2', 
                            facecolor=consensus_color, 
                            edgecolor='black',
                            alpha=0.2, linewidth=2))
            
            # Save to BytesIO
            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            buf.seek(0)
            plt.close(fig)
            
            logger.info(f"Enhanced multi-timeframe chart created for {symbol}")
            return buf
            
        except Exception as e:
            logger.error(f"Error creating multi-timeframe chart: {e}", exc_info=True)
            return None
