@echo off
echo ====================================
echo   GrabWave — Windows Build Script
echo ====================================

:: Убедись что pyinstaller установлен
pip install pyinstaller pillow --quiet

echo [1/3] Установка зависимостей...
pip install -r ..\requirements.txt --quiet

echo [2/3] Сборка GrabWave.exe...
cd ..
pyinstaller ^
    --onefile ^
    --windowed ^
    --name=GrabWave ^
    --icon=assets\icon.ico ^
    --add-data="style.qss;." ^
    --add-data="assets;assets" ^
    --add-data="deno.exe;." ^
    --add-data="config.py;." ^
    --add-data="src;src" ^
    --hidden-import=PyQt6 ^
    --hidden-import=yt_dlp ^
    --hidden-import=imageio_ffmpeg ^
    --hidden-import=browser_cookie3 ^
    main.py

echo [3/3] Готово!
echo Файл: dist\GrabWave.exe
echo.
pause
