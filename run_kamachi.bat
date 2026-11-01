@echo off
title KAMACHI 2.0 Desktop Assistant
cd /d "%~dp0"

echo ===================================================
echo             STARTING KAMACHI 2.0
echo ===================================================

if exist "kamachi\Scripts\activate.bat" (
    call "kamachi\Scripts\activate.bat"
    python run_with_avatar.py
) else (
    python run_with_avatar.py
)

if %errorlevel% neq 0 (
    echo.
    echo [Fallback]: Starting in standard console mode...
    python kamachi2_0.py
)

pause

