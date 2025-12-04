@echo off
echo ========================================
echo   Parando Aplicacao RFV
echo ========================================
echo.

echo Verificando processos na porta 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Encerrando processo %%a...
    taskkill /F /PID %%a >nul 2>&1
)

echo Verificando processos na porta 5173 (Frontend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173') do (
    echo Encerrando processo %%a...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Aplicacao parada!
pause



