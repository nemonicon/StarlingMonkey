"""Source/read/hash/AST/injected pure models only; no caller/helper/monitor import."""
import ast,copy,hashlib,json,os,stat
from pathlib import Path
HERE=Path(__file__).resolve().parent
observed={};checks=0;cases=[]


def need(value,message='check'):
    global checks
    checks+=1
    assert value,message


def file(path,sha=None,size=None,force=False):
    p=Path(path);need(p.is_absolute()and p.is_file()and not p.is_symlink(),str(p));a=p.stat();identity=(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns);real=str(p.resolve())
    if str(p)not in observed or force:
        h=hashlib.sha256()
        with p.open('rb')as f:
            for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
        z=p.stat();need(identity==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)and real==str(p.resolve()))
        row=dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
        if str(p)in observed:need(observed[str(p)]==(row,identity,real))
        observed[str(p)]=(row,identity,real)
    row,previous,resolved=observed[str(p)];need(identity==previous and real==resolved)
    if sha is not None:need(row['sha256']==sha,str(p))
    if size is not None:need(row['bytes']==size,str(p))
    return row


def verify(r,force=False):return file(r['path'],r['sha256'],r['bytes'],force)
def read(r):verify(r);return json.loads(Path(r['path']).read_bytes())
def load(p):file(p);return json.loads(Path(p).read_bytes())


def family(index):
    value=read(index);root=Path(index['path']).parent;names={'index.json'};rows=[index]
    for r in value['files']:
        n=r['path'];need(n not in names and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')));names.add(n);row=dict(r,path=str(root/n));verify(row);rows.append(row)
    actual=set()
    for p in root.rglob('*'):
        need(not p.is_symlink())
        if p.is_file():actual.add(str(p.relative_to(root)))
    need(actual==names);return rows


def pure(text,name,env):
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name==name)
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<extracted pure '+name+'>','exec'),env);return env[name]


def case(name,callback,reject=False):
    failed=False
    try:callback()
    except(AssertionError,KeyError,TypeError,ValueError):failed=True
    need(failed==reject,name);cases.append(dict(name=name,passed=True,expected='REJECT'if reject else'PASS'))


