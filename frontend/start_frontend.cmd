@echo off
echo ========================================
echo   Iniciando Frontend RFV
echo ========================================
echo.

cd /d %~dp0

echo Verificando se node_modules existe...
if not exist "node_modules" (
    echo Instalando dependencias...
    call npm install
    echo.
)

echo Iniciando servidor de desenvolvimento...
echo.
echo Frontend estara disponivel em: http://localhost:5173
echo.
echo Para parar, pressione Ctrl+C
echo.

call npm run dev

pause

