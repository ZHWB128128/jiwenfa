# -*- coding: utf-8 -*-
"""一键打包：pyinstaller --clean build.py"""

import PyInstaller.__main__

PyInstaller.__main__.run([
    'jiwenfa.py',
    '--onefile',             # 打包成单个 exe
    '--clean',               # 每次清理上次的 build 缓存，避免残留
    '--noconfirm',           # 覆盖 dist 下已存在的 exe
    '--console',             # 显示控制台窗口
    '--name=记文法加密器',   # 程序名称
    # 修正：'--icon=NONE' 并不是"不要图标"，PyInstaller 会去找名为 NONE 的
    # 图标文件而报错。默认不传 --icon 即为无图标。
    '--hidden-import=pypinyin',   # pypinyin 在函数内延迟导入，显式声明更稳妥
    '--collect-data=pypinyin',    # 附带其词典数据文件，保证冻结后中文可用
])