def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    need(not(HERE/'index.json').exists())
    refs=load(HERE/'references.json')
    for f in refs['families']:family(f['index'])
    for key in['verifierContract','verifierEntry','verifierSourceInputs','actualArtifactContract','artifactInputLedger','normalProtection','monitorEntry','engine','metadata','freezeReceipt']:verify(refs[key])
    peer=read(refs['verifierSourceReview']['result']);need(peer['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_FROZEN_VERIFIER_SOURCE_REVIEW_PASSED_V1'and peer['verifierSourceIndexSha256']==refs['verifierSourceIndex']['sha256']and peer['ownerActionsInvoked']is False and peer['completeVerifierInvoked']is False)
    source_inputs=read(refs['verifierSourceInputs'])
    for r in source_inputs['files']:verify(r)
    ledger=read(refs['artifactInputLedger'])
    for r in ledger['files']:verify(r)
    normal=read(refs['normalProtection']);need(normal['originalReferenceEntries']==1387 and len(normal['requiredNormalFreezeMembership'])==1391)
    verify(normal['freezeReceipt'])
    for r in normal['frozenCopyEntries']:verify({k:r[k]for k in['path','sha256','bytes']})
    for r in normal['originals']:verify(r['original']);verify(r['frozen'])
    normalroot=Path(normal['freezeReceipt']['path']).parent;need({str(p.relative_to(normalroot))for p in normalroot.rglob('*')if p.is_file()}==set(normal['requiredNormalFreezeMembership']))
    receipt=read(refs['freezeReceipt']);need(len(receipt['copies'])==1902 and sum(r['original']is not None for r in receipt['copies'])==1899)
    for r in receipt['copies']:
        verify({k:r[k]for k in['path','sha256','bytes']});need(stat.S_IMODE(Path(r['path']).stat().st_mode)==0o600)
        if r['original']is not None:verify(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']))
    frozen=Path(refs['frozenRoot']);need({str(p.relative_to(frozen))for p in frozen.rglob('*')if p.is_file()}=={str(Path(r['path']).relative_to(frozen))for r in receipt['copies']}|{'normal-off-freeze-receipt.json'})
    c=read(refs['verifierContract']);text=(HERE/'controller.py').read_text();tree=ast.parse(text);definitions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    env=dict(Path=Path,OWN=HERE,VERIFIER=Path(refs['verifierEntry']['path']).parent,OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-frozen-verifier-v1'),EXTERNAL=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-frozen-verifier-v1-external-root'),TIMEOUT=600,VERIFIER_SHA=refs['verifierSourceIndex']['sha256'])
    root_model=pure(text,'validate_root',env);peer_model=pure(text,'validate_peer',env);frame_model=pure(text,'expected_frame',env);terminal_model=pure(text,'clean_terminal',env)
    template=load(HERE/'future-root-authority.template.json');index=dict(path=str(HERE/'index.json'),sha256='a'*64,bytes=1)
    case('unissued Root template refuses',lambda:root_model(template,index,refs),True)
    root=copy.deepcopy(template);root.update(state='ROOT_REVIEWED_SECRET_OWNER355_FROZEN_VERIFIER_READ_ONLY_V1',verifierReadOnlyAllowed=True,controllerIndex=index,controllerEntry=dict(path=str(HERE/'controller.py'),sha256='b'*64,bytes=1))
    case('synthetic exact read-only Root shape',lambda:root_model(root,index,refs))
    for key,value in[('phase','export'),('expectedVerifierCalls',2),('externalParentDeadlineSeconds',601),('engineExecutionAllowed',True),('ownerHelperAllowed',True),('ninjaAllowed',True),('nodeAllowed',True),('exportAllowed',True),('actualVerifierResult',{}),('outputRoot','/wrong')]:
        case('Root rejects '+key,lambda k=key,v=value:root_model({**root,k:v},index,refs),True)
    p=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_VERIFIER_CONTROLLER_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256=index['sha256'],verifierSourceIndexSha256=refs['verifierSourceIndex']['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,verifierActionsInvoked=False)
    case('synthetic source peer shape',lambda:peer_model(p,index))
    for key,value in[('state','OLD_GC_SOURCE'),('verifierSourceIndexSha256','0'*64),('verifierActionsInvoked',True)]:case('peer rejects '+key,lambda k=key,v=value:peer_model({**p,k:v},index),True)
    # Bounded synthetic metadata/manifests: not a retained/actual verifier frame.
    metadata=dict(sourceManifest=[dict(path='synthetic-'+str(i),sha256='c'*64)for i in range(355)],componentizeSourceManifest=[dict(path=str(i),sha256='d'*64)for i in range(3)],selectedModuleManifests=[dict(path='synthetic-manifest-'+str(i),sha256='e'*64)for i in range(11)],opaqueUnchangedValue=dict(originalWorkRoot=c['workRoot'],noProjection=True))
    manifests=[dict(profileVersion='synthetic',modules={})for _ in range(11)];before=copy.deepcopy(metadata)
    model=frame_model(c,metadata,manifests);need(model['metadata']==metadata==before and model['verifierOriginalToolingRoot']==c['originalToolingRoot']and model['configuredSourceRoot']!=model['sourceRoot'])
    need(model['originalReferencesReopened']is False and model['engineExecuted']is False and model['grantsActionAuthority']is False)
    for key,value in[('metadata',{}),('sourceRoot',c['configuredSourceRoot']),('runtimeAcceptanceClaim',True),('selectedManifests',[])]:case('whole frame mutation '+key,lambda k=key,v=value:need({**model,k:v}==frame_model(c,metadata,manifests)),True)
    case('whole frame extra field',lambda:need({**model,'projected':True}==frame_model(c,metadata,manifests)),True)
    terminal=dict(rawExitCode=0,authority=dict(path='/synthetic/authority.json',sha256='f'*64,bytes=1),parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,timeout=False,forcedCleanup=False,errors=[],signals=[],interruptedSignals=[],remainingObservedPids=[],finalGroups=[dict(alive=False)],stderr=dict(bytes=0))
    case('clean synthetic raw terminal',lambda:terminal_model(terminal,terminal['authority']))
    for key,value in[('rawExitCode',1),('rawExitCode',False),('forcedCleanup',True),('signals',[9]),('remainingObservedPids',[123]),('stderr',dict(bytes=1))]:case('terminal rejects '+key+' '+str(value),lambda k=key,v=value:terminal_model({**terminal,k:v},terminal['authority']),True)
    helper_text=Path(refs['verifierEntry']['path']).read_text();helper_tree=ast.parse(helper_text);verify_node=next(n for n in helper_tree.body if isinstance(n,ast.FunctionDef)and n.name=='verify_frozen')
    need([a.arg for a in verify_node.args.args]==['c'])
    returned=next(n for n in verify_node.body if isinstance(n,ast.Return)).value;modeled=next(n for n in definitions['expected_frame'].body if isinstance(n,ast.Return)).value
    need({k.arg for k in returned.keywords}=={k.arg for k in modeled.keywords},'whole original helper return keys exactly modeled')
    worker=definitions['worker'];helper_calls=[n for n in ast.walk(worker)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='helper'and n.func.attr=='verify_frozen'];need(len(helper_calls)==1)
    need(text.index("write(OUT/'whole-frame.json',value)")<text.index('print(json.dumps(value),flush=True)'))
    need("assert helper.HERE==VERIFIER"in text)
    need(not any(isinstance(n,ast.Assign)and any(isinstance(t,ast.Attribute)and isinstance(t.value,ast.Name)and t.value.id in['helper','monitor','module']for t in n.targets)for n in ast.walk(tree)))
    need("frame=authorize("in text and 'finally:frame[\'capture\'].recheck()'in text)
    need(text.index("write(OUT/'raw-terminal-observed.json'")<text.index("clean_terminal(terminal,frame['rootRow'])"))
    need("value==retained"in text and "value==expected_frame(c,metadata,manifests)"in text)
    mon=ast.parse(Path(refs['monitorEntry']['path']).read_text());fn=next(n for n in mon.body if isinstance(n,ast.FunctionDef)and n.name=='monitor');need([a.arg for a in fn.args.args]==['argv','cwd','environment','output','timeout_seconds','authority'])
    parent_calls=[n for n in ast.walk(definitions['parent'])if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='monitor'];need(len(parent_calls)==1 and len(parent_calls[0].args)==6 and not parent_calls[0].keywords)
    for field in['controllerIndependentReview','rootAuthority','actualVerifierResult','actualExport','reviewedPins','bootstrapAuthority','runtimeAuthority']:need(refs[field]is None)
    need(not env['OUT'].exists()and not env['EXTERNAL'].exists())
    asts=0
    for p in HERE.rglob('*'):
        if p.is_file()and p.name not in['source-inputs.json','check-results.json','pure-results.json']:
            file(p)
            if p.suffix=='.py':ast.parse(p.read_text());asts+=1
            if p.suffix=='.json':json.loads(p.read_bytes())
    snapshots=[r[0]for r in observed.values()]
    for r in snapshots:verify(r,True)
    ledger_paths={r['path']for r in ledger['files']}
    write('source-inputs.json',dict(schemaVersion=1,files=[r for r in snapshots if r['path']not in ledger_paths],artifactInputLedger=refs['artifactInputLedger'],artifactInputLedgerRows=len(ledger['files']),allObservedInputsRehashedFinally=True))
    write('pure-results.json',dict(schemaVersion=1,scope='Extracted IO-free Root/peer/frame/terminal predicates with synthetic unissued authority/metadata values; no complete helper/caller run',cases=cases,actualVerifierFrameCreated=False))
    write('check-results.json',dict(schemaVersion=1,state='SECRET_OWNER355_READ_ONLY_VERIFIER_CONTROLLER_SOURCE_CHECKS_PASSED_V1',sourceOnly=True,sourceChecksPassed=True,checks=checks,uniqueInputPaths=len(snapshots),pureCases=len(cases),pythonAstFiles=asts,helperReturnKeysExactlyModeled=True,helperCallsPerFutureWorker=1,originalHelperContextPreserved=True,monitorActualPositionalApi=6,externalParentDeadlineSeconds=600,rawAndWholeFrameRetainedBeforeModelAssertions=True,preservationOriginalReadsSeparateFromFrozenOnlyHelper=True,normalFrozen1391Original1387AndNewFrozen1903Protected=True,controllerOrHelperOrMonitorImported=False,processesStarted=False,fullVerifierInvoked=False,nodeOrNinjaInvoked=False,copyExportBootstrapOrEngineInvoked=False,operationalAdmission=False,actualRootAuthority=None,actualVerifierResult=None))
    print(json.dumps(dict(sourceChecksPassed=True,checks=checks,uniqueInputPaths=len(snapshots),pureCases=len(cases),pythonAstFiles=asts,actualVerifierResult=None)))


if __name__=='__main__':main()
