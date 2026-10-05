# -*- coding: utf-8 -*-
"""《记文法》加密系统

设计要点
--------
1. 递进映射：第 n 个字母占用 n 个连续数字。
   小写 a=0001、b=0002~0003 …… y=0301~0325，z 特殊独占 0000。
2. 保留码（顺延在大写之后，保证 0000~0325 的原有密文仍可解密）：
   大写 A~Y 沿用同一递进规则占用 0326~0650，Z 独占 0651；
   0652 是普通空格的保留码；其后是换行、制表符、全角空格等全部空白字符
   的保留码，再之后是字面数字 0~9 的保留码。码值连续且远小于 10000。
3. 密文中只可能出现 ASCII 数字、空白分隔符，以及原样保留的非数字字符。
4. 密文格式：每个码写 4 位；**仅当相邻两个 token 都是码时才插入空格分隔**，
   标点等原样字符与码之间一律紧贴。例："a,b" -> "0001,0003"。
5. 解密时空白一律当分隔符丢弃，明文里的空白由保留码承载，
   因此 "nihao" 与 "ni hao" 不再混淆，往返可完全还原。
"""

import random
import re
import sys

LOWER = "abcdefghijklmnopqrstuvwxyz"
UPPER = LOWER.upper()
_DIGITS = "0123456789"

# 密文结构：4 位码与单个非数字原样字符组成的序列，相邻项之间至多一个空格。
# 注意码与标点是紧贴的（"a,b" -> "0001,0003"），所以不能要求每两个 token 之间都有空格。
# 码必须写 [0-9] 而不是正则的 \d —— \d 在 Unicode 模式下同样匹配全角数字，
# 会把原样保留的"１２３４"误判成码。
_CIPHER_RE = re.compile(r'(?:[0-9]{4}|[^0-9\s])(?: ?(?:[0-9]{4}|[^0-9\s]))*')


class JiWenFaError(Exception):
    """业务异常：缺少依赖、输入非法等。"""


def out(text=''):
    """GBK 安全的打印。

    Windows 中文控制台默认代码页 936，无法编码 emoji 等字符，
    直接 print 会抛 UnicodeEncodeError 让程序当场崩溃。
    这里先原样输出，失败时按 replace 降级，保证程序不会因编码问题退出。
    """
    try:
        print(text)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, 'encoding', None) or 'ascii'
        out_retry = text.encode(enc, errors='replace').decode(enc, errors='replace')
        print(out_retry)


