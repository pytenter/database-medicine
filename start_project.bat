@echo off
setlocal

cd /d %~dp0

echo [1/3] Checking openGauss connection...
powershell -NoProfile -Command "$client = New-Object Net.Sockets.TcpClient; try { $client.Connect('127.0.0.1', 5432); Write-Host 'openGauss is reachable on 127.0.0.1:5432'; exit 0 } catch { Write-Host 'openGauss is not reachable on 127.0.0.1:5432'; exit 1 } finally { if ($client.Connected) { $client.Close() } }"
if errorlevel 1 (
    echo.
    echo Failed to connect to openGauss. Start the Docker container first.
    pause
    exit /b 1
)

echo [2/3] Starting Django backend...
start "Pharmacy Backend" cmd /k "cd /d %~dp0backend && python manage.py runserver"

echo [3/3] Starting Vue frontend...
start "Pharmacy Frontend" cmd /k "cd /d %~dp0frontend && npm.cmd run dev"

echo.
echo Backend:  http://127.0.0.1:8000/
echo Frontend: http://127.0.0.1:5173/
echo.
echo Two new windows were opened for the backend and frontend.
endlocal
