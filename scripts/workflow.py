#!/usr/bin/env python3
"""Fail-closed workflow state machine, guards and SHA-256 handoff manifests."""
from __future__ import annotations
import argparse, hashlib, json, os, re, sys, time, subprocess
from contextlib import contextmanager, nullcontext
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from method_evidence import validate_methods
from question_coverage import validate_coverage
import roadmap_deps

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'workflow-state.json'
STAGES_FILE=ROOT/'process/WORKFLOW-STAGES.json'
CONTRACT_FILE='process/STEP-ARTIFACT-CONTRACTS.json'
MANIFEST_FILE='docs/architecture/baseline-manifest.json'
CONSTRAINT_FILE='docs/architecture/constraint-registry.json'
BASELINE_STATUS_FILE='docs/architecture/baseline-status.md'
STAGES=json.loads(STAGES_FILE.read_text(encoding='utf-8'))['stages']
BY_ID={s['id']:s for s in STAGES}
ORDER=[s['id'] for s in STAGES]
PROJECT_STEP_IDS=[s['id'] for s in STAGES if s['scope']=='project']
CHANGE_STEP_IDS=[s['id'] for s in STAGES if s['scope']=='change']
V2_VERSION='2.0'
PATH_TOKEN=re.compile(r'(?:docs|templates|openspec|workflow|prompts|scripts|design)/[A-Za-z0-9_\-./<>*]+')
FILE_TOKEN=re.compile(r'^[A-Za-z0-9_.\-]+\.[A-Za-z0-9]{2,5}$')

def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
def append_event(event, **payload):
    path=ROOT/'workflow/state-events.jsonl'
    path.parent.mkdir(parents=True,exist_ok=True)
    record={'event':event,'at':now()}
    record.update(payload)
    with path.open('a',encoding='utf-8') as stream:
        stream.write(json.dumps(record,ensure_ascii=False,sort_keys=True)+'\n')
def relpath(p:Path):
    try:return p.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError: raise ValueError(f'Path escapes project root: {p}')
def is_v2(state):
    return str(state.get('state_schema_version'))==V2_VERSION and isinstance(state.get('project'),dict) and isinstance(state.get('changes'),dict)

COMMON_DEFAULTS={'project_name':'','active_change_id':'','transition_history':[],'approvals_history':[],'reopen_history':[],'reset_history':[],'topology_migrations':[],'change_history':[],'skip_history':[],'abandoned_changes':[],'completed_changes':[],'approval_policy':'standard','approval_policy_history':[],'baseline':{},'last_transition':None,'last_completed_outputs':[],'implementation_lease':None,'notes':''}
LANE_DEFAULTS={'current_step':'','completed_steps':[],'skipped_steps':[],'pending_approvals':[],'blocked_items':[]}

def load_state():
    if not STATE.exists(): raise ValueError(f'Missing {STATE.relative_to(ROOT)}')
    data=json.loads(STATE.read_text(encoding='utf-8'))
    if is_v2(data):
        for k,v in COMMON_DEFAULTS.items(): data.setdefault(k,v)
        if not isinstance(data.get('project'),dict): raise ValueError('v2 state requires a project lane object')
        for k,v in LANE_DEFAULTS.items(): data['project'].setdefault(k,v)
        if not isinstance(data.get('changes'),dict): raise ValueError('v2 state requires a changes object')
        for cid,lane in data['changes'].items():
            if not isinstance(lane,dict): raise ValueError(f'v2 change lane {cid!r} must be an object')
            for k,v in LANE_DEFAULTS.items(): lane.setdefault(k,v)
            lane.setdefault('status','ACTIVE')
            lane.setdefault('dependencies',{'required':[],'verified_at':'','waivers':[]})
        if data['project'].get('current_step') not in PROJECT_STEP_IDS+['PROJECT_COMPLETE','ALL_STEPS_COMPLETE']:
            raise ValueError(f"Unknown project current_step: {data['project'].get('current_step')}")
        unknown=set(data['project']['completed_steps'])-set(PROJECT_STEP_IDS)
        if unknown: raise ValueError('Unknown project completed steps: '+', '.join(sorted(unknown)))
        for cid,lane in data['changes'].items():
            if lane.get('current_step') not in CHANGE_STEP_IDS+['CHANGE_COMPLETE','ALL_STEPS_COMPLETE']:
                raise ValueError(f"Unknown change current_step for {cid}: {lane.get('current_step')}")
            bad=set(lane['completed_steps'])-set(CHANGE_STEP_IDS)
            if bad: raise ValueError(f'Unknown completed steps for {cid}: '+', '.join(sorted(bad)))
        if str(data.get('approval_policy')).strip().lower() not in ('standard','risk-based'):
            raise ValueError(f"Unknown approval_policy: {data.get('approval_policy')}")
        return data
    for k,v in {'state_schema_version':'1.0','completed_steps':[],'pending_approvals':[],'blocked_items':[],'last_completed_outputs':[],'active_change_id':'','transition_history':[],'approvals_history':[],'reopen_history':[],'reset_history':[],'topology_migrations':[],'completed_substeps':[],'current_substep':'','change_history':[],'skipped_steps':[],'skip_history':[],'abandoned_changes':[],'approval_policy':'standard','approval_policy_history':[]}.items(): data.setdefault(k,v)
    if str(data.get('approval_policy')).strip().lower() not in ('standard','risk-based'):
        raise ValueError(f"Unknown approval_policy: {data.get('approval_policy')}")
    if data.get('current_step') not in BY_ID and data.get('current_step')!='ALL_STEPS_COMPLETE': raise ValueError(f"Unknown current_step: {data.get('current_step')}")
    unknown=set(data['completed_steps'])-set(BY_ID)
    if unknown: raise ValueError('Unknown completed steps: '+', '.join(sorted(unknown)))
    return data

def project_lane(state):
    return state['project'] if is_v2(state) else state

def change_lanes(state):
    return state.get('changes') or {} if is_v2(state) else {}

def active_change_ids(state):
    if not is_v2(state): return []
    return [cid for cid,lane in (state.get('changes') or {}).items() if str(lane.get('status','')).upper()=='ACTIVE']

def all_pending_items(state):
    if not is_v2(state): return list(state.get('pending_approvals') or [])
    items=list(project_lane(state).get('pending_approvals') or [])
    for lane in (state.get('changes') or {}).values():
        items+=list(lane.get('pending_approvals') or [])
    return items

def resolve_change_id(state,step_id,change_id=None):
    stage=BY_ID[step_id]
    if stage['scope']!='change': return None
    if change_id: return change_id
    if not is_v2(state):
        cid=state.get('active_change_id') or None
        if not cid: raise ValueError('Change-scoped stage requires active_change_id / --change-id')
        return cid
    active=active_change_ids(state)
    matches=[cid for cid in active if (state['changes'][cid].get('current_step')==step_id)]
    if len(matches)==1: return matches[0]
    if len(active)==1: return active[0]
    raise ValueError('Change-scoped stage requires --change-id (multiple active lanes: '+', '.join(active)+')')

def lane_for(state,step_id,change_id=None):
    stage=BY_ID[step_id]
    if stage['scope']=='project': return project_lane(state),None
    cid=resolve_change_id(state,step_id,change_id)
    if is_v2(state):
        if cid not in state['changes']: raise ValueError(f'Unknown change lane: {cid}')
        return state['changes'][cid],cid
    return state,cid

def lane_dependencies_met(state,lane,stage):
    completed=set(lane.get('completed_steps') or [])
    for dep in stage['dependencies']:
        dep_lane=project_lane(state) if (is_v2(state) and BY_ID[dep]['scope']=='project') else lane
        if dep not in set(dep_lane.get('completed_steps') or []): return False
    return True

def next_lane_stage(state,lane,stage_ids):
    completed=set(lane.get('completed_steps') or [])
    for sid in stage_ids:
        if sid in completed: continue
        if lane_dependencies_met(state,lane,BY_ID[sid]): return sid
    return None

def lane_complete_value(stage_ids): return 'PROJECT_COMPLETE' if stage_ids==PROJECT_STEP_IDS else 'CHANGE_COMPLETE'

def lane_scope_ids(step_id):
    return PROJECT_STEP_IDS if BY_ID[step_id]['scope']=='project' else CHANGE_STEP_IDS

def evidence_namespace(state,step_id,cid):
    if not is_v2(state): return 'workflow/evidence'
    if BY_ID[step_id]['scope']=='change' and cid: return f'workflow/evidence/{cid}'
    return 'workflow/evidence/project'

def default_evidence_path(state,step_id,cid):
    return f"{evidence_namespace(state,step_id,cid)}/{step_id}.json"

def default_review_packet_path(state,step_id,cid):
    return f"{evidence_namespace(state,step_id,cid)}/{step_id}-review.json"

def default_skip_evidence_path(state,step_id,cid):
    return f"{evidence_namespace(state,step_id,cid)}/{step_id}-skip.json"

def _first_ready_stage(completed,stage_ids):
    completed=set(completed)
    for sid in stage_ids:
        if sid in completed: continue
        if all(dep in completed for dep in BY_ID[sid]['dependencies']): return sid
    return None

def _state_backup(name):
    path=ROOT/'workflow/evidence'/name
    atomic_json(path,{'archived_at':now(),'state':json.loads(STATE.read_text(encoding='utf-8'))})
    return path

def cmd_upgrade_state(args):
    """Convert a v1 single-lane state into the v2 project + change lanes."""
    if not args.reason or not args.reason.strip(): raise ValueError('upgrade-state requires --reason')
    state=load_state()
    if is_v2(state):
        print('ALREADY_V2=workflow-state.json')
        print(f'CURRENT_STEP={state["project"].get("current_step")}')
        return 0
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup=_state_backup(f'state-v2-backup-{stamp}.json')
    completed=list(state.get('completed_steps') or [])
    skipped=list(state.get('skipped_steps') or [])
    project_completed=[sid for sid in PROJECT_STEP_IDS if sid in completed]
    change_completed=[sid for sid in CHANGE_STEP_IDS if sid in completed]
    active=state.get('active_change_id') or ''
    project_current=_first_ready_stage(project_completed,PROJECT_STEP_IDS) or 'PROJECT_COMPLETE'
    project={
        'current_step':project_current,
        'completed_steps':project_completed,
        'skipped_steps':[sid for sid in PROJECT_STEP_IDS if sid in skipped],
        'pending_approvals':[],
        'blocked_items':[],
    }
    changes={}
    if active or change_completed:
        cid=active or 'legacy-change'
        if state.get('current_step') in CHANGE_STEP_IDS:
            lane_current=state['current_step']
        else:
            lane_current=_first_ready_stage(change_completed,CHANGE_STEP_IDS) or 'CHANGE_COMPLETE'
        lane={
            'status':'ACTIVE',
            'current_step':lane_current,
            'completed_steps':change_completed,
            'skipped_steps':[sid for sid in CHANGE_STEP_IDS if sid in skipped],
            'pending_approvals':[],
            'blocked_items':[],
            'started_at':now(),
            'dependencies':{'required':[],'verified_at':'','waivers':[]},
        }
        accepted=any(row.get('step_id')=='10-acceptance-audit' and row.get('change_id')==cid for row in state.get('transition_history') or [])
        if lane_current in ('CHANGE_COMPLETE','ALL_STEPS_COMPLETE') and accepted:
            lane['status']='ACCEPTED'
            lane['current_step']='CHANGE_COMPLETE'
        changes[cid]=lane
    for item in state.get('pending_approvals') or []:
        step_id=item_step(item)
        target=(changes.get(active) if step_id in CHANGE_STEP_IDS or (isinstance(item,dict) and item.get('change_id')) else project)
        if target is None: target=project
        target['pending_approvals'].append(item)
    for item in state.get('blocked_items') or []:
        step_id=item_step(item)
        target=(changes.get(active) if step_id in CHANGE_STEP_IDS or (isinstance(item,dict) and item.get('change_id')) else project)
        if target is None: target=project
        target['blocked_items'].append(item)
    new_state={k:v for k,v in state.items() if k not in ('completed_steps','current_step','pending_approvals','blocked_items','skipped_steps','active_change_id')}
    new_state['state_schema_version']=V2_VERSION
    new_state['project']=project
    new_state['changes']=changes
    new_state['completed_changes']=state.get('completed_changes') or []
    new_state['active_change_id']=active
    new_state['last_updated']=now()
    new_state.setdefault('upgrade_history',[]).append({'at':new_state['last_updated'],'from':'1.0','to':V2_VERSION,'reason':args.reason,'backup':relpath(backup),'active_change_id':active})
    atomic_json(STATE,new_state)
    append_event('upgrade_state',reason=args.reason,from_version='1.0',to_version=V2_VERSION,active_change=active)
    print('UPGRADED=workflow-state.json')
    print(f'PROJECT_CURRENT_STEP={project_current}')
    if active: print(f'CHANGE={active} CURRENT_STEP={changes[active]["current_step"]} STATUS={changes[active]["status"]}')
    print('BACKUP='+relpath(backup))
    return 0

