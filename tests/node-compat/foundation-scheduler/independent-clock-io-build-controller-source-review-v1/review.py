"""Independent finite read/hash/AST and injected stdlib model. No network or owner entry."""
from pathlib import Path
import ast,hashlib,json,urllib.request,urllib.error
from email.message import Message
HERE=Path(__file__).resolve().parent
SUBJECT=HERE.parent/'clock-io-build-controller-candidate-v1'
checks=[];seen={};identities={}
def need(v,n):
 assert v,n;checks.append(n)
def descriptor(p):
 p=Path(p);a=p.stat();assert p.is_file()and not p.is_symlink();h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 z=p.stat();key=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 assert key(a)==key(z);identities[str(p)]=key(z)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
def verify(r):
 if r['path']not in seen:need(descriptor(r['path'])==r,'exact input '+r['path']);seen[r['path']]=r
 else:need(seen[r['path']]==r,'consistent duplicate descriptor')
def family(p,sha):
 ix=descriptor(p);need(ix['sha256']==sha,'pinned Source index');verify(ix);v=json.loads(p.read_bytes());names={'index.json'}
 for r in v['files']:
  n=r['path'];need(not n.startswith('/')and all(x not in ['','.','..']for x in n.split('/'))and n not in names,'local unique family row');names.add(n);verify(dict(path=str(p.parent/n),sha256=r['sha256'],bytes=r['bytes']))
 need(not any(q.is_symlink()for q in p.parent.rglob('*'))and{q.relative_to(p.parent).as_posix()for q in p.parent.rglob('*')if q.is_file()}==names,'complete family membership');return v
ix=family(SUBJECT/'index.json','064003004505c71b5cc28aef92fd929a0165d6cf3b69eb73bd935f9932dc72c8')
inputs=json.loads((SUBJECT/'source-inputs.json').read_bytes());need(len(inputs['files'])==5606,'all5606 declared Source inputs')
for r in inputs['files']:verify(r)
for f in inputs['families']:family(Path(f['index']['path']),f['index']['sha256'])
for a in inputs['links']:
 import os
 p=Path(a['path']);need(p.is_symlink()and os.readlink(p)==a['target']and str(p.resolve())==a['resolved']['path'],'declared JS alias');verify(a['resolved'])
source=(SUBJECT/'controller.py').read_text();tree=ast.parse(source)
for p in SUBJECT.rglob('*.py'):ast.parse(p.read_text())
need('with urllib.request.urlopen(url, timeout=60) as response' in source,'default urlopen before final URL assertion')
need("need(response.geturl()==url,'no unknown download redirect')" in source,'post-response equality only')
need('redirects are refused' in(SUBJECT/'README.md').read_text(),'actual Source promise')
d=json.loads((SUBJECT/'derivations.json').read_text());before=(SUBJECT/d['donor']).read_text();forward=before;reverse=source
for e in reversed(d['edits']):
 need(forward[e['beforeStart']:e['beforeEnd']]==e['old'],'exact forward donor slice');forward=forward[:e['beforeStart']]+e['new']+forward[e['beforeEnd']:]
 need(reverse[e['afterStart']:e['afterEnd']]==e['new'],'exact reverse slice');reverse=reverse[:e['afterStart']]+e['old']+reverse[e['afterEnd']:]
need(forward==source and reverse==before,'full exact derivation')
stdlib=Path(urllib.request.__file__);stdlibrow=descriptor(stdlib);verify(stdlibrow);text=stdlib.read_text()
need('HTTPRedirectHandler' in text[text.index('def build_opener'):text.index('def build_opener')+1800],'default opener includes redirect handler')
need('return self.parent.open(new, timeout=req.timeout)'in text,'default handler opens redirect before caller response')
url='https://static.crates.io/crates/windows-sys/windows-sys-0.61.2.crate'
class FakeResponse:
 def read(self):return b''
 def close(self):pass
 def geturl(self):return url
class Parent:
 def __init__(self):self.calls=[]
 def open(self,req,timeout):self.calls.append(dict(url=req.full_url,timeout=timeout));return FakeResponse()
handler=urllib.request.HTTPRedirectHandler();parent=Parent();handler.add_parent(parent);req=urllib.request.Request(url);req.timeout=60;headers=Message();headers['Location']=url
response=handler.http_error_302(req,FakeResponse(),302,'Found',headers)
need(len(parent.calls)==1 and response.geturl()==url,'pure same-URL redirect contacts fake parent and passes old final equality')
for p,k in identities.items():
 s=Path(p).stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==k,'final input identity')
result=dict(schemaVersion=1,state='INDEPENDENT_CLOCK_IO_BUILD_CONTROLLER_SOURCE_REVIEW_HOLD_V1',controllerSourceIndexSha256=descriptor(SUBJECT/'index.json')['sha256'],sourceIndexSha256='55338bc0e5e0f47ed473ccd283ed1eae70183f081abb8f6a61e5c8001711945f',sourceOnly=True,sourceReviewPassed=False,verifiedPassed=False,ownerActionsInvoked=False,hostActionsInvoked=False,buildActionsInvoked=False,networkActionsInvoked=False,stdlibRedirectHandlerExercisedOnlyWithFakeParent=True,checks=len(checks),declaredSourceInputs=5606,uniqueInputFiles=len(seen),findingCount=1,findings=[dict(id='M1',scope='Source transport guard, no actual download failure',sourcePath=str(SUBJECT/'controller.py'),finding='Default urlopen follows redirects before geturl assertion; a same-URL redirect can invoke parent.open and still pass final URL equality',requiredCorrection='Reject redirect before followup using local explicit no-proxy opener and raising HTTPRedirectHandler; preserve final URL/SHA/private/bounds guards')],pinnedStdlib=stdlibrow,pureDefaultRedirectModel=dict(parentOpenCalls=parent.calls,oldFinalUrlCheckPasses=True,networkPerformed=False),limitations=['No operation or external request ran','Exact hashes/private outputs still guard acceptance; no altered artifact or actual network claimed','No other concrete blocker found in bounded inspected Source/guard/lifecycle/command joins'],operationalAdmission=False,runtimeAcceptanceClaim=False)
(HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n');(HERE/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=list(seen.values())),indent=2)+'\n');print(json.dumps(dict(state=result['state'],checks=len(checks),inputs=len(seen),pinnedStdlib=stdlibrow)))
