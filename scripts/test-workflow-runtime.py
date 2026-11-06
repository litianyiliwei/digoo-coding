#!/usr/bin/env python3
"""Regression tests for workflow state machine and SHA-256 handoff guards."""
import importlib.util, json, tempfile, unittest
from pathlib import Path

SCRIPT=Path(__file__).with_name('workflow.py')
spec=importlib.util.spec_from_file_location('workflow_runtime',SCRIPT)
w=importlib.util.module_from_spec(spec); spec.loader.exec_module(w)

class WorkflowRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        w.ROOT=self.root; w.STATE=self.root/'workflow-state.json'
        (self.root/'workflow').mkdir()
        (self.root/'docs').mkdir()
        state={'project_name':'test','active_change_id':'','completed_steps':[],'current_step':'01-project-bootstrap','pending_approvals':[],'blocked_items':[],'last_completed_outputs':[]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        (self.root/'out.md').write_text('baseline output v1',encoding='utf-8')
        (self.root/'check.log').write_text('PASS\n',encoding='utf-8')
    def tearDown(self): self.tmp.cleanup()
    def test_first_transition_creates_hash_handoff_and_advances(self):
        state=w.load_state()
        self.assertEqual([],w.check_entry('01-project-bootstrap',state))
        evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'out.md','status':'created','required':True}],
                  'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python3 check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'required':False,'status':'not-required'}}
        ep=self.root/'evidence.json'; ep.write_text(json.dumps(evidence),encoding='utf-8')
        args=type('Args',(),{'step':'01-project-bootstrap','evidence':str(ep),'change_id':None})()
        self.assertEqual(0,w.cmd_transition(args))
        state=w.load_state()
        self.assertEqual('02-requirements-analysis',state['current_step'])
        self.assertIn('01-project-bootstrap',state['completed_steps'])
        manifest=self.root/'workflow/handoffs/project/01-project-bootstrap--02-requirements-analysis.json'
        ok,errors=w.verify_manifest(manifest)
        self.assertTrue(ok,errors)
        self.assertEqual([],w.check_entry('02-requirements-analysis',state))
    def test_state_file_output_hash_is_taken_after_atomic_transition(self):
        state=w.load_state()
        evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'workflow-state.json','status':'updated'}],
                  'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python3 check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'status':'not-required'}}
        ep=self.root/'state-evidence.json'; ep.write_text(json.dumps(evidence),encoding='utf-8')
        args=type('Args',(),{'step':'01-project-bootstrap','evidence':str(ep),'change_id':None})()
        self.assertEqual(0,w.cmd_transition(args))
        manifest=self.root/'workflow/handoffs/project/01-project-bootstrap--02-requirements-analysis.json'
        ok,errors=w.verify_manifest(manifest)
        self.assertTrue(ok,errors)

    def test_modified_artifact_blocks_downstream_entry(self):
        state=w.load_state()
        evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'out.md','status':'created'}],
                  'checks':[{'name':'lint','status':'passed','command':'python3 check.py','exit_code':0,'log':'check.log'}], 'approval':{'status':'not-required'}}
        ep=self.root/'evidence.json'; ep.write_text(json.dumps(evidence),encoding='utf-8')
        args=type('Args',(),{'step':'01-project-bootstrap','evidence':str(ep),'change_id':None})()
        self.assertEqual(0,w.cmd_transition(args))
        (self.root/'out.md').write_text('silently modified',encoding='utf-8')
        errors=w.check_entry('02-requirements-analysis',w.load_state())
        self.assertTrue(any('Hash mismatch' in e for e in errors),errors)
    def test_dependency_guard_blocks_skipped_stage(self):
        state=w.load_state()
        errors=w.check_entry('03-project-architecture-baseline',state,verify_handoffs=False)
        self.assertTrue(any('Uncompleted dependencies' in e for e in errors),errors)
    def test_project_proposal_entry_runs_frozen_baseline_guard(self):
        state={'project_name':'test','active_change_id':'','completed_steps':['02-requirements-analysis','03-project-architecture-baseline'],
               'current_step':'04-proposal-planning','pending_approvals':[],'blocked_items':[],'last_completed_outputs':[]}
        calls=[]
        original=w.run_baseline_gate
        w.run_baseline_gate=lambda args,label: calls.append((args,label)) or ''
        try:
            errors=w.check_entry('04-proposal-planning',state,verify_handoffs=False)
        finally:
            w.run_baseline_gate=original
        self.assertEqual([],errors)
        self.assertEqual(['audit','--require-frozen'],calls[0][0])

    def test_feature_entry_runs_manifest_and_change_binding_guards(self):
        state={'project_name':'test','active_change_id':'demo-feature','completed_steps':['04-proposal-planning'],
               'current_step':'05-feature-requirements','pending_approvals':[],'blocked_items':[],'last_completed_outputs':[]}
        calls=[]
        original=w.run_baseline_gate
        w.run_baseline_gate=lambda args,label: calls.append(args) or ''
        try:
            errors=w.check_entry('05-feature-requirements',state,verify_handoffs=False)
        finally:
            w.run_baseline_gate=original
        self.assertEqual([],errors)
        self.assertEqual(['audit','--require-frozen'],calls[0])
        self.assertEqual(['check-change','--change-id','demo-feature','--phase','requirement'],calls[1])

    def test_baseline_freeze_transition_requires_manifest_and_registry_outputs(self):
        state={'project_name':'test','active_change_id':'','completed_steps':['02-requirements-analysis'],
               'current_step':'03-project-architecture-baseline','pending_approvals':[],'blocked_items':[],'last_completed_outputs':[]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        (self.root/'docs/architecture').mkdir(parents=True,exist_ok=True)
        (self.root/'docs/architecture/baseline-manifest.json').write_text('{}',encoding='utf-8')
        (self.root/'docs/architecture/constraint-registry.json').write_text('{}',encoding='utf-8')
        calls=[]
        original_check,original_gate=w.check_entry,w.run_baseline_gate
        w.check_entry=lambda *a,**k: []
        w.run_baseline_gate=lambda args,label: calls.append(args) or ''
        try:
            evidence={'step_id':'03-project-architecture-baseline','outputs':[
                {'path':'docs/architecture/baseline-manifest.json','status':'verified'},
                {'path':'docs/architecture/constraint-registry.json','status':'verified'}],
                'checks':[{'name':'baseline-audit','kind':'automated','status':'passed','command':'python3 scripts/baseline-governance.py audit --require-frozen','exit_code':0,'log':'check.log'}],
                'approval':{'required':True,'status':'approved','approver':'Owner','approved_at':'2026-11-03'}}
            ep=self.root/'baseline-evidence.json'; ep.write_text(json.dumps(evidence),encoding='utf-8')
            args=type('Args',(),{'step':'03-project-architecture-baseline','evidence':str(ep),'change_id':None})()
            self.assertEqual(0,w.cmd_transition(args))
        finally:
            w.check_entry,w.run_baseline_gate=original_check,original_gate
        self.assertEqual([['audit','--require-frozen']],calls)
        self.assertIn('03-project-architecture-baseline',w.load_state()['completed_steps'])

    def test_human_approval_required_for_feature_stage(self):
        stage=w.BY_ID['05-feature-requirements']
        self.assertTrue(stage['human_approval_required'])
    def test_feature_transition_rejects_missing_human_approval(self):
        evidence={'step_id':'05-feature-requirements','change_id':'sample-change',
                  'outputs':[{'path':'out.md','status':'verified'}],
                  'checks':[{'name':'gate','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'required':True,'status':'pending'}}
        ep=self.root/'feature-evidence.json'; ep.write_text(json.dumps(evidence),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Human approval required'):
            w.parse_evidence(str(ep),'05-feature-requirements','sample-change')

if __name__=='__main__': unittest.main(verbosity=2)
