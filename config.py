import os
from pathlib import Path

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent

# Папка по умолчанию для скачивания видео
DOWNLOAD_DIR = BASE_DIR / "downloads"

# Создаем папку загрузок, если её нет
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
