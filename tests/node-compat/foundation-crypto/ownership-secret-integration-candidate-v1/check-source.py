"""Own read/hash/AST and pure source models. No owner modules are imported."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import stat
import types

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
checks = 0
captured = {}


def check(value, note):
    global checks
    assert value, note
    checks += 1


def read(path):
    return json.loads(Path(path).read_bytes())


def regular(row):
    path = Path(row['path'])
    if str(path).startswith('/tmp/'):
        path = Path('/private' + str(path))
    check(path.is_absolute() and '..' not in path.parts, 'absolute canonical source')
    for p in (path, *path.parents):
        check(not p.is_symlink(), 'no source links')
    before = path.stat()
    check(stat.S_ISREG(before.st_mode) and before.st_size == row['bytes'], 'regular source size')
    ident = (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)
    cached = captured.get(str(path))
    if cached and cached['identity'] == ident:
        check(cached['sha256'] == row['sha256'], 'same path compatible descriptors')
        return path
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024), b''):
            h.update(b)
    after = path.stat()
    check(ident == (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns), 'stable read')
    check(h.hexdigest() == row['sha256'], 'source hash')
    captured[str(path)] = dict(path=str(path), sha256=row['sha256'], bytes=row['bytes'], identity=ident)
    return path


def indexed(row):
    path = regular(row)
    value = read(path)
    names = set()
    for r in value['files']:
        check(r['path'] not in names and not Path(r['path']).is_absolute() and '..' not in Path(r['path']).parts, 'finite index member')
        names.add(r['path'])
        regular(dict(path=str(path.parent/r['path']),sha256=r['sha256'],bytes=r['bytes']))
    actual = set()
    for p in path.parent.rglob('*'):
        check(not p.is_symlink(), 'index family no links')
        if p.is_file():
            actual.add(str(p.relative_to(path.parent)))
    check(actual == names|{'index.json'}, 'complete index membership')


def extracted(path, names, env):
    tree = ast.parse(path.read_bytes(), filename=str(path))
    chosen = [n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in names]
    check({n.name for n in chosen} == set(names), 'exact extracted pure definitions')
    exec(compile(ast.Module(body=chosen,type_ignores=[]),str(path)+':pure-extract','exec'),env)
    return env


def rejects(call, note):
    try:
        call()
    except (AssertionError, KeyError, TypeError):
        check(True,note)
    else:
        check(False,note)


def main():
    refs = read(HERE/'references.json')
    for row in refs['families']:
        indexed(row['index'])
    regular(refs['mandatoryHistoryErratum'])
    indexed(refs['nativeBaseSourceIndex'])
    regular(refs['normalProtection'])
    protection = read(refs['normalProtection']['path'])
    check(protection['originalReferenceEntries']==1387 and len(protection['originals'])==1387,'normal1387')
    check(len(protection['requiredNormalFreezeMembership'])==1391,'normal1391')
    regular(protection['freezeReceipt'])
    for r in protection['frozenCopyEntries']:
        regular(r)
    for r in protection['originals']:
        regular(r['original']);regular(r['frozen'])
    root=Path(protection['freezeReceipt']['path']).parent
    check({str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}==set(protection['requiredNormalFreezeMembership']),'normal full frozen membership')
    check(len(protection['vulnerableProjectOriginals'])==2,'normal cache/DB pair')
    for r in protection['vulnerableProjectOriginals']:
        regular(r['original']);regular(r['frozen'])

    policy = read(HERE/'policy.json')
    parent = read(HERE.parent/'native-integration-candidate-v2/policy.json')
    payload = read(HERE.parent/'ownership-secret-failure-candidate-v2/source-contract.json')
    rows=read(HERE/'native-origins.json')['files']
    before={r['path']:r['sha256']for r in parent['expectedNativeSourceManifest']}
    after={r['path']:r['sha256']for r in policy['expectedNativeSourceManifest']}
    check(len(rows)==len(before)==len(after)==355 and before.keys()==after.keys(),'same355paths')
    check(policy['expectedNativeSourceManifest']==payload['expectedNativeSourceManifest'],'exact26ed final355')
    check(sum(before[k]==after[k]for k in before)==352,'352 unchanged native sources')
    changed=sorted(k for k in before if before[k]!=after[k])
    check(changed==payload['changedNativeFiles'],'only three named crypto afterimages')
    check({r['path']:r['sha256']for r in rows}==after,'native origins all355')
    for r in rows:
        regular(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']))
    restored=copy.deepcopy(policy)
    restored['version']=parent['version']
    restored['expectedNativeSourceManifest']=parent['expectedNativeSourceManifest']
    del restored['cryptoSecretFailureSourcePolicy']
    for k in changed:
        restored['sourceLayer'][k]=parent['sourceLayer'][k]
    check(restored==parent,'exact finite policy reversal')
    check(policy['cryptoKeyOwnershipSourcePolicy']==parent['cryptoKeyOwnershipSourcePolicy'],'owner/prototype ancestry unchanged')
    for key in ['embedding','selectedCodecCompileContract','zlibSourcePolicy','streamConsumersSourcePolicy','privateTargetCpp','requiredHostInterfaces','profileVersion']:
        check(policy[key]==parent[key],'unchanged real source/API policy '+key)
    edits=0
    for d in read(HERE/'derivations.json')['exactTextDerivations']:
        regular(d['donor']);regular(d['after'])
        text=Path(d['donor']['path']).read_text()
        for e in d['edits']:
            check(text.count(e['before'])==e['count'],'exact forward match');text=text.replace(e['before'],e['after']);edits+=1
        check(text==Path(d['after']['path']).read_text(),'derived afterimage exact')
        for e in reversed(d['edits']):
            check(text.count(e['after'])==e['count'],'exact reverse match');text=text.replace(e['after'],e['before'])
        check(text==Path(d['donor']['path']).read_text(),'donor reversal exact')

    tools=read(HERE/'tool-origins.json')['files']
    check(len(tools)==len({r['path']for r in tools})==1051,'finite tools1051')
    for r in tools:
        regular(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']))
    recipe=(HERE/'proposed/tests/node-compat/build-engine.sh').read_text()
    check('NODE_COMPAT_BUILD_ROOT' in recipe and 'secretfailure-v1.' in recipe,'genuine work-root extension and fresh suffix')
    check('"$stress" == 0 && "$entropy_mode" == OFF' in recipe,'normal-OFF first refusal')
    check('"$repo_root" == "'+refs['configuredSourceRoot']+'"' in recipe,'exact configured source context')
    check('"$work_root" == "'+refs['workRoot']+'"' in recipe,'exact work context')
    check('consumers_layer_root="$repo_root/tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1"' in recipe,'genuine new helper location')
    # Parse only embedded Python from the actual derived shell source.
    lines=recipe.splitlines();embedded=0;i=0
    while i<len(lines):
        line=lines[i]
        import re
        match=re.search(r"<<'([A-Z]+)'",line)
        if match:
            delimiter=match.group(1);body=[];i+=1
            while lines[i]!=delimiter:
                body.append(lines[i]);i+=1
            if 'python3 ' in line:
                ast.parse('\n'.join(body),filename='build-engine.sh:'+delimiter);embedded+=1
        i+=1
    check(embedded>0,'actual embedded Python parsed')
    pyfiles=[]
    for path in sorted(HERE.rglob('*.py')):
        ast.parse(path.read_bytes(),filename=str(path));pyfiles.append(str(path.relative_to(HERE)))

    # Actual source_manifest body, entirely synthetic path/digest environment.
    class FakePath:
        def __init__(self, name):self.name=str(name)
        def __truediv__(self, part):return FakePath(self.name+'/'+part)
        def is_symlink(self):return False
        def is_file(self):return self.name.removeprefix('/synthetic/') in model
    model=after.copy()
    env=extracted(HERE/'layer-policy.py',['source_manifest','_macro','_release'],
        dict(Path=lambda value:value if isinstance(value,FakePath)else FakePath(value),
             POLICY=policy,digest=lambda p:model[p.name.removeprefix('/synthetic/')],copy=copy))
    check(env['source_manifest'](FakePath('/synthetic'))==policy['expectedNativeSourceManifest'],'actual new manifest function accepts synthetic final355')
    model=before.copy()
    rejects(lambda:env['source_manifest'](FakePath('/synthetic')),'old355 payload rejected by actual function')
    for k in changed:
        model=after.copy();model[k]=before[k]
        rejects(lambda:env['source_manifest'](FakePath('/synthetic')),'each missing corrected hash rejected')
    model=after.copy();del model[changed[0]]
    rejects(lambda:env['source_manifest'](FakePath('/synthetic')),'missing source refused')
    for enabled in [False,True]:
        tokens=['-DNODE_COMPAT_GC_STRESS=1']if enabled else[]
        env['_macro'](tokens,'NODE_COMPAT_GC_STRESS',enabled);check(True,'exact inherited macro model')
        rejects(lambda:env['_macro'](tokens+['-UNODE_COMPAT_GC_STRESS'],'NODE_COMPAT_GC_STRESS',enabled),'macro override rejected')
    env['_release'](['-O3','-DNDEBUG']);check(True,'ordinary release model')
    for tokens in [['-O0','-DNDEBUG'],['-O3','-DNDEBUG','-DNODE_COMPAT_OOM_TESTING'],['-O3','-DDEBUG']]:
        rejects(lambda:env['_release'](tokens),'nonordinary release refused')

    stage=(HERE/'stage.py').read_text()
    constants=dict(DEST=Path(refs['configuredSourceRoot']),WORK=Path(refs['workRoot']),FREEZE=Path(refs['freezeRoot']))
    env=extracted(HERE/'stage.py',['authority_model'],constants)
    template=read(HERE/'root-stage-authority.template.json')
    rejects(lambda:env['authority_model'](template,'f'*64,refs['sourcePeer']),'unissued template refused')
    synthetic=copy.deepcopy(template)
    synthetic.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_SECRET_SOURCE_STAGE_V1',sourceIndexSha256='f'*64,
        payloadSourceReview=refs['sourcePeer'],independentSourceReview={'syntheticOnly':True},sourceStageAllowed=True)
    check(env['authority_model'](synthetic,'f'*64,refs['sourcePeer']),'synthetic future stage model only')
    for key in ['nativeBuildAllowed','freezeAllowed','engineExecutionAllowed','keyOperationsAllowed','guestAllowed','gcAllowed','operationalAdmission','runtimeAcceptanceClaim','pinsAdopted']:
        wrong=copy.deepcopy(synthetic);wrong[key]=True
        rejects(lambda:env['authority_model'](wrong,'f'*64,refs['sourcePeer']),'separate phase cannot piggyback '+key)
    for key in ['sourceIndexSha256','destination','workRoot','freezeRoot','payloadSourceReview','independentSourceReview']:
        wrong=copy.deepcopy(synthetic);wrong[key]=None
        rejects(lambda:env['authority_model'](wrong,'f'*64,refs['sourcePeer']),'missing exact stage binding '+key)
    check(stage.index('refs, rows = inputs(expected)')<stage.index('authorize(descriptor, expected, refs)  # Before')<stage.index("['git','clone'"),'actual complete input barrier before action')
    check("after_refs, after_rows = inputs(expected)" in stage and "failureInputRecheckPassed" in stage,'final and failure input rechecks present')
    check('normal_protection(refs)' in stage and 'requiredNormalFreezeMembership' in stage,'normal protection authentic source seam')
    check('endswith(' not in stage and 'importlib' not in stage,'no suffix/custom helper import seam')
    check('HERE =' not in (HERE/'layer-policy.py').read_text().split('def decorate')[1],'no helper global root rebinding')
    for key,value in read(HERE/'future-authority.json').items():
        if key not in ['schemaVersion','state']:
            check(value is None or value is False,'unissued activation '+key)
    for key in ['configuredSourceRoot','workRoot','freezeRoot','stageJournal']:
        check(not Path(read(HERE/'phase-plan.json')[key]).exists(),'no action destination '+key)
    # Finite stage-plan DATA: own-family rows/index are added by stage only after seal.
    plan={}
    for r in rows+tools:
        if r['path'] in plan:
            check((plan[r['path']]['sha256'],plan[r['path']]['bytes'])==(r['sha256'],r['bytes']),'stage duplicate compatible')
        plan[r['path']]={k:r[k]for k in ['path','original','sha256','bytes']}
    put('stage-input-plan.json',dict(schemaVersion=1,state='UNEXECUTED_STAGE_BASE_INPUTS_EXCLUDING_FUTURE_OWN_SEAL',
        destination=refs['configuredSourceRoot'],nativeSourceFiles=355,toolRows=len(tools),
        ownSealRowsAddedOnlyAfterSeal=True,sourceStageExecuted=False,files=[plan[k]for k in sorted(plan)]))
    # Fresh reads of the small active source donor roles after the finite read pass.
    for r in policy['cryptoSecretFailureSourcePolicy']['changes']:
        regular(r['afterimage'])
    inputs=[{k:r[k]for k in ['path','sha256','bytes']}for _,r in sorted(captured.items())]
    put('checked-inputs.json',dict(schemaVersion=1,sourceReadHashOnly=True,files=inputs))
    result=dict(schemaVersion=1,state='SECRET_OWNER355_INTEGRATION_SOURCE_CHECKS_COMPLETE_V1',
        sourceOnly=True,checks=checks,uniqueReadHashInputs=len(inputs),nativeSourceFiles=355,
        unchangedNativeSources=352,correctedAfterimages=3,toolRows=len(tools),baseStageRows=len(plan),
        exactTextDerivations=3,exactTextEdits=edits,policyReversal=True,pythonAstFiles=pyfiles,
        embeddedPythonAstBlocks=embedded,pureExtractedFunctions=['source_manifest','_macro','_release','authority_model'],
        sourcePeerActivation=None,rootActivation=None,helperImported=False,ownerActionsInvoked=False,
        compilerInvoked=False,nodeInvoked=False,stageExecuted=False,nativeBuildExecuted=False,
        engineExecuted=False,guestOrCryptoOrGcExecuted=False,operationalAdmission=False,
        limits=['Extracted synthetic models do not prove actions or fault behavior',
                'No JS/shell runtime parsing or imported admission function execution',
                'Owned build controller and new freeze/pin/bootstrap implementations remain unimplemented'])
    put('source-check-results.json',result)
    print(json.dumps(result))


def put(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2)+'\n')


if __name__=='__main__':
    main()
