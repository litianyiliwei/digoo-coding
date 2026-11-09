#!/usr/bin/env python3
"""Generate or verify docs/product/BASELINE-INDEX.md from baseline artifacts.

Usage:
  python scripts/gen-baseline-index.py --write
  python scripts/gen-baseline-index.py --check
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/product/BASELINE-INDEX.md'


def lines(path):
    target = ROOT / path
    if not target.is_file():
        return []
    return target.read_text(encoding='utf-8').splitlines()


def csv_rows(path):
    target = ROOT / path
    if not target.is_file():
        return []
    with target.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def count(path, pattern):
    return len(re.findall(pattern, '\n'.join(lines(path)), re.M))


def status(path):
    for line in lines(path)[:12]:
        match = re.search(r'状态[:：]\s*([^（(，,]+)', line)
        if match:
            return match.group(1).strip()
    return '—'


def build():
    flow_count = count('docs/product/workflows.md', r'^##\s+(FLOW-\d{3})\b')
    node_count = count('docs/product/workflows.md', r'^\|\s*(NODE-\d{3}-\d{2})\s*\|')
    do_count = len(csv_rows('docs/product/data-objects.csv'))
    rd_count = len(csv_rows('docs/product/rd-matrix.csv'))
    role_rows = csv_rows('docs/product/role-permission-matrix.csv')
    roles = {r.get('role_id', '').strip() for r in role_rows if r.get('role_id')}
    caps = {r.get('capability_id', '').strip() for r in role_rows if r.get('capability_id')}
    br_count = count('docs/product/business-rules.md', r'^\|\s*(BR-\d{3})\s*\|')
    term_count = count('docs/product/glossary.md', r'^\|\s*(TERM-\d{3})\s*\|')
    q_count = count('docs/product/open-questions.md', r'^\|\s*(Q-\d{3})\s*\|')
    dec_count = count('docs/product/decisions.md', r'^\|\s*(DEC-\d{3})\s*\|')
    asm_count = count('docs/product/assumptions.md', r'^\|\s*(ASM-\d{3})\s*\|')
    lesson_count = count('docs/product/lessons.md', r'^\|\s*(LESSON-\d{3})\s*\|')
    brief_lines = len(lines('docs/product/BASELINE-BRIEF.md'))
    req_lines = len(lines('docs/product/requirements-analysis.md'))
    sizing_lines = len(lines('docs/product/change-sizing.md'))
    id_lines = len(lines('docs/product/id-conventions.md'))
    accept_lines = len(lines('docs/product/acceptance-policy.md'))
    artifacts = [
        ('基线常驻简报', 'docs/product/BASELINE-BRIEF.md', f'{brief_lines} 行', '阶段 02–05 常驻入口'),
        ('需求业务梳理', 'docs/product/requirements-analysis.md', f'{req_lines} 行', '目标、范围、角色、假设与决策索引'),
        ('业务流程', 'docs/product/workflows.md', f'FLOW {flow_count} / NODE {node_count}', '主流程、替代流程、异常流程节点表'),
        ('业务数据对象', 'docs/product/data-objects.csv', f'{do_count} 个 DO', '业务概念目录，不是数据库表'),
        ('RD 矩阵', 'docs/product/rd-matrix.csv', f'{rd_count} 条 RD', '节点→角色→DO→访问类型→验证意图'),
        ('业务规则', 'docs/product/business-rules.md', f'{br_count} 条 BR', '全局与功能级规则，含等级/执行方式'),
        ('术语表', 'docs/product/glossary.md', f'{term_count} 个 TERM', '统一词汇与禁用词'),
        ('未决问题', 'docs/product/open-questions.md', f'{q_count} 个 Q', '未决问题、责任人、阻塞条件'),
        ('角色权限矩阵', 'docs/product/role-permission-matrix.csv', f'{len(role_rows)} 行 / ROLE {len(roles)} / CAP {len(caps)}', '提案级权限 AC 的锚点'),
        ('切片与 DoD', 'docs/product/change-sizing.md', f'{sizing_lines} 行', 'Change 预算、拆分信号与完成定义'),
        ('决策日志', 'docs/product/decisions.md', f'{dec_count} 条 DEC', '防止重复争论已决问题'),
        ('假设登记', 'docs/product/assumptions.md', f'{asm_count} 条 ASM', '假设、验证方式、到期点与责任人'),
        ('教训/反模式', 'docs/product/lessons.md', f'{lesson_count} 条 LESSON', '验收后回写的可复用失败模式'),
        ('ID 约定', 'docs/product/id-conventions.md', f'{id_lines} 行', '项目级/Change 级 ID 与并行分配规则'),
        ('验收政策', 'docs/product/acceptance-policy.md', f'{accept_lines} 行', 'AC 格式、测试映射、阻断项与证据要求'),
        ('基线状态', 'docs/architecture/baseline-status.md', status('docs/architecture/baseline-status.md'), '各基线域版本、冻结状态与审批'),
    ]
    out = [
        '# 基线索引（自动生成）',
        '',
        '> 本文件由 `scripts/gen-baseline-index.py` 生成，禁止手改。运行 `python scripts/gen-baseline-index.py --write` 更新；`--check` 校验是否过期。',
        '',
        '| 产物 | 路径 | 状态/规模 | 用途 |',
        '|---|---|---|---|',
    ]
    for name, path, amount, purpose in artifacts:
        exists = (ROOT / path).is_file()
        out.append(f'| {name} | `{path}` | {status(path) if status(path) != "—" else amount}{"（缺失）" if not exists else ""} | {purpose} |')
    out.extend(['', '## 当前缺口', ''])
    gaps = []
    if flow_count == 0:
        gaps.append('`workflows.md` 没有 FLOW 节点表。')
    if node_count == 0:
        gaps.append('`workflows.md` 没有 NODE 行；阶段 02 未完成。')
    if do_count == 0:
        gaps.append('`data-objects.csv` 仅有表头。')
    if rd_count == 0:
        gaps.append('`rd-matrix.csv` 仅有表头。')
    out.extend([f'- {gap}' for gap in gaps] or ['- 机器可读产物已齐备。'])
    out.extend(['', '## 生成规则', '',
                '- 索引只汇总路径、状态与数量，不复制基线内容。',
                '- 产物缺失时在状态列标注“缺失”；不得用空文件满足检查。',
                '- 状态变化或新增产物后重新生成；`--check` 失败视为基线漂移。'])
    return '\n'.join(out) + '\n'


def main():
    args = sys.argv[1:]
    if len(args) != 1 or args[0] not in {'--write', '--check'}:
        print('Usage: gen-baseline-index.py --write|--check', file=sys.stderr)
        sys.exit(2)
    content = build()
    if args[0] == '--write':
        OUT.write_text(content, encoding='utf-8')
        print(f'Wrote {OUT.relative_to(ROOT)}')
        return
    if not OUT.is_file():
        print(f'ERROR: missing {OUT.relative_to(ROOT)}; run --write', file=sys.stderr)
        sys.exit(1)
    if OUT.read_text(encoding='utf-8') != content:
        print('ERROR: BASELINE-INDEX.md is stale; run python scripts/gen-baseline-index.py --write', file=sys.stderr)
        sys.exit(1)
    print('Baseline index is up to date.')


if __name__ == '__main__':
    main()
