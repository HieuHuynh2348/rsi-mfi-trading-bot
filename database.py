"""
Database module for Analysis History
PostgreSQL on Railway with auto-cleanup
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import SimpleConnectionPool

class AnalysisDatabase:
    def __init__(self):
        """Initialize PostgreSQL connection pool"""
        # Railway PostgreSQL connection
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create connection pool (min=1, max=10)
        self.pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=database_url
        )
        
        # Initialize schema
        self._init_schema()
    
    def _init_schema(self):
        """Create tables if not exist"""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                # Create analysis_history table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_history (
                        id SERIAL PRIMARY KEY,
                        analysis_id VARCHAR(100) UNIQUE NOT NULL,
                        user_id BIGINT NOT NULL,
                        symbol VARCHAR(20) NOT NULL,
                        timeframe VARCHAR(10) NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        expires_at TIMESTAMP NOT NULL,
                        
                        -- AI Full Response (JSONB)
                        ai_full_response JSONB NOT NULL,
                        
                        -- Market Snapshot (JSONB)
                        market_snapshot JSONB NOT NULL,
                        
                        -- Auto-tracking Results (JSONB)
                        tracking_result JSONB,
                        
                        -- Metadata
                        status VARCHAR(20) DEFAULT 'COMPLETED',
                        
                        -- Indexes for fast queries
                        CONSTRAINT unique_user_symbol_time UNIQUE (user_id, symbol, created_at)
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_user_symbol 
                        ON analysis_history(user_id, symbol);
                    
                    CREATE INDEX IF NOT EXISTS idx_symbol_created 
                        ON analysis_history(symbol, created_at DESC);
                    
                    CREATE INDEX IF NOT EXISTS idx_expires 
                        ON analysis_history(expires_at);
                """)
                
                # Create function for auto-cleanup
                cur.execute("""
                    CREATE OR REPLACE FUNCTION cleanup_expired_analyses()
                    RETURNS INTEGER AS $$
                    DECLARE
                        deleted_count INTEGER;
                    BEGIN
                        DELETE FROM analysis_history 
                        WHERE expires_at < NOW();
                        
                        GET DIAGNOSTICS deleted_count = ROW_COUNT;
                        RETURN deleted_count;
                    END;
                    $$ LANGUAGE plpgsql;
                """)
                
                conn.commit()
                print("✅ Database schema initialized successfully")
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error initializing schema: {e}")
            raise
        finally:
            self.pool.putconn(conn)
    
    def save_analysis(
        self,
        user_id: int,
        symbol: str,
        timeframe: str,
        ai_response: Dict,
        market_snapshot: Dict,
        retention_days: int = 7
    ) -> str:
        """
        Save new analysis to database
        
        Args:
            user_id: Telegram user ID
            symbol: Trading symbol (e.g., BTCUSDT)
            timeframe: Chart timeframe (1h, 4h, 1d)
            ai_response: Full AI JSON response
            market_snapshot: Market indicators snapshot
            retention_days: Days to keep (default 7)
        
        Returns:
            analysis_id: Generated unique ID
        """
        conn = self.pool.getconn()
        try:
            # Generate analysis_id
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            analysis_id = f"{symbol.lower()}_{timestamp}_{user_id}"
            
            # Calculate expiry
            expires_at = datetime.now() + timedelta(days=retention_days)
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO analysis_history (
                        analysis_id, user_id, symbol, timeframe,
                        expires_at, ai_full_response, market_snapshot,
                        status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    analysis_id,
                    user_id,
                    symbol,
                    timeframe,
                    expires_at,
                    Json(ai_response),
                    Json(market_snapshot),
                    'PENDING_TRACKING'  # Will be updated by tracker
                ))
                
                conn.commit()
                record_id = cur.fetchone()[0]
                
                print(f"✅ Saved analysis {analysis_id} (DB ID: {record_id})")
                return analysis_id
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error saving analysis: {e}")
            raise
        finally:
            self.pool.putconn(conn)
    
    def update_tracking_result(
        self,
        analysis_id: str,
        tracking_result: Dict
    ):
        """
        Update tracking result after price monitoring
        
        Args:
            analysis_id: Analysis ID to update
            tracking_result: Tracking data (entry, TP/SL hits, PnL)
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE analysis_history
                    SET tracking_result = %s,
                        status = 'COMPLETED'
                    WHERE analysis_id = %s
                """, (
                    Json(tracking_result),
                    analysis_id
                ))
                
                conn.commit()
                print(f"✅ Updated tracking for {analysis_id}")
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error updating tracking: {e}")
            raise
        finally:
            self.pool.putconn(conn)
    
    def add_manual_review(
        self,
        analysis_id: str,
        user_id: int,
        review: str,  # 'good' or 'bad'
        comment: str = None
    ):
        """
        Add manual review from user (👍/👎)
        
        Args:
            analysis_id: Analysis ID to review
            user_id: User ID
            review: 'good' or 'bad'
            comment: Optional comment
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                # Add review to tracking_result JSON
                cur.execute("""
                    UPDATE analysis_history
                    SET tracking_result = COALESCE(tracking_result, '{}'::jsonb) || 
                        jsonb_build_object('manual_review', %s, 'review_comment', %s, 'reviewed_at', NOW())
                    WHERE analysis_id = %s AND user_id = %s
                    RETURNING analysis_id
                """, (review, comment, analysis_id, user_id))
                
                result = cur.fetchone()
                if result:
                    conn.commit()
                    print(f"✅ Added manual review {review} for {analysis_id}")
                    return True
                else:
                    print(f"❌ Analysis {analysis_id} not found or unauthorized")
                    return False
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error adding review: {e}")
            return False
        finally:
            self.pool.putconn(conn)
    
    def get_symbol_history(
        self,
        symbol: str,
        user_id: int,
        days: int = 7,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get analysis history for specific symbol
        
        Args:
            symbol: Trading symbol
            user_id: User ID
            days: Look back days
            limit: Max results
        
        Returns:
            List of analysis records (most recent first)
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        analysis_id,
                        symbol,
                        timeframe,
                        created_at,
                        ai_full_response,
                        market_snapshot,
                        tracking_result,
                        status
                    FROM analysis_history
                    WHERE user_id = %s
                      AND symbol = %s
                      AND created_at >= NOW() - INTERVAL '%s days'
                      AND status = 'COMPLETED'
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (user_id, symbol, days, limit))
                
                results = cur.fetchall()
                
                # Convert to list of dicts
                return [dict(row) for row in results]
                
        except Exception as e:
            print(f"❌ Error fetching history: {e}")
            return []
        finally:
            self.pool.putconn(conn)
    
    def get_all_history(
        self,
        user_id: int,
        days: int = 7,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get ALL analysis history for user (all symbols)
        
        Args:
            user_id: User ID
            days: Look back days
            limit: Max results
        
        Returns:
            List of analysis records (most recent first)
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        analysis_id,
                        symbol,
                        timeframe,
                        created_at,
                        ai_full_response,
                        market_snapshot,
                        tracking_result,
                        status
                    FROM analysis_history
                    WHERE user_id = %s
                      AND created_at >= NOW() - INTERVAL '%s days'
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (user_id, days, limit))
                
                results = cur.fetchall()
                
                # Convert to list of dicts
                return [dict(row) for row in results]
                
        except Exception as e:
            print(f"❌ Error fetching all history: {e}")
            return []
        finally:
            self.pool.putconn(conn)
    
    def get_all_history(
        self,
        user_id: int,
        days: int = 7,
        symbol_filter: Optional[str] = None,
        timeframe_filter: Optional[str] = None,
        result_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all analysis history with filters
        
        Args:
            user_id: User ID
            days: Look back days
            symbol_filter: Filter by symbol (optional)
            timeframe_filter: Filter by timeframe (optional)
            result_filter: Filter by result WIN/LOSS (optional)
        
        Returns:
            List of analysis records
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Build dynamic query
                query = """
                    SELECT 
                        analysis_id,
                        symbol,
                        timeframe,
                        created_at,
                        ai_full_response,
                        market_snapshot,
                        tracking_result,
                        status
                    FROM analysis_history
                    WHERE user_id = %s
                      AND created_at >= NOW() - INTERVAL '%s days'
                      AND status = 'COMPLETED'
                """
                params = [user_id, days]
                
                if symbol_filter:
                    query += " AND symbol = %s"
                    params.append(symbol_filter)
                
                if timeframe_filter:
                    query += " AND timeframe = %s"
                    params.append(timeframe_filter)
                
                if result_filter:
                    query += " AND tracking_result->>'result' = %s"
                    params.append(result_filter)
                
                query += " ORDER BY created_at DESC LIMIT 100"
                
                cur.execute(query, params)
                results = cur.fetchall()
                
                return [dict(row) for row in results]
                
        except Exception as e:
            print(f"❌ Error fetching all history: {e}")
            return []
        finally:
            self.pool.putconn(conn)
    
    def calculate_accuracy_stats(
        self,
        symbol: str,
        user_id: int,
        days: int = 7
    ) -> Dict:
        """
        Calculate win rate and accuracy stats for symbol
        
        Args:
            symbol: Trading symbol
            user_id: User ID
            days: Look back days
        
        Returns:
            Dict with accuracy statistics
        """
        history = self.get_symbol_history(symbol, user_id, days, limit=50)
        
        if not history:
            return {
                'total': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'patterns': {}
            }
        
        wins = []
        losses = []
        
        for record in history:
            tracking = record.get('tracking_result', {})
            result = tracking.get('result')
            pnl = tracking.get('pnl_percent', 0)
            
            if result == 'WIN':
                wins.append({
                    'pnl': pnl,
                    'snapshot': record['market_snapshot']
                })
            elif result == 'LOSS':
                losses.append({
                    'pnl': pnl,
                    'snapshot': record['market_snapshot']
                })
        
        total = len(wins) + len(losses)
        win_rate = (len(wins) / total * 100) if total > 0 else 0
        
        avg_profit = sum(w['pnl'] for w in wins) / len(wins) if wins else 0
        avg_loss = sum(l['pnl'] for l in losses) / len(losses) if losses else 0
        
        return {
            'total': total,
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': round(win_rate, 1),
            'avg_profit': round(avg_profit, 2),
            'avg_loss': round(avg_loss, 2),
            'patterns': self._analyze_patterns(wins, losses)
        }
    
    def _analyze_patterns(self, wins: List[Dict], losses: List[Dict]) -> Dict:
        """
        Analyze winning/losing patterns
        
        Returns:
            Dict with pattern analysis
        """
        if not wins and not losses:
            return {}
        
        patterns = {
            'winning_conditions': {},
            'losing_conditions': {},
            'recommendations': []
        }
        
        # Analyze winning patterns
        if wins:
            rsi_wins = [w['snapshot']['rsi_6'] for w in wins]
            mfi_wins = [w['snapshot']['mfi_6'] for w in wins]
            vp_wins = [w['snapshot'].get('volume_profile_position', 'UNKNOWN') for w in wins]
            
            patterns['winning_conditions'] = {
                'rsi_range': f"{min(rsi_wins):.1f} - {max(rsi_wins):.1f}",
                'rsi_avg': round(sum(rsi_wins) / len(rsi_wins), 1),
                'mfi_avg': round(sum(mfi_wins) / len(mfi_wins), 1),
                'best_vp_position': max(set(vp_wins), key=vp_wins.count)
            }
        
        # Analyze losing patterns
        if losses:
            rsi_losses = [l['snapshot']['rsi_6'] for l in losses]
            mfi_losses = [l['snapshot']['mfi_6'] for l in losses]
            
            patterns['losing_conditions'] = {
                'rsi_range': f"{min(rsi_losses):.1f} - {max(rsi_losses):.1f}",
                'rsi_avg': round(sum(rsi_losses) / len(rsi_losses), 1),
                'mfi_avg': round(sum(mfi_losses) / len(mfi_losses), 1)
            }
        
        return patterns
    
    def cleanup_expired(self) -> int:
        """
        Manually trigger cleanup of expired analyses
        
        Returns:
            Number of deleted records
        """
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT cleanup_expired_analyses()")
                deleted_count = cur.fetchone()[0]
                conn.commit()
                
                if deleted_count > 0:
                    print(f"🗑️ Cleaned up {deleted_count} expired analyses")
                
                return deleted_count
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error during cleanup: {e}")
            return 0
        finally:
            self.pool.putconn(conn)
    
    def close(self):
        """Close all connections in pool"""
        if self.pool:
            self.pool.closeall()
            print("✅ Database connections closed")


# Global database instance
_db_instance = None

def get_db() -> AnalysisDatabase:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = AnalysisDatabase()
    return _db_instance
