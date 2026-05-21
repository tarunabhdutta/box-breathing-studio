@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   Box Breathing Studio - Rebuild bundled Python
echo ============================================================
echo.
echo This is a one-time build step. It downloads the embeddable
echo Python 3.11.9 runtime and installs numpy + pygame into a
echo local python_portable\ folder.
echo.
echo Requires: internet, ~250 MB free disk, ~3 minutes.
echo.
echo Once finished, run install_app.bat to create Desktop shortcuts.
echo.
pause

if exist "python_portable\python.exe" (
    echo [info] python_portable already exists. Skipping download.
    goto install_deps
)

mkdir build_cache 2>nul
echo [1/4] Downloading Python 3.11.9 embeddable ...
powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile 'build_cache\python_embed.zip' -UseBasicParsing"
if errorlevel 1 (
    echo [error] Python download failed. Check your internet connection.
    pause
    exit /b 1
)

echo [2/4] Extracting ...
powershell -NoProfile -Command "Expand-Archive 'build_cache\python_embed.zip' -DestinationPath 'python_portable' -Force"

echo [3/4] Configuring embeddable Python (enabling site-packages) ...
powershell -NoProfile -Command "(Get-Content 'python_portable\python311._pth') -replace '#import site','import site`r`nLib\site-packages' | Set-Content 'python_portable\python311._pth'"

powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'build_cache\get-pip.py' -UseBasicParsing"
"python_portable\python.exe" "build_cache\get-pip.py" --no-warn-script-location >nul

:install_deps
echo [4/4] Installing numpy and pygame into the local Python ...
"python_portable\python.exe" -m pip install --no-warn-script-location numpy pygame --quiet
if errorlevel 1 (
    echo [error] Dependency install failed.
    pause
    exit /b 1
)

rem clean up the download cache
if exist "build_cache" rmdir /s /q "build_cache"

echo.
echo ============================================================
echo   Build complete.
echo ============================================================
echo.
echo Next step:  double-click install_app.bat to create the
echo "Box Breathing" Desktop shortcut.
echo.
pause
endlocal
