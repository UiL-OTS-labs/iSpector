# -*- mode: python -*-

block_cipher = None

#added files Not needed to build, but to run the program.
#               ( path to file              , output directory)
added_files = [ ('./logo/iSpectorLogo.ico'  ,'logo'),
                ('iSpectorLogo.svg'         ,'.'),
                ('./images/error.svg'       , './images'),
                ('./images/warning.svg'     , './images')
                ]
                

a = Analysis(['iSpector.py'],
             pathex=['C:\\Users\\Duijn119\\Desktop\\testsmi'],
             binaries=None,
             datas=added_files,
             hiddenimports=['scipy.linalg.cython_blas', 'scipy.linalg.cython_lapack'],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='iSpector',
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='iSpector')
