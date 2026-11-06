#!/usr/bin/env python3
"""Fail-closed workflow state machine, guards and SHA-256 handoff manifests."""
from __future__ import annotations
import argparse, hashlib, json, os, sys, time, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'workflow-state.json'
STAGES_FILE=ROOT/'docs/WORKFLOW-STAGES.json'
STAGES=json.loads(STAGES_FILE.read_text(encoding='utf-8'))['stages']
BY_ID={s['id']:s for s in STAGES}
ORDER=[s['id'] for s in STAGES]

def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
def relpath(p:Path):
    try:return p.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError: raise ValueError(f'Path escapes project root: {p}')
def load_state():
    if not STATE.exists(): raise ValueError(f'Missing {STATE.relative_to(ROOT)}')
    data=json.loads(STATE.read_text(encoding='utf-8'))
    for k,v in {'state_schema_version':'1.0','completed_steps':[],'pending_approvals':[],'blocked_items':[],'last_completed_outputs':[],'active_change_id':'','transition_history':[]}.items(): data.setdefault(k,v)
    if data.get('current_step') not in BY_ID and data.get('current_step')!='ALL_STEPS_COMPLETE': raise ValueError(f"Unknown current_step: {data.get('current_step')}")
    unknown=set(data['completed_steps'])-set(BY_ID)
    if unknown: raise ValueError('Unknown completed steps: '+', '.join(sorted(unknown)))
    return data

def atomic_json(path:Path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    lock=path.with_suffix(path.suffix+'.lock')
    fd=None; acquired=False
    try:
        fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600); acquired=True
        os.write(fd,str(os.getpid()).encode()); os.close(fd); fd=None
        tmp=path.with_suffix(path.suffix+'.tmp')
        tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        os.replace(tmp,path)
    except FileExistsError: raise RuntimeError(f'Lock exists: {lock}; another transition may be running. Inspect before removing stale lock.')
    finally:
        if fd is not None: os.close(fd)
        if acquired:
            try: lock.unlink()
            except FileNotFoundError: pass


def run_baseline_gate(args, *, label):
    result=subprocess.run([sys.executable,str(ROOT/'scripts'/'baseline-governance.py'),*args],capture_output=True,text=True)
    if result.returncode:
        detail=(result.stdout+'\n'+result.stderr).strip()
        raise ValueError(f'{label} blocked (exit={result.returncode}): {detail}')
    return result.stdout.strip()

def baseline_phase_for_entry(step_id):
    if step_id in ('10-feature-requirements','10b-prototype-generation','11-page-interaction-inventory','12-figma-ui-audit','13a-feature-design'):
        return 'requirement'
    if step_id in ('13b-api-contract-design','13c-frontend-detail-design','13d-backend-detail-design','13e-test-design','14-implementation-orchestrator'):
        return 'design'
    if step_id=='14b-independent-verification':
        return 'implementation'
    if step_id=='15-acceptance-audit':
        return 'acceptance'
    return None

def baseline_phase_for_transition(step_id):
    if step_id=='10b-prototype-generation' or step_id=='13a-feature-design' or step_id in ('13b-api-contract-design','13c-frontend-detail-design','13d-backend-detail-design','13e-test-design'):
        return 'design' if step_id != '10b-prototype-generation' else 'requirement'
    if step_id in ('14-implementation-orchestrator','14b-independent-verification'):
        return 'implementation'
    if step_id=='15-acceptance-audit':
        return 'acceptance'
    return None

def handoff_dir(stage_id,change_id):
    scope='project' if BY_ID[stage_id]['scope']=='project' else (change_id or '')
    if not scope: raise ValueError('Change-scoped handoff requires --change-id or workflow-state.active_change_id')
    return ROOT/'workflow'/'handoffs'/scope

def manifest_path(from_id,to_id,change_id): return handoff_dir(from_id,change_id)/f'{from_id}--{to_id}.json'

def hash_file(path):
    # Normalize CRLF to LF so handoff hashes are stable across Windows/Linux checkouts.
    data=path.read_bytes().replace(b'\r\n',b'\n')
    return hashlib.sha256(data).hexdigest()

