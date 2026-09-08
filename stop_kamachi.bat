@echo off
title Stop KAMACHI 3.0
echo ===================================================
echo Stopping KAMACHI 3.0 Voice Assistant ^& Avatar...
echo ===================================================

:: Terminate background pythonw.exe instances
taskkill /F /IM pythonw.exe 2>nul

:: Terminate any processes running KAMACHI scripts
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*kamachi*' -or $_.CommandLine -like '*run_with_avatar*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }" 2>nul

echo.
echo [SUCCESS] KAMACHI 3.0 has been stopped completely.
timeout /t 2 >nul
