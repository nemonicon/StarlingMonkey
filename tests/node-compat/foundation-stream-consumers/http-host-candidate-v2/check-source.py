"""Finite M1 source/read-hash/pure checks; no operational action/helper."""
from pathlib import Path
import hashlib,json,os,re,subprocess,ast
D=Path(__file__).resolve().parent
inputs={};checks=[]
def need(v,m):
    if not v:raise AssertionError(m)
    checks.append(m)
def load(p):return json.loads(Path(p).read_bytes())
def desc(p):
    p=Path(p);a=p.lstat();need(p.is_file() and not p.is_symlink(),'ordinary input')
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.lstat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable read')
    return {'path':str(p),'sha256':h.hexdigest(),'bytes':z.st_size}
def verify(r):
    need(desc(r['path'])=={k:r[k] for k in ['path','sha256','bytes']},'exact input '+r['path'])
    if not Path(r['path']).is_relative_to(D):inputs[r['path']]={k:r[k] for k in ['path','sha256','bytes']}
def descriptors(v):
    out=[]
    if isinstance(v,dict):
        if isinstance(v.get('path'),str) and isinstance(v.get('sha256'),str) and type(v.get('bytes')) is int:out.append({k:v[k] for k in ['path','sha256','bytes']})
        for x in v.values():out+=descriptors(x)
    elif isinstance(v,list):
        for x in v:out+=descriptors(x)
    return out
def write(n,v):
    need(not (D/'index.json').exists(),'unsealed source generation only')
    with (D/n).open('w') as f:json.dump(v,f,indent=2);f.write('\n')
def packet(r,count=None):
    verify(r);root=Path(r['path']).parent;ix=load(r['path']);names=[]
    for v in ix['files']:
        n=v['path'];need(n not in names and not n.startswith('/') and all(x not in ('','.','..') for x in n.split('/')),'finite indexed source');names.append(n);verify({'path':str(root/n),'sha256':v['sha256'],'bytes':v['bytes']})
    need(sorted(str(f.relative_to(root)) for f in root.rglob('*') if f.is_file())==sorted(names+['index.json']),'complete original packet membership')
    if count is not None:need(len(names)==count,'exact original indexed count')
p=load(D/'prerequisites.json')
need(p['heldHostSourceIndex']['sha256']=='4b7c36f2d50e2c3bee831d7c4681b62bea67fb667e5da10f227125e3dd860e70','immutable held4b7')
packet(p['heldHostSourceIndex'],42);packet(p['formalHold']['index'],10)
for r in descriptors(p):verify(r)
verify(p['inheritedPreparationInputFreeze'])
old_inputs=load(p['inheritedPreparationInputFreeze']['path'])['files'];need(len(old_inputs)==12781,'original complete prep context retained')
for r in old_inputs:verify(r)
packet(p['availableComponentReviewData']['index'],16)
edits=0
for v in load(D/'source-derivations.json')['files']:
    verify(v['origin']);before=Path(v['origin']['path']).read_text();data=before
    for e in v['edits']:
        old,new,at=e['old'],e['new'],e['afterOffsetAtEdit'];need(data.count(old)==1 and data.find(old)==at,'exact forward offset');data=data[:at]+new+data[at+len(old):];edits+=1
    need(data==(D/v['afterimage']).read_text() and hashlib.sha256(data.encode()).hexdigest()==v['afterSha256'],'exact afterimage')
    for e in reversed(v['edits']):
        old,new,at=e['old'],e['new'],e['afterOffsetAtEdit'];need(data[at:at+len(new)]==new,'exact reverse bytes');data=data[:at]+old+data[at+len(new):]
    need(data==before,'held donor reconstructed')
