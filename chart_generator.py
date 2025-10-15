"""
Chart Generator Module
Creates technical analysis charts
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
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
        
        # Set style
        if style == 'dark':
            plt.style.use('dark_background')
        elif style == 'light':
            plt.style.use('seaborn-v0_8-whitegrid')
    
    def create_rsi_mfi_chart(self, symbol, df, rsi_series, mfi_series, 
                            rsi_lower=20, rsi_upper=80, mfi_lower=20, mfi_upper=80,
                            timeframe='5m'):
        """
        Create a chart with price, RSI, and MFI
        
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
            fig = plt.figure(figsize=(self.width, self.height), dpi=self.dpi)
            gs = GridSpec(3, 1, height_ratios=[2, 1, 1], hspace=0.3)
            
            # Price chart
            ax1 = fig.add_subplot(gs[0])
            ax1.plot(df.index, df['close'], label='Close Price', color='#2962FF', linewidth=1.5)
            ax1.set_title(f'{symbol} - {timeframe.upper()} | {datetime.now().strftime("%Y-%m-%d %H:%M")}', 
                         fontsize=14, fontweight='bold')
            ax1.set_ylabel('Price (USDT)', fontsize=10)
            ax1.legend(loc='upper left')
            ax1.grid(True, alpha=0.3)
            
            # RSI chart
            ax2 = fig.add_subplot(gs[1])
            ax2.plot(rsi_series.index, rsi_series, label='RSI', color='#2962FF', linewidth=1.5)
            ax2.axhline(y=rsi_upper, color='red', linestyle='--', alpha=0.7, label=f'Overbought ({rsi_upper})')
            ax2.axhline(y=50, color='gray', linestyle=':', alpha=0.5)
            ax2.axhline(y=rsi_lower, color='green', linestyle='--', alpha=0.7, label=f'Oversold ({rsi_lower})')
            ax2.fill_between(rsi_series.index, rsi_lower, rsi_series, 
                            where=(rsi_series <= rsi_lower), alpha=0.3, color='green')
            ax2.fill_between(rsi_series.index, rsi_upper, rsi_series, 
                            where=(rsi_series >= rsi_upper), alpha=0.3, color='red')
            ax2.set_ylabel('RSI', fontsize=10)
            ax2.set_ylim(0, 100)
            ax2.legend(loc='upper left', fontsize=8)
            ax2.grid(True, alpha=0.3)
            
            # MFI chart
            ax3 = fig.add_subplot(gs[2])
            ax3.plot(mfi_series.index, mfi_series, label='MFI', color='#FF6D00', linewidth=1.5)
            ax3.axhline(y=mfi_upper, color='red', linestyle='--', alpha=0.7, label=f'Overbought ({mfi_upper})')
            ax3.axhline(y=50, color='gray', linestyle=':', alpha=0.5)
            ax3.axhline(y=mfi_lower, color='green', linestyle='--', alpha=0.7, label=f'Oversold ({mfi_lower})')
            ax3.fill_between(mfi_series.index, mfi_lower, mfi_series, 
                            where=(mfi_series <= mfi_lower), alpha=0.3, color='green')
            ax3.fill_between(mfi_series.index, mfi_upper, mfi_series, 
                            where=(mfi_series >= mfi_upper), alpha=0.3, color='red')
            ax3.set_ylabel('MFI', fontsize=10)
            ax3.set_xlabel('Time', fontsize=10)
            ax3.set_ylim(0, 100)
            ax3.legend(loc='upper left', fontsize=8)
            ax3.grid(True, alpha=0.3)
            
            # Rotate x-axis labels
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Save to BytesIO
            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)
            
            logger.info(f"Chart created for {symbol}")
            return buf
            
        except Exception as e:
            logger.error(f"Error creating chart: {e}")
            return None
    
    def create_multi_timeframe_chart(self, symbol, timeframe_data, price=None):
        """
        Create a summary chart showing all timeframes
        
        Args:
            symbol: Trading symbol
            timeframe_data: Dictionary of {timeframe: analysis_data}
            price: Current price
        
        Returns:
            BytesIO object containing PNG image
        """
        try:
            fig, ax = plt.subplots(figsize=(self.width, 6), dpi=self.dpi)
            
            timeframes = list(timeframe_data.keys())
            n_tf = len(timeframes)
            
            if n_tf == 0:
                plt.close(fig)
                return None
            
            # Prepare data
            rsi_values = [timeframe_data[tf]['rsi'] for tf in timeframes]
            mfi_values = [timeframe_data[tf]['mfi'] for tf in timeframes]
            signals = [timeframe_data[tf]['signal'] for tf in timeframes]
            
            # X positions
            x = range(n_tf)
            width = 0.35
            
            # Create bars
            bars1 = ax.bar([i - width/2 for i in x], rsi_values, width, 
                          label='RSI', color='#2962FF', alpha=0.8)
            bars2 = ax.bar([i + width/2 for i in x], mfi_values, width, 
                          label='MFI', color='#FF6D00', alpha=0.8)
            
            # Add signal indicators
            for i, signal in enumerate(signals):
                if signal == 1:  # BUY
                    ax.plot(i, 15, marker='^', markersize=15, color='green')
                elif signal == -1:  # SELL
                    ax.plot(i, 85, marker='v', markersize=15, color='red')
            
            # Reference lines
            ax.axhline(y=80, color='red', linestyle='--', alpha=0.5, label='Overbought (80)')
            ax.axhline(y=50, color='gray', linestyle=':', alpha=0.5)
            ax.axhline(y=20, color='green', linestyle='--', alpha=0.5, label='Oversold (20)')
            
            # Labels and title
            ax.set_ylabel('Value', fontsize=12)
            ax.set_title(f'{symbol} - Multi-Timeframe Analysis\n{datetime.now().strftime("%Y-%m-%d %H:%M")}', 
                        fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels([tf.upper() for tf in timeframes])
            ax.legend()
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3, axis='y')
            
            # Add price if available
            if price:
                ax.text(0.02, 0.98, f'Price: ${price:,.4f}', 
                       transform=ax.transAxes, fontsize=10,
                       verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            # Save to BytesIO
            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)
            
            logger.info(f"Multi-timeframe chart created for {symbol}")
            return buf
            
        except Exception as e:
            logger.error(f"Error creating multi-timeframe chart: {e}")
            return None
