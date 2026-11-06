@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto :install
py -3.12 -c "import struct; assert struct.calcsize('P') == 8" >nul 2>&1
if errorlevel 1 goto :missingpython
py -3.12 -m venv .venv
if errorlevel 1 goto :failed
:install
".venv\Scripts\python.exe" -m pip install -r "01_requirements_cad_R02.txt"
if errorlevel 1 goto :failed
echo Setup complete. Run 06_Open_CAD_Editor_R02.bat next.
pause
exit /b 0
:missingpython
echo Python 3.12 64-bit was not found. The editor has not started yet.
echo Download and install the official Windows 64-bit version:
echo https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe
echo Then run 06_Open_CAD_Editor_R02.bat again.
echo Check Add python.exe to PATH during installation.
start "" "https://www.python.org/downloads/release/python-31210/"
pause
exit /b 1
:failed
echo Setup failed. Inspect the error above.
pause
exit /b 1
