#!/usr/bin/env python3
"""Validate the Figma UI audit record for UI-bearing Changes (stage 06)."""
from pathlib import Path
import csv, re, sys

ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[1:]
strict = '--strict' in args
no_ui = '--no-ui' in args
change = None
reason = None
if '--change' in args:
    idx = args.index('--change')
    if idx + 1 >= len(args):
        print('Usage: check-figma-audit.py --change <change-id> [--no-ui --reason <reason>] [--strict]', file=sys.stderr)
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
    print('Usage: check-figma-audit.py --change <change-id> [--no-ui --reason <reason>] [--strict]', file=sys.stderr)
    sys.exit(2)
if no_ui and (not reason or not reason.strip()):
    print('--no-ui requires --reason <reason>', file=sys.stderr); sys.exit(2)

base = ROOT / 'openspec/changes' / change / 'design'
AUDIT = base / 'figma-audit.md'
PAGE = base / 'page-inventory.csv'

def page_rows():
    if not PAGE.is_file():
        return []
    with PAGE.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

rows = page_rows()
has_ui = bool(rows)
if no_ui:
    if AUDIT.is_file() and AUDIT.stat().st_size:
        print('ERROR: --no-ui declared but design/figma-audit.md exists; remove it or drop --no-ui')
        sys.exit(1)
    if has_ui:
        print('ERROR: --no-ui declared but page-inventory.csv has data rows')
        sys.exit(1)
    print(f'Figma audit check passed: this Change explicitly has no UI. Reason: {reason}')
    sys.exit(0)

if not has_ui:
    print('Figma audit check skipped: page-inventory.csv has no UI rows (declare --no-ui explicitly when closing stage 06).')
    sys.exit(0)

errors, warnings = [], []
if not AUDIT.is_file() or not AUDIT.stat().st_size:
    print(f'ERROR: missing Figma audit record: {AUDIT.relative_to(ROOT)}')
    print('UI-bearing Changes must read the real Figma file/nodes/components/variables via Figma MCP and record the audit.')
    sys.exit(1)

text = AUDIT.read_text(encoding='utf-8')
lines = text.splitlines()
required_sections = ['## Figma 文件', '## 节点映射', '## 区块覆盖', '## 差异与待确认', '## MCP 读取记录']
for section in required_sections:
    if section not in text:
        errors.append(f'missing section: {section}')

figma_refs = re.findall(r'https://(?:www\.)?figma\.com/[^\s)）]*|node-id=[A-Za-z0-9:%-]+|fileKey[=:][A-Za-z0-9]+|FIGMA-[A-Za-z0-9-]+', text, re.I)
if not figma_refs:
    errors.append('Figma 文件未登记：至少登记真实 Figma 链接、node-id、fileKey 或 FIGMA-ID')

in_mcp = False
mcp_lines = []
for line in lines:
    if line.strip() == '## MCP 读取记录':
        in_mcp = True; continue
    if in_mcp and line.startswith('## '):
        in_mcp = False
    if in_mcp:
        mcp_lines.append(line)
mcp_text = '\n'.join(mcp_lines)
tools = re.findall(r'(get_design_context|get_metadata|get_variable_defs|get_screenshot|use_figma|figma\s*mcp)', mcp_text, re.I)
if not tools:
    errors.append('MCP 读取记录缺少真实 Figma MCP 工具调用（get_design_context/get_metadata/get_variable_defs/get_screenshot/use_figma）')
if re.search(r'MCP\s*不可用|blocked|未读取|未执行', mcp_text, re.I) and not tools:
    errors.append('UI 变更不得以“MCP 不可用/未读取”通过；必须实际读取 Figma 设计或阻断阶段')

for line_no, line in enumerate(lines, 1):
    if re.search(r'PENDING|TODO|TBD|\[填充\]', line, re.I):
        warnings.append(f'{AUDIT.relative_to(ROOT)}:{line_no}: unresolved placeholder remains')

if errors:
    for e in errors: print('ERROR:', e)
for w in warnings: print('WARN:', w)
if errors or (strict and warnings):
    print(f'Figma audit check failed: {len(errors)} error(s), {len(warnings)} warning(s).')
    sys.exit(1)
print(f'Figma audit check passed: {len(rows)} UI page(s), {len(figma_refs)} Figma reference(s), MCP tools: {", ".join(sorted(set(t.lower() for t in tools)))}.')
