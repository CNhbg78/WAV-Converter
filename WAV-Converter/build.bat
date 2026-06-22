@echo off
chcp 65001 >nul
title Audio Converter - Build Tool
echo ==========================================
echo   Audio Converter ^| ^]转换器 - Build Tool
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
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [3/3] Building executable...
pyinstaller src/main.py --onefile --windowed --name "AudioConverter" --add-data "src/i18n;./i18n" --version-file version.txt --clean --noconfirm

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   SUCCESS!
echo   Output: dist\AudioConverter.exe
echo.
echo   Note: Users need ffmpeg to run.
echo   Place ffmpeg.exe in:
echo     - System PATH, or
echo     - Same directory as exe, or
echo     - ffmpeg_bin\ folder
echo ==========================================
echo.
pause
