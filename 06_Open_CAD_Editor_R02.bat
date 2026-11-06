@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  call "02_Setup_CAD_Windows_R02.bat"
  if errorlevel 1 exit /b 1
)
if not exist ".venv\Scripts\python.exe" goto :failed
".venv\Scripts\python.exe" -c "import cadquery,numpy,matplotlib" >nul 2>&1
if errorlevel 1 (
  call "02_Setup_CAD_Windows_R02.bat"
  if errorlevel 1 exit /b 1
)
".venv\Scripts\python.exe" -c "import cadquery,numpy,matplotlib" >nul 2>&1
if errorlevel 1 goto :failed
start "MOF CAD Editor" /min ".venv\Scripts\python.exe" "Modules\01_Sonicator_Rack_Guide\02_Work\05_Rack_Guide_Editor_R02\01_editor.py"
exit /b 0
:failed
echo Install Python 3.12 with the Python launcher, then run this file again.
echo See 07_CAD_Editor_README_R02.md for instructions.
pause
exit /b 1
