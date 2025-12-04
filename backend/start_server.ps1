# Script PowerShell para iniciar o servidor
Write-Host "Verificando se a porta 8000 esta em uso..." -ForegroundColor Yellow

$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "Porta 8000 esta em uso. Tentando liberar..." -ForegroundColor Yellow
    $processId = $portInUse.OwningProcess
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "Iniciando servidor FastAPI na porta 8000..." -ForegroundColor Green
Write-Host "Acesse: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para parar o servidor, pressione Ctrl+C" -ForegroundColor Yellow
Write-Host ""

python main.py





