@echo off
setlocal enabledelayedexpansion

echo Registering MiniMind to User PATH...

set "TARGET_DIR=%~dp0"
:: Remove trailing backslash if exists
if "%TARGET_DIR:~-1%"=="\" set "TARGET_DIR=%TARGET_DIR:~0,-1%"

:: Get current user PATH from Registry
for /f "tokens=2* delims= " %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USER_PATH=%%b"

:: Check if already in PATH
echo "%USER_PATH%" | find /i "%TARGET_DIR%" >nul
if %errorlevel%==0 (
    echo [INFO] MiniMind is already registered in PATH.
) else (
    if defined USER_PATH (
        set "NEW_PATH=%USER_PATH%;%TARGET_DIR%"
    ) else (
        set "NEW_PATH=%TARGET_DIR%"
    )
    reg add "HKCU\Environment" /v PATH /t REG_EXPAND_SZ /d "!NEW_PATH!" /f >nul
    echo.
    echo [OK] MiniMind has been added to User PATH successfully!
)

echo.
echo Please restart your terminal, then type: minimind
pause