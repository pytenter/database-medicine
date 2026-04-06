@echo off
setlocal

cd /d %~dp0

set "PYTHON_EXE=C:\ProgramData\Miniconda3\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

set "BACKEND_PORT=8000"
set "FRONTEND_PORT=5173"

echo [1/4] 检查 openGauss 状态...
powershell -NoProfile -Command "$client = New-Object Net.Sockets.TcpClient; try { $client.Connect('127.0.0.1', 5432); Write-Host 'openGauss 已就绪: 127.0.0.1:5432'; exit 0 } catch { Write-Host 'openGauss 未启动: 127.0.0.1:5432'; exit 1 } finally { if ($client.Connected) { $client.Close() } }"
if errorlevel 1 (
    echo.
    echo 请先启动 openGauss 数据库或 Docker 容器。
    pause
    exit /b 1
)

echo [2/4] 使用 Python: %PYTHON_EXE%
where.exe npm.cmd >nul 2>nul
if errorlevel 1 (
    echo 未找到 npm.cmd，请先安装 Node.js 并加入环境变量。
    pause
    exit /b 1
)

echo [3/4] 启动 Django 后端...
start "Pharmacy Backend" cmd /k "cd /d %~dp0backend && "%PYTHON_EXE%" manage.py runserver %BACKEND_PORT%"

timeout /t 3 /nobreak >nul
powershell -NoProfile -Command "$client = New-Object Net.Sockets.TcpClient; try { $client.Connect('127.0.0.1', %BACKEND_PORT%); Write-Host 'Django 已启动: http://127.0.0.1:%BACKEND_PORT%/'; exit 0 } catch { Write-Host 'Django 还未成功启动，请检查 Pharmacy Backend 窗口中的报错信息。'; exit 1 } finally { if ($client.Connected) { $client.Close() } }"
if errorlevel 1 (
    echo.
    echo 后端启动失败，请查看错误信息后重试。
    pause
    exit /b 1
)

echo [4/4] 启动 Vue 前端...
start "Pharmacy Frontend" cmd /k "cd /d %~dp0frontend && npm.cmd run dev"

echo.
echo 后端地址: http://127.0.0.1:%BACKEND_PORT%/
echo 前端地址: 请查看 Pharmacy Frontend 窗口中的 Vite 输出
echo.
echo 已打开以下窗口:
echo - Pharmacy Backend
echo - Pharmacy Frontend
endlocal