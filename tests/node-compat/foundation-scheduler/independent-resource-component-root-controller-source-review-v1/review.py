"""Independent bounded read/hash/AST/extracted-pure review; no controller import."""
from pathlib import Path
import ast,copy,hashlib,json,os,stat

REPO=Path('/Users/dan/dev/StarlingMonkey')
S=REPO/'tests/node-compat/foundation-scheduler'
TARGET=S/'resource-component-root-controller-candidate-v1'
SOURCE=S/'resource-component-candidate-v1'
OWN=Path(__file__).resolve().parent
SHA='453f220f83887dcd53b8dd8a9db330840dd094a6e096668a095254384cda167c'
observed={};checks=0;cases=[]


def need(condition,reason='check'):
    global checks
    checks+=1
    assert condition,reason


def physical(p):
    p=str(p);return Path('/private'+p)if p.startswith('/tmp/')else Path(p)


def record(path,sha=None,size=None):
    p=physical(path);need(p.is_absolute()and '..'not in p.parts)
    for q in(p,*p.parents):need(not q.is_symlink(),str(q))
    a=p.stat();need(stat.S_ISREG(a.st_mode));h=hashlib.sha256()
    with p.open('rb')as stream:
        for b in iter(lambda:stream.read(4*1024*1024),b''):h.update(b)
    z=p.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns))
    r=dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
    if sha is not None:need(r['sha256']==sha,str(p))
    if size is not None:need(r['bytes']==size,str(p))
    if str(p)in observed:need(observed[str(p)]==r)
    observed[str(p)]=r;return r


def verify(r):record(r['path'],r['sha256'],r['bytes']);return physical(r['path'])
def load(p):record(p);return json.loads(Path(p).read_bytes())
def read(r):return json.loads(verify(r).read_bytes())


def family(ix):
    v=read(ix);root=Path(ix['path']).parent;names=set();rows=[ix]
    for r in v['files']:
        name=r['path'];need(name not in names and name and not name.startswith('/')and all(x not in('','.','..')for x in name.split('/')));names.add(name)
        d=dict(r,path=str(root/name));verify(d);rows.append(d)
    actual=set()
    for p in root.rglob('*'):
        need(not p.is_symlink())
        if p.is_file():actual.add(str(p.relative_to(root)))
    need(actual==names|{'index.json'},str(root));return rows


def model_case(name,callback,reject=False):
    failed=False
    try:callback()
    except (AssertionError,TypeError,KeyError):failed=True
    need(failed==reject,name);cases.append(dict(name=name,passed=True,expected='REJECT'if reject else'PASS'))


def pure_models(tree):
    definitions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    env=dict(Path=Path,OUTPUT_BASE=Path('/private/tmp/starling-node-compat/scheduler-resource-component-v1'),FIXTURES=('resource','pure','fatal','init-fatal'))
    exec(compile(ast.Module(body=[definitions['action_model'],definitions['owned_clean']],type_ignores=[]),'<extracted IO-free controller predicates>','exec'),env)
    for fixture in env['FIXTURES']:
        expected=dict(fixture=fixture,outputRoot=str(env['OUTPUT_BASE'])+'-'+fixture,externalRoot=str(env['OUTPUT_BASE'])+'-'+fixture+'-external-root',timeoutSeconds=2400)
        model_case('exact '+fixture,lambda f=fixture,e=expected:need(env['action_model'](f)==e))
    for value in ['',None,0,'../resource','resource/old','then','unknown']:
        model_case('invalid fixture '+repr(value),lambda v=value:env['action_model'](v),True)
    terminal=dict(allObservedOwnedGroupsGone=True,timeout=False,forcedCleanup=False,remainingObservedPids=[],errors=[],signals=[],interruptedSignals=[])
    model_case('clean genuine terminal fields',lambda:need(env['owned_clean'](terminal)))
    for key,value in terminal.items():
        changed={**terminal,key:[1]if isinstance(value,list)else not value}
        model_case('dirty '+key,lambda v=changed:need(not env['owned_clean'](v)))
    # Extract only the IO-free publication projection statements. checked() is
    # injected to collect descriptors; no main/module or filesystem action runs.
    main=definitions['main'];start=next(i for i,n in enumerate(main.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='publications'for t in n.targets))
    projection=ast.Module(body=main.body[start:start+2],type_ignores=[])
    code=compile(projection,'<extracted bounded relative publication model>','exec')
    action=env['action_model']('resource');r=dict(path='index.json',sha256='a'*64,bytes=12);c=dict(path='completion.json',sha256='b'*64,bytes=13)
    tests=[('valid relative rows',dict(root=action['outputRoot'],index=r,completion=c),2),('wrong root',dict(root='/wrong',index=r,completion=c),0),('parent escape refused',dict(root=action['outputRoot'],index={**r,'path':'../index.json'},completion=c),1),('absolute original row refused',dict(root=action['outputRoot'],index={**r,'path':action['outputRoot']+'/index.json'},completion=c),1),('missing completion',dict(root=action['outputRoot'],index=r),1),('null final',None,0),('nonobject row',dict(root=action['outputRoot'],index=1,completion=c),1)]
    for name,final,count in tests:
        original=copy.deepcopy(final);captured=[];scope=dict(final=final,model=action,Path=Path,checked=lambda value:captured.append(value))
        exec(code,scope);need(len(scope['publications'])==count and final==original,name)
        for key,value in scope['publications'].items():need(value['path']==action['outputRoot']+'/'+key+'.json'and value in captured)
        cases.append(dict(name='actual projection '+name,passed=True,expectedCount=count,originalRelativeRowsUnchanged=True))
    return dict(original19Replayed=True,publicationProjectionCases=7,pureCaseCount=len(cases))


