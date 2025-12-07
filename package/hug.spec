# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Collect hidden imports if necessary (e.g., pynput backends)
hiddenimports = []
hiddenimports += collect_submodules('pynput')
# Ensure X11 dependencies are included for Linux
try:
    hiddenimports += collect_submodules('Xlib')
except:
    pass

a = Analysis(
    ['../src/hug/__main__.py'],
    pathex=['../src'],
    binaries=[],
    datas=[
        ('../src/hug/resources', 'hug/resources'),
        ('../snippets', 'snippets'),
        ('../docs', 'docs'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='hug',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='hug',
)
