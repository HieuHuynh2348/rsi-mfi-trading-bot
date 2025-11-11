/**
 * AI Analysis API Integration for WebApp
 * Uses Telegram WebApp sendData for proper integration
 */

// Override the AI analysis function
window.triggerAIAnalysis = async function(symbol, timeframe) {
    const tg = window.Telegram?.WebApp;
    if (!tg) {
        console.error('❌ Telegram WebApp not available');
        throw new Error('Telegram WebApp not initialized');
    }
    
    try {
        // Get user ID from Telegram
        const userId = tg.initDataUnsafe?.user?.id;
        if (!userId) {
            throw new Error('Cannot get user ID from Telegram');
        }
        
        console.log(`🤖 Triggering AI Analysis: symbol=${symbol}, timeframe=${timeframe}`);
        
        // Prepare data for Telegram bot
        const analysisData = {
            action: 'ai_analysis',
            user_id: userId,
            symbol: symbol,
            timeframe: timeframe || '1h'
        };
        
        console.log('📤 Sending data to Telegram bot:', analysisData);
        
        // Send data to bot via Telegram WebApp API
        tg.sendData(JSON.stringify(analysisData));
        
        // Success haptic
        if (tg.HapticFeedback) {
            tg.HapticFeedback.notificationOccurred('success');
        }
        
        return { 
            success: true, 
            message: 'Analysis request sent to Telegram bot'
        };
        
    } catch (error) {
        console.error('❌ AI Analysis Error:', error);
        
        // Error haptic
        if (tg.HapticFeedback) {
            tg.HapticFeedback.notificationOccurred('error');
        }
        
        throw error;
    }
};

console.log('✅ AI Analysis API loaded');
