"""
Price Tracker - Auto-track TP/SL after AI analysis
No Telegram notifications - just save results to DB
"""

import asyncio
import websockets
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from database import get_db

class PriceTracker:
    def __init__(self):
        self.active_tracks = {}  # {analysis_id: track_data}
        self.ws_connections = {}  # {symbol: websocket}
        self.db = get_db()
    
    def start_tracking(
        self,
        analysis_id: str,
        symbol: str,
        ai_response: Dict,
        entry_price: float
    ):
        """
        Start tracking TP/SL for new analysis
        
        Args:
            analysis_id: Analysis ID from database
            symbol: Trading symbol
            ai_response: AI full response with entry/TP/SL
            entry_price: Actual entry price (current market price)
        """
        recommendation = ai_response.get('recommendation', {})
        
        # Extract TP/SL from AI response
        stop_loss = recommendation.get('stop_loss')
        take_profits = recommendation.get('take_profit', [])
        action = recommendation.get('recommendation', 'BUY')
        
        if not stop_loss or not take_profits:
            print(f"⚠️ No TP/SL in analysis {analysis_id}, skipping tracking")
            return
        
        # Calculate tracking duration (7 days max)
        start_time = datetime.now()
        end_time = start_time + timedelta(days=7)
        
        track_data = {
            'analysis_id': analysis_id,
            'symbol': symbol,
            'action': action,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profits': take_profits,
            'start_time': start_time,
            'end_time': end_time,
            
            # Tracking state
            'highest_price': entry_price,
            'lowest_price': entry_price,
            'tp_hits': [False] * len(take_profits),
            'sl_hit': False,
            'completed': False,
            'result': None,
            'exit_price': None,
            'exit_reason': None
        }
        
        self.active_tracks[analysis_id] = track_data
        
        # Start WebSocket for this symbol if not already running
        if symbol not in self.ws_connections:
            asyncio.create_task(self._monitor_symbol(symbol))
        
        print(f"📊 Started tracking {analysis_id}: {symbol} @ ${entry_price}")
    
    async def _monitor_symbol(self, symbol: str):
        """
        Monitor symbol price via Binance WebSocket
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
        """
        ws_url = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@kline_1m"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                self.ws_connections[symbol] = websocket
                print(f"🔌 Connected to {symbol} price stream")
                
                async for message in websocket:
                    data = json.loads(message)
                    
                    if data.get('e') == 'kline':
                        kline = data['k']
                        close_price = float(kline['c'])
                        is_closed = kline['x']  # Candle closed?
                        
                        # Only check on candle close (more reliable)
                        if is_closed:
                            await self._check_all_tracks(symbol, close_price)
                
        except Exception as e:
            print(f"❌ WebSocket error for {symbol}: {e}")
        finally:
            if symbol in self.ws_connections:
                del self.ws_connections[symbol]
    
    async def _check_all_tracks(self, symbol: str, current_price: float):
        """
        Check all active tracks for this symbol
        
        Args:
            symbol: Trading symbol
            current_price: Current market price (candle close)
        """
        # Find all tracks for this symbol
        symbol_tracks = [
            (aid, track) for aid, track in self.active_tracks.items()
            if track['symbol'] == symbol and not track['completed']
        ]
        
        for analysis_id, track in symbol_tracks:
            # Update price range
            track['highest_price'] = max(track['highest_price'], current_price)
            track['lowest_price'] = min(track['lowest_price'], current_price)
            
            # Check if expired (7 days)
            if datetime.now() > track['end_time']:
                await self._complete_tracking(
                    analysis_id,
                    current_price,
                    'EXPIRED',
                    'TIME_EXPIRED'
                )
                continue
            
            # Check TP/SL based on action
            if track['action'] == 'BUY':
                await self._check_buy_position(analysis_id, track, current_price)
            elif track['action'] == 'SELL':
                await self._check_sell_position(analysis_id, track, current_price)
    
    async def _check_buy_position(
        self,
        analysis_id: str,
        track: Dict,
        current_price: float
    ):
        """Check TP/SL for BUY position"""
        
        # Check Stop Loss (price went DOWN)
        if current_price <= track['stop_loss'] and not track['sl_hit']:
            track['sl_hit'] = True
            await self._complete_tracking(
                analysis_id,
                current_price,
                'LOSS',
                'SL_HIT'
            )
            return
        
        # Check Take Profits (price went UP)
        for i, tp in enumerate(track['take_profits']):
            if current_price >= tp and not track['tp_hits'][i]:
                track['tp_hits'][i] = True
                
                # If TP3 hit, complete immediately
                if i == len(track['take_profits']) - 1:
                    await self._complete_tracking(
                        analysis_id,
                        current_price,
                        'WIN',
                        f'TP{i+1}_HIT'
                    )
                    return
                
                print(f"✅ {analysis_id}: TP{i+1} hit @ ${current_price}")
    
    async def _check_sell_position(
        self,
        analysis_id: str,
        track: Dict,
        current_price: float
    ):
        """Check TP/SL for SELL position"""
        
        # Check Stop Loss (price went UP)
        if current_price >= track['stop_loss'] and not track['sl_hit']:
            track['sl_hit'] = True
            await self._complete_tracking(
                analysis_id,
                current_price,
                'LOSS',
                'SL_HIT'
            )
            return
        
        # Check Take Profits (price went DOWN)
        for i, tp in enumerate(track['take_profits']):
            if current_price <= tp and not track['tp_hits'][i]:
                track['tp_hits'][i] = True
                
                # If TP3 hit, complete immediately
                if i == len(track['take_profits']) - 1:
                    await self._complete_tracking(
                        analysis_id,
                        current_price,
                        'WIN',
                        f'TP{i+1}_HIT'
                    )
                    return
                
                print(f"✅ {analysis_id}: TP{i+1} hit @ ${current_price}")
    
    async def _complete_tracking(
        self,
        analysis_id: str,
        exit_price: float,
        result: str,
        exit_reason: str
    ):
        """
        Complete tracking and save result to database
        
        Args:
            analysis_id: Analysis ID
            exit_price: Final exit price
            result: WIN/LOSS/EXPIRED
            exit_reason: TP1/TP2/TP3/SL_HIT/TIME_EXPIRED
        """
        track = self.active_tracks.get(analysis_id)
        if not track:
            return
        
        # Mark as completed
        track['completed'] = True
        track['exit_price'] = exit_price
        track['result'] = result
        track['exit_reason'] = exit_reason
        
        # Calculate PnL
        entry_price = track['entry_price']
        
        if track['action'] == 'BUY':
            pnl_percent = ((exit_price - entry_price) / entry_price) * 100
        else:  # SELL
            pnl_percent = ((entry_price - exit_price) / entry_price) * 100
        
        # Calculate duration
        duration_hours = (datetime.now() - track['start_time']).total_seconds() / 3600
        
        # Calculate max drawdown
        if track['action'] == 'BUY':
            max_drawdown = ((track['lowest_price'] - entry_price) / entry_price) * 100
        else:
            max_drawdown = ((entry_price - track['highest_price']) / entry_price) * 100
        
        # Prepare tracking result
        tracking_result = {
            'result': result,
            'exit_price': exit_price,
            'exit_reason': exit_reason,
            'pnl_percent': round(pnl_percent, 2),
            'duration_hours': round(duration_hours, 1),
            'max_drawdown_percent': round(max_drawdown, 2),
            'highest_price': track['highest_price'],
            'lowest_price': track['lowest_price'],
            'tp_hits': track['tp_hits'],
            'sl_hit': track['sl_hit'],
            'completed_at': datetime.now().isoformat()
        }
        
        # Save to database
        try:
            self.db.update_tracking_result(analysis_id, tracking_result)
            print(f"💾 Saved tracking result for {analysis_id}: {result} ({pnl_percent:+.2f}%)")
        except Exception as e:
            print(f"❌ Error saving tracking result: {e}")
        
        # Remove from active tracks
        del self.active_tracks[analysis_id]
    
    def get_active_count(self) -> int:
        """Get number of active tracking sessions"""
        return len([t for t in self.active_tracks.values() if not t['completed']])
    
    def stop_all(self):
        """Stop all tracking (for graceful shutdown)"""
        for ws in self.ws_connections.values():
            asyncio.create_task(ws.close())
        
        self.ws_connections.clear()
        self.active_tracks.clear()
        print("🛑 Stopped all price tracking")


# Global tracker instance
_tracker_instance = None

def get_tracker() -> PriceTracker:
    """Get or create tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = PriceTracker()
    return _tracker_instance
