@echo off
chcp 65001 >nul
setlocal

cd /d %~dp0

set "PYTHON_EXE=C:\ProgramData\Miniconda3\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

set "BACKEND_PORT=8000"
set "FRONTEND_PORT=5173"

echo [1/4] Checking openGauss status...
powershell -NoProfile -Command "$client = New-Object Net.Sockets.TcpClient; try { $client.Connect('127.0.0.1', 5432); Write-Host 'openGauss is ready: 127.0.0.1:5432'; exit 0 } catch { Write-Host 'openGauss is not running: 127.0.0.1:5432'; exit 1 } finally { if ($client.Connected) { $client.Close() } }"
if errorlevel 1 (
    echo.
    echo Please start the openGauss database or Docker container first.
    pause
    exit /b 1
)

echo [2/4] Using Python: %PYTHON_EXE%
where.exe npm.cmd >nul 2>nul
if errorlevel 1 (
    echo npm.cmd was not found. Please install Node.js and add it to PATH.
    pause
    exit /b 1
)

echo [3/4] Starting Django backend...
start "Pharmacy Backend" cmd /k "cd /d %~dp0backend && "%PYTHON_EXE%" manage.py runserver %BACKEND_PORT%"

timeout /t 3 /nobreak >nul
powershell -NoProfile -Command "$client = New-Object Net.Sockets.TcpClient; try { $client.Connect('127.0.0.1', %BACKEND_PORT%); Write-Host 'Django is running: http://127.0.0.1:%BACKEND_PORT%/'; exit 0 } catch { Write-Host 'Django has not started yet. Check the Pharmacy Backend window for errors.'; exit 1 } finally { if ($client.Connected) { $client.Close() } }"
if errorlevel 1 (
    echo.
    echo Backend startup failed. Check the error message and retry.
    pause
    exit /b 1
)

echo [4/4] Starting Vue frontend...
start "Pharmacy Frontend" cmd /k "cd /d %~dp0frontend && npm.cmd run dev"

echo.
echo Backend URL: http://127.0.0.1:%BACKEND_PORT%/
echo Frontend URL: check the Vite output in the Pharmacy Frontend window.
echo.
echo Opened windows:
echo - Pharmacy Backend
echo - Pharmacy Frontend
endlocal
