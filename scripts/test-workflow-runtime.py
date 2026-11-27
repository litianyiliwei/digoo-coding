#!/usr/bin/env python3
"""Regression tests for workflow state machine and SHA-256 handoff guards."""
import contextlib, importlib.util, io, json, subprocess, sys, tempfile, unittest
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
        (self.root/'process').mkdir()
        state={'project_name':'test','active_change_id':'','completed_steps':[],'current_step':'01-project-bootstrap','pending_approvals':[],'blocked_items':[],'last_completed_outputs':[],
               'approvals_history':[{'step_id':'01-project-bootstrap','change_id':'','approver':'用户','approved_at':'2026-11-13','evidence':'check.log','targets':[]}]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        (self.root/'out.md').write_text('baseline output v1',encoding='utf-8')
        (self.root/'check.log').write_text('PASS\n',encoding='utf-8')
        review_evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'out.md','status':'created','required':True}],
                         'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python3 check.py','exit_code':0,'log':'check.log'}],
                         'approval':{'required':False,'status':'not-required'}}
        (self.root/'review-evidence.json').write_text(json.dumps(review_evidence),encoding='utf-8')
    def tearDown(self): self.tmp.cleanup()

    def test_recover_state_restores_backup_and_logs(self):
        backup = self.root / "backup.json"
        backup.write_bytes(self.root.joinpath("workflow-state.json").read_bytes())
        self.root.joinpath("workflow-state.json").write_text("{ broken", encoding="utf-8")
        args = type("Args", (), {"backup": str(backup), "reason": "test"})()
        self.assertEqual(0, w.cmd_recover_state(args))
        state = w.load_state()
        self.assertEqual("01-project-bootstrap", state["current_step"])
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

    def test_feature_entry_requires_frozen_project_baseline(self):
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
        self.assertEqual([['audit','--require-frozen']],calls)

    def test_implementation_entry_rechecks_strict_baseline_impact(self):
        state={'project_name':'test','active_change_id':'demo-feature',
               'completed_steps':['07-detailed-design'],
               'current_step':'08-implementation-orchestrator','pending_approvals':[],
               'blocked_items':[],'last_completed_outputs':[]}
        calls=[]
        original_gate,original_impact=w.run_baseline_gate,w.run_baseline_impact_gate
        w.run_baseline_gate=lambda args,label: calls.append(('baseline',args)) or ''
        w.run_baseline_impact_gate=lambda change_id: calls.append(('impact',change_id)) or ''
        try:
            errors=w.check_entry('08-implementation-orchestrator',state,verify_handoffs=False)
        finally:
            w.run_baseline_gate,w.run_baseline_impact_gate=original_gate,original_impact
        self.assertEqual([],errors)
        self.assertIn(('impact','demo-feature'),calls)

    def test_implementation_entry_blocks_when_impact_decision_is_not_approved(self):
        state={'project_name':'test','active_change_id':'demo-feature',
               'completed_steps':['07-detailed-design'],
               'current_step':'08-implementation-orchestrator','pending_approvals':[],
               'blocked_items':[],'last_completed_outputs':[]}
        original_gate,original_impact=w.run_baseline_gate,w.run_baseline_impact_gate
        w.run_baseline_gate=lambda args,label: ''
        w.run_baseline_impact_gate=lambda change_id: (_ for _ in ()).throw(ValueError('decision says NO'))
        try:
            errors=w.check_entry('08-implementation-orchestrator',state,verify_handoffs=False)
        finally:
            w.run_baseline_gate,w.run_baseline_impact_gate=original_gate,original_impact
        self.assertTrue(any('decision says NO' in error for error in errors),errors)

    def test_baseline_freeze_transition_requires_manifest_and_registry_outputs(self):
        state={'project_name':'test','active_change_id':'','completed_steps':['02-requirements-analysis'],
               'current_step':'03-project-architecture-baseline','pending_approvals':[],'blocked_items':[],
               'last_completed_outputs':[],'approvals_history':[
                   {'step_id':'03-project-architecture-baseline','approver':'Owner','approved_at':'2026-11-03','evidence':'check.log'}]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        (self.root/'docs/architecture').mkdir(parents=True,exist_ok=True)
        (self.root/'docs/architecture/baseline-manifest.json').write_text('{}',encoding='utf-8')
        (self.root/'docs/architecture/constraint-registry.json').write_text('{}',encoding='utf-8')
        self._write_method_artifact()
        calls=[]
        original_check,original_gate=w.check_entry,w.run_baseline_gate
        w.check_entry=lambda *a,**k: []
        w.run_baseline_gate=lambda args,label: calls.append(args) or ''
        try:
            evidence={'step_id':'03-project-architecture-baseline','outputs':[
                {'path':'docs/architecture/baseline-manifest.json','status':'verified'},
                {'path':'docs/architecture/constraint-registry.json','status':'verified'}],
                'methods':[self._method_entry()],
                'question_coverage':self._coverage('03-project-architecture-baseline'),
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

    def test_builder_and_verifier_stages_require_review(self):
        self.assertTrue(w.BY_ID['08-implementation-orchestrator']['human_approval_required'])
        self.assertTrue(w.BY_ID['09-independent-verification']['human_approval_required'])

    def test_request_review_freezes_current_step(self):
        args=type('Args',(),{'step':'01-project-bootstrap','change_id':None,'summary':'ready for review','target':[],'evidence':'review-evidence.json'})()
        self.assertEqual(0,w.cmd_request_review(args))
        state=w.load_state()
        self.assertEqual('01-project-bootstrap',state['current_step'])
        self.assertEqual(['01-project-bootstrap'],[w.item_step(x) for x in state['pending_approvals']])
        errors=w.check_entry('02-requirements-analysis',state,verify_handoffs=False)
        self.assertTrue(any('Pending approvals' in e for e in errors),errors)

    def test_approve_clears_pending_and_records_user_approval(self):
        args=type('Args',(),{'step':'01-project-bootstrap','change_id':None,'summary':'ready','target':[],'evidence':'review-evidence.json'})()
        self.assertEqual(0,w.cmd_request_review(args))
        approve_args=type('Args',(),{'step':'01-project-bootstrap','change_id':None,
                                     'approver':'用户','approved_at':'2026-11-13','evidence':'check.log'})()
        self.assertEqual(0,w.cmd_approve(approve_args))
        state=w.load_state()
        self.assertEqual([],state['pending_approvals'])
        self.assertEqual('01-project-bootstrap',state['current_step'])
        self.assertEqual('用户',state['approvals_history'][0]['approver'])

    def test_approve_requires_pending_review_request(self):
        approve_args=type('Args',(),{'step':'01-project-bootstrap','change_id':None,
                                     'approver':'用户','approved_at':'2026-11-13','evidence':'check.log'})()
        with self.assertRaisesRegex(ValueError,'No pending review request'):
            w.cmd_approve(approve_args)

    def test_human_stage_transition_requires_recorded_approval(self):
        state={'project_name':'test','active_change_id':'','completed_steps':['02-requirements-analysis'],
               'current_step':'03-project-architecture-baseline','pending_approvals':[],'blocked_items':[],
               'last_completed_outputs':[]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        (self.root/'docs/architecture').mkdir(parents=True,exist_ok=True)
        (self.root/'docs/architecture/baseline-manifest.json').write_text('{}',encoding='utf-8')
        (self.root/'docs/architecture/constraint-registry.json').write_text('{}',encoding='utf-8')
        self._write_method_artifact()
        calls=[]
        original_check,original_gate=w.check_entry,w.run_baseline_gate
        w.check_entry=lambda *a,**k: []
        w.run_baseline_gate=lambda args,label: calls.append(args) or ''
        try:
            evidence={'step_id':'03-project-architecture-baseline','outputs':[
                {'path':'docs/architecture/baseline-manifest.json','status':'verified'},
                {'path':'docs/architecture/constraint-registry.json','status':'verified'}],
                'methods':[self._method_entry()],
                'question_coverage':self._coverage('03-project-architecture-baseline'),
                'checks':[{'name':'baseline-audit','kind':'automated','status':'passed','command':'python3 scripts/baseline-governance.py audit --require-frozen','exit_code':0,'log':'check.log'}],
                'approval':{'required':True,'status':'approved','approver':'Owner','approved_at':'2026-11-03'}}
            ep=self.root/'unapproved-baseline-evidence.json'; ep.write_text(json.dumps(evidence),encoding='utf-8')
            args=type('Args',(),{'step':'03-project-architecture-baseline','evidence':str(ep),'change_id':None})()
            with self.assertRaisesRegex(ValueError,'run request-review'):
                w.cmd_transition(args)
        finally:
            w.check_entry,w.run_baseline_gate=original_check,original_gate

    def test_change_scoped_approval_is_not_reused_across_changes(self):
        state={'approvals_history':[{'step_id':'05-feature-requirements','change_id':'change-a',
                                     'approver':'用户','approved_at':'2026-11-13','evidence':'check.log'}]}
        self.assertIsNone(w.approval_record(state,'05-feature-requirements','change-b'))
        self.assertIsNotNone(w.approval_record(state,'05-feature-requirements','change-a'))

    def test_handoff_create_rejects_approval_bypass_for_human_stage(self):
        self._write_method_artifact()
        evidence={'step_id':'05-feature-requirements','change_id':'sample-change',
                  'outputs':[{'path':'out.md','status':'verified'}],
                  'methods':[self._method_entry(),self._method_entry(skill='baseline-impact-classification')],
                  'checks':[{'name':'gate','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'required':True,'status':'pending'}}
        ep=self._write_evidence('handoff-recovery-evidence.json',evidence)
        args=type('Args',(),{'from_step':'05-feature-requirements','to_step':'06-figma-design-review',
                             'change_id':'sample-change','evidence':str(ep),'baseline_version':''})()
        with self.assertRaisesRegex(ValueError,'recorded user approval'):
            w.cmd_handoff_create(args)

    def test_feature_transition_rejects_missing_human_approval(self):
        self._write_method_artifact()
        evidence={'step_id':'05-feature-requirements','change_id':'sample-change',
                  'outputs':[{'path':'out.md','status':'verified'}],
                  'methods':[self._method_entry(),self._method_entry(skill='baseline-impact-classification')],
                  'checks':[{'name':'gate','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'required':True,'status':'pending'}}
        ep=self.root/'feature-evidence.json'; ep.write_text(json.dumps(evidence),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Human approval required'):
            w.parse_evidence(str(ep),'05-feature-requirements','sample-change')

    def test_question_coverage_is_optional_for_stage_05(self):
        # QUESTION-COVERAGE-CHECKLIST.md is an elicitation aid, not a gate:
        # omitting the block entirely is valid.
        evidence={'step_id':'05-feature-requirements','change_id':'sample-change',
                  'outputs':[{'path':'out.md','status':'verified'}],
                  'methods':[self._method_entry()],
                  'checks':[{'name':'gate','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'required':True,'status':'pending'}}
        errors=w.validate_coverage(evidence,'05-feature-requirements',self.root)
        self.assertEqual([],errors)

    def _write_policy_state(self, current, completed, policy):
        state={'project_name':'test','active_change_id':'','completed_steps':completed,
               'current_step':current,'pending_approvals':[],'blocked_items':[],
               'last_completed_outputs':[],'approvals_history':[],'approval_policy':policy}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        return state

    def test_risk_based_policy_fast_tracks_low_risk_stage(self):
        self._write_policy_state('01-project-bootstrap',[],'risk-based')
        args=type('Args',(),{'step':'01-project-bootstrap','change_id':None,'summary':'ready',
                             'target':[],'evidence':'review-evidence.json'})()
        self.assertEqual(0,w.cmd_request_review(args))
        state=w.load_state()
        self.assertEqual([],state['pending_approvals'])
        self.assertEqual('01-project-bootstrap',state['current_step'])

        evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'out.md','status':'created','required':True}],
                  'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python3 check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'required':True,'status':'pending'}}
        ep=self._write_evidence('risk-based-01-evidence.json',evidence)
        self.assertEqual(0,self._transition('01-project-bootstrap',ep))
        self.assertEqual('02-requirements-analysis',w.load_state()['current_step'])

    def test_risk_based_policy_still_requires_high_risk_stage_approval(self):
        self._write_method_artifact()
        self._write_policy_state('05-feature-requirements',['04-proposal-planning'],'risk-based')
        state=w.load_state(); state['active_change_id']='sample-change'; w.STATE.write_text(json.dumps(state),encoding='utf-8')
        evidence={'step_id':'05-feature-requirements','change_id':'sample-change',
                  'outputs':[{'path':'out.md','status':'verified'}],
                  'methods':[self._method_entry(),self._method_entry(skill='baseline-impact-classification')],
                  'checks':[{'name':'gate','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'required':False,'status':'not-required'}}
        ep=self._write_evidence('risk-based-05-evidence.json',evidence)
        with self.assertRaisesRegex(ValueError,'Human approval required'):
            self._transition('05-feature-requirements',ep)

    def test_standard_policy_still_requires_low_risk_stage_approval(self):
        self._write_policy_state('01-project-bootstrap',[],'standard')
        evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'out.md','status':'created','required':True}],
                  'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python3 check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'required':False,'status':'not-required'}}
        ep=self._write_evidence('standard-01-evidence.json',evidence)
        with self.assertRaisesRegex(ValueError,'Human approval required'):
            self._transition('01-project-bootstrap',ep)

    def test_set_approval_policy_requires_no_pending_review(self):
        args=type('Args',(),{'policy':'risk-based','reason':'single-team project','by':'owner'})()
        self.assertEqual(0,w.cmd_set_approval_policy(args))
        self.assertEqual('risk-based',w.load_state()['approval_policy'])
        state=w.load_state()
        state['pending_approvals']=[{'step_id':'01-project-bootstrap','artifact':'out.md'}]
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'reviews are pending'):
            w.cmd_set_approval_policy(args)

    def test_check_coverage_subcommand_accepts_valid_coverage(self):
        evidence={'step_id':'05-feature-requirements','change_id':None,
                  'question_coverage':[{'item_id':'CUSTOM-01','status':'n/a','reason':'fixture'}]}
        ep=self._write_evidence('coverage-command-evidence.json',evidence)
        args=type('Args',(),{'step':'05-feature-requirements','evidence':str(ep)})()
        self.assertEqual(0,w.cmd_check_coverage(args))

    def test_check_coverage_subcommand_accepts_omitted_block(self):
        evidence={'step_id':'05-feature-requirements','change_id':None}
        ep=self._write_evidence('no-coverage-command-evidence.json',evidence)
        args=type('Args',(),{'step':'05-feature-requirements','evidence':str(ep)})()
        self.assertEqual(0,w.cmd_check_coverage(args))

    def _write_evidence(self, name, payload):
        ep=self.root/name; ep.write_text(json.dumps(payload),encoding='utf-8'); return ep

    def _transition(self, step, evidence):
        args=type('Args',(),{'step':step,'evidence':str(evidence),'change_id':None})()
        return w.cmd_transition(args)

    def test_own_pending_approval_does_not_deadlock_transition(self):
        state=w.load_state()
        state['pending_approvals']=[{'step_id':'01-project-bootstrap','artifact':'out.md','reason':'awaiting approval'}]
        state['approvals_history']=[{'step_id':'01-project-bootstrap','change_id':'','approver':'Owner','approved_at':'2026-11-10','evidence':'check.log','targets':[]}]
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

    def test_own_pending_approval_requires_recorded_approval(self):
        state=w.load_state()
        state['pending_approvals']=[{'step_id':'01-project-bootstrap','artifact':'out.md'}]
        state['approvals_history']=[]
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'out.md','status':'created'}],
                  'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'status':'not-required'}}
        ep=self._write_evidence('unapproved-evidence.json',evidence)
        with self.assertRaisesRegex(ValueError,'Human approval required'):
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

    def test_v1_project_reopen_closes_downstream_change_stages(self):
        state={'project_name':'test','active_change_id':'change-a',
               'completed_steps':[s['id'] for s in w.STAGES],
               'current_step':'ALL_STEPS_COMPLETE','pending_approvals':[],'blocked_items':[],
               'last_completed_outputs':[],
               'approvals_history':[
                   {'step_id':sid,'change_id':'change-a','approver':'Owner',
                    'approved_at':'2026-11-19','evidence':'check.log','targets':[]}
                   for sid in ('05-feature-requirements','06-figma-design-review','07-detailed-design')]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        args=type('Args',(),{'step':'04-proposal-planning','reason':'roadmap rework','note':'','change_id':None})()
        self.assertEqual(0,w.cmd_reopen(args))
        state=w.load_state()
        self.assertEqual(['01-project-bootstrap','02-requirements-analysis','03-project-architecture-baseline'],state['completed_steps'])
        self.assertEqual('04-proposal-planning',state['current_step'])
        history={item['step_id']:item for item in state['approvals_history']}
        for sid in ('05-feature-requirements','06-figma-design-review','07-detailed-design'):
            self.assertTrue(history[sid].get('superseded_at'))

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
        (self.root/'process/STEP-ARTIFACT-CONTRACTS.json').write_text(json.dumps(contract),encoding='utf-8')
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
        (self.root/'process/STEP-ARTIFACT-CONTRACTS.json').write_text(json.dumps(contract),encoding='utf-8')
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

    def _coverage(self, step):
        # Question coverage is optional; an empty block is valid evidence.
        return []

    def _method_entry(self, **overrides):
        entry={'skill':'brainstorming','mode':'stage-scoped','summary':'test methods',
               'questions':['新系统还是基于现有系统二开？','现有系统代码地址（仓库/分支/commit）？','依赖哪些第三方接口？','平台/跨端方案？'],
               'alternatives':['a1','a2'],
               'decisions':['d1'],'open_questions':[],
               'artifact_section':'docs/architecture/technology-decisions.md#1. 技术选型访谈记录',
               'evidence':'docs/architecture/technology-decisions.md'}
        entry.update(overrides)
        return entry

    def _write_method_artifact(self):
        (self.root/'docs/architecture').mkdir(parents=True,exist_ok=True)
        artifact=self.root/'docs/architecture/technology-decisions.md'
        artifact.write_text('# 技术选型决策\n\n## 1. 技术选型访谈记录\n\n- 客户端形态：Web/H5、Android、iOS\n- 跨端方案：uni-app / Flutter / 原生双端\n',encoding='utf-8')
        return artifact

    def test_method_evidence_advisory_for_stage_03(self):
        evidence={'step_id':'03-project-architecture-baseline',
                  'outputs':[{'path':'out.md','status':'created'}],
                  'checks':[{'name':'gate','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'status':'not-required'}}
        errors,warnings=w.validate_methods_detailed(evidence,'03-project-architecture-baseline',self.root)
        self.assertEqual([],errors)
        self.assertTrue(any('brainstorming' in msg for msg in warnings),warnings)

    def test_method_evidence_hard_for_stage_05_and_09(self):
        ev05={'step_id':'05-feature-requirements','methods':[]}
        errors05,_=w.validate_methods_detailed(ev05,'05-feature-requirements',self.root)
        self.assertTrue(any('baseline-impact-classification' in e for e in errors05),errors05)
        ev09={'step_id':'09-independent-verification','methods':[]}
        errors09,_=w.validate_methods_detailed(ev09,'09-independent-verification',self.root)
        self.assertTrue(any('verification-before-completion' in e for e in errors09),errors09)

    def test_method_evidence_passes_with_questions_and_alternatives(self):
        self._write_method_artifact()
        evidence={'step_id':'03-project-architecture-baseline',
                  'methods':[self._method_entry()]}
        errors=w.validate_methods(evidence,'03-project-architecture-baseline',self.root)
        self.assertEqual([],errors)

    def test_equivalent_method_requires_reason(self):
        self._write_method_artifact()
        evidence={'step_id':'03-project-architecture-baseline',
                  'methods':[self._method_entry(mode='equivalent')]}
        errors=w.validate_methods(evidence,'03-project-architecture-baseline',self.root)
        self.assertTrue(any('reason' in e for e in errors),errors)

    def test_method_evidence_requires_artifact_heading(self):
        self._write_method_artifact()
        evidence={'step_id':'03-project-architecture-baseline',
                  'methods':[self._method_entry(artifact_section='docs/architecture/technology-decisions.md#不存在的章节')]}
        errors=w.validate_methods(evidence,'03-project-architecture-baseline',self.root)
        self.assertTrue(any('heading' in e for e in errors),errors)

    def test_method_evidence_no_longer_requires_question_counts(self):
        self._write_method_artifact()
        evidence={'step_id':'03-project-architecture-baseline',
                  'methods':[self._method_entry(questions=[],alternatives=[],decisions=[])]}
        errors=w.validate_methods(evidence,'03-project-architecture-baseline',self.root)
        self.assertEqual([],errors)

    def test_method_evidence_no_longer_requires_topic_keywords(self):
        self._write_method_artifact()
        evidence={'step_id':'03-project-architecture-baseline',
                  'methods':[self._method_entry(questions=['客户端形态？','跨端方案？','设备协议？','离线同步？'])]}
        errors=w.validate_methods(evidence,'03-project-architecture-baseline',self.root)
        self.assertEqual([],errors)

    def test_method_policy_prefers_process_contract_over_docs(self):
        process=(self.root/'process/STEP-ARTIFACT-CONTRACTS.json')
        docs=(self.root/'docs/STEP-ARTIFACT-CONTRACTS.json')
        process.write_text(json.dumps({'method_policy':{'03-project-architecture-baseline':{
            'required':[{'skill':'custom-skill','requires_artifact':True}]}}}),encoding='utf-8')
        docs.write_text(json.dumps({'method_policy':{'03-project-architecture-baseline':{
            'required':[{'skill':'brainstorming','requires_artifact':True}]}}}),encoding='utf-8')
        self._write_method_artifact()
        evidence={'step_id':'03-project-architecture-baseline','methods':[self._method_entry()]}
        errors=w.validate_methods(evidence,'03-project-architecture-baseline',self.root)
        self.assertTrue(any('custom-skill' in e for e in errors),errors)

    def test_stage_02_internet_research_is_advisory(self):
        self._write_method_artifact()
        (self.root/'docs/product').mkdir(parents=True,exist_ok=True)
        research=self.root/'docs/product/reference-research.md'
        research.write_text('# 参考产品与互联网调研\n\n## 3. 研究记录\n\n| 1 | WebSearch | https://example.com | 2026-11-13 |\n',encoding='utf-8')
        evidence={'step_id':'02-requirements-analysis','methods':[self._method_entry()]}
        errors,warnings=w.validate_methods_detailed(evidence,'02-requirements-analysis',self.root)
        self.assertEqual([],errors)
        self.assertTrue(any('internet-research' in msg for msg in warnings),warnings)
        evidence['methods'].append({'skill':'internet-research','mode':'stage-scoped','summary':'market research',
            'questions':['q1','q2','q3'],'alternatives':['a1','a2'],'decisions':['d1'],'open_questions':[],
            'artifact_section':'docs/product/reference-research.md#3. 研究记录',
            'evidence':'docs/product/reference-research.md'})
        evidence['methods'].append({'skill':'competitor-research','mode':'stage-scoped','summary':'same-category comparison',
            'questions':['同类产品有哪些？','核心流程差异？'],'alternatives':['采纳','不采纳'],'decisions':['d1'],'open_questions':[],
            'artifact_section':'docs/product/reference-research.md#3. 研究记录',
            'evidence':'docs/product/reference-research.md'})
        errors,warnings=w.validate_methods_detailed(evidence,'02-requirements-analysis',self.root)
        self.assertEqual([],errors)
        self.assertEqual([],warnings)

    def test_method_evidence_supports_multiple_required_skills(self):
        (self.root/'docs/product').mkdir(parents=True,exist_ok=True)
        artifact=self.root/'docs/product/reference-research.md'
        artifact.write_text('# 参考产品与互联网调研\n\n## 1. 研究范围与问题\n\n| RQ-001 | 研究问题 | 为什么重要 |\n|---|---|---|\n',encoding='utf-8')
        section='docs/product/reference-research.md#1. 研究范围与问题'
        entry=self._method_entry(skill='brainstorming',artifact_section=section,evidence='docs/product/reference-research.md')
        research=self._method_entry(skill='internet-research',questions=['q1','q2','q3'],alternatives=['a1','a2'],
                                    decisions=['d1'],artifact_section=section,evidence='docs/product/reference-research.md')
        competitor=self._method_entry(skill='competitor-research',questions=['同类产品？','流程差异？'],alternatives=['采纳','不采纳'],
                                      decisions=['d1'],artifact_section=section,evidence='docs/product/reference-research.md')
        evidence={'step_id':'02-requirements-analysis','methods':[entry,research,competitor]}
        errors=w.validate_methods(evidence,'02-requirements-analysis',self.root)
        self.assertEqual([],errors)

    def test_conditional_stage_skip_creates_skip_handoff(self):
        state={'project_name':'test','active_change_id':'sample-change',
               'completed_steps':['01-project-bootstrap','02-requirements-analysis','03-project-architecture-baseline','04-proposal-planning','05-feature-requirements'],
               'current_step':'06-figma-design-review','pending_approvals':[],'blocked_items':[],'last_completed_outputs':[]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        evidence={'step_id':'06-figma-design-review','change_id':'sample-change','skip':True,
                  'reason':'Approved Change has no user-facing UI.',
                  'checks':[{'name':'no-ui','kind':'automated','status':'passed',
                             'command':'python scripts/check-figma-audit.py --change sample-change --strict --no-ui --reason "no UI"',
                             'exit_code':0,'log':'check.log'}]}
        ep=self._write_evidence('skip-evidence.json',evidence)
        original=w.run_baseline_gate; w.run_baseline_gate=lambda *a,**k: ''
        try:
            args=type('Args',(),{'step':'06-figma-design-review','change_id':'sample-change','evidence':str(ep)})()
            self.assertEqual(0,w.cmd_skip_stage(args))
        finally:
            w.run_baseline_gate=original
        state=w.load_state()
        self.assertIn('06-figma-design-review',state['completed_steps'])
        self.assertIn('06-figma-design-review',state['skipped_steps'])
        self.assertEqual('07-detailed-design',state['current_step'])
        manifest=self.root/'workflow/handoffs/sample-change/06-figma-design-review--07-detailed-design.json'
        ok,errors=w.verify_manifest(manifest)
        self.assertTrue(ok,errors)

    def test_request_review_excludes_volatile_state_from_targets(self):
        (self.root/'docs').mkdir(exist_ok=True)
        (self.root/'docs/out.md').write_text('approved output',encoding='utf-8')
        contract={'steps':[{'step':'01','outputs':['docs/out.md','workflow-state.json']}]}
        (self.root/'process/STEP-ARTIFACT-CONTRACTS.json').write_text(json.dumps(contract),encoding='utf-8')
        evidence={'step_id':'01-project-bootstrap','outputs':[
            {'path':'docs/out.md','status':'created','required':True},
            {'path':'workflow-state.json','status':'updated'}],
            'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
            'approval':{'status':'not-required'}}
        ep=self._write_evidence('review-volatile-evidence.json',evidence)
        args=type('Args',(),{'step':'01-project-bootstrap','change_id':None,'summary':'ready','target':[],'evidence':str(ep)})()
        self.assertEqual(0,w.cmd_request_review(args))
        state=w.load_state()
        targets=[t['path'] for t in state['pending_approvals'][0]['targets']]
        self.assertEqual(['docs/out.md'],targets)
        approve_args=type('Args',(),{'step':'01-project-bootstrap','change_id':None,
                                     'approver':'用户','approved_at':'2026-11-18','evidence':'check.log'})()
        self.assertEqual(0,w.cmd_approve(approve_args))

    def test_state_file_is_volatile_and_does_not_invalidate_handoff(self):
        (self.root/'docs').mkdir(exist_ok=True)
        (self.root/'docs/out.md').write_text('approved output',encoding='utf-8')
        contract={'steps':[{'step':'01','outputs':['docs/out.md','workflow-state.json']}]}
        (self.root/'process/STEP-ARTIFACT-CONTRACTS.json').write_text(json.dumps(contract),encoding='utf-8')
        evidence={'step_id':'01-project-bootstrap','outputs':[
            {'path':'docs/out.md','status':'created','required':True},
            {'path':'workflow-state.json','status':'updated'}],
            'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
            'approval':{'status':'not-required'}}
        ep=self._write_evidence('volatile-evidence.json',evidence)
        self.assertEqual(0,self._transition('01-project-bootstrap',ep))
        manifest=self.root/'workflow/handoffs/project/01-project-bootstrap--02-requirements-analysis.json'
        payload=json.loads(manifest.read_text(encoding='utf-8'))
        state_artifact=[a for a in payload['artifacts'] if a['path']=='workflow-state.json'][0]
        self.assertTrue(state_artifact.get('mutable_by_design'))
        state=w.load_state(); state['pending_approvals']=[{'step_id':'02-requirements-analysis'}]
        state['last_updated']=w.now(); w.STATE.write_text(json.dumps(state),encoding='utf-8')
        ok,errors=w.verify_manifest(manifest)
        self.assertTrue(ok,errors)

    def test_stage01_handoff_excludes_state_and_undeclared_outputs(self):
        (self.root/'docs').mkdir(exist_ok=True)
        (self.root/'docs/out.md').write_text('approved output',encoding='utf-8')
        contract={'steps':[{'step':'01','outputs':['docs/out.md']}]}
        (self.root/'process/STEP-ARTIFACT-CONTRACTS.json').write_text(json.dumps(contract),encoding='utf-8')
        evidence={'step_id':'01-project-bootstrap','outputs':[
            {'path':'docs/out.md','status':'created','required':True},
            {'path':'workflow-state.json','status':'updated'}],
            'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
            'approval':{'status':'not-required'}}
        ep=self._write_evidence('declared-output-evidence.json',evidence)
        self.assertEqual(0,self._transition('01-project-bootstrap',ep))
        manifest=self.root/'workflow/handoffs/project/01-project-bootstrap--02-requirements-analysis.json'
        artifacts=[a['path'] for a in json.loads(manifest.read_text(encoding='utf-8'))['artifacts']]
        self.assertEqual(['docs/out.md'],artifacts)

    def test_request_review_pins_hashes_and_blocks_post_review_changes(self):
        review_args=type('Args',(),{'step':'01-project-bootstrap','change_id':None,'summary':'ready','target':[],'evidence':'review-evidence.json'})()
        self.assertEqual(0,w.cmd_request_review(review_args))
        state=w.load_state(); self.assertIn('targets',state['pending_approvals'][0])
        (self.root/'out.md').write_text('changed after review',encoding='utf-8')
        approve_args=type('Args',(),{'step':'01-project-bootstrap','change_id':None,
                                     'approver':'用户','approved_at':'2026-11-17','evidence':'check.log'})()
        with self.assertRaisesRegex(ValueError,'changed since request-review'):
            w.cmd_approve(approve_args)

    def test_stage01_transition_without_recorded_approval_is_blocked(self):
        state=w.load_state(); state['approvals_history']=[]; w.STATE.write_text(json.dumps(state),encoding='utf-8')
        evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'out.md','status':'created'}],
                  'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'required':False,'status':'not-required'}}
        ep=self._write_evidence('no-approval-evidence.json',evidence)
        with self.assertRaisesRegex(ValueError,'Human approval required'):
            self._transition('01-project-bootstrap',ep)

    def test_reopen_preserves_approvals_and_invalidates_outgoing_handoffs(self):
        state={'project_name':'test','active_change_id':'','completed_steps':['01-project-bootstrap','02-requirements-analysis','03-project-architecture-baseline'],
               'current_step':'04-proposal-planning','pending_approvals':[],'blocked_items':[],
               'last_completed_outputs':[],'approvals_history':[
                   {'step_id':'02-requirements-analysis','change_id':'','approver':'用户','approved_at':'2026-11-13','evidence':'check.log'},
                   {'step_id':'03-project-architecture-baseline','change_id':'','approver':'用户','approved_at':'2026-11-13','evidence':'check.log'}]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        handoff_dir=self.root/'workflow/handoffs/project'; handoff_dir.mkdir(parents=True,exist_ok=True)
        for name,from_step,to_step in [('02--03.json','02-requirements-analysis','03-project-architecture-baseline'),
                                       ('03--04.json','03-project-architecture-baseline','04-proposal-planning')]:
            (handoff_dir/name).write_text(json.dumps({'from_step':from_step,'to_step':to_step,'change_id':None,'approval':{'status':'approved'},'checks':[],'artifacts':[{'path':'out.md','sha256':w.hash_file(self.root/'out.md')}]}),encoding='utf-8')
        args=type('Args',(),{'step':'03-project-architecture-baseline','reason':'design rework','note':''})()
        self.assertEqual(0,w.cmd_reopen(args))
        state=w.load_state()
        self.assertEqual(['01-project-bootstrap','02-requirements-analysis'],state['completed_steps'])
        active=[r for r in state['approvals_history'] if not r.get('superseded_at')]
        self.assertEqual(['02-requirements-analysis'],[w.item_step(r) for r in active])
        self.assertFalse(json.loads((handoff_dir/'02--03.json').read_text(encoding='utf-8')).get('invalidated_at'))
        self.assertTrue(json.loads((handoff_dir/'03--04.json').read_text(encoding='utf-8')).get('invalidated_at'))

    def test_reset_state_returns_to_uninitialized_and_archives_history(self):
        state={'project_name':'test','active_change_id':'demo-change','completed_steps':['01-project-bootstrap'],
               'current_step':'02-requirements-analysis','pending_approvals':[],'blocked_items':[],
               'last_completed_outputs':[],'baseline':{'overall_version':'0.3.0'},'approvals_history':[
                   {'step_id':'01-project-bootstrap','change_id':'','approver':'用户','approved_at':'2026-11-13','evidence':'check.log'}]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        handoff_dir=self.root/'workflow/handoffs/project'; handoff_dir.mkdir(parents=True,exist_ok=True)
        (handoff_dir/'01--02.json').write_text(json.dumps({'from_step':'01-project-bootstrap','to_step':'02-requirements-analysis','change_id':None,'approval':{'status':'approved'},'checks':[],'artifacts':[{'path':'out.md','sha256':w.hash_file(self.root/'out.md')}]}),encoding='utf-8')
        args=type('Args',(),{'reason':'user requested uninitialized state','note':''})()
        self.assertEqual(0,w.cmd_reset_state(args))
        state=w.load_state()
        self.assertEqual('01-project-bootstrap',state['current_step'])
        self.assertEqual([],state['completed_steps'])
        self.assertEqual('',state['active_change_id'])
        self.assertEqual({},state['baseline'])
        self.assertEqual([],state['approvals_history'])
        self.assertEqual(1,len(state['reset_history']))
        archive=self.root/state['reset_history'][0]['archive']
        self.assertTrue(archive.is_file())
        self.assertTrue(json.loads((handoff_dir/'01--02.json').read_text(encoding='utf-8')).get('invalidated_at'))

    def test_abandon_change_clears_change_steps_and_records_history(self):
        state={'project_name':'test','active_change_id':'sample-change',
               'completed_steps':['01-project-bootstrap','02-requirements-analysis','03-project-architecture-baseline','04-proposal-planning','05-feature-requirements','06-figma-design-review','07-detailed-design'],
               'current_step':'08-implementation-orchestrator','pending_approvals':[],'blocked_items':[],'last_completed_outputs':[]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        handoff_dir=self.root/'workflow/handoffs/sample-change'; handoff_dir.mkdir(parents=True,exist_ok=True)
        (handoff_dir/'07-detailed-design--08-implementation-orchestrator.json').write_text(json.dumps({'from_step':'07-detailed-design','to_step':'08-implementation-orchestrator','change_id':'sample-change','approval':{'status':'approved'},'checks':[],'artifacts':[{'path':'out.md','sha256':w.hash_file(self.root/'out.md')}]}),encoding='utf-8')
        args=type('Args',(),{'change_id':'sample-change','reason':'roadmap changed','note':''})()
        self.assertEqual(0,w.cmd_abandon_change(args))
        state=w.load_state()
        self.assertEqual('',state['active_change_id'])
        self.assertEqual(['01-project-bootstrap','02-requirements-analysis','03-project-architecture-baseline','04-proposal-planning'],state['completed_steps'])
        self.assertEqual('05-feature-requirements',state['current_step'])
        self.assertEqual('sample-change',state['abandoned_changes'][0]['change_id'])
        self.assertTrue(json.loads((handoff_dir/'07-detailed-design--08-implementation-orchestrator.json').read_text(encoding='utf-8')).get('invalidated_at'))
        self.assertTrue((self.root/'workflow/state-events.jsonl').is_file())

    def test_static_evidence_gate_blocks_bad_evidence(self):
        scripts=Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=scripts) as tmp:
            root=Path(tmp)
            gates={'schema_version':'1.0','project':'test-project','status':'DRAFT',
                   'policy':{'blocking_severities':['error'],'require_clean_exit':True,
                             'waiver_file':'openspec/changes/<change-id>/design/static-waivers.json',
                             'waiver':{'allowed':True,'requires_approver':True,'max_days':90},
                             'allow_network_install':False},
                   'stacks':[{'id':'app','language':'python','root':'app','tools':[
                       {'id':'lint','mode':'blocking',
                        'command':f'"{sys.executable}" -c "import sys; sys.exit(0)"',
                        'configs':['eslint.config.js']}]}]}
            (root/'docs/architecture').mkdir(parents=True)
            (root/'docs/architecture/quality-gates.json').write_text(json.dumps(gates),encoding='utf-8')
            (root/'app').mkdir()
            (root/'app/eslint.config.js').write_text('export default [];\n',encoding='utf-8')
            (root/'openspec/changes/demo-change').mkdir(parents=True)
            evidence_rel='openspec/changes/demo-change/design/evidence/static-analysis.json'
            runner=scripts/'run-quality-gates.py'
            proc=subprocess.run([sys.executable,str(runner),'demo-change','--root',str(root),
                                 '--output',evidence_rel,'--identity','AGENT','--source-revision','test-rev'],
                                capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(0,proc.returncode,proc.stdout+proc.stderr)
            original=w.ROOT
            w.ROOT=root
            try:
                self.assertIsNone(w.static_evidence_gate('08-implementation-orchestrator','demo-change'))
                evidence_path=root/evidence_rel
                bad=json.loads(evidence_path.read_text(encoding='utf-8'))
                bad['verdict']='FAIL'
                evidence_path.write_text(json.dumps(bad),encoding='utf-8')
                with self.assertRaisesRegex(ValueError,'Static analysis evidence'):
                    w.static_evidence_gate('08-implementation-orchestrator','demo-change')
            finally:
                w.ROOT=original

    def _write_static_fixture(self, change_id='demo-change'):
        """Materialize a minimal adopted static-analysis gate in self.root."""
        gates={'schema_version':'1.0','project':'test-project','status':'DRAFT',
               'policy':{'blocking_severities':['error'],'require_clean_exit':True,
                         'waiver_file':'openspec/changes/<change-id>/design/static-waivers.json',
                         'waiver':{'allowed':True,'requires_approver':True,'max_days':90},
                         'allow_network_install':False},
               'stacks':[{'id':'app','language':'python','root':'app','tools':[
                   {'id':'lint','mode':'blocking',
                    'command':f'"{sys.executable}" -c "import sys; sys.exit(0)"',
                    'configs':['eslint.config.js']}]}]}
        (self.root/'docs/architecture').mkdir(parents=True,exist_ok=True)
        (self.root/'docs/architecture/quality-gates.json').write_text(json.dumps(gates),encoding='utf-8')
        (self.root/'app').mkdir(exist_ok=True)
        (self.root/'app/eslint.config.js').write_text('export default [];\n',encoding='utf-8')
        (self.root/'openspec/changes'/change_id).mkdir(parents=True,exist_ok=True)
        return f'openspec/changes/{change_id}/design/evidence/static-analysis.json'

    def _run_static_runner(self, change_id, output_rel, *extra):
        runner=Path(__file__).resolve().with_name('run-quality-gates.py')
        return subprocess.run([sys.executable,str(runner),change_id,'--root',str(self.root),
                               '--output',output_rel,'--source-revision','test-rev',*extra],
                              capture_output=True,text=True,encoding='utf-8')

    def _write_change_state(self, step, change_id, completed):
        state={'project_name':'test','active_change_id':change_id,'completed_steps':completed,
               'current_step':step,'pending_approvals':[],'blocked_items':[],
               'last_completed_outputs':[],
               'approvals_history':[{'step_id':step,'change_id':change_id,'approver':'Owner',
                                     'approved_at':'2026-11-19','evidence':'check.log','targets':[]}]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')

    def _stage_evidence(self, step, change_id, name):
        evidence={'step_id':step,'change_id':change_id,
                  'outputs':[{'path':'out.md','status':'created','required':True}],
                  'methods':[
                      {'skill':'test-driven-development','mode':'stage-scoped',
                       'summary':'tdd implement','questions':[],'alternatives':[],
                       'decisions':[],'open_questions':[],'artifact_section':'',
                       'evidence':'check.log'},
                      {'skill':'verification-before-completion','mode':'stage-scoped',
                       'summary':'verify before completion','questions':[],'alternatives':[],
                       'decisions':[],'open_questions':[],'artifact_section':'',
                       'evidence':'check.log'}],
                  'checks':[{'name':'gate','kind':'automated','status':'passed',
                             'command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'required':True,'status':'approved','approver':'Owner',
                              'approved_at':'2026-11-19'}}
        return self._write_evidence(name,evidence)

    def test_transition_08_enforces_strict_static_evidence(self):
        change='demo-change'
        evidence_rel=self._write_static_fixture(change)
        self.assertEqual(0,self._run_static_runner(change,evidence_rel,'--identity','builder').returncode)
        original_check,original_gate=w.check_entry,w.run_baseline_gate
        w.check_entry=lambda *a,**k: []
        w.run_baseline_gate=lambda args,label: ''
        try:
            self._write_change_state('08-implementation-orchestrator',change,
                                     ['01-project-bootstrap','02-requirements-analysis',
                                      '03-project-architecture-baseline','04-proposal-planning',
                                      '05-feature-requirements','06-figma-design-review',
                                      '07-detailed-design'])
            evidence_path=self.root/evidence_rel
            bad=json.loads(evidence_path.read_text(encoding='utf-8'))
            bad['builder_identity']=''
            evidence_path.write_text(json.dumps(bad),encoding='utf-8')
            ep=self._stage_evidence('08-implementation-orchestrator',change,'strict-08-evidence.json')
            args=type('Args',(),{'step':'08-implementation-orchestrator','evidence':str(ep),'change_id':None})()
            with self.assertRaisesRegex(ValueError,'builder_identity'):
                w.cmd_transition(args)
            self.assertEqual(0,self._run_static_runner(change,evidence_rel,'--identity','builder').returncode)
            self.assertEqual(0,w.cmd_transition(args))
            self.assertEqual('09-independent-verification',w.load_state()['current_step'])
        finally:
            w.check_entry,w.run_baseline_gate=original_check,original_gate

    def test_transition_08_without_gates_file_skips_static_checker(self):
        calls=[]
        original_check,original_gate,original_static=w.check_entry,w.run_baseline_gate,w.static_evidence_gate
        w.check_entry=lambda *a,**k: []
        w.run_baseline_gate=lambda args,label: ''

        def unexpected(*args,**kwargs):
            calls.append(args)
            raise AssertionError('static checker must stay dormant without quality-gates.json')
        w.static_evidence_gate=unexpected
        try:
            self._write_change_state('08-implementation-orchestrator','demo-change',
                                     ['07-detailed-design'])
            ep=self._stage_evidence('08-implementation-orchestrator','demo-change',
                                    'dormant-08-evidence.json')
            args=type('Args',(),{'step':'08-implementation-orchestrator','evidence':str(ep),'change_id':None})()
            self.assertEqual(0,w.cmd_transition(args))
        finally:
            w.check_entry,w.run_baseline_gate,w.static_evidence_gate=original_check,original_gate,original_static
        self.assertEqual([],calls)

    def test_static_evidence_gate_09_requires_independent_evidence(self):
        change='demo-change'
        builder_rel=self._write_static_fixture(change)
        self.assertEqual(0,self._run_static_runner(change,builder_rel,'--identity','builder').returncode)
        original=w.ROOT
        w.ROOT=self.root
        try:
            with self.assertRaisesRegex(ValueError,'Static analysis evidence'):
                w.static_evidence_gate('09-independent-verification',change)
            indep_rel=f'openspec/changes/{change}/design/evidence/static-analysis-independent.json'
            proc=self._run_static_runner(change,indep_rel,
                                         '--independent','--identity','verifier',
                                         '--builder-identity','builder')
            self.assertEqual(0,proc.returncode,proc.stdout+proc.stderr)
            self.assertIsNone(w.static_evidence_gate('09-independent-verification',change))
        finally:
            w.ROOT=original

    def test_transition_appends_state_event_log(self):
        (self.root/'docs').mkdir(exist_ok=True)
        (self.root/'docs/out.md').write_text('approved output',encoding='utf-8')
        contract={'steps':[{'step':'01','outputs':['docs/out.md']}]}
        (self.root/'process/STEP-ARTIFACT-CONTRACTS.json').write_text(json.dumps(contract),encoding='utf-8')
        evidence={'step_id':'01-project-bootstrap','outputs':[{'path':'docs/out.md','status':'created','required':True}],
                  'checks':[{'name':'lint','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'status':'not-required'}}
        ep=self._write_evidence('event-evidence.json',evidence)
        self.assertEqual(0,self._transition('01-project-bootstrap',ep))
        events=[json.loads(line) for line in (self.root/'workflow/state-events.jsonl').read_text(encoding='utf-8').splitlines()]
        self.assertEqual('transition',events[-1]['event'])

    # --- Task 11: workflow hard gates (07 slice / 08 footprint) ---

    def _temporarily(self, **overrides):
        """Patch module globals and return the originals for restoration."""
        originals={name:getattr(w,name,None) for name in overrides}
        for name,value in overrides.items(): setattr(w,name,value)
        return originals

    def _restore(self, originals):
        for name,value in originals.items():
            if value is None: delattr(w,name)
            else: setattr(w,name,value)

    def _run_transition_cli(self, step, evidence):
        argv=sys.argv
        sys.argv=['workflow.py','transition','--step',step,'--evidence',str(evidence)]
        try: return w.main()
        finally: sys.argv=argv

    def _design_evidence(self, change_id, name):
        rel=f'openspec/changes/{change_id}/design.md'
        design=self.root/rel
        design.parent.mkdir(parents=True,exist_ok=True)
        design.write_text('# 详细设计\n\n## 设计决策\n\n### Implementation Slice\n\n- Owned paths: `app/**`\n- Integration paths: N/A\n',encoding='utf-8')
        methods=[{'skill':skill,'mode':'stage-scoped','summary':'slice design','questions':[],
                  'alternatives':[],'decisions':[],'open_questions':[],
                  'artifact_section':rel+'#设计决策','evidence':rel}
                 for skill in ('brainstorming','writing-plans','existing-code-impact-analysis')]
        evidence={'step_id':'07-detailed-design','change_id':change_id,
                  'outputs':[{'path':'out.md','status':'created','required':True}],
                  'methods':methods,
                  'checks':[{'name':'gate','kind':'automated','status':'passed',
                             'command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'required':True,'status':'approved','approver':'Owner','approved_at':'2026-11-19'}}
        return self._write_evidence(name,evidence)

    def _verification_evidence(self, change_id, name):
        base=f'openspec/changes/{change_id}/design/evidence'
        report=f'{base}/independent-verification-report.md'
        machine=f'{base}/independent-verification.json'
        (self.root/base).mkdir(parents=True,exist_ok=True)
        (self.root/report).write_text('# Independent verification\n\nPASS\n',encoding='utf-8')
        (self.root/machine).write_text('{"verdict": "PASS"}\n',encoding='utf-8')
        evidence={'step_id':'09-independent-verification','change_id':change_id,
                  'outputs':[{'path':report,'status':'created','required':True},
                             {'path':machine,'status':'created','required':True}],
                  'methods':[{'skill':'verification-before-completion','mode':'stage-scoped',
                              'summary':'verify','questions':[],'alternatives':[],'decisions':[],
                              'open_questions':[],'artifact_section':'','evidence':'check.log'}],
                  'checks':[{'name':'verifier','kind':'automated','status':'passed',
                             'command':f'python scripts/check-independent-verification.py --change {change_id}',
                             'exit_code':0,'log':'check.log'}],
                  'approval':{'required':True,'status':'approved','approver':'Owner','approved_at':'2026-11-19'}}
        return self._write_evidence(name,evidence)

    CHANGE_COMPLETE=['01-project-bootstrap','02-requirements-analysis','03-project-architecture-baseline',
                     '04-proposal-planning','05-feature-requirements','06-figma-design-review']

    def test_07_transition_blocks_when_slice_gate_fails(self):
        change='demo-change'
        self._write_change_state('07-detailed-design',change,self.CHANGE_COMPLETE)
        ep=self._design_evidence(change,'slice-fail-evidence.json')
        calls=[]
        def fail(change_id):
            calls.append(change_id)
            raise ValueError(f'07 slice gate blocked for {change_id} (exit=1): ERROR: slice invalid')
        def wrong_gate(*a,**k):
            raise AssertionError('footprint gate must not run for stage 07')
        originals=self._temporarily(check_entry=lambda *a,**k: [],
                                    run_baseline_gate=lambda args,label: '',
                                    project_strategy=lambda: 'footprint',
                                    run_slice_gate=fail,
                                    run_footprint_gate=wrong_gate)
        try:
            code=self._run_transition_cli('07-detailed-design',ep)
        finally:
            self._restore(originals)
        self.assertNotEqual(0,code)
        self.assertEqual(['demo-change'],calls)
        state=w.load_state()
        self.assertEqual('07-detailed-design',state['current_step'])
        self.assertNotIn('07-detailed-design',state['completed_steps'])

    def test_07_skips_slice_gate_when_strategy_none(self):
        change='demo-change'
        self._write_change_state('07-detailed-design',change,self.CHANGE_COMPLETE)
        ep=self._design_evidence(change,'slice-skip-evidence.json')
        calls=[]
        def unexpected(name):
            def gate(*a,**k):
                calls.append(name); raise AssertionError(f'{name} must not run when strategy is none')
            return gate
        out=io.StringIO()
        originals=self._temporarily(check_entry=lambda *a,**k: [],
                                    run_baseline_gate=lambda args,label: '',
                                    project_strategy=lambda: 'none',
                                    run_slice_gate=unexpected('slice'),
                                    run_footprint_gate=unexpected('footprint'))
        try:
            with contextlib.redirect_stdout(out):
                self.assertEqual(0,self._transition('07-detailed-design',ep))
        finally:
            self._restore(originals)
        self.assertEqual([],calls)
        self.assertIn('FOOTPRINT_GATE=SKIPPED (strategy none)',out.getvalue())
        self.assertEqual('08-implementation-orchestrator',w.load_state()['current_step'])

    def test_08_transition_blocks_when_footprint_gate_fails(self):
        change='demo-change'
        self._write_change_state('08-implementation-orchestrator',change,
                                 self.CHANGE_COMPLETE+['07-detailed-design'])
        ep=self._stage_evidence('08-implementation-orchestrator',change,'footprint-fail-evidence.json')
        calls=[]
        def fail(change_id):
            calls.append(change_id)
            raise ValueError(f'08 footprint gate blocked for {change_id} (exit=1): ERROR: owned path outside module')
        def wrong_gate(*a,**k):
            raise AssertionError('slice gate must not run for stage 08')
        originals=self._temporarily(check_entry=lambda *a,**k: [],
                                    run_baseline_gate=lambda args,label: '',
                                    project_strategy=lambda: 'module-packages',
                                    run_footprint_gate=fail,
                                    run_slice_gate=wrong_gate)
        try:
            code=self._run_transition_cli('08-implementation-orchestrator',ep)
        finally:
            self._restore(originals)
        self.assertNotEqual(0,code)
        self.assertEqual(['demo-change'],calls)
        state=w.load_state()
        self.assertEqual('08-implementation-orchestrator',state['current_step'])
        self.assertNotIn('08-implementation-orchestrator',state['completed_steps'])

    def test_08_skips_footprint_gate_when_strategy_none(self):
        change='demo-change'
        self._write_change_state('08-implementation-orchestrator',change,
                                 self.CHANGE_COMPLETE+['07-detailed-design'])
        ep=self._stage_evidence('08-implementation-orchestrator',change,'footprint-skip-evidence.json')
        calls=[]
        def unexpected(name):
            def gate(*a,**k):
                calls.append(name); raise AssertionError(f'{name} must not run when strategy is none')
            return gate
        out=io.StringIO()
        originals=self._temporarily(check_entry=lambda *a,**k: [],
                                    run_baseline_gate=lambda args,label: '',
                                    project_strategy=lambda: 'none',
                                    run_footprint_gate=unexpected('footprint'),
                                    run_slice_gate=unexpected('slice'))
        try:
            with contextlib.redirect_stdout(out):
                self.assertEqual(0,self._transition('08-implementation-orchestrator',ep))
        finally:
            self._restore(originals)
        self.assertEqual([],calls)
        self.assertIn('FOOTPRINT_GATE=SKIPPED (strategy none)',out.getvalue())
        self.assertEqual('09-independent-verification',w.load_state()['current_step'])

    def test_footprint_gate_not_called_for_09(self):
        change='demo-change'
        self._write_change_state('09-independent-verification',change,
                                 self.CHANGE_COMPLETE+['07-detailed-design','08-implementation-orchestrator'])
        ep=self._verification_evidence(change,'verifier-gate-evidence.json')
        calls=[]
        def unexpected(*a,**k):
            calls.append(a); raise AssertionError('slice/footprint gate must not run for stage 09')
        originals=self._temporarily(check_entry=lambda *a,**k: [],
                                    run_baseline_gate=lambda args,label: '',
                                    project_strategy=lambda: 'footprint',
                                    run_slice_gate=unexpected,
                                    run_footprint_gate=unexpected)
        try:
            self.assertEqual(0,self._transition('09-independent-verification',ep))
        finally:
            self._restore(originals)
        self.assertEqual([],calls)
        self.assertEqual('10-acceptance-audit',w.load_state()['current_step'])

    def test_project_strategy_rejects_invalid_value(self):
        self.assertEqual('none',w.project_strategy())
        layout=self.root/'docs/architecture/code-layout.json'
        layout.parent.mkdir(parents=True,exist_ok=True)
        layout.write_text(json.dumps({'strategy':'bogus-strategy'}),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,"bogus-strategy.*docs/architecture/code-layout.json"):
            w.project_strategy()
        layout.write_text('{ not json',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'docs/architecture/code-layout.json'):
            w.project_strategy()

    def test_roadmap_declared_later_output_is_mutable_by_design(self):
        contract={'steps':[{'step':'04','outputs':['docs/product/proposal-roadmap.md']},
                           {'step':'05','outputs':['docs/product/proposal-roadmap.md']}]}
        (self.root/'process/STEP-ARTIFACT-CONTRACTS.json').write_text(json.dumps(contract),encoding='utf-8')
        artifacts=w.annotate_mutable_artifacts(
            [{'path':'docs/product/proposal-roadmap.md'}],'04-proposal-planning')
        self.assertTrue(artifacts[0].get('mutable_by_design'))

    def test_request_review_aggregates_check_and_method_warnings(self):
        (self.root/'docs').mkdir(exist_ok=True)
        (self.root/'docs/out.md').write_text('approved output',encoding='utf-8')
        (self.root/'warn.log').write_text('WARN: only 1 source URL; 3 recommended\nOK\n',encoding='utf-8')
        contract={'steps':[{'step':'03','outputs':['docs/out.md']}]}
        (self.root/'process/STEP-ARTIFACT-CONTRACTS.json').write_text(json.dumps(contract),encoding='utf-8')
        state={'project_name':'test','active_change_id':'',
               'completed_steps':['01-project-bootstrap','02-requirements-analysis'],
               'current_step':'03-project-architecture-baseline','pending_approvals':[],'blocked_items':[],'last_completed_outputs':[]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        evidence={'step_id':'03-project-architecture-baseline',
                  'outputs':[{'path':'docs/out.md','status':'created','required':True}],
                  'checks':[{'name':'research','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'warn.log'}],
                  'approval':{'status':'pending'}}
        ep=self._write_evidence('warn-review-evidence.json',evidence)
        args=type('Args',(),{'step':'03-project-architecture-baseline','change_id':None,'summary':'ready','target':[],'evidence':str(ep)})()
        self.assertEqual(0,w.cmd_request_review(args))
        packet_path=self.root/'workflow/evidence/03-project-architecture-baseline-review.json'
        packet=json.loads(packet_path.read_text(encoding='utf-8'))
        self.assertTrue(any('only 1 source URL' in msg for msg in packet.get('warnings',[])),packet)
        self.assertTrue(any('brainstorming' in msg for msg in packet.get('warnings',[])),packet)

    def test_stage_08_risk_based_fast_track_and_standard_approval(self):
        self.assertEqual('low',w.BY_ID['08-implementation-orchestrator']['risk_level'])
        change='demo-change'
        state={'project_name':'test','active_change_id':change,'approval_policy':'risk-based',
               'completed_steps':self.CHANGE_COMPLETE+['07-detailed-design'],
               'current_step':'08-implementation-orchestrator','pending_approvals':[],'blocked_items':[],'last_completed_outputs':[]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        (self.root/'out.md').write_text('ok',encoding='utf-8')
        evidence={'step_id':'08-implementation-orchestrator','change_id':change,
                  'outputs':[{'path':'out.md','status':'created','required':True}],
                  'checks':[{'name':'gate','kind':'automated','status':'passed','command':'python check.py','exit_code':0,'log':'check.log'}],
                  'approval':{'status':'pending'}}
        ep=self._write_evidence('08-fast-track.json',evidence)
        out=io.StringIO()
        originals=self._temporarily(check_entry=lambda *a,**k: [],
                                    run_baseline_gate=lambda args,label: '',
                                    project_strategy=lambda: 'none')
        try:
            with contextlib.redirect_stdout(out):
                args=type('Args',(),{'step':'08-implementation-orchestrator','change_id':change,'summary':'done','target':[],'evidence':str(ep)})()
                self.assertEqual(0,w.cmd_request_review(args))
            self.assertIn('STATUS=RISK_BASED_FAST_TRACK',out.getvalue())
            self.assertEqual(0,self._transition('08-implementation-orchestrator',ep))
        finally:
            self._restore(originals)
        self.assertEqual('09-independent-verification',w.load_state()['current_step'])

    def test_skip_stage_06_with_reason_auto_generates_audit_and_evidence(self):
        change='backend-only'
        state={'project_name':'test','active_change_id':change,
               'completed_steps':['01-project-bootstrap','02-requirements-analysis','03-project-architecture-baseline','04-proposal-planning','05-feature-requirements'],
               'current_step':'06-figma-design-review','pending_approvals':[],'blocked_items':[],'last_completed_outputs':[]}
        w.STATE.write_text(json.dumps(state),encoding='utf-8')
        # Copy real check-figma-audit.py and gate_common.py into temp workspace
        src_scripts=Path(__file__).resolve().parent
        dst_scripts=self.root/'scripts'
        dst_scripts.mkdir(parents=True,exist_ok=True)
        for fname in ('check-figma-audit.py','gate_common.py'):
            (dst_scripts/fname).write_text((src_scripts/fname).read_text(encoding='utf-8'),encoding='utf-8')
        originals=self._temporarily(run_baseline_gate=lambda *a,**k: '')
        try:
            args=type('Args',(),{'step':'06-figma-design-review','change_id':change,'evidence':None,'reason':'Backend API change only'})()
            self.assertEqual(0,w.cmd_skip_stage(args))
        finally:
            self._restore(originals)
        audit=self.root/'openspec/changes'/change/'design/figma-audit.md'
        self.assertTrue(audit.is_file())
        self.assertIn('Design source status: N/A',audit.read_text(encoding='utf-8'))
        self.assertEqual('07-detailed-design',w.load_state()['current_step'])

if __name__=='__main__': unittest.main(verbosity=2)
