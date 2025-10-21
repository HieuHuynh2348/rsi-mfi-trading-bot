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
from volume_detector import VolumeDetector

logger = logging.getLogger(__name__)


class WatchlistMonitor:
    def __init__(self, command_handler, check_interval=300, volume_check_interval=60):
        """
        Initialize watchlist monitor
        
        Args:
            command_handler: TelegramCommandHandler instance
            check_interval: Check interval in seconds (default: 300 = 5 minutes)
            volume_check_interval: Volume check interval in seconds (default: 60 = 1 minute)
        """
        self.command_handler = command_handler
        self.check_interval = check_interval
        self.volume_check_interval = volume_check_interval
        self.running = False
        self.thread = None
        self.volume_thread = None
        self.last_signals = {}  # Track last signals to avoid duplicates
        self.last_volume_alerts = {}  # Track volume alerts
        self.signal_history_file = 'watchlist_signals_history.json'
        self.volume_history_file = 'watchlist_volume_history.json'
        
        # Initialize volume detector
        self.volume_detector = VolumeDetector(
            command_handler.binance,
            sensitivity='medium'
        )
        
        # Load signal history
        self.load_history()
        
        logger.info(f"Watchlist monitor initialized (signal: {check_interval}s, volume: {volume_check_interval}s)")
    
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
        
        # Load volume history
        if os.path.exists(self.volume_history_file):
            try:
                with open(self.volume_history_file, 'r') as f:
                    self.last_volume_alerts = json.load(f)
                logger.info(f"Loaded volume history: {len(self.last_volume_alerts)} alerts")
            except Exception as e:
                logger.error(f"Error loading volume history: {e}")
                self.last_volume_alerts = {}
        else:
            self.last_volume_alerts = {}
    
    def save_history(self):
        """Save signal history to file"""
        try:
            with open(self.signal_history_file, 'w') as f:
                json.dump(self.last_signals, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving signal history: {e}")
        
        # Save volume history
        try:
            with open(self.volume_history_file, 'w') as f:
                json.dump(self.last_volume_alerts, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving volume history: {e}")
    
    def start(self):
        """Start monitoring watchlist"""
        if self.running:
            logger.warning("Watchlist monitor already running")
            return
        
        self.running = True
        
        # Start signal monitoring thread
        self.thread = Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
        # Start volume monitoring thread
        self.volume_thread = Thread(target=self._volume_monitor_loop, daemon=True)
        self.volume_thread.start()
        
        logger.info("Watchlist monitor started (signals + volume)")
    
    def stop(self):
        """Stop monitoring watchlist"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        if self.volume_thread:
            self.volume_thread.join(timeout=5)
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
                    logger.info(f"📤 Sending detailed analysis {i}/{len(signals)} for {result['symbol']}")
                    # Send text alert
                    self.command_handler.bot.send_signal_alert(
                        result['symbol'],
                        result['timeframe_data'],
                        result['consensus'],
                        result['consensus_strength'],
                        result['price'],
                        result.get('market_data'),
                        result.get('volume_data')
                    )
                    logger.info(f"✅ Successfully sent alert for {result['symbol']}")
                    
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
                    logger.error(f"❌ Error sending notification for {result['symbol']}: {e}")
                    logger.exception(e)  # Full traceback
                    continue
            
            # Final summary
            self.command_handler.bot.send_message(
                f"✅ <b>All {len(signals)} watchlist alerts sent!</b>\n\n"
                f"⏰ Next check in {self.check_interval//60} minutes"
            )
            
        except Exception as e:
            logger.error(f"Error sending signal notifications: {e}")
    
    def _volume_monitor_loop(self):
        """Volume monitoring loop (runs more frequently)"""
        while self.running:
            try:
                self.check_watchlist_volumes()
            except Exception as e:
                logger.error(f"Error in volume monitor loop: {e}")
            
            # Sleep in small intervals to allow quick shutdown
            for _ in range(self.volume_check_interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def check_watchlist_volumes(self):
        """Check watchlist for volume anomalies"""
        try:
            symbols = self.command_handler.watchlist.get_all()
            
            if not symbols:
                logger.debug("Watchlist is empty, skipping volume check")
                return
            
            logger.info(f"Checking volumes for {len(symbols)} watchlist symbols...")
            
            # Scan for volume spikes
            spike_alerts = self.volume_detector.scan_watchlist_volumes(
                symbols,
                timeframes=['5m', '1h']
            )
            
            if not spike_alerts:
                logger.info("No volume spikes detected")
                return
            
            # Filter out recently alerted spikes (avoid spam)
            new_alerts = []
            current_time = time.time()
            
            for alert in spike_alerts:
                symbol = alert['symbol']
                alert_key = f"{symbol}_volume"
                last_alert_time = self.last_volume_alerts.get(alert_key, 0)
                
                # Only alert if it's been more than 1 hour since last alert
                if current_time - last_alert_time > 3600:
                    new_alerts.append(alert)
                    self.last_volume_alerts[alert_key] = current_time
            
            if not new_alerts:
                logger.info("All volume spikes were recently alerted, skipping")
                return
            
            # Save updated history
            self.save_history()
            
            # Send notifications
            self._send_volume_notifications(new_alerts)
            
        except Exception as e:
            logger.error(f"Error checking watchlist volumes: {e}")
    
    def _send_volume_notifications(self, spike_alerts):
        """Send volume spike notifications"""
        try:
            # Send summary
            summary = self.volume_detector.get_watchlist_spike_summary(spike_alerts)
            self.command_handler.bot.send_message(summary)
            
            time.sleep(2)
            
            # Send detailed analysis for each spike
            for i, alert in enumerate(spike_alerts, 1):
                try:
                    symbol = alert['symbol']
                    
                    # Get full analysis for the symbol
                    result = self.command_handler._analyze_symbol_full(symbol)
                    
                    if not result:
                        continue
                    
                    # Add volume info to message
                    vol_header = f"<b>🔥 VOLUME SPIKE DETECTED!</b>\n\n"
                    
                    # Get volume details from the strongest timeframe
                    strongest_tf = None
                    max_ratio = 0
                    for tf, tf_result in alert['timeframe_results'].items():
                        if tf_result['is_spike'] and tf_result['volume_ratio'] > max_ratio:
                            max_ratio = tf_result['volume_ratio']
                            strongest_tf = tf
                    
                    if strongest_tf:
                        tf_data = alert['timeframe_results'][strongest_tf]
                        vol_text = self.volume_detector.get_volume_analysis_text(tf_data)
                        vol_header += vol_text + "\n\n"
                    
                    # Send volume analysis first
                    self.command_handler.bot.send_message(vol_header)
                    time.sleep(1)
                    
                    # Send full technical analysis
                    self.command_handler.bot.send_signal_alert(
                        result['symbol'],
                        result['timeframe_data'],
                        result['consensus'],
                        result['consensus_strength'],
                        result['price'],
                        result.get('market_data'),
                        result.get('volume_data')
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
                                caption=f"📊 {result['symbol']} - Volume Spike Analysis ({i}/{len(spike_alerts)})"
                            )
                    
                    time.sleep(2)  # Delay between alerts
                    
                except Exception as e:
                    logger.error(f"Error sending volume notification for {alert['symbol']}: {e}")
                    continue
            
            # Final summary
            self.command_handler.bot.send_message(
                f"✅ <b>All {len(spike_alerts)} volume alerts sent!</b>\n\n"
                f"⏰ Next volume check in {self.volume_check_interval//60} minute(s)"
            )
            
        except Exception as e:
            logger.error(f"Error sending volume notifications: {e}")
