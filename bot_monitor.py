"""
Bot Activity Monitor
Monitors watchlist for bot trading and pump bot patterns
"""

import logging
import time
import threading
from datetime import datetime

logger = logging.getLogger(__name__)


class BotMonitor:
    def __init__(self, command_handler, check_interval=1800, scan_mode='all'):
        """
        Initialize Bot Monitor
        
        Args:
            command_handler: TelegramCommandHandler instance
            check_interval: Check interval in seconds (default: 1800 = 30 minutes)
            scan_mode: 'watchlist' for watchlist only, 'all' for all top volume coins (default: 'all')
        """
        self.command_handler = command_handler
        self.binance = command_handler.binance
        self.bot = command_handler.bot
        self.bot_detector = command_handler.bot_detector
        self.watchlist = command_handler.watchlist
        self.check_interval = check_interval
        self.scan_mode = scan_mode  # 'watchlist' or 'all'
        
        # Monitor state
        self.running = False
        self.thread = None
        self.last_alerts = {}  # Track last alerts to avoid spam
        
        # Alert thresholds (more sensitive)
        self.bot_score_threshold = 40  # Alert if bot score >= 40%
        self.pump_score_threshold = 45  # Alert if pump score >= 45%
        self.alert_cooldown = 3600  # 1 hour cooldown per symbol
        
        logger.info(f"Bot monitor initialized (interval: {check_interval}s, mode: {scan_mode})")
    
    def start(self):
        """Start bot monitor"""
        if self.running:
            logger.warning("Bot monitor already running")
            return False
        
        # For 'all' mode, no need to check watchlist
        if self.scan_mode == 'watchlist' and self.watchlist.count() == 0:
            logger.warning("Cannot start bot monitor: watchlist is empty")
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
        logger.info("✅ Bot monitor started")
        return True
    
    def stop(self):
        """Stop bot monitor"""
        if not self.running:
            logger.warning("Bot monitor not running")
            return False
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("⛔ Bot monitor stopped")
        return True
    
    def _get_top_volume_coins(self, limit=50):
        """
        Get top coins by 24h volume from Binance
        
        Args:
            limit: Number of top coins to return (default: 50)
            
        Returns:
            List of trading symbols
        """
        try:
            logger.info(f"Fetching top {limit} coins by volume...")
            
            # Get all USDT pairs ticker
            tickers = self.binance.client.get_ticker()
            
            # Filter USDT pairs only
            usdt_pairs = [
                ticker for ticker in tickers 
                if ticker['symbol'].endswith('USDT')
                and not any(x in ticker['symbol'] for x in ['UP', 'DOWN', 'BULL', 'BEAR'])  # Exclude leveraged tokens
            ]
            
            # Sort by 24h quote volume (volume in USDT)
            sorted_pairs = sorted(
                usdt_pairs, 
                key=lambda x: float(x.get('quoteVolume', 0)), 
                reverse=True
            )
            
            # Get top N symbols
            top_symbols = [pair['symbol'] for pair in sorted_pairs[:limit]]
            
            logger.info(f"✅ Found {len(top_symbols)} top volume coins")
            return top_symbols
            
        except Exception as e:
            logger.error(f"Error getting top volume coins: {e}")
            return []
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        logger.info(f"Bot monitor loop started (mode: {self.scan_mode})")
        
        while self.running:
            try:
                # Get symbols based on scan mode
                if self.scan_mode == 'watchlist':
                    symbols = self.watchlist.get_all()
                    if not symbols:
                        logger.warning("Watchlist is empty, stopping monitor")
                        self.running = False
                        break
                else:  # 'all' mode
                    symbols = self._get_top_volume_coins(limit=50)
                    if not symbols:
                        logger.error("Failed to get top volume coins, retrying in 5 minutes...")
                        time.sleep(300)
                        continue
                
                logger.info(f"🔍 Checking {len(symbols)} symbols for bot activity (mode: {self.scan_mode})...")
                start_time = time.time()
                
                # Scan for bot activity
                detections = self._scan_bot_activity(symbols)
                
                scan_time = time.time() - start_time
                logger.info(f"✅ Bot scan completed in {scan_time:.1f}s - Found {len(detections)} alerts")
                
                # Send alerts
                if detections:
                    self._send_bot_alerts(detections)
                
                # Sleep until next check
                if self.running:
                    logger.info(f"💤 Sleeping for {self.check_interval}s until next bot check...")
                    time.sleep(self.check_interval)
                    
            except Exception as e:
                logger.error(f"Error in bot monitor loop: {e}")
                if self.running:
                    time.sleep(60)  # Sleep 1 minute on error
        
        logger.info("Bot monitor loop stopped")
    
    def _scan_bot_activity(self, symbols):
        """
        Scan symbols for bot activity and pump patterns
        
        Args:
            symbols: List of trading symbols
        
        Returns:
            List of detections requiring alerts
        """
        detections = []
        
        for symbol in symbols:
            try:
                # Ensure symbol has USDT suffix
                if not symbol.endswith('USDT'):
                    symbol = symbol + 'USDT'
                
                # Check cooldown
                current_time = time.time()
                last_alert_time = self.last_alerts.get(symbol, 0)
                
                if current_time - last_alert_time < self.alert_cooldown:
                    logger.debug(f"Skipping {symbol} - in cooldown period")
                    continue
                
                # Detect bot activity
                detection = self.bot_detector.detect_bot_activity(symbol)
                
                if not detection:
                    logger.debug(f"No detection data for {symbol}")
                    continue
                
                bot_score = detection.get('bot_score', 0)
                pump_score = detection.get('pump_score', 0)
                
                # Check if alert thresholds are met
                alert_bot = bot_score >= self.bot_score_threshold
                alert_pump = pump_score >= self.pump_score_threshold
                
                if alert_bot or alert_pump:
                    detection['alert_type'] = []
                    
                    if alert_pump:
                        detection['alert_type'].append('PUMP')
                        logger.warning(f"🚀 PUMP BOT detected: {symbol} (Score: {pump_score}%)")
                    
                    if alert_bot:
                        detection['alert_type'].append('BOT')
                        logger.info(f"🤖 Trading BOT detected: {symbol} (Score: {bot_score}%)")
                    
                    detections.append(detection)
                    self.last_alerts[symbol] = current_time
                else:
                    logger.debug(f"No alert for {symbol} - Bot: {bot_score}%, Pump: {pump_score}%")
                
                # Small delay between API calls
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
                continue
        
        return detections
    
    def _send_bot_alerts(self, detections):
        """
        Send alerts for bot detections
        
        Args:
            detections: List of detection results
        """
        try:
            # Send summary first
            summary = f"<b>🤖 BOT ACTIVITY ALERT</b>\n\n"
            summary += f"⚠️ Detected <b>{len(detections)}</b> symbols with bot activity:\n\n"
            
            pump_count = sum(1 for d in detections if 'PUMP' in d.get('alert_type', []))
            bot_count = sum(1 for d in detections if 'BOT' in d.get('alert_type', []))
            
            if pump_count > 0:
                summary += f"🚀 <b>PUMP BOTS:</b> {pump_count}\n"
            if bot_count > 0:
                summary += f"🤖 <b>Trading BOTS:</b> {bot_count}\n"
            
            summary += f"\n📤 Sending detailed analysis...\n"
            
            self.bot.send_message(summary)
            time.sleep(1)
            
            # Send detailed analysis for each detection
            for i, detection in enumerate(detections, 1):
                try:
                    symbol = detection['symbol']
                    alert_types = detection.get('alert_type', [])
                    
                    # Add alert header
                    alert_header = "⚠️ "
                    if 'PUMP' in alert_types:
                        alert_header += "🚀 <b>PUMP BOT ALERT!</b>\n"
                    if 'BOT' in alert_types:
                        alert_header += "🤖 <b>Trading BOT Alert</b>\n"
                    
                    alert_header += f"Symbol: {symbol} ({i}/{len(detections)})\n\n"
                    
                    # Get formatted analysis
                    analysis_msg = self.bot_detector.get_formatted_analysis(detection)
                    
                    # Combine header + analysis
                    full_msg = alert_header + analysis_msg
                    
                    self.bot.send_message(full_msg)
                    time.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error sending alert for {detection.get('symbol', 'UNKNOWN')}: {e}")
            
            logger.info(f"✅ Sent {len(detections)} bot activity alerts")
            
        except Exception as e:
            logger.error(f"Error sending bot alerts: {e}")
    
    def manual_scan(self):
        """
        Perform manual bot activity scan (for /botscan command)
        
        Returns:
            List of detections
        """
        try:
            # Get symbols based on scan mode
            if self.scan_mode == 'watchlist':
                symbols = self.watchlist.get_all()
                if not symbols:
                    return []
            else:  # 'all' mode
                symbols = self._get_top_volume_coins(limit=50)
                if not symbols:
                    return []
            
            logger.info(f"Manual bot scan for {len(symbols)} symbols (mode: {self.scan_mode})")
            detections = []
            
            for symbol in symbols:
                try:
                    if not symbol.endswith('USDT'):
                        symbol = symbol + 'USDT'
                    
                    detection = self.bot_detector.detect_bot_activity(symbol)
                    
                    if detection:
                        detections.append(detection)
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error in manual scan for {symbol}: {e}")
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in manual_scan: {e}")
            return []
    
    def get_status(self):
        """
        Get monitor status
        
        Returns:
            dict with status info
        """
        return {
            'running': self.running,
            'scan_mode': self.scan_mode,
            'check_interval': self.check_interval,
            'watchlist_count': self.watchlist.count(),
            'bot_threshold': self.bot_score_threshold,
            'pump_threshold': self.pump_score_threshold,
            'alert_cooldown': self.alert_cooldown,
            'tracked_symbols': len(self.last_alerts)
        }
    
    def set_thresholds(self, bot_threshold=None, pump_threshold=None):
        """
        Update alert thresholds
        
        Args:
            bot_threshold: Bot score threshold (0-100)
            pump_threshold: Pump score threshold (0-100)
        """
        if bot_threshold is not None:
            self.bot_score_threshold = max(0, min(100, bot_threshold))
            logger.info(f"Bot threshold updated to {self.bot_score_threshold}%")
        
        if pump_threshold is not None:
            self.pump_score_threshold = max(0, min(100, pump_threshold))
            logger.info(f"Pump threshold updated to {self.pump_score_threshold}%")
