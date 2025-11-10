#!/usr/bin/env python3
"""
Fix GitHub Pages URL in telegram_commands.py line 3266
Replace with Railway URL and add cache buster
"""

with open('telegram_commands.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the exact line
old_line = 'chart_webapp_url = f"https://hieuhhuynh2348.github.io/rsi-mfi-trading-bot/webapp/chart.html?symbol={symbol}&timeframe={timeframe}"'

if old_line in content:
    # Replacement with proper indentation (32 spaces based on context)
    replacement = '''webapp_url = self.bot._get_webapp_url()
                                if webapp_url:
                                    cache_buster = int(time.time())
                                    chart_webapp_url = f"{webapp_url}/webapp/chart.html?symbol={symbol}&timeframe={timeframe}&_t={cache_buster}"
                                    logger.info(f"🔗 [webapp_data_handler] WebApp URL: {chart_webapp_url}")
                                    keyboard = types.InlineKeyboardMarkup()
                                    keyboard.row(
                                        types.InlineKeyboardButton(
                                            text=f"📊 View {symbol} Chart",
                                            web_app=types.WebAppInfo(url=chart_webapp_url)
                                        )
                                    )
                                else:
                                    keyboard = None'''
    
    # Replace old keyboard creation block
    old_block = '''keyboard = types.InlineKeyboardMarkup()
                                chart_webapp_url = f"https://hieuhhuynh2348.github.io/rsi-mfi-trading-bot/webapp/chart.html?symbol={symbol}&timeframe={timeframe}"
                                keyboard.row(
                                    types.InlineKeyboardButton(
                                        text=f"📊 View {symbol} Chart",
                                        web_app=types.WebAppInfo(url=chart_webapp_url)
                                    )
                                )'''
    
    content = content.replace(old_block, replacement)
    
    with open('telegram_commands.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed GitHub Pages URL in telegram_commands.py")
    print("   Replaced with Railway URL + cache buster")
else:
    print("⚠️  Pattern not found - may already be fixed")
