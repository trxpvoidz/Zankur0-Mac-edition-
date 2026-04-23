# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

block_cipher = None

# Collect all needed data and hidden imports
added_files = [
    ('templates', 'templates'),   # HTML files
    ('assets', 'assets'),         # sound files, bg-music.mp3, etc.
]

added_files.append(('icon.icns', '.'))

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'flask',
        'flask_cors',
        'PIL',
        'PIL._imaging',
        'cryptography',
        'cryptography.hazmat.backends.openssl',
        'werkzeug',
        'engineio.async_drivers.threading',
        'jinja2',
        'jinja2.ext',
        'webview',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Zankur0',
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
    icon='icon.icns' if sys.platform == 'darwin' else None,  # Put your .icns file in the project root
)

app = BUNDLE(
    exe,
    name='Zankur0.app',
    icon='icon.icns' if sys.platform == 'darwin' else None,
    bundle_identifier='com.ecliptix.zankur0',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleName': 'Zankur0',
        'NSMicrophoneUsageDescription': 'This app does not need microphone access.',
        'LSMinimumSystemVersion': '10.15',
    },
)