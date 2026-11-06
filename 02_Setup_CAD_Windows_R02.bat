@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3.12 -m venv .venv
  if errorlevel 1 goto :failed
)
".venv\Scripts\python.exe" -m pip install -r "01_requirements_cad_R02.txt"
if errorlevel 1 goto :failed
echo Setup complete. Run 03_Build_CAD_Windows_R02.bat next.
pause
exit /b 0
:failed
echo Setup failed. Install Python 3.12 with the Python launcher and inspect the error above.
pause
exit /b 1
