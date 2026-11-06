#!/usr/bin/env python3
"""Validate that every file output has a declared consumer or is explicitly evidence-only."""
import json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = json.loads((ROOT / 'docs/STEP-ARTIFACT-CONTRACTS.json').read_text(encoding='utf-8'))
STAGES = json.loads((ROOT / 'docs/WORKFLOW-STAGES.json').read_text(encoding='utf-8'))['stages']
ROWS = CONTRACTS['steps']
ORDER = [r['step'] for r in ROWS]
DAG_IDS = {s['id'] for s in STAGES}
SPECIAL = {'ALL', 'SYSTEM', 'GATE', 'FUTURE'}


def extract(o):
    for token in ('docs/', 'templates/', 'openspec/', 'workflow/', 'prompts/', 'scripts/'):
        i = o.find(token)
        if i >= 0:
            s = o[i:]
            s = re.split(r'[（(，,；;、\s]', s, 1)[0]
            return s.rstrip('。.）)')
    for special in ('workflow-state.json', 'AGENTS.md'):
        if special in o:
            return special
    return None


errors = []
warnings = []
records = CONTRACTS.get('output_consumption', [])
if not records:
    errors.append('Missing output_consumption map in docs/STEP-ARTIFACT-CONTRACTS.json')

by_key = {}
for rec in records:
    key = (rec.get('step'), rec.get('artifact'))
    if key in by_key:
        errors.append(f'duplicate output_consumption record: {key}')
    by_key[key] = rec

# Every file output must have a record.
for row in ROWS:
    for output in row.get('outputs', []):
        art = extract(output)
        if not art:
            continue
        if (row['step'], art) not in by_key:
            errors.append(f'{row["step"]}: file output has no consumption record: {art}')

for rec in records:
    step = rec.get('step')
    art = rec.get('artifact')
    consumers = rec.get('consumed_by', [])
    evidence_only = bool(rec.get('evidence_only'))
    if step not in ORDER:
        errors.append(f'unknown source step in consumption map: {step}')
        continue
    row = next(r for r in ROWS if r['step'] == step)
    if not any(art in o for o in row.get('outputs', [])):
        errors.append(f'{step}: consumption artifact not listed in outputs: {art}')
    if not consumers and not evidence_only:
        errors.append(f'{step}: output has no consumer and is not evidence_only: {art}')
    for c in consumers:
        if c in SPECIAL:
            continue
        if c not in ORDER:
            errors.append(f'{step}: unknown consumer stage {c} for {art}')
            continue
        if ORDER.index(c) <= ORDER.index(step):
            errors.append(f'{step}: consumer {c} is not later than source for {art}')
            continue
        target = next(r for r in ROWS if r['step'] == c)
        base = os.path.basename(art)
        if not any(art in inp or base in inp for inp in target.get('inputs', [])):
            errors.append(f'{step}: consumer {c} inputs do not reference {art}')

for w in warnings:
    print('WARN:', w)
for e in errors:
    print('ERROR:', e)
if errors:
    print(f'Output consumption check failed: {len(errors)} error(s).')
    sys.exit(1)
print(f'Output consumption check passed: {len(records)} file output(s), '
      f'{sum(1 for r in records if r.get("evidence_only"))} evidence-only.')
