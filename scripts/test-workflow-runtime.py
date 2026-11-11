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

    def _write_evidence(self, name, payload):
        ep=self.root/name; ep.write_text(json.dumps(payload),encoding='utf-8'); return ep

    def _transition(self, step, evidence):
        args=type('Args',(),{'step':step,'evidence':str(evidence),'change_id':None})()
        return w.cmd_transition(args)

    def test_own_pending_approval_does_not_deadlock_transition(self):
        state=w.load_state()
        state['pending_approvals']=[{'step_id':'01-project-bootstrap','artifact':'out.md','reason':'awaiting approval'}]
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'out.md','status':'created'}],
                  'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'required':True,'status':'approved','approver':'Owner','approved_at':'2026-11-10'}}
        ep=self._write_evidence('approval-evidence.json',evidence)
        self.assertEqual(0,self._transition('01-project-bootstrap',ep))
        state=w.load_state()
        self.assertEqual('02-requirements-analysis',state['current_step'])
        self.assertEqual([],state['pending_approvals'])

    def test_own_blocked_item_can_be_resolved_with_evidence(self):
        state=w.load_state()
        state['blocked_items']=[{'step_id':'01-project-bootstrap','reason':'awaiting external input'}]
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'out.md','status':'created'}],
                  'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'status':'not-required'},
                  'resolved_blockers':[{'step_id':'01-project-bootstrap','resolution':'external input received','evidence':'check.log'}]}
        ep=self._write_evidence('resolved-blocker-evidence.json',evidence)
        self.assertEqual(0,self._transition('01-project-bootstrap',ep))
        state=w.load_state()
        self.assertEqual([],state['blocked_items'])

    def test_own_blocked_item_requires_resolved_evidence(self):
        state=w.load_state()
        state['blocked_items']=[{'step_id':'01-project-bootstrap','reason':'awaiting external input'}]
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'out.md','status':'created'}],
                  'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'status':'not-required'}}
        ep=self._write_evidence('blocked-evidence.json',evidence)
        self.assertEqual(3,self._transition('01-project-bootstrap',ep))

    def test_own_pending_approval_requires_approved_evidence(self):
        state=w.load_state()
        state['pending_approvals']=[{'step_id':'01-project-bootstrap','artifact':'out.md'}]
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'out.md','status':'created'}],
                  'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'status':'not-required'}}
        ep=self._write_evidence('unapproved-evidence.json',evidence)
        with self.assertRaisesRegex(ValueError,'requires approved evidence'):
            self._transition('01-project-bootstrap',ep)

    def test_reopen_removes_stage_and_all_dependents(self):
        state={'project_name':'test','active_change_id':'','completed_steps':['01-project-bootstrap','02-requirements-analysis','03-project-architecture-baseline'],
               'current_step':'04-proposal-planning','pending_approvals':[{'step_id':'03-project-architecture-baseline'}],
               'blocked_items':[],'last_completed_outputs':[]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        args=type('Args',(),{'step':'02-requirements-analysis','reason':'requirement rework','note':''})()
        self.assertEqual(0,w.cmd_reopen(args))
        state=w.load_state()
        self.assertEqual(['01-project-bootstrap'],state['completed_steps'])
        self.assertEqual('02-requirements-analysis',state['current_step'])
        self.assertEqual([],state['pending_approvals'])
        removed=state['reopen_history'][0]['removed_steps']
        self.assertIn('03-project-architecture-baseline',removed)
        self.assertIn('04-proposal-planning',removed)

    def test_next_change_archives_change_phase_and_reopens_stage_05(self):
        change_steps=[s['id'] for s in w.STAGES if s['scope']=='change']
        state={'project_name':'test','active_change_id':'change-a','completed_steps':[s['id'] for s in w.STAGES],
               'current_step':'ALL_STEPS_COMPLETE','pending_approvals':[],'blocked_items':[],
               'last_completed_outputs':[],'transition_history':[
                   {'step_id':'10-acceptance-audit','change_id':'change-a','completed_at':'2026-11-10T00:00:00+00:00','evidence_path':'workflow/evidence/10.json'}]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        args=type('Args',(),{'change_id':'change-b','note':''})()
        self.assertEqual(0,w.cmd_next_change(args))
        state=w.load_state()
        self.assertEqual('change-b',state['active_change_id'])
        self.assertEqual('05-feature-requirements',state['current_step'])
        self.assertFalse(any(x in state['completed_steps'] for x in change_steps))
        self.assertIn('04-proposal-planning',state['completed_steps'])
        self.assertEqual('change-a',state['completed_changes'][0]['change_id'])

    def test_declared_downstream_output_is_mutable_in_handoff(self):
        contract={'steps':[{'step':'01','outputs':['docs/out.md']},{'step':'05','outputs':['docs/out.md']}]}
        (self.root/'docs/STEP-ARTIFACT-CONTRACTS.json').write_text(json.dumps(contract),encoding='utf-8')
        (self.root/'docs/out.md').write_text('v1',encoding='utf-8')
        evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'docs/out.md','status':'created'}],
                  'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'status':'not-required'}}
        ep=self._write_evidence('mutable-evidence.json',evidence)
        self.assertEqual(0,self._transition('01-project-bootstrap',ep))
        manifest=self.root/'workflow/handoffs/project/01-project-bootstrap--02-requirements-analysis.json'
        self.assertTrue(w.verify_manifest(manifest)[0])
        (self.root/'docs/out.md').write_text('v2 from downstream stage',encoding='utf-8')
        ok,errors=w.verify_manifest(manifest)
        self.assertTrue(ok,errors)

    def test_transition_requires_all_declared_outputs_or_explicit_na_waiver(self):
        contract={'steps':[{'step':'01','outputs':['docs/a.md','docs/b.md']}]}
        (self.root/'docs/STEP-ARTIFACT-CONTRACTS.json').write_text(json.dumps(contract),encoding='utf-8')
        (self.root/'docs/a.md').write_text('a',encoding='utf-8')
        evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'docs/a.md','status':'created'}],
                  'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'status':'not-required'}}
        ep=self._write_evidence('missing-output-evidence.json',evidence)
        with self.assertRaisesRegex(ValueError,'omits declared stage outputs'):
            self._transition('01-project-bootstrap',ep)
        evidence['outputs'].append({'path':'docs/b.md','status':'n/a','required':False,'waiver_reason':'not applicable'})
        ep=self._write_evidence('waived-output-evidence.json',evidence)
        self.assertEqual(0,self._transition('01-project-bootstrap',ep))

if __name__=='__main__': unittest.main(verbosity=2)
