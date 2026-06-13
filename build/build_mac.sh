#!/bin/bash
echo "===================================="
echo "  GrabWave — macOS Build Script"
echo "===================================="

# Убедись что pyinstaller установлен
pip install pyinstaller pillow --quiet

echo "[1/4] Установка зависимостей..."
pip install -r ../requirements.txt --quiet

echo "[2/4] Конвертация иконки в .icns..."
cd ..
mkdir -p assets/icon.iconset
sips -z 16 16     assets/icon.png --out assets/icon.iconset/icon_16x16.png
sips -z 32 32     assets/icon.png --out assets/icon.iconset/icon_16x16@2x.png
sips -z 32 32     assets/icon.png --out assets/icon.iconset/icon_32x32.png
sips -z 64 64     assets/icon.png --out assets/icon.iconset/icon_32x32@2x.png
sips -z 128 128   assets/icon.png --out assets/icon.iconset/icon_128x128.png
sips -z 256 256   assets/icon.png --out assets/icon.iconset/icon_128x128@2x.png
sips -z 256 256   assets/icon.png --out assets/icon.iconset/icon_256x256.png
sips -z 512 512   assets/icon.png --out assets/icon.iconset/icon_256x256@2x.png
sips -z 512 512   assets/icon.png --out assets/icon.iconset/icon_512x512.png
iconutil -c icns assets/icon.iconset -o assets/icon.icns

echo "[3/4] Сборка GrabWave.app..."
pyinstaller \
    --onefile \
    --windowed \
    --name=GrabWave \
    --icon=assets/icon.icns \
    --add-data="style.qss:." \
    --add-data="assets:assets" \
    --add-data="config.py:." \
    --add-data="src:src" \
    --hidden-import=PyQt6 \
    --hidden-import=yt_dlp \
    --hidden-import=imageio_ffmpeg \
    --hidden-import=browser_cookie3 \
    main.py

echo "[4/4] Готово!"
echo "Файл: dist/GrabWave"
echo ""
echo "Примечание: deno для macOS нужно скачать отдельно:"
echo "  curl -fsSL https://deno.land/install.sh | sh"
