#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""项目测试入口 —— 本地和 GitHub Actions 跑的是同一个。

用法 / Usage:
    python run_tests.py            # 静默，只报结果
    python run_tests.py -v         # 逐项打印

退出码 0 表示全部通过。

刻意不依赖任何第三方库，也不用 shell 重定向，
因为 GitHub Actions 在 Windows 上用 cmd 跑内联命令时，
CALL 的二次展开会把 python -c 里的 '%d' 当成参数吃掉。
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_FILES = ["jiwenfa.py", "jiwenfa_compat.py", "build.py", "run_tests.py"]

VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv
failures = []
passed = 0


def check(label, ok, detail=""):
    global passed
    if ok:
        passed += 1
        if VERBOSE:
            print("  [OK ] %s" % label)
    else:
        failures.append(("%s %s" % (label, detail)).strip())
        print("  [FAIL] %s  %s" % (label, detail))


def test_compile():
    """语法编译检查"""
    print("== 编译检查 ==")
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile"] + SRC_FILES,
        cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    check("语法编译", proc.returncode == 0,
          " ".join(proc.stdout.decode("utf-8", "replace").split()[:6]))


def test_self():
    """jiwenfa 自带的 50 项断言"""
    print("== 自检 ==")
    sys.path.insert(0, HERE)
    import jiwenfa
    n, f = jiwenfa.run_self_test(verbose=VERBOSE)
    check("自检 %d 项" % n, not f,
          "失败: %s" % "; ".join(f[:3]) if f else "")


def test_smoke():
    """菜单端到端冒烟：喂一串输入进去，确认能跑完。

    输入刻意只用 ASCII，这样无论子进程用 GBK 还是 UTF-8 解码 stdin，
    结果都一样，断言才不会因编码而误报。
    """
    print("== 菜单冒烟 ==")
    script = "\n".join([
        "2", "hello world",   # 英文加密
        "2", "ni hao",        # 拼音 + 词边界
        "2", "a,b",           # 标点规则
        "3", "0001,0003",     # 解密
        "6",                  # 跑自检
        "0",                  # 退出
    ]) + "\n"
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "jiwenfa.py")],
            input=script.encode("ascii"),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=HERE, timeout=180,
        )
    except subprocess.TimeoutExpired:
        check("菜单端到端", False, "超时")
        return
    out = proc.stdout.decode("utf-8", "replace")
    # 输出可能是 GBK，只用纯 ASCII 标记做断言，避免编码干扰。
    # 菜单里的自检结论是中文的，这里不去断言它 —— 自检本身已由 test_self() 单独跑过。
    check("菜单退出码为 0", proc.returncode == 0, "实际 %d" % proc.returncode)
    check("无异常堆栈", "Traceback" not in out,
          out.strip().splitlines()[-1] if out.strip() else "")
    check("词间空格用保留码 0661（ni hao 未塌成 nihao）", "0661" in out)
    check("标点与码紧贴（a,b -> 0001,000x）", "0001,000" in out)
    check("密文能解回原文（0001,000x -> a,b）", "a,b" in out)


def main():
    print("记文法 测试入口 / JiWenFa test runner")
    print("Python %d.%d.%d" % sys.version_info[:3])
    print("stdout 编码: %s" % (getattr(sys.stdout, 'encoding', '?') or '?'))
    print("-" * 56)
    test_compile()
    test_self()
    test_smoke()
    print("-" * 56)
    if failures:
        print("失败 %d 项 / FAILED: %d" % (len(failures), len(failures)))
        for item in failures:
            print("    - %s" % item)
        return 1
    print("全部通过 / PASSED (%d 项)" % passed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
