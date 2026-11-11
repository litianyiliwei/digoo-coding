#!/usr/bin/env python3
"""Validate declared output consumers and reverse input provenance.

Forward: every file output has a declared consumer (or is evidence-only), each
consumer is a later DAG stage, and the consumer's inputs mention the artifact.
Reverse: every input reference to an artifact produced by an earlier stage must
be registered in that producer's output_consumption record, so an output that is
actually read but not tracked fails the check.
"""
import json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = json.loads((ROOT / 'docs/STEP-ARTIFACT-CONTRACTS.json').read_text(encoding='utf-8'))
STAGES = json.loads((ROOT / 'docs/WORKFLOW-STAGES.json').read_text(encoding='utf-8'))['stages']
ROWS = CONTRACTS['steps']
ORDER = [r['step'] for r in ROWS]
DAG_IDS = {s['id'] for s in STAGES}
SPECIAL = {'ALL', 'SYSTEM', 'GATE', 'FUTURE'}
PATH_RE = re.compile(r'(?:docs|templates|openspec|workflow|prompts|scripts|design)/[A-Za-z0-9_\-./<>*]+')
FILE_RE = re.compile(r'[A-Za-z0-9_\-]+\.(?:md|csv|json|yaml|yml|pen)')


def norm(value):
    return str(value).replace(chr(92), '/').strip().rstrip('。.）)')


def extract(o):
    """Return the first declared file path in an output entry, if any."""
    match = PATH_RE.search(str(o))
    return norm(match.group(0)) if match else None


def input_tokens(text):
    """Collect candidate path/file references from a free-form input entry."""
    tokens = [norm(x) for x in PATH_RE.findall(str(text))]
    tokens += [norm(x) for x in FILE_RE.findall(str(text))]
    return [x for x in tokens if x]


errors = []
records = CONTRACTS.get('output_consumption', [])
if not records:
    errors.append('Missing output_consumption map in docs/STEP-ARTIFACT-CONTRACTS.json')

by_key = {}
for rec in records:
    key = (rec.get('step'), rec.get('artifact'))
    if key in by_key:
        errors.append(f'duplicate output_consumption record: {key}')
    by_key[key] = rec

# Forward: every file output must have a record.
for row in ROWS:
    for output in row.get('outputs', []):
        art = extract(output)
        if not art:
            continue
        if (row['step'], art) not in by_key:
            errors.append(f'{row["step"]}: file output has no consumption record: {art}')

# Forward: consumer relationships must be valid and visible in consumer inputs.
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
        base = os.path.basename(norm(art))
        if not any(art in inp or base in inp for inp in target.get('inputs', [])):
            errors.append(f'{step}: consumer {c} inputs do not reference {art}')

# Producers: artifact path -> earliest step that declares it as an output.
producers = {}
for row in ROWS:
    for output in row.get('outputs', []):
        art = extract(output)
        if art:
            producers.setdefault(art, []).append(row['step'])


def registered_consumers(source_step, artifact):
    return set(by_key.get((source_step, artifact), {}).get('consumed_by', []))


# Reverse: every input reference to an earlier-produced artifact must be registered.
seen = set()
for row in ROWS:
    consumer = row['step']
    if consumer == '00':
        # The orchestrator reads package-static process docs and runtime state,
        # not stage outputs; its handoff is the selected stage's input contract.
        continue
    for text in row.get('inputs', []):
        for token in input_tokens(text):
            if '*' in token:
                continue
            if token.startswith('openspec/specs/'):
                # Main specs come from archive/acceptance, an external state.
                continue
            base = os.path.basename(token)
            candidates = [(s, art) for art, steps in producers.items() for s in steps
                          if norm(art) == token or os.path.basename(norm(art)) == base]
            candidates = [(s, art) for s, art in candidates if ORDER.index(s) < ORDER.index(consumer)]
            if not candidates:
                continue
            source, artifact = min(candidates, key=lambda pair: ORDER.index(pair[0]))
            key = (source, artifact, consumer)
            if consumer in registered_consumers(source, artifact) or key in seen:
                continue
            seen.add(key)
            errors.append(f'{source} -> {consumer}: input references {artifact} '
                          f'but output_consumption does not register this consumer')

# Guard: Change-scoped design artifacts named as inputs must have an earlier producer.
# Without this, an input like design/design-tokens.json can be read forever while no
# stage declares who creates it (the original reverse check silently skips such tokens).
for row in ROWS:
    if row['step'] == '00':
        continue
    for text in row.get('inputs', []):
        for token in input_tokens(text):
            if '*' in token:
                continue
            if not (token.startswith('openspec/changes/') or token.startswith('design/')):
                continue
            base = os.path.basename(token)
            candidates = [(s, art) for art, steps in producers.items() for s in steps
                          if norm(art) == token or os.path.basename(norm(art)) == base]
            candidates = [(s, art) for s, art in candidates if ORDER.index(s) < ORDER.index(row['step'])]
            if not candidates:
                errors.append(f'{row["step"]}: input {token} has no producer in an earlier stage')

for e in errors:
    print('ERROR:', e)
if errors:
    print(f'Output consumption check failed: {len(errors)} error(s).')
    sys.exit(1)
print(f'Output consumption check passed: {len(records)} file output(s), '
      f'{sum(1 for r in records if r.get("evidence_only"))} evidence-only, '
      f'{len(producers)} producer path(s).')