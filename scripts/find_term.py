#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the meta-knowledge-prompt-system contributors
# Licensed under the MIT License; see LICENSE.md for the full text.
"""AI元知识技能词典检索器（三层：问题类型索引→方法卡→名词表，另存长期原则）。
用法:
  find_term.py <关键词>       全文检索（问题类型/方法卡/名词/原则）
  find_term.py --index        问题类型索引：这个问题属于哪类、调哪张卡
  find_term.py --methods      方法卡简表
  find_term.py --card <ID>    调出某张方法卡全文及其名词（如 --card M001）
  find_term.py --principles   全部长期原则
  find_term.py --all          全部条目简表
  find_term.py --flows        流程卡（编排层）简表
  find_term.py --flow <ID>    调出某张流程卡全文（如 --flow F001）
数据: 同目录 terms.json，按 schema 按需追加，不预先穷举。
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(_HERE, "terms.json")
if not os.path.exists(DATA):
    DATA = os.path.join(_HERE, "..", "dictionary", "terms.json")


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def method_by_id(d, mid):
    for m in d["methods"]:
        if m["id"] == mid:
            return m
    return None


def show_card(d, m, full=True):
    print("【方法卡 %s·%s】" % (m["id"], m["name"]))
    print("  解决什么问题: %s" % m["solves"])
    if full:
        print("  触发条件: %s" % m["trigger"])
        print("  核心步骤: %s" % m["steps"])
        print("  判断标准: %s" % m["criteria"])
        if m.get("origin"):
            print("  原初问题: %s" % m["origin"])
            print("  前提假设: %s" % m["premise"])
            print("  费曼自述: %s" % m["feynman"])
        print("  常见误区: %s" % m["pitfalls"])
        print("  来源/置信度: %s / %s（更新 %s）" % (m["source"], m["confidence"], m["updated"]))
        if m.get("parent"):
            print("  上位: %s" % m["parent"])
        if m.get("related"):
            print("  关联方法: %s" % ", ".join(m["related"]))
        for tid in m["terms"]:
            for t in d["terms"]:
                if t["id"] == tid:
                    print("  名词 %s·%s: 代表 %s；在该方法中的作用: %s" % (t["id"], t["name"], t["represents"], t["role"]))


def show_principle(p):
    print("【原则 %s·%s】%s" % (p["id"], p["title"], p["text"]))
    print("  适用范围: %s" % p["scope"])
    print("  触发条件: %s" % p["trigger"])
    print("  执行动作: %s" % p["actions"])
    if p.get("relation"):
        print("  与现有规则关系: %s" % p["relation"])


def list_flows(d, full_id=None):
    for fl in d.get("flows", []):
        if full_id:
            if fl["id"] != full_id:
                continue
            print("【流程卡 %s·%s】" % (fl["id"], fl["name"]))
            print("  解决什么问题: %s" % fl["solves"])
            print("  触发条件: %s" % fl["trigger"])
            print("  来源: %s / %s" % (fl["source"], fl["confidence"]))
            for st in fl["steps"]:
                print("  %2d) [%s] %s" % (st["n"], st["card"], st["action"]))
                print("       检查点: %s" % st["checkpoint"])
            print("  冲突裁决: %s" % fl["conflict_policy"])
            print("  验收标准: %s" % fl["acceptance"])
            return
        print("%s·%s — %s（%d 步）" % (fl["id"], fl["name"], fl["solves"], len(fl["steps"])))
    if full_id:
        print("没有这张流程卡")
    else:
        print("共 %d 张流程卡" % len(d.get("flows", [])))


def main():
    d = load()
    args = sys.argv[1:]
    if args and args[0] == "--flows":
        list_flows(d)
        return
    if args and args[0] == "--flow":
        list_flows(d, args[1] if len(args) > 1 else None)
        return
    if not args or args[0] == "--all":
        for row in d["problem_index"]:
            m = method_by_id(d, row["method_id"])
            if m:
                print("%s → %s·%s（%s）" % (row["type"], m["id"], m["name"], row["scene"]))
            else:
                print("%s → 待建（%s）" % (row["type"], row["scene"]))
        print("共 %d 类问题 / %d 张方法卡 / %d 个名词 / %d 条原则 / %d 张流程卡" % (
            len(d["problem_index"]), len(d["methods"]), len(d["terms"]), len(d["principles"]), len(d.get("flows", []))))
        return
    if args[0] == "--index":
        for row in d["problem_index"]:
            m = method_by_id(d, row["method_id"])
            if m:
                print("%s → %s·%s（%s）" % (row["type"], m["id"], m["name"], row["scene"]))
            else:
                print("%s → 待建（%s）" % (row["type"], row["scene"]))
        return
    if args[0] == "--methods":
        for m in d["methods"]:
            print("%s·%s — %s" % (m["id"], m["name"], m["solves"]))
        return
    if args[0] == "--card":
        m = method_by_id(d, args[1]) if len(args) > 1 else None
        if m:
            show_card(d, m)
        else:
            print("没有这张卡")
        return
    if args[0] == "--principles":
        for p in d["principles"]:
            show_principle(p)
        print("共 %d 条原则" % len(d["principles"]))
        return
    q = " ".join(args)
    hits = 0
    for row in d["problem_index"]:
        cands = row.get("aliases", []) + [row["type"]]
        if q in row["scene"] or any(q in c or c in q for c in cands):
            m = method_by_id(d, row["method_id"])
            if m:
                print("问题类型命中: %s → 调用 %s·%s" % (row["type"], m["id"], m["name"]))
            else:
                if row.get("candidate"):
                    print("命中待建格: %s —— 未建卡，候选方法 %s，是否按组合补卡？" % (row["type"], row["candidate"]))
                else:
                    print("命中待建格: %s —— 此格已画未建，是否按闭环补卡？" % row["type"])
            hits += 1
    for m in d["methods"]:
        blob = m["name"] + m["solves"] + m["trigger"] + m["steps"] + m["pitfalls"]
        if q in blob:
            show_card(d, m, full=False)
            hits += 1
    for t in d["terms"]:
        blob = t["name"] + t["represents"] + t["role"] + t.get("plain", "")
        if q in blob:
            print("名词 %s·%s（属 %s）: %s" % (t["id"], t["name"], t["method_id"], t["represents"]))
            hits += 1
    for p in d["principles"]:
        if q in p["title"] or q in p["text"] or q in p["actions"]:
            show_principle(p)
            hits += 1
    for fl in d.get("flows", []):
        blob = fl["name"] + fl["solves"] + fl["trigger"] + " ".join(x["action"] for x in fl["steps"])
        if q in blob:
            print("流程卡命中: %s·%s（%d 步）" % (fl["id"], fl["name"], len(fl["steps"])))
            hits += 1
    print("命中 %d 处" % hits)


if __name__ == "__main__":
    main()
