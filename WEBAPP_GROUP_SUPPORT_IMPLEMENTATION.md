# WebApp Group Support Implementation

## Problem Solved

**Issue:** `BUTTON_TYPE_INVALID` error when using WebApp buttons in Telegram groups.

**Root Cause:** Telegram API limitation - WebApp buttons (`web_app` parameter in `InlineKeyboardButton`) only work in **private chats**, not in groups or supergroups.

**Official Documentation:**
> "Available only in private chats between a user and the bot"

## Solution Overview

Implemented **Direct Link Approach** that:
1. Shows regular URL button in groups (not WebApp button)
2. Redirects users to private chat with bot via `t.me` link
3. Tracks user ID and group ID for admin notifications
4. Opens WebApp in private chat (where it works)

## Implementation Details

### 1. Modified Keyboard Methods (telegram_bot.py)

#### `create_ai_analysis_keyboard(symbol, user_id, chat_id, chat_type)`

**Behavior:**
- **In Private Chat:** Shows WebApp button (opens chart IN Telegram)
- **In Groups:** Shows URL button that opens bot in private chat

**Code:**
```python
def create_ai_analysis_keyboard(self, symbol, user_id=None, chat_id=None, chat_type='private'):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Row 1: AI and Chart buttons
    keyboard.row(
        types.InlineKeyboardButton(f"🤖 AI Phân Tích", callback_data=f"ai_analyze_{symbol}"),
        types.InlineKeyboardButton(f"📊 Chart", callback_data=f"chart_{symbol}")
    )
    
    # Row 2: Live Chart - Different behavior based on chat type
    webapp_url = self._get_webapp_url()
    if webapp_url:
        if chat_type == 'private':
            # In private: Use WebApp (opens IN Telegram)
            chart_webapp_url = f"{webapp_url}?symbol={symbol}&timeframe=1h"
            keyboard.row(
                types.InlineKeyboardButton(
                    "📊 Live Chart (in Telegram)", 
                    web_app=types.WebAppInfo(url=chart_webapp_url)
                )
            )
        else:
            # In groups: Use t.me link to open private chat
            bot_username = self._get_bot_username()
            if bot_username:
                start_param = f"chart_{symbol}_{user_id}_{chat_id}"
                bot_link = f"https://t.me/{bot_username}?start={start_param}"
                keyboard.row(
                    types.InlineKeyboardButton(
                        "📊 Open Live Chart in Bot", 
                        url=bot_link
                    )
                )
                # Log access attempt
                logger.info(f"📊 Chart from group - User: {user_id}, Chat: {chat_id}, Symbol: {symbol}")
    
    return keyboard
```

#### `create_symbol_analysis_keyboard(symbol, user_id, chat_id, chat_type)`

Same pattern as `create_ai_analysis_keyboard`.

### 2. Added Bot Username Method (telegram_bot.py)

```python
def _get_bot_username(self):
    """Get bot username (cached)"""
    if not hasattr(self, '_bot_username'):
        try:
            bot_info = self.bot.get_me()
            self._bot_username = bot_info.username
            logger.info(f"✅ Bot username: @{self._bot_username}")
        except Exception as e:
            logger.error(f"❌ Error getting bot username: {e}")
            self._bot_username = None
    return self._bot_username
```

### 3. Enhanced /start Handler (telegram_commands.py)

**Functionality:**
1. Detects chart deep link: `/start chart_SYMBOL_USERID_CHATID`
2. Parses parameters (symbol, user_id, source_chat_id)
3. Sends notification to admin with user/group IDs
4. Opens WebApp in private chat

