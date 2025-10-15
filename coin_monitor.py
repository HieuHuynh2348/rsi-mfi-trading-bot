"""
Continuous Monitor Module
Sends periodic updates for tracked coins
"""

import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

WATCHLIST_FILE = "watchlist.json"


class CoinMonitor:
    def __init__(self):
        """Initialize coin monitor"""
        self.watchlist = self.load_watchlist()
    
    def load_watchlist(self):
        """Load watchlist from file"""
        if os.path.exists(WATCHLIST_FILE):
            try:
                with open(WATCHLIST_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading watchlist: {e}")
                return {}
        return {}
    
    def save_watchlist(self):
        """Save watchlist to file"""
        try:
            with open(WATCHLIST_FILE, 'w') as f:
                json.dump(self.watchlist, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving watchlist: {e}")
    
    def add_to_watchlist(self, symbol, reason=""):
        """Add a coin to watchlist"""
        self.watchlist[symbol] = {
            'added_at': datetime.now().isoformat(),
            'reason': reason,
            'last_update': None
        }
        self.save_watchlist()
        logger.info(f"Added {symbol} to watchlist")
    
    def remove_from_watchlist(self, symbol):
        """Remove a coin from watchlist"""
        if symbol in self.watchlist:
            del self.watchlist[symbol]
            self.save_watchlist()
            logger.info(f"Removed {symbol} from watchlist")
    
    def update_last_scan(self, symbol):
        """Update last scan time for a coin"""
        if symbol in self.watchlist:
            self.watchlist[symbol]['last_update'] = datetime.now().isoformat()
            self.save_watchlist()
    
    def get_watchlist(self):
        """Get current watchlist"""
        return list(self.watchlist.keys())
    
    def should_send_update(self, symbol):
        """
        Check if we should send update for this coin
        Returns True if coin is in watchlist
        """
        return symbol in self.watchlist
