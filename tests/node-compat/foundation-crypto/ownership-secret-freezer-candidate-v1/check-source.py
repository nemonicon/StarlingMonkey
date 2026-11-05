"""Finite read/hash/AST/extracted-pure Source review. Never import an owner module."""
import ast
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import stat
import types

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
observed={}
checks=0
models=[]


def require(value,message='check'):
    global checks
    checks+=1
    assert value,message


def record(path,expected=None,size=None):
    path=Path(path)
    if str(path).startswith('/tmp/'):path=Path('/private'+str(path))
    require(path.is_absolute()and '..'not in path.parts,str(path))
    for part in (path,*path.parents):require(not part.is_symlink(),str(part))
    before=path.stat();require(stat.S_ISREG(before.st_mode),str(path));h=hashlib.sha256()
    with path.open('rb')as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
    after=path.stat()
    require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),str(path))
    row=dict(path=str(path),sha256=h.hexdigest(),bytes=after.st_size)
    if expected is not None:require(row['sha256']==expected,str(path))
    if size is not None:require(row['bytes']==size,str(path))
    if str(path)in observed:require(observed[str(path)]==row,str(path))
    observed[str(path)]=row
    return row


def row(value):return record(value['path'],value['sha256'],value['bytes'])
def load(path):record(path);return json.loads(Path(path).read_bytes())
def read(value):row(value);return json.loads(Path(value['path']).read_bytes())
def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def family(index):
    value=read(index);base=Path(index['path']).parent;names=set()
    for entry in value['files']:
        name=entry['path'];require(name not in names and not name.startswith('/')and all(part not in ('','.','..')for part in name.split('/')))
        names.add(name);record(base/name,entry['sha256'],entry['bytes'])
    actual=set()
    for p in base.rglob('*'):
        require(not p.is_symlink(),str(p))
        if p.is_file():actual.add(str(p.relative_to(base)))
    require(actual==names|{'index.json'},str(base))


def function(text,name,namespace):
    tree=ast.parse(text);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name)
    # Only this named pure/injected function is compiled; no module top level runs.
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<extracted-pure-'+name+'>','exec'),namespace)
    return namespace[name]


def case(name,callback,reject=False):
    failed=False
    try:callback()
    except (AssertionError,KeyError,ValueError,TypeError):failed=True
    require(failed==reject,name)
    models.append(dict(name=name,expected='REJECT'if reject else'PASS',passed=True))


def mutate(value,path,replacement):
    value=copy.deepcopy(value);target=value
    for key in path[:-1]:target=target[key]
    target[path[-1]]=replacement
    return value