**Code:**
```python
@self.telegram_bot.message_handler(commands=['start', 'help'])
def handle_help(message):
    if not check_authorized(message):
        return
    
    # Check for chart deep link
    if message.text and message.text.startswith('/start chart_'):
        try:
            params = message.text[14:].split('_')  # Skip "/start chart_"
            
            symbol = params[0]
            source_user_id = params[1] if len(params) >= 2 else None
            source_chat_id = params[2] if len(params) >= 3 else None
            
            # Log access
            logger.info(f"📊 Chart access: {symbol}, User={source_user_id}, Chat={source_chat_id}")
            
            # Notify admin with IDs
            admin_message = f"""
🔔 <b>Live Chart Access Request</b>

👤 <b>User ID:</b> <code>{source_user_id}</code>
💬 <b>Chat ID:</b> <code>{source_chat_id}</code>
📊 <b>Symbol:</b> {symbol}
🕒 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<i>User clicked chart button in group and opened bot in private chat.</i>
"""
            self.bot.send_message(admin_message, parse_mode='HTML')
            
            # Get WebApp URL
            webapp_url = self.bot._get_webapp_url()
            if webapp_url:
                # Create WebApp button (works in private!)
                chart_webapp_url = f"{webapp_url}?symbol={symbol}&timeframe=1h"
                keyboard = types.InlineKeyboardMarkup()
                keyboard.row(
                    types.InlineKeyboardButton(
                        f"📊 View {symbol} Live Chart",
                        web_app=types.WebAppInfo(url=chart_webapp_url)
                    )
                )
                
                self.bot.send_message(
                    f"✅ <b>Welcome!</b>\n\n"
                    f"Click button below to view <b>{symbol}</b> live chart:\n\n"
                    f"<i>📱 Chart will open directly in Telegram</i>",
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
                return
        except Exception as e:
            logger.error(f"Error processing chart deep link: {e}")
    
    # Default help message
    from vietnamese_messages import HELP_MESSAGE
    keyboard = self.bot.create_main_menu_keyboard()
    self.bot.send_message(HELP_MESSAGE, reply_markup=keyboard)
```

### 4. Updated Command Handlers (telegram_commands.py)

Both `/analyzer` and symbol analysis handlers now pass chat context:

```python
# Get chat context
user_id = message.from_user.id if message.from_user else None
chat_id = message.chat.id
chat_type = message.chat.type  # 'private', 'group', 'supergroup'

# Create keyboard with context
keyboard = self.bot.create_ai_analysis_keyboard(
    symbol, 
    user_id=user_id, 
    chat_id=chat_id, 
    chat_type=chat_type
)
```

## User Flow

### Private Chat (Original Behavior - Still Works)
1. User sends `/BTC` command
2. Bot shows analysis with "📊 Live Chart (in Telegram)" button
3. User clicks → Chart opens IN Telegram
4. ✅ No page redirection

### Group Chat (New Behavior)
1. User sends `/BTC` command in group
2. Bot shows analysis with "📊 Open Live Chart in Bot" button
3. User clicks → Opens `https://t.me/botname?start=chart_BTC_123456_-9876543`
4. Bot starts in private chat with user
5. Admin receives notification:
   ```
   🔔 Live Chart Access Request
   
   👤 User ID: 123456
   💬 Chat ID: -9876543
   📊 Symbol: BTC
   🕒 Time: 2024-01-15 14:30:00
   ```
6. Bot shows "📊 View BTC Live Chart" button (WebApp)
7. User clicks → Chart opens IN Telegram (private chat)
8. ✅ Chart works perfectly

## Admin Notifications

Each chart access from group generates:
- User ID (for user tracking)
- Group/Chat ID (for analytics)
- Symbol requested
- Timestamp
- Context message

**Format:**
```
🔔 Live Chart Access Request

👤 User ID: <code>123456789</code>
💬 Chat ID: <code>-1001234567890</code>
📊 Symbol: BTCUSDT
🕒 Time: 2024-01-15 14:30:45

User clicked chart button in group and opened bot in private chat.
```

## Logging

Enhanced logging for tracking:

```python
logger.info(f"📊 Chart access from group - User ID: {user_id}, Chat ID: {chat_id}, Symbol: {symbol}")
logger.info(f"📊 Chart access request: Symbol={symbol}, From User={source_user_id}, From Chat={source_chat_id}")
```

## Files Modified

1. **telegram_bot.py**
   - Modified `create_ai_analysis_keyboard()`
   - Modified `create_symbol_analysis_keyboard()`
   - Added `_get_bot_username()`

2. **telegram_commands.py**
   - Enhanced `/start` handler with deep link processing
   - Updated `/analyzer` command to pass chat context
   - Updated symbol analysis handler to pass chat context

## Testing Checklist

