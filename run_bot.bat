@echo off
REM RSI+MFI Trading Bot Launcher
REM This script activates the virtual environment and runs the bot

echo ========================================
echo   RSI+MFI Trading Bot
echo ========================================
echo.

REM Change to bot directory
cd /d "H:\BOT UPGRADE"

echo [1/3] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [2/3] Starting trading bot...
echo.

REM Run the bot
python main.py

echo.
echo ========================================
echo   Bot stopped
echo ========================================
pause
