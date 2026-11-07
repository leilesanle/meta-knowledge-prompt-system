#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 the meta-knowledge-prompt-system contributors
"""元数据自证闸门（规则：发布前元数据四字段自证）。

发布前检查交付信息是否写全四字段；缺一即拦截，不许进发布队列。
用法:
  python scripts/seal_metadata.py <成品信息.json>
  python scripts/seal_metadata.py --example    # 打印最小合规格示例
退出码: 0=PASS（可进发布队列）, 1=FAIL（拦截）, 2=文件/JSON 错误
"""
import json, sys

REQUIRED = ("script_used_in_audio", "audio_source", "portrait_source", "aigc_label")
EXAMPLE = {
    "file": "path/to/final.mp4",
    "classification": "链路验证片 · 不可发布",
    "width": 720, "height": 1280,
    "script_used_in_audio": False,
    "audio_source": "示例音频拼接，非文稿朗读",
    "portrait_source": "自有/授权素材（授权状态：已确认）",
    "aigc_label": True,
    "cloud_steps": "无，全程本地",
}


def check(d):
    out = []
    for k in REQUIRED:
        out.append(("字段 %s" % k, k in d and d[k] not in (None, "", []), "缺失或为空"))
    if d.get("script_used_in_audio") is False:
        out.append(("无真配音 → 定位降为不可发布",
                    "不可发布" in str(d.get("classification", "")),
                    "classification 须含「不可发布」，不冒充可发布口播成品"))
        out.append(("无真配音 → 音频来源如实写明",
                    len(str(d.get("audio_source", ""))) >= 8,
                    "audio_source 须写清来源类型"))
    if d.get("aigc_label") is True:
        out.append(("AI 标识为 true → 需有可见标识说明",
                    "aigc" in json.dumps(d, ensure_ascii=False).lower(),
                    "建议同时写明标识位置"))
    fields_ok = all(k in d and d[k] not in (None, "", []) for k in REQUIRED)
    out.append(("素材授权状态明确",
                fields_ok and "待确认" not in str(d.get("portrait_source", "")),
                "四字段须齐全，且 portrait_source 授权状态待确认时不得直接发布"))
    return out


def main():
    if "--example" in sys.argv:
        print(json.dumps(EXAMPLE, ensure_ascii=False, indent=2))
        return 0
    if len(sys.argv) < 2:
        print("用法: seal_metadata.py <成品信息.json> | --example")
        return 2
    try:
        d = json.load(open(sys.argv[1], encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print("读取/解析失败:", e)
        return 2
    rs = check(d)
    for name, ok, why in rs:
        print("  %s %-36s %s" % ("✓" if ok else "✗", name, "" if ok else why))
    bad = [n for n, ok, _ in rs if not ok]
    print("\n%s  %d/%d 通过" % ("PASS 可进发布队列" if not bad else "FAIL 拦截，不进发布队列",
                                 len(rs) - len(bad), len(rs)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
