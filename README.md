# 记文法加密系统 / JiWenFa Cipher

**中文 · 拼音 · 英文替音工具 / A Chinese, pinyin and English substitution cipher**

把中文（经 pypinyin 转拼音）、拼音或任意英文，按自定的「记文法」码表替换成 4 位数字串。  
Replaces Chinese (converted via pypinyin), pinyin, or plain English with 4-digit codes using a custom lookup table.

> ### ⚠️ 这不是加密 / This is NOT encryption
>
> 记文法是**公开码表的替音编码**：没有密钥，码表直接写在源码里，拿到码表就等于拿到解密能力，也没有做抗频率分析设计。  
JiWenFa is a **public-table substitution cipher**: there is no key, the table is right there in the source, and it is not designed to resist frequency analysis.
>
> 请只用它做**个人备忘、玩梗、避免被一眼看懂的社交内容**。真正需要保密的内容，请用 AES 等成熟算法，不要用本项目。  
Use it for **personal notes, jokes, and casual content you do not want read at a glance**. For anything that must actually stay secret, use a mature cipher such as AES — not this project.

---

## 快速开始 / Quick Start

```bash
pip install pypinyin     # 仅「中文加密」需要 / only for Chinese input
python jiwenfa.py        # 运行交互式菜单 / run the interactive menu
python build.py          # 打包成 dist\记文法加密器.exe / build a single-file exe
```

| 项 / Item | 说明 / Detail |
| --- | --- |
| Python | **3.9 及以上**，CI 在 3.9 ~ 3.13 上验证 / **3.9+**, verified on 3.9–3.13 |
| 依赖 / Dependency | `pypinyin`，仅中文加密需要，其余功能零依赖 / only for Chinese input |
| 构建产物 / Artifacts | `build/`、`dist/` 已在 `.gitignore` 排除，不进版本库 |

---

## 菜单 / Menu

| 选项 / Option | 功能 / What it does |
| --- | --- |
| `1` | 中文加密 → pypinyin → 加密 / Chinese → pinyin → cipher |
| `2` | 拼音 / 英文加密 / Pinyin / English → cipher |
| `3` | 密文解密 → 拼音或英文 / cipher → plaintext |
| `4` | 显示映射表 / print the full code table |
| `5` | 显示统计信息 / print statistics |
| `6` | 运行自检（50 项断言）/ run the self-test (50 assertions) |
| `0` | 退出系统 / quit |

### 用法示例 / Examples

**拼音 / Pinyin**

```text
1  输入: 你好，世界。
   拼音: nihao，shijie。
   密文: 0096 0044 0029 0001 0106，0182 0029 0042 0046 0037 0012。

2  输入: ni hao
   密文: 0093 0043 0661 0033 0001 0114
        中间的 0661 是「词间空格」的保留码，所以 ni hao 不会被还原成 nihao
        0661 is the reserved code for a word space, so "ni hao" never collapses to "nihao"

2  输入: a,b
   密文: 0001,0003          标点与码之间不留空格 / punctuation stays tight against the codes

3  输入: 0001,0003
   明文: a,b
```

**英文 / English**

菜单 `2` 直接输入英文即可，无需任何额外设置。  
Just type English into menu option `2`. No extra setup needed.

```text
2  输入: hello world
   密文: 0034 0012 0073 0077 0106 0661 0271 0107 0165 0076 0007

2  输入: Hello, World!
   密文: 0357 0011 0068 0073 0112,0661 0586 0107 0171 0073 0007!

2  输入: I don't think it's ready.
   密文: 0365 0661 0009 0114 0099'0201 0661 0200 0030 0038 0100 0062

2  输入: Python 3.14 was released in 2026.
   密文: 0457 0320 0206 0036 0107 0105 0661 0684.0682 0685 0661 0276
```

大小写、标点、缩写撇号、邮箱符号、小数点全部原样保留并可完整还原。  
Letter case, punctuation, apostrophes, `@`, and decimal points all survive a round trip.

---

## 码表设计 / Code Table Design

### 1. 递进映射 / Progressive mapping

