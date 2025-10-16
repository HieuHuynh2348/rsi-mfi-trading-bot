"""
Watchlist Monitor
Monitors watchlist coins and sends automatic notifications when signals are detected
"""

import logging
import time
import json
import os
from datetime import datetime
from threading import Thread

logger = logging.getLogger(__name__)


class WatchlistMonitor:
    def __init__(self, command_handler, check_interval=300):
        """
        Initialize watchlist monitor
        
        Args:
            command_handler: TelegramCommandHandler instance
            check_interval: Check interval in seconds (default: 300 = 5 minutes)
        """
        self.command_handler = command_handler
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        self.last_signals = {}  # Track last signals to avoid duplicates
        self.signal_history_file = 'watchlist_signals_history.json'
        
        # Load signal history
        self.load_history()
        
        logger.info(f"Watchlist monitor initialized (interval: {check_interval}s)")
    
    def load_history(self):
        """Load signal history from file"""
        if os.path.exists(self.signal_history_file):
            try:
                with open(self.signal_history_file, 'r') as f:
                    self.last_signals = json.load(f)
                logger.info(f"Loaded signal history: {len(self.last_signals)} symbols")
            except Exception as e:
                logger.error(f"Error loading signal history: {e}")
                self.last_signals = {}
        else:
            self.last_signals = {}
    
    def save_history(self):
        """Save signal history to file"""
        try:
            with open(self.signal_history_file, 'w') as f:
                json.dump(self.last_signals, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving signal history: {e}")
    
    def start(self):
        """Start monitoring watchlist"""
        if self.running:
            logger.warning("Watchlist monitor already running")
            return
        
        self.running = True
        self.thread = Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info("Watchlist monitor started")
    
    def stop(self):
        """Stop monitoring watchlist"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Watchlist monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self.check_watchlist()
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            
            # Sleep in small intervals to allow quick shutdown
            for _ in range(self.check_interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def check_watchlist(self):
        """Check watchlist for new signals"""
        try:
            symbols = self.command_handler.watchlist.get_all()
            
            if not symbols:
                logger.debug("Watchlist is empty, skipping check")
                return
            
            logger.info(f"Checking {len(symbols)} watchlist symbols for signals...")
            
            new_signals = []
            
            for symbol in symbols:
                try:
                    # Analyze symbol
                    result = self.command_handler._analyze_symbol_full(symbol)
                    
                    if not result:
                        continue
                    
                    # Check if this is a NEW signal
                    if result['has_signal']:
                        signal_key = f"{symbol}_{result['consensus']}"
                        last_signal_time = self.last_signals.get(signal_key, 0)
                        current_time = time.time()
                        
                        # Only notify if signal is new (or older than 24 hours)
                        if current_time - last_signal_time > 86400:  # 24 hours
                            new_signals.append(result)
                            self.last_signals[signal_key] = current_time
                            logger.info(f"NEW signal detected: {symbol} - {result['consensus']}")
                    
                except Exception as e:
                    logger.error(f"Error analyzing {symbol}: {e}")
                    continue
                
                # Small delay
                time.sleep(0.1)
            
            # Save updated history
            if new_signals:
                self.save_history()
            
            # Send notifications for new signals
            if new_signals:
                self._send_signal_notifications(new_signals)
            else:
                logger.info("No new signals detected in watchlist")
        
        except Exception as e:
            logger.error(f"Error checking watchlist: {e}")
    
    def _send_signal_notifications(self, signals):
        """Send notifications for new signals"""
        try:
            # Send summary
            summary = f"🔔 <b>WATCHLIST ALERT!</b>\n\n"
            summary += f"🎯 {len(signals)} New Signal(s) Detected!\n"
            summary += f"🕐 {datetime.now().strftime('%H:%M:%S')}\n\n"
            
            for sig in signals:
                icon = "🚀" if sig['consensus'] == "BUY" else "⚠️"
                strength_bar = ("🟩" if sig['consensus'] == "BUY" else "🟥") * sig['consensus_strength']
                summary += f"{icon} <b>{sig['symbol']}</b> - {sig['consensus']}\n"
                summary += f"   {strength_bar} {sig['consensus_strength']}/4\n"
            
            summary += f"\n💡 Sending detailed analysis..."
            
            self.command_handler.bot.send_message(summary)
            
            # Send detailed analysis for each signal
            for i, result in enumerate(signals, 1):
                try:
                    # Send text alert
                    self.command_handler.bot.send_signal_alert(
                        result['symbol'],
                        result['timeframe_data'],
                        result['consensus'],
                        result['consensus_strength'],
                        result['price'],
                        result.get('market_data')
                    )
                    
                    # Send chart if enabled
                    if self.command_handler._config.SEND_CHARTS:
                        chart_buf = self.command_handler.chart_gen.create_multi_timeframe_chart(
                            result['symbol'],
                            result['timeframe_data'],
                            result['price'],
                            result.get('klines_dict')
                        )
                        
                        if chart_buf:
                            self.command_handler.bot.send_photo(
                                chart_buf,
                                caption=f"🎯 SIGNAL - {result['symbol']} ({i}/{len(signals)})"
                            )
                    
                    time.sleep(1)  # Delay between messages
                    
                except Exception as e:
                    logger.error(f"Error sending notification for {result['symbol']}: {e}")
                    continue
            
            # Final summary
            self.command_handler.bot.send_message(
                f"✅ <b>All {len(signals)} watchlist alerts sent!</b>\n\n"
                f"⏰ Next check in {self.check_interval//60} minutes"
            )
            
        except Exception as e:
            logger.error(f"Error sending signal notifications: {e}")
