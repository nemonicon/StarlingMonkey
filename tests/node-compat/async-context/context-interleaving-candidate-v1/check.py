"""Portable Source/retained host DATA check, no JS/workload/custom-code import."""
from pathlib import Path,PurePosixPath
import hashlib,json,sys,tarfile
HERE=Path(__file__).resolve().parent
IDS=['fresh-branches','cross-owner-promises','shared-readiness','disable-captures','normal-timer-abort']
def digest(b):return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def main():
 if (HERE/'index.json').exists():
  rows=json.loads((HERE/'index.json').read_text())['files'];assert {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}=={r['path'] for r in rows}|{'index.json'}
  for r in rows:assert digest((HERE/r['path']).read_bytes())=={k:r[k] for k in ['bytes','sha256']}
 index=json.loads((HERE/'host-raw-index.json').read_text());assert digest((HERE/'host-raw.tar.gz').read_bytes())=={k:index['bundle'][k] for k in ['bytes','sha256']}
 expected={r['path']:r for r in index['files']};data={};origins={}
 with tarfile.open(HERE/'host-raw.tar.gz','r:gz') as archive:
  members=archive.getmembers();assert len(members)==len(expected)
  for m in members:
   p=PurePosixPath(m.name);assert m.isfile() and not p.is_absolute() and '..' not in p.parts and m.name in expected and m.name not in data
   b=archive.extractfile(m).read();r=expected[m.name];assert digest(b)=={k:r[k] for k in ['bytes','sha256']};b.decode('utf8');data[m.name]=b;origins[r['originalPath']]=m.name
 assert set(data)==set(expected)
 host=json.loads((HERE/'host-check-results.json').read_text());assert host['passed'] and host['sourceProtectionPassed'] and host['hostOnly'] and not host['guestOrEngineOrCompilerExecuted']
 assert len(host['phases'])==5
 for phase in host['phases']:
  t=json.loads(data[origins[phase['terminal']['path']]]);s=json.loads(data[phase['name']+'/started.json'])
  assert t['rawExitCode']==0 and t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone'] and not t['timeout'] and not t['forcedCleanup']
  assert all(t[k]==[] for k in ['signals','errors','interruptedSignals','remainingObservedPids'])
  assert s['timeoutSeconds']==120 and s['argv']==phase['argv'] and s['pid']==t['pid'] and s['authority']==t['authority']
  for key in ['stdout','stderr']:
   assert t[key]==phase[key];assert digest(data[origins[t[key]['path']]])=={k:t[key][k] for k in ['bytes','sha256']}
  assert t['stderr']['bytes']==0
 raw=(HERE/'node-oracle.stdout.jsonl').read_bytes();assert raw==data['node-oracle/stdout.log']
 frames=[json.loads(line) for line in raw.splitlines()];assert len(frames)==7 and frames[-1]==host['summary']
 projections=[];counts=[41,44,31,22,15]
 for i,frame in enumerate(frames[:-1]):
  assert frame['kind']=='whole-collection' and frame['variant']==('node-original' if i<3 else 'node-sealed-facade') and frame['call']==i%3+1
  result=frame['observed'];assert result['passed'] is True and result['call']==frame['call'] and result['boundaryMode']=='node-public-empty-store-projection'
  assert result['logicalBranchesOnly'] and result['actualHttpResourceConcurrencyProved'] is False and result['nativeOwnerIdentityOrTeardownProved'] is False and result['resetOrGcWorkload'] is False
  assert result['peakPlannedWaits']==3 and [r['id'] for r in result['records']]==IDS
  projected=[]
  for record,count in zip(result['records'],counts):
   assert record['passed'] is True and len(record['assertions'])==count and all(a['passed'] is True for a in record['assertions'])
   assert len({a['id'] for a in record['assertions']})==count and len(set(record['events']))==len(record['events'])
   for a,b in record['requiredEdges']:assert a in record['events'] and b in record['events'] and record['events'].index(a)<record['events'].index(b)
   projected.append(dict(id=record['id'],assertions=sorted(record['assertions'],key=lambda r:r['id']),eventIds=sorted(record['events']),requiredEdges=sorted(record['requiredEdges'],key=lambda x:json.dumps(x,separators=(',',':')))))
  projections.append(dict(call=result['call'],records=projected))
 assert projections[:3]==projections[3:]
 plan=json.loads((HERE/'plan.json').read_text());refs=json.loads((HERE/'references.json').read_text())
 assert plan['caseIds']==IDS and plan['componentExports']==['wasi:http/incoming-handler@0.2.10'] and plan['worldName']=='next-http'
 assert len(plan['selectedInterfaces'])==len(set(plan['selectedInterfaces']))==13 and plan['selectedInterfaces']==refs['selectedInterfaces']
 assert plan['actualRootAuthority'] is None and plan['actualComponent'] is None and plan['actualGuestRuntime'] is None and plan['actualEngine'] is None
 assert len(refs['witInputs'])==8 and plan['worldSourceIndex']==refs['worldSourceIndex']
 if '--current' in sys.argv:
  for r in json.loads((HERE/'source-inputs.json').read_text())['inputs']:
   p=Path(r['path']);assert not p.is_symlink() and digest(p.read_bytes())=={k:r[k] for k in ['bytes','sha256']}
 print(json.dumps(dict(passed=True,hostCollections=6,controlsPerCollection=5,checksPerCollection=sum(counts),totalHostChecks=6*sum(counts),nativeBoundaryProof=False,targetActions=False)))
if __name__=='__main__':main()
