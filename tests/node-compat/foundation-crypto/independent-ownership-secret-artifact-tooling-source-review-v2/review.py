"""Independent read/hash/AST/pure DATA only; no operational module import."""
from pathlib import Path
import ast,copy,hashlib,json,re
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'ownership-secret-artifact-tooling-candidate-v2'
seen={};checks=0

def need(value,message='check'):
    global checks
    checks+=1
    assert value,message

def file(path,sha=None,size=None,force=False):
    p=Path(path);need(p.is_absolute()and p.is_file()and not p.is_symlink(),str(p));a=p.stat();identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns);real=str(p.resolve())
    if str(p)not in seen or force:
        h=hashlib.sha256()
        with p.open('rb')as stream:
            for b in iter(lambda:stream.read(4*1024*1024),b''):h.update(b)
        z=p.stat();need(identity(a)==identity(z)and real==str(p.resolve()));row=dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
        if str(p)in seen:need(seen[str(p)]==(row,identity(z),real))
        seen[str(p)]=(row,identity(z),real)
    row,old,resolved=seen[str(p)];need(identity(a)==old and real==resolved)
    if sha is not None:need(row['sha256']==sha,str(p))
    if size is not None:need(row['bytes']==size,str(p))
    return row

def verify(row,force=False):return file(row['path'],row['sha256'],row['bytes'],force)
def read(row):verify(row);return json.loads(Path(row['path']).read_bytes())
def load(p):file(p);return json.loads(Path(p).read_bytes())
def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')

def family(index):
    value=read(index);root=Path(index['path']).parent;names={'index.json'};rows=[index]
    for r in value['files']:
        n=r['path'];need(n not in names and not n.startswith('/')and all(v not in['','.','..']for v in n.split('/')));names.add(n);row=dict(r,path=str(root/n));verify(row);rows.append(row)
    need({str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}==names and not any(p.is_symlink()for p in root.rglob('*')));return rows

