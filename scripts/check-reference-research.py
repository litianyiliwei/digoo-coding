#!/usr/bin/env python3
"""Validate the stage 02 reference-product and internet-research artifact."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADINGS = {
    "1": ("研究范围与问题", "Research Scope and Questions"),
    "2": ("参考产品清单", "Reference Product List"),
    "3": ("研究记录", "Research Records"),
    "4": ("对比与借鉴", "Comparison and Lessons"),
    "5": ("结论与假设", "Conclusions and Assumptions"),
    "6": ("影响映射", "Impact Mapping"),
    "7": ("未决问题", "Open Questions"),
    "8": ("来源与审批", "Sources and Approval"),
    "9": ("同类产品偏差确认", "Similar Product Deviation Confirmation"),
}
PLACEHOLDER = re.compile(r"\bTODO\b|\bTBD\b|PENDING|待确认|待补充|\[填充\]")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
URL = re.compile(r"https?://[^\s|\]]+")
IMPACT = re.compile(r"(FLOW-\d{3}|NODE-\d{3}-\d{2}|DO-\d{3}|BR-\d{3}|NFR-\d{3})")
DECISION = re.compile(r"采纳|不采纳|部分采纳|N/A|adopt|do not adopt|partially adopt", re.I)
SAME_CATEGORY = re.compile(r"同类|同类型|same category|similar product|competitor|竞品", re.I)
CONFIRMED = re.compile(r"用户已确认|已确认|confirmed|approved", re.I)
UNCONFIRMED = re.compile(r"待用户确认|未确认|pending|unconfirmed", re.I)


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
    # Advisory thresholds: recommended research depth. They are reported as
    # WARN lines and never fail the check; the stage review judges sufficiency.
    warnings: list[str] = []
    for prefix, titles in HEADINGS.items():
        if section(data, prefix) is None:
            errors.append(f"missing section: ## {prefix}. {titles[0]} / {titles[1]}")

    if args.strict:
        for n, line in enumerate(text.splitlines(), 1):
            if PLACEHOLDER.search(line):
                errors.append(f"line {n}: unresolved placeholder: {line.strip()[:80]}")

    questions = table_rows(section(data, "1") or [])
    if not questions:
        errors.append("section 1: need at least 1 research question (table row)")
    elif len(questions) < 3:
        warnings.append(f"section 1: {len(questions)} research question(s); 3 or more is recommended")

    product_section = section(data, "2") or []
    status_line = next((line for line in product_section if "参考产品状态" in line or "Reference product status" in line), None)
    status = None
    if status_line is None:
        errors.append("section 2: missing '- 参考产品状态：PRESENT / NONE' / '- Reference product status: PRESENT / NONE'")
    else:
        upper = status_line.upper()
        status = "NONE" if "NONE" in upper else "PRESENT" if "PRESENT" in upper else None
        if status is None:
            errors.append("section 2: Reference product status must be PRESENT or NONE")
    if status == "NONE":
        reason_line = next((line for line in product_section if "无参考产品理由" in line or "Reason for no reference product" in line), None)
        reason_text = re.split(r"[:：]", reason_line, 1)[-1].strip() if reason_line else ""
        if reason_line is None or has_placeholder(reason_text) or reason_text.upper() in {"N/A", "无", "NONE"}:
            errors.append("section 2: Reference product status=NONE requires a non-placeholder reason (无参考产品理由 / Reason for no reference product)")
    elif status == "PRESENT":
        products = table_rows(product_section)
        if not products:
            errors.append("section 2: 参考产品状态=PRESENT requires at least one product row")
        elif not any(
            len(cells) > 1 and SAME_CATEGORY.search(cells[1]) for cells in products
        ):
            errors.append(
                "section 2: 参考产品状态=PRESENT requires at least one same-category "
                "(同类/竞品/same category/similar product) product row"
            )
        for index, cells in enumerate(products, 1):
            joined = " | ".join(cells)
            if has_placeholder(joined):
                errors.append(f"section 2: product row {index} has unresolved placeholder")
            if not (URL.search(joined) or re.search(r"官网|文档|试用|截图|访谈|用户提供", joined)):
                errors.append(f"section 2: product row {index} needs a URL or access method")
            if not DATE.search(joined):
                errors.append(f"section 2: product row {index} needs a YYYY-MM-DD research date")

    research = table_rows(section(data, "3") or [])
    if not research:
        errors.append("section 3: need at least 1 internet research record (table row)")
    elif len(research) < 3:
        warnings.append(f"section 3: {len(research)} research record(s); 3 or more is recommended")
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
    if not urls:
        errors.append("section 3: need at least 1 real source URL from internet research")
    elif len(urls) < 3:
        warnings.append(f"section 3: {len(urls)} distinct source URL(s); 3 or more is recommended")

    comparisons = table_rows(section(data, "4") or [])
    if not comparisons:
        errors.append("section 4: need at least 1 comparison row")
    elif len(comparisons) < 2:
        warnings.append(f"section 4: {len(comparisons)} comparison row(s); 2 or more is recommended")
    for index, cells in enumerate(comparisons, 1):
        joined = " | ".join(cells)
        if not DECISION.search(joined):
            errors.append(f"section 4: comparison row {index} needs adopt/do not adopt/partially adopt/N/A (采纳/不采纳/部分采纳/N/A)")
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
    date_line = next((line for line in source.splitlines() if "调研日期" in line or "Research date" in line), "")
    if not DATE.search(date_line):
        errors.append("section 8: research date (调研日期 / Research date) must use YYYY-MM-DD")
    status_line = next((line for line in source.splitlines() if "审批状态" in line or "Approval status" in line), "")
    if not re.search(r"DRAFT|APPROVED", status_line, re.I):
        errors.append("section 8: approval status (审批状态 / Approval status) must be DRAFT or APPROVED")

    deviation_section = section(data, "9")
    if deviation_section is None:
        errors.append(
            "missing section: ## 9. 同类产品偏差确认 / Similar Product Deviation Confirmation"
        )
    else:
        deviation_body = "\n".join(deviation_section)
        deviation_rows = table_rows(deviation_section)
        if status == "NONE":
            if not re.search(r"N/A", deviation_body):
                errors.append(
                    "section 9: when there is no reference product, write N/A + reason"
                )
            reason_line = next(
                (
                    line
                    for line in deviation_section
                    if "理由" in line or "reason" in line.lower()
                ),
                None,
            )
            reason_text = re.split(r"[:：]", reason_line, 1)[-1].strip() if reason_line else ""
            if (
                reason_line is None
                or has_placeholder(reason_text)
                or reason_text.upper() in {"N/A", "NONE", "无"}
            ):
                errors.append(
                    "section 9: N/A requires a non-placeholder reason "
                    "(理由 / Reason)"
                )
        else:
            if not deviation_rows:
                errors.append(
                    "section 9: need at least 1 similar-product deviation row "
                    "(对比项 / 本项目输出 / 同类产品做法 / 偏差等级 / 影响对象 / 确认状态)"
                )
            elif len(deviation_rows) < 2:
                warnings.append(
                    f"section 9: {len(deviation_rows)} deviation row(s); 2 or more is recommended"
                )
            for index, cells in enumerate(deviation_rows, 1):
                joined = " | ".join(cells)
                level = cells[3] if len(cells) > 3 else ""
                if args.strict and has_placeholder(joined):
                    errors.append(f"section 9: deviation row {index} has unresolved placeholder")
                if not re.match(
                    r"(一致|可接受差异|重大差异|重大偏差|小差异|consistent|acceptable|minor|major|acceptable difference)",
                    level,
                    re.I,
                ):
                    errors.append(
                        f"section 9: deviation row {index} needs a deviation level "
                        "(一致/可接受差异/重大偏差 / consistent/acceptable/major)"
                    )
                if not IMPACT.search(joined) and "N/A" not in joined:
                    errors.append(
                        f"section 9: deviation row {index} needs a FLOW/NODE/DO/BR/NFR "
                        "reference or N/A"
                    )
                if re.match(r"(重大偏差|\bmajor\b)", level or joined, re.I):
                    if len(cells) < 8:
                        errors.append(
                            f"section 9: major deviation row {index} must record "
                            "confirmation status, confirmer, and date"
                        )
                        continue
                    confirm_status = cells[5]
                    approver = cells[6]
                    confirmed_at = cells[7]
                    if UNCONFIRMED.search(confirm_status) or not CONFIRMED.search(confirm_status):
                        errors.append(
                            f"section 9: major deviation row {index} deviates too far from "
                            "similar products; prompt the user to confirm and record "
                            "确认状态=用户已确认 plus 确认人/确认日期"
                        )
                    elif not approver or has_placeholder(approver):
                        errors.append(
                            f"section 9: major deviation row {index} requires the confirmer "
                            "(确认人 / Confirmer)"
                        )
                    elif not DATE.fullmatch(confirmed_at):
                        errors.append(
                            f"section 9: major deviation row {index} requires the confirmation "
                            "date as YYYY-MM-DD (确认日期 / Confirmed at)"
                        )

    for warning in warnings:
        print("WARN:", warning)
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
