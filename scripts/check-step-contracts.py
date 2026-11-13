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
# Validate the method policy covers 02-10 and that its required skills are
# actually mentioned in the matching Skill and Prompt (not just in the contract).
dag_ids={s['id'] for s in stages}
policy=data.get('method_policy') or {}
policy_steps={str(k).split('-')[0] for k in policy}
required_steps={'02','03','04','05','06','07','08','09','10'}
missing_policy=required_steps-policy_steps
if missing_policy:
    errors.append('method_policy missing stages: '+', '.join(sorted(missing_policy)))
for key, rule in policy.items():
    if key not in dag_ids:
        errors.append(f'method_policy references unknown stage id: {key}')
        continue
    row=next((r for r in data['steps'] if str(r.get('step'))==str(key).split('-')[0]), None)
    if not row:
        errors.append(f'method_policy stage has no contract row: {key}')
        continue
    sid=row.get('skill')
    skill_file=SKILLS_DIR/sid/'SKILL.md'
    prompt_file=ROOT/row.get('prompt','')
    skill_text=skill_file.read_text(encoding='utf-8') if skill_file.is_file() else ''
    prompt_text=prompt_file.read_text(encoding='utf-8') if prompt_file.is_file() else ''
    for requirement in rule.get('required',[]):
        name=str(requirement.get('skill') or '').strip()
        if not name:
            errors.append(f'method_policy {key}: empty required skill')
            continue
        if skill_file.is_file() and name not in skill_text:
            errors.append(f'method_policy {key}: skill {name} not mentioned in {skill_file.relative_to(ROOT)}')
        if prompt_file.is_file() and name not in prompt_text:
            errors.append(f'method_policy {key}: skill {name} not mentioned in {row.get("prompt")}')
        for topic in requirement.get('required_topics', []):
            topic=str(topic).strip()
            if not topic:
                continue
            if skill_file.is_file() and topic not in skill_text:
                errors.append(f'method_policy {key}: required topic {topic!r} not mentioned in {skill_file.relative_to(ROOT)}')
            if prompt_file.is_file() and topic not in prompt_text:
                errors.append(f'method_policy {key}: required topic {topic!r} not mentioned in {row.get("prompt")}')
# Validate lean-context policies: every change stage has a lean default read
# set within its declared file budget, plus an on-demand overflow list.
input_policy=data.get('input_policy') or {}
output_policy=data.get('output_policy') or {}
if not input_policy.get('stage_profiles'):
    errors.append('input_policy.stage_profiles is missing')
if not output_policy.get('summary_budgets'):
    errors.append('output_policy.summary_budgets is missing')
profiles=input_policy.get('stage_profiles') or {}
for step in ('03','04','05','06','07','08','09','10'):
    profile=profiles.get(step)
    if not profile:
        errors.append(f'input_policy missing stage profile: {step}')
        continue
    lean=profile.get('lean') or []
    on_demand=profile.get('on_demand') or []
    max_files=profile.get('max_files')
    if not lean:
        errors.append(f'input_policy {step}: lean must be non-empty')
    if not on_demand:
        errors.append(f'input_policy {step}: on_demand must be non-empty')
    if not isinstance(max_files,int) or max_files<1:
        errors.append(f'input_policy {step}: max_files must be a positive integer')
    elif len(lean)>max_files:
        errors.append(f'input_policy {step}: lean has {len(lean)} entries, exceeding max_files={max_files}')
    for name,items in (('lean',lean),('on_demand',on_demand)):
        for item in items:
            if not str(item).strip():
                errors.append(f'input_policy {step}: empty {name} entry')
if not output_policy.get('principle'):
    errors.append('output_policy.principle is missing')
if not output_policy.get('rules'):
    errors.append('output_policy.rules is missing')
if not output_policy.get('stage_focus'):
    errors.append('output_policy.stage_focus is missing')
if not (ROOT/'templates/workflow/step-handoff-report.md').is_file(): errors.append('missing handoff report template')
if errors:
    print('Step contract check failed:')
    for e in errors: print('ERROR:',e)
    sys.exit(1)
print(f'Step contracts passed: {len(seen)} rows aligned with {len(stages)} DAG stages; all Skills, Prompts and handoff report template linked.')
