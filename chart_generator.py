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
            df_display = df.iloc[-display_length:].copy()
            
            # Reset index but keep timestamp as column
            if df_display.index.name == 'timestamp' or 'timestamp' in str(type(df_display.index)):
                df_display = df_display.reset_index()
            
            df_display = df_display.reset_index(drop=True)
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
            ax3.set_xlabel('Time', fontsize=10)
            ax3.set_ylim(0, 100)
            ax3.legend(loc='upper left', fontsize=8, ncol=3)
            ax3.grid(True, alpha=0.3, color=self.colors['grid'])
            
            # X-axis: Format with timestamps
            tick_spacing = max(1, len(df_display) // 8)
            tick_positions = range(0, len(df_display), tick_spacing)
            ax3.set_xticks(tick_positions)
            
            # Format timestamps if available
            if 'timestamp' in df_display.columns:
                tick_labels = []
                for pos in tick_positions:
                    ts = df_display.iloc[pos]['timestamp']
                    if isinstance(ts, (int, float)):
                        dt = pd.to_datetime(ts, unit='ms')
                    else:
                        dt = pd.to_datetime(ts)
                    
                    # Format based on timeframe
                    if timeframe in ['5m', '15m', '30m', '1h']:
                        label = dt.strftime('%m/%d %H:%M')
                    elif timeframe in ['3h', '4h']:
                        label = dt.strftime('%m/%d %H:00')
                    else:  # 1d
                        label = dt.strftime('%Y-%m-%d')
                    tick_labels.append(label)
                
                ax3.set_xticklabels(tick_labels, rotation=45, ha='right', fontsize=8)
            else:
                # Fallback to index if no timestamp
                ax3.set_xticklabels([f'{i}' for i in tick_positions], fontsize=8)
            
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
    
    def create_multi_timeframe_chart(self, symbol, timeframe_data, price=None, klines_dict=None):
        """
        Create multi-timeframe candlestick chart (TradingView style)
        Shows candlestick charts for all timeframes in separate panels
        
        Args:
            symbol: Trading symbol
            timeframe_data: Dictionary of {timeframe: analysis_data}
            price: Current price
            klines_dict: Dictionary of {timeframe: DataFrame} with OHLCV data
        
        Returns:
            BytesIO object containing PNG image
        """
        try:
            # Get timeframes and OHLCV data
            timeframes = sorted(list(timeframe_data.keys()), 
                              key=lambda x: {'5m': 1, '1h': 2, '3h': 3, '4h': 3.5, '1d': 4}.get(x, 5))
            n_tf = len(timeframes)
            
            if n_tf == 0:
                return None
            
            # Create figure with subplots for each timeframe
            fig = plt.figure(figsize=(self.width, n_tf * 3), dpi=self.dpi)
            gs = GridSpec(n_tf, 1, hspace=0.4)
            
            # Plot candlestick for each timeframe
            for idx, tf in enumerate(timeframes):
                ax = fig.add_subplot(gs[idx, 0])
                
                # Get OHLCV data from klines_dict
                df = None
                if klines_dict and tf in klines_dict:
                    df = klines_dict[tf]
                
                # Get analysis data
                tf_data = timeframe_data[tf]
                
                # Check if we have DataFrame
                if df is not None and len(df) > 0:
                    
                    # Take last 100 candles for better visualization
                    df_plot = df.tail(100).copy()
                    
                    # Reset index but keep timestamp as column
                    if df_plot.index.name == 'timestamp' or 'timestamp' in str(type(df_plot.index)):
                        df_plot = df_plot.reset_index()
                    
                    df_plot = df_plot.reset_index(drop=True)
                    
                    # Plot candlesticks
                    self.plot_candlestick(ax, df_plot, width=0.6)
                    
                    # Format x-axis with timestamps
                    n_candles = len(df_plot)
                    tick_positions = np.linspace(0, n_candles-1, min(8, n_candles), dtype=int)
                    
                    ax.set_xticks(tick_positions)
                    
                    # Format timestamps
                    if 'timestamp' in df_plot.columns:
                        tick_labels = []
                        for pos in tick_positions:
                            ts = df_plot.iloc[pos]['timestamp']
                            if isinstance(ts, (int, float)):
                                dt = pd.to_datetime(ts, unit='ms')
                            else:
                                dt = pd.to_datetime(ts)
                            
                            # Format based on timeframe
                            if tf in ['5m', '15m', '30m', '1h']:
                                label = dt.strftime('%m/%d %H:%M')
                            elif tf in ['3h', '4h']:
                                label = dt.strftime('%m/%d %H:00')
                            else:  # 1d
                                label = dt.strftime('%Y-%m-%d')
                            tick_labels.append(label)
                        
                        ax.set_xticklabels(tick_labels, rotation=45, ha='right', fontsize=8)
                    else:
                        ax.set_xticklabels([f'C{i}' for i in tick_positions], fontsize=8)
                    
                    # Get price range for y-axis
                    high_max = df_plot['high'].max()
                    low_min = df_plot['low'].min()
                    price_range = high_max - low_min
                    
                    # Set y-axis limits with padding
                    ax.set_ylim(low_min - price_range * 0.05, high_max + price_range * 0.05)
                    
                    # Add current price line if this is the last timeframe
                    if price and idx == n_tf - 1:
                        ax.axhline(y=price, color='blue', linestyle='--', 
                                 linewidth=1.5, alpha=0.7, label=f'Current: ${price:,.2f}')
                        ax.legend(loc='upper left', fontsize=9)
                    
                    # Get signal from analysis
                    signal = tf_data.get('signal', 0)
                    rsi = tf_data.get('rsi', 0)
                    mfi = tf_data.get('mfi', 0)
                    
                    # Determine signal text and color
                    if signal == 1:
                        signal_text = f'🟢 BUY'
                        signal_color = '#26A69A'
                    elif signal == -1:
                        signal_text = f'🔴 SELL'
                        signal_color = '#EF5350'
                    else:
                        signal_text = f'⚪ NEUTRAL'
                        signal_color = 'gray'
                    
                    # Title with timeframe and signal
                    title = f'{symbol} - {tf.upper()} | {signal_text} | RSI: {rsi:.1f} | MFI: {mfi:.1f}'
                    ax.set_title(title, fontsize=11, fontweight='bold', 
                               bbox=dict(boxstyle='round,pad=0.5', 
                                       facecolor=signal_color, 
                                       edgecolor='black',
                                       alpha=0.3, linewidth=1.5))
                    
                    ax.set_ylabel('Price (USDT)', fontsize=10, fontweight='bold')
                    ax.set_xlabel('Time', fontsize=10, fontweight='bold')
                    ax.grid(True, alpha=0.3, color=self.colors['grid'], linestyle=':')
                    
                else:
                    # No data available
                    ax.text(0.5, 0.5, f'No data for {tf.upper()}', 
                           ha='center', va='center', fontsize=12,
                           transform=ax.transAxes)
                    ax.set_title(f'{symbol} - {tf.upper()}', fontsize=11, fontweight='bold')
                    ax.axis('off')
            
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
