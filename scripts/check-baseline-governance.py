#!/usr/bin/env python3
"""Check that baseline/feature governance is wired into package artifacts."""
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
required_files = [
    'docs/BASELINE-FEATURE-INTERACTION.md',
    'templates/change-assets/design/baseline-impact.md',
    'templates/project-baseline/baseline-status.md',
    'templates/project-baseline/baseline-change-request.md',
    'docs/architecture/baseline-status.md',
]
for rel in required_files:
    if not (ROOT / rel).is_file():
        errors.append(f'missing required baseline governance file: {rel}')

contracts_path = ROOT / 'docs/STEP-ARTIFACT-CONTRACTS.json'
contracts = json.loads(contracts_path.read_text(encoding='utf-8'))
if 'baseline_feature_interaction' not in contracts:
    errors.append('STEP-ARTIFACT-CONTRACTS.json missing baseline_feature_interaction policy')
by_skill = {row.get('skill'): row for row in contracts.get('steps', [])}
feature = by_skill.get('feature-requirements', {})
if not any('baseline-impact.md' in x for x in feature.get('outputs', [])):
    errors.append('feature-requirements contract must output design/baseline-impact.md')
for sid in ('proposal-planning','feature-requirements','feature-design','api-contract-design',
            'frontend-detail-design','backend-detail-design','test-design',
            'implementation-orchestrator','acceptance-audit','baseline-audit'):
    p = ROOT / '.claude/skills' / sid / 'SKILL.md'
    if not p.is_file():
        p = ROOT / '.agents/skills' / sid / 'SKILL.md'
    if not p.is_file():
        errors.append(f'missing Skill for baseline interaction: {sid}')
        continue
    body = p.read_text(encoding='utf-8')
    if 'BASELINE-FEATURE-INTERACTION.md' not in body and '基线' not in body:
        errors.append(f'Skill does not mention baseline interaction: {sid}')
for fn in ('04-proposal-planning.md','05-feature-requirements.md','09-feature-design.md',
           '10-api-contract-design.md','11-frontend-detail-design.md',
           '12-backend-detail-design.md','13-test-design.md',
           '14-implementation-orchestrator.md','16-acceptance-audit.md'):
    p = ROOT / 'prompts' / fn
    if not p.is_file() or '基线交互要求' not in p.read_text(encoding='utf-8'):
        errors.append(f'Prompt missing explicit baseline interaction instructions: {fn}')

state = json.loads((ROOT/'workflow-state.json').read_text(encoding='utf-8'))
if not isinstance(state.get('baseline'), dict) or 'domains' not in state['baseline']:
    errors.append('workflow-state.json missing baseline domain/version index')

matrix = (ROOT/'docs/OUTPUT-TEMPLATE-MATRIX.csv').read_text(encoding='utf-8-sig')
for rel in ('templates/change-assets/design/baseline-impact.md',
            'templates/project-baseline/baseline-status.md',
            'templates/project-baseline/baseline-change-request.md'):
    if rel not in matrix:
        errors.append(f'OUTPUT-TEMPLATE-MATRIX.csv does not register {rel}')

if errors:
    print('Baseline governance check failed:')
    for e in errors:
        print('ERROR:', e)
    sys.exit(1)
print('Baseline governance check passed: policy, templates, contracts, skills, prompts, workflow state and template registry.')
