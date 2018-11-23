# -*- mode: python -*-

block_cipher = None

tiffy_files = [('locale/de/LC_MESSAGES/*.mo', 'locale/de/LC_MESSAGES'),
               ('locale/en/LC_MESSAGES/*.mo', 'locale/en/LC_MESSAGES'),
               ('ui/gui_resource*', 'ui'),
               ('ui/tiffy*', 'ui'),
               ('license.txt', '.'),]

a = Analysis(['tiffy.py'],
             pathex=['./modules'],
             binaries=[('bin/*', 'bin'),],
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
          [],
          exclude_binaries=True,
          name='tiffy',
          icon='./ui/Icon.ico',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='tiffy')
