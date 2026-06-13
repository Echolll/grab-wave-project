# GrabWave — Build Scripts

В папке `build/` находятся скрипты для сборки исполняемого файла под каждую платформу.

## Требования (перед сборкой)

```bash
pip install pyinstaller
```

---

## Windows

Запусти `build_windows.bat` двойным кликом или из терминала:

```bat
cd build
build_windows.bat
```

Результат: `dist\GrabWave.exe`

---

## macOS

```bash
chmod +x build/build_mac.sh
./build/build_mac.sh
```

Результат: `dist/GrabWave` (запускаемый файл) или `.app`

> **Примечание:** Deno на Mac устанавливается отдельно: `curl -fsSL https://deno.land/install.sh | sh`

---

## Linux

```bash
chmod +x build/build_linux.sh
./build/build_linux.sh
```

Результат: `dist/GrabWave`

> **Примечание:** Deno на Linux устанавливается отдельно: `curl -fsSL https://deno.land/install.sh | sh`