### Private Chat Testing
- [ ] Send `/BTC` in private chat
- [ ] Verify "📊 Live Chart (in Telegram)" button appears
- [ ] Click button
- [ ] Chart opens IN Telegram (no redirect)
- [ ] Chart displays correctly
- [ ] Interactive features work (zoom, scroll, haptic feedback)

### Group Chat Testing
- [ ] Send `/BTC` in group chat
- [ ] Verify "📊 Open Live Chart in Bot" button appears
- [ ] Click button
- [ ] Bot opens in private chat
- [ ] Admin receives notification with:
  - [ ] User ID
  - [ ] Group ID
  - [ ] Symbol (BTC)
  - [ ] Timestamp
- [ ] "📊 View BTC Live Chart" button appears
- [ ] Click button
- [ ] Chart opens IN Telegram
- [ ] Chart displays correctly

### Edge Cases
- [ ] User not started bot before → First message shows help
- [ ] Invalid symbol parameter → Falls back to help
- [ ] Missing user_id/chat_id → Button still works (no IDs logged)
- [ ] WebApp URL not configured → No Live Chart button shown

## Configuration

### Required Environment Variables

```bash
# Railway automatically provides this
RAILWAY_PUBLIC_DOMAIN=your-app.up.railway.app

# Or manually set
WEBAPP_URL=https://your-app.up.railway.app

# Bot token (already configured)
TELEGRAM_BOT_TOKEN=your_bot_token
```

### No Changes Needed To
- `.env` file (already configured)
- `webapp/app.py` (Flask backend)
- `webapp/chart.html` (frontend)
- Railway configuration

## Benefits

✅ **Works in All Chat Types:** Private, groups, supergroups
✅ **User Tracking:** Admin sees who accesses charts from which group
✅ **No Breaking Changes:** Private chat behavior unchanged
✅ **Seamless UX:** One click from group → opens in bot
✅ **Compliant:** Follows Telegram API limitations correctly
✅ **Professional:** Clean notifications with formatted IDs

## Known Limitations

1. **Two-Step Process in Groups:**
   - User clicks button in group
   - Bot opens in private chat
   - User clicks again to open chart
   
2. **Requires Bot Start:**
   - Users must have started bot at least once
   - First-time users see help message first

3. **Platform Limitation:**
   - WebApp buttons will NEVER work in groups (Telegram API)
   - This is not a bug, it's by design

## Future Enhancements

Potential improvements:
- Store access logs in database for analytics
- Add rate limiting per user/group
- Generate usage statistics
- Add user preferences (default timeframe, etc.)
- Implement session tracking across group → private transition

## Troubleshooting

### Button Not Appearing
- Check `WEBAPP_URL` is set
- Verify bot username is accessible
- Check logs for errors

### Admin Not Receiving Notifications
- Verify `self.chat_id` is set correctly
- Check bot has permission to send messages
- Review logs for send errors

### WebApp Not Opening
- Ensure URL is HTTPS
- Verify Railway deployment is running
- Check webapp/app.py is serving correctly

## Commit Message

```
feat: Add group support for WebApp with user/group tracking

- Modified keyboard methods to detect chat type
- Direct Link approach for groups (WebApp only works in private)
- Enhanced /start handler to process chart deep links
- Admin notifications with user ID and group ID
- Logging for analytics and debugging
- Seamless transition from group to private chat
- Fixes BUTTON_TYPE_INVALID error

Files changed:
- telegram_bot.py: Modified keyboard methods, added _get_bot_username()
- telegram_commands.py: Enhanced /start handler, updated command handlers
```

## Related Documentation

- [TELEGRAM_WEBAPP_COMPLETE_GUIDE.md](./TELEGRAM_WEBAPP_COMPLETE_GUIDE.md) - Complete WebApp implementation guide
- [RAILWAY_SETUP.md](./RAILWAY_SETUP.md) - Railway deployment guide
- [RAILWAY_PUBLIC_URL_FIX.md](./RAILWAY_PUBLIC_URL_FIX.md) - URL configuration guide

## Support

For issues or questions:
1. Check logs for error messages
2. Verify environment variables
3. Test in private chat first (should always work)
4. Review Telegram API documentation