def _row_cell(row,label):
    wanted=' '.join(label.casefold().split())
    for key,value in (row or {}).items():
        if ' '.join((key or '').casefold().split())==wanted: return (value or '').strip()
    return ''

def _row_primary_capability(root,cid):
    try:
        roadmap=gm_parse_roadmap(root)
    except Exception:
        return ''
    row=next((r for r in roadmap.get('rows',[]) if roadmap_deps._row_change_id(r)==cid),None)
    if row is None:
        row=next((r for r in roadmap.get('amendments',[]) if roadmap_deps._row_change_id(r)==cid and roadmap_deps._amendment_approved(r)),None)
    return _row_cell(row,'Primary Capability') if row else ''

def gm_parse_roadmap(root):
    import gate_common
    return gate_common.parse_roadmap(root=root)

def _dependency_gate_for_start(parsed,state,cid,args):
    waived=[]
    requested=list(getattr(args,'waive_dependency',None) or [])
    if requested:
        reason=str(getattr(args,'reason','') or '').strip()
        by=str(getattr(args,'by','') or '').strip()
        evidence=str(getattr(args,'evidence','') or '').strip()
        if not reason or not by or not evidence:
            raise ValueError('dependency waiver requires --reason, --by, and --evidence')
        path=(ROOT/evidence).resolve()
        try: path.relative_to(ROOT.resolve())
        except ValueError: raise ValueError('dependency waiver evidence must be inside project root')
        if not path.is_file(): raise ValueError(f'dependency waiver evidence missing: {evidence}')
        known={item['id'] for item in roadmap_deps.dependency_states(parsed,state,cid)}
        for dependency in requested:
            if dependency not in known:
                raise ValueError(f'dependency waiver names an edge that is not a dependency of {cid}: {dependency}')
            waived.append({'dependency':dependency,'reason':reason,'by':by,'evidence':evidence,'waived_at':now()})
    errors=[]
    waiver_ids={item['dependency'] for item in waived}
    for item in roadmap_deps.dependency_states(parsed,state,cid):
        if item['status']=='ACCEPTED': continue
        if item['status']=='BROKEN':
            chain=' ← '.join(item.get('chain') or [cid,item['id']])
            errors.append(f"{item['id']}: BROKEN ({chain}); a broken transitive chain cannot be waived")
            continue
        if item['status'] in ('UNKNOWN','CYCLE'):
            errors.append(f"{item['id']}: {item['status']}; this status cannot be waived")
            continue
        if item['id'] in waiver_ids: continue
        detail=f"{item['id']}: {item['status']}"
        if item.get('stage'): detail+=f"@{item['stage']}"
        errors.append(detail)
    if errors:
        raise ValueError('CHANGE_START_BLOCKED: unmet proposal dependencies\n'+'\n'.join('- '+error for error in errors))
    return waived

def update_capability_registry(cid,action):
    """Maintain active_changes when the project uses a capability registry."""
    try:
        strategy=project_strategy()
    except ValueError:
        return
    if strategy=='none': return
    registry=ROOT/'docs/product/capabilities.csv'
    script=ROOT/'scripts'/'update-capabilities.py'
    if not registry.is_file() or not script.is_file(): return
    result=subprocess.run([sys.executable,str(script),'--change',cid,'--action',action],cwd=ROOT,capture_output=True,text=True)
    if result.returncode:
        raise ValueError(f'Capability registry update failed for {cid}: {(result.stderr or result.stdout).strip()}')

def cmd_start_change(args):
    state=load_state()
    if not is_v2(state):
        raise ValueError('start-change requires v2 state; run: python scripts/workflow.py upgrade-state --reason <reason>')
    cid=str(getattr(args,'change_id','') or '').strip()
    if not cid: raise ValueError('start-change requires --change-id')
    project=project_lane(state)
    if any(sid not in project['completed_steps'] for sid in PROJECT_STEP_IDS):
        raise ValueError('CHANGE_START_BLOCKED: project stages 01-04 are not complete')
    if project.get('pending_approvals') or project.get('blocked_items'):
        raise ValueError('CHANGE_START_BLOCKED: resolve project-level pending approvals and blockers first')
    try:
        run_baseline_gate(['audit','--require-frozen'],label='Project baseline gate')
    except Exception as exc:
        raise ValueError('CHANGE_START_BLOCKED: '+str(exc))
    parsed=roadmap_deps.parse(ROOT)
    if not parsed.get('present'):
        raise ValueError('CHANGE_START_BLOCKED: docs/product/proposal-roadmap.md is missing')
    if cid not in set(parsed.get('registered') or []):
        raise ValueError(f'CHANGE_START_BLOCKED: Change {cid!r} is not in the roadmap main table or an approved amendment')
    try:
        strategy=project_strategy()
    except Exception as exc:
        raise ValueError('CHANGE_START_BLOCKED: '+str(exc))
    roadmap_errors,_,_=roadmap_deps.validate(parsed, require_dependencies=(strategy=='module-packages'))
    if roadmap_errors:
        raise ValueError('CHANGE_START_BLOCKED: roadmap dependency check failed\n'+'\n'.join('- '+item for item in roadmap_errors))
    lane=(state.get('changes') or {}).get(cid)
    if lane and str(lane.get('status','')).upper() in ('ACTIVE','ACCEPTED'):
        raise ValueError(f'CHANGE_START_BLOCKED: Change {cid!r} is already {lane.get("status")}')
    abandoned=[item.get('change_id') if isinstance(item,dict) else item for item in state.get('abandoned_changes') or []]
    if cid in abandoned and not getattr(args,'retry_abandoned',False):
        raise ValueError(f'CHANGE_START_BLOCKED: Change {cid!r} was abandoned; pass --retry-abandoned --reason <reason> to restart it')
    waived=_dependency_gate_for_start(parsed,state,cid,args)
    required=list(parsed['graph'].get(cid,[]))
    new_lane={
        'status':'ACTIVE',
        'current_step':'05-feature-requirements',
        'completed_steps':[],
        'skipped_steps':[],
        'pending_approvals':[],
        'blocked_items':[],
        'started_at':now(),
        'dependencies':{'required':required,'verified_at':now(),'waivers':waived},
    }
    warnings=[]
    primary=_row_primary_capability(ROOT,cid)
    if primary:
        for other in active_change_ids(state):
            other_primary=_row_primary_capability(ROOT,other)
            if not other_primary or other_primary!=primary: continue
            related=(other in required) or (cid in (parsed['graph'].get(other) or []))
            if not related:
                warnings.append(f'CONCURRENCY_WARNING: {cid} and {other} share capability {primary!r} without a dependency edge')
    new_lane['concurrency_warnings']=warnings
    update_capability_registry(cid,'add')
    state.setdefault('changes',{})[cid]=new_lane
    state['active_change_id']=cid
    state['abandoned_changes']=[item for item in state.get('abandoned_changes') or [] if (item.get('change_id') if isinstance(item,dict) else item)!=cid]
    state['last_updated']=now()
    atomic_json(STATE,state)
    append_event('change_started',change_id=cid,dependencies=required,waivers=len(waived))
    print(f'CHANGE_STARTED={cid}')
    print('CURRENT_STEP=05-feature-requirements')
    print('DEPENDENCIES='+(', '.join(required) if required else 'none'))
    if waived: print('DEPENDENCY_WAIVERS='+', '.join(item['dependency'] for item in waived))
    for warning in warnings: print(warning)
    return 0

def cmd_list_changes(args):
    state=load_state()
    if not is_v2(state):
        print('UPGRADE_REQUIRED=workflow-state.json (run upgrade-state)')
        return 2
    payload={
        'project':{'current_step':project_lane(state).get('current_step'),'completed_steps':project_lane(state).get('completed_steps'),'pending_approvals':project_lane(state).get('pending_approvals'),'blocked_items':project_lane(state).get('blocked_items')},
        'changes':[
            {'change_id':cid,'status':lane.get('status'),'current_step':lane.get('current_step'),
             'completed_steps':lane.get('completed_steps'),'pending_approvals':lane.get('pending_approvals'),
             'blocked_items':lane.get('blocked_items'),'dependencies':lane.get('dependencies')}
            for cid,lane in sorted((state.get('changes') or {}).items())
        ],
        'implementation_lease':state.get('implementation_lease'),
        'completed_changes':[item.get('change_id') if isinstance(item,dict) else item for item in state.get('completed_changes') or []],
    }
    print(json.dumps(payload,ensure_ascii=False,indent=2))
    return 0

def norm_path(value):
    return str(value).replace(chr(92),'/').strip().rstrip('。.）)')

def item_step(item):
    return item.get('step_id') if isinstance(item,dict) else item

def approval_record(state,step_id,change_id=None):
    for item in reversed(state.get('approvals_history') or []):
        if item.get('superseded_at'): continue
        if item_step(item)!=step_id: continue
        if change_id is not None and (item.get('change_id') or '')!=change_id: continue
        return item
    return None

def stage_requires_human_approval(stage,state=None):
    """Return whether a stage needs a recorded user approval under the current policy."""
    if not stage.get('human_approval_required'):
        return False
    policy=str((state or {}).get('approval_policy') or 'standard').strip().lower()
    if policy=='risk-based' and stage.get('risk_level','high')=='low':
        return False
    return True

def contract_doc():
    path=ROOT/CONTRACT_FILE
    if not path.exists():
        # Test fixtures and pre-bootstrap checkouts may not have the contract yet.
        return {'steps':[]}
    try:return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc: raise ValueError(f'Invalid {CONTRACT_FILE}: {exc}')

def contract_step_num(step_id):
    try:return int(step_id.split('-')[0])
    except (ValueError,IndexError):return None

def output_paths_for_step(step_id,cid=None):
    row=next((r for r in contract_doc().get('steps',[]) if r.get('step')==step_id.split('-')[0]),None)
    if not row:return []
    paths=[]
    for entry in row.get('outputs',[]):
        text=str(entry)
        match=PATH_TOKEN.search(text)
        if match:
            path=norm_path(match.group(0))
            if cid:path=path.replace('<change-id>',cid)
            paths.append(path)
            continue
        token=text.strip().split()[0].strip('`（）(),')
        if FILE_TOKEN.match(token) and '/' not in token:
            paths.append(norm_path(token))
    return paths

MULTI_WRITER_ARTIFACTS={'baseline-binding.json'}
VOLATILE_ARTIFACTS={
    'workflow-state.json',
    'AGENTS.md',
    'docs/architecture/baseline-status.md',
    'docs/architecture/baseline-manifest.json',
    'docs/architecture/constraint-registry.json',
    'docs/product/BASELINE-INDEX.md',
    'docs/project/toolchain-report.md',
}

def volatile_artifacts():
    extra=contract_doc().get('handoff_policy',{}).get('volatile_artifacts',[])
    return VOLATILE_ARTIFACTS | {norm_path(x) for x in extra if isinstance(x,str)}

def is_volatile(path):
    return norm_path(path) in volatile_artifacts()

def has_later_declared_output(path,sid,cid=None):
    if Path(str(path)).name in MULTI_WRITER_ARTIFACTS:return True
    current=contract_step_num(sid)
    if current is None:return False
    for row in contract_doc().get('steps',[]):
        n=contract_step_num(str(row.get('step','')))
        if n is None or n<=current:continue
        for candidate in output_paths_for_step(str(row.get('step',''))+'-x',cid):
            if norm_path(candidate)==norm_path(path):return True
    return False

def annotate_mutable_artifacts(artifacts,sid,cid=None):
    for item in artifacts:
        volatile=is_volatile(item['path'])
        if has_later_declared_output(item['path'],sid,cid) or volatile:
            item['mutable_by_design']=True
        if volatile: item['volatile']=True
    return artifacts

def missing_declared_outputs(evidence,sid,cid=None):
    declared=output_paths_for_step(sid,cid)
    if not declared:return []
    ready={norm_path(o.get('path','')) for o in evidence.get('outputs',[]) if o.get('status') in ('created','updated','verified')}
    waived={norm_path(o.get('path','')) for o in evidence.get('outputs',[]) if o.get('status')=='n/a' and o.get('waiver_reason')}
    def matches_contract(contract_path,artifact_path):
        # Capability names are selected per Change, so contracts use this one
        # path segment as a placeholder instead of requiring a literal directory.
        marker='<capability>'
        if marker not in contract_path:
            return norm_path(contract_path)==norm_path(artifact_path)
        prefix,suffix=contract_path.split(marker,1)
        candidate=norm_path(artifact_path)
        expression='^'+re.escape(norm_path(prefix))+'[^/]+'+re.escape(norm_path(suffix))+'$'
        return re.fullmatch(expression,candidate) is not None
    def satisfied(path):
        p=norm_path(path)
        if p.endswith('/'):
            # Directory outputs are satisfied by any handed-off file under that directory.
            return p in waived or any(r.startswith(p) for r in ready)
        return any(matches_contract(p,r) for r in ready) or p in waived
    return [p for p in declared if not satisfied(p)]

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

