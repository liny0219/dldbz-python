# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import glob
import os
block_cipher = None

# 初始化空的数据和二进制文件列表
datas = []
binaries = []  # 只打包加密后的 .pyd 文件
hiddenimports = []

# 列出所有需要自动处理的依赖库
packages = [
    'uiautomator2'
]

# 获取 build/lib 目录下的所有目录
for dir_path in glob.glob('build/lib/*/', recursive=False):
    # 计算目标路径
    target_path = os.path.relpath(dir_path, 'build/lib')
    binaries.append((dir_path, target_path))

# 使用 collect_all 自动收集每个包的资源
for package in packages:
    pkg_data, pkg_binaries, pkg_hiddenimports = collect_all(package)
    datas += pkg_data
    binaries += pkg_binaries
    hiddenimports += pkg_hiddenimports

# 添加手动指定的数据目录
datas += [('assets', 'assets'), ('fonts', 'fonts')]

# 主脚本路径
main_script = 'main.py'

a = Analysis([main_script],
             pathex=['build/lib'],
             binaries=binaries,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=['*.py'],
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
