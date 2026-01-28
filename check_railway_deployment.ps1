# Script para monitorear deployment de Railway
# Ejecutar con: .\check_railway_deployment.ps1

$url = "https://web-production-4c740.up.railway.app/health"
$maxAttempts = 10
$delaySeconds = 30

Write-Host "`n🚀 Monitoreando deployment en Railway..." -ForegroundColor Cyan
Write-Host "URL: $url" -ForegroundColor Gray
Write-Host "Esperando versión: 2.3.0" -ForegroundColor Gray
Write-Host "Comprobaciones cada $delaySeconds segundos`n" -ForegroundColor Gray

for ($i = 1; $i -le $maxAttempts; $i++) {
    try {
        $response = Invoke-RestMethod -Uri $url -Method GET -ErrorAction Stop
        
        Write-Host "[$i/$maxAttempts] " -NoNewline -ForegroundColor Yellow
        Write-Host "Versión actual: $($response.version)" -NoNewline
        
        if ($response.version -eq "2.3.0") {
            Write-Host " ✅" -ForegroundColor Green
            Write-Host "`n🎉 ¡Deployment completado exitosamente!" -ForegroundColor Green
            
            if ($response.PSObject.Properties.Name -contains "ai_system") {
                Write-Host "`n🤖 Sistema AI Híbrido:" -ForegroundColor Cyan
                Write-Host "   ML Entrenado: $($response.ai_system.ml_trained)" -ForegroundColor White
                Write-Host "   Prophet: $($response.ai_system.prophet_available)" -ForegroundColor White
                Write-Host "   FinBERT: $($response.ai_system.finbert_available)" -ForegroundColor White
            }
            
            Write-Host "`n✅ Railway está listo para usar con IA" -ForegroundColor Green
            Write-Host "`n📝 Prueba con:" -ForegroundColor Cyan
            Write-Host "Invoke-RestMethod -Uri 'https://web-production-4c740.up.railway.app/api/v1/stock/SAN.MC/score?use_ai=true'" -ForegroundColor Gray
            
            exit 0
        } else {
            Write-Host " ⏳ (esperando...)" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "[$i/$maxAttempts] ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    if ($i -lt $maxAttempts) {
        Start-Sleep -Seconds $delaySeconds
    }
}

Write-Host "`n⚠️ Deployment aún en progreso después de $($maxAttempts * $delaySeconds) segundos" -ForegroundColor Yellow
Write-Host "Verifica el dashboard de Railway: https://railway.app" -ForegroundColor Gray
Write-Host "O ejecuta este script nuevamente en unos minutos" -ForegroundColor Gray
