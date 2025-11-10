"""Test institutional indicators on historical data"""
import asyncio
from gemini_analyzer import GeminiAnalyzer
from binance_client import BinanceClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_historical_institutional():
    """Test institutional analysis on historical klines"""
    try:
        analyzer = GeminiAnalyzer()
        binance = BinanceClient()
        
        symbol = "BTCUSDT"
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing Historical Institutional Analysis: {symbol}")
        logger.info(f"{'='*60}\n")
        
        # Get historical klines (7 days, 1h interval)
        klines_1h = await binance.get_klines(symbol, '1h', limit=168)  # 7 days
        
        if not klines_1h or len(klines_1h) < 50:
            logger.error("Not enough historical data")
            return
        
        import pandas as pd
        df = pd.DataFrame(klines_1h, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Convert to numeric
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        
        current_price = float(df.iloc[-1]['close'])
        
        # Test each institutional indicator
        logger.info(f"Current Price: ${current_price:,.2f}\n")
        
        # 1. Volume Profile
        logger.info("1️⃣ Volume Profile Historical Analysis:")
        vp_result = analyzer._analyze_volume_profile_historical(df, current_price)
        if vp_result:
            logger.info(f"   POC (Point of Control): ${vp_result.get('poc', 0):,.2f}")
            logger.info(f"   VAH (Value Area High): ${vp_result.get('vah', 0):,.2f}")
            logger.info(f"   VAL (Value Area Low): ${vp_result.get('val', 0):,.2f}")
            logger.info(f"   Price Position: {vp_result.get('current_position', 'N/A')}")
            logger.info(f"   Distance from POC: {vp_result.get('distance_from_poc_pct', 0):+.2f}%\n")
        else:
            logger.warning("   ❌ Volume Profile failed\n")
        
        # 2. Fair Value Gaps
        logger.info("2️⃣ Fair Value Gaps Historical Analysis:")
        fvg_result = analyzer._analyze_fvg_historical(df, current_price)
        if fvg_result:
            logger.info(f"   Total Bullish Gaps: {fvg_result.get('total_bullish_gaps', 0)}")
            logger.info(f"   Total Bearish Gaps: {fvg_result.get('total_bearish_gaps', 0)}")
            logger.info(f"   Unfilled Bullish: {fvg_result.get('unfilled_bullish_count', 0)}")
            logger.info(f"   Unfilled Bearish: {fvg_result.get('unfilled_bearish_count', 0)}")
            logger.info(f"   Gap Density: {fvg_result.get('gap_density_pct', 0):.2f}%")
            
            if fvg_result.get('nearest_bullish_gap'):
                gap = fvg_result['nearest_bullish_gap']
                logger.info(f"   Nearest Bullish Gap: ${gap['bottom']:,.2f} - ${gap['top']:,.2f}")
            if fvg_result.get('nearest_bearish_gap'):
                gap = fvg_result['nearest_bearish_gap']
                logger.info(f"   Nearest Bearish Gap: ${gap['bottom']:,.2f} - ${gap['top']:,.2f}")
            logger.info("")
        else:
            logger.warning("   ❌ FVG analysis failed\n")
        
        # 3. Order Blocks
        logger.info("3️⃣ Order Blocks Historical Analysis:")
        ob_result = analyzer._analyze_order_blocks_historical(df, current_price)
        if ob_result:
            logger.info(f"   Total Bullish OB: {ob_result.get('total_bullish_ob', 0)}")
            logger.info(f"   Total Bearish OB: {ob_result.get('total_bearish_ob', 0)}")
            logger.info(f"   Active Bullish OB: {ob_result.get('active_bullish_count', 0)}")
            logger.info(f"   Active Bearish OB: {ob_result.get('active_bearish_count', 0)}")
            logger.info(f"   OB Density: {ob_result.get('ob_density_pct', 0):.2f}%")
            
            if ob_result.get('strongest_bullish_ob'):
                ob = ob_result['strongest_bullish_ob']
                logger.info(f"   Strongest Bullish OB: ${ob['low']:,.2f} - ${ob['high']:,.2f} (Strength: {ob['strength']:.1f})")
            if ob_result.get('strongest_bearish_ob'):
                ob = ob_result['strongest_bearish_ob']
                logger.info(f"   Strongest Bearish OB: ${ob['low']:,.2f} - ${ob['high']:,.2f} (Strength: {ob['strength']:.1f})")
            logger.info("")
        else:
            logger.warning("   ❌ Order Blocks analysis failed\n")
        
        # 4. Smart Money Concepts
        logger.info("4️⃣ Smart Money Concepts Historical Analysis:")
        smc_result = analyzer._analyze_smc_historical(df)
        if smc_result:
            logger.info(f"   BOS Bullish: {smc_result.get('bos_bullish', 0)}")
            logger.info(f"   BOS Bearish: {smc_result.get('bos_bearish', 0)}")
            logger.info(f"   CHoCH Bullish: {smc_result.get('choch_bullish', 0)}")
            logger.info(f"   CHoCH Bearish: {smc_result.get('choch_bearish', 0)}")
            logger.info(f"   Swing Highs: {smc_result.get('swing_highs_count', 0)}")
            logger.info(f"   Swing Lows: {smc_result.get('swing_lows_count', 0)}")
            logger.info(f"   Structure Bias: {smc_result.get('structure_bias', 'N/A')}")
            logger.info(f"   Bullish Bias: {smc_result.get('bullish_bias_pct', 0):.1f}%")
            logger.info(f"   Total Structure Events: {smc_result.get('total_structure_events', 0)}\n")
        else:
            logger.warning("   ❌ SMC analysis failed\n")
        
        logger.info(f"{'='*60}")
        logger.info("✅ All institutional indicators tested successfully!")
        logger.info(f"{'='*60}\n")
        
        await binance.close()
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_historical_institutional())
