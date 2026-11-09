#!/usr/bin/env python3
"""Validate required subsections inside the unified design.md."""
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[1:]
change = None
if '--change' in args:
    idx = args.index('--change')
    if idx + 1 >= len(args):
        print('Usage: check-design-sections.py --change <change-id>', file=sys.stderr)
        sys.exit(2)
    change = args[idx + 1]
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', change):
        print('Invalid change-id', file=sys.stderr); sys.exit(2)
    args = args[:idx] + args[idx + 2:]
args = [a for a in args if a != '--strict']
if args or not change:
    print('Usage: check-design-sections.py --change <change-id>', file=sys.stderr)
    sys.exit(2)

DESIGN = ROOT / 'openspec/changes' / change / 'design.md'
if not DESIGN.is_file():
    print(f'ERROR: missing design.md: {DESIGN.relative_to(ROOT)}')
    sys.exit(1)

text = DESIGN.read_text(encoding='utf-8')
lines = text.splitlines()
sections = {}
current = None
for line in lines:
    if line.startswith('## ') and not line.startswith('### '):
        current = line[3:].strip()
        sections[current] = []
    elif current is not None:
        sections[current].append(line)

REQUIRED = {
    '设计决策': ['### 范围与非目标', '### 关键决策与权衡', '### 设计任务分解与接口范围', '### 设计缺口与准入结论'],
    '接口设计': ['### 接口清单', '### 契约与错误语义', '### 接口追踪'],
    '前端详细设计': ['### 路由与组件树', '### PAGE→BLOCK→组件映射', '### 组件职责与状态', '### 事件处理', '### 状态覆盖', '### 测试映射'],
    '后端详细设计': ['### API 执行链', '### API→IO 映射', '### IO 契约', '### 数据模型与迁移', '### 非数据库 IO', '### 领域类型与方法', '### 错误与一致性', '### 共享关注点', '### 测试覆盖', '### 未决决策'],
    '测试设计': ['### 测试策略', '### 测试环境与替身', '### 人工验证'],
}
SECTION_ALIASES = {
    '设计决策': ['设计决策'],
    '接口设计': ['接口设计'],
    '前端详细设计': ['前端详细设计'],
    '后端详细设计': ['后端详细设计'],
    '测试设计': ['测试设计'],
}

errors, warnings = [], []
for section, required in REQUIRED.items():
    aliases = SECTION_ALIASES[section]
    present = next((a for a in aliases if a in sections), None)
    if not present:
        errors.append(f'design.md missing section: ## {section}')
        continue
    body = '\n'.join(sections[present]).strip()
    if not body:
        errors.append(f'## {section} is empty; fill content or write N/A with a reason')
        continue
    # A section explicitly scoped out may be just N/A (or x-api-scope: none for API).
    if re.search(r'x-api-scope:\s*none', body, re.I) and '### ' not in body:
        continue
    if body.upper().startswith('N/A') and '### ' not in body:
        continue
    for sub in required:
        if sub not in body:
            errors.append(f'## {section} missing required subsection: {sub}')

if errors:
    for e in errors:
        print('ERROR:', e)
    print(f'Design section check failed: {len(errors)} issue(s).')
    sys.exit(1)
print('Design section check passed: design.md has the required unified subsections.')
