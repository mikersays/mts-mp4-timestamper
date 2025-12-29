# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for MTS to MP4 Converter (Single-file mode)

Build command:
    pyinstaller mts_converter.spec

This creates standalone single-file executables with ffmpeg bundled inside.
"""

import os
from pathlib import Path

block_cipher = None

# Find FFmpeg binaries (check current dir, then ffmpeg subdir)
ffmpeg_files = []
for exe in ['ffmpeg.exe', 'ffprobe.exe']:
    if os.path.exists(exe):
        ffmpeg_files.append((exe, '.'))
    elif os.path.exists(os.path.join('ffmpeg', exe)):
        ffmpeg_files.append((os.path.join('ffmpeg', exe), '.'))

if not ffmpeg_files:
    print("WARNING: ffmpeg.exe/ffprobe.exe not found - they won't be bundled!")

# GUI version (single file)
gui_a = Analysis(
    ['mts_converter_gui.py'],
    pathex=[],
    binaries=ffmpeg_files,
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

gui_pyz = PYZ(gui_a.pure, gui_a.zipped_data, cipher=block_cipher)

gui_exe = EXE(
    gui_pyz,
    gui_a.scripts,
    gui_a.binaries,
    gui_a.zipfiles,
    gui_a.datas,
    [],
    name='MTS_Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one: icon='icon.ico'
)

# CLI version (single file)
cli_a = Analysis(
    ['mts_converter.py'],
    pathex=[],
    binaries=ffmpeg_files,
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

cli_pyz = PYZ(cli_a.pure, cli_a.zipped_data, cipher=block_cipher)

cli_exe = EXE(
    cli_pyz,
    cli_a.scripts,
    cli_a.binaries,
    cli_a.zipfiles,
    cli_a.datas,
    [],
    name='MTS_Converter_CLI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console window for CLI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
