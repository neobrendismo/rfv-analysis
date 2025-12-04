@echo off
echo ========================================
echo   Iniciando Aplicacao RFV
echo ========================================
echo.

echo Iniciando Backend...
start "Backend RFV" cmd /k "cd backend && python main.py"

timeout /t 3 /nobreak >nul

echo Iniciando Frontend...
start "Frontend RFV" cmd /k "cd frontend && start_frontend.cmd"

echo.
echo ========================================
echo   Aplicacao iniciada!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Para parar, use: parar_aplicacao.bat
echo Ou feche as janelas do terminal
echo.
pause



