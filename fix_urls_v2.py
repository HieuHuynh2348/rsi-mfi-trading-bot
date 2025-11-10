#!/usr/bin/env python3
"""
Fix WebApp URLs in telegram_commands.py
Add /webapp/chart.html path and cache buster
"""

# Read file
with open('telegram_commands.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Process line by line
output = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this is the buggy URL line
    if 'chart_webapp_url = f"{webapp_url}?symbol=' in line:
        # Get indentation
        indent = len(line) - len(line.lstrip())
        spaces = ' ' * indent
        
        # Insert cache buster line before
        output.append(f'{spaces}cache_buster = int(time.time())\n')
        
        # Fix the URL line
        fixed_line = line.replace(
            'chart_webapp_url = f"{webapp_url}?symbol=',
            'chart_webapp_url = f"{webapp_url}/webapp/chart.html?symbol='
        )
        # Add cache buster to end (before closing quote)
        if '&timeframe=1h"' in fixed_line:
            fixed_line = fixed_line.replace('&timeframe=1h"', '&timeframe=1h&_t={cache_buster}"')
        elif '&timeframe={timeframe}"' in fixed_line:
            fixed_line = fixed_line.replace('&timeframe={timeframe}"', '&timeframe={timeframe}&_t={cache_buster}"')
        
        output.append(fixed_line)
        
        # Add logging line after
        output.append(f'{spaces}logger.info(f"🔗 [commands] WebApp URL: {{chart_webapp_url}}")\n')
        
        print(f"✅ Fixed line {i+1}: {line.strip()[:60]}...")
    else:
        output.append(line)
    
    i += 1

# Write back
with open('telegram_commands.py', 'w', encoding='utf-8') as f:
    f.writelines(output)

print(f"\n✅ Completed! Check telegram_commands.py")