def main():
    need(not(HERE/'index.json').exists());index=file(SOURCE/'index.json','8ebec1f8dd19af71a64faefd9527263054445704ae7f6595c78156e4567d1259',4659);need(len(family(index))==30)
    refs=load(SOURCE/'references.json');inputs=load(SOURCE/'source-inputs.json');ledger=read(refs['protectedInputLedger']);need(len(ledger['files'])==27729)
    for row in inputs['files']:verify(row)
    for row in ledger['files']:verify({k:row[k]for k in['path','sha256','bytes']})
    family_paths=set()
    for ix in refs['families']:
        for r in family(ix):family_paths.add(r['path'])
    declared={r['path']for r in inputs['files']}|{r['path']for r in ledger['files']};need(len(declared)==27755)
    runtime={r['path']for r in ledger['files']}|family_paths|{refs['node']['path'],refs['python']['path']}
    missing=sorted(declared-runtime);need(len(missing)==1 and missing[0].endswith('/foundation-scheduler/resource-pin-tooling-candidate-v1/pin_model.py')and len(declared&runtime)==27754)
    missing_row=next(r for r in inputs['files']if r['path']==missing[0]);verify(missing_row)
    source=(SOURCE/'artifact_tooling.py').read_text();js=(SOURCE/'bootstrap.mjs').read_text();tree=ast.parse(source)
    authorize=ast.get_source_segment(source,next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='authorize'))
    need('source-inputs.json'not in authorize and 'source-inputs.json'not in js)
    need(authorize.index("ledger=capture.read")<authorize.index('model=load_actual')and 'finally:capture.recheck()'in authorize)
    need("timedOut:error?.killed===true"in js and "rawStreamsComplete:error===null"in js and "need(error===null&&stderr.length===0"in js)
    error_models=[]
    for kind,error in[('success',None),('nonzero',dict(code=1,killed=False)),('ambiguous-killed',dict(code=None,killed=True)),('maxBuffer-kill-carrier',dict(code='ERR_CHILD_PROCESS_STDIO_MAXBUFFER',killed=True))]:
        modeled=dict(rawExitCode=0 if error is None else error['code']if type(error['code'])is int else None,timedOut=False if error is None else error['killed']is True,rawStreamsComplete=error is None,accepted=error is None)
        need(modeled['accepted']==(error is None));error_models.append(dict(kind=kind,injectedErrorData=error,currentLiteralModel=modeled,actualProcessExecuted=False))
    need(error_models[-1]['currentLiteralModel']['timedOut']is True and error_models[-1]['currentLiteralModel']['accepted']is False)
    actual=read(refs['actualVerifierReview']['result']);wire=read(refs['actualVerifierContract']);need(actual['state']==wire['requiredReviewState']and actual['verifiedPassed']is True)
    for k,v in wire['requiredFixedValues'].items():need(actual[k]==v)
    for k,v in wire['requiredExactDescriptors'].items():need(actual[k]==v)
    frame=read(refs['actualVerifierWholeFrame']);receipt=read(refs['freezeReceipt']);metadata=read(refs['metadata']);need(frame['metadata']==metadata and len(metadata)==75)
    need(len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(frame['selectedManifests'])==11)
    for row,value in zip(metadata['selectedModuleManifests'],frame['selectedManifests']):p=Path(refs['frozenSourceRoot'])/row['path'];file(p,row['sha256']);need(json.loads(p.read_bytes())==value)
    model_source=(SOURCE/'pin_model.py').read_text();model_tree=ast.parse(model_source);env=dict(copy=copy)
    for n in model_tree.body:
        if isinstance(n,ast.Assign):
            for t in n.targets:
                if isinstance(t,ast.Name):env[t.id]=ast.literal_eval(n.value)
    defs=[n for n in model_tree.body if isinstance(n,ast.FunctionDef)];exec(compile(ast.Module(body=defs,type_ignores=[]),'<extracted IO-free pin DATA functions>','exec'),env)
    pin=env['candidate'](frame,receipt,refs,index);unreviewed=env['unreviewed_document'](pin);reviewed=env['reviewed_document'](unreviewed)
    need(pin['verifierFrame']==frame and len(pin['frozenFiles'])==1902 and all(unreviewed['variants'][k]is None for k in['normal-runtime','gc-off','disabled-off']))
    changed=[]
    def compare(a,b,path=''):
        if type(a)is dict and type(b)is dict:
            need(a.keys()==b.keys())
            for k in a:compare(a[k],b[k],path+'/'+k)
        elif type(a)is list and type(b)is list:
            need(len(a)==len(b))
            for i,(x,y)in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i))
        elif a!=b:changed.append(path)
    compare(unreviewed,reviewed);need(changed==['/state','/reviewRequired','/variants/normal-off/state','/variants/normal-off/reviewRequired'])
    donor=load(SOURCE/'derivations.json');original=Path(donor['donors'][0]['path']).read_text();a=ast.parse(original)
    for entry in donor['exactFunctionCopies']:
        old=next(n for n in a.body if getattr(n,'name',None)==entry['name']);new=next(n for n in tree.body if getattr(n,'name',None)==entry['name']);old_s=ast.get_source_segment(original,old);new_s=ast.get_source_segment(source,new);need(old_s==new_s and hashlib.sha256(old_s.encode()).hexdigest()==entry['sourceSha256'])
    parent=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='parent');argv=next(n.value for n in parent.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='argv'for t in n.targets))
    parser=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
    joins=[]
    for phase in['export','bootstrap']:
        cfg=dict(path='/private/pure-config.json',sha256='0'*64,bytes=0);f=dict(refs=refs,phase=phase,configRow=cfg);command=eval(compile(ast.Expression(argv),'<actual argv expression>','eval'),dict(frame=f,OWN=SOURCE,json=json));events=[]
        class Sys:pass
        class Cap:
            def recheck(self):events.append('recheck')
        sys=Sys();sys.argv=command[3:];e=dict(Path=Path,OWN=SOURCE,__file__=str(SOURCE/'artifact_tooling.py'),sys=sys,json=json,authorize=lambda row,p:dict(capture=Cap()),worker=lambda f:events.append('worker'),parent=lambda f:0)
        exec(compile(ast.Module(body=[parser],type_ignores=[]),'<actual main with injected action endpoints>','exec'),e);need(e['main']()==0 and events==['worker','recheck']);joins.append(dict(phase=phase,argv=command,actionEndpointsInjected=True))
    need("['-B','-I',join(HERE,'artifact_tooling.py'),'parent','bootstrap','--config-descriptor',JSON.stringify(cfgRow)]"in js)
    syntax=load(HERE/'syntax/terminal.json');need(syntax['rawExitCode']==0 and syntax['syntaxCheckerUsed']is True and syntax['grammarOnly']is True)
    for row in syntax['streams'].values():verify(row);need(row['bytes']==0)
    for p in SOURCE.glob('*.py'):ast.parse(p.read_text())
    file(Path(__file__).resolve())
    for row in[v[0]for v in seen.values()]:verify(row,True)
    write('input-hashes.json',dict(schemaVersion=1,files=[v[0]for v in seen.values()],allDeclared27755Rehashed=True,initialFinalIdentitiesAndHashesVerified=True))
    write('scope-and-models.json',dict(schemaVersion=1,declaredExternalPaths=27755,protectedLedgerPaths=27729,currentRuntimeFixedDeclaredProtection=27754,missingBeforeImportAndRecheck=missing_row,missingRole='Algorithm/provenance DATA donor; not runtime imported',actualImportedDependenciesCovered=True,errorCarrierModels=error_models,actualTimeoutOrOverflowExecuted=False,wholeFrameRawMetadataFields=75,nativeSources=355,embeddingSources=3,selectedFullManifests=11,frozenPinFiles=1902,stateOnlyReviewChangedPaths=changed,argvMainJoins=joins,syntaxCheckerUsed=True,ownerActionsInvoked=False,hostActionsInvoked=False,exportOrBootstrapActionsInvoked=False))
    write('review-checks.json',dict(schemaVersion=1,checks=checks,readHashedPaths=len(seen),candidateMembers=29,declaredExternalInputPaths=27755,currentRuntimeProtectedDeclaredPaths=27754,missingDeclaredDataDonors=1,exactCopiedDonorFunctions=7,pythonArgvMainJoins=2,syntaxCheckerUsed=True,nodeSyntaxRawExitCode=0,ownerActionsInvoked=False,hostActionsInvoked=False,exportOrBootstrapActionsInvoked=False,engineExecuted=False,sourceReviewPassed=False,holdFindings=2))
    print(json.dumps(dict(checks=checks,paths=len(seen),declared27755=True,holdFindings=2,syntaxCheckerUsed=True,ownerActionsInvoked=False)))

if __name__=='__main__':main()