class JiWenFa:
    """记文法加密系统"""

    CODE_SPACE = 0        # 普通空格 ' ' 的保留码，构建后赋值
    CODE_DIGIT_BASE = 0   # 字面数字的起始码，构建后赋值
    MAX_CODE = 0          # 最大码值，构建后赋值
    WS_CHARS = ()         # 全部空白字符，构建后赋值
    WS_CODE_RANGE = (0, 0)  # 空白保留码的区间，构建后赋值

    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
        self.letter_to_range = {}    # 多选码：a~y / A~Y / z / Z
        self.fixed_to_code = {}      # 单选码：空格、字面数字 0-9
        self.number_to_letter = {}   # 反查表，解密用
        self._build_mapping()

    # ------------------------------------------------------------------ 码表

    def _assign(self, letter, codes):
        self.letter_to_range[letter] = list(codes)
        for code in codes:
            self.number_to_letter[code] = letter

    def _build_mapping(self):
        start = 1

        # 1) 小写 a~y 递进，z 特殊独占 0
        for i, letter in enumerate(LOWER):
            if letter == 'z':
                self._assign(letter, [0])
            else:
                count = i + 1
                end = start + count - 1
                self._assign(letter, range(start, end + 1))
                start = end + 1

        # 2) 大写 A~Y 沿用同一递进规则顺延，Z 特殊独占一码
        for i, letter in enumerate(UPPER):
            if letter == 'Z':
                self._assign(letter, [start])
                start += 1
            else:
                count = i + 1
                end = start + count - 1
                self._assign(letter, range(start, end + 1))
                start = end + 1

        # 3) 所有空白字符统一用保留码。
        #    密文里因此不会出现任何裸空白，解密时就能放心地把空白一律当分隔符
        #    丢弃；否则换行/制表符/全角空格会原样进入密文，解密时被 isspace
        #    吞掉，往返就丢了信息。range 上界取 0x3001 是因为全角空格 U+3000
    #    本身就是最后一个 Unicode 空白，写成 0x3000 会漏掉它。
        ws_chars = [chr(c) for c in range(0x3001) if chr(c).isspace()]
        ws_start = start
        for ch in ws_chars:
            self.fixed_to_code[ch] = start
            self.number_to_letter[start] = ch
            start += 1
        self.WS_CHARS = ws_chars
        self.WS_CODE_RANGE = (ws_start, start - 1)
        # 注意 ws_chars 按码位排序，第一个是 '\t'(U+0009) 而不是空格 U+0020，
        # 所以普通空格的码必须查表拿，不能直接拿块首 start。
        self.CODE_SPACE = self.fixed_to_code[' ']

        # 4) 字面数字用独立保留码，避免明文 4 位数字被误当成码
        self.CODE_DIGIT_BASE = start
        for digit in range(10):
            code = start + digit
            self.fixed_to_code[str(digit)] = code
            self.number_to_letter[code] = str(digit)
        start += 10

        self.MAX_CODE = start - 1

    def _codes_for(self, char):
        """返回该字符的候选码列表；返回 None 表示原样保留该字符。"""
        if char in self.letter_to_range:
            return self.letter_to_range[char]
        if char in self.fixed_to_code:
            return [self.fixed_to_code[char]]
        return None

    # -------------------------------------------------------------- 加解密

    def chinese_to_pinyin(self, chinese_text):
        """中文转拼音。

        缺少 pypinyin 时抛出 JiWenFaError —— 旧实现返回 None，
        会让调用方一路把 None 当密文用，最终抛 TypeError 而看不懂原因。
        """
        if not chinese_text:
            return ''
        try:
            from pypinyin import pinyin, Style
        except ImportError as exc:
            raise JiWenFaError(
                "缺少 pypinyin 库，无法进行中文加密。请执行：pip install pypinyin"
            ) from exc
        return ''.join(word[0] for word in pinyin(chinese_text, style=Style.NORMAL))

    def encrypt_from_chinese(self, chinese_text):
        """直接从中文加密。

        只返回密文，不往 stdout 写东西 —— 库方法带打印副作用会污染
        自检和 CI 的输出。「转换拼音」那行由菜单负责显示。
        """
        return self.encrypt_from_pinyin(self.chinese_to_pinyin(chinese_text))

    def encrypt_from_pinyin(self, pinyin_text):
        """从拼音加密。

        token 只有两类：码（4 位数字）与原样保留字符。
        只有"码 + 码"相邻时才插空格，规则单一、对中英文标点一致。
        """
        tokens = []
        prev_is_code = False

        for char in pinyin_text:
            codes = self._codes_for(char)
            if codes is None:
                tokens.append(char)
                prev_is_code = False
                continue
            if prev_is_code:
                tokens.append(' ')
            tokens.append("%04d" % random.choice(codes))
            prev_is_code = True

        return ''.join(tokens)

    def decrypt_to_pinyin(self, cipher_text):
        """解密密文到拼音。

        空格仅为分组分隔符，直接丢弃；连续 4 位数字按码表还原；
        无法识别的码降级为 '?'，让用户能看出密文有误。
        """
        result = []
        i, n = 0, len(cipher_text)
        while i < n:
            char = cipher_text[i]
            if char.isspace():
                i += 1
                continue
            # 码只可能是 ASCII 数字，必须显式限定。str.isdigit() 对全角数字
            # 和上标（U+00B2 之类）都返回 True，但 int() 前者会算出数值、
            # 后者直接抛 ValueError，两者都会把解密搞坏。
            # （注释里只用码位表示上标，因为源码全表要过 GBK 编码检查。）
            if char in _DIGITS:
                chunk = cipher_text[i:i + 4]
                if len(chunk) == 4 and all(c in _DIGITS for c in chunk):
                    result.append(self.number_to_letter.get(int(chunk), '?'))
                    i += 4
                else:
                    # 不足 4 位的孤立数字，原样保留
                    result.append(char)
                    i += 1
                continue
            result.append(char)
            i += 1

        return ''.join(result)

    # ---------------------------------------------------------------- 信息

    def show_mapping(self):
        """显示映射表"""
        out("《记文法》字符映射表")
        out("-" * 56)
        out("  小写（a~y 递进，z 特殊独占 0000）")
        for letter in LOWER:
            codes = self.letter_to_range[letter]
            if letter == 'z':
                out("  %s -> %04d   (特殊: z 独占 1 码)" % (letter, codes[0]))
            else:
                out("  %s -> %04d~%04d   (%d 种)" % (letter, codes[0], codes[-1], len(codes)))
        out("-" * 56)
        out("  大写（A~Y 顺延递进，Z 特殊独占 1 码）")
        for letter in UPPER:
            codes = self.letter_to_range[letter]
            if letter == 'Z':
                out("  %s -> %04d   (特殊)" % (letter, codes[0]))
            else:
                out("  %s -> %04d~%04d   (%d 种)" % (letter, codes[0], codes[-1], len(codes)))
        out("-" * 56)
        out("  保留码")
        out("  空白字符 -> %04d~%04d  (%d 种：空格/换行/制表符/全角空格等，密文里不留裸空白)"
            % (self.WS_CODE_RANGE[0], self.WS_CODE_RANGE[1], len(self.WS_CHARS)))
        out("    其中普通空格 ' ' -> %04d  (与分隔空格区分，保证词边界可还原)"
            % self.CODE_SPACE)
        out("  数字 0-9 -> %04d~%04d  (明文数字不再被误判为码)"
            % (self.CODE_DIGIT_BASE, self.CODE_DIGIT_BASE + 9))
        out("-" * 56)
        out("  码值总数: %d    码值上限: %04d  (4 位数字可容纳)"
            % (len(self.number_to_letter), self.MAX_CODE))

    def get_stats(self):
        """获取统计信息"""
        ranges = [len(v) for v in self.letter_to_range.values()]
        return {
            'total_mappings': len(self.number_to_letter),
            'max_code': self.MAX_CODE,
            'avg_range': sum(ranges) / len(ranges),
            'max_range': max(ranges),
            'min_range': min(ranges),
        }


