"""Read-only portable DATA checks for four completed component constructions."""
from pathlib import Path, PurePosixPath
import argparse,hashlib,json,re,tarfile

KINDS=['regexp','stacktrace','dependencies','real-next']
IMPORTS={'wasi:cli/environment@0.2.10','wasi:io/poll@0.2.10','wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10','wasi:random/random@0.2.10','wasi:io/error@0.2.10','wasi:io/streams@0.2.10','wasi:filesystem/types@0.2.10','wasi:filesystem/preopens@0.2.10','wasi:http/types@0.2.10','wasi:cli/stdout@0.2.10','wasi:cli/stderr@0.2.10','wasi:http/outgoing-handler@0.2.10'}
ENGINE='e7baa5a9201ac8d81005294fc02cd463d75b61e43b95158512985feba995b1a5'
META='cb473c7230102712b71399a70184988934cebae85d3efea6c50beecf039ed36d'


def digest(b):return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def safe(s):
 p=PurePosixPath(s);assert s and not p.is_absolute()and'..'not in p.parts and'\\'not in s and str(p)==s;return s
def properties(node):
 assert node['type']in ['Object','Array'];r={}
 for p in node['properties']:
  assert p['kind']=='data'and set(p['key'])=={'string'}and p['key']['string']not in r;r[p['key']['string']]=p['value']
 return r
def typed_array(node):
 assert node['type']=='Array';p=properties(node);length=p.pop('length');assert length['type']=='number';n=int(length['value']);assert set(p)==set(map(str,range(n)));out=[]
 for i in range(n):
  v=p[str(i)]
  if v['type']=='Array':out.append(typed_array(v))
  else:assert v['type']=='string';out.append(v['value'])
 return out


