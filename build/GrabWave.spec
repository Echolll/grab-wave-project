# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# Папка проекта (на уровень выше от build/)
project_dir = os.path.abspath(os.path.join(os.path.dirname(SPECPATH), '..'))

a = Analysis(
    [os.path.join(project_dir, 'main.py')],
    pathex=[project_dir],
    binaries=[],
    datas=[
        (os.path.join(project_dir, 'assets'), 'assets'),
        (os.path.join(project_dir, 'config.py'), '.'),
        (os.path.join(project_dir, 'src'), 'src'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'yt_dlp',
        'imageio_ffmpeg',
        'browser_cookie3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# Добавляем deno если существует (Windows)
deno_win = os.path.join(project_dir, 'deno.exe')
if os.path.exists(deno_win):
    a.datas += [(deno_win, '.')]

# Добавляем deno если существует (Mac/Linux)
deno_unix = os.path.join(project_dir, 'deno')
if os.path.exists(deno_unix):
    a.datas += [(deno_unix, '.')]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GrabWave',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_dir, 'assets', 'icon.ico') if sys.platform == 'win32' else None,
)
