@echo off
echo Verificando se a porta 8000 esta em uso...
netstat -ano | findstr :8000 >nul
if %errorlevel% == 0 (
    echo Porta 8000 esta em uso. Tentando liberar...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

echo.
echo Iniciando servidor FastAPI na porta 8000...
echo Acesse: http://localhost:8000
echo.
echo Para parar o servidor, pressione Ctrl+C
echo.

python main.py





