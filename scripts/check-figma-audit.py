#!/usr/bin/env python3
"""Validate the Figma UI audit record for UI-bearing Changes (stage 06)."""
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


def page_ids(text):
    start = text.find('## 页面覆盖')
    if start < 0:
        return []
    end = text.find('\n## ', start + len('## 页面覆盖'))
    section = text[start:end if end >= 0 else len(text)]
    return sorted(set(re.findall(r'PAGE-\d{3}', section)))


def section(text, title):
    start = text.find(title)
    if start < 0:
        return ''
    end = text.find('\n## ', start + len(title))
    return text[start:end if end >= 0 else len(text)]


if no_ui:
    if AUDIT.is_file() and AUDIT.stat().st_size:
        text = AUDIT.read_text(encoding='utf-8')
        if not re.search(r'^- 设计来源状态：N/A\s*$', section(text, '## 设计来源与选择'), re.M):
            print('ERROR: --no-ui declared but design/figma-audit.md does not declare 设计来源状态：N/A; update it or drop --no-ui')
            sys.exit(1)
    print(f'Figma audit check passed: this Change explicitly has no UI. Reason: {reason}')
    sys.exit(0)

if not AUDIT.is_file() or not AUDIT.stat().st_size:
    print(f'ERROR: missing Figma audit record: {AUDIT.relative_to(ROOT)}')
    print('UI-bearing Changes must read the real Figma file/nodes/components/variables via Figma MCP and record the audit in design/figma-audit.md.')
    sys.exit(1)

text = AUDIT.read_text(encoding='utf-8')
source_section = section(text, '## 设计来源与选择')
if re.search(r'^- 设计来源状态：N/A\s*$', source_section, re.M):
    if not re.search(r'^- 无 UI 理由：\s*\S', source_section, re.M):
        print('ERROR: 无 UI 时必须在“设计来源与选择”写入“- 无 UI 理由：<原因>”')
        sys.exit(1)
    print('Figma audit check passed: this Change declares no UI in figma-audit.md.')
    sys.exit(0)

pages = page_ids(text)
if not pages:
    print('ERROR: figma-audit.md 页面覆盖 must declare at least one PAGE-###; use 设计来源状态：N/A + 无 UI 理由 when the Change has no UI.')
    sys.exit(1)

errors, warnings = [], []
lines = text.splitlines()
required_sections = ['## 设计来源与选择', '## 设计输入与风格参考', '## Figma 文件', '## 节点映射', '## 页面覆盖', '## 差异与待确认', '## MCP 读取记录', '## UI 评审']
for section in required_sections:
    if section not in text:
        errors.append(f'missing section: {section}')

source_section = ''
start = text.find('## 设计来源与选择')
if start >= 0:
    end = text.find('\n## ', start + len('## 设计来源与选择'))
    source_section = text[start:end if end >= 0 else len(text)]
if not re.search(r'(人工\s*Figma\s*设计|Figma\s*MCP\s*AI\s*自动设计)', source_section):
    errors.append('设计来源与选择必须明确为“人工 Figma 设计”或“Figma MCP AI 自动设计”')
if not re.search(r'^- 设计来源状态：APPROVED\s*$', source_section, re.M):
    errors.append('设计来源与选择必须标记“- 设计来源状态：APPROVED”，否则 06 不得开始')

required_inputs = ['需求与 AC', 'Figma MCP', '设计规范']
input_section = ''
start = text.find('## 设计输入与风格参考')
if start >= 0:
    end = text.find('\n## ', start + len('## 设计输入与风格参考'))
    input_section = text[start:end if end >= 0 else len(text)]
missing_inputs = [name for name in required_inputs if name not in input_section]
if missing_inputs:
    errors.append('设计输入与风格参考表缺少: ' + '、'.join(missing_inputs))

figma_refs = re.findall(r'https://(?:www\.)?figma\.com/[^\s)）]*|node-id=[A-Za-z0-9:%-]+|fileKey[=:][A-Za-z0-9]+', text, re.I)
figma_refs += re.findall(r'FIGMA-[A-Za-z0-9-]+', text)
if not figma_refs:
    errors.append('Figma 文件未登记：至少登记真实 Figma 链接、node-id、fileKey 或 FIGMA-ID')

# UI review is the design-owner sign-off on the real Figma design.
ui_section = ''
start = text.find('## UI 评审')
if start >= 0:
    end = text.find('\n## ', start + len('## UI 评审'))
    ui_section = text[start:end if end >= 0 else len(text)]
if not re.search(r'^- UI 评审状态：APPROVED\s*$', ui_section, re.M):
    errors.append('UI 评审必须标记“- UI 评审状态：APPROVED”，否则 06 不得通过')
if not re.search(r'^- 评审人：.+$', ui_section, re.M):
    errors.append('UI 评审缺少“- 评审人：”')
m = re.search(r'^- 评审证据：(.+)$', ui_section, re.M)
if not m:
    errors.append('UI 评审缺少“- 评审证据：”')
else:
    ev = m.group(1).strip()
    candidates = [(ROOT / ev).resolve(), (base / ev).resolve()]
    if not any(p.is_file() for p in candidates):
        errors.append(f'UI 评审证据文件不存在: {ev}')

# Every PAGE declared in 页面覆盖 must be mapped to a real Figma node/component/variable.
node_map = ''
start = text.find('## 节点映射')
if start >= 0:
    end = text.find('\n## ', start + len('## 节点映射'))
    node_map = text[start:end if end >= 0 else len(text)]
for pid in pages:
    if pid not in node_map:
        errors.append(f'节点映射缺少 {pid} → Figma node/component/variable 映射')

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
# Tool names alone are not evidence: at least one row must report a successful real call.
mcp_rows = [l for l in mcp_lines if l.strip().startswith('|')
            and '工具/命令' not in l
            and not re.match(r'^\|[\s:|-]+\|$', l.strip())]
if not any(any(t in l.lower() for t in ('use_figma', 'get_design_context', 'get_metadata', 'get_variable_defs', 'get_screenshot'))
           and ('passed' in l.lower() or '成功' in l) for l in mcp_rows):
    errors.append('MCP 读取记录缺少实际成功的 Figma MCP 调用；仅登记工具名或“未执行”不算读取')

for line_no, line in enumerate(lines, 1):
    if re.search(r'PENDING|TODO|TBD|\[填充\]', line, re.I):
        warnings.append(f'{AUDIT.relative_to(ROOT)}:{line_no}: unresolved placeholder remains')

if errors:
    for e in errors: print('ERROR:', e)
for w in warnings: print('WARN:', w)
if errors or (strict and warnings):
    print(f'Figma audit check failed: {len(errors)} error(s), {len(warnings)} warning(s).')
    sys.exit(1)
print(f'Figma audit check passed: {len(pages)} UI page(s), {len(figma_refs)} Figma reference(s), MCP tools: {", ".join(sorted(set(t.lower() for t in tools)))}.')
