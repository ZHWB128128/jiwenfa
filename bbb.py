# -*- coding: utf-8 -*-
"""兼容入口文件。

历史背景：本文件曾是 v2.0 改进版，与 jiwenfa.py 并存了两份分叉实现，
同一输入（如 "a,b"）两者给出的密文空格规则不一致，是长期 bug 来源。
现实现已统一收敛到 jiwenfa.py，本文件只保留旧类名 JiWenFaImproved
作为别名，避免外部脚本 from bbb import JiWenFaImproved 报 ImportError。

新代码请直接使用 jiwenfa.JiWenFa。
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
