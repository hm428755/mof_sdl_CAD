@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
set "PYTHONUTF8=1"
if not exist ".venv\Scripts\python.exe" goto :missing_env_exe
".venv\Scripts\python.exe" -c "import sys,struct; assert sys.version_info[:2] == (3,12) and struct.calcsize('P') == 8" >nul 2>&1
if not errorlevel 1 goto :install
:keepenv
set "CAD_OLD_ENV=.venv_previous_%RANDOM%"
echo Existing virtual environment is not usable. Keeping it as %CAD_OLD_ENV%.
ren ".venv" "%CAD_OLD_ENV%"
if errorlevel 1 goto :failed
:missing_env_exe
if exist ".venv" goto :keepenv
:findpython
set "CAD_PY_EXE="
py -3.12 -c "import struct; assert struct.calcsize('P') == 8" >nul 2>&1
if not errorlevel 1 goto :create_with_launcher
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "CAD_PY_EXE=%LocalAppData%\Programs\Python\Python312\python.exe"
if defined CAD_PY_EXE goto :check_exe
if exist "%ProgramFiles%\Python312\python.exe" set "CAD_PY_EXE=%ProgramFiles%\Python312\python.exe"
if defined CAD_PY_EXE goto :check_exe
python -c "import sys,struct; assert sys.version_info[:2] == (3,12) and struct.calcsize('P') == 8" >nul 2>&1
if errorlevel 1 goto :missingpython
python -m venv .venv
if errorlevel 1 goto :failed
goto :install
:check_exe
"%CAD_PY_EXE%" -c "import sys,struct; assert sys.version_info[:2] == (3,12) and struct.calcsize('P') == 8" >nul 2>&1
if errorlevel 1 goto :missingpython
"%CAD_PY_EXE%" -m venv .venv
if errorlevel 1 goto :failed
goto :install
:create_with_launcher
py -3.12 -m venv .venv
if errorlevel 1 goto :failed
:install
".venv\Scripts\python.exe" -m pip install --log "CAD_Install.log" -r "01_requirements_cad_R02.txt"
if errorlevel 1 goto :failed
echo Setup complete. Starting the editor next.
exit /b 0
:missingpython
echo Python 3.12 64-bit was not found. The editor has not started yet.
echo Install: https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe
echo Then run 06_Open_CAD_Editor_R02.bat again.
echo If already installed, restart this window after installation.
start "" "https://www.python.org/downloads/release/python-31210/"
pause
exit /b 1
:failed
echo Setup failed. Read the error above and CAD_Install.log.
pause
exit /b 1