def run_baseline_impact_gate(change_id):
    """Require an approved, implementation-allowing impact decision at Stage 08."""
    command=[sys.executable,str(ROOT/'scripts'/'check-baseline-impact.py'),change_id,'--implementation']
    result=subprocess.run(command,capture_output=True,text=True)
    if result.returncode:
        detail=(result.stdout+'\n'+result.stderr).strip()
        raise ValueError('Implementation baseline-impact gate failed'+(': '+detail if detail else ''))
    return result.stdout.strip()

LAYOUT_FILE='docs/architecture/code-layout.json'
MODULE_STRATEGIES={'none','footprint','module-packages'}

def project_strategy():
    """Return the project module strategy from code-layout.json; ``none`` when absent.

    A malformed layout fails closed: an unreadable strategy can never be
    interpreted as "none" because that would silently disable the hard gates.
    """
    path=ROOT/LAYOUT_FILE
    if not path.exists(): return 'none'
    try: data=json.loads(path.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError) as exc:
        raise ValueError(f'Invalid {LAYOUT_FILE}: {exc}')
    value=data.get('strategy') if isinstance(data,dict) else None
    if not isinstance(value,str) or value.strip() not in MODULE_STRATEGIES:
        raise ValueError(f"Invalid strategy {value!r} in {LAYOUT_FILE}; expected one of none, footprint, module-packages")
    return value.strip()

def run_slice_gate(change_id):
    """07 hard gate: the design.md Implementation Slice must be valid."""
    command=[sys.executable,str(ROOT/'scripts'/'check-design-sections.py'),'--change',change_id,'--slice-only']
    result=subprocess.run(command,capture_output=True,text=True)
    if result.returncode:
        detail=(result.stdout+'\n'+result.stderr).strip()
        raise ValueError(f'07 slice gate blocked for {change_id} (exit={result.returncode}): {detail}')
    return result.stdout.strip()

def run_footprint_gate(change_id):
    """08 hard gate: the implemented diff must stay inside the declared footprint."""
    command=[sys.executable,str(ROOT/'scripts'/'check-change-footprint.py'),change_id,'--verify']
    result=subprocess.run(command,capture_output=True,text=True)
    if result.returncode:
        detail=(result.stdout+'\n'+result.stderr).strip()
        raise ValueError(f'08 footprint gate blocked for {change_id} (exit={result.returncode}): {detail}')
    return result.stdout.strip()

def static_evidence_gate(step_id, change_id):
    """Fail closed unless the Change has passing static-analysis evidence."""
    if not change_id:
        raise ValueError('Static analysis evidence gate requires an active Change id')
    checker=Path(__file__).resolve().parent/'check-static-analysis.py'
    command=[sys.executable,str(checker),'--change',str(change_id),'--root',str(ROOT)]
    # The authoritative 08 command is ``check-static-analysis.py --change <id> --strict``.
    if step_id=='08-implementation-orchestrator':
        command.append('--strict')
    if step_id=='09-independent-verification':
        command.append('--expect-independent')
    result=subprocess.run(command,capture_output=True,text=True)
    if result.returncode:
        detail=(result.stdout+'\n'+result.stderr).strip()
        raise ValueError(f'Static analysis evidence gate failed for {change_id} (exit={result.returncode}): {detail}')

def baseline_phase_for_entry(step_id):
    # Stage 05 creates the initial baseline binding as one of its declared
    # outputs. Require the frozen project baseline at entry, then validate the
    # completed binding on transition and again at Stage 06 entry.
    if step_id=='06-figma-design-review':
        return 'requirement'
    if step_id in ('07-detailed-design','08-implementation-orchestrator'):
        return 'design'
    if step_id=='09-independent-verification':
        return 'implementation'
    if step_id=='10-acceptance-audit':
        return 'acceptance'
    return None

def baseline_phase_for_transition(step_id):
    if step_id=='05-feature-requirements':
        return 'requirement'
    if step_id=='06-figma-design-review':
        return 'requirement'
    if step_id=='07-detailed-design':
        return 'design'
    if step_id in ('08-implementation-orchestrator','09-independent-verification'):
        return 'implementation'
    if step_id=='10-acceptance-audit':
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
        return False,errors
    if m.get('to_step') not in [x['id'] for x in STAGES if m.get('from_step') in x['dependencies']]:
        errors.append('Handoff target is not a direct successor')
    skipped=bool(m.get('skipped'))
    if skipped:
        if not BY_ID[m['from_step']].get('conditional'):
            errors.append('Skip manifest is only valid for a conditional stage')
        if not str(m.get('skip_reason','')).strip():
            errors.append('Skip manifest requires a skip_reason')
        ev=str(m.get('evidence','')).strip()
        if not ev:
            errors.append('Skip manifest requires an evidence path')
        else:
            ep=(ROOT/ev).resolve()
            try: ep.relative_to(ROOT.resolve())
            except ValueError: errors.append('Skip evidence path escapes project root')
            else:
                if not ep.is_file(): errors.append('Skip evidence file missing: '+ev)
        if not m.get('checks'): errors.append('Skip manifest requires at least one machine check')
    elif BY_ID[m['from_step']]['human_approval_required'] and m.get('approval',{}).get('status')!='approved':
        errors.append('Source stage requires approved human approval in handoff manifest')
    for check in m.get('checks',[]):
        if check.get('status')!='passed': errors.append(f"Handoff contains failed check: {check.get('name','unnamed')}")
        if check.get('kind','automated')=='automated' and check.get('exit_code')!=0: errors.append(f"Handoff contains non-zero check: {check.get('name','unnamed')}")
    if m.get('from_step')=='09-independent-verification':
        paths={a.get('path','') for a in m.get('artifacts',[])}
        if not any(x.endswith('independent-verification-report.md') for x in paths): errors.append('Verifier handoff missing Markdown report')
        if not any(x.endswith('independent-verification.json') for x in paths): errors.append('Verifier handoff missing JSON evidence')
        if not any('check-independent-verification.py' in c.get('command','') and c.get('exit_code')==0 for c in m.get('checks',[])):
            errors.append('Verifier handoff missing passing independent-verification checker')
    if not skipped:
        for item in m.get('artifacts',[]):
            p=(ROOT/item['path']).resolve()
            try:p.relative_to(ROOT.resolve())
            except ValueError: errors.append(f"Unsafe artifact path: {item.get('path')}"); continue
            if not p.is_file(): errors.append(f"Missing artifact: {item['path']}"); continue
            if item.get('mutable_by_design'):
                # A later DAG stage declares this path as its own output; existence is required,
                # but the original hash is allowed to drift by design (e.g. baseline-status,
                # design.md, traceability.csv, lessons/decisions/assumptions).
                continue
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

def dependency_gate_errors(state,cid):
    """Return the dependency-gate errors for a v2 change lane."""
    if not is_v2(state) or not cid: return []
    parsed=roadmap_deps.parse(ROOT)
    if not parsed.get('present'):
        return ['proposal-roadmap.md is missing; dependencies cannot be verified']
    try:
        strategy=project_strategy()
        roadmap_errors,_,_=roadmap_deps.validate(parsed, require_dependencies=(strategy=='module-packages'))
    except Exception as exc:
        roadmap_errors=[str(exc)]
    lane=(state.get('changes') or {}).get(cid) or {}
    waived={str(item.get('dependency')) for item in ((lane.get('dependencies') or {}).get('waivers') or []) if isinstance(item,dict)}
    errors=['roadmap dependency check: '+error for error in roadmap_errors]
    for item in roadmap_deps.dependency_states(parsed,state,cid):
        status=item.get('status','')
        dependency=item.get('id','')
        if status=='ACCEPTED': continue
        if status in ('ACTIVE','NOT_STARTED','ABANDONED') and dependency in waived: continue
        detail=f"dependency {dependency}: {status}"
        if status=='ACTIVE' and item.get('stage'): detail+=f"@{item['stage']}"
        if status=='BROKEN':
            detail+=' ('+' ← '.join(item.get('chain') or [cid,dependency])+')'
        errors.append(detail)
    return errors

def check_entry(step_id,state,change_id=None,verify_handoffs=True,allow_pending_for_step=None,allow_blocked_for_step=None):
    errors=[]; stage=BY_ID[step_id]
    lane,cid=lane_for(state,step_id,change_id)
    completed=set(lane.get('completed_steps') or [])
    missing=[d for d in stage['dependencies'] if d not in completed] if not is_v2(state) else [d for d in stage['dependencies'] if not lane_dependencies_met(state,lane,BY_ID[d])]
    if missing: errors.append('Uncompleted dependencies: '+', '.join(missing))
    pending=list(lane.get('pending_approvals') or [])
    if is_v2(state) and stage['scope']=='change':
        pending+=list(project_lane(state).get('pending_approvals') or [])
    if allow_pending_for_step:
        pending=[x for x in pending if (x.get('step_id') if isinstance(x,dict) else x)!=allow_pending_for_step]
    if pending: errors.append('Pending approvals exist: '+json.dumps(pending,ensure_ascii=False))
    blocked=list(lane.get('blocked_items') or [])
    if is_v2(state) and stage['scope']=='change':
        blocked+=list(project_lane(state).get('blocked_items') or [])
    if allow_blocked_for_step:
        blocked=[x for x in blocked if (x.get('step_id') if isinstance(x,dict) else x)!=allow_blocked_for_step]
    if blocked: errors.append('Blocked items exist: '+json.dumps(blocked,ensure_ascii=False))
    if lane.get('current_step')!=step_id: errors.append(f"current_step is {lane.get('current_step')}, not {step_id}")
    if stage['scope']=='change' and not cid: errors.append('Change-scoped stage requires active_change_id / --change-id')
    if step_id=='04-proposal-planning' or stage['scope']=='change':
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
    # Stage 08 is the first point where code changes can consume the approved
    # design. Recheck the Change-level decision here so a stale or blocking
    # baseline-impact record cannot be bypassed by a valid baseline binding.
    if step_id=='08-implementation-orchestrator' and cid:
        try:
            run_baseline_impact_gate(cid)
        except Exception as exc:
            errors.append(str(exc))
    if is_v2(state) and stage['scope']=='change' and step_id in ('05-feature-requirements','08-implementation-orchestrator'):
        dependency_errors=dependency_gate_errors(state,cid)
        if dependency_errors:
            errors.append('Unmet proposal dependencies: '+'; '.join(dependency_errors))
    if is_v2(state) and step_id=='08-implementation-orchestrator' and cid:
        lease=state.get('implementation_lease')
        holders=set((lease or {}).get('change_ids') or ([lease.get('change_id')] if (lease or {}).get('change_id') else []))
        if holders and cid not in holders:
            errors.append('IMPLEMENTATION_LEASE_HELD: '+', '.join(sorted(holders)))
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

def declared_path_matches(contract_path,artifact_path):
    contract_path=norm_path(contract_path); artifact_path=norm_path(artifact_path)
    marker='<capability>'
    if marker not in contract_path:
        if contract_path.endswith('/'):
            return artifact_path.startswith(contract_path)
        return contract_path==artifact_path
    prefix,suffix=contract_path.split(marker,1)
    expression='^'+re.escape(prefix)+'[^/]+'+re.escape(suffix)+'$'
    return re.fullmatch(expression,artifact_path) is not None

