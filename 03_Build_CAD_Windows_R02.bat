@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run 02_Setup_CAD_Windows_R02.bat first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "Modules\01_Sonicator_Rack_Guide\02_Work\03_Rack_Guide_4Rod_R02\01_build_Preview_R02_4Rod.py"
if errorlevel 1 goto :failed
echo CAD generation complete.
explorer "Modules\01_Sonicator_Rack_Guide\03_Preview\03_Rack_Guide_4Rod_R02"
exit /b 0
:failed
echo CAD generation failed. Inspect the error above.
pause
exit /b 1