# ------------------------------------------------------------------ 自检

def run_self_test(verbose=True):
    """自检：对加解密做真实断言，返回 (通过数, 失败列表)。

    旧版的"测试"只打印不断言，密文格式明明有问题也照样报成功。
    """
    jwf = JiWenFa(seed=20240101)
    failures = []
    passed = 0

    def check(name, condition, detail=''):
        nonlocal passed
        if condition:
            passed += 1
            if verbose:
                out("  [√] %s" % name)
        else:
            failures.append(("%s %s" % (name, detail)).strip())
            if verbose:
                out("  [×] %s  %s" % (name, detail))

    if verbose:
        out("● 记文法自检")

    # --- GBK 回归防护 ---
    # 历史事故：源码里用了 emoji（如 U+1F50D），Windows 中文控制台默认 GBK
    # 无法编码，打包后的 exe 一启动就 UnicodeEncodeError 崩溃。
    # 这里把整份源码扫一遍，防止再引入 GBK 编不出来的字符。
    try:
        with open(__file__, encoding='utf-8') as fp:
            bad_chars = {}
            for lineno, line in enumerate(fp, 1):
                for ch in line:
                    try:
                        ch.encode('gbk')
                    except UnicodeEncodeError:
                        bad_chars.setdefault(ch, []).append(lineno)
        check("源码不含 GBK 编不出的字符（不会在中文控制台崩溃）", not bad_chars,
              " %s" % bad_chars if bad_chars else "")
    except OSError as exc:
        if verbose:
            out("  [-] 跳过源码 GBK 扫描（%s）" % exc)

    # --- 码表结构 ---
    check("码值连续且无空洞（0~MAX_CODE 全部有定义）",
          len(jwf.number_to_letter) == jwf.MAX_CODE + 1,
          "映射 %d 个，上限 %d" % (len(jwf.number_to_letter), jwf.MAX_CODE))
    check("码值上限 < 10000（4 位可容纳）", jwf.MAX_CODE < 10000,
          "实际 %d" % jwf.MAX_CODE)
    check("原有 0000~0325 区间保持不变（历史密文仍可解密）",
          jwf.number_to_letter[0] == 'z' and jwf.number_to_letter[1] == 'a'
          and jwf.number_to_letter[325] == 'y')
    check("正查表与反查表自洽",
          all(code in jwf.number_to_letter
              for codes in jwf.letter_to_range.values() for code in codes))
    # 回归：ws_chars 按码位排序，首项是 '\t' 而非空格，早期版本把 CODE_SPACE
    # 直接赋成块首，导致映射表把制表符的码显示成"空格"的码。
    check("CODE_SPACE 确实是空格 ' ' 的码",
          jwf.CODE_SPACE == jwf.fixed_to_code[' ']
          and jwf.number_to_letter[jwf.CODE_SPACE] == ' '
          and jwf.WS_CHARS[0] != ' ',
          "CODE_SPACE=%d, 实际空格码=%d, 首空白=%r"
          % (jwf.CODE_SPACE, jwf.fixed_to_code[' '], jwf.WS_CHARS[0]))
    check("全部空白都走保留码",
          all(ch in jwf.fixed_to_code for ch in jwf.WS_CHARS)
          and jwf.WS_CODE_RANGE[1] - jwf.WS_CODE_RANGE[0] + 1 == len(jwf.WS_CHARS))

    # --- 往返还原 ---
    # 后三组是回归用例，对应曾经真实存在的缺陷：
    #   全角数字/上标曾被 int() 当成码，或直接把解密搞崩；
    #   换行、制表符、全角空格曾原样进密文又在解密时被 isspace 吞掉。
    cases = [
        "nihao", "ni hao", "nihao，shijie。", "z", "zhongguo", "aoe",
        "NIHAO", "Ni Hao", "1234", "abc1234", "wo ai zhong guo!",
        "zhe,shi yi ge.you 'duo zhong' biao,dian de;ce shi.",
        "１２３４", "\u00b2\u00b2\u00b2\u00b2", "ni\nhao",
        "ni\thaо".replace("\u0445", "x"), "ni\u3000hao", "\u2460" + "2", "a\u00b7b",
    ]
    for src in cases:
        back = jwf.decrypt_to_pinyin(jwf.encrypt_from_pinyin(src))
        check("往返还原 %r" % src, back == src, "得到 %r" % back)

    # --- 词边界 ---
    c1 = jwf.encrypt_from_pinyin("nihao")
    c2 = jwf.encrypt_from_pinyin("ni hao")
    check("'nihao' 与 'ni hao' 密文不同", c1 != c2)
    check("'nihao' 与 'ni hao' 解密后仍可区分",
          jwf.decrypt_to_pinyin(c1) != jwf.decrypt_to_pinyin(c2))

    # --- 密文里不应出现裸空白 ---
    # 所有空白都走保留码，密文中只允许出现充当分组分隔符的普通空格。
    # 否则解密时 isspace 会把原样保留的换行/制表符/全角空格一并吞掉。
    leak = set()
    for src in cases:
        for ch in jwf.encrypt_from_pinyin(src):
            if ch.isspace() and ch != ' ':
                leak.add((src, ch))
    check("密文中不出现裸空白（空白全部走保留码）", not leak, " %s" % sorted(leak)[:3])

    # --- 密文格式 ---
    for src in ["a,b", "a，b", "a . b", "a, b", "ni hao"]:
        cipher = jwf.encrypt_from_pinyin(src)
        check("空格只出现在码与码之间 %r" % src,
              re.search(r'(?<=[^0-9]) | (?=[^0-9])', cipher) is None,
              "密文=%r" % cipher)
        check("密文结构合法 %r" % src,
              _CIPHER_RE.fullmatch(cipher) is not None, "密文=%r" % cipher)
        groups = re.findall(r'\d{4}', cipher)
        check("码组全部可查 %r" % src,
              all(int(g) in jwf.number_to_letter for g in groups))

    # --- 边界与异常 ---
    check("空串加密", jwf.encrypt_from_pinyin("") == "")
    check("空串解密", jwf.decrypt_to_pinyin("") == "")
    check("未知码降级为 '?'", jwf.decrypt_to_pinyin("9999") == "?")
    check("不足 4 位的孤立数字原样保留", jwf.decrypt_to_pinyin("123") == "123")

    # --- 中文路径 ---
    try:
        import pypinyin  # noqa: F401
        has_pypinyin = True
    except ImportError:
        has_pypinyin = False

    if has_pypinyin:
        cipher = jwf.encrypt_from_chinese("你好，世界。")
        back = jwf.decrypt_to_pinyin(cipher)
        check("中文往返还原", back == "nihao，shijie。", "得到 %r" % back)
    else:
        if verbose:
            out("  [-] 跳过中文用例（未安装 pypinyin）")
        try:
            jwf.encrypt_from_chinese("你好")
            check("缺 pypinyin 时应抛 JiWenFaError", False, "竟然没有抛异常")
        except JiWenFaError:
            check("缺 pypinyin 时抛出 JiWenFaError", True)

    # --- 随机模糊测试 ---
    random.seed(99)
    pool = list(LOWER + UPPER) + list(" ，,。.!123")
    bad = 0
    for _ in range(2000):
        text = ''.join(random.choice(pool) for _ in range(random.randint(0, 40)))
        if jwf.decrypt_to_pinyin(jwf.encrypt_from_pinyin(text)) != text:
            bad += 1
    check("2000 组随机文本往返 100% 还原", bad == 0, "失败 %d 组" % bad)

    if verbose:
        out("-" * 56)
        if failures:
            out("  [×] 自检未通过：通过 %d 项，失败 %d 项" % (passed, len(failures)))
            for item in failures:
                out("      - %s" % item)
        else:
            out("  [√] 自检全部通过：%d 项" % passed)
    return passed, failures


