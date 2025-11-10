#!/usr/bin/env python3
"""Fix indentation in telegram_commands.py"""

with open('telegram_commands.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 3281 - split comment to new line
for i, line in enumerate(lines):
    if 'self.bot.send_message(analysis_msg, reply_markup=keyboard)' in line and '# Also send result' in line:
        # Split into two lines
        indent = len(line) - len(line.lstrip())
        spaces = ' ' * indent
        
        lines[i] = f'{spaces}self.bot.send_message(analysis_msg, reply_markup=keyboard)\n'
        
        # Insert comment lines after
        lines.insert(i+1, f'{spaces}\n')
        lines.insert(i+2, f'{spaces}# Also send result back to WebApp using answerWebAppQuery\n')
        lines.insert(i+3, f'{spaces}# This will display in the webapp\'s AI Analysis tab\n')
        lines.insert(i+4, f'{spaces}try:\n')
        
        # Find and remove the old comment/try lines
        j = i + 5
        while j < len(lines) and '# This will display' in lines[j]:
            lines.pop(j)
        while j < len(lines) and 'try:' in lines[j] and lines[j].strip() == 'try:':
            lines.pop(j)
            break
        
        print(f"✅ Fixed indentation at line {i+1}")
        break

with open('telegram_commands.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Done!")
