#!/usr/bin/env python3
"""Validate independent verification report and machine-readable evidence."""
import argparse,json,sys
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--report',required=True); p.add_argument('--evidence',required=True); a=p.parse_args()
root=Path(__file__).resolve().parents[1]
def resolve(raw):
 x=Path(raw); x=(root/x).resolve() if not x.is_absolute() else x.resolve(); x.relative_to(root.resolve()); return x
try:
 report=resolve(a.report); evidence=resolve(a.evidence)
 if not report.is_file() or not evidence.is_file(): raise ValueError('Report and evidence JSON must both exist')
 md=report.read_text(encoding='utf-8'); d=json.loads(evidence.read_text(encoding='utf-8'))
 required=['change_id','verdict','source_revision','revision_stable','read_only','verifier_identity','builder_identity','acceptance_checks','test_runs','findings']
 missing=[k for k in required if k not in d]
 if missing: raise ValueError('Missing evidence fields: '+', '.join(missing))
 errors=[]
 if d['verdict']!='PASS': errors.append('verdict is not PASS')
 if not d['source_revision']: errors.append('source_revision is empty')
 if d['revision_stable'] is not True: errors.append('revision_stable must be true')
 if d['read_only'] is not True: errors.append('read_only must be true')
 if not d['verifier_identity'] or not d['builder_identity'] or d['verifier_identity']==d['builder_identity']: errors.append('verifier_identity and builder_identity must be present and distinct')
 if not d['acceptance_checks']: errors.append('acceptance_checks is empty')
 for ac in d['acceptance_checks']:
  if not ac.get('id') or ac.get('result')!='PASS' or not ac.get('evidence'): errors.append(f"AC not independently passed: {ac.get('id','<missing>')}")
 if not d['test_runs']: errors.append('test_runs is empty')
 for t in d['test_runs']:
  if not t.get('command') or t.get('exit_code')!=0: errors.append(f"Test command failed or missing exit code: {t.get('command','<missing>')}")
  if not t.get('log'): errors.append(f"Test run log is missing: {t.get('command','<missing>')}")
  else:
   lp=Path(t['log']); lp=(root/lp).resolve() if not lp.is_absolute() else lp.resolve()
   try: lp.relative_to(root.resolve())
   except ValueError: errors.append('Test log path escapes project root')
   else:
    if not lp.is_file(): errors.append(f"Test log file does not exist: {t['log']}")
 blockers=[f for f in d['findings'] if f.get('severity') in ('BLOCKER','CRITICAL')]
 if blockers: errors.append(f'{len(blockers)} blocker/critical finding(s) remain')
 if not any(x in md for x in ('判定：PASS','Verdict: PASS','Verdict：PASS')): errors.append('Markdown report does not state PASS')
 for heading in ('## 1. 验证范围','## 2. 验收标准','## 3. 测试与检查','## 7. 最终判定'):
  if heading not in md: errors.append(f'Markdown report missing section: {heading}')
 if errors:
  print('INDEPENDENT_VERIFICATION_FAILED'); [print(' - '+e) for e in errors]; sys.exit(3)
 print(f"INDEPENDENT_VERIFICATION_PASS change_id={d['change_id']} AC={len(d['acceptance_checks'])} tests={len(d['test_runs'])}")
except Exception as e:
 print(f'ERROR: {e}',file=sys.stderr); sys.exit(2)
