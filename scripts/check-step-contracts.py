#!/usr/bin/env python3
"""Check one-to-one workflow step contracts against Skill and Prompt files."""
from pathlib import Path
import json, re, sys
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'process/STEP-ARTIFACT-CONTRACTS.json').read_text(encoding='utf-8'))
stages=json.loads((ROOT/'process/WORKFLOW-STAGES.json').read_text(encoding='utf-8'))['stages']
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
    elif '## 输入/输出/交接契约（强制）' not in skill.read_text(encoding='utf-8') and '## Input/Output/Handoff Contract' not in skill.read_text(encoding='utf-8'): errors.append(f'Skill missing handoff contract section: {sid}')
    if not prompt.is_file(): errors.append(f'missing Prompt: {row.get("prompt")}')
    elif '## 强制交付物交接' not in prompt.read_text(encoding='utf-8') and '## Mandatory Deliverable Handoff' not in prompt.read_text(encoding='utf-8'): errors.append(f'Prompt missing handoff contract section: {row.get("prompt")}')
# Cross-check contract rows against the authoritative stage DAG (process/WORKFLOW-STAGES.json).
# workflow-orchestrator is the "next step" entry point, intentionally not a DAG stage.
ORCHESTRATOR_SKILLS={'workflow-orchestrator'}
dag_skills={s['skill'] for s in stages}
if dag_skills|ORCHESTRATOR_SKILLS!=seen:
    errors.append(f'Contract/DAG skill mismatch: contract-only={sorted(seen-dag_skills)} dag-only={sorted(dag_skills-seen)}')
for s in stages:
    row=contract_by_skill.get(s['skill'])
    if row and row.get('prompt')!=s['prompt']:
        errors.append(f"Prompt path mismatch for {s['skill']}: contract={row.get('prompt')} dag={s['prompt']}")
    if s.get('conditional') and not (row or {}).get('conditional'):
        errors.append(f"Conditional DAG stage has no contract conditional spec: {s['id']}")
    if (row or {}).get('conditional') and not s.get('conditional'):
        errors.append(f"Contract declares a conditional spec for a non-conditional DAG stage: {s['id']}")
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
# Method evidence deliberately does not enforce question/alternative/decision
# counts or topic keywords; the policy only declares required skills and
# whether their conclusions must land in an artifact section.
# Validate the question-coverage policy: 02/03/05/07 carry it, every required
# The question-coverage checklist is recommended guidance, not a hard
# item-by-item gate. Verify the checklist files exist and that the four guided
# stages reference the checklist in their Skill and Prompt.
coverage=data.get('question_coverage_policy') or {}
for key in ('checklist','checklist_zh'):
    rel=str(coverage.get(key) or '')
    path=ROOT/rel if rel else None
    if not rel or not path or not path.is_file():
        errors.append(f'question_coverage_policy.{key} is missing or unreadable: '+rel)
checklist_rel=str(coverage.get('checklist') or '')
checklist_path=ROOT/checklist_rel if checklist_rel else None
if checklist_path and checklist_path.is_file():
    checklist_text=checklist_path.read_text(encoding='utf-8')
    for prefix in ('02','03','05','07'):
        if not re.search(r'\| '+prefix+r'-T\d{2}-\d{2} \|', checklist_text):
            errors.append(f'question coverage checklist has no items for stage {prefix}')
for key in ('02','03','05','07'):
    row=next((r for r in data['steps'] if str(r.get('step'))==key), None)
    if not row:
        errors.append(f'question coverage stage has no contract row: {key}')
        continue
    sid=row.get('skill')
    skill_file=SKILLS_DIR/sid/'SKILL.md'
    prompt_file=ROOT/row.get('prompt','')
    skill_text=skill_file.read_text(encoding='utf-8') if skill_file.is_file() else ''
    prompt_text=prompt_file.read_text(encoding='utf-8') if prompt_file.is_file() else ''
    if 'QUESTION-COVERAGE-CHECKLIST' not in skill_text:
        errors.append(f'question coverage: Skill {sid} does not reference process/QUESTION-COVERAGE-CHECKLIST.md')
    if 'QUESTION-COVERAGE-CHECKLIST' not in prompt_text:
        errors.append(f'question coverage: Prompt {row.get("prompt")} does not reference process/QUESTION-COVERAGE-CHECKLIST.md')
# Validate lean-context policies: every requirements/design/Change stage has a
# lean default read set within its declared file budget, plus on-demand inputs.
input_policy=data.get('input_policy') or {}
output_policy=data.get('output_policy') or {}
if not input_policy.get('stage_profiles'):
    errors.append('input_policy.stage_profiles is missing')
if not output_policy.get('summary_budgets'):
    errors.append('output_policy.summary_budgets is missing')
profiles=input_policy.get('stage_profiles') or {}
for step in ('02','03','04','05','06','07','08','09','10'):
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
    if 'max_files' in profile and (not isinstance(max_files,int) or max_files<1):
        errors.append(f'input_policy {step}: max_files must be a positive integer when present')
# max_files is an advisory guideline; lean may exceed it when the stage records
# why the extra reads are needed.
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
# Guard the hand-maintained human contract table against drift from the machine
# contract: every declared docs/ or openspec/ artifact path must appear in the
# matching step row. CI previously validated only the JSON.
CONTRACTS_MD=ROOT/'process/STEP-ARTIFACT-CONTRACTS.md'
ARTIFACT_RE=re.compile(r'(?:docs/|openspec/)[A-Za-z0-9_./<>-]+?\.(?:md|csv|json|ya?ml)')
if not CONTRACTS_MD.is_file():
    errors.append('missing contract document: process/STEP-ARTIFACT-CONTRACTS.md')
else:
    md_lines=CONTRACTS_MD.read_text(encoding='utf-8').splitlines()
    try:
        start=md_lines.index('## Stage Contract Master Table')
    except ValueError:
        start=0
        errors.append('contract md missing "## Stage Contract Master Table" heading')
    table_lines=md_lines[start:]
    def md_row(step):
        for line in table_lines:
            if re.match(r'^\|\s*'+re.escape(str(step))+r'\s', line):
                return line
        return None
    for row in data.get('steps',[]):
        step=str(row.get('step'))
        line=md_row(step)
        if line is None:
            errors.append(f'contract md has no table row for step {step}')
            continue
        for kind in ('outputs','inputs'):
            for entry in row.get(kind,[]):
                for token in ARTIFACT_RE.findall(str(entry)):
                    if token not in line:
                        errors.append(f'contract md step {step} {kind} omits {token}')
if errors:
    print('Step contract check failed:')
    for e in errors: print('ERROR:',e)
    sys.exit(1)
print(f'Step contracts passed: {len(seen)} rows aligned with {len(stages)} DAG stages; all Skills, Prompts and handoff report template linked.')
