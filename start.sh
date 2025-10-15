#!/bin/bash
# Railway startup script for RSI+MFI Trading Bot

echo "🔍 Checking Python installation..."
which python || which python3 || echo "❌ Python not found!"

echo "🐍 Python version:"
python --version 2>/dev/null || python3 --version 2>/dev/null || echo "❌ Cannot get version"

echo "📦 Installing dependencies..."
python -m pip install -r requirements.txt 2>/dev/null || python3 -m pip install -r requirements.txt || echo "❌ Pip install failed"

echo "🚀 Starting Trading Bot..."
python -u main.py 2>/dev/null || python3 -u main.py || echo "❌ Bot failed to start"