第 n 个字母占用 n 个连续码，位置越靠后可随机选择的码越多。  
The *n*-th letter occupies *n* consecutive codes, so later letters have more random choices.

| 字母 | 码值 | 种数 |  | 字母 | 码值 | 种数 |
| --- | --- | --- | --- | --- | --- | --- |
| a | 0001 | 1 |  | n | 0092~0105 | 14 |
| b | 0002~0003 | 2 |  | o | 0106~0120 | 15 |
| c | 0004~0006 | 3 |  | p | 0121~0136 | 16 |
| d | 0007~0010 | 4 |  | q | 0137~0153 | 17 |
| e | 0011~0015 | 5 |  | r | 0154~0171 | 18 |
| f | 0016~0021 | 6 |  | s | 0172~0190 | 19 |
| g | 0022~0028 | 7 |  | t | 0191~0210 | 20 |
| h | 0029~0036 | 8 |  | u | 0211~0231 | 21 |
| i | 0037~0045 | 9 |  | v | 0232~0253 | 22 |
| j | 0046~0055 | 10 |  | w | 0254~0276 | 23 |
| k | 0056~0066 | 11 |  | x | 0277~0300 | 24 |
| l | 0067~0078 | 12 |  | y | 0301~0325 | 25 |
| m | 0079~0091 | 13 |  | **z** | **0000** | 1 |

`z` 特殊：独占 `0000`。它排在最后又只需要 1 个码，用 `0000` 让密文更好读。  
`z` is special and takes `0000` alone — it is last in the alphabet and needs only one code.

小写占满 `0000~0325`。大写 `A~Y` 用**完全相同的递进规则整体顺延 325**：  
Lowercase fills `0000~0325`. Uppercase `A~Y` uses **the exact same progression, offset by 325**:

| 大写 | A | B | … | Y | Z |
| --- | --- | --- | --- | --- | --- |
| 码值 | 0326 | 0327~0328 | … | 0626~0650 | 0651 |

### 2. 保留码 / Reserved codes

排在所有字母之后。码值连续，共 **691** 个，最大 `0690`，4 位数字足够容纳。  
They come after every letter. Codes are contiguous: **691** in total, the largest is `0690`.

| 用途 / Purpose | 码值 / Codes | 说明 / Why |
| --- | --- | --- |
| 空白字符（29 种） | 0652~0680 | 含空格 `0661`、制表符、换行、全角空格 U+3000 等 |
| 字面数字 0-9 | 0681~0690 | 明文里的数字不再被误判成码 |

这两个块各自堵掉一类真实缺陷：  
Each block closes off a real class of defect:

- **空白码**：密文里若直接出现空格，它既可能是分组分隔符、也可能来自原文，`nihao` 和 `ni hao` 就会解成一样。改用保留码承载原文空白后，解密时就能放心丢弃所有分隔空格；同时密文里不再有裸空白，解密也不会漏掉换行、制表符、全角空格。  
  **Whitespace codes**: a literal space in the ciphertext could be either a separator or real text, so `nihao` and `ni hao` decoded identically. Encoding real whitespace as reserved codes lets the decryptor discard every separator safely — and since the ciphertext then contains no bare whitespace, newlines, tabs and full-width spaces no longer get lost either.
- **数字码**：明文里的 `1234` 原本会原样穿过加密器，解密时被当成码表索引而变成 `?`。现在所有 ASCII 数字一律编码。  
  **Digit codes**: a literal `1234` used to pass through untouched and then be decoded as a table index, turning into `?`. All ASCII digits are now encoded.

### 3. 兼容旧密文 / Backward compatibility

`0000~0325` 这个区间**一个字都没有改过**，早期版本产生的密文至今仍可解密。  
The range `0000~0325` has never changed, so ciphertext produced by earlier versions still decrypts today.

新增的大写、空白、数字码全部排在 `0326` 之后，不会挤占历史区间。  
All newly added codes live above `0326` and never collide with the historical range.

---

## 密文格式 / Cipher Format

