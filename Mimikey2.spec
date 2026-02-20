# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['customtkinter']
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['mimikey.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Mimikey',
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
    icon=['icon.icns'],
)
app = BUNDLE(
    exe,
    name='Mimikey.app',
    icon='icon.icns',
    bundle_identifier='com.vedanshkumar.mimikey',,

info_plist={
    'NSAppleEventsUsageDescription': 'Mimikey needs to script Apple Events to function correctly over other apps.',
    'NSAccessibilityUsageDescription': 'Mimikey requires Accessibility permissions to listen for global hotkeys (F9/F10) and simulate intelligent typing.',
    'NSPrincipalClass': 'NSApplication',
    'NSHighResolutionCapable': 'True'
},

)
