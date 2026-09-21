@echo off
echo Registering MiniMind to User PATH...
setx PATH "%PATH%;%~dp0"
echo.
echo [OK] MiniMind has been added to PATH successfully!
echo You can now open a new terminal anywhere and type: minimind
pause