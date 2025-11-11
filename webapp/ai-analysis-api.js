/**
 * AI Analysis API Integration for WebApp
 * Calls Flask API endpoint directly and returns full analysis result
 * Version: 2.0 - Direct API Integration
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
        
        console.log(`🤖 Triggering AI Analysis: symbol=${symbol}, timeframe=${timeframe}, user=${userId}`);
        
        // Prepare request data
        const requestData = {
            user_id: userId,
            symbol: symbol,
            timeframe: timeframe || '1h'
        };
        
        console.log('📤 Calling API endpoint /api/ai-analysis:', requestData);
        
        // Call Flask API endpoint
        const response = await fetch('/api/ai-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        // Check response status
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        // Parse response
        const result = await response.json();
        
        console.log('✅ API Response received:', result);
        
        if (!result.success) {
            throw new Error(result.error || 'Analysis failed');
        }
        
        // Success haptic
        if (tg.HapticFeedback) {
            tg.HapticFeedback.notificationOccurred('success');
        }
        
        // Return full analysis data for webapp display
        return {
            success: true,
            message: result.message || 'Analysis complete',
            analysis: result.analysis  // Contains full Gemini analysis
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

console.log('✅ AI Analysis API v2.0 loaded - Direct API integration');
