"""Independent combined355 retry-v2 Source review; no owner module/main/build evaluated."""
from pathlib import Path
import ast
import hashlib
import json
import re
import stat

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'combined-native-build-controller-candidate-v2'
SOURCE_SHA = '24584f9686e3c88d935a2d92c376818b462692af9dc68de2703fbf73748fef38'
seen = {}
checks = []
check_count = 0


def need(value, label):
    global check_count
    check_count += 1
    if not value:
        raise AssertionError(label)


def checkpoint(label):
    checks.append(label)


def ident(p):
    s = p.lstat()
    need(stat.S_ISREG(s.st_mode), 'Ordinary non-symlink file: ' + str(p))
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns,
            stat.S_IMODE(s.st_mode), s.st_nlink, str(p.resolve()))


def file(row):
    p = Path(row['path'])
    need(p.is_absolute() and str(p) == row['path'], 'Canonical absolute path')
    need(set(row) == {'path', 'sha256', 'bytes'}, 'Exact three-field descriptor')
    need(type(row['bytes']) is int and row['bytes'] >= 0, 'Actual finite byte count')
    need(re.fullmatch('[a-f0-9]{64}', row['sha256']) is not None, 'SHA256 descriptor')
    before = ident(p)
    if str(p) in seen:
        need(seen[str(p)] == (row, before), 'Repeated row and identity unchanged')
        return row
    h = hashlib.sha256()
    length = 0
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
            length += len(b)
    need(before == ident(p), 'File stable through streamed hash')
    need(length == row['bytes'] and h.hexdigest() == row['sha256'], 'Exact actual file bytes')
    seen[str(p)] = (dict(row), before)
    return row


def row(p):
    p = Path(p)
    b = p.read_bytes()
    return file(dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b)))


def read(d):
    file(d)
    b = Path(d['path']).read_bytes()
    need(len(b) == d['bytes'] and hashlib.sha256(b).hexdigest() == d['sha256'], 'Stable JSON read')
    return json.loads(b)


def tree(p):
    need(p.is_dir() and not p.is_symlink(), 'Ordinary tree root')
    names = []
    for q in p.rglob('*'):
        need(not q.is_symlink(), 'No tree aliases')
        need(q.is_dir() or q.is_file(), 'Ordinary tree entry')
        if q.is_file():
            names.append(q.relative_to(p).as_posix())
    return sorted(names)


def family(d):
    value = read(d)
    need(value['schemaVersion'] == 1 and 0 < len(value['files']) <= 2048, 'Finite indexed family')
    base = Path(d['path']).parent
    names = ['index.json']
    rows = [d]
    for m in value['files']:
        n = m['path']
        need(n and not Path(n).is_absolute() and all(x not in ('', '.', '..') for x in n.split('/')) and '\\' not in n, 'Confined indexed path')
        names.append(n)
        rows.append(file(dict(m, path=str(base / n))))
    need(len(names) == len(set(names)), 'Unique family membership')
    need(tree(base) == sorted(names), 'Complete exact indexed membership')
    return rows


def proof(pair):
    members = family(pair['index'])
    need(sum(d == pair['result'] for d in members) == 1, 'Result indexed exactly once')
    return read(pair['result'])


def descriptors(value):
    if isinstance(value, dict):
        if set(value) == {'path', 'sha256', 'bytes'}:
            yield value
        else:
            for item in value.values():
                yield from descriptors(item)
    elif isinstance(value, list):
        for item in value:
            yield from descriptors(item)