def main():
    need(not(OWN/'index.json').exists())
    ix=record(TARGET/'index.json',SHA,1028);own=family(ix);need(len(own)==7)
    refs=load(TARGET/'references.json');need(len(refs['families'])==3)
    for f in refs['families']:family(f)
    need(refs['outerTimeoutSeconds']==2400 and refs['workerTimeoutSeconds']==600)
    source_index=refs['families'][0];need(source_index['sha256']=='74413aa9d1520139dc2ac4d8e43f0d99bab06477b8d8eb6e9d2db6bb58580055')
    peer_index=refs['families'][1];need(peer_index['sha256']=='dc452069b619be3a50dbf3bf71ba9487fe39194637da1dcb60806516a21fe02c')
    source_peer=load(Path(peer_index['path']).parent/'results.json')
    need(source_peer['schemaVersion']==1 and source_peer['state']=='INDEPENDENT_SCHEDULER_RESOURCE342_COMPONENT_SOURCE_REVIEW_PASSED_V1'and source_peer['sourceIndexSha256']==source_index['sha256']and source_peer['sourceOnly']is True and source_peer['sourceReviewPassed']is True and source_peer['ownerActionsInvoked']is False)
    source_refs=load(SOURCE/'references.json');manifest=load(SOURCE/'input-freeze.json');need(len(manifest['files'])==5399)
    for r in manifest['files']:verify(r)
    for f in source_refs['families']:family(f['index'])
    for key in['node','bootstrapConfig','bootstrapRootObservation','reviewedPins','rootPinReview','bootstrapEntry','engine','metadata','freezeReceipt','actualBootstrapWholeFrame','packagingMap']:verify(source_refs[key])
    map=read(source_refs['packagingMap']);need(len(map['files'])==4934 and len(map['links'])==22)
    package_root=Path(map['publicationRoot']);p=package_root.stat();need(p.st_dev==map['rootIdentity']['device']and p.st_ino==map['rootIdentity']['inode']and stat.S_IMODE(p.st_mode)==0o700)
    for r in map['files']:
        p=package_root/r['path'];record(p,r['sha256'],r['bytes']);need(stat.S_IMODE(p.stat().st_mode)==r['mode']and p.stat().st_nlink==1)
    for r in map['links']:
        p=package_root/r['destination'];need(p.is_symlink()and os.readlink(p)==r['newLinkText']and p.resolve()==package_root/r['mappedTarget'])
    text=(TARGET/'controller.py').read_text();tree=ast.parse(text);ast.parse((TARGET/'prepare.py').read_text())
    functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)};need(set(functions)=={'row','checked','load','family','write','action_model','owned_clean','inventory','main'})
    details=pure_models(tree);stored=load(TARGET/'pure-source-results.json');need(stored['pureCases']==19 and stored['sourceOnly']is True and stored['ownerActionsInvoked']is False)
    m=functions['main'];calls=[n for n in ast.walk(m)if isinstance(n,ast.Call)]
    custom=[n for n in calls if isinstance(n.func,ast.Attribute)and n.func.attr=='exec_module'];need(len(custom)==1 and isinstance(custom[0].args[0],ast.Name)and custom[0].args[0].id=='monitor')
    monitor_line=custom[0].lineno
    for token in["own = family(HERE", "source = family(SOURCE", "peer = dict(index=family(PEER", "review_index = family(", "review_value = load(", "checked(refs['node'])", "monitor_index = family(MONITOR"]:
        need(text.index(token)<text.index('spec.loader.exec_module(monitor)'),token)
    monitor_calls=[n for n in calls if isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='monitor'and n.func.attr=='monitor'];need(len(monitor_calls)==1)
    need(len(monitor_calls[0].args)==6 and not monitor_calls[0].keywords)
    monitor_path=Path(refs['families'][2]['path']).parent/'monitor.py';mon=ast.parse(monitor_path.read_text());definition=next(n for n in mon.body if isinstance(n,ast.FunctionDef)and n.name=='monitor')
    need([n.arg for n in definition.args.args]==['argv','cwd','environment','output','timeout_seconds','authority'])
    need(mon.body[-1].test.left.id=='__name__')
    need("MONITOR = S.parent / 'foundation-crypto/ownership-gc-build-controller-candidate-v1'"in text)
    need("argv = [refs['node']['path'], str(SOURCE / 'entry.mjs'), SOURCE_SHA, 'construct', json.dumps(config_row, separators=(',', ':'))]"in text)
    need("environment.update(PYTHONDONTWRITEBYTECODE='1', NODE_COMPAT_TOOLCHAIN=refs['toolchainRoot'], NODE_COMPAT_COMPONENTIZE_MODULE=refs['packagerRoot'] + '/src/componentize.js')"in text)
    need(not any(isinstance(n,ast.Assign)and any(isinstance(t,ast.Subscript)and isinstance(t.slice,ast.Constant)and t.slice.value=='HOME'for t in n.targets)for n in ast.walk(tree)))
    entry=(SOURCE/'entry.mjs').read_text();build=(SOURCE/'build.mjs').read_text()
    need("need(process.argv.length===5"in entry and "mode==='construct'||mode==='worker'"in entry)
    need("const {buildComponent}=await import('./build.mjs')"in entry)
    need(entry.index('for(const r of manifest.files)await streamHash(r)')<entry.index('const {resourceBootstrapPreflight}=await import('))
    need('root.workerTimeoutMs===600000'in entry and 'ordinaryExportsAllowed'in entry and 'initializationOnly===true'in entry)
    template=load(SOURCE/'future-root-authority.template.json');need(template['workerTimeoutMs']==600000 and template['initializationOnly']is True and template['componentConstructionAllowed']is False)
    for key in['nativeBuildAllowed','nativeFreezeAllowed','ordinaryExportsAllowed','timerRuntimeAllowed','guestLoadingAllowed','hostRequestsAllowed','gcAllowed','keyOrCryptoAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim','metadataProjectionAllowed']:need(template[key]is False)
    need('return{root:output.root,index:indexRow,completion:completed}'in build)
    need("checkOwnedTerminal(outcome); // raw streams and terminal are durable before this assertion"in build)
    need("originalLastStdoutRecord=final, absolutePublications=publications"in text)
    need(text.index("checked(terminal[key])")<text.index("capture = inventory(")<text.index("report = write(paths['results'], summary)"))
    need("if final is not None and final.get('root') == model['outputRoot']:"in text)
    need("value.get('path') == key + '.json'"in text)
    need("return 0 if success else 1"in text)
    snapshots=list(observed.values())
    for r in snapshots:verify(r)
    write('input-hashes.json',dict(schemaVersion=1,files=snapshots,finalRehashPassed=True))
    write('pure-review-results.json',dict(schemaVersion=1,scope='Only two IO-free functions and the publication projection AST; full controller/monitor never imported or called',details=details,cases=cases))
    qualifications=[
        'Controller authenticates its own/source/peer/monitor families and pinned primitive descriptors before its sole custom monitor import. Complete5399 source/packaging/native-bootstrap checks then belong to the unchanged744 entry before that entry imports custom provider code.',
        'owned_clean checks the genuine monitor allObservedOwnedGroupsGone field; the actual0af implementation assigns it and parentOwnedGroupGone from the same complete value.',
        'Raw monitor streams/terminal are durable before post-reader assertions. An assertion/IO failure in the controller post-reader may escape without a Root summary; retained raw files remain the evidence, never a PASS.',
        'The controller reports unreviewed raw construction success/publication observations only. Full output membership, component/ABI/native claims require a separate actual-result review.',
        'No host lifecycle regression or actual process/Node/bootstrap/packager/component/guest action was performed by this reviewer.'
    ]
    write('source-audit.json',dict(schemaVersion=1,controller=ix,source=source_index,sourcePeer=peer_index,monitor=refs['families'][2],customImports=1,monitorPositionalArguments=6,outerDeadlineSeconds=2400,innerWorkerDeadlineSeconds=600,fixtures=['resource','pure','fatal','init-fatal'],sourceInputs5399=True,packagingFiles4934=True,physicalLinks22=True,sourceEntryOriginalContext=True,homeAndUserContextPreserved=True,relativeRowsPreservedWithSeparateAbsoluteDescriptors=True,qualifications=qualifications))
    write('results.json',dict(schemaVersion=1,state='INDEPENDENT_RESOURCE342_COMPONENT_ROOT_CONTROLLER_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256=SHA,controllerSourceIndex=ix,componentSourceIndexSha256=source_index['sha256'],componentSourceReviewIndexSha256=peer_index['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,controllerImported=False,monitorImportedOrInvoked=False,nodeInvoked=False,bootstrapInvoked=False,packagerInvoked=False,engineInvoked=False,guestInvoked=False,checks=checks,uniqueInputPaths=len(snapshots),controllerMembers=6,actualPureCases=len(cases),pythonAstFiles=2,sourceAudit=descriptor(OWN/'source-audit.json'),inputHashes=descriptor(OWN/'input-hashes.json'),pureReview=descriptor(OWN/'pure-review-results.json'),actualRootAuthority=None,actualConstruction=None,grantsAnyActionAuthority=False,operationalAdmission=False,runtimeAcceptanceClaim=False,qualifications=qualifications))
    print(json.dumps(dict(sourceReviewPassed=True,checks=checks,uniqueInputPaths=len(snapshots),pureCases=len(cases),ownerActionsInvoked=False)))


def descriptor(p):
    p=Path(p);raw=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))


def write(name,value):
    with(OWN/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())


if __name__=='__main__':main()