- 每个码写满 4 位，前导 0 补齐 / every code is exactly 4 digits, zero-padded
- **只有「码 + 码」相邻时才插一个空格作分隔** / a single space separates two adjacent **codes**
- 标点、符号等原样字符与码之间一律紧贴 / punctuation sits flush against the codes

这条规则同时覆盖中英文标点，不会出现「逗号前有空格、后没有」这类不一致：  
One rule covers both ASCII and full-width punctuation, so behaviour never depends on which mark was typed:

```text
a,b    ->  0001,0002
a，b   ->  0001，0002
a . b  ->  0001 0661.0661 0002
```

同一字母每次落在区间内哪个码是**随机**的，所以上面只是其中一种可能结果。  
Which code a letter picks from its range is **random**, so the above is just one possible result.

解密时空白一律丢弃，因此手工换行、多打的空格都不影响结果；无法识别的码降级成 `?`，一眼就能看出密文有错字。  
On decrypt all whitespace is discarded, so hand-wrapped or sloppy ciphertext still works; an unrecognised code degrades to `?` so typos are visible at a glance.

### 关于英文的说明 / A note on English

同一套码表直接用于英文，但**递进映射和英语字母频率正好相反**：  
The same table works for English, but **the progressive mapping runs against English letter frequencies**:
英语最高频的 `t` 有 20 个码（最长 100 字符），而低频的 `a` 只有 1 个码（5 字符）。  
the most frequent letter `t` gets 20 codes (up to 100 characters), while `a` gets just one (5 characters).

后果是密文偏长，且码长本身泄露了字母频率。加密逻辑无需改动即可用，但如果你的主要用途是英文，**按频率重排码表**会显著更短。  
The result is longer ciphertext that leaks letter frequency through code length. It works as-is, but a frequency-ordered table would be far more compact for English-heavy use.

膨胀率参考：拼音约 **4.7 倍**，英文约 **4.8 倍**。  
Rough expansion: about **4.7x** for pinyin, **4.8x** for English.

---

## 安全边界 / Security Boundaries

| 项目 / Item | 说明 / Detail |
| --- | --- |
| 无密钥 / No key | 码表写死在源码里且公开。拿到码表 = 拥有解密能力 / The table is public. Having it *is* having the decryption |
| 非密码学 / Not cryptography | 没有密钥派生、没有完整性校验、没有抗频率分析 / No key derivation, no integrity protection, no frequency-analysis resistance |
| 弱掩盖 / Weak masking | 同字母多码能打散「相同字母得相同码」的特征，样本一多统计规律仍会显现 / It breaks the "same letter, same code" tell, but statistics still leak with enough text |
| 原样字符 / Pass-through chars | 标点原样出现；**全角数字 `１２３４` 也不加密**，码表只收录 ASCII 字符 / Punctuation appears verbatim, and **full-width digits like `１２３４` are not encrypted** — the table is ASCII-only |

---

## 编码与平台 / Encoding & Platforms

- 界面符号全部使用 GBK 可编码字符（`● √ × ※ →`）。  
  All UI symbols are GBK-encodable.
- **不要往源码里加 emoji。** Windows 中文控制台默认代码页 936 编不出 emoji，一句 `print` 就会抛 `UnicodeEncodeError` 让程序直接崩溃。这个坑本项目踩过一次：打包后的 exe 一启动就崩。自检里的源码 GBK 全表扫描就是为了防这个回归。  
  **Do not add emoji to the source.** The default Windows Chinese console is code page 936, which cannot encode emoji; a single `print` then raises `UnicodeEncodeError` and kills the program. This project hit exactly that bug — the packaged exe crashed on startup. The self-test scans the whole source file to prevent a regression.
- `out()` 在编码失败时按 `replace` 降级输出，保证程序不会因字符编码退出。  
  `out()` falls back to `replace`, so a printing problem can never kill the program.
- 标准输入输出统一 `errors='replace'`，控制台、管道、文件三种来源都不会崩。  
  Standard streams use `errors='replace'`, so console, pipe and file input are all safe.

---

## 测试 / Testing

```bash
python run_tests.py        # 完整测试：编译 + 自检 + 菜单冒烟
python run_tests.py -v     # 逐项打印

python jiwenfa.py          # 交互式运行后选菜单 6 可单独跑自检
```