def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
    import copy,io
    ix=row(SOURCE/'index.json');need(ix['sha256']==SOURCE_SHA and ix['bytes']==4998,'Held exact retry Source2458');members=family(ix);need(len(members)==32,'Complete31 indexed members plus index')
    refs=read(row(SOURCE/'references.json'));ledger=read(row(SOURCE/'source-inputs.json'));der=read(row(SOURCE/'derivations.json'));future=read(row(SOURCE/'future-source-review-contract.json'))
    need(len(ledger['files'])==len(ledger['modeRows'])==4515 and len(refs['families'])==12,'Full4515 mode/file rows and12 original families')
    rows={r['path']:r for r in ledger['files']};need(len(rows)==4515 and sum(r['bytes']for r in rows.values())==2446337314,'Whole unique external Source/protection bytes')
    for d in ledger['files']:file(d)
    for m in ledger['modeRows']:file(m['file']);need(rows.get(m['file']['path'])==m['file']and ident(Path(m['file']['path']))[5]==m['mode'],'Every finite captured mode matches')
    for d in refs['families']:
        for r in family(d):need(rows.get(r['path'])==r,'Every inherited family complete and covered by runtime intake')
    own={r['path']:r for r in members}
    for d in descriptors(refs):file(d);need(rows.get(d['path'])==d or own.get(d['path'])==d,'Every referenced original/own physical dependency covered')
    failed=proof(refs['failedBuildReview']);probe=proof(refs['privateRustupProbeReview']);stage=proof(refs['actualStageReview']);integration=proof(refs['integrationSourceReview'])
    checkpoint('Complete held31 own members,4515 external hashes/modes/2.446GB,12 exact family memberships and all own/original reference roles independently authenticated')
    # Exact byte offsets in five afterimages, no recipe/helper execution.
    need(len(der['files'])==5 and sum(len(r['edits'])for r in der['files'])==43 and der['nativeFilesChanged']==0 and der['importedModuleNamespacesRebound']is False,'Finite five-file43-edit Source-only cut')
    for r in der['files']:
        file(r['donor']);need(row(SOURCE/r['output'])==r['after'],'Exact real afterimage descriptor');old=Path(r['donor']['path']).read_bytes();new=(SOURCE/r['output']).read_bytes();forward=old
        for e in reversed(r['edits']):
            pos=e['beforeOffset'];before=e['before'].encode();need(forward[pos:pos+len(before)]==before,'Every exact forward old-byte offset');forward=forward[:pos]+e['after'].encode()+forward[pos+len(before):]
        need(forward==new,'Whole forward derivation')
        inverse=new
        for e in reversed(r['edits']):
            pos=e['afterOffset'];after=e['after'].encode();need(inverse[pos:pos+len(after)]==after,'Every exact inverse new-byte offset');inverse=inverse[:pos]+e['before'].encode()+inverse[pos+len(after):]
        need(inverse==old,'Whole exact donor recovery')
    policy=read(refs['policy']);oldpolicy=read(refs['originalConfiguredPolicy']);expected=copy.deepcopy(oldpolicy)
    expected['contexts']['workRoot']='/private/tmp/starling-node-compat/combined-native355-v2-build';expected['contexts']['freezeRoot']='/private/tmp/starling-node-compat/combined-native355-v2-freeze'
    need(policy==expected,'Only real policy WORK/FREEZE context changed; complete native355/3/11 data unchanged')
    need(len(policy['expectedNativeSourceManifest'])==355 and len(policy['expectedComponentizeSourceManifest'])==3 and len(policy['selectedModuleManifests'])==len(policy['selectedManifestValues'])==11,'Complete355+3/11 native layer')
    need((SOURCE/'native-admission-model.py').read_bytes()==Path(der['files'][-1]['donor']['path']).read_bytes(),'Pure current355 metadata model unchanged')
    stage_plan=read(refs['stageCopyPlan'])['files'];journal=read(refs['stageResult']);configured=Path(policy['contexts']['configuredSourceRoot'])
    need(journal['copies']==journal['copiesCompleted']==stage_plan and len(stage_plan)==1613,'Actual same1613 Source stage,not a new stage')
    target_ids=set();original_ids=set()
    for m in stage_plan:
        a=file(dict(path=m['original'],sha256=m['sha256'],bytes=m['bytes']));b=file(dict(path=str(configured/m['path']),sha256=m['sha256'],bytes=m['bytes']));sa,sb=ident(Path(a['path'])),ident(Path(b['path']))
        need(sa[5]==sb[5]==m['sourceMode']and sb[6]==1 and sa[:2]!=sb[:2]and sb[:2]not in target_ids,'Each actual source-stage mode/distinct inode/nlink');target_ids.add(sb[:2]);original_ids.add(sa[:2])
    need(not target_ids&original_ids and(configured/'.git/HEAD').read_text()=='54b3329b3ce818fd1f244e871e9c259b63667cda\n'and not(configured/'.git/objects/info/alternates').exists(),'Actual detached Source/stage independence/no alternates preserved')
    for m in policy['expectedNativeSourceManifest']:
        name=str(configured/m['path']);need(name in rows and rows[name]['sha256']==m['sha256'],'Every actual staged native355 unchanged')
    failed_inventory=read(refs['protectedTreeInventories'][0]);failed_root=Path(failed_inventory['root']);need(len(failed_inventory['files'])==755 and tree(failed_root)==sorted(m['path']for m in failed_inventory['files']),'Whole old failed755 membership exact')
    for m in failed_inventory['files']:file(dict(path=str(failed_root/m['path']),sha256=m['sha256'],bytes=m['bytes']));need(ident(failed_root/m['path'])[5]==m['mode'],'Each old failed file mode unchanged')
    for host in refs['hostTools']:file(host['executable']);need(str(Path(host['selectedAlias']).resolve())==host['executable']['path'],'Exact finite original host alias')
    checkpoint('Five complete afterimages/43 forward+inverse edits; unchanged model/355+3/11 policy except two own contexts; all1613 actual stage pairs/755 old failed files/modes/inodes/host aliases preserved')
    text=(SOURCE/'controller.py').read_text();nodes=ast.parse(text);functions={n.name:n for n in nodes.body if isinstance(n,ast.FunctionDef)}
    env_node=next(n.value for n in nodes.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ENV_POLICY'for t in n.targets));need(isinstance(env_node,ast.Call)and isinstance(env_node.func,ast.Name)and env_node.func.id=='dict'and not env_node.args,'Literal ENV policy only')
    env_policy={k.arg:ast.literal_eval(k.value)for k in env_node.keywords};need(env_policy==future['requiredFixedValues']['requiredRootEnvironmentPolicy'],'Genuine future wire environment policy exact')
    root_template=read(row(SOURCE/'root-authority.template.json'))
    scope=dict(Path=Path,hashlib=hashlib,SOURCE_SHA=refs['integrationIndex']['sha256'],OWN=SOURCE,SOURCE=configured,WORK=Path(policy['contexts']['workRoot']),FREEZE=Path(policy['contexts']['freezeRoot']),BUILD_OUTPUT=Path(root_template['buildOutputRoot']),OUT=Path(root_template['externalOutputRoot']),OBSERVER=Path(root_template['rootObserverOutputRoot']),TIMEOUT=7200,START_FREE=2147483648,STOP_FREE=838860800,ENV_POLICY=env_policy)
    allowed=['clean_environment','require_clean_environment','validate_terminal','root_model','stage_model','source_peer_model','controller_peer_model','cache_plan_model','build_environment','stream_copy','failure_model','probe_model']
    exec(compile(ast.Module(body=[functions[n]for n in allowed],type_ignores=[]),str(SOURCE/'controller.py')+'#extracted-pure','exec'),scope)
    cases=[]
    def good(fn,name):fn();cases.append(name)
    def deny(fn,name):
        try:fn()
        except(AssertionError,KeyError,TypeError,ValueError,UnicodeError):cases.append(name);return
        raise AssertionError('Pure negative unexpectedly accepted: '+name)
    good(lambda:scope['source_peer_model'](integration),'Actual08bf Source peer')
    for value,fn,label in [(stage,'stage_model','actual1613 stage'),(failed,'failure_model','actualfailedv1'),(probe,'probe_model','actualprivateprobe')]:good(lambda value=value,fn=fn:scope[fn](value,refs),label)
    cache=read(refs['cachePlan']);good(lambda:scope['cache_plan_model'](cache),'Exact original four cache sources/new WORK')
    need(sum(m['source']['bytes']for m in cache['copies'])==205865445,'Finite205865445B cache population')
    for m in cache['copies']:need(not m['source']['path'].startswith(str(failed_root)+'/'),'No failed-work toolchain/cache seeds');file(m['source'])
    for value,fn,key,bad in [(probe,'probe_model','privateAutoSelfUpdateDisabled',False),(probe,'probe_model','nativeBuildAuthorityGranted',True),(probe,'probe_model','rawCommandCount',5),(failed,'failure_model','nativeBuildSucceeded',True),(failed,'failure_model','repeatOrResumeGranted',True),(stage,'stage_model','nativeSourceFiles',342),(stage,'stage_model','grantsNativeBuildAuthority',True)]:
        altered=copy.deepcopy(value);altered[key]=bad;deny(lambda altered=altered,fn=fn:scope[fn](altered,refs),'Reject crossed actual role '+fn+' '+key)
    own_model=dict(path=str(SOURCE/'index.json'),sha256=SOURCE_SHA,bytes=ix['bytes'])
    deny(lambda:scope['root_model'](root_template,own_model,refs),'Unissued Root refuses')
    future_root=copy.deepcopy(root_template);future_root.update(state='ROOT_REVIEWED_COMBINED355_NORMAL_OFF_BUILD_RETRY_V2',phase='native-build-only',buildAllowed=True,controllerIndex=ix,controllerEntry=row(SOURCE/'controller.py'),cacheSeedCopiesAllowed=True,dependencyNetworkWithinBuildAllowed=True)
    good(lambda:scope['root_model'](future_root,ix,refs),'Pure future Root shape only,no actual authority emitted')
    for key,value in [('workRoot',str(failed_root)),('configuredSourceRoot','/wrong'),('oldWorkResumeAllowed',True),('retryRecipe',{}),('rootLauncherRequired',False),('rootEnvironmentPolicy',{}),('parallelBuilds',2),('nativeSourceFiles',342),('selectedManifestCount',9),('externalParentDeadlineSeconds',7201),('freezeAllowed',True),('gcReconfigureAllowed',True),('engineExecutionAllowed',True),('operationalAdmission',True),('actualBuildResult',{})]:
        altered=copy.deepcopy(future_root);altered[key]=value;deny(lambda altered=altered:scope['root_model'](altered,ix,refs),'Reject future Root '+key)
    peer_value=dict(future['requiredFixedValues'],state=future['requiredState'],controllerSourceIndexSha256=SOURCE_SHA)
    good(lambda:scope['controller_peer_model'](peer_value,ix,refs),'Exact prospective own Source peer wire')
    for key,value in [('controllerSourceIndexSha256','0'*64),('retryRecipeSha256','0'*64),('sourceReviewPassed',False),('hostActionsInvoked',True),('privateRustupProbeReviewIndexSha256','0'*64)]:
        altered=copy.deepcopy(peer_value);altered[key]=value;deny(lambda altered=altered:scope['controller_peer_model'](altered,ix,refs),'Reject own peer '+key)
    parent={'HOME':'home-model','home':'lower-model','CODEX_HOME':'codex-model','PATH':'untouched-model','BASH_FUNC_rustup%%':'inert','NODE_OPTIONS':'inert','RUSTUP_HOME':'old-model','CARGO_TARGET_DIR':'old-model'}
    parent.update({k:'inert'for k in env_policy['removeExactNames']});before=copy.deepcopy(parent);clean,removed=scope['clean_environment'](parent)
    need(parent==before and all(clean[k]==parent[k]for k in ['HOME','home','CODEX_HOME'])and removed==sorted(k for k in parent if k.startswith('BASH_FUNC_')or k in env_policy['removeExactNames']),'Actual pure cleaning preserves home/input and records only removed names');cases.append('Actual clean environment pure')
    deny(lambda:scope['require_clean_environment'](parent),'Direct dirty parent refuses');good(lambda:scope['require_clean_environment'](clean),'Clean parent accepts')
    env=scope['build_environment'](parent,refs);need(all(env[k]==v for k,v in refs['buildEnvironment'].items())and all(env[k]==parent[k]for k in ['HOME','home','CODEX_HOME'])and all(k not in env for k in ['NODE_OPTIONS','CARGO_TARGET_DIR','BASH_ENV','BASH_FUNC_rustup%%']),'Actual build environment exact selected private homes/onejob and no overrides');cases.append('Actual build environment pure')
    for payload in [b'',b'abc',bytes(range(256))*4097]:
        dst=io.BytesIO();actual=scope['stream_copy'](io.BytesIO(payload),dst);need(actual==dict(sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload))and dst.getvalue()==payload,'Exact finite in-memory copy');cases.append('Exact in-memory copy '+str(len(payload)))
    class Short:
        def write(self,b):return len(b)-1
    deny(lambda:scope['stream_copy'](io.BytesIO(b'ab'),Short()),'Short-write cache refusal')
    recipe=(SOURCE/'build-engine.sh').read_text();blocks={m.group(1):m.group(2)for m in re.finditer(r"<<'([A-Z]+)'\n(.*?)\n\1(?:\n|$)",recipe,re.S)}
    need(len(blocks)==5 and 'PYRUSTUP'in blocks,'Complete five actual embedded Python blocks')
    for code in blocks.values():ast.parse(code)
    settings_nodes=ast.parse(blocks['PYRUSTUP']);settings_fn=next(n for n in settings_nodes.body if isinstance(n,ast.FunctionDef)and n.name=='validate_private_settings');ns={};exec(compile(ast.Module(body=[settings_fn],type_ignores=[]),'#actual-private-setting-pure','exec'),ns)
    good(lambda:ns['validate_private_settings'](Path(probe['settings']['path']).read_bytes()),'Actual reviewed107B settings at genuine preinstall guard')
    for bad in [b'',b'auto_self_update = "enable"\n',b'auto_self_update = "disable"\nauto_self_update = "disable"\n',b'\xff','not-bytes']:deny(lambda bad=bad:ns['validate_private_settings'](bad),'Private-setting refusal '+repr(bad))
    need(recipe.index('rustup set auto-self-update disable')<recipe.index("<<'PYRUSTUP'")<recipe.index('rustup toolchain install 1.88.0 --profile minimal')<recipe.index('rustup target add --toolchain 1.88.0 wasm32-wasip1')<recipe.index('cmake -S'),'Persistent actual disable/read guard precedes original pinned install/target/CMake')
    need('sha256_file "$recipe_path" > "$recipe_before"'in recipe and "'buildRecipeSha256': digest(pathlib.Path(actual_recipe))"in recipe,'Own actual recipe before/after/raw sidecar identity')
    helper=(SOURCE/'layer-policy.py').read_text();need("REPO=Path('/private/tmp/starling-node-compat/combined-native355-v1-source')"in helper and "DONOR_INPUTS=REPO/"in helper and "digest(DONOR_INPUTS)==AUTH_SHA256"in helper,'Actual own helper/unchanged staged donor context')
    for key in ['controller.py','layer-policy.py','native-admission-model.py','prepare-data.py','derive-data.py','check-source.py']:ast.parse((SOURCE/key).read_text())
    snippets={n:ast.get_source_segment(text,functions[n])for n in ['authorize','recheck','main','launcher','parent','worker','load_actual','validate_metadata']}
    need("manifest['files']"in snippets['authorize']and "manifest['modeRows']"in snippets['authorize']and 'recheck(frame);return frame'in snippets['authorize'],'Complete family/hash/mode/stage/failed-work/alias guards before custom import')
    need(snippets['launcher'].index('clean_environment')<snippets['launcher'].index('os.execve')and "write(OBSERVER/'preentry-environment.json'"in snippets['launcher'],'Actual clean bootstrap exec,preentry record before parent')
    need(snippets['parent'].index('require_clean_environment')<snippets['parent'].index('load_actual')and snippets['worker'].index('require_clean_environment')<snippets['worker'].index('load_actual'),'Dirty direct entries refuse before genuine monitor/lifecycle imports')
    need('monitor.monitor(argv,str(REPO)'in snippets['parent']and 'OUT,TIMEOUT,'in snippets['parent']and 'lifecycle.monitor_owned_command(command,str(SOURCE),env,log,build_free)'in snippets['worker'],'Real original0af7200/f751 inner lifecycle interfaces')
    need('finally:recheck(frame)'in snippets['main']and 'finally:recheck(frame)'in snippets['parent']and "'final-protection-recheck'"in snippets['worker'],'Main/parent/worker final+failure complete original protections')
    need(snippets['worker'].index('lifecycle.publish_result(')<snippets['worker'].index("assert result['launcherExitCode']==0"),'Whole raw result/log before acceptance assertion')
    for k in ['WORK','FREEZE','BUILD_OUTPUT','OUT','OBSERVER']:need(not scope[k].exists()and not scope[k].is_symlink(),'Genuine new dormant role absent '+k)
    need(not any(t in text+helper for t in ['globals().update','.REPO=','.HERE=','.OUTPUT=','sys.modules[']),'No donor namespace injection/rebinding')
    checkpoint('Actual extracted pure Root/source/stage/failure/probe/cache/env/copy/settings functions tested only on inert DATA; six own Python/five embedded ASTs; concrete API/failure/raw-before-assert/auth sequencing reviewed')
    for name,(d,before)in list(seen.items()):need(ident(Path(name))==before,'Every observed input identity/mode final unchanged')
    for d in refs['families']:family(d)
    need(tree(failed_root)==sorted(m['path']for m in failed_inventory['files']),'Final failed-work membership unchanged')
    dump('pure-review-results.json',dict(schemaVersion=1,passed=True,count=len(cases),cases=cases,actualFunctionsASTExtracted=allowed+['validate_private_settings'],ownerModuleImported=False,authorizeOrOperationalBodyInvoked=False,hostOrRustupOrBuildInvoked=False))
    coverage=dict(ownIndexedMembers=31,declaredInputFiles=4515,modeRows=4515,completeFamilies=12,stageCopyPairs=1613,failedWorkFiles=755,nativeSourceFiles=355,retainedParentNativeFiles=348,integratedNativeChanges=7,newNativeChanges=0,externalEmbeddingSources=3,selectedWholeManifests=11,derivationFiles=5,exactForwardInverseEdits=43,pureReviewerCases=len(cases),pythonAstFiles=6,embeddedPythonBlocks=5,cacheSourceFiles=4,cacheSourceBytes=205865445)
    result=dict(future['requiredFixedValues'],state=future['requiredState'],controllerSourceIndexSha256=SOURCE_SHA,sourceIndex=ix,entry=row(SOURCE/'controller.py'),recipe=refs['recipe'],helper=refs['helper'],policy=refs['policy'],failedBuildReview=refs['failedBuildReview'],privateRustupProbeReview=refs['privateRustupProbeReview'],actualStageReview=refs['actualStageReview'],coverage=coverage,findings=[],actualBuildProof=None,grantsAnyActionAuthority=False,operationalAdmission=False,runtimeAcceptanceClaim=False,limits=['Source/read-hash/AST/pure only; no owner module/authorize/launcher/parent/worker/helper operational body,monitor,lifecycle,Rustup,Bash,compiler or guest executed.','New retry reuses actual configured355 Source read-only,never failed WORK/toolchain. Fresh WORK/FREEZE/output/observer roots and real Root-owned launcher phase remain required.','Observed old Rustup success is finite diagnostic DATA; environment limitations remain and no native build success is inferred.','The integrated stdlib launcher cleans Bash startup controls before exec into parent; parent/worker then independently refuse dirty entry before action imports. This is finite known-startup policy,not global OS/env attestation.','Cache disk checks are before/after bounded population; one-second floor applies inside actual build lifecycle. SDKarchive/version equality occurs after actual command,not precompiler.','Failure before owned inner output may retain only outer raw streams/terminal; no failed partial output is accepted. Whole worker/parent JSONL must be decoded as separate records.','Actual new metadata must carry own recipe/helper/policy and native355+3/11/fullcompile/link/library/source protection. No old native metadata/state/Root projection or freeze/export/bootstrap/runtime/promotion grant follows.'])
    scope['controller_peer_model'](result,ix,refs)
    dump('results.json',result);dump('result-contract.json',dict(schemaVersion=1,requiredReviewState=result['state'],requiredFixedValues={k:result[k]for k in future['requiredFixedValues']},requiredOwnIndexBinding=dict(controllerSourceIndexSha256=SOURCE_SHA),requiredExactDescriptors={k:result[k]for k in ['sourceIndex','entry','recipe','helper','policy']},requiredCoverage=coverage,actualBuildProof=None,grantsAnyActionAuthority=False))
    dump('input-hashes.json',dict(schemaVersion=1,files=[d for name,(d,b)in sorted(seen.items())if not Path(name).is_relative_to(HERE)],observedSourceDataOnly=True))
    dump('audit-results.json',dict(schemaVersion=1,passed=True,checks=check_count,observedFiles=len(seen),observedBytes=sum(d['bytes']for d,b in seen.values()),checkpoints=checks,ownerActionsInvoked=False))
    print(json.dumps(dict(passed=True,checks=check_count,files=len(seen),pureCases=len(cases))))
if __name__=='__main__':main()
