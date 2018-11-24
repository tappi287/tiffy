# -*- mode: python -*-

block_cipher = None

tiffy_files = [('bin/exiftool', 'bin'),
               ('bin/lib', 'bin/lib'),
               ('locale/de/LC_MESSAGES/*.mo', 'locale/de/LC_MESSAGES'),
               ('locale/en/LC_MESSAGES/*.mo', 'locale/en/LC_MESSAGES'),
               ('ui/gui_resource*', 'ui'),
               ('ui/tiffy*', 'ui'),
               ('license.txt', '.'),]

a = Analysis(['tiffy.py'],
             pathex=['/Users/stefan/PycharmProjects/tiffy'],
             binaries=[],
             datas=tiffy_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='tiffy',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
app = BUNDLE(exe,
             name='tiffy.app',
             icon='ui/AppIcon.icns',
             bundle_identifier=None)