def models_for_guards(c,refs,metadata,policy,body_text,entry_text):
    common_text=(HERE/'artifact-tools/artifact_common.py').read_text()
    env=dict(LABELS=('normal-off',),RECIPE=c['recipe']['sha256'],SOURCE_POLICY=policy)
    classify=function(common_text,'classify',env)
    case('actual393125byte normal-off metadata accepted',lambda:require(classify(metadata,'normal-off')==(False,'off')))
    for path,value in [(['buildRecipeSha256'],'0'*64),(['cryptoSecretFailureSourcePolicy'],{}),(['sourceManifest'],[]),(['gcStress'],True),(['entropyPolicy'],'runtime-only'),(['syntheticMetadataOnly'],True),(['diagnosticOnly'],True),(['cryptoSecretFailureBuildEvidence','runtimeValidation'],{}),(['oomTesting'],True)]:
        case('classifier rejects '+'.'.join(path),lambda p=path,v=value:classify(mutate(metadata,p,v),'normal-off'),True)
    case('GC variant rejected',lambda:classify(metadata,'gc-off'),True)
    env=dict(Path=Path,REPO=REPO,COMMON_RELATIVE=c['activeCommonRelativePath'])
    select=function(entry_text,'select_common',env);actual=record(HERE/'artifact-tools/artifact_common.py')
    donor_rows=[]
    for f in refs['families']:
        idx=read(f['index']);base=Path(f['index']['path']).parent
        donor_rows.extend(dict(path=str(base/r['path']),sha256=r['sha256'],bytes=r['bytes'])for r in idx['files']if r['path'].endswith('artifact_common.py'))
    case('exact helper beats unrelated suffix rows',lambda:require(select([*donor_rows,actual],actual)==actual))
    case('missing exact helper rejected',lambda:select(donor_rows,actual),True)
    case('duplicate exact helper rejected',lambda:select([actual,actual],actual),True)
    for key,value in [('sha256','0'*64),('bytes',actual['bytes']+1),('path',actual['path']+'.other')]:
        case('helper wrong '+key+' rejected',lambda k=key,v=value:select([actual],{**actual,k:v}),True)
    build=read(c['actualBuildReview']['result'])
    validate_build=function(entry_text,'validate_build',dict(NATIVE_SHA=c['nativeSourceIndex']['sha256'],SOURCE=c['configuredSourceRoot'],WORK=c['workRoot']))
    case('actual independent BUILD result accepted',lambda:validate_build(build,c))
    for key,value in [('engineSha256','0'*64),('sourceIndexSha256','0'*64),('controllerSourceIndexSha256','0'*64),('variant','gc-off'),('changedNativeFiles',2),('actualFreezeVerified',True),('engineExecuted',True)]:
        case('BUILD wrong '+key+' rejected',lambda k=key,v=value:validate_build({**build,k:v},c),True)
    contract=read(c['actualBuildContract']);require(all(build[k]==v for k,v in contract.items()),'actual flat BUILD contract')
    validate_root=function(entry_text,'validate_root',dict(OWN=HERE,SOURCE=c['configuredSourceRoot'],WORK=c['workRoot'],FROZEN=c['freezeRoot'],OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze-external-root'),NATIVE_SHA=c['nativeSourceIndex']['sha256'],TIMEOUT=2400,REPO=REPO,COMMON_RELATIVE=c['activeCommonRelativePath']))
    # In-memory model only; this is NOT an issued Root action document.
    root=load(HERE/'root-authority.template.json');index=dict(path=str(HERE/'index.json'),sha256='a'*64,bytes=1)
    root.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_SECRET_NORMAL_OFF_FREEZE_V1',freezeAllowed=True,freezerIndex=index,entry=dict(path=str(HERE/'freeze.py'),sha256='b'*64,bytes=1),commonHelper=actual)
    case('synthetic exact Root-field model accepted',lambda:validate_root(root,index,c,refs))
    for key,value in [('freezeAllowed',False),('workRoot','/wrong'),('nativeSourceFiles',354),('gcAllowed',True),('runtimeAuthority',{}),('metadataProjectionAllowed',True)]:
        case('Root wrong '+key+' rejected',lambda k=key,v=value:validate_root({**root,k:v},index,c,refs),True)
    peer=function(entry_text,'validate_source_peer',dict(NATIVE_SHA=c['nativeSourceIndex']['sha256']))
    value=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_FREEZER_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=index['sha256'],nativeSourceIndexSha256=c['nativeSourceIndex']['sha256'],actualBuildReviewIndexSha256=c['actualBuildReview']['index']['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,nativeFreezeActionsInvoked=False)
    case('synthetic prospective peer shape accepted',lambda:peer(value,index,c))
    for key,replacement in [('state','OLD'),('sourceIndexSha256','0'*64),('actualBuildReviewIndexSha256','0'*64),('nativeFreezeActionsInvoked',True)]:
        case('prospective peer wrong '+key+' rejected',lambda k=key,v=replacement:peer({**value,k:v},index,c),True)
    frame=dict(contract=c,nativeSourceIndex=c['nativeSourceIndex'],sourceIndex=index,active=root['entry'],entryPath=str(HERE/'freeze.py'),donor=refs['donorBody'])
    admission=dict(state=c['sourceAdmissionState'],label='normal-off',sourceRoot=c['configuredSourceRoot'],sourceFiles=355,selectedManifestCount=11,engineBytesRead=False,guestExecuted=False,policySha256=c['policy']['sha256'],admissionSourceSha256=c['buildAdmission']['sha256'],classicSourceAdmission=dict(cryptoSecretFailureSourcePolicy=policy['cryptoSecretFailureSourcePolicy']),validationBootstrapOnly=True,operationalAdmission=False)
    env=dict(SOURCE=c['configuredSourceRoot'],OWN=HERE,FROZEN=c['freezeRoot'],read=read)
    validate_admission=function(entry_text,'validate_admission',env)
    case('synthetic actual new admission return shape accepted',lambda:validate_admission(frame,admission))
    for key,value in [('state','ACTUAL_FINITE_CRYPTO_OWNER355_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'),('sourceRoot','/old/root'),('admissionSourceSha256','0'*64),('engineBytesRead',True)]:
        case('admission wrong '+key+' rejected',lambda k=key,v=value:validate_admission(frame,{**admission,k:v}),True)
    receipt=dict(state=c['frozenReceiptState'],label='normal-off',nativeSourceIndexed=frame['nativeSourceIndex'],freezerSourceIndexed=index,cryptoSecretFailureSourcePolicy=policy['cryptoSecretFailureSourcePolicy'],helperSha256=root['entry']['sha256'],activeFreezerTooling=dict(original=frame['entryPath'],sha256=root['entry']['sha256']),donorFreezerTooling=dict(original=refs['donorBody']['path'],sha256=refs['donorBody']['sha256']),configuredSourceRoot=c['configuredSourceRoot'],originalToolingRoot=str(HERE),sourceRoot=c['freezeRoot']+'/source',componentizeSourceRoot=c['freezeRoot']+'/componentize-source',runtimeBackendProof=dict(verified=False,version=None,vernum=None))
    validate_receipt=function(entry_text,'validate_receipt_roles',env)
    case('synthetic new receipt active/donor roles accepted',lambda:validate_receipt(frame,receipt,root['entry']['sha256'],refs['donorBody']['sha256']))
    for path,value in [(['state'],'immutable-crypto-owner-release-engine-frozen'),(['nativeSourceIndexed'],index),(['activeFreezerTooling','original'],refs['donorBody']['path']),(['runtimeBackendProof','verified'],True)]:
        case('receipt wrong '+'.'.join(path)+' rejected',lambda p=path,v=value:validate_receipt(frame,mutate(receipt,p,v),root['entry']['sha256'],refs['donorBody']['sha256']),True)
    terminal_guard=function(entry_text,'validate_terminal',{})
    outer=next(r for r in refs['files']if 'normal-off-build-parent-external-root/'in r['path']and r['path'].endswith('/terminal.json'))
    terminal=read(outer)
    case('actual clean owned build terminal shape accepted',lambda:terminal_guard(terminal,terminal['authority']))
    for key,value in [('rawExitCode',1),('parentOwnedGroupGone',False),('forcedCleanup',True),('remainingObservedPids',[123]),('signals',[{}])]:
        case('terminal wrong '+key+' rejected',lambda k=key,v=value:terminal_guard({**terminal,k:v},terminal['authority']),True)
    env=dict(shlex=shlex);function(common_text,'exact_release',env);compile_command=function(common_text,'compile_command',env)
    database=read(record(metadata['compileCommandsPath']));native={r['path']for r in metadata['sourceManifest']}
    selected=[r for r in database if any(r['file']==c['configuredSourceRoot']+'/'+n for n in native if n.endswith('.cpp')and n.startswith(('builtins/','runtime/')))]
    require(len(database)==68 and len(selected)==62,'68 database rows/62 policy C++')
    for r in selected:
        source=str(Path(r['file']).relative_to(c['configuredSourceRoot']))
        compile_command(r['command'],False,source,True,False,True,True)
    require(not any(r['file'].endswith('/embedding/embedding.cpp')for r in database))
    require(len(metadata['actualEmbeddingCompileCommands'])==1)
    compile_command(metadata['actualEmbeddingCompileCommands'][0],False,'embedding/embedding.cpp',True,False,True,True)
    models.append(dict(name='actual62 policy commands plus separate embedding1',passed=True,expected='PASS'))
    # Caller/callee key and injected-method closure is independent of running either module.
    body_ast=ast.parse(body_text);entry_ast=ast.parse(entry_text)
    keys={n.slice.value for n in ast.walk(body_ast)if isinstance(n,ast.Subscript)and isinstance(n.value,ast.Name)and n.value.id=='context'and isinstance(n.slice,ast.Constant)and isinstance(n.slice.value,str)}
    authorize=next(n for n in entry_ast.body if isinstance(n,ast.FunctionDef)and n.name=='authorize')
    frame=next(n.value for n in ast.walk(authorize)if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='frame'for x in n.targets))
    require(keys<={k.arg for k in frame.keywords},'body frame keys')
    calls={n.attr for n in ast.walk(body_ast)if isinstance(n,ast.Attribute)and isinstance(n.value,ast.Name)and n.value.id=='source_guard'}
    worker=next(n for n in entry_ast.body if isinstance(n,ast.FunctionDef)and n.name=='worker')
    guard=next(n.value for n in ast.walk(worker)if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='guard'for x in n.targets))
    require(calls=={k.arg for k in guard.keywords},'all genuine injected guard methods supplied')
    return dict(bodyContextKeys=sorted(keys),injectedGuardMethods=sorted(calls),compileDatabaseRows=68,policyCompileRows=62,otherConfiguredCompileRows=5,generatedCompileRows=1,embeddingSeparateRows=1)


def capture_models(entry_text,c,refs):
    # Execute only the actual extracted capture function against in-memory I/O,
    # injected process outcomes and fsync ledger. No child or filesystem output.
    for role,scenario in [(r,s)for r in ['source-admission','embedding-after']for s in ['success','raw1','stderr','timeout','launch-error']]:
        files={};events=[];directories={'OUT'}
        class Stream(io.BytesIO):
            def __init__(self,name):super().__init__();self.name=name
            def fileno(self):return self.name
            def close(self):
                files[self.name]=self.getvalue();events.append(('close',self.name));super().close()
        class MemoryPath:
            def __init__(self,name):self.name=str(name)
            def __truediv__(self,name):return MemoryPath(self.name+'/'+str(name))
            def is_dir(self):return self.name in directories
            def is_symlink(self):return False
            def mkdir(self,**kw):
                if not kw.get('exist_ok'):assert self.name not in directories
                directories.add(self.name)
            def open(self,mode):assert mode=='xb'and self.name not in files;return Stream(self.name)
            def __str__(self):return self.name
        class Timeout(Exception):
            stdout=b'partial-prefix';stderr=b'partial-error'
        def run(*args,**kw):
            events.append(('run',scenario))
            if scenario=='timeout':raise Timeout()
            if scenario=='launch-error':raise OSError('injected')
            return types.SimpleNamespace(returncode=1 if scenario=='raw1'else 0,stdout=b'whole-stdout',stderr=b'error'if scenario=='stderr'else b'')
        def descriptor(p):
            data=files[str(p)];return dict(path=str(p),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
        def output(p,value):files[str(p)]=(json.dumps(value)+'\n').encode();events.append(('terminal-fsync',str(p)))
        namespace=dict(Path=Path,OWN=HERE,SOURCE=c['configuredSourceRoot'],OUT=MemoryPath('OUT'),types=types,read=lambda _:json.loads(Path(c['metadata']['path']).read_bytes()),
            subprocess=types.SimpleNamespace(run=run,TimeoutExpired=Timeout,PIPE='IN_MEMORY_PIPE'),os=types.SimpleNamespace(fsync=lambda fd:events.append(('fsync',fd))),descriptor=descriptor,write=output)
        capture=function(entry_text,'capture_command',namespace)
        frame=dict(refs=refs,contract=c,commandRecords=[])
        argv=[refs['node']['path'],str(HERE/'artifact-tools/metadata-admission.mjs'),c['metadata']['path'],'normal-off',c['configuredSourceRoot']]if role=='source-admission'else [refs['ninja']['path'],'-C',str(Path(namespace['read'](None)['cmakeCachePath']).parent),'-t','commands','builtin_componentize_embedding']
        failed=False
        try:capture(frame,role,argv)
        except AssertionError:
            if scenario=='success':raise
            failed=True
        require(failed==(scenario!='success'),scenario)
        require(len(frame['commandRecords'])==1 and len(files)==3,scenario+' retained all raw outputs')
        terminal=json.loads(files['OUT/helper-calls/'+role+'/terminal.json'])
        require(len([x for x in events if x[0]=='fsync'])==2 and events[-1][0]=='terminal-fsync',scenario+' durability precedes assertion')
        require(terminal['engineExecuted']is False)
        if scenario=='timeout':require(files['OUT/helper-calls/'+role+'/stdout.log']==b'partial-prefix'and terminal['timeout']is True)
        if scenario=='launch-error':require(terminal['rawExitCode']is None and terminal['error']=='OSError')
        models.append(dict(name='actual injected capture '+role+' '+scenario,passed=True,rawRetainedBeforeRefusal=True))


def main():
    require(not(HERE/'index.json').exists(),'no modification after seal')
    c=load(HERE/'source-contract.json');refs=load(HERE/'references.json');derivations=load(HERE/'derivations.json')
    require(c['nativeSourceIndex']['sha256']=='7eb863b94b3f65b8f19480d8e8a5f3a1dac62c65d5be241097c6a0f382d74108')
    require(c['actualBuildReview']['index']['sha256']=='6a0ce53a0e9688db25501a87cb2cc763c7fceb8bdfc353b5e33999820e3fd32c')
    for item in refs['families']:family(item['index'])
    native_refs=read(record(Path(c['nativeSourceIndex']['path']).parent/'references.json'))
    for item in native_refs['families']:family(item['index'])
    for r in refs['files']:row(r)
    for key in ['policy','helper','recipe','buildAdmission','engine','metadata','actualBuildRootObservation','actualBuildContract','buildReferenceLedger']:row(c[key])
    for key in ['node','monitorEntry','donorBody']:row(refs[key])
    ledger=read(c['buildReferenceLedger']);require(ledger['schemaVersion']==1 and len(ledger['files'])==25594)
    require(len({r['path']for r in ledger['files']})==25594)
    for r in ledger['files']:require(set(r)=={'path','sha256','bytes'});row(r)
    stage=read(refs['actualStageJournal']);require(len(stage['copies'])==1424)
    for r in stage['copies']:
        a=Path(r['original']);b=Path(c['configuredSourceRoot'])/r['path']
        record(a,r['sha256'],r['bytes']);record(b,r['sha256'],r['bytes'])
        require(stat.S_IMODE(a.stat().st_mode)==stat.S_IMODE(b.stat().st_mode)==r['sourceMode'])
        require((a.stat().st_dev,a.stat().st_ino)!=(b.stat().st_dev,b.stat().st_ino))
    normal=read(refs['normalProtection'])
    require(normal['originalReferenceEntries']==1387 and len(normal['requiredNormalFreezeMembership'])==1391)
    row(normal['freezeReceipt'])
    for r in normal['frozenCopyEntries']:row(r)
    for r in normal['originals']:row(r['original']);row(r['frozen'])
    normal_root=Path(normal['freezeReceipt']['path']).parent;actual=set()
    for p in normal_root.rglob('*'):
        require(not p.is_symlink())
        if p.is_file():actual.add(str(p.relative_to(normal_root)))
    require(actual==set(normal['requiredNormalFreezeMembership']));normal_names=actual
    policy=read(c['policy']);metadata=read(c['metadata'])
    require(metadata['sourceManifest']==policy['expectedNativeSourceManifest']and len(metadata['sourceManifest'])==355)
    require(len(metadata['selectedModuleManifests'])==11 and len(metadata['componentizeSourceManifest'])==3)
    # Exact extraction/reversal proof, including inherited copy functions.
    common=(HERE/'artifact-tools/artifact_common.py').read_text()
    for extraction in derivations['commonExactFunctionExtractions']:
        row(extraction['donor']);donor=Path(extraction['donor']['path']).read_text()
        for text in [common,donor]:
            node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name==extraction['name'])
            require(ast.get_source_segment(text,node)==extraction['source'],extraction['name'])
    reversal_count=0
    for key,name in [('metadataAdmission','artifact-tools/metadata-admission.mjs'),('freezerBody','freezer-body.py')]:
        d=derivations[key];row(d['donor']);base=Path(d['donor']['path']).read_text();forward=base
        for edit in d['edits']:
            require(forward.count(edit['before'])==edit['count']);forward=forward.replace(edit['before'],edit['after']);reversal_count+=1
        actual=(HERE/name).read_text();require(forward==actual,name+' exact afterimage')
        reverse=actual
        for edit in reversed(d['edits']):
            require(reverse.count(edit['after'])==edit['count']);reverse=reverse.replace(edit['after'],edit['before'])
        require(reverse==base,name+' exact reverse')
    row(derivations['buildManifestsExactCopy']);require((HERE/'artifact-tools/build-manifests.mjs').read_bytes()==Path(derivations['buildManifestsExactCopy']['path']).read_bytes())
    parses=0
    for p in HERE.rglob('*'):
        if p.is_file()and p.name not in {'source-inputs.json','source-check-results.json','pure-model-results.json'}:
            record(p)
            if p.suffix=='.json':json.loads(p.read_bytes())
    for p in HERE.rglob('*.py'):ast.parse(p.read_text(),filename=str(p));record(p);parses+=1
    entry=(HERE/'freeze.py').read_text();body=(HERE/'freezer-body.py').read_text()
    closure=models_for_guards(c,refs,metadata,policy,body,entry);capture_models(entry,c,refs)
    require(not Path(c['freezeRoot']).exists()and not Path(c['freezeRoot']).is_symlink(),'no actual freeze')
    require(not Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-freeze-external-root').exists(),'no actual future helper output')
    for key in ['rootAuthority','independentSourceReview','actualFreezeReceipt']:require(c[key]is None)
    require(c['engineExecuted']is False and c['operationalAdmission']is False and c['runtimeAcceptanceClaim']is False)
    root_template=load(HERE/'root-authority.template.json');require(root_template['freezeAllowed']is False and root_template['freezerIndex']is None and root_template['independentSourceReview']is None)
    # Final stream rehash of the complete finite read set; source-only work.
    snapshots=list(observed.values())
    for r in snapshots:row(r)
    ledger_paths={('/private'+r['path'])if r['path'].startswith('/tmp/')else r['path']for r in ledger['files']}
    write('source-inputs.json',dict(schemaVersion=1,files=[r for r in snapshots if r['path']not in ledger_paths],separateBuildLedger=c['buildReferenceLedger'],separateBuildLedgerRows=25594,separateBuildLedgerCanonicalPaths=len(ledger_paths),uniqueObservedCanonicalPaths=len(snapshots),allObservedInputsRehashedFinally=True))
    write('pure-model-results.json',dict(schemaVersion=1,scope='Actual extracted finite predicates and injected in-memory capture; no owner imports/processes/output copies',models=models,closure=closure))
    write('source-check-results.json',dict(schemaVersion=1,state='SECRET_NORMAL_OFF_FREEZER_SOURCE_CHECKS_PASSED_V1',sourceOnly=True,sourceChecksPassed=True,checks=checks,uniqueObservedFiles=len(snapshots),actualBuildLedgerRows=25594,stageCopies1424=len(stage['copies']),normalMembership1391=len(normal_names),normalOriginalReferences1387=normal['originalReferenceEntries'],pythonAstFiles=parses,exactCommonFunctions=len(derivations['commonExactFunctionExtractions']),exactForwardReverseEdits=reversal_count,pureModels=len(models),closure=closure,actualFreezeReceipt=None,independentSourceReview=None,rootAuthority=None,ownerHelpersImported=False,helperCommandsInvoked=False,nodeInvoked=False,compilerInvoked=False,freezeCopiesExecuted=False,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
    print(json.dumps(dict(sourceChecksPassed=True,checks=checks,uniqueObservedFiles=len(snapshots),pureModels=len(models),pythonAstFiles=parses)))


if __name__=='__main__':main()
