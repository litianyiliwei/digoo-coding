#!/usr/bin/env python3
"""Validate the stage 02 reference-product and internet-research artifact."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADINGS = {
    "1": "研究范围与问题",
    "2": "参考产品清单",
    "3": "研究记录",
    "4": "对比与借鉴",
    "5": "结论与假设",
    "6": "影响映射",
    "7": "未决问题",
    "8": "来源与审批",
}
PLACEHOLDER = re.compile(r"\bTODO\b|\bTBD\b|PENDING|待确认|待补充|\[填充\]")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
URL = re.compile(r"https?://[^\s|\]]+")
IMPACT = re.compile(r"(FLOW-\d{3}|NODE-\d{3}-\d{2}|DO-\d{3}|BR-\d{3}|NFR-\d{3})")
DECISION = re.compile(r"采纳|不采纳|部分采纳|N/A")


def sections(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        match = re.match(r"^##\s+(.*)$", line)
        if match:
            current = match.group(1).strip()
            result[current] = []
        elif current is not None:
            result[current].append(line)
    return result


def section(data: dict[str, list[str]], prefix: str) -> list[str] | None:
    for name, lines in data.items():
        if name.startswith(prefix + ".") or name.startswith(prefix + " "):
            return lines
    return None


def table_rows(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    header_seen = False
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):
            continue
        if not header_seen:
            header_seen = True
            continue
        if any(cells):
            rows.append(cells)
    return rows


def has_placeholder(value: str) -> bool:
    return bool(PLACEHOLDER.search(value or ""))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", default="docs/product/reference-research.md")
    ap.add_argument("--root", default=str(ROOT), help="Project root (defaults to this package)")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    path = Path(args.file)
    path = (root / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_file():
        print(f"ERROR: missing reference research artifact: {path}")
        print("Stage 02 must produce docs/product/reference-research.md.")
        return 1
    text = path.read_text(encoding="utf-8")
    data = sections(text)
    errors: list[str] = []
    for prefix, title in HEADINGS.items():
        if section(data, prefix) is None:
            errors.append(f"missing section: ## {prefix}. {title}")

    if args.strict:
        for n, line in enumerate(text.splitlines(), 1):
            if PLACEHOLDER.search(line):
                errors.append(f"line {n}: unresolved placeholder: {line.strip()[:80]}")

    questions = table_rows(section(data, "1") or [])
    if len(questions) < 3:
        errors.append("section 1: need at least 3 research questions (table rows)")

    product_section = section(data, "2") or []
    status_line = next((line for line in product_section if "参考产品状态" in line), None)
    status = None
    if status_line is None:
        errors.append("section 2: missing '- 参考产品状态：PRESENT / NONE'")
    else:
        upper = status_line.upper()
        status = "NONE" if "NONE" in upper else "PRESENT" if "PRESENT" in upper else None
        if status is None:
            errors.append("section 2: 参考产品状态 must be PRESENT or NONE")
    if status == "NONE":
        reason_line = next((line for line in product_section if "无参考产品理由" in line), None)
        reason_text = reason_line.split("：", 1)[-1].strip() if reason_line else ""
        if reason_line is None or has_placeholder(reason_text) or reason_text.upper() in {"N/A", "无", "NONE"}:
            errors.append("section 2: 参考产品状态=NONE requires a non-placeholder 无参考产品理由")
    elif status == "PRESENT":
        products = table_rows(product_section)
        if not products:
            errors.append("section 2: 参考产品状态=PRESENT requires at least one product row")
        for index, cells in enumerate(products, 1):
            joined = " | ".join(cells)
            if has_placeholder(joined):
                errors.append(f"section 2: product row {index} has unresolved placeholder")
            if not (URL.search(joined) or re.search(r"官网|文档|试用|截图|访谈|用户提供", joined)):
                errors.append(f"section 2: product row {index} needs a URL or access method")
            if not DATE.search(joined):
                errors.append(f"section 2: product row {index} needs a YYYY-MM-DD research date")

    research = table_rows(section(data, "3") or [])
    if len(research) < 3:
        errors.append("section 3: need at least 3 internet research records (table rows)")
    urls: set[str] = set()
    for index, cells in enumerate(research, 1):
        joined = " | ".join(cells)
        found = URL.findall(joined)
        if not found:
            errors.append(f"section 3: research row {index} needs an http(s) source URL")
        urls.update(found)
        if not DATE.search(joined):
            errors.append(f"section 3: research row {index} needs a YYYY-MM-DD access date")
        if args.strict and has_placeholder(joined):
            errors.append(f"section 3: research row {index} has unresolved placeholder")
    if len(urls) < 3:
        errors.append("section 3: need at least 3 distinct source URLs from internet research")

    comparisons = table_rows(section(data, "4") or [])
    if len(comparisons) < 2:
        errors.append("section 4: need at least 2 comparison rows")
    for index, cells in enumerate(comparisons, 1):
        joined = " | ".join(cells)
        if not DECISION.search(joined):
            errors.append(f"section 4: comparison row {index} needs 采纳/不采纳/部分采纳/N/A")
        if args.strict and has_placeholder(joined):
            errors.append(f"section 4: comparison row {index} has unresolved placeholder")

    conclusion = "\n".join(section(data, "5") or [])
    if not re.search(r"ASM-|DEC-|N/A", conclusion):
        errors.append("section 5: record at least one ASM/DEC consequence, or N/A + reason")

    impact = table_rows(section(data, "6") or [])
    if not impact:
        errors.append("section 6: need at least one impact row")
    for index, cells in enumerate(impact, 1):
        joined = " | ".join(cells)
        if not (IMPACT.search(joined) or "N/A" in joined):
            errors.append(f"section 6: impact row {index} needs a FLOW/NODE/DO/BR/NFR reference or N/A")
        if args.strict and has_placeholder(joined):
            errors.append(f"section 6: impact row {index} has unresolved placeholder")

    open_questions = table_rows(section(data, "7") or [])
    if not open_questions:
        errors.append("section 7: need at least one Q row or N/A + reason")

    source = "\n".join(section(data, "8") or [])
    date_line = next((line for line in source.splitlines() if "调研日期" in line), "")
    if not DATE.search(date_line):
        errors.append("section 8: 调研日期 must use YYYY-MM-DD")
    status_line = next((line for line in source.splitlines() if "审批状态" in line), "")
    if not re.search(r"DRAFT|APPROVED", status_line, re.I):
        errors.append("section 8: 审批状态 must be DRAFT or APPROVED")

    if errors:
        for error in errors:
            print("ERROR:", error)
        print(f"Reference research check failed: {len(errors)} issue(s).")
        return 1
    print(
        "Reference research check passed: "
        f"{len(questions)} questions, {len(research)} research records, "
        f"{len(urls)} distinct sources, {len(comparisons)} comparisons."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
