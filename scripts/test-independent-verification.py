#!/usr/bin/env python3
"""Regression tests for independent-verifier evidence gate."""
import json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
checker=ROOT/'scripts/check-independent-verification.py'
with tempfile.TemporaryDirectory(dir=ROOT/'scripts') as td:
    d=Path(td); report=d/'report.md'; evidence=d/'evidence.json'
    (d/'test.log').write_text('1 passed\n',encoding='utf-8')
    report.write_text('判定：PASS\n## 1. 验证范围\n## 2. 验收标准\n## 3. 测试与检查\n## 7. 最终判定\n',encoding='utf-8')
    payload={'change_id':'test-change','verdict':'PASS','source_revision':'abc123','revision_stable':True,'read_only':True,'verifier_identity':'verifier-session','builder_identity':'builder-session',
             'acceptance_checks':[{'id':'AC-1','result':'PASS','evidence':'tests/test_ac.py::test_ok'}],
             'test_runs':[{'command':'pytest -q','exit_code':0,'log':str(d/'test.log')}],'findings':[]}
    evidence.write_text(json.dumps(payload),encoding='utf-8')
    cmd=[sys.executable,str(checker),'--report',str(report),'--evidence',str(evidence)]
    good=subprocess.run(cmd,capture_output=True,text=True)
    if good.returncode: raise SystemExit('Expected PASS but failed: '+good.stdout+good.stderr)
    payload['test_runs'][0]['exit_code']=1
    evidence.write_text(json.dumps(payload),encoding='utf-8')
    bad=subprocess.run(cmd,capture_output=True,text=True)
    if bad.returncode==0: raise SystemExit('Expected failing test evidence to be rejected')
    payload['test_runs'][0]['exit_code']=0; payload['read_only']=False
    evidence.write_text(json.dumps(payload),encoding='utf-8')
    bad2=subprocess.run(cmd,capture_output=True,text=True)
    if bad2.returncode==0: raise SystemExit('Expected non-read-only verifier evidence to be rejected')
print('Independent verifier regression tests passed.')