# ------------------------------------------------------------------ 主程序

def _harden_stdio():
    """让标准输入输出在编码不匹配时降级而不是崩溃。

    控制台代码页（936）、重定向的文件、管道三者的编码经常对不上，
    strict 模式下 stdin 遇到解不开的字节会抛 UnicodeDecodeError 直接退出。
    """
    for stream in (sys.stdin, sys.stdout):
        try:
            stream.reconfigure(errors='replace')
        except (AttributeError, ValueError, OSError):
            pass  # 被重定向成不支持 reconfigure 的对象时忽略


def main():
    _harden_stdio()
    jwf = JiWenFa()

    while True:
        out()
        out("=" * 56)
        out("            《记文法》加密系统 v2.0")
        out("=" * 56)
        out("  1. 中文加密")
        out("  2. 拼音/英文加密")
        out("  3. 密文解密")
        out("  4. 显示映射表")
        out("  5. 显示统计信息")
        out("  6. 运行自检")
        out("  0. 退出系统")
        out("=" * 56)

        try:
            choice = input("请选择 (0-6): ").strip()
        except (EOFError, KeyboardInterrupt):
            out()
            out("感谢使用《记文法》！")
            return

        if choice == '0':
            out("感谢使用《记文法》！")
            return

        if choice == '1':
            out()
            out("→ 【中文加密模式】")
            text = input("请输入中文: ").strip()
            if not text:
                out("  [×] 输入不能为空！")
                continue
            try:
                pinyin = jwf.chinese_to_pinyin(text)
                cipher = jwf.encrypt_from_pinyin(pinyin)
            except JiWenFaError as exc:
                out("  [×] %s" % exc)
                continue
            out("  转换拼音: %s" % pinyin)
            out("  [√] 记文密文: %s" % cipher)

        elif choice == '2':
            out()
            out("→ 【拼音/英文加密模式】")
            text = input("请输入拼音或英文: ").strip()
            if not text:
                out("  [×] 输入不能为空！")
                continue
            cipher = jwf.encrypt_from_pinyin(text)
            out("  [√] 记文密文: %s" % cipher)

        elif choice == '3':
            out()
            out("→ 【密文解密模式】")
            text = input("请输入密文: ").strip()
            if not text:
                out("  [×] 输入不能为空！")
                continue
            plain = jwf.decrypt_to_pinyin(text)
            if '?' in plain:
                out("  ※ 密文含无法识别的码（已还原为 '?'），请检查有无错字或漏字")
            out("  [√] 解密结果: %s" % plain)

        elif choice == '4':
            out()
            jwf.show_mapping()

        elif choice == '5':
            out()
            out("→ 【统计信息】")
            stats = jwf.get_stats()
            out("  映射总数: %d" % stats['total_mappings'])
            out("  最大码值: %04d" % stats['max_code'])
            out("  平均范围: %.2f" % stats['avg_range'])
            out("  最大范围: %d" % stats['max_range'])
            out("  最小范围: %d" % stats['min_range'])

        elif choice == '6':
            out()
            run_self_test()

        else:
            out("  [×] 无效选择！请输入 0-6")


if __name__ == "__main__":
    main()
