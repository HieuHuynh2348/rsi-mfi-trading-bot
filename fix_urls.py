#!/usr/bin/env python3
"""
Fix WebApp URLs in telegram_commands.py
"""

import re

# Read file
with open('telegram_commands.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find and replace
# Find: chart_webapp_url = f"{webapp_url}?symbol={symbol}&timeframe=1h"
# Replace with correct path

pattern = r'chart_webapp_url = f"\{webapp_url\}\?symbol=\{symbol\}&timeframe=(.*?)"'

def replacement(match):
    timeframe = match.group(1)
    return f'''cache_buster = int(time.time())
                                chart_webapp_url = f"{{webapp_url}}/webapp/chart.html?symbol={{symbol}}&timeframe={timeframe}&_t={{cache_buster}}"
                                logger.info(f"🔗 [commands] WebApp URL: {{chart_webapp_url}}")'''

# Replace
new_content = re.sub(pattern, replacement, content)

# Check if anything changed
if new_content != content:
    with open('telegram_commands.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ Fixed WebApp URLs in telegram_commands.py")
    print(f"   Changes: {content.count('chart_webapp_url = f') - new_content.count('chart_webapp_url = f')}")
else:
    print("⚠️  No changes needed")
