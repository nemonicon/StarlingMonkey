"""Finite source/DATA preparation only; never invokes a host/action/helper."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess

D=Path(__file__).resolve().parent
inputs={}
checks=[]

def need(v,m):
    if not v:raise AssertionError(m)
    checks.append(m)

def load(p):return json.loads(Path(p).read_bytes())

def desc(p):
    p=Path(p);before=p.lstat();need(p.is_file() and not p.is_symlink(),'ordinary source/data')
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    after=p.lstat();need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'stable hash')
    return {'path':str(p),'sha256':h.hexdigest(),'bytes':after.st_size}

def verify(r):
    got=desc(r['path']);need(got=={k:r[k] for k in ['path','sha256','bytes']},'exact descriptor '+r['path'])
    if not Path(r['path']).is_relative_to(D):inputs[r['path']]=got

def rows(v):
    out=[]
    if isinstance(v,dict):
        if isinstance(v.get('path'),str) and isinstance(v.get('sha256'),str) and type(v.get('bytes')) is int:out.append({k:v[k] for k in ['path','sha256','bytes']})
        for x in v.values():out+=rows(x)
    elif isinstance(v,list):
        for x in v:out+=rows(x)
    return out

def write(n,v):
    need(not (D/'index.json').exists(),'generated source DATA only before final seal')
    with (D/n).open('w') as f:json.dump(v,f,indent=2);f.write('\n')

def packet(r):
    verify(r);root=Path(r['path']).parent;v=load(r['path']);names=[]
    for x in v['files']:
        n=x['path'];need(n not in names and not n.startswith('/') and all(p not in ('','.','..') for p in n.split('/')),'finite index member');names.append(n);verify({'path':str(root/n),'sha256':x['sha256'],'bytes':x['bytes']})
    need(sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file())==sorted(names+['index.json']),'complete packet membership')

p=load(D/'prerequisites.json')
for r in rows(p):verify(r)
for k in ['constructionSourceIndex','constructionPeerIndex','oldHTTPSourceIndex']:packet(p[k])
packet(p['availableComponentReviewData']['index'])
closure=load(p['constructionClosure']['path'])
need(closure['state']=='FINITE_ORIGINAL_CONTEXT_355_HTTP_PHYSICAL_CLOSURE' and len(closure['files'])==12667,'exact delegated whole355/source/tool/native closure')
for r in closure['files']:verify(r)
for tree in closure['toolTrees']:
    need(str(Path(tree['path']).resolve())==tree['realPath'],'exact tool physical root')
    actual=[]
    for at,dirs,leaves in os.walk(tree['path'],followlinks=False):
        for name in dirs+leaves:
            f=Path(at)/name;n=str(f.relative_to(tree['path']));kind='symlink' if f.is_symlink() else 'directory' if f.is_dir() else 'file';actual.append({'path':n,'kind':kind})
    need(sorted(actual,key=lambda r:r['path'])==tree['entries'],'full tool tree membership')
for link in closure['toolLinks']:
    f=Path(link['path']);need(f.is_symlink() and os.readlink(f)==link['linkText'] and str(f.resolve())==link['resolvedTarget'],'exact known tool link')
need(len(closure['liveInputs'])==8,'LIVE7WIT+53512adapter inherited')
for r in closure['liveInputs']:verify(r)

der=load(D/'derivations.json')
for x in der['exactCopies']:
    verify(x['origin']);need(Path(x['origin']['path']).read_bytes()==(D/x['afterimage']).read_bytes(),'exact audited standard helper copy')
x=der['standardSourceReader'];verify(x['origin']);t=Path(x['origin']['path']).read_text();need((D/'source-auth.mjs').read_text().startswith(t[:x['prefixEnd']]+t[x['bodyStart']:x['bodyEnd']]),'exact standard source reader extraction')
x=der['commandLifecycle'];verify(x['origin']);before=Path(x['origin']['path']).read_text();data=before
for e in x['edits']:
    old,new,at=e['old'],e['new'],e['afterOffsetAtEdit'];need(data.count(old)==1 and data.find(old)==at,'exact owned-command forward edit');data=data[:at]+new+data[at+len(old):]
need(data==(D/x['afterimage']).read_text() and hashlib.sha256(data.encode()).hexdigest()==x['afterSha256'],'exact owned-command afterimage')
for e in reversed(x['edits']):
    old,new,at=e['old'],e['new'],e['afterOffsetAtEdit'];need(data[at:at+len(new)]==new,'exact reverse segment');data=data[:at]+old+data[at+len(new):]
need(data==before,'owned command donor restored')

# Concrete custom source/import graph. Dynamic publication and old validator
# locations are separately fixed/authenticated descriptors, never guessed APIs.
static=re.compile(r"(?m)^\s*(?:import|export)\s+[^\n]*?\sfrom\s*['\"]([^'\"\n]+)['\"]|^\s*import\s*['\"]([^'\"\n]+)['\"]")
dynamic=re.compile(r"\bimport\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
pending=[D/'run.mjs',Path(p['validators']['combined']['path']),Path(p['validators']['hosts']['path'])];modules={};edges=[]
while pending:
    f=pending.pop().resolve()
    if str(f) in modules:continue
    modules[str(f)]=desc(f)
    if not f.is_relative_to(D):verify(modules[str(f)])
    t=f.read_text();specs=[(m.group(1) or m.group(2),'static') for m in static.finditer(t)]+[(m.group(1),'literal-dynamic') for m in dynamic.finditer(t)]
    for spec,kind in specs:
        e={'from':str(f),'specifier':spec,'kind':kind}
        if not spec.startswith('node:'):
            need(spec.startswith('.'),'no new package or guest/provider import');target=(f.parent/spec).resolve();need(target.is_file(),'physical custom dependency');e['target']=str(target);pending.append(target)
        edges.append(e)
runtime={r['path']:r for r in p['validatorPhysicalClosure']}
for path,r in modules.items():
    if not Path(path).is_relative_to(D):runtime[path]=r
need(len(runtime)<256 and all(r['bytes']<=4*1024*1024 for r in runtime.values()),'bounded complete external host helper/DATA sources')
write('runtime-dependencies.json',{'schemaVersion':1,'files':[runtime[k] for k in sorted(runtime)],'scope':'Actual host custom-import closure plus all literal validator initialization source/DATA; original355 native/tool construction closure is verified by the genuine published construction guard.','descriptorGatedDynamicImports':['Actual published construction admission only after full source/publication/artifact proof checks','Exact accepted old pure validators only after this source/dependency capsule and genuine355 admission']})
write('module-edges.json',{'schemaVersion':1,'modules':[modules[k] for k in sorted(modules)],'edges':edges,'old342EngineAdmissionInvoked':False,'new355GenuineAdmissionEntry':'published httpPreflight, unchanged constructionConfig','newWireBodyAdapter':False})

text=(D/'run.mjs').read_text();need(text.index('await captureHostSources(')<text.index('await import('),'source auth before custom body');need('finally{await source.recheck();}' in text,'wrapper final source recheck')
body=(D/'run-body.mjs').read_text();guard=(D/'guard.mjs').read_text()
need("httpPreflight({configDescriptor:rows.constructionConfig})" in guard and 'validationPreflight' not in body and 'verifyProductionTicks' not in guard+body,'genuine new355 construction admission, no old engine wrappers')
need('same(audit.fullActualNativeMetadata,frame.metadata)' in guard and 'same(audit.actualSelectedManifests,frame.selectedManifests)' in guard,'full native metadata/manifests compared unchanged')
need('await frame.recheck()' in guard and body.count('await source.recheck()')>=4,'complete native/source final/failure audits')
need(body.index("await output.write(name+'-body.bin',raw)")<body.index('JSON.parse(r.text)'),'full raw body persisted before JSON/assertions')
need('stdoutFile.bytes===0' in body and 'expectedCode:7' in body,'stopped curl refusal is explicit raw7 not a raw0 artifact')
need('createServer()' in body and "probe.close(" in body,'owned ephemeral wash port probe is closed')
need('inheritedHomePaths(process.env)' in body and not re.search(r'(?:^|[,{\s])(?:HOME|home|CODEX_HOME)\s*:\s*join\(',body),'HOME/home/CODEX_HOME preserved, only XDG/TMP task paths changed')
need('wireBodyAdapter' not in body or 'wireBodyAdapter:false' in body,'no wirebody adapter')
for n in ['future-authority.template.json','future-component-phase.template.json','future-host-controller.template.json']:
    v=load(D/n);need(v.get('sourceIndexSha256',v.get('hostSourceIndexSha256')) is None,'future source binding null')
    for k in ['actionAllowed','hostExecutionAllowed','hostRequestsAllowed']:
        if k in v:need(v[k] is False,'host action remains false')
need(load(D/'artifact-review-contract.template.json')['actualProof'] is None,'no future component proof fabricated')

e=D/'evidence';e.mkdir(exist_ok=True)
env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','LANG':'C','LC_ALL':'C','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1'}
attempt=1
while (e/('pure-attempt'+str(attempt))).exists():attempt+=1
run=e/('pure-attempt'+str(attempt));run.mkdir()
v=subprocess.run([p['node']['path'],str(D/'test-pure.mjs')],env=env,capture_output=True)
(run/'stdout.log').write_bytes(v.stdout);(run/'stderr.log').write_bytes(v.stderr)
(run/'terminal.json').write_text(json.dumps({'schemaVersion':1,'rawExitCode':v.returncode,'actualNodePureModelAndJsonDataOnly':True,'guardServerRequestsHostOrOtherActionsInvoked':False},indent=2)+'\n')
need(v.returncode==0 and not v.stderr,'pure models and full old report validator fixtures passed')
pure=json.loads(v.stdout);need(pure['checks']>=60 and pure['sourceGuardPreflightServerPortsCurlRequestsHostNativeComponentGuestCodecOrOtherActionsInvoked'] is False,'bounded positive/negative pure checks only')
syntax=[]
for f in sorted(D.glob('*.mjs')):
    v=subprocess.run([p['node']['path'],'--check',str(f)],env=env,capture_output=True);syntax.append({'file':f.name,'rawExitCode':v.returncode,'stderr':v.stderr.decode()});need(v.returncode==0,'grammar only '+f.name)
write('evidence/syntax.json',syntax)
write('source-inputs.json',{'schemaVersion':1,'files':[inputs[k] for k in sorted(inputs)],'delegatedFull355PhysicalFiles':len(closure['files']),'allInputsReadHashDataOnly':True,'operationalGuardsInvoked':False})
write('source-checks.json',{'schemaVersion':1,'state':'CONSUMERS355_HTTP_HOST_SOURCE_PURE_DATA_CHECKS_PASSED','checks':len(checks),'pureChecks':pure['checks'],'syntaxFiles':len(syntax),'inputFiles':len(inputs),'delegatedNativeToolSourceFiles':len(closure['files']),'runtimeDependencies':len(runtime),'moduleFiles':len(modules),'moduleEdges':len(edges),'oldBodyOraclesUnchanged':True,'noHostOrAdmissionActions':True})
print(json.dumps(load(D/'source-checks.json')))
