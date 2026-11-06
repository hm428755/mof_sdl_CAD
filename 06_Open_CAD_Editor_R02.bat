@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
set "PYTHONUTF8=1"
if not exist "Modules\01_Sonicator_Rack_Guide\02_Work\05_Rack_Guide_Editor_R02\08_start_editor.py" (
  echo Required editor files are missing.
  echo Extract the ENTIRE editor ZIP first. Do not run this BAT from inside a ZIP.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  call "02_Setup_CAD_Windows_R02.bat"
  if errorlevel 1 exit /b 1
)
".venv\Scripts\python.exe" -c "import sys,struct; assert sys.version_info[:2] == (3,12) and struct.calcsize('P') == 8; import cadquery,numpy,matplotlib" >nul 2>&1
if errorlevel 1 (
  call "02_Setup_CAD_Windows_R02.bat"
  if errorlevel 1 exit /b 1
)
".venv\Scripts\python.exe" -u "Modules\01_Sonicator_Rack_Guide\02_Work\05_Rack_Guide_Editor_R02\08_start_editor.py"
if errorlevel 1 (
  echo Editor startup failed. See CAD_Editor_Start.log in this folder.
  pause
  exit /b 1
)
exit /b 0
