# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all
block_cipher = None

# 导入 PyInstaller 的收集功能

# 初始化空的数据和二进制文件列表
datas = []
binaries = []
hiddenimports = []

# 列出所有需要自动处理的依赖库
packages = [
    'uiautomator2',
    'easyocr'
]

# 使用 collect_all 自动收集每个包的资源
for package in packages:
    pkg_data, pkg_binaries, pkg_hiddenimports = collect_all(package)
    datas += pkg_data
    binaries += pkg_binaries
    hiddenimports += pkg_hiddenimports

# 添加手动指定的数据目录
datas += [('assets', 'assets'),('fonts', 'fonts')]

# 主脚本路径
main_script = 'main.py'

a = Analysis([main_script],
             pathex=['.'],
             binaries=binaries,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
             hooksconfig={},
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
          name='大霸茶馆v${version}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          icon='assets/icon_exe.ico',
          console=False)
