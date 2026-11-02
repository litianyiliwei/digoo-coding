#!/usr/bin/env python3
"""Check one-to-one workflow step contracts against Skill and Prompt files."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
skills_root=next((ROOT/d for d in ('.claude/skills', '.agents/skills') if (ROOT/d).is_dir()), ROOT/'.claude/skills')
data=json.loads((ROOT/'docs/STEP-ARTIFACT-CONTRACTS.json').read_text(encoding='utf-8'))
errors=[]
seen=set()
for row in data.get('steps',[]):
    sid=row.get('skill')
    if not sid or sid in seen: errors.append(f'duplicate/missing skill id: {sid}'); continue
    seen.add(sid)
    if not row.get('inputs') or not row.get('outputs') or not row.get('next_inputs'): errors.append(f'incomplete contract arrays: {sid}')
    skill=skills_root/sid/'SKILL.md'
    prompt=ROOT/row.get('prompt','')
    if not skill.is_file(): errors.append(f'missing Skill: {skill.relative_to(ROOT)}')
    elif '## 输入/输出/交接契约（强制）' not in skill.read_text(encoding='utf-8'): errors.append(f'Skill missing handoff contract section: {sid}')
    if not prompt.is_file(): errors.append(f'missing Prompt: {row.get("prompt")}')
    elif '## 强制交付物交接' not in prompt.read_text(encoding='utf-8'): errors.append(f'Prompt missing handoff contract section: {row.get("prompt")}')
if not (ROOT/'templates/workflow/step-handoff-report.md').is_file(): errors.append('missing handoff report template')
if len(seen)!=20: errors.append(f'expected 20 contract rows, got {len(seen)}')
if errors:
    print('Step contract check failed:')
    for e in errors: print('ERROR:',e)
    sys.exit(1)
print(f'Step contracts passed: {len(seen)} rows; all Skills, Prompts and handoff report template linked.')
