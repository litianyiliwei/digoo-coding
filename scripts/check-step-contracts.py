#!/usr/bin/env python3
"""Check one-to-one workflow step contracts against Skill and Prompt files."""
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'docs/STEP-ARTIFACT-CONTRACTS.json').read_text(encoding='utf-8'))
stages=json.loads((ROOT/'docs/WORKFLOW-STAGES.json').read_text(encoding='utf-8'))['stages']
SKILLS_DIR=ROOT/'.claude/skills' if (ROOT/'.claude/skills').is_dir() else ROOT/'.agents/skills'
errors=[]
seen=set()
contract_by_skill={}
for row in data.get('steps',[]):
    sid=row.get('skill')
    if not sid or sid in seen: errors.append(f'duplicate/missing skill id: {sid}'); continue
    seen.add(sid); contract_by_skill[sid]=row
    if not row.get('inputs') or not row.get('outputs') or not row.get('next_inputs'): errors.append(f'incomplete contract arrays: {sid}')
    skill=SKILLS_DIR/sid/'SKILL.md'
    prompt=ROOT/row.get('prompt','')
    if not skill.is_file(): errors.append(f'missing Skill: {skill.relative_to(ROOT)}')
    elif '## 输入/输出/交接契约（强制）' not in skill.read_text(encoding='utf-8'): errors.append(f'Skill missing handoff contract section: {sid}')
    if not prompt.is_file(): errors.append(f'missing Prompt: {row.get("prompt")}')
    elif '## 强制交付物交接' not in prompt.read_text(encoding='utf-8'): errors.append(f'Prompt missing handoff contract section: {row.get("prompt")}')
# Cross-check contract rows against the authoritative stage DAG (docs/WORKFLOW-STAGES.json).
# workflow-orchestrator is the "next step" entry point, intentionally not a DAG stage.
ORCHESTRATOR_SKILLS={'workflow-orchestrator'}
dag_skills={s['skill'] for s in stages}
if dag_skills|ORCHESTRATOR_SKILLS!=seen:
    errors.append(f'Contract/DAG skill mismatch: contract-only={sorted(seen-dag_skills)} dag-only={sorted(dag_skills-seen)}')
for s in stages:
    row=contract_by_skill.get(s['skill'])
    if row and row.get('prompt')!=s['prompt']:
        errors.append(f"Prompt path mismatch for {s['skill']}: contract={row.get('prompt')} dag={s['prompt']}")
if not (ROOT/'templates/workflow/step-handoff-report.md').is_file(): errors.append('missing handoff report template')
if errors:
    print('Step contract check failed:')
    for e in errors: print('ERROR:',e)
    sys.exit(1)
print(f'Step contracts passed: {len(seen)} rows aligned with {len(stages)} DAG stages; all Skills, Prompts and handoff report template linked.')
