import os
import glob

# library path
python_lib = glob.glob('/usr/local/python3.9-static/lib/libpython3.9.so*')[0]

a = Analysis(
    ['main.py'],
    binaries=[
        ('/usr/local/lib/libz.a', '.'),
        (python_lib, '.')
    ],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=True
)

pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="binmgr",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    runtime_tmpdir='.'  # Extract to current directory instead of /tmp
)