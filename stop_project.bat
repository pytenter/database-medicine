@echo off
chcp 65001 >nul
setlocal

echo Stopping Django and Vite windows...
taskkill /FI "WINDOWTITLE eq Pharmacy Backend" /T /F >nul 2>nul
taskkill /FI "WINDOWTITLE eq Pharmacy Frontend" /T /F >nul 2>nul

echo Done.
endlocal
