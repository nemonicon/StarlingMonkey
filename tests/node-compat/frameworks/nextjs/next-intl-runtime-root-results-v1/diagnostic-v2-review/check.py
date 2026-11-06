"""Portable retained diagnostic DATA reader; executes no constructor or guest."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,re,tarfile
def digest(b):return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def safe(s):
 p=PurePosixPath(s);assert s and not p.is_absolute()and'..'not in p.parts and'\\'not in s and str(p)==s;return s
def verify(root):
 root=Path(root)
 if(root/'index.json').exists():
  rows=json.loads((root/'index.json').read_text())['files'];assert {str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}=={r['path']for r in rows}|{'index.json'}
  for r in rows:assert digest((root/safe(r['path'])).read_bytes())=={k:r[k]for k in ['bytes','sha256']}
 index=json.loads((root/'payload-index.json').read_text());assert digest((root/'data.tar.gz').read_bytes())=={k:index['bundle'][k]for k in ['bytes','sha256']}
 expected={r['path']:r for r in index['entries']};data={}
 with tarfile.open(root/'data.tar.gz','r|gz')as tar:
  for m in tar:
   n=safe(m.name);assert m.isfile()and n in expected and n not in data;b=tar.extractfile(m).read();b.decode();assert digest(b)=={k:expected[n][k]for k in ['bytes','sha256']};data[n]=b
 assert set(data)==set(expected);origins={r['originalPath']:r['path']for r in index['entries']}
 def obj(n):return json.loads(data[n])
 def ref(r):
  n=origins[r['path']];assert digest(data[n])=={k:r[k]for k in ['bytes','sha256']};return n
 def terminal(prefix,code):
  t=obj(prefix+'/terminal.json');assert t['rawExitCode']==code and t['parentOwnedGroupGone']and t['allObservedOwnedGroupsGone']and not t['forcedCleanup']and not t['timeout']
  assert all(t[k]==[]for k in ['errors','signals','interruptedSignals','remainingObservedPids']);ref(t['stdout']);ref(t['stderr'])
  events=[obj(n)for n in sorted(data)if n.startswith(prefix+'/owned-')];assert[e['sequence']for e in events]==list(range(len(events)))and[e['process']for e in events]==t['observedProcesses'];return t,len(events)
 ca=obj('authority/construction.json');ra=obj('authority/runtime.json');cr=obj('constructor/result.json');rr=obj('runtime/result.json')
 assert cr['state']=='NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2'and cr['passed']is True and cr['error']is None and cr['finalProtection']=={'unchanged':True}
 assert cr['callerIndex']==ca['callerIndex']==ra['constructionCallerIndex'];ref(cr['callerIndex']);ref(cr['rootAuthority']);ref(cr['plan'])
 for key in ['ordinaryExportsInvoked','httpServed','appMountedAtInit','productionProfilePromoted','metadataFrameProjected']:assert cr[key]is False
 assert cr['artifacts']['component']==ra['component']==rr['component']and cr['artifacts']['component']in index['externalBinaryReferences']
 assert ra['constructionResult']==rr['constructionResult']==dict(path=ca['outputRoot']+'/result.json',**digest(data['constructor/result.json']))
 assert ra['inputEntry']==rr['inputEntry']==cr['artifacts']['inputEntry']and ra['inputSourceIndex']==rr['inputSourceIndex']==cr['artifacts']['inputSourceIndex'];ref(ra['inputEntry']);ref(ra['inputSourceIndex'])
 audit=obj('constructor/component-audit.json');assert audit['passed']is True and audit['component']==ra['component']and len(audit['emittedImports'])==13
 assert set(audit['emittedImports'])==set(audit['selectedInterfaces'])==set(rr['emittedImports'])==set(rr['selectedInterfaces'])
 assert all(re.fullmatch(r'wasi:[a-z-]+/[a-z-]+@0\.2\.10',s)for s in audit['emittedImports'])and audit['noExternalPreview1OrCustomImports']is True
 assert audit['exports']==['wasi:http/incoming-handler@0.2.10']
 assert [c['label']for c in cr['commands']]==['componentize-init','component-validate','component-wit'];processes=0
 for c in cr['commands']:
  assert c['rawExitCode']==0 and c['clean']is True;ref(c['terminal']);ref(c['stdout']);ref(c['stderr']);t,n=terminal('constructor/'+c['label'],0);processes+=n
 _,n=terminal('constructor-outer',0);processes+=n
 assert rr['state']=='NEXT_WASMTIME_DEPLOYMENT_FAILED_UNACCEPTED_V2'and rr['passed']is False and rr['adoption']is False
 assert rr['originalInputsPreserved']is True and rr['readonlyAppPreserved']is True
 assert rr['server']['exit']=={'code':0,'signal':None,'error':None}and rr['server']['forcedCleanup']is False
 assert rr['server']['shutdownRequested']and rr['server']['sigintSent']and rr['client']['exit']=={'code':1,'signal':None,'error':None}
 for process in ['server','client']:
  for stream in ['stdout','stderr']:ref(rr[process][stream])
 client=obj(ref(rr['client']['result']));assert client['passed']is False and len(client['http'])==24 and sum(c['passed']is True for c in client['http'])==11
 assert client['transportErrors']==[]and client['errors']
 for c in client['http']:
  body=data['runtime/client/responses/'+c['id']+'.txt'];assert len(body)==c['bodyBytes']and hashlib.sha256(body).hexdigest()==c['bodySha256']
 _,n=terminal('runtime-outer',1);processes+=n
 stderr=data['runtime/wasmtime.stderr.log'].decode();source=[];views=[];causes=[]
 for line in stderr.splitlines():
  if line.startswith('NEXT_SOURCE_INPUT_DIAGNOSTIC '):source.append(json.loads(line.split(' ',1)[1]))
  if line.startswith('NEXT_BUFFER_INPUT_DIAGNOSTIC '):views.append(json.loads(line.split(' ',1)[1]))
  if line.startswith('NEXT_CAUSE_DIAGNOSTIC '):causes.append(json.loads(line.split(' ',1)[1]))
 assert len(source)==2
 for s in source:
  assert s['stage']=='Module._compile'and s['contentType']=='string'and s['euroLiteralOffset']>=0 and s['mojibakeLiteralOffset']==-1
  assert 8364 in s['windowCodeUnits']and '\u20ac'in s['window']and[ord(c)for c in s['window']]==s['windowCodeUnits']
 assert len(views)==1;v=views[0]['intrinsicView'];assert v['isView']is True and v['typedArrayTag']['value']=='Uint8Array'
 assert v['byteOffset']['value']==0 and v['byteLength']['value']==134 and v['prototypeIsCapturedU8']is False and v['capturedU8HasInstance']is False
 assert v['backing']['prototypeIsCapturedAB']is True and v['backing']['arrayBufferByteLength']['value']==134
 assert views[0]['error'][0]['code']=='ERR_SM_NODE_UNSUPPORTED'
 return dict(schemaVersion=1,state='RETAINED_SOURCE_VIEW_DIAGNOSTIC_V2_DATA_REVIEW_PASSED_V1',verifiedPassed=True,constructorPassed=True,constructorInnerRawExitCodes=[0,0,0],constructorOuterRawExitCode=0,
             runtimeOriginalPassed=False,runtimeOuterRawExitCode=1,wasmtimeGracefulExitCode=0,clientExitCode=1,httpPassed=11,httpTotal=24,browserAcceptanceClaim=False,
             sourceInputDiagnostics=source,postBodyInputDiagnostics=views,causeDiagnostics=causes,observedProcessRecords=processes,standardInterfaces=13,externalPreview1OrCustomImports=False,
             originalInputsAndReadonlyCopyPreserved=True,bigBinaryOrApplicationCopiesIncluded=False,diagnosticChangesFunctionIdentities=True,
             scope='Source input is observed before native compilation; this does not prove correct compiled literal semantics. View branding is an observation, not a Buffer implementation fix.',
             implementationOrFullNextAccepted=False,newConstructorOrRuntimeActionByReader=False)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('data',nargs='?',default=str(Path(__file__).resolve().parent));a=p.parse_args();print(json.dumps(verify(a.data),indent=2))
