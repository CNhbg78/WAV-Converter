@echo off
chcp 65001 >nul
title WAV Converter - Build Tool
echo ==========================================
echo   WAV Converter - Build Tool
echo   XTS Studio
echo ==========================================
echo.

echo [1/3] Installing dependencies...
pip install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo ERROR: Dependency installation failed
    pause
    exit /b 1
)

echo.
echo [2/3] Cleaning old builds...
if exist src\build rmdir /s /q src\build

echo.
echo [3/3] Building executable...
cd src
pyinstaller app.py --onefile --windowed --name "WAVConverter" --add-data "i18n;./i18n" --hidden-import converter --hidden-import i18n --version-file ..\version.txt --distpath ..\release --clean --noconfirm --paths .
cd ..

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   SUCCESS!
echo   Output: release\WAVConverter.exe
echo.
echo   Note: Users need ffmpeg to run.
echo   Place ffmpeg.exe in:
echo     - System PATH, or
echo     - Same directory as exe, or
echo     - ffmpeg_bin\ folder
echo ==========================================
echo.
pause