need(edits==26,'five thin afterimages26 exact edits')
static=re.compile(r"(?m)^\s*(?:import|export)\s+[^\n]*?\sfrom\s*['\"]([^'\"\n]+)['\"]|^\s*import\s*['\"]([^'\"\n]+)['\"]")
dynamic=re.compile(r"\bimport\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
pending=[D/'run.mjs',Path(p['validators']['combined']['path']),Path(p['validators']['hosts']['path'])];modules={};edges=[]
while pending:
    f=pending.pop().resolve()
    if str(f) in modules:continue
    modules[str(f)]=desc(f)
    if not f.is_relative_to(D):verify(modules[str(f)])
    text=f.read_text();specs=[(m.group(1) or m.group(2),'static') for m in static.finditer(text)]+[(m.group(1),'literal-dynamic') for m in dynamic.finditer(text)]
    for spec,kind in specs:
        e={'from':str(f),'specifier':spec,'kind':kind}
        if not spec.startswith('node:'):
            need(spec.startswith('.'),'finite local custom import');target=(f.parent/spec).resolve();need(target.is_file(),'real physical import');e['target']=str(target);pending.append(target)
        edges.append(e)
runtime={r['path']:r for r in p['validatorPhysicalClosure']}
for path,r in modules.items():
    if not Path(path).is_relative_to(D):runtime[path]=r
need(len(runtime)<=256 and all(r['bytes']<=4*1024*1024 for r in runtime.values()),'bounded full custom helper/data dependencies')
write('runtime-dependencies.json',{'schemaVersion':1,'files':[runtime[k] for k in sorted(runtime)],'completeInheritedFamilyAuthenticatedSeparately':p['heldHostSourceIndex'],'allActualCustomImportsBound':True})
write('module-edges.json',{'schemaVersion':1,'modules':[modules[k] for k in sorted(modules)],'edges':edges,'scope':'Static/literal dynamic source paths plus fixed variable-validator and authenticated original published355 admission joins.'})
auth=(D/'source-auth.mjs').read_text();entry=(D/'run.mjs').read_text();body=(D/'run-body.mjs').read_text();capture=(D/'response-capture.mjs').read_text()
need("sha256:'4b7c36f2d50e2c3bee831d7c4681b62bea67fb667e5da10f227125e3dd860e70'" in auth and 'inherited=await checkIndexedFamily(OLD_INDEX)' in auth,'full fixed old42 before custom body import')
need('await inherited.recheck();await family.recheck();await deps.recheck()' in auth,'old/current/helper source rechecks')
need(entry.index('await captureHostSources(')<entry.index('await import(') and 'finally{await source.recheck();}' in entry,'standard bootstrap first/final source checks')
need('assertHostSources(source,options.sourceIndex)' in body and body.count('await source.recheck()')>=4 and 'await a.recheck()' in body,'private capsule and complete success/failure native/source audits')
need(capture.index("await save('json',name+'-headers.json'")<capture.index('reader=response.body?.getReader()'),'headers durable before reader acquisition')
need('Buffer.from(step.value)' in capture and "await save('bytes',name+'-chunks/'" in capture,'copied visible-window chunks durable before next read')
need(capture.index("if(aggregate===null)aggregate=await attempt('bytes',name+'-body.partial.bin'")<capture.index("name+'-failure.json'"),'available partial bytes before failure receipt')
need('captureWriteFailures:' in capture and 'failed.rawCapture=summary()' in capture,'writer failures exported honestly after receipt attempt')
need('partialRawRetained:true' not in body and 'captureSetSummary(responseCaptures)' in body and 'availableResponseRawRetained:' in capture and 'responseCaptureWriteFailureObserved:' in capture,'outer failure has no blanket raw-retention claim')
need('captureResponse({name,url,tag' in body and 'responseCaptures.push(captured.capture)' in body and 'responseCaptures.push(error?.rawCapture' in body,'actual request path and all outcomes use new capture seam')
need('HOME:join(' not in body.replace('XDG_CACHE_HOME:join(','').replace('XDG_CONFIG_HOME:join(','').replace('XDG_DATA_HOME:join(',''),'HOME not repurposed')
for n in ['future-authority.template.json','future-component-phase.template.json','future-host-controller.template.json']:
    v=load(D/n);need(v.get('sourceIndexSha256',v.get('hostSourceIndexSha256')) is None,'future source binding null')
    for k in ['actionAllowed','hostExecutionAllowed','hostRequestsAllowed']:
        if k in v:need(v[k] is False,'future action remains false')
e=D/'evidence';e.mkdir(exist_ok=True);attempt=1
while (e/('pure-attempt'+str(attempt))).exists():attempt+=1
out=e/('pure-attempt'+str(attempt));out.mkdir()
env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','LANG':'C','LC_ALL':'C','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1'}
v=subprocess.run([p['node']['path'],str(D/'test-capture.mjs')],env=env,capture_output=True)
(out/'stdout.log').write_bytes(v.stdout);(out/'stderr.log').write_bytes(v.stderr);(out/'terminal.json').write_text(json.dumps({'schemaVersion':1,'rawExitCode':v.returncode,'pureInjectedReaderWriterOnly':True,'operationalActionsInvoked':False},indent=2)+'\n')
need(v.returncode==0 and not v.stderr,'all pure injected response and writer-failure regressions passed')
pure=json.loads(v.stdout);need(pure['checks']>=100 and pure['actualFetchNetworkReaderIoServersPortsCurlPreflightGuestNativeCodecOrOtherActionsInvoked'] is False,'meaningful pure checks without actions')
syntax=[]
for f in sorted(D.glob('*.mjs')):
    v=subprocess.run([p['node']['path'],'--check',str(f)],env=env,capture_output=True);syntax.append({'file':f.name,'rawExitCode':v.returncode,'stderr':v.stderr.decode()});need(v.returncode==0,'grammar only '+f.name)
write('evidence/syntax.json',syntax)
for f in D.glob('*.py'):ast.parse(f.read_text(),filename=str(f))
write('source-inputs.json',{'schemaVersion':1,'files':[inputs[k] for k in sorted(inputs)],'inheritedFreezeReadInOriginalContext':p['inheritedPreparationInputFreeze'],'all12781OriginalPhysicalInputsRehashed':True,'operationalActionsInvoked':False})
write('source-checks.json',{'schemaVersion':1,'state':'HTTP_HOST_V2_SOURCE_INJECTED_CAPTURE_CHECKS_PASSED','checks':len(checks),'pureChecks':pure['checks'],'syntaxFiles':len(syntax),'inputFiles':len(inputs),'inheritedInputs':len(old_inputs),'exactThinEdits':edits,'runtimeDependencies':len(runtime),'moduleFiles':len(modules),'moduleEdges':len(edges),'old42AndHold10Unchanged':True,'captureFailureSeamExercisedWithoutNetwork':True,'operationalActionsInvoked':False})
print(json.dumps(load(D/'source-checks.json')))