def parse_evidence(path,step_id,change_id,require_approval=True,include_undeclared=False):
    p=(ROOT/path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    try:p.relative_to(ROOT.resolve())
    except ValueError: raise ValueError('Evidence file must be inside project root')
    e=json.loads(p.read_text(encoding='utf-8'))
    if e.get('step_id')!=step_id: raise ValueError(f"Evidence step_id must be {step_id}")
    if change_id and e.get('change_id') not in (None,change_id): raise ValueError('Evidence change_id mismatch')
    outputs=e.get('outputs',[])
    if not outputs: raise ValueError('Evidence must list at least one output artifact')
    declared=output_paths_for_step(step_id,change_id)
    artifacts=[]
    for o in outputs:
        status=o.get('status','created')
        if status=='n/a':
            if not o.get('waiver_reason'):
                raise ValueError(f"Output marked N/A requires waiver_reason: {o.get('path')}")
            continue
        if status not in ('created','updated','verified'):
            if o.get('required',True): raise ValueError(f"Required output not ready: {o.get('path')} status={status}")
            continue
        rel=norm_path(o['path'])
        if not include_undeclared and declared and not any(declared_path_matches(d,rel) for d in declared):
            # Extra outputs may be logged for audit, but they are not part of the
            # reviewed handoff. This keeps mutable runtime state, generated indexes
            # and toolkit scripts from invalidating an upstream approval.
            continue
        op=(ROOT/o['path']).resolve()
        try: out_rel=op.relative_to(ROOT.resolve()).as_posix()
        except ValueError: raise ValueError(f"Output escapes project root: {o.get('path')}")
        if op.is_dir():
            files=[f for f in sorted(op.rglob('*')) if f.is_file()]
            if not files:
                if o.get('required',True): raise ValueError(f"Required directory output is empty: {out_rel}")
                continue
            for f in files:
                child=out_rel.rstrip('/')+'/'+f.relative_to(op).as_posix()
                artifacts.append({'path':child,'sha256':hash_file(f),'size_bytes':f.stat().st_size,'role':o.get('role','output')})
            continue
        if not op.is_file():
            if o.get('required',True): raise ValueError(f"Required output missing: {out_rel}")
            continue
        artifacts.append({'path':out_rel,'sha256':hash_file(op),'size_bytes':op.stat().st_size,'role':o.get('role','output')})
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
    method_errors=validate_methods(e,step_id,ROOT)
    if method_errors:
        raise ValueError('Method evidence failed: '+'; '.join(method_errors))
    coverage_errors=validate_coverage(e,step_id,ROOT)
    if coverage_errors:
        raise ValueError('Question coverage failed: '+'; '.join(coverage_errors))
    if step_id=='09-independent-verification':
        paths={a['path'] for a in artifacts}
        required_suffixes=('independent-verification-report.md','independent-verification.json')
        for suffix in required_suffixes:
            if not any(p.endswith(suffix) for p in paths):
                raise ValueError(f'Independent verifier must output {suffix}')
        if not any('check-independent-verification.py' in c.get('command','') and c.get('exit_code')==0 for c in checks):
            raise ValueError('09-independent-verification requires a real check-independent-verification.py gate with exit_code=0')
    stage=BY_ID[step_id]
    approval=e.get('approval',{})
    if require_approval and (stage['human_approval_required'] or approval.get('required') is True) and approval.get('status')!='approved':
        raise ValueError('Human approval required; evidence.approval.status must be approved')
    if require_approval and approval.get('status')=='approved' and (not approval.get('approver') or not approval.get('approved_at')):
        raise ValueError('Approved evidence requires approver and approved_at')
    return e,artifacts

def cmd_request_review(args):
    """Record that the current stage is finished and awaiting user review."""
    s=load_state(); sid=args.step; stage=BY_ID[sid]
    lane,cid=lane_for(s,sid,getattr(args,'change_id',None))
    if lane.get('current_step')!=sid:
        raise ValueError(f"current_step is {lane.get('current_step')}, not {sid}")
    missing=[d for d in stage['dependencies'] if not lane_dependencies_met(s,lane,BY_ID[d])]
    if missing: raise ValueError('Uncompleted dependencies: '+', '.join(missing))
    ev=getattr(args,'evidence',None) or default_evidence_path(s,sid,cid)
    ev_path=(ROOT/ev).resolve()
    try: ev_rel=ev_path.relative_to(ROOT.resolve()).as_posix()
    except ValueError: raise ValueError('Review evidence must be inside project root')
    if not ev_path.is_file():
        raise ValueError(f'Review evidence missing: {ev}; generate evidence and run the stage checks before request-review')
    e,artifacts=parse_evidence(ev_rel,sid,cid,require_approval=False)
    missing_outputs=missing_declared_outputs(e,sid,cid)
    if missing_outputs:
        raise ValueError('Evidence omits declared stage outputs (mark N/A with waiver_reason when not applicable): '+', '.join(missing_outputs))
    targets=[{'path':a['path'],'sha256':a['sha256'],'size_bytes':a['size_bytes']} for a in artifacts if not is_volatile(a['path'])]
    if args.target:
        targets=[]
        for raw in args.target:
            p=(ROOT/raw).resolve()
            try: rel=p.relative_to(ROOT.resolve()).as_posix()
            except ValueError: raise ValueError(f'Review target escapes project root: {raw}')
            if not p.is_file(): raise ValueError(f'Review target missing: {raw}')
            targets.append({'path':rel,'sha256':hash_file(p),'size_bytes':p.stat().st_size})
    checks=[{'name':c.get('name'),'status':c.get('status'),'exit_code':c.get('exit_code'),
             'command':c.get('command'),'log':c.get('log')} for c in e.get('checks',[])]
    packet={'step_id':sid,'change_id':cid,'summary':args.summary or '','created_at':now(),
            'evidence':ev_rel,'targets':targets,'checks':checks}
    packet_rel=default_review_packet_path(s,sid,cid)
    packet_path=ROOT/packet_rel
    atomic_json(packet_path,packet)
    if not stage_requires_human_approval(stage,s):
        lane['pending_approvals']=[x for x in (lane.get('pending_approvals') or []) if item_step(x)!=sid]
        s['last_updated']=now()
        atomic_json(STATE,s)
        append_event('review_requested',step_id=sid,change_id=cid,review_packet=relpath(packet_path))
        append_event('risk_based_fast_track',step_id=sid,change_id=cid)
        print(f'REVIEW_REQUESTED={sid}')
        print('CURRENT_STEP='+lane['current_step'])
        if targets: print('REVIEW_TARGETS='+'; '.join(t['path'] for t in targets))
        print('REVIEW_PACKET='+relpath(packet_path))
        print('STATUS=RISK_BASED_FAST_TRACK')
        print('NEXT_ACTION=Run transition after the gates; this low-risk stage needs no user approval under risk-based policy.')
        return 0
    entry={'step_id':sid,'change_id':cid,'requested_at':now(),
           'summary':args.summary or '','evidence':ev_rel,'targets':targets,
           'checks':checks,'review_packet':relpath(packet_path)}
    lane['pending_approvals']=[x for x in (lane.get('pending_approvals') or []) if item_step(x)!=sid]+[entry]
    s['last_updated']=now()
    atomic_json(STATE,s)
    append_event('review_requested',step_id=sid,change_id=cid,review_packet=relpath(packet_path))
    print(f'REVIEW_REQUESTED={sid}')
    print('CURRENT_STEP='+lane['current_step'])
    if targets: print('REVIEW_TARGETS='+'; '.join(t['path'] for t in targets))
    print('REVIEW_PACKET='+relpath(packet_path))
    print('STATUS=AWAITING_USER_REVIEW')
    print('NEXT_ACTION=End the turn now. Do not read or execute any later stage Prompt/Skill or create later-stage artifacts until the user explicitly approves.')
    print(f'ON_APPROVAL=python scripts/workflow.py approve --step {sid} --change-id {cid} --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval evidence path>' if cid else f'ON_APPROVAL=python scripts/workflow.py approve --step {sid} --approver "<user>" --approved-at <YYYY-MM-DD> --evidence <approval evidence path>')
    return 0

def cmd_approve(args):
    """Record an explicit user approval for the current stage (clears its pending review)."""
    s=load_state(); sid=args.step
    lane,cid=lane_for(s,sid,getattr(args,'change_id',None))
    if lane.get('current_step')!=sid:
        raise ValueError(f"current_step is {lane.get('current_step')}, not {sid}")
    pending=[x for x in (lane.get('pending_approvals') or []) if item_step(x)==sid]
    if not pending:
        raise ValueError(f'No pending review request for {sid}; run request-review first and wait for the user')
    if not args.approver.strip() or not args.approved_at.strip():
        raise ValueError('approve requires the real approver and approval date from the user')
    ev=(ROOT/args.evidence).resolve()
    try: ev.relative_to(ROOT.resolve())
    except ValueError: raise ValueError('Approval evidence must be inside project root')
    if not ev.is_file(): raise ValueError('Approval evidence file missing: '+args.evidence)
    entry=pending[0]
    targets=entry.get('targets') or []
    for target in targets:
        if not isinstance(target,dict) or not target.get('path'): continue
        path=(ROOT/target['path']).resolve()
        try: path.relative_to(ROOT.resolve())
        except ValueError: raise ValueError('Review target escapes project root: '+str(target.get('path')))
        if not path.is_file(): raise ValueError('Reviewed artifact is missing: '+str(target.get('path')))
        if target.get('sha256') and hash_file(path)!=target['sha256']:
            raise ValueError('Artifact changed since request-review; re-run request-review before approving: '+str(target.get('path')))
    rec={'step_id':sid,'change_id':cid or '',
         'approver':args.approver,'approved_at':args.approved_at,
         'evidence':relpath(ev),'recorded_at':now(),
         'targets':targets,'review_packet':entry.get('review_packet','')}
    s['approvals_history']=list(s.get('approvals_history') or [])+[rec]
    lane['pending_approvals']=[x for x in (lane.get('pending_approvals') or []) if item_step(x)!=sid]
    s['last_updated']=now()
    atomic_json(STATE,s)
    append_event('approved',step_id=sid,change_id=rec['change_id'],approver=rec['approver'],targets=len(targets))
    packet_rel=entry.get('review_packet')
    if packet_rel:
        packet_path=(ROOT/packet_rel).resolve()
        if packet_path.is_file():
            try:
                packet=json.loads(packet_path.read_text(encoding='utf-8'))
                packet['approval']={'approver':rec['approver'],'approved_at':rec['approved_at'],'evidence':rec['evidence'],'recorded_at':rec['recorded_at']}
                atomic_json(packet_path,packet)
            except Exception:
                pass
    print(f'APPROVED={sid}')
    print('APPROVER='+args.approver)
    print('APPROVED_AT='+args.approved_at)
    print(f'NEXT=python scripts/workflow.py transition --step {sid} --evidence <stage evidence>'+(f' --change-id {cid}' if cid else ''))
    return 0

def cmd_status(args):
    s=load_state()
    if is_v2(s):
        print(json.dumps({'project_name':s.get('project_name'),'state_schema_version':V2_VERSION,
            'project':project_lane(s),'changes':s.get('changes'),'completed_changes':s.get('completed_changes',[]),
            'abandoned_changes':s.get('abandoned_changes',[]),'implementation_lease':s.get('implementation_lease'),
            'approvals_history':s.get('approvals_history',[]),'transition_history':s.get('transition_history',[]),
            'reopen_history':s.get('reopen_history',[]),'reset_history':s.get('reset_history',[]),
            'skip_history':s.get('skip_history',[]),'change_history':s.get('change_history',[]),
            'baseline':s.get('baseline',{})},ensure_ascii=False,indent=2)); return 0
    print(json.dumps({'project_name':s.get('project_name'),'active_change_id':s.get('active_change_id'),'current_step':s.get('current_step'),'completed_steps':s.get('completed_steps'),'skipped_steps':s.get('skipped_steps',[]),'completed_changes':s.get('completed_changes',[]),'abandoned_changes':s.get('abandoned_changes',[]),'pending_approvals':s.get('pending_approvals'),'blocked_items':s.get('blocked_items'),'approvals_history':s.get('approvals_history',[]),'last_transition':s.get('last_transition'),'transition_history':s.get('transition_history',[]),'reopen_history':s.get('reopen_history',[]),'reset_history':s.get('reset_history',[]),'skip_history':s.get('skip_history',[]),'change_history':s.get('change_history',[]),'baseline':s.get('baseline',{})},ensure_ascii=False,indent=2)); return 0

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

def verify_review_targets(rec):
    for target in rec.get('targets',[]) or []:
        if not isinstance(target,dict) or not target.get('path'): continue
        path=(ROOT/target['path']).resolve()
        try: path.relative_to(ROOT.resolve())
        except ValueError: raise ValueError('Review target escapes project root: '+str(target.get('path')))
        if not path.is_file(): raise ValueError('Reviewed artifact is missing: '+str(target.get('path')))
        if target.get('sha256') and hash_file(path)!=target['sha256']:
            raise ValueError('Artifact changed since approval; re-run request-review: '+str(target.get('path')))

def cmd_skip_stage(args):
    """Skip a conditional stage with machine evidence (currently Stage 06 no-UI)."""
    s=load_state(); sid=args.step; stage=BY_ID[sid]
    if not stage.get('conditional'):
        raise ValueError(f'{sid} is not a conditional stage and cannot be skipped')
    lane,cid=lane_for(s,sid,getattr(args,'change_id',None))
    if lane.get('current_step')!=sid:
        raise ValueError(f"current_step is {lane.get('current_step')}, not {sid}")
    missing=[d for d in stage['dependencies'] if not lane_dependencies_met(s,lane,BY_ID[d])]
    if missing: raise ValueError('Uncompleted dependencies: '+', '.join(missing))
    if lane.get('pending_approvals') or lane.get('blocked_items'):
        raise ValueError('Resolve pending approvals and blockers before skipping a stage')
    phase=baseline_phase_for_entry(sid)
    if stage['scope']=='change' and phase and cid:
        run_baseline_gate(['check-change','--change-id',cid,'--phase',phase],label=f'Change baseline skip gate ({phase})')
    ev=args.evidence or default_skip_evidence_path(s,sid,cid)
    ep=(ROOT/ev).resolve()
    try: ev_rel=ep.relative_to(ROOT.resolve()).as_posix()
    except ValueError: raise ValueError('Skip evidence must be inside project root')
    if not ep.is_file(): raise ValueError('Skip evidence file missing: '+ev)
    e=json.loads(ep.read_text(encoding='utf-8'))
    if e.get('step_id')!=sid: raise ValueError(f'Skip evidence step_id must be {sid}')
    if cid and e.get('change_id') not in (None,cid): raise ValueError('Skip evidence change_id mismatch')
    if e.get('skip') is not True: raise ValueError('Skip evidence must set "skip": true')
    if not str(e.get('reason','')).strip(): raise ValueError('Skip evidence requires a reason')
    checks=e.get('checks',[])
    if not checks: raise ValueError('Skip evidence requires at least one machine check')
    for check in checks:
        if check.get('status')!='passed': raise ValueError('Skip checks must all pass')
        if check.get('kind','automated')!='automated': raise ValueError('Skip checks must be automated')
        if check.get('exit_code')!=0: raise ValueError('Skip automated checks must exit 0')
        command=str(check.get('command',''))
        if 'check-figma-audit' not in command or '--no-ui' not in command:
            raise ValueError('Stage 06 skip requires a real check-figma-audit --no-ui check')
        proof=str(check.get('log','')).strip()
        if not proof: raise ValueError('Skip checks require a log path')
        pp=(ROOT/proof).resolve()
        try: pp.relative_to(ROOT.resolve())
        except ValueError: raise ValueError('Skip check log escapes project root')
        if not pp.is_file(): raise ValueError('Skip check log missing: '+proof)
    if is_v2(s):
        lane['completed_steps']=list(dict.fromkeys(list(lane.get('completed_steps') or [])+[sid]))
        lane['skipped_steps']=list(dict.fromkeys(list(lane.get('skipped_steps') or [])+[sid]))
        lane['pending_approvals']=[x for x in (lane.get('pending_approvals') or []) if item_step(x)!=sid]
        lane['blocked_items']=[x for x in (lane.get('blocked_items') or []) if item_step(x)!=sid]
        lane_ids=PROJECT_STEP_IDS if stage['scope']=='project' else CHANGE_STEP_IDS
        nxt=next_lane_stage(s,lane,lane_ids)
        lane['current_step']=nxt or lane_complete_value(lane_ids)
    else:
        s['completed_steps']=list(dict.fromkeys(s.get('completed_steps',[])+[sid]))
        s['skipped_steps']=list(dict.fromkeys(s.get('skipped_steps',[])+[sid]))
        s['pending_approvals']=[x for x in (s.get('pending_approvals') or []) if item_step(x)!=sid]
        s['blocked_items']=[x for x in (s.get('blocked_items') or []) if item_step(x)!=sid]
        completed=set(s['completed_steps'])
        nxt=next((x for x in STAGES if x['id'] not in completed and all(d in completed for d in x['dependencies'])),None)
        s['current_step']=nxt['id'] if nxt else 'ALL_STEPS_COMPLETE'
    s['last_updated']=now()
    record={'step_id':sid,'change_id':cid or '','skipped_at':s['last_updated'],'reason':e.get('reason',''),
            'evidence':ev_rel,'checks':checks,'conditional_reason':e.get('conditional_reason','')}
    s.setdefault('skip_history',[]).append(record)
    s['last_transition']=record
    atomic_json(STATE,s)
    append_event('skip',step_id=sid,change_id=cid or '',reason=e.get('reason',''))
    successors=[x for x in STAGES if sid in x['dependencies']]
    outcid=cid if stage['scope']=='change' else None
    for nxt_stage in successors:
        mp=manifest_path(sid,nxt_stage['id'],outcid)
        atomic_json(mp,{'version':'1.0','from_step':sid,'to_step':nxt_stage['id'],'change_id':outcid,
                        'created_at':now(),'skipped':True,'skip_reason':e.get('reason',''),
                        'evidence':ev_rel,'checks':checks,'artifacts':[],
                        'approval':{'status':'skipped','required':False}})
        print(f'HANDOFF_CREATED={relpath(mp)}')
    print(f'SKIPPED={sid}')
    print('CURRENT_STEP='+(lane['current_step'] if is_v2(s) else s['current_step']))
    return 0

@contextmanager
def state_transaction(timeout=15.0, interval=0.2):
    """Serialize the whole read-check-write cycle across processes."""
    lock=STATE.parent/(STATE.name+'.txn.lock')
    deadline=time.time()+timeout
    fd=None
    while True:
        try:
            fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
            os.write(fd,str(os.getpid()).encode()); os.close(fd); fd=None
            break
        except FileExistsError:
            if time.time()>=deadline:
                raise RuntimeError(f'State transaction lock timeout: {lock}; inspect for a stale lock')
            time.sleep(interval)
    try:
        yield
    finally:
        try: lock.unlink()
        except FileNotFoundError: pass

def _norm_lease_path(value):
    value=str(value or '').replace('\\','/').strip()
    while value.startswith('./'): value=value[2:]
    value=value.rstrip('/')
    if value.endswith('/**'): value=value[:-3].rstrip('/')
    return value

def slice_paths_for_change(cid):
    """Return {'owned': [...], 'integration': [...]} or None when unavailable."""
    design=ROOT/f'openspec/changes/{cid}/design.md'
    if not design.is_file(): return None
    try:
        import gate_common
        parsed=gate_common.parse_slice(design.read_text(encoding='utf-8'))
    except Exception:
        return None
    owned=[_norm_lease_path(item) for item in parsed.get('owned') or [] if _norm_lease_path(item)]
    integration=[]
    for entry in parsed.get('integration') or []:
        path=entry.get('path') if isinstance(entry,dict) else entry
        if path and _norm_lease_path(path): integration.append(_norm_lease_path(path))
    return {'owned':owned,'integration':integration}

def declaration_valid(cid):
    script=ROOT/'scripts'/'check-change-footprint.py'
    if not script.is_file(): return False
    result=subprocess.run([sys.executable,str(script),cid,'--declaration-only'],cwd=ROOT,capture_output=True,text=True)
    return result.returncode==0

def _paths_overlap(left,right):
    if not left or not right: return False
    for first in left:
        for second in right:
            if first==second or first.startswith(second+'/') or second.startswith(first+'/'):
                return True
    return False

def _lane_at_or_after_implementation(state,cid):
    lane=(state.get('changes') or {}).get(cid) or {}
    if str(lane.get('status','')).upper()!='ACTIVE': return False
    return lane.get('current_step') in ('08-implementation-orchestrator','09-independent-verification','10-acceptance-audit')

def acquire_implementation_lease(state,cid):
    """Acquire an exclusive lease, or a shared one when footprints are disjoint."""
    strategy=project_strategy()
    lease=state.get('implementation_lease')
    holders=lambda value: set((value or {}).get('change_ids') or ([value.get('change_id')] if (value or {}).get('change_id') else []))
    if strategy=='none' or not lease:
        if lease:
            existing=holders(lease)
            if existing and existing!={cid}:
                raise ValueError('IMPLEMENTATION_LEASE_HELD: '+', '.join(sorted(existing)))
        state['implementation_lease']={'mode':'exclusive','change_id':cid,'acquired_at':now()}
        return
    others=[other for other in active_change_ids(state) if other!=cid and _lane_at_or_after_implementation(state,other)]
    fallback=False
    if not others:
        state['implementation_lease']={'mode':'shared','change_ids':[cid],'acquired_at':now()}
        return
    own=slice_paths_for_change(cid)
    if own:
        own={'owned':[_norm_lease_path(item) for item in own.get('owned') or []],
             'integration':[_norm_lease_path(item) for item in own.get('integration') or []]}
    if not own or not declaration_valid(cid) or not (own['owned'] or own['integration']):
        fallback=True
    if not fallback:
        for other in others:
            other_slice=slice_paths_for_change(other)
            if other_slice:
                other_slice={'owned':[_norm_lease_path(item) for item in other_slice.get('owned') or []],
                             'integration':[_norm_lease_path(item) for item in other_slice.get('integration') or []]}
            if not other_slice or not declaration_valid(other):
                fallback=True; break
            if not (other_slice['owned'] or other_slice['integration']):
                fallback=True; break
            if _paths_overlap(own['owned'],other_slice['owned']) or _paths_overlap(own['integration'],other_slice['integration']):
                fallback=True; break
    if fallback:
        existing=holders(lease)
        if existing and existing!={cid}:
            raise ValueError('IMPLEMENTATION_LEASE_HELD: '+', '.join(sorted(existing)))
        state['implementation_lease']={'mode':'exclusive','change_id':cid,'acquired_at':now()}
        return
    existing=holders(lease)
    existing|= {cid}
    state['implementation_lease']={'mode':'shared','change_ids':sorted(existing),'acquired_at':now()}

def release_implementation_lease(state,cid):
    lease=state.get('implementation_lease')
    if not lease: return
    holders=set(lease.get('change_ids') or ([lease.get('change_id')] if lease.get('change_id') else []))
    if cid in holders:
        holders.discard(cid)
        if not holders:
            state['implementation_lease']=None
        elif lease.get('mode')=='shared':
            lease['change_ids']=sorted(holders)
            state['implementation_lease']=lease
        else:
            state['implementation_lease']=None

def cmd_transition(args):
    s=load_state(); sid=args.step; stage=BY_ID[sid]
    lane,cid=lane_for(s,sid,getattr(args,'change_id',None))
    own_pending=[x for x in (lane.get('pending_approvals') or []) if (x.get('step_id') if isinstance(x,dict) else x)==sid]
    e,artifacts=parse_evidence(args.evidence,sid,args.change_id or cid,require_approval=False)
    if e.get('change_id') and cid and e.get('change_id')!=cid: raise ValueError('Evidence change_id does not match the selected lane')
    if stage['scope']=='change' and not cid: raise ValueError('Change-scoped stage requires --change-id / active change')
    approval=e.get('approval',{}) if isinstance(e.get('approval'),dict) else {}
    rec=approval_record(s,sid,cid if stage['scope']=='change' else None)
    low_fast=str(s.get('approval_policy') or 'standard').strip().lower()=='risk-based' and stage.get('risk_level','high')=='low'
    if stage_requires_human_approval(stage,s) or own_pending or (approval.get('required') is True and not low_fast):
        if not rec:
            raise ValueError(f'Human approval required: run request-review, wait for the user, then run workflow.py approve --step {sid} before transition')
        verify_review_targets(rec)
        if approval.get('approver') and rec.get('approver') and approval['approver']!=rec['approver']:
            raise ValueError('Evidence approver does not match the recorded user approval')
        approval={'required':True,'status':'approved','approver':rec.get('approver',''),
                  'approved_at':rec.get('approved_at',''),'evidence':rec.get('evidence','')}
    own_blocked=[x for x in (lane.get('blocked_items') or [])
                 if (x.get('step_id') if isinstance(x,dict) else x)==sid]
    resolved=[r for r in (e.get('resolved_blockers') or []) if r.get('step_id')==sid]
    if own_blocked and resolved:
        for r in resolved:
            if not str(r.get('resolution','')).strip():
                raise ValueError('resolved_blockers requires a non-empty resolution')
            ev=str(r.get('evidence','')).strip()
            if not ev:
                raise ValueError('resolved_blockers requires an evidence path')
            p=(ROOT/ev).resolve()
            try: p.relative_to(ROOT.resolve())
            except ValueError: raise ValueError('resolved blocker evidence must be inside project root')
            if not p.is_file(): raise ValueError('resolved blocker evidence file missing: '+ev)
    errs=check_entry(sid,s,args.change_id,allow_pending_for_step=sid,
                     allow_blocked_for_step=sid if (own_blocked and resolved) else None)
    if errs:
        print('TRANSITION_BLOCKED'); [print(' - '+e) for e in errs]; return 3
    missing=missing_declared_outputs(e,sid,cid)
    if missing:
        raise ValueError('Evidence omits declared stage outputs (mark N/A with waiver_reason when not applicable): '+', '.join(missing))
    if sid in ('08-implementation-orchestrator','09-independent-verification'):
        gates_path=ROOT/'docs/architecture/quality-gates.json'
        if gates_path.exists():
            static_evidence_gate(sid,cid)
    # Hard gate: 07 -> 08 proves the Implementation Slice is valid; 08 -> 09
    # proves the landed diff stays inside the declared code footprint. Both are
    # strategy-driven and fail closed on an unreadable code-layout.json.
    if stage['scope']=='change' and cid and sid in ('07-detailed-design','08-implementation-orchestrator'):
        strategy=project_strategy()
        if strategy=='none':
            print('FOOTPRINT_GATE=SKIPPED (strategy none)')
        elif sid=='07-detailed-design':
            run_slice_gate(cid)
        else:
            run_footprint_gate(cid)
    if sid=='03-project-architecture-baseline':
        run_baseline_gate(['audit','--require-frozen'],label='Baseline freeze gate')
        artifact_paths={a['path'] for a in artifacts}
        required_baseline_artifacts={'docs/architecture/baseline-manifest.json','docs/architecture/constraint-registry.json'}
        missing=required_baseline_artifacts-artifact_paths
        if missing:
            raise ValueError('03-project-architecture-baseline evidence must hand off machine baseline artifacts: '+', '.join(sorted(missing)))
    transition_phase=baseline_phase_for_transition(sid)
    if stage['scope']=='change' and transition_phase and cid:
        run_baseline_gate(['check-change','--change-id',cid,'--phase',transition_phase],label=f'Change baseline transition gate ({transition_phase})')
    # Acquire the implementation lease only after every gate has passed, so a
    # failed 07 transition never leaves a lease behind.
    if is_v2(s) and stage['scope']=='change' and cid and sid=='07-detailed-design':
        acquire_implementation_lease(s,cid)
    evidence_path=Path(args.evidence); evidence_path=evidence_path if evidence_path.is_absolute() else ROOT/evidence_path
    if is_v2(s):
        lane['completed_steps']=list(dict.fromkeys(list(lane.get('completed_steps') or [])+[sid]))
        if stage['scope']=='change' and sid=='10-acceptance-audit':
            update_capability_registry(cid,'remove')
            lane['status']='ACCEPTED'; lane['current_step']='CHANGE_COMPLETE'
            release_implementation_lease(s,cid)
            completed=[item for item in (s.get('completed_changes') or []) if (item.get('change_id') if isinstance(item,dict) else item)!=cid]
            completed.append({'change_id':cid,'steps':list(CHANGE_STEP_IDS),'completed_at':now(),'acceptance_evidence':relpath(evidence_path)})
            s['completed_changes']=completed
        else:
            lane_ids=PROJECT_STEP_IDS if stage['scope']=='project' else CHANGE_STEP_IDS
            nxt=next_lane_stage(s,lane,lane_ids)
            lane['current_step']=nxt or lane_complete_value(lane_ids)
        if cid: s['active_change_id']=cid
    else:
        s['completed_steps']=list(dict.fromkeys(s['completed_steps']+[sid]))
        if cid: s['active_change_id']=cid
        completed=set(s['completed_steps']); nxt=next((x for x in STAGES if x['id'] not in completed and all(d in completed for d in x['dependencies'])),None)
        s['current_step']=nxt['id'] if nxt else 'ALL_STEPS_COMPLETE'
    s['last_completed_outputs']=[a['path'] for a in artifacts]
    s['last_updated']=now()
    transition_record={'step_id':sid,'completed_at':s['last_updated'],'change_id':cid,'evidence_path':relpath(evidence_path),'outputs':[a['path'] for a in artifacts],'checks':[{'name':c.get('name'),'status':c.get('status'),'exit_code':c.get('exit_code')} for c in e.get('checks',[])],'approval':approval}
    s.setdefault('transition_history',[]).append(transition_record)
    s['last_transition']=transition_record
    if approval.get('status')=='approved':
        lane['pending_approvals']=[x for x in (lane.get('pending_approvals') or []) if item_step(x)!=sid]
    if own_blocked and resolved:
        lane['blocked_items']=[x for x in (lane.get('blocked_items') or []) if (x.get('step_id') if isinstance(x,dict) else x)!=sid]
    atomic_json(STATE,s)
    append_event('transition',step_id=sid,change_id=cid,next_step=(lane.get('current_step') if is_v2(s) else s['current_step']),artifacts=len(artifacts))
    for artifact in artifacts:
        ap=(ROOT/artifact['path']).resolve()
        if ap.is_file():
            artifact['sha256']=hash_file(ap)
            artifact['size_bytes']=ap.stat().st_size
    annotate_mutable_artifacts(artifacts,sid,cid)
    successors=[x for x in STAGES if sid in x['dependencies']]
    for nxt_stage in successors:
        outcid=cid if stage['scope']=='change' else None
        mp=manifest_path(sid,nxt_stage['id'],outcid)
        manifest={'version':'1.0','from_step':sid,'to_step':nxt_stage['id'],'change_id':outcid,'created_at':now(),'baseline_version':e.get('baseline_version',''),'approval':approval,'checks':e.get('checks',[]),'artifacts':artifacts}
        atomic_json(mp,manifest)
        print(f'HANDOFF_CREATED={relpath(mp)}')
    print(f"COMPLETED={sid}")
    print('NEXT_STEP='+(lane.get('current_step') if is_v2(s) else s['current_step']))
    return 0

def cmd_handoff_create(args):
    # Explicit recovery utility: rebuild a handoff from the original approved
    # stage evidence. Free-form --file manifests are intentionally unsupported.
    if args.from_step not in BY_ID or args.to_step not in BY_ID: raise ValueError('Unknown from/to step')
    if args.to_step not in [x['id'] for x in STAGES if args.from_step in x['dependencies']]: raise ValueError('to-step is not a direct successor')
    if getattr(args,'file',None): raise ValueError('handoff-create no longer accepts --file; use the original stage --evidence')
    if not args.evidence: raise ValueError('handoff-create requires --evidence (the original approved stage evidence)')
    state=load_state()
    stage=BY_ID[args.from_step]
    if stage['scope']=='change':
        cid=resolve_change_id(state,args.from_step,args.change_id)
    else:
        cid=None
    evidence_data,artifacts=parse_evidence(args.evidence,args.from_step,cid,require_approval=False)
    approval=evidence_data.get('approval',{}) if isinstance(evidence_data.get('approval'),dict) else {}
    if stage_requires_human_approval(stage,state):
        rec=approval_record(state,args.from_step,cid if stage['scope']=='change' else None)
        if not rec:
            raise ValueError(f'{args.from_step} requires a recorded user approval; run request-review/approve first')
        verify_review_targets(rec)
        approval={'required':True,'status':'approved','approver':rec.get('approver',''),
                  'approved_at':rec.get('approved_at',''),'evidence':rec.get('evidence','')}
    annotate_mutable_artifacts(artifacts,args.from_step,cid)
    mp=manifest_path(args.from_step,args.to_step,cid)
    atomic_json(mp,{'version':'1.0','from_step':args.from_step,'to_step':args.to_step,'change_id':cid,'created_at':now(),'baseline_version':evidence_data.get('baseline_version',''),'approval':approval,'checks':evidence_data.get('checks',[]),'artifacts':artifacts})
    print(f'HANDOFF_CREATED={relpath(mp)}'); return 0

def cmd_recover_state(args):
    # Explicit recovery utility: restore a state backup written by
    # toolkit-sync apply (workflow/state-backups/) and record the event.
    backup=Path(args.backup)
    if not backup.is_file(): raise ValueError(f'backup not found: {backup}')
    try: data=json.loads(backup.read_text(encoding='utf-8'))
    except Exception as exc: raise ValueError(f'backup unreadable: {exc}')
    if not isinstance(data,dict): raise ValueError('backup is not a JSON object')
    if is_v2(data):
        atomic_json(STATE,data)
        append_event('recover',reason=getattr(args,'reason','') or '',backup=str(backup))
        print('RECOVERED=workflow-state.json')
        print('SCHEMA_VERSION='+V2_VERSION)
        return 0
    for k,v in {'state_schema_version':'1.0','completed_steps':[],'pending_approvals':[],'blocked_items':[],'last_completed_outputs':[],'active_change_id':'','transition_history':[],'approvals_history':[],'reopen_history':[],'reset_history':[],'topology_migrations':[],'completed_substeps':[],'current_substep':'','change_history':[],'skipped_steps':[],'skip_history':[],'abandoned_changes':[]}.items(): data.setdefault(k,v)
    if data.get('current_step') not in BY_ID and data.get('current_step')!='ALL_STEPS_COMPLETE': raise ValueError(f"Unknown current_step: {data.get('current_step')}")
    unknown=set(data.get('completed_steps',[]))-set(BY_ID)
    if unknown: raise ValueError('Unknown completed steps: '+', '.join(sorted(unknown)))
    atomic_json(STATE,data)
    append_event('recover',reason=getattr(args,'reason','') or '',backup=str(backup))
    print('RECOVERED=workflow-state.json'); return 0

def _cmd_migrate_v2(args,data):
    reset=set(getattr(args,'reset_step',None) or [])
    if not reset: raise ValueError('migrate-state v2 requires --reset-step')
    scopes={BY_ID[sid]['scope'] for sid in reset}
    if len(scopes)>1: raise ValueError('migrate-state cannot reset project and change stages in one call')
    scope=scopes.pop()
    cid=getattr(args,'change_id',None)
    if scope=='change':
        if not cid: raise ValueError('migrate-state --change-id is required when resetting change stages')
        lane,lane_cid=lane_for(data,next(sid for sid in reset if BY_ID[sid]['scope']=='change'),cid)
        scope_ids=CHANGE_STEP_IDS
    else:
        if active_change_ids(data):
            raise ValueError('Cannot reset project stages while ACTIVE change lanes exist; abandon them first: '+', '.join(active_change_ids(data)))
        lane=project_lane(data); lane_cid=''
        scope_ids=PROJECT_STEP_IDS
    changed=True
    while changed:
        changed=False
        for sid in scope_ids:
            if sid in reset: continue
            if any(dep in reset for dep in BY_ID[sid]['dependencies']):
                reset.add(sid); changed=True
    removed=[sid for sid in scope_ids if sid in reset]
    superseded=supersede_approvals(data,set(removed),args.reason,lane_cid if scope=='change' else '')
    invalidated=invalidate_handoffs(removed,args.reason,'migrate-state',cid if scope=='change' else None)
    lane['completed_steps']=[sid for sid in lane.get('completed_steps') or [] if sid not in removed]
    lane['skipped_steps']=[sid for sid in lane.get('skipped_steps') or [] if sid not in removed]
    lane['pending_approvals']=[item for item in lane.get('pending_approvals') or [] if item_step(item) not in removed]
    lane['blocked_items']=[item for item in lane.get('blocked_items') or [] if item_step(item) not in removed]
    lane['current_step']=next(sid for sid in scope_ids if sid in reset)
    if scope=='change' and lane.get('status')=='ACCEPTED':
        lane['status']='ACTIVE'
        data['completed_changes']=[item for item in data.get('completed_changes') or [] if (item.get('change_id') if isinstance(item,dict) else item)!=cid]
        release_implementation_lease(data,cid)
    data['last_updated']=now()
    if getattr(args,'note',None): data['notes']=args.note
    data.setdefault('topology_migrations',[]).append({'at':data['last_updated'],'reason':args.reason,'change_id':lane_cid,
        'reset_steps':sorted(reset),'removed_steps':removed,'superseded_approvals':superseded,
        'invalidated_handoffs':invalidated,'current_step':lane['current_step'],'scope':scope})
    atomic_json(STATE,data)
    append_event('migrate',reason=args.reason,removed_steps=len(removed),current_step=lane['current_step'],change_id=lane_cid)
    print('MIGRATED=workflow-state.json')
    print('CHANGE='+(lane_cid or ''))
    print('REMOVED='+', '.join(removed))
    print('CURRENT_STEP='+lane['current_step'])
    print('SUPERSEDED_APPROVALS='+str(len(superseded)))
    print('INVALIDATED_HANDOFFS='+str(len(invalidated)))
    return 0

def cmd_migrate_state(args):
    if not args.reason or not args.reason.strip():
        raise ValueError('migrate-state requires --reason')
    loaded=load_state()
    if is_v2(loaded): return _cmd_migrate_v2(args,loaded)
    data=json.loads(STATE.read_text(encoding='utf-8'))
    valid=set(BY_ID); reset=set(args.reset_step or [])
    # A reset step invalidates its whole downstream closure; otherwise the
    # state can claim Stage 04 is complete while Stage 03 is being redone.
    changed=True
    while changed:
        changed=False
        for stage in STAGES:
            if stage['id'] in reset: continue
            if any(dep in reset for dep in stage['dependencies']):
                reset.add(stage['id']); changed=True
    removed=[x for x in ORDER if x in reset]
    old=list(data.get('completed_steps',[]))
    legacy=[s for s in old if s not in valid or s in reset]
    data.setdefault('legacy_completed_steps',[])
    data['legacy_completed_steps']=list(dict.fromkeys(data['legacy_completed_steps']+legacy))
    data['completed_steps']=[s for s in old if s in valid and s not in reset]
    data['skipped_steps']=[s for s in (data.get('skipped_steps') or []) if s not in reset]
    completed=set(data['completed_steps'])
    broken=[s for s in completed if any(d not in completed for d in BY_ID[s]['dependencies'])]
    if broken:
        raise ValueError('migrate-state would leave stages with incomplete dependencies: '+', '.join(broken))
    superseded=supersede_approvals(data,set(removed),args.reason)
    invalidated=invalidate_handoffs(removed,args.reason,'migrate-state','*')
    nxt=next((x for x in STAGES if x['id'] not in completed and all(d in completed for d in x['dependencies'])),None)
    data['current_step']=nxt['id'] if nxt else 'ALL_STEPS_COMPLETE'
    data['last_updated']=now()
    if getattr(args,'note',None):
        data['notes']=args.note
    data.setdefault('topology_migrations',[]).append({'at':data['last_updated'],'reason':args.reason,'legacy_steps':legacy,'reset_steps':sorted(reset),'removed_steps':removed,'superseded_approvals':superseded,'invalidated_handoffs':invalidated,'completed_steps':data['completed_steps'],'current_step':data['current_step']})
    atomic_json(STATE,data)
    append_event('migrate',reason=args.reason,removed_steps=len(removed),current_step=data['current_step'])
    print(f'MIGRATED=workflow-state.json')
    print('COMPLETED='+', '.join(data['completed_steps']))
    print('LEGACY='+', '.join(data['legacy_completed_steps']))
    print('CURRENT_STEP='+data['current_step'])
    return 0

def supersede_approvals(state,removed,reason,change_id=None):
    superseded=[]
    for rec in (state.get('approvals_history') or []):
        if change_id is not None and (rec.get('change_id') or '')!=change_id: continue
        if item_step(rec) in removed and not rec.get('superseded_at'):
            rec['superseded_at']=now(); rec['supersede_reason']=reason
            superseded.append({'step_id':item_step(rec),'change_id':rec.get('change_id',''),'approver':rec.get('approver',''),'approved_at':rec.get('approved_at',''),'evidence':rec.get('evidence','')})
    return superseded

def invalidate_handoffs(from_steps,reason,source,change_id=None):
    removed=set(from_steps); paths=[]
    root=ROOT/'workflow/handoffs'
    if not root.exists(): return paths
    for mp in sorted(root.glob('**/*.json')):
        try: m=json.loads(mp.read_text(encoding='utf-8'))
        except Exception: continue
        if m.get('from_step') not in removed: continue
        actual_cid=m.get('change_id')
        if change_id == '*':
            pass
        elif change_id is None:
            if actual_cid not in (None,''): continue
        else:
            if actual_cid!=change_id: continue
        m['invalidated_at']=now(); m['invalidated_reason']=reason; m['invalidated_by']=source
        atomic_json(mp,m); paths.append(relpath(mp))
    return paths

def invalidate_all_handoffs(reason):
    paths=[]
    root=ROOT/'workflow/handoffs'
    if not root.exists(): return paths
    for mp in sorted(root.glob('**/*.json')):
        try: m=json.loads(mp.read_text(encoding='utf-8'))
        except Exception: continue
        m['invalidated_at']=now(); m['invalidated_reason']=reason; m['invalidated_by']='state-reset'
        atomic_json(mp,m); paths.append(relpath(mp))
    return paths

def cmd_reset_state(args):
    """Return workflow-state.json to the pre-Stage-01 position, keeping an audit archive."""
    s=load_state()
    if not args.reason or not args.reason.strip(): raise ValueError('reset-state requires --reason')
    clean=bool(getattr(args,'clean',False))
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    archive=None; archive_data=None
    previous_project=project_lane(s)
    if not clean:
        archive=ROOT/'workflow/evidence'/f'state-reset-{stamp}.json'
        archive_data={'archived_at':now(),'reason':args.reason,'note':getattr(args,'note','') or '',
                      'previous_current_step':previous_project.get('current_step'),'previous_completed_steps':previous_project.get('completed_steps',[]),
                      'previous_active_change_id':s.get('active_change_id',''),'previous_baseline_version':(s.get('baseline') or {}).get('overall_version',''),
                      'state':s}
        atomic_json(archive,archive_data)
    invalidated=invalidate_all_handoffs(args.reason)
    if is_v2(s):
        fresh={
            'project_name':s.get('project_name','项目'),
            'state_schema_version':V2_VERSION,
            'project':{'current_step':'01-project-bootstrap','completed_steps':[],'skipped_steps':[],'pending_approvals':[],'blocked_items':[]},
            'changes':{},
            'completed_changes':[],
            'abandoned_changes':[],
            'implementation_lease':None,
            'notes':getattr(args,'note','') or ('流程状态已由 reset-state 清洁初始化为未初始化；旧项目数据已移出工作区。' if clean else '流程状态已由 reset-state 重置为未初始化；旧状态与交接已归档。'),
            'transition_history':[],
            'topology_migrations':[],
            'reopen_history':[],
            'reset_history':([] if clean else [{
                'at':now(),'reason':args.reason,'note':getattr(args,'note','') or '',
                'archive':relpath(archive),'invalidated_handoffs':invalidated,
                'previous_current_step':archive_data['previous_current_step'],
                'previous_completed_steps':archive_data['previous_completed_steps'],
                'previous_active_change_id':archive_data['previous_active_change_id'],
                'previous_baseline_version':archive_data['previous_baseline_version'],
            }]),
            'baseline':{},
            'approvals_history':[],
            'approval_policy':'standard',
            'approval_policy_history':[],
            'last_completed_outputs':[],
            'last_transition':None,
            'skip_history':[],
            'change_history':[],
            'active_change_id':'',
        }
    else:
        fresh={
            'project_name':s.get('project_name','项目'),
            'active_change_id':'',
            'completed_steps':[],
            'current_step':'01-project-bootstrap',
            'skipped_steps':[],
            'skip_history':[],
            'abandoned_changes':[],
            'pending_approvals':[],
            'blocked_items':[],
            'last_completed_outputs':[],
            'notes':getattr(args,'note','') or ('流程状态已由 reset-state 清洁初始化为未初始化；旧项目数据已移出工作区。' if clean else '流程状态已由 reset-state 重置为未初始化；旧状态与交接已归档。'),
            'state_schema_version':'1.0',
            'transition_history':[],
            'topology_migrations':[],
            'completed_substeps':[],
            'current_substep':'',
            'reopen_history':[],
            'reset_history':([] if clean else [{
                'at':now(),'reason':args.reason,'note':getattr(args,'note','') or '',
                'archive':relpath(archive),'invalidated_handoffs':invalidated,
                'previous_current_step':archive_data['previous_current_step'],
                'previous_completed_steps':archive_data['previous_completed_steps'],
                'previous_active_change_id':archive_data['previous_active_change_id'],
                'previous_baseline_version':archive_data['previous_baseline_version'],
            }]),
            'baseline':{},
            'approvals_history':[],
            'approval_policy':'standard',
            'approval_policy_history':[],
            'last_transition':None,
        }
    atomic_json(STATE,fresh)
    append_event('reset',reason=args.reason,clean=clean,archive=(relpath(archive) if archive else ''),
                 invalidated_handoffs=len(invalidated))
    print('STATE_RESET=UNINITIALIZED')
    print('CURRENT_STEP=01-project-bootstrap')
    if archive: print('ARCHIVE='+relpath(archive))
    print('INVALIDATED_HANDOFFS='+str(len(invalidated)))
    return 0

def cmd_reopen(args):
    s=load_state(); sid=args.step
    if not args.reason or not args.reason.strip(): raise ValueError('reopen requires --reason')
    lane,cid=lane_for(s,sid,getattr(args,'change_id',None))
    if is_v2(s) and BY_ID[sid]['scope']=='project' and active_change_ids(s):
        raise ValueError('Cannot reopen a project stage while ACTIVE change lanes exist; abandon them first: '+', '.join(active_change_ids(s)))
    if sid not in (lane.get('completed_steps') or []) and lane.get('current_step')!=sid:
        raise ValueError('Only a completed stage or the current stage can be reopened')
    scope_ids=ORDER if not is_v2(s) else lane_scope_ids(sid)
    removed={sid}; changed=True
    while changed:
        changed=False
        for stage_id in scope_ids:
            if stage_id in removed: continue
            if any(dep in removed for dep in BY_ID[stage_id]['dependencies']):
                removed.add(stage_id); changed=True
    removed=[x for x in scope_ids if x in removed]
    approval_cid=cid if BY_ID[sid]['scope']=='change' else ('' if is_v2(s) else None)
    removed_approvals=supersede_approvals(s,set(removed),args.reason,approval_cid)
    invalidated=invalidate_handoffs(removed,args.reason,'reopen',cid if BY_ID[sid]['scope']=='change' else None)
    lane['completed_steps']=[x for x in lane.get('completed_steps') or [] if x not in removed]
    lane['skipped_steps']=[x for x in lane.get('skipped_steps') or [] if x not in removed]
    lane['pending_approvals']=[x for x in lane.get('pending_approvals') or [] if item_step(x) not in removed]
    lane['blocked_items']=[x for x in lane.get('blocked_items') or [] if item_step(x) not in removed]
    lane['current_step']=sid
    if is_v2(s) and lane.get('status')=='ACCEPTED':
        lane['status']='ACTIVE'
        s['completed_changes']=[item for item in s.get('completed_changes') or [] if (item.get('change_id') if isinstance(item,dict) else item)!=cid]
        release_implementation_lease(s,cid)
    s['last_updated']=now()
    record={'at':s['last_updated'],'reopened_step':sid,'change_id':cid or '','removed_steps':removed,
            'reason':args.reason,'note':getattr(args,'note','') or '',
            'removed_approvals':removed_approvals,'invalidated_handoffs':invalidated}
    s.setdefault('reopen_history',[]).append(record)
    atomic_json(STATE,s)
    append_event('reopen',step_id=sid,change_id=cid or '',removed_steps=len(removed),reason=args.reason)
    print('REOPENED='+sid)
    print('REMOVED='+', '.join(removed))
    print('SUPERSEDED_APPROVALS='+str(len(removed_approvals)))
    print('INVALIDATED_HANDOFFS='+str(len(invalidated)))
    print('CURRENT_STEP='+sid)
    return 0

def cmd_abandon_change(args):
    """Abandon the active Change without acceptance; project stages stay complete."""
    s=load_state()
    if is_v2(s):
        old=args.change_id or s.get('active_change_id') or ''
        lane=(s.get('changes') or {}).get(old)
        if not lane: raise ValueError(f'No change lane to abandon: {old or "(none)"}')
        if str(lane.get('status','')).upper()=='ABANDONED': raise ValueError(f'Change {old} is already abandoned')
        if lane.get('pending_approvals') or lane.get('blocked_items'):
            raise ValueError('Resolve pending approvals and blockers before abandoning a Change')
        if not args.reason or not args.reason.strip(): raise ValueError('abandon-change requires --reason')
        update_capability_registry(old,'remove')
        snapshot=list(lane.get('completed_steps') or [])
        skipped_snapshot=list(lane.get('skipped_steps') or [])
        superseded=supersede_approvals(s,set(CHANGE_STEP_IDS),args.reason,old)
        invalidated=invalidate_handoffs(CHANGE_STEP_IDS,args.reason,'abandon-change',old)
        lane['status']='ABANDONED'
        lane['current_step']='CHANGE_COMPLETE'
        lane['completed_steps']=[]
        lane['skipped_steps']=[]
        lane['pending_approvals']=[]
        lane['blocked_items']=[]
        s['completed_changes']=[item for item in s.get('completed_changes') or [] if (item.get('change_id') if isinstance(item,dict) else item)!=old]
        release_implementation_lease(s,old)
        s['active_change_id']=''
        s['last_updated']=now()
        s.setdefault('abandoned_changes',[]).append({
            'change_id':old,'abandoned_at':s['last_updated'],'reason':args.reason,
            'note':getattr(args,'note','') or '','completed_steps':snapshot,'skipped_steps':skipped_snapshot,
            'superseded_approvals':superseded,'invalidated_handoffs':invalidated})
        atomic_json(STATE,s)
        append_event('abandon_change',change_id=old,reason=args.reason,invalidated_handoffs=len(invalidated))
        print('CHANGE_ABANDONED='+old)
        print('CURRENT_STEP=CHANGE_COMPLETE')
        print('SUPERSEDED_APPROVALS='+str(len(superseded)))
        print('INVALIDATED_HANDOFFS='+str(len(invalidated)))
        return 0
    if s.get('pending_approvals') or s.get('blocked_items'):
        raise ValueError('Resolve pending approvals and blockers before abandoning a Change')
    old=s.get('active_change_id') or ''
    if not old: raise ValueError('No active Change to abandon')
    if args.change_id!=old: raise ValueError(f'--change-id must match active Change {old}')
    if not args.reason or not args.reason.strip(): raise ValueError('abandon-change requires --reason')
    change_steps=[x['id'] for x in STAGES if x['scope']=='change']
    snapshot=[x for x in s.get('completed_steps',[]) if x in change_steps]
    skipped_snapshot=[x for x in s.get('skipped_steps',[]) if x in change_steps]
    superseded=supersede_approvals(s,set(change_steps),args.reason)
    invalidated=invalidate_handoffs(change_steps,args.reason,'abandon-change',old)
    s['completed_steps']=[x for x in s.get('completed_steps',[]) if x not in change_steps]
    s['skipped_steps']=[x for x in s.get('skipped_steps',[]) if x not in change_steps]
    s['pending_approvals']=[x for x in s.get('pending_approvals',[]) if item_step(x) not in change_steps]
    s['blocked_items']=[x for x in s.get('blocked_items',[]) if item_step(x) not in change_steps]
    s['active_change_id']=''
    s['last_updated']=now()
    completed=set(s['completed_steps'])
    nxt=next((x for x in STAGES if x['id'] not in completed and all(d in completed for d in x['dependencies'])),None)
    s['current_step']=nxt['id'] if nxt else 'ALL_STEPS_COMPLETE'
    s.setdefault('abandoned_changes',[]).append({
        'change_id':old,'abandoned_at':s['last_updated'],'reason':args.reason,
        'note':getattr(args,'note','') or '','completed_steps':snapshot,'skipped_steps':skipped_snapshot,
        'superseded_approvals':superseded,'invalidated_handoffs':invalidated})
    atomic_json(STATE,s)
    append_event('abandon_change',change_id=old,reason=args.reason,invalidated_handoffs=len(invalidated))
    print('CHANGE_ABANDONED='+old)
    print('CURRENT_STEP='+s['current_step'])
    print('SUPERSEDED_APPROVALS='+str(len(superseded)))
    print('INVALIDATED_HANDOFFS='+str(len(invalidated)))
    return 0

def cmd_next_change(args):
    s=load_state()
    if is_v2(s):
        if not args.change_id or not args.change_id.strip():
            raise ValueError('next-change requires --change-id')
        old=s.get('active_change_id') or ''
        if not old: raise ValueError('No active change to close; use start-change for the first change')
        if args.change_id==old: raise ValueError('--change-id must differ from the completed change')
        lane=(s.get('changes') or {}).get(old) or {}
        if str(lane.get('status','')).upper()!='ACCEPTED':
            raise ValueError(f'Change {old} is not accepted; complete stage 10 before starting the next change')
        start_args=type('Args',(),{
            'change_id':args.change_id,'retry_abandoned':False,'waive_dependency':[],
            'reason':f'next-change after {old}','by':'','evidence':'','note':getattr(args,'note','') or '',
        })()
        result=cmd_start_change(start_args)
        if result==0:
            state=load_state()
            state.setdefault('change_history',[]).append({
                'at':now(),'completed_change_id':old,'next_change_id':args.change_id,
                'note':getattr(args,'note','') or ''})
            atomic_json(STATE,state)
            append_event('next_change',completed_change=old,active_change=args.change_id)
            print('CHANGE_CLOSED='+old)
        return result
    if s.get('pending_approvals') or s.get('blocked_items'):
        raise ValueError('Resolve pending approvals and blockers before starting the next change')
    if not args.change_id or not args.change_id.strip():
        raise ValueError('next-change requires --change-id')
    old=s.get('active_change_id') or ''
    if not old: raise ValueError('No active change to close; start the first change from stage 05')
    if args.change_id==old: raise ValueError('--change-id must differ from the completed change')
    change_steps=[x['id'] for x in STAGES if x['scope']=='change']
    completed=set(s.get('completed_steps',[]))
    missing=[x for x in change_steps if x not in completed]
    if missing: raise ValueError('Active change phase is not complete; missing: '+', '.join(missing))
    accepted=[r for r in s.get('transition_history',[]) if r.get('step_id')=='10-acceptance-audit' and r.get('change_id')==old]
    if not accepted: raise ValueError('No completed acceptance transition recorded for '+old)
    record=accepted[-1]
    s.setdefault('completed_changes',[]).append({
        'change_id':old,'steps':change_steps,'completed_at':record.get('completed_at',''),
        'acceptance_evidence':record.get('evidence_path','')})
    s['completed_steps']=[x for x in s['completed_steps'] if x not in change_steps]
    s['skipped_steps']=[x for x in s.get('skipped_steps',[]) if x not in change_steps]
    s['active_change_id']=args.change_id
    s['last_updated']=now()
    completed=set(s['completed_steps'])
    nxt=next((x for x in STAGES if x['id'] not in completed and all(d in completed for d in x['dependencies'])),None)
    s['current_step']=nxt['id'] if nxt else 'ALL_STEPS_COMPLETE'
    s.setdefault('change_history',[]).append({
        'at':s['last_updated'],'completed_change_id':old,'next_change_id':args.change_id,
        'note':getattr(args,'note','') or ''})
    atomic_json(STATE,s)
    append_event('next_change',completed_change=old,active_change=args.change_id)
    print('CHANGE_CLOSED='+old)
    print('ACTIVE_CHANGE='+args.change_id)
    print('CURRENT_STEP='+s['current_step'])
    return 0

def cmd_sync_baseline_index(args):
    s=load_state(); mp=ROOT/MANIFEST_FILE
    if not mp.is_file(): raise ValueError('Missing '+MANIFEST_FILE)
    manifest=json.loads(mp.read_text(encoding='utf-8'))
    domains={}
    for name,cfg in (manifest.get('domains') or {}).items():
        domains[name]={'version':cfg.get('version',''),'status':cfg.get('status',''),
                       'owner':cfg.get('owner',''),'approver':cfg.get('approver',''),
                       'approved_at':cfg.get('approved_at','')}
    s['baseline']={
        'manifest':MANIFEST_FILE,'constraint_registry':CONSTRAINT_FILE,'status':BASELINE_STATUS_FILE,
        'overall_version':manifest.get('overall_version') or manifest.get('version') or '',
        'status_value':manifest.get('status',''),'domains':domains}
    s['last_updated']=now()
    atomic_json(STATE,s)
    append_event('baseline_index_synced',overall_version=s['baseline'].get('overall_version',''))
    print('BASELINE_INDEX_SYNCED='+str(s['baseline']['overall_version']))
    return 0

def cmd_check_methods(args):
    p=(ROOT/args.evidence).resolve() if not Path(args.evidence).is_absolute() else Path(args.evidence).resolve()
    try:
        p.relative_to(ROOT.resolve())
    except ValueError:
        print('METHOD_EVIDENCE_FAILED: evidence file must be inside project root')
        return 1
    try:
        e=json.loads(p.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'METHOD_EVIDENCE_FAILED: cannot read evidence: {exc}')
        return 1
    if e.get('step_id')!=args.step:
        print(f'METHOD_EVIDENCE_FAILED: evidence.step_id must be {args.step}')
        return 1
    errors=validate_methods(e,args.step,ROOT)
    if errors:
        print('METHOD_EVIDENCE_FAILED')
        for error in errors: print(' - '+error)
        return 1
    print(f'METHOD_EVIDENCE_PASSED={args.step}')
    return 0

def cmd_check_coverage(args):
    p=(ROOT/args.evidence).resolve() if not Path(args.evidence).is_absolute() else Path(args.evidence).resolve()
    try:
        p.relative_to(ROOT.resolve())
    except ValueError:
        print('QUESTION_COVERAGE_FAILED: evidence file must be inside project root')
        return 1
    try:
        e=json.loads(p.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'QUESTION_COVERAGE_FAILED: cannot read evidence: {exc}')
        return 1
    if e.get('step_id')!=args.step:
        print(f'QUESTION_COVERAGE_FAILED: evidence.step_id must be {args.step}')
        return 1
    errors=validate_coverage(e,args.step,ROOT)
    if errors:
        print('QUESTION_COVERAGE_FAILED')
        for error in errors: print(' - '+error)
        return 1
    print(f'QUESTION_COVERAGE_PASSED={args.step}')
    return 0

def cmd_set_approval_policy(args):
    s=load_state()
    policy=str(args.policy).strip().lower()
    if policy not in ('standard','risk-based'):
        raise ValueError(f'Unknown approval policy: {args.policy}')
    if all_pending_items(s):
        raise ValueError('Cannot change approval_policy while reviews are pending; approve or clear them first')
    old=str(s.get('approval_policy') or 'standard')
    s['approval_policy']=policy
    s.setdefault('approval_policy_history',[]).append({
        'from':old,'to':policy,'reason':args.reason,'by':getattr(args,'by','') or '','at':now()})
    s['last_updated']=now()
    atomic_json(STATE,s)
    append_event('approval_policy_set',old=old,new=policy,reason=args.reason)
    print(f'APPROVAL_POLICY={policy}')
    print(f'PREVIOUS_APPROVAL_POLICY={old}')
    return 0

def main():
    ap=argparse.ArgumentParser(description=__doc__); sub=ap.add_subparsers(dest='cmd',required=True)
    sub.add_parser('status')
    p=sub.add_parser('check-entry'); p.add_argument('--step',required=True,choices=ORDER); p.add_argument('--change-id')
    p=sub.add_parser('handoff-verify'); p.add_argument('--manifest',required=True)
    p=sub.add_parser('handoff-create'); p.add_argument('--from-step',required=True,choices=ORDER); p.add_argument('--to-step',required=True,choices=ORDER); p.add_argument('--change-id'); p.add_argument('--baseline-version'); p.add_argument('--evidence',required=True)
    p=sub.add_parser('transition'); p.add_argument('--step',required=True,choices=ORDER); p.add_argument('--evidence',required=True); p.add_argument('--change-id')
    p=sub.add_parser('request-review'); p.add_argument('--step',required=True,choices=ORDER); p.add_argument('--change-id'); p.add_argument('--summary',default=''); p.add_argument('--target',action='append',default=[]); p.add_argument('--evidence')
    p=sub.add_parser('approve'); p.add_argument('--step',required=True,choices=ORDER); p.add_argument('--approver',required=True); p.add_argument('--approved-at',required=True); p.add_argument('--evidence',required=True); p.add_argument('--change-id')
    p=sub.add_parser('check-methods'); p.add_argument('--step',required=True,choices=ORDER); p.add_argument('--evidence',required=True)
    p=sub.add_parser('check-coverage'); p.add_argument('--step',required=True,choices=ORDER); p.add_argument('--evidence',required=True)
    p=sub.add_parser('set-approval-policy'); p.add_argument('--policy',required=True,choices=('standard','risk-based')); p.add_argument('--reason',required=True); p.add_argument('--by')
    p=sub.add_parser('migrate-state'); p.add_argument('--reason',required=True); p.add_argument('--note'); p.add_argument('--reset-step',action='append',default=[],choices=ORDER); p.add_argument('--change-id')
    p=sub.add_parser('recover-state'); p.add_argument('--backup',required=True); p.add_argument('--reason',default='')
    p=sub.add_parser('reopen'); p.add_argument('--step',required=True,choices=ORDER); p.add_argument('--reason',required=True); p.add_argument('--note'); p.add_argument('--change-id')
    p=sub.add_parser('skip-stage'); p.add_argument('--step',required=True,choices=ORDER); p.add_argument('--change-id'); p.add_argument('--evidence')
    p=sub.add_parser('reset-state'); p.add_argument('--reason',required=True); p.add_argument('--note'); p.add_argument('--clean',action='store_true')
    p=sub.add_parser('next-change'); p.add_argument('--change-id',required=True); p.add_argument('--note')
    p=sub.add_parser('abandon-change'); p.add_argument('--change-id',required=True); p.add_argument('--reason',required=True); p.add_argument('--note')
    p=sub.add_parser('upgrade-state'); p.add_argument('--reason',required=True); p.add_argument('--note')
    p=sub.add_parser('start-change'); p.add_argument('--change-id',required=True); p.add_argument('--retry-abandoned',action='store_true'); p.add_argument('--waive-dependency',action='append',default=[]); p.add_argument('--reason',default=''); p.add_argument('--by',default=''); p.add_argument('--evidence',default=''); p.add_argument('--note',default='')
    sub.add_parser('list-changes')
    sub.add_parser('sync-baseline-index')
    args=ap.parse_args()
    mutating={'transition','request-review','approve','set-approval-policy','migrate-state','recover-state','reopen','skip-stage','reset-state','next-change','abandon-change','upgrade-state','start-change','handoff-create','sync-baseline-index'}
    context=state_transaction() if args.cmd in mutating else nullcontext()
    try:
        with context:
            return {'status':cmd_status,'check-entry':cmd_check_entry,'handoff-verify':cmd_handoff_verify,'handoff-create':cmd_handoff_create,'transition':cmd_transition,'request-review':cmd_request_review,'approve':cmd_approve,'set-approval-policy':cmd_set_approval_policy,'migrate-state':cmd_migrate_state,'recover-state':cmd_recover_state,'reopen':cmd_reopen,'skip-stage':cmd_skip_stage,'reset-state':cmd_reset_state,'next-change':cmd_next_change,'abandon-change':cmd_abandon_change,'upgrade-state':cmd_upgrade_state,'start-change':cmd_start_change,'list-changes':cmd_list_changes,'sync-baseline-index':cmd_sync_baseline_index,'check-methods':cmd_check_methods,'check-coverage':cmd_check_coverage}[args.cmd](args)
    except Exception as exc:
        print(f'ERROR: {exc}',file=sys.stderr); return 2
if __name__=='__main__': raise SystemExit(main())
