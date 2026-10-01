import os

block_cipher = None

PROJECT_ROOT = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['main.py'],
    pathex=[PROJECT_ROOT],
    binaries=[
        (os.path.join(PROJECT_ROOT, 'lib', '*.dll'), 'lib'),
    ],
    datas=[
        (os.path.join(PROJECT_ROOT, 'resources', 'app.ico'), 'resources'),
    ],
    hiddenimports=[
        'comtypes',
        'comtypes.client',
        'comtypes.automation',
        'comtypes.gen',
        'comtypes.stream',
        'comtypes.persist',
        'win32api',
        'win32con',
        'win32gui',
        'pythoncom',
        'pywintypes',
        'win32timezone',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib', 'numpy', 'PyQt5', 'PySide2',
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
    [],
    exclude_binaries=True,
    name='好看韩剧5',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(PROJECT_ROOT, 'resources', 'app.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='hkhj5',
)