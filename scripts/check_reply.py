#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the meta-knowledge-prompt-system contributors
"""发送前模板硬校验（规则：两行起头长度上限＋关键判据实测值硬校验）。

把「两行起头 / 查证行 / 自查结论 / 关键判据实测值」从靠自觉变成可执行的闸门。
用法:
  python scripts/check_reply.py <reply.txt>     # 校验一份回复草稿
  cat reply.txt | python scripts/check_reply.py # 从 stdin 读
  python scripts/check_reply.py --template      # 打印合规模板
退出码: 0=PASS（可发）, 1=FAIL（拦截，不许发）
"""
import re
import sys

MAX_HEAD = 60      # 两行起头合计字数上限（A2）
MAX_SELFCHECK = 80 # 自查结论压成一行（A2）

TEMPLATE = """【优化版】<一句话写清目标与硬约束>
【查证行】<查了哪个源／哪张卡，一行写完，与上句合计不超过60字>
<正文：现在到哪了 / 卡在哪 / 需要你做什么，三句话，大白话＋术语括注>
【自查清单】档位= 卡= 关键判据实测值=<填实际数值，不许留空> 验收=<对着哪条> 回填=是/否
【自查结论】对照优化版——两行起头 ✓ 查证实写 ✓ 实测值已填 ✓；差：无
"""


def check(text):
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    results = []

    def add(name, ok, why=""):
        results.append((name, bool(ok), why))

    add("两行起头存在", len(lines) >= 2,
        "前两行不足，需「优化版 → 查证行 → 结果」" if len(lines) < 2 else "")
    if len(lines) >= 2:
        # 行首标记判定，避免「没有查证行」这类否定句被误判为通过
        add("查证行在位", bool(re.match(r"^(【查证行】|查证[:：]|依据[:：]|查了[:：])", lines[1])),
            "第二行须以【查证行】/查证:/依据: 开头，光提到「查证」二字不算")
        head_plain = re.sub(r"【[^】]*】", "", lines[0] + lines[1])
        add("两行合计 ≤%d 字" % MAX_HEAD, len(head_plain) <= MAX_HEAD,
            "实测 %d 字" % len(head_plain))
    # A6：必须填实际测量值，占位符/「待填」/只写卡号一律拦截
    m = re.search(r"关键判据实测值\s*[=:：]\s*([^\s，,;；】]+)", text)
    val = m.group(1) if m else ""
    add("关键判据实测值已填（A6）", bool(val) and not re.search(r"[<填待]|占位|xxx|XXX", val),
        "须写实际测量值（如 1024），不许留 <填...>、待填，也不许只写卡号")
    sc = [l for l in lines if re.match(r"^(【自查结论】|自查结论[:：])", l)]
    add("自查结论一行", bool(sc) and len(sc[0]) <= MAX_SELFCHECK,
        "须有以【自查结论】开头的一行，长度 ≤%d 字" % MAX_SELFCHECK)
    return results


def main():
    if "--template" in sys.argv:
        print(TEMPLATE)
        return 0
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        try:
            text = open(sys.argv[1], encoding="utf-8").read()
        except OSError as e:
            print("读取失败:", e)
            return 2
    else:
        text = sys.stdin.read()
    if not text.strip():
        print("空输入")
        return 2
    rs = check(text)
    for name, ok, why in rs:
        print("  %s %-28s %s" % ("✓" if ok else "✗", name, "" if ok else why))
    bad = [n for n, ok, _ in rs if not ok]
    print("\n%s  %d/%d 通过" % ("PASS 可发" if not bad else "FAIL 拦截", len(rs) - len(bad), len(rs)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
