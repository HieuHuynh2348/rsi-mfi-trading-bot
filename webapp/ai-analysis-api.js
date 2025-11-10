/**
 * AI Analysis API Integration for WebApp
 * Replaces tg.sendData() with direct API calls
 */

// Override the AI analysis function
window.triggerAIAnalysis = async function(symbol, timeframe) {
    const tg = window.Telegram?.WebApp;
    if (!tg) {
        console.error('Telegram WebApp not available');
        return;
    }
    
    try {
        // Get user ID from Telegram
        const userId = tg.initDataUnsafe?.user?.id;
        if (!userId) {
            throw new Error('Cannot get user ID from Telegram');
        }
        
        // Prepare API request
        const apiUrl = window.location.origin + '/api/ai-analysis';
        const requestBody = {
            user_id: userId,
            symbol: symbol,
            timeframe: timeframe || '1h'
        };
        
        console.log(`📤 Calling AI Analysis API: ${apiUrl}`, requestBody);
        
        // Call API
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        console.log('✅ API Response:', data);
        
        if (data.success) {
            // Success haptic
            if (tg.HapticFeedback) {
                tg.HapticFeedback.notificationOccurred('success');
            }
            return { success: true, message: 'Analysis sent to Telegram' };
        } else {
            throw new Error(data.error || 'API request failed');
        }
        
    } catch (error) {
        console.error('❌ AI Analysis API Error:', error);
        
        // Error haptic
        if (tg.HapticFeedback) {
            tg.HapticFeedback.notificationOccurred('error');
        }
        
        throw error;
    }
};

console.log('✅ AI Analysis API loaded');
