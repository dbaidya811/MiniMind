@echo off
set "MINIMIND_ROOT=%~dp0"
cd /d "%MINIMIND_ROOT%"
call "%MINIMIND_ROOT%venv\Scripts\activate.bat"
python "%MINIMIND_ROOT%app\cli.py" %*