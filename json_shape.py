#!/usr/bin/env python3
"""Summarize JSON structure without printing its values."""

import argparse
from collections import Counter
from itertools import islice
import json
from pathlib import Path
import sys


MAX_INPUT_BYTES = 8 * 1024 * 1024
MAX_DEPTH = 5
MAX_ARRAY_ITEMS = 100
MAX_OBJECT_KEYS = 200
MAX_NODES = 20_000
MAX_ROWS = 200


def terminal_safe(value):
    return "".join(
        char if char.isprintable() else char.encode("unicode_escape").decode("ascii")
        for char in value
    )


def kind(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, dict):
        return "object"
    return "array"


def property_path(path, key):
    if len(key) > 80:
        key = key[:77] + "..."
    return f"{path}[{json.dumps(key, ensure_ascii=True)}]"


def reject_constant(value):
    raise ValueError(f"JSON 不支持非标准常量 {value}。")


def summarize(root):
    counts = Counter()
    array_lengths = {}
    stack = [("$", root, 0)]
    visited = 0
    depth_limited = False
    array_sampled = False
    object_sampled = False

    while stack and visited < MAX_NODES:
        path, value, depth = stack.pop()
        visited += 1
        counts[(path, kind(value))] += 1

        if isinstance(value, dict):
            if depth + 1 >= MAX_DEPTH:
                depth_limited |= bool(value)
                continue
            entries = list(islice(value.items(), MAX_OBJECT_KEYS))
            object_sampled |= len(value) > len(entries)
            stack.extend(
                (property_path(path, key), child, depth + 1)
                for key, child in reversed(entries)
            )
        elif isinstance(value, list):
            lengths = array_lengths.setdefault(path, [])
            lengths.append(len(value))
            if depth + 1 >= MAX_DEPTH:
                depth_limited |= bool(value)
                continue
            children = value[:MAX_ARRAY_ITEMS]
            array_sampled |= len(value) > len(children)
            stack.extend((path + "[]", child, depth + 1) for child in reversed(children))

    node_limited = bool(stack)
    rows = sorted(counts.items())
    for (path, value_kind), count in rows[:MAX_ROWS]:
        detail = f"{value_kind} × {count}"
        if value_kind == "array":
            lengths = array_lengths[path]
            detail += f"，长度 {min(lengths)}–{max(lengths)}"
        print(f"{path}  {detail}")

    if len(rows) > MAX_ROWS:
        print(f"…还有 {len(rows) - MAX_ROWS} 条结构记录未显示。")
    if array_sampled:
        print(f"提示：每个数组最多查看前 {MAX_ARRAY_ITEMS} 项；路径计数可能是样本数。")
    if object_sampled:
        print(f"提示：每个对象最多查看前 {MAX_OBJECT_KEYS} 个字段。")
    if depth_limited:
        print(f"提示：已限制在 {MAX_DEPTH} 层以内。")
    if node_limited:
        print(f"提示：已达到 {MAX_NODES} 个节点上限，摘要不完整。")


def main(argv=None):
    parser = argparse.ArgumentParser(description="查看 JSON 字段结构，不输出数据值。")
    parser.add_argument("source", nargs="?", default="-", help="JSON 文件；省略时从标准输入读取")
    args = parser.parse_args(argv)

    try:
        if args.source == "-":
            raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        else:
            with Path(args.source).open("rb") as source:
                raw = source.read(MAX_INPUT_BYTES + 1)
    except OSError as error:
        print(f"json-shape: {terminal_safe(str(error))}", file=sys.stderr)
        return 2

    if len(raw) > MAX_INPUT_BYTES:
        print(f"json-shape: 输入超过 {MAX_INPUT_BYTES // (1024 * 1024)} MiB 上限。", file=sys.stderr)
        return 2
    try:
        document = json.loads(raw.decode("utf-8-sig"), parse_constant=reject_constant)
    except RecursionError:
        print("json-shape: JSON 嵌套过深，无法解析。", file=sys.stderr)
        return 2
    except (UnicodeError, ValueError) as error:
        print(f"json-shape: {terminal_safe(str(error))}", file=sys.stderr)
        return 2

    summarize(document)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
