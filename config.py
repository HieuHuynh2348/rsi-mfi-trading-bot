# Configuration file for Binance + Telegram Bot

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# API KEYS - Loaded from .env file
# ============================================================================
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# WebApp URL for live charts - HOSTED ON RAILWAY
# Railway serves both bot and webapp on same domain - use different routes
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://rsi-mfi-trading-bot-production.up.railway.app/webapp/chart.html")

# ============================================================================
# TRADING PARAMETERS
# ============================================================================
# RSI Settings
RSI_PERIOD = 6
RSI_LOWER = 20
RSI_UPPER = 80

# MFI Settings
MFI_PERIOD = 6
MFI_LOWER = 20
MFI_UPPER = 80

# Timeframes to analyze (in minutes)
# 5m, 1h, 4h, 1d
TIMEFRAMES = ['5m', '1h', '4h', '1d']

# ============================================================================
# BINANCE SETTINGS
# ============================================================================
# Symbols to exclude (coins with these keywords)
EXCLUDED_KEYWORDS = ['BEAR', 'BULL', 'UP', 'DOWN']

# Quote asset (what you're trading against)
QUOTE_ASSET = 'USDT'

# Minimum 24h volume (in USDT) to consider a coin
# Set to 0 to analyze ALL coins (no volume filter)
MIN_VOLUME_USDT = 0  # Analyze all coins regardless of volume

# ============================================================================
# BOT SETTINGS
# ============================================================================
# Owner user (no restrictions applied)
OWNER_USER_ID = 6228875204  # @Hieuhuynh234
OWNER_USERNAME = "Hieuhuynh234"

# Group chat ID (no Live Chart button, only indicators)
GROUP_CHAT_ID = -1002395637657  # Group chat - indicators only, no buttons

# How often to scan (in seconds)
SCAN_INTERVAL = 300  # 5 minutes

# Minimum consensus strength to send alert (1-4)
MIN_CONSENSUS_STRENGTH = 1

# Enable/disable features
SEND_CHARTS = True
SEND_SUMMARY_ONLY = False  # If True, only sends summary table, not individual signals
SEND_CONTINUOUS_UPDATES = True  # Send updates for ALL coins that meet criteria (not just new signals)

# Maximum coins to report at once
MAX_COINS_PER_MESSAGE = 10

# Auto-add coins to watchlist when signal found
AUTO_WATCHLIST = False  # If True, automatically track coins with strong signals

# Fast scan settings (parallel processing)
USE_FAST_SCAN = True  # Enable parallel processing for faster scans
MAX_SCAN_WORKERS = 0  # Number of concurrent threads (0 = auto-scale based on symbols, max 20)

# ============================================================================
# CHART SETTINGS
# ============================================================================
CHART_STYLE = 'default'  # 'default', 'dark', 'light'
CHART_DPI = 100
CHART_WIDTH = 12
CHART_HEIGHT = 6
