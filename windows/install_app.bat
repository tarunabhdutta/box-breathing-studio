@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   Box Breathing Studio  -  Offline portable installer
echo   Developed by Tarunabh Dutta
echo ============================================================
echo.

rem ------------------------------------------------------------
rem  Sanity check - the bundled Python must be present
rem ------------------------------------------------------------
if not exist "python_portable\pythonw.exe" (
    echo [error] python_portable\pythonw.exe is missing.
    echo         This installation appears to be incomplete.
    echo         Please re-copy the BoxBreathingApp folder.
    pause
    exit /b 1
)
if not exist "app.py" (
    echo [error] app.py is missing from this folder.
    pause
    exit /b 1
)

echo [ok] Bundled Python found.
"python_portable\python.exe" --version
echo [ok] App file found.
echo.

rem ------------------------------------------------------------
rem  Create Desktop + Start Menu shortcuts
rem ------------------------------------------------------------
echo [info] Creating shortcuts ...

set "TARGET=%~dp0run_app.bat"
set "WD=%~dp0"
set "ICON=%~dp0assets\icon.ico"

rem If we don't have an .ico, fall back to using pythonw as the icon source.
if not exist "%ICON%" set "ICON=%~dp0python_portable\pythonw.exe"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "foreach ($p in @([Environment]::GetFolderPath('Desktop'), (Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'))) {" ^
  "  $lnk = Join-Path $p 'Box Breathing.lnk';" ^
  "  $s = $ws.CreateShortcut($lnk);" ^
  "  $s.TargetPath = '%TARGET%';" ^
  "  $s.WorkingDirectory = '%WD%';" ^
  "  $s.WindowStyle = 7;" ^
  "  $s.IconLocation = '%ICON%';" ^
  "  $s.Description = 'Box Breathing Studio - guided pranayama by Tarunabh Dutta';" ^
  "  $s.Save();" ^
  "}"

echo.
echo ============================================================
echo   Installation complete.
echo ============================================================
echo.
echo   A "Box Breathing" shortcut is now on your Desktop and
echo   in the Start Menu.
echo.
echo   The whole app lives inside this folder - delete it to
echo   uninstall, nothing else on your machine is touched.
echo.
choice /m "Launch the app now"
if errorlevel 2 goto end
start "" "%~dp0run_app.bat"

:end
endlocal
