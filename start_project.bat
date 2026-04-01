@echo off
setlocal

cd /d %~dp0

set "PYTHON_EXE=C:\ProgramData\Miniconda3\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

set "BACKEND_PORT=8000"
set "FRONTEND_PORT=5173"

echo [1/4] ?? openGauss ??...
powershell -NoProfile -Command "$client = New-Object Net.Sockets.TcpClient; try { $client.Connect('127.0.0.1', 5432); Write-Host 'openGauss ???: 127.0.0.1:5432'; exit 0 } catch { Write-Host 'openGauss ????: 127.0.0.1:5432'; exit 1 } finally { if ($client.Connected) { $client.Close() } }"
if errorlevel 1 (
    echo.
    echo ???? openGauss????? Docker ???
    pause
    exit /b 1
)

echo [2/4] ?????: %PYTHON_EXE%
where.exe npm.cmd >nul 2>nul
if errorlevel 1 (
    echo ??? npm.cmd???? Node.js ??????
    pause
    exit /b 1
)

echo [3/4] ?? Django ??...
start "Pharmacy Backend" cmd /k "cd /d %~dp0backend && "%PYTHON_EXE%" manage.py runserver %BACKEND_PORT%"

timeout /t 3 /nobreak >nul
powershell -NoProfile -Command "$client = New-Object Net.Sockets.TcpClient; try { $client.Connect('127.0.0.1', %BACKEND_PORT%); Write-Host 'Django ??????: http://127.0.0.1:%BACKEND_PORT%/'; exit 0 } catch { Write-Host 'Django ??????????? Pharmacy Backend ?????????'; exit 1 } finally { if ($client.Connected) { $client.Close() } }"
if errorlevel 1 (
    echo.
    echo ????????????????
    pause
    exit /b 1
)

echo [4/4] ?? Vue ??...
start "Pharmacy Frontend" cmd /k "cd /d %~dp0frontend && npm.cmd run dev"

echo.
echo ????: http://127.0.0.1:%BACKEND_PORT%/
echo ????: ??? Pharmacy Frontend ?????? Vite ???
echo.
echo ?????????
echo - Pharmacy Backend
echo - Pharmacy Frontend
endlocal
