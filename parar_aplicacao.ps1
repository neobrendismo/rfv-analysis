# Script PowerShell para parar a aplicação RFV
Write-Host "Parando aplicacao RFV..." -ForegroundColor Yellow
Write-Host ""

# Para Backend (porta 8000)
Write-Host "Verificando processos na porta 8000 (Backend)..." -ForegroundColor Cyan
$backendProcesses = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($backendProcesses) {
    foreach ($pid in $backendProcesses) {
        Write-Host "Encerrando processo $pid..." -ForegroundColor Yellow
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "Nenhum processo encontrado na porta 8000" -ForegroundColor Green
}

# Para Frontend (porta 5173)
Write-Host "Verificando processos na porta 5173 (Frontend)..." -ForegroundColor Cyan
$frontendProcesses = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($frontendProcesses) {
    foreach ($pid in $frontendProcesses) {
        Write-Host "Encerrando processo $pid..." -ForegroundColor Yellow
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "Nenhum processo encontrado na porta 5173" -ForegroundColor Green
}

Write-Host ""
Write-Host "Aplicacao parada!" -ForegroundColor Green