def verify_manifest(path):
    if not path.is_file(): return False,[f'Missing handoff manifest: {relpath(path)}']
    try: m=json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:return False,[f'Invalid handoff JSON: {e}']
    errors=[]
    if m.get('from_step') not in BY_ID or m.get('to_step') not in BY_ID:
        errors.append('Handoff has unknown from_step / to_step')
    elif m.get('to_step') not in [x['id'] for x in STAGES if m.get('from_step') in x['dependencies']]:
        errors.append('Handoff target is not a direct successor')
    elif BY_ID[m['from_step']]['human_approval_required'] and m.get('approval',{}).get('status')!='approved':
        errors.append('Source stage requires approved human approval in handoff manifest')
    for check in m.get('checks',[]):
        if check.get('status')!='passed': errors.append(f"Handoff contains failed check: {check.get('name','unnamed')}")
        if check.get('kind','automated')=='automated' and check.get('exit_code')!=0: errors.append(f"Handoff contains non-zero check: {check.get('name','unnamed')}")
    if m.get('from_step')=='14b-independent-verification':
        paths={a.get('path','') for a in m.get('artifacts',[])}
        if not any(x.endswith('independent-verification-report.md') for x in paths): errors.append('Verifier handoff missing Markdown report')
        if not any(x.endswith('independent-verification.json') for x in paths): errors.append('Verifier handoff missing JSON evidence')
        if not any('check-independent-verification.py' in c.get('command','') and c.get('exit_code')==0 for c in m.get('checks',[])):
            errors.append('Verifier handoff missing passing independent-verification checker')
    for item in m.get('artifacts',[]):
        p=(ROOT/item['path']).resolve()
        try:p.relative_to(ROOT.resolve())
        except ValueError: errors.append(f"Unsafe artifact path: {item.get('path')}"); continue
        if not p.is_file(): errors.append(f"Missing artifact: {item['path']}"); continue
        actual=hash_file(p)
        if actual!=item.get('sha256'): errors.append(f"Hash mismatch: {item['path']} expected={item.get('sha256')} actual={actual}")
    if not m.get('artifacts'): errors.append('Handoff contains no artifacts')
    return not errors,errors

def incoming_manifests(step_id,change_id):
    stage=BY_ID[step_id]; manifests=[]
    for dep in stage['dependencies']:
        dep_stage=BY_ID[dep]
        # A project stage hands into project scope; a feature stage hands into the active Change.
        cid=change_id if dep_stage['scope']=='change' else None
        manifests.append(manifest_path(dep,step_id,cid))
    return manifests

def check_entry(step_id,state,change_id=None,verify_handoffs=True):
    errors=[]; stage=BY_ID[step_id]; completed=set(state['completed_steps'])
    missing=[d for d in stage['dependencies'] if d not in completed]
    if missing: errors.append('Uncompleted dependencies: '+', '.join(missing))
    if state.get('pending_approvals'): errors.append('Pending approvals exist: '+json.dumps(state['pending_approvals'],ensure_ascii=False))
    if state.get('blocked_items'): errors.append('Blocked items exist: '+json.dumps(state['blocked_items'],ensure_ascii=False))
    if state.get('current_step')!=step_id: errors.append(f"current_step is {state.get('current_step')}, not {step_id}")
    cid=change_id or state.get('active_change_id') or None
    if stage['scope']=='change' and not cid: errors.append('Change-scoped stage requires active_change_id / --change-id')
    if step_id=='09-proposal-planning' or stage['scope']=='change':
        try:
            run_baseline_gate(['audit','--require-frozen'],label='Project baseline gate')
        except Exception as exc:
            errors.append(str(exc))
    phase=baseline_phase_for_entry(step_id)
    if stage['scope']=='change' and phase and cid:
        try:
            run_baseline_gate(['check-change','--change-id',cid,'--phase',phase],label=f'Change baseline gate ({phase})')
        except Exception as exc:
            errors.append(str(exc))
    if verify_handoffs:
        for dep,mp in zip(stage['dependencies'],incoming_manifests(step_id,cid)):
            ok,errs=verify_manifest(mp)
            if not ok: errors.extend(errs)
            elif mp.is_file():
                manifest=json.loads(mp.read_text(encoding='utf-8'))
                expected_cid=cid if BY_ID[dep]['scope']=='change' else None
                if manifest.get('from_step')!=dep or manifest.get('to_step')!=step_id: errors.append(f'Incorrect handoff endpoints: {relpath(mp)}')
                if manifest.get('change_id')!=expected_cid: errors.append(f'Change ID mismatch in handoff: {relpath(mp)} expected={expected_cid}')
    return errors

