# -*- coding: utf-8 -*-
"""旧类名兼容垫片 —— 没有任何实现，全部转发自 jiwenfa.py。

历史背景
--------
这个文件最早叫 bbb.py，里面曾存过一份 v2.0「改进版」实现，与 jiwenfa.py
并存了两份分叉代码。同一输入（如 "a,b"）两者给出的密文空格规则还不一致，
是长期的 bug 来源。现已把实现统一收敛到 jiwenfa.py，本文件只留一个别名，
因此改名为 jiwenfa_compat.py。

它存在的唯一理由
--------------
让写于旧版本、外部脚本里的 from jiwenfa_compat import JiWenFaImproved
（早先是 from bbb import JiWenFaImproved）不至于 ImportError。
JiWenFaImproved 和 JiWenFa 是同一个类对象，不存在第二份实现。

项目内部没有任何地方 import 它 —— jiwenfa.py、build.py、.spec 都只认 jiwenfa.py。

新代码请直接：

    from jiwenfa import JiWenFa

确认项目内确实无人引用后即可删除本文件。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jiwenfa import (  # noqa: E402
    JiWenFa,
    JiWenFaError,
    out,
    run_self_test,
)

# 旧类名 = 新类名，不再有第二份实现
JiWenFaImproved = JiWenFa


def main():
    """与 jiwenfa.main 完全一致。"""
    from jiwenfa import main as _main
    return _main()


__all__ = [
    'JiWenFa', 'JiWenFaImproved', 'JiWenFaError',
    'run_self_test', 'out', 'main',
]


if __name__ == "__main__":
    main()
