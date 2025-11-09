# Test API endpoint
$response = Invoke-WebRequest -Uri 'http://localhost:8080/api/chart?symbol=BTCUSDT&timeframe=1h' -UseBasicParsing
$json = $response.Content | ConvertFrom-Json

Write-Host "✅ Symbol: $($json.symbol)"
Write-Host "✅ Timeframe: $($json.timeframe)"
Write-Host "✅ Price: `$$($json.currentPrice)"
Write-Host "✅ Change: $($json.priceChange)%"
Write-Host "✅ RSI: $($json.rsi)"
Write-Host "✅ MFI: $($json.mfi)"
Write-Host "✅ Candles: $($json.candles.Count) items"
Write-Host "✅ First candle time: $($json.candles[0].time)"
Write-Host "✅ Last candle close: `$$($json.candles[-1].close)"