源码环境跑 **50 项**断言；打包后的 exe 内跑 **49 项**（少了一项：冻结环境没有 `.py` 源文件，源码 GBK 扫描会自动跳过）。  
**50 assertions** run from source; **49** inside the packaged exe (the missing one is the source-GBK scan, skipped because a frozen exe has no source file).

覆盖范围 / Coverage:

- 码表连续性、正反查自洽、历史区 `0000~0325` 未被破坏
- 往返还原，含全角数字、上标字符、换行、制表符、全角空格等回归用例
- 词边界可区分（`nihao` ≠ `ni hao`）、大小写保留
- 密文结构合法、空格只出现在码与码之间、密文中不出现裸空白
- 2000 组随机文本往返 / 2000 random round trips
- 源码 GBK 可编码性（防 emoji 回归）
- `CODE_SPACE` 取值正确（曾因按码位排序首项是制表符而显示错误）

GitHub Actions 会在每次 push / PR 自动跑 `run_tests.py`：Linux 上 Python 3.9 ~ 3.13，以及一个设置了 `PYTHONIOENCODING=cp936` 的 Windows 任务，用来复现真实中文控制台。  
GitHub Actions runs these on every push and pull request: Python 3.9–3.13 on Linux, plus a Windows job with `PYTHONIOENCODING=cp936` to reproduce a real Chinese console.

---

## 项目结构 / Project Structure

```text
README.md            本文件 / this file
CHANGELOG.md         更新日志 / changelog
LICENSE              MIT 许可证 / MIT license
jiwenfa.py           唯一实现：码表 + 加解密 + 菜单 + 自检
                     the only implementation: table, cipher, menu, self-test
run_tests.py          测试入口：编译检查 + 自检 + 菜单端到端冒烟
jiwenfa_compat.py    兼容垫片（原名 bbb.py），仅保留旧类名 JiWenFaImproved 别名，
                     项目内部无人引用 / legacy alias shim, unused internally
build.py             PyInstaller 打包脚本 / packaging script
记文法加密器.spec      构建配置，由 build.py 自动重新生成
                     build config, regenerated by build.py
.github/workflows/   自动化测试 / CI
```

新增功能请只改 `jiwenfa.py`。  
Add new features to `jiwenfa.py` only.

---

## 常见问题 / FAQ

**Q: 密文变长了正常吗？** 每个字母固定占 5 个字符（4 位码 + 分隔空格），所以 4~5 倍膨胀是设计使然，不是 bug。  
Yes. Each letter takes a fixed 5 characters (4-digit code + separator), so 4–5x expansion is by design, not a bug.

**Q: 为什么 `--icon=NONE` 被去掉了？** PyInstaller 没有「无图标」这个参数值，`--icon=NONE` 会被当成去找一个名为 NONE 的图标文件；默认不传 `--icon` 即为无图标。  
PyInstaller has no "no icon" value — `--icon=NONE` makes it look for a file literally named NONE. Omitting `--icon` means no icon.

**Q: 中文加密报「缺少 pypinyin 库」？** 执行 `pip install pypinyin`。这个依赖只影响菜单 `1`，拼音/英文加密和解密都不需要它；打包时 `build.py` 已用 `--collect-data=pypinyin` 带上词典数据。  
Run `pip install pypinyin`. It only affects option `1`; `build.py` bundles pypinyin's dictionary via `--collect-data=pypinyin`.

**Q: 能自定义码表吗？** 可以，改 `JiWenFa._build_mapping()`。但要让保留码避开小写字母的 `0000~0325`，否则旧密文会解错。  
Edit `JiWenFa._build_mapping()`, but keep reserved codes above `0325` or old ciphertext will decode incorrectly.

**Q: 加密用了随机码，同一段文字两次结果不同，还能解密对吗？** 能。每个字母的多个码全部映射回同一个字母，解密只看「这个码属于哪个字母」。  
Yes. Every code in a letter's range maps back to that letter, so decryption only asks which letter a code belongs to.

---

## License

MIT © 2026 ZHWB128128