def verify(root):
 root=Path(root)
 if(root/'index.json').exists():
  rows=json.loads((root/'index.json').read_text())['files'];assert {str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}=={r['path']for r in rows}|{'index.json'}
  for r in rows:assert digest((root/safe(r['path'])).read_bytes())=={k:r[k]for k in ['bytes','sha256']}
 index=json.loads((root/'payload-index.json').read_text());bundle=root/'data.tar.gz';assert digest(bundle.read_bytes())=={k:index['bundle'][k]for k in ['bytes','sha256']}
 entries={r['path']:r for r in index['entries']};assert len(entries)==len(index['entries']);data={}
 with tarfile.open(bundle,'r|gz')as tar:
  for member in tar:
   n=safe(member.name);assert member.isfile()and n in entries and n not in data;b=tar.extractfile(member).read();b.decode();assert digest(b)=={k:entries[n][k]for k in ['bytes','sha256']};data[n]=b
 assert set(data)==set(entries)
 origins={r['originalPath']:r['path']for r in index['entries']}
 def ref(r):
  n=origins[r['path']];assert digest(data[n])=={k:r[k]for k in ['bytes','sha256']};return n
 def obj(n):return json.loads(data[n])
 def clean(prefix,terminal):
  assert terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone']and terminal['allObservedOwnedGroupsGone']and not terminal['timeout']and not terminal['forcedCleanup']
  assert all(terminal[k]==[]for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
  assert terminal['finalGroups']and all(not x['alive']for x in terminal['finalGroups'])
  ref(terminal['stdout']);ref(terminal['stderr'])
  events=[obj(n)for n in sorted(data)if n.startswith(prefix+'/owned-')]
  assert [e['sequence']for e in events]==list(range(len(events)))and[e['process']for e in events]==terminal['observedProcesses']
  return len(events)
 summaries=[];processes=0
 for kind in KINDS:
  base=kind+'/output/';a=obj(kind+'/authority.json');r=obj(base+'result.json');audit=obj(base+'component-audit.json');node=obj(base+'api-return/node-result.json')
  assert r['schemaVersion']==1 and r['state']=='NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2'and r['passed']is True and r['error']is None
  assert r['entryMode']==a['entryMode']and r['callerIndex']==a['callerIndex']and r['rootAuthority']['sha256']==digest(data[kind+'/authority.json'])['sha256']
  ref(r['rootAuthority']);ref(r['callerIndex']);ref(r['plan'])
  assert r['finalProtection']=={'unchanged':True}
  for key in ['metadataFrameProjected','ordinaryExportsInvoked','httpServed','appMountedAtInit','productionProfilePromoted']:assert r[key]is False
  assert a['componentizeInitAllowed']is True
  for key in ['ordinaryExportsAllowed','httpServingAllowed','networkAllowed','nativeBuildAllowed','packageMutationAllowed','globalPinMutationAllowed','debugAllowed','applicationMountAtInitAllowed','deployedResnapshotAllowed']:assert a[key]is False
  art=r['artifacts'];assert art['engine']==a['engine']and art['nativeMetadata']==a['nativeMetadata']
  assert a['engine']['sha256']==ENGINE and a['engine']['bytes']==31324485 and a['nativeMetadata']['sha256']==META
  assert art['engineBuildEvidence']==a['engineBuildEvidence'];ref(art['nativeMetadata'])
  assert art['component']in index['externalBinaryReferences']
  assert audit['state']=='NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1'and audit['passed']is True and audit['component']==art['component']
  assert audit['engine']==a['engine']and audit['nativeMetadata']==a['nativeMetadata']and audit['entryMode']==r['entryMode']
  assert set(audit['emittedImports'])==set(audit['selectedInterfaces'])==IMPORTS and len(audit['emittedImports'])==13
  assert audit['unusedSelectedInterfaces']==[]and audit['allEmittedVersion']=='0.2.10'and audit['noExternalPreview1OrCustomImports']is True
  assert audit['exports']==['wasi:http/incoming-handler@0.2.10']
  assert node['state']=='NEXT_NATIVE_COMPONENT_API_RETURN_CAPTURED_UNREVIEWED_V1'and node['entryMode']==r['entryMode']
  for key in ['component','returnedImports','returnedOwnShape']:assert node['artifacts'][key]==art[key]
  assert node['inputEntry']==art['inputEntry']and node['inputSourceIndex']==art['inputSourceIndex'];ref(art['inputEntry']);ref(art['inputSourceIndex'])
  for key in ['returnedImports','returnedOwnShape','componentAudit']:ref(art[key])
  pairs=obj(base+'api-return/returned-imports.json');assert len(pairs)==131 and len({tuple(x)for x in pairs})==131
  assert all(isinstance(p,list)and len(p)==2 and all(isinstance(v,str)for v in p)for p in pairs)
  assert {p[0]for p in pairs}==IMPORTS
  shape=obj(base+'api-return/returned-own-shape.json');props=properties(shape);assert set(props)=={'component','imports','debug'}
  assert props['component']['type']=='Uint8Array'and props['component']['file']==art['component']
  assert props['component']['byteLength']==art['component']['bytes']and props['component']['sha256']==art['component']['sha256']
  assert typed_array(props['imports'])==pairs and props['debug']=={'type':'undefined'}
  assert [c['label']for c in r['commands']]==['componentize-init','component-validate','component-wit']
  for c in r['commands']:
   assert c==obj(base+c['label']+'-observation.json')and c['rawExitCode']==0 and c['clean']is True
   terminal=obj(ref(c['terminal']));started=obj(base+c['label']+'/started.json')
   assert started['argv']==c['argv']and started['timeoutSeconds']==c['capSeconds'];ref(c['stdout']);ref(c['stderr'])
   assert terminal['stdout']==c['stdout']and terminal['stderr']==c['stderr'];processes+=clean(base+c['label'],terminal)
  assert audit['validateTerminal']==r['commands'][1]['terminal']and audit['witTerminal']==r['commands'][2]['terminal']
  text=data[base+'component-wit/stdout.log'].decode();world=text.split('\npackage wasi:',1)[0]
  wit_imports=re.findall(r'^\s*import ([^;]+);',world,re.M);wit_exports=re.findall(r'^\s*export ([^;]+);',world,re.M)
  assert set(wit_imports)==IMPORTS and len(wit_imports)==13 and wit_exports==audit['exports']
  outer=obj(kind+'/outer/terminal.json');started=obj(kind+'/outer/started.json');processes+=clean(kind+'/outer',outer)
  assert outer['authority']==r['rootAuthority']and started['authority']==r['rootAuthority']and started['timeoutSeconds']==2400
  assert a['callerIndex']['path'].removesuffix('/index.json')+'/run.py'in started['argv']and a['outputRoot']in outer['stdout']['path']
  lines=data[kind+'/outer/stdout.log'].splitlines();assert len(lines)==1
  observed=json.loads(lines[0]);assert observed['passed']is True and observed['result']==dict(path=a['outputRoot']+'/result.json',**digest(data[base+'result.json']))
  summaries.append(dict(kind=kind,entryMode=r['entryMode'],result=dict(path=a['outputRoot']+'/result.json',**digest(data[base+'result.json'])),
                        component=art['component'],componentAudit=art['componentAudit'],inputEntry=art['inputEntry'],inputSourceIndex=art['inputSourceIndex'],
                        callerIndex=art['callerIndex']if'callerIndex'in art else r['callerIndex'],threePhaseRawExitCodes=[0,0,0],outerRawExitCode=0,
                        emittedInterfaces=13,standardVersion='0.2.10',noExternalPreview1OrCustomImports=True,returnedTypedPairs=131,
                        wholeTypedGraphPreserved=True,debugReturnType='undefined',ordinaryExportsInvoked=False,initOnlyConstruction=True))
 return dict(schemaVersion=1,state='FOUR_INTL_COMPONENT_CONSTRUCTIONS_RETAINED_DATA_REVIEW_PASSED_V1',verifiedPassed=True,constructions=summaries,
             innerRawZeroPhases=12,outerRawZeroPhases=4,observedProcessRecords=processes,allImportsStandard13Only=True,
             externalComponentBinariesNotCopied=True,inputBookendsAreRecordedSourceCoupledEvidence=True,
             newEngineOrConstructorOrGuestActionByReader=False,ordinaryRuntimeAccepted=False,fullNextAccepted=False)


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('data',nargs='?',default=str(Path(__file__).resolve().parent));a=p.parse_args();print(json.dumps(verify(a.data),indent=2))
