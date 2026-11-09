#!/usr/bin/env python3
"""Check a Change-scoped prototype and review record (stage 06)."""
from pathlib import Path
import re, sys
ROOT = Path(__file__).resolve().parents[1]

args = sys.argv[1:]
strict = '--strict' in args
no_ui = '--no-ui' in args
change = None
reason = None
if '--change' in args:
    idx = args.index('--change')
    if idx + 1 >= len(args):
        print('Usage: check-prototype-build.py --change <change-id> [--strict | --no-ui --reason <reason>]', file=sys.stderr)
        sys.exit(2)
    change = args[idx + 1]
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', change):
        print('Invalid change-id', file=sys.stderr); sys.exit(2)
    args = args[:idx] + args[idx + 2:]
if '--reason' in args:
    idx = args.index('--reason')
    if idx + 1 >= len(args):
        print('--reason requires a value', file=sys.stderr); sys.exit(2)
    reason = args[idx + 1]
    args = args[:idx] + args[idx + 2:]
args = [a for a in args if a not in {'--strict', '--no-ui'}]
if args or not change:
    print('Usage: check-prototype-build.py --change <change-id> [--strict | --no-ui --reason <reason>]', file=sys.stderr)
    sys.exit(2)
if no_ui and (not reason or not reason.strip()):
    print('--no-ui requires --reason <reason>', file=sys.stderr); sys.exit(2)
if no_ui and not strict:
    print('Use --strict with --no-ui so the explicit scope exception is checked', file=sys.stderr); sys.exit(2)

base = ROOT / 'openspec/changes' / change / 'design'
PROTO = base / 'prototype.md'
if no_ui:
    if PROTO.is_file():
        print('ERROR: --no-ui declared but prototype artifacts exist; remove --no-ui or delete/rename them')
        sys.exit(1)
    print(f'Prototype check passed: this Change explicitly has no UI. Reason: {reason}')
    sys.exit(0)

if not PROTO.is_file():
    print(f'ERROR: missing prototype/review record: {PROTO.relative_to(ROOT)}')
    print('Stage 06 has not produced its artifact; prototype generation not verifiable.')
    sys.exit(1)

errors, warnings = [], []
lines = PROTO.read_text(encoding='utf-8').splitlines()
text = '\n'.join(lines)
required_sections = ['## 原型链接', '## 页面清单', '## 页面-需求映射', '## MCP 调用记录', '## 评审结论', '## 页面差异', '## 需求澄清']
for section in required_sections:
    if section not in text:
        errors.append(f'missing section: {section}')
for line_no, line in enumerate(lines, 1):
    if re.search(r'<原型|<页面|TBD|\[填充\]|PENDING', line, re.I) and '--' not in line:
        warnings.append(f'{PROTO.relative_to(ROOT)}:{line_no}: unresolved template placeholder remains')

link_lines = [l for l in lines if l.strip().startswith('-') and ('pen.dev' in l or 'pen.new' in l or 'pencil' in l or '未使用' in l or 'blocked' in l.lower())]
if not link_lines:
    errors.append('原型链接未登记：至少登记一条 pen.dev 链接，或明确说明未使用/不可用')

SEP = re.compile(r'^\|[\s:|-]+\|$')
def is_noise(line, header_kw):
    return SEP.match(line.strip()) or header_kw in line

page_ids = []
in_pages = False
for line_no, line in enumerate(lines, 1):
    if line.strip() == '## 页面清单':
        in_pages = True; continue
    if in_pages and line.startswith('## '):
        in_pages = False
    if in_pages:
        m = re.match(r'^\|\s*(PAGE-\d+)\s*\|', line)
        if m:
            page_ids.append((m.group(1), line_no))
        elif line.strip() and not is_noise(line, 'PAGE ID'):
            warnings.append(f'{PROTO.relative_to(ROOT)}:{line_no}: 页面清单行不是 PAGE-ID 表行')
if not page_ids:
    warnings.append('页面清单为空：本 Change 可能无 UI；请确认并考虑使用 --no-ui')

seen = {}
for pid, line_no in page_ids:
    if pid in seen:
        errors.append(f'{PROTO.relative_to(ROOT)}:{line_no}: duplicate PAGE-ID {pid} (first at line {seen[pid]})')
    else:
        seen[pid] = line_no

req_ids = set()
for rel, pattern in [
    ('docs/product/workflows.md', r'FLOW-\d{3}'),
    ('docs/product/business-rules.md', r'BR-\d{3}'),
    (f'openspec/changes/{change}/design/user-stories.md', r'(?:US|AC)-\d{3}')]:
    p = ROOT / rel
    if p.is_file():
        req_ids.update(re.findall(pattern, p.read_text(encoding='utf-8')))

mapping_rows = []
in_map = False
for line_no, line in enumerate(lines, 1):
    if line.strip() == '## 页面-需求映射':
        in_map = True; continue
    if in_map and line.startswith('## '):
        in_map = False
    if in_map:
        m = re.match(r'^\|\s*(PAGE-\d+)\s*\|\s*([^|]*)\|\s*([^|]*)\|', line)
        if m:
            mapping_rows.append((m.group(1), m.group(2).strip(), m.group(3).strip(), line_no))
        elif line.strip() and not is_noise(line, 'PAGE ID'):
            warnings.append(f'{PROTO.relative_to(ROOT)}:{line_no}: 映射行不是 PAGE-ID 表行')
covered = {r[0] for r in mapping_rows}
for pid in seen:
    if pid not in covered:
        warnings.append(f'{pid}: 页面未映射到任何需求 ID')
for pid, refs, _, line_no in mapping_rows:
    for ref in [x.strip() for x in refs.replace('；', ';').replace('，', ',').split(';') if x.strip()]:
        if not ref or ref.upper() == 'PENDING':
            continue
        if ref not in req_ids:
            errors.append(f'{PROTO.relative_to(ROOT)}:{line_no}: {pid} 引用了不存在的需求 ID: {ref}')
if mapping_rows and not req_ids:
    warnings.append('提案级 US/AC 或项目 FLOW/BR 尚未声明稳定 ID；映射表引用无法核验，阶段 05/02 产物需先补齐')

PENCIL_TOOLS = ('execute', 'get_app_state', 'get_style', 'read_skill')
mcp_rows = []
in_mcp = False
for line in lines:
    if line.strip() == '## MCP 调用记录':
        in_mcp = True; continue
    if in_mcp and line.startswith('## '):
        in_mcp = False
    if in_mcp and line.strip().startswith('|'):
        row = line.strip()
        if is_noise(row, '工具/命令'):
            continue
        mcp_rows.append(row)
if not any(any(t in row for t in PENCIL_TOOLS) or '不可用' in row or 'blocked' in row.lower() or '未使用' in row for row in mcp_rows):
    warnings.append('MCP 调用记录缺少工具/命令明细；请登记 pencil 工具实际调用与结果（或如实标记 blocked/未使用）')

if strict:
    if 'APPROVED' not in text:
        errors.append('prototype.md: 评审结论未标记 APPROVED（严格模式要求原型/页面清单已批准）')

if errors:
    for e in errors:
        print('ERROR:', e)
for w in warnings:
    print('WARN:', w)
if errors or (strict and warnings):
    print(f'Prototype/review record check failed: {len(errors)} error(s), {len(warnings)} warning(s).')
    sys.exit(1)
print(f'Pages: {len(page_ids)}; mapped: {len(mapping_rows)}; requirement refs valid; review record present.')
print('Prototype and review check passed.')
