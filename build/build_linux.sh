#!/bin/bash
echo "===================================="
echo "  GrabWave — Linux Build Script"
echo "===================================="

# Убедись что pyinstaller установлен
pip install pyinstaller pillow --quiet

echo "[1/3] Установка зависимостей..."
pip install -r ../requirements.txt --quiet

echo "[2/3] Сборка GrabWave..."
cd ..
pyinstaller \
    --onefile \
    --windowed \
    --name=GrabWave \
    --add-data="style.qss:." \
    --add-data="assets:assets" \
    --add-data="config.py:." \
    --add-data="src:src" \
    --hidden-import=PyQt6 \
    --hidden-import=yt_dlp \
    --hidden-import=imageio_ffmpeg \
    --hidden-import=browser_cookie3 \
    main.py

echo "[3/3] Готово!"
echo "Файл: dist/GrabWave"
echo ""
echo "Запуск: ./dist/GrabWave"
echo ""
echo "Примечания для Linux:"
echo "  - Установи Deno: curl -fsSL https://deno.land/install.sh | sh"
echo "  - Для иконки в панели задач создай .desktop файл:"
echo '    [Desktop Entry]'
echo '    Name=GrabWave'
echo '    Exec=/path/to/GrabWave'
echo '    Icon=/path/to/assets/icon.png'
echo '    Type=Application'
echo '    Categories=Network;'
