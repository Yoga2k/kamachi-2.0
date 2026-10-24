@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Building KAMACHI AI Executable (.exe)

echo ===================================================
echo     KAMACHI AI 2.0 / 3.0 — Executable Builder
echo ===================================================
echo.

:: Detect Python environment
set "PYTHON_CMD="
if exist "%~dp0kamachi\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0kamachi\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_CMD=python"
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python was not found!
    echo Please install Python 3.10+ or set up the virtualenv in .\kamachi
    pause
    exit /b 1
)

echo [1/3] Using Python: %PYTHON_CMD%
"%PYTHON_CMD%" -m pip show pyinstaller >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo PyInstaller is not installed. Installing now...
    "%PYTHON_CMD%" -m pip install pyinstaller
)

echo.
echo [2/3] Building standalone KAMACHI.exe...
"%PYTHON_CMD%" -m PyInstaller --clean --noconfirm KAMACHI.spec

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Build failed. Please review the error messages above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [3/3] Build completed successfully!
echo Standalone executable created at:
echo    %~dp0dist\KAMACHI.exe
echo.
echo This file can be copied and used on any Windows PC!
echo ===================================================
pause
