# 更新日志 / Changelog

本项目所有值得注意的变更。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
Notable changes to this project. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [未发布] / Unreleased

## [0.2.0] - 2026-10-05

### 新增 / Added

- 英文支持：菜单 `2` 现可直接输入英文，文案改为「拼音/英文加密」
- English support: menu option `2` now accepts English; relabelled 「拼音/英文加密」
- 大写字母保留：新增大写码库 `0326~0651`，`NIHAO` 不再被还原成 `nihao`
- Uppercase preserved: new uppercase code range `0326~0651`
- 明文数字不再被误解码：新增数字保留码 `0681~0690`
- Literal digits no longer misdecoded: new reserved codes `0681~0690`
- 全部空白字符（29 种）改用保留码 `0652~0680`，密文中不再出现裸空白
- All 29 whitespace characters now use reserved codes `0652~0680`; ciphertext contains no bare whitespace
- 自检从「只打印」改为真断言，扩充到 50 项，覆盖码表自洽性、往返、密文格式与随机模糊测试
- Self-test now asserts instead of merely printing; expanded to 50 checks
- `README.md` 中英对照版 / bilingual README
- `LICENSE`（MIT）/ MIT license
- `run_tests.py` 测试入口：编译检查 + 自检 + 菜单端到端冒烟，本地与 CI 共用
- GitHub Actions：Linux 上 Python 3.9~3.13 + 设置 `PYTHONIOENCODING=cp936` 的 Windows 任务
- GitHub Actions: Python 3.9–3.13 on Linux, plus a Windows job with `PYTHONIOENCODING=cp936`
- `.gitattributes` 统一 UTF-8 / LF / CRLF
- `.gitattributes` normalising UTF-8 / LF / CRLF

### 修复 / Fixed

- **打包后的 exe 启动即崩溃**：源码中的 emoji 超出 Windows 中文控制台（代码页 936）
  编码范围，一句 `print` 抛 `UnicodeEncodeError`。改用 GBK 安全符号，并新增降级打印
  **The packaged exe crashed on startup**: emoji in the source cannot be encoded by the default
  Windows Chinese console (code page 936), so a single `print` raised `UnicodeEncodeError`.
- **词边界不可逆**：密文空格既作分隔符又可能来自原文，`nihao` 与 `ni hao` 解密结果相同。
  改由保留码承载原文空白
 **Word boundaries were lossy**: a ciphertext space could be either a separator or real text, so
 `nihao` and `ni hao` decoded identically. Real whitespace is now carried by reserved codes.
- **标点空格规则自相矛盾**：`jiwenfa.py` 与 `bbb.py` 两份分叉实现对同一输入给出不同密文。
  已统一为单一规则：仅「码+码」相邻才插空格
 **Punctuation spacing was inconsistent** between two divergent implementations; unified into one
 rule — a space appears only between two adjacent codes.
- **上标字符致解密崩溃**：`str.isdigit()` 对 U+00B2 返回 True，但 `int('²²²²')` 抛 `ValueError`
 **Superscripts crashed the decryptor**: `isdigit()` returns True for U+00B2 but `int()` rejects it.
- **全角数字被当成码**：`int('１２３４')` 算出 1234 并查表，导致明文数字解密成 `?`
 **Full-width digits were decoded as codes**, turning literal text into `?`.
- **换行、制表符、全角空格静默丢失**：原样进密文后又被 `isspace()` 当分隔符吞掉
 **Newlines, tabs and full-width spaces were silently dropped** on the round trip.
- **`CODE_SPACE` 取值错误**：空白码按码位排序首项是制表符，导致映射表把 `0652` 显示成空格码
 **`CODE_SPACE` pointed at the wrong character** (tab, not space), so the table display lied.
- **`build.py` 的 `--icon=NONE` 是无效参数**：PyInstaller 会去找名为 NONE 的图标文件
 **`--icon=NONE` is not a valid "no icon" directive**; PyInstaller looked for a file named NONE.
- **pypinyin 缺失时静默返回 `None`**，最终抛出难以理解的 `TypeError`
 **A missing pypinyin failed silently**, ending in a confusing `TypeError`.

### 移除 / Removed

- `bbb.py` 并入 `jiwenfa.py` 后改名为 `jiwenfa_compat.py`，仅保留旧类名别名
- `bbb.py` was merged into `jiwenfa.py` and renamed to `jiwenfa_compat.py`, now a pure alias shim
- 自检不再在程序启动时自动运行（它曾是崩溃现场），改为菜单 `6` 按需触发
- The self-test no longer runs at startup (it was where the crash happened); it is menu option `6` now

### 兼容性 / Compatibility

码表 `0000~0325` **从未改动**，所有历史密文仍可解密。新增码全部排在 `0326` 之后。
The code range `0000~0325` has never changed, so all historical ciphertext still decrypts.
All newly added codes live above `0326`.
