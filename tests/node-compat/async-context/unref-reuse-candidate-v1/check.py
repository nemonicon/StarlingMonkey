"""Read-only portable Source/host DATA check; no JS, oracle, monitor or guest call."""
from pathlib import Path,PurePosixPath
import hashlib,json,stat,sys,tarfile
HERE=Path(__file__).resolve().parent
def digest(b):return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def clean(t):
 return t['rawExitCode']==0 and t['parentOwnedGroupGone'] is True and t['allObservedOwnedGroupsGone'] is True and t['timeout'] is False and t['forcedCleanup'] is False and all(t[k]==[] for k in ['signals','errors','interruptedSignals','remainingObservedPids'])
def main():
 if (HERE/'index.json').exists():
  rows=json.loads((HERE/'index.json').read_text())['files'];names=[r['path'] for r in rows]
  assert len(set(names))==len(names) and set(names)|{'index.json'}=={p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}
  assert not any(p.is_symlink() for p in HERE.rglob('*'))
  for r in rows:
   p=PurePosixPath(r['path']);assert not p.is_absolute() and '..' not in p.parts
   assert digest((HERE/r['path']).read_bytes())=={k:r[k] for k in ['bytes','sha256']}
 index=json.loads((HERE/'host-raw-index.json').read_text());expected={r['path']:r for r in index['files']};data={};origins={}
 assert digest((HERE/'host-raw.tar.gz').read_bytes())=={k:index['bundle'][k] for k in ['bytes','sha256']}
 with tarfile.open(HERE/'host-raw.tar.gz','r:gz') as archive:
  assert len(archive.getmembers())==len(expected)
  for m in archive.getmembers():
   p=PurePosixPath(m.name);assert m.isfile() and not p.is_absolute() and '..' not in p.parts and m.name in expected and m.name not in data
   b=archive.extractfile(m).read();r=expected[m.name];assert digest(b)=={k:r[k] for k in ['bytes','sha256']};b.decode('utf8');data[m.name]=b;origins[r['originalPath']]=m.name
 assert set(data)==set(expected)
 host=json.loads((HERE/'host-check-results.json').read_text());pure=json.loads((HERE/'data-check-results.json').read_text());assert host['passed'] is True and host['sourceProtectionPassed'] is True and host['hostOnly'] is True and host['guestOrEngineOrCompilerOrNetworkExecuted'] is False
 assert pure['passed'] is True and pure['sourceProtectionPassed'] is True and pure['pureDataOnly'] is True and pure['oracleReexecuted'] is False
 assert len(host['phases'])==4 and len(pure['phases'])==3
 for phase in host['phases']+pure['phases']:
  t=json.loads(data[origins[phase['terminal']['path']]]);s=json.loads(data[phase['name']+'/started.json']);assert clean(t)
  assert s['timeoutSeconds']==120 and s['argv']==phase['argv'] and s['pid']==t['pid'] and s['authority']==t['authority']
  for key in ['stdout','stderr']:
   assert t[key]==phase[key] and digest(data[origins[t[key]['path']]])=={k:t[key][k] for k in ['bytes','sha256']}
  assert t['stderr']['bytes']==0
 raw=(HERE/'node-oracle.stdout.jsonl').read_bytes();assert raw==data['node-oracle/stdout.log'];frames=[json.loads(l) for l in raw.splitlines()]
 assert len(frames)==5 and frames[0]['kind']=='identity' and frames[0]['version']=='v22.14.0' and frames[-1]==host['summary']
 contract=json.loads((HERE/'future-runtime-contract.json').read_text());tag=frames[0]['hostCase'];callchecks=0
 for i,row in enumerate(frames[1:4],1):
  v=row['observed'];phase=['A','B','C'][i-1];c=contract['controls'][phase]
  assert row['kind']=='whole-call' and row['phase']==phase and row['ordinal']==i and v['phase']==phase and v['ordinal']==i
  assert v['firstHostCase']==v['requestedHostCase']==tag and v['boundaryMode']=='node-public-empty-store-projection'
  for k,x in contract['requiredConstants'].items():assert v[k]==x
  assert [x['id'] for x in v['checks']]==c['checksIds'] and [x['id'] for x in v['callbackChecks']]==c['callbackChecksIds']
  assert all(x['passed'] is True for x in v['checks']+v['callbackChecks']);callchecks+=len(v['checks'])
  assert v['counts']==c['counts'] and v['plannedHandles']==c['plannedHandles']
  assert [{k:x[k] for k in ['sequence','id','phase','ordinal','firstLabel','secondLabel']} for x in v['observations']]==c['observations']
  assert all(x['firstIdentity'] is True and x['secondIdentity'] is True for x in v['observations'])
 assert callchecks==51 and len(frames[3]['observed']['callbackChecks'])==9
 assert frames[3]['observed']['finalCleanup']==contract['finalCleanup'] and contract['finalCleanup']['errors']==[] and contract['finalCleanup']['workloadPendingAfterClear']==0
 assert json.loads(data['pure-data/stdout.log'])['pureDataChecks']==60
 plan=json.loads((HERE/'plan.json').read_text());refs=json.loads((HERE/'references.json').read_text())
 assert plan['worldName']=='next-http' and plan['selectedInterfaces']==refs['selectedInterfaces'] and len(plan['selectedInterfaces'])==len(set(plan['selectedInterfaces']))==13
 assert plan['componentExports']==['wasi:http/incoming-handler@0.2.10'] and len(plan['witInputs'])==8
 assert all(plan[k] is None for k in ['actualEngine','actualNativeMetadata','actualRootAuthority','actualComponent','actualGuestRuntime'])
 if '--current' in sys.argv:
  for r in json.loads((HERE/'source-inputs.json').read_text())['inputs']:
   p=Path(r['path']);assert stat.S_ISREG(p.lstat().st_mode) and not p.is_symlink() and digest(p.read_bytes())=={k:r[k] for k in ['bytes','sha256']}
 print(json.dumps(dict(passed=True,hostCalls=3,hostCallChecks=51,distinctCallbackChecks=9,pureDataChecks=60,rawCommands=7,guestOrNativeExecuted=False)))
if __name__=='__main__':main()