def parse_evidence(path,step_id,change_id):
    p=(ROOT/path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    try:p.relative_to(ROOT.resolve())
    except ValueError: raise ValueError('Evidence file must be inside project root')
    e=json.loads(p.read_text(encoding='utf-8'))
    if e.get('step_id')!=step_id: raise ValueError(f"Evidence step_id must be {step_id}")
    if change_id and e.get('change_id') not in (None,change_id): raise ValueError('Evidence change_id mismatch')
    outputs=e.get('outputs',[])
    if not outputs: raise ValueError('Evidence must list at least one output artifact')
    artifacts=[]
    for o in outputs:
        if o.get('status','created') not in ('created','updated','verified'): 
            if o.get('required',True): raise ValueError(f"Required output not ready: {o.get('path')} status={o.get('status')}")
            continue
        op=(ROOT/o['path']).resolve()
        try: rel=op.relative_to(ROOT.resolve()).as_posix()
        except ValueError: raise ValueError(f"Output escapes project root: {o.get('path')}")
        if not op.is_file():
            if o.get('required',True): raise ValueError(f"Required output missing: {rel}")
            continue
        artifacts.append({'path':rel,'sha256':hash_file(op),'size_bytes':op.stat().st_size,'role':o.get('role','output')})
    if not artifacts: raise ValueError('No existing output artifacts to hand off')
    checks=e.get('checks',[])
    if not checks: raise ValueError('Evidence must contain at least one gate check')
    failed=[]
    for c in checks:
        if c.get('status')!='passed': failed.append(c.get('name','unnamed check')+': status is not passed')
        if c.get('kind','automated')=='automated':
            if c.get('exit_code')!=0: failed.append(c.get('name','unnamed check')+': automated exit_code must be 0')
            if not c.get('command'): failed.append(c.get('name','unnamed check')+': exact command is required')
            if not c.get('log'): failed.append(c.get('name','unnamed check')+': execution log path is required')
        if c.get('kind')=='manual':
            if not c.get('reviewer'): failed.append(c.get('name','unnamed check')+': manual check requires reviewer')
            if not c.get('evidence'): failed.append(c.get('name','unnamed check')+': manual check requires evidence path')
        proof=c.get('log') or c.get('evidence')
        if proof:
            pp=(ROOT/proof).resolve()
            try: pp.relative_to(ROOT.resolve())
            except ValueError: failed.append(c.get('name','unnamed check')+': proof path escapes project root')
            else:
                if not pp.is_file(): failed.append(c.get('name','unnamed check')+f': proof file missing: {proof}')
    if failed: raise ValueError('Gate checks failed: '+'; '.join(failed))
    if step_id=='14b-independent-verification':
        paths={a['path'] for a in artifacts}
        required_suffixes=('independent-verification-report.md','independent-verification.json')
        for suffix in required_suffixes:
            if not any(p.endswith(suffix) for p in paths):
                raise ValueError(f'Independent verifier must output {suffix}')
        if not any('check-independent-verification.py' in c.get('command','') and c.get('exit_code')==0 for c in checks):
            raise ValueError('14b requires a real check-independent-verification.py gate with exit_code=0')
    stage=BY_ID[step_id]
    approval=e.get('approval',{})
    if (stage['human_approval_required'] or approval.get('required') is True) and approval.get('status')!='approved':
        raise ValueError('Human approval required; evidence.approval.status must be approved')
    if approval.get('status')=='approved' and (not approval.get('approver') or not approval.get('approved_at')):
        raise ValueError('Approved evidence requires approver and approved_at')
    return e,artifacts

def cmd_status(args):
    s=load_state(); print(json.dumps({'project_name':s.get('project_name'),'active_change_id':s.get('active_change_id'),'current_step':s.get('current_step'),'completed_steps':s.get('completed_steps'),'pending_approvals':s.get('pending_approvals'),'blocked_items':s.get('blocked_items'),'last_transition':s.get('last_transition'),'transition_history':s.get('transition_history',[]),'baseline':s.get('baseline',{})},ensure_ascii=False,indent=2)); return 0

def cmd_check_entry(args):
    s=load_state(); errs=check_entry(args.step,s,args.change_id)
    if errs:
        print('ENTRY_BLOCKED'); [print(' - '+e) for e in errs]; return 3
    print(f'ENTRY_READY={args.step}'); return 0

def cmd_handoff_verify(args):
    mp=Path(args.manifest); mp=mp if mp.is_absolute() else ROOT/mp
    ok,errs=verify_manifest(mp)
    if ok: print(f'HANDOFF_VERIFIED={relpath(mp)}'); return 0
    print('HANDOFF_INVALID'); [print(' - '+e) for e in errs]; return 4

def cmd_transition(args):
    s=load_state(); sid=args.step; stage=BY_ID[sid]
    errs=check_entry(sid,s,args.change_id)
    if errs:
        print('TRANSITION_BLOCKED'); [print(' - '+e) for e in errs]; return 3
    e,artifacts=parse_evidence(args.evidence,sid,args.change_id)
    cid=e.get('change_id') or args.change_id or s.get('active_change_id') or None
    if sid=='05-project-architecture-baseline':
        run_baseline_gate(['audit','--require-frozen'],label='Baseline freeze gate')
        artifact_paths={a['path'] for a in artifacts}
        required_baseline_artifacts={'docs/architecture/baseline-manifest.json','docs/architecture/constraint-registry.json'}
        missing=required_baseline_artifacts-artifact_paths
        if missing:
            raise ValueError('05-project-architecture-baseline evidence must hand off machine baseline artifacts: '+', '.join(sorted(missing)))
    transition_phase=baseline_phase_for_transition(sid)
    if stage['scope']=='change' and transition_phase and cid:
        run_baseline_gate(['check-change','--change-id',cid,'--phase',transition_phase],label=f'Change baseline transition gate ({transition_phase})')
    # Commit state first, then hash outputs. This matters when workflow-state.json itself
    # is a declared stage output: its final post-transition bytes must be in the handoff.
    s['completed_steps']=list(dict.fromkeys(s['completed_steps']+[sid]))
    if cid: s['active_change_id']=cid
    s['last_completed_outputs']=[a['path'] for a in artifacts]
    s['last_updated']=now()
    evidence_path=Path(args.evidence); evidence_path=evidence_path if evidence_path.is_absolute() else ROOT/evidence_path
    transition_record={'step_id':sid,'completed_at':s['last_updated'],'change_id':cid,'evidence_path':relpath(evidence_path),'outputs':[a['path'] for a in artifacts],'checks':[{'name':c.get('name'),'status':c.get('status'),'exit_code':c.get('exit_code')} for c in e.get('checks',[])],'approval':e.get('approval',{})}
    s.setdefault('transition_history',[]).append(transition_record)
    s['last_transition']=transition_record
    if e.get('approval',{}).get('status')=='approved':
        s['pending_approvals']=[x for x in s.get('pending_approvals',[]) if x.get('step_id')!=sid and x!=sid]
    # Select first topologically ready stage in declared order.
    completed=set(s['completed_steps']); nxt=next((x for x in STAGES if x['id'] not in completed and all(d in completed for d in x['dependencies'])),None)
    s['current_step']=nxt['id'] if nxt else 'ALL_STEPS_COMPLETE'
    atomic_json(STATE,s)
    for artifact in artifacts:
        ap=(ROOT/artifact['path']).resolve()
        if ap.is_file():
            artifact['sha256']=hash_file(ap)
            artifact['size_bytes']=ap.stat().st_size
    successors=[x for x in STAGES if sid in x['dependencies']]
    for nxt_stage in successors:
        outcid=cid if stage['scope']=='change' else None
        mp=manifest_path(sid,nxt_stage['id'],outcid)
        manifest={'version':'1.0','from_step':sid,'to_step':nxt_stage['id'],'change_id':outcid,'created_at':now(),'baseline_version':e.get('baseline_version',''),'approval':e.get('approval',{}),'checks':e.get('checks',[]),'artifacts':artifacts}
        atomic_json(mp,manifest)
        print(f'HANDOFF_CREATED={relpath(mp)}')
    print(f"COMPLETED={sid}"); print(f"NEXT_STEP={s['current_step']}")
    return 0

def cmd_handoff_create(args):
    # Explicit utility for re-creating a handoff after a predecessor has been re-approved.
    if args.from_step not in BY_ID or args.to_step not in BY_ID: raise ValueError('Unknown from/to step')
    if args.to_step not in [x['id'] for x in STAGES if args.from_step in x['dependencies']]: raise ValueError('to-step is not a direct successor')
    cid=args.change_id
    evidence_data=None; checks=[]; approval={'status':'approved' if args.approved else 'not-recorded'}; baseline_version=args.baseline_version or ''
    if args.evidence:
        evidence_data,artifacts=parse_evidence(args.evidence,args.from_step,cid)
        checks=evidence_data.get('checks',[]); approval=evidence_data.get('approval',{}); baseline_version=evidence_data.get('baseline_version','')
    else:
        if args.from_step=='14b-independent-verification': raise ValueError('Verifier handoff recovery requires --evidence so PASS proof is preserved')
        if BY_ID[args.from_step]['human_approval_required'] and not args.approved:
            raise ValueError('Source stage requires --approved or an approved --evidence file')
        artifacts=[]
    for raw in ([] if evidence_data else args.file):
        p=Path(raw); p=(ROOT/p).resolve() if not p.is_absolute() else p.resolve()
        try: rel=p.relative_to(ROOT.resolve()).as_posix()
        except ValueError: raise ValueError(f'File outside project: {raw}')
        if not p.is_file(): raise ValueError(f'Missing file: {rel}')
        artifacts.append({'path':rel,'sha256':hash_file(p),'size_bytes':p.stat().st_size,'role':'output'})
    if not artifacts: raise ValueError('At least one --file is required')
    mp=manifest_path(args.from_step,args.to_step,cid)
    atomic_json(mp,{'version':'1.0','from_step':args.from_step,'to_step':args.to_step,'change_id':cid,'created_at':now(),'baseline_version':baseline_version, 'approval':approval,'checks':checks,'artifacts':artifacts})
    print(f'HANDOFF_CREATED={relpath(mp)}'); return 0

def cmd_migrate_state(args):
    if not args.reason or not args.reason.strip():
        raise ValueError('migrate-state requires --reason')
    data=json.loads(STATE.read_text(encoding='utf-8'))
    valid=set(BY_ID); reset=set(args.reset_step or [])
    old=list(data.get('completed_steps',[]))
    legacy=[s for s in old if s not in valid or s in reset]
    data.setdefault('legacy_completed_steps',[])
    data['legacy_completed_steps']=list(dict.fromkeys(data['legacy_completed_steps']+legacy))
    data['completed_steps']=[s for s in old if s in valid and s not in reset]
    completed=set(data['completed_steps'])
    nxt=next((x for x in STAGES if x['id'] not in completed and all(d in completed for d in x['dependencies'])),None)
    data['current_step']=nxt['id'] if nxt else 'ALL_STEPS_COMPLETE'
    data['last_updated']=now()
    if getattr(args,'note',None):
        data['notes']=args.note
    data.setdefault('topology_migrations',[]).append({'at':data['last_updated'],'reason':args.reason,'legacy_steps':legacy,'reset_steps':sorted(reset),'completed_steps':data['completed_steps'],'current_step':data['current_step']})
    atomic_json(STATE,data)
    print(f'MIGRATED=workflow-state.json')
    print('COMPLETED='+', '.join(data['completed_steps']))
    print('LEGACY='+', '.join(data['legacy_completed_steps']))
    print('CURRENT_STEP='+data['current_step'])
    return 0

def main():
    ap=argparse.ArgumentParser(description=__doc__); sub=ap.add_subparsers(dest='cmd',required=True)
    sub.add_parser('status')
    p=sub.add_parser('check-entry'); p.add_argument('--step',required=True,choices=ORDER); p.add_argument('--change-id')
    p=sub.add_parser('handoff-verify'); p.add_argument('--manifest',required=True)
    p=sub.add_parser('handoff-create'); p.add_argument('--from-step',required=True,choices=ORDER); p.add_argument('--to-step',required=True,choices=ORDER); p.add_argument('--change-id'); p.add_argument('--baseline-version'); p.add_argument('--approved',action='store_true'); p.add_argument('--evidence'); p.add_argument('--file',action='append',default=[])
    p=sub.add_parser('transition'); p.add_argument('--step',required=True,choices=ORDER); p.add_argument('--evidence',required=True); p.add_argument('--change-id')
    p=sub.add_parser('migrate-state'); p.add_argument('--reason',required=True); p.add_argument('--note'); p.add_argument('--reset-step',action='append',default=[],choices=ORDER)
    args=ap.parse_args()
    try:
        return {'status':cmd_status,'check-entry':cmd_check_entry,'handoff-verify':cmd_handoff_verify,'handoff-create':cmd_handoff_create,'transition':cmd_transition,'migrate-state':cmd_migrate_state}[args.cmd](args)
    except Exception as exc:
        print(f'ERROR: {exc}',file=sys.stderr); return 2
if __name__=='__main__': raise SystemExit(main())
