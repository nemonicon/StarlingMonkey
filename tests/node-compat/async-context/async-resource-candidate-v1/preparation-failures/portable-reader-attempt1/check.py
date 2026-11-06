"""Read-only portable Source/raw-host DATA check; executes no JS or workload."""
from pathlib import Path
import hashlib, json, sys, tarfile
HERE=Path(__file__).resolve().parent
def digest(b):return hashlib.sha256(b).hexdigest()
def load(name):return json.loads((HERE/name).read_text())
def main():
 index=load('index.json');rows=index['files']
 actual={p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file() and p!=HERE/'index.json'}
 assert actual=={r['path'] for r in rows} and len(actual)==len(rows)
 for r in rows:
  p=HERE/r['path'];assert not p.is_symlink();b=p.read_bytes();assert len(b)==r['bytes'] and digest(b)==r['sha256']
 inventory=load('host-raw-index.json');raw={}
 with tarfile.open(HERE/'host-raw.tar.gz','r:gz') as archive:
  members=archive.getmembers();assert len(members)==len(inventory['files'])
  expected={r['path']:r for r in inventory['files']};assert len(expected)==len(members)
  for member in members:
   assert member.isfile() and member.name in expected
   assert not member.name.startswith('/') and '..' not in Path(member.name).parts
   b=archive.extractfile(member).read();r=expected[member.name]
   assert len(b)==r['bytes'] and digest(b)==r['sha256'];raw[r['originalPath']]=b
 terminals=[]
 for phase in inventory['phases']:
  t=json.loads(raw[phase['terminalPath']]);assert t['rawExitCode']==phase['expectedRawExitCode']
  assert t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone'] and not t['timeout'] and not t['forcedCleanup']
  assert all(t[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
  assert t['timeoutSeconds']==120
  for k in ['stdout','stderr']:
   b=raw[t[k]['path']];assert len(b)==t[k]['bytes'] and digest(b)==t[k]['sha256']
  terminals.append(t)
 final=inventory['finalDifferentialStdout'];tests=json.loads(raw[final])
 assert tests['passed'] is True and tests['hostOnly'] is True and tests['guestOrNativeExecuted'] is False
 assert tests['cases']==16==len(tests['records']) and all(r['passed'] is True for r in tests['records'])
 result=load('results.json');assert result['selectedHostDifferentialsPassed'] and not result['firstHostAttemptPassed']
 assert not any(result[k] for k in ['nativeBuildExecuted','targetGuestExecuted','fullAppExecuted','adoptionGranted'])
 if '--current' in sys.argv:
  for r in load('source-inputs.json')['inputs']:
   b=Path(r['path']).read_bytes();assert len(b)==r['bytes'] and digest(b)==r['sha256']
 print(json.dumps(dict(passed=True,sourcePayloads=len(rows),hostRawTextFiles=len(raw),terminalPhases=len(terminals),hostCases=16,targetActions=False)))
if __name__=='__main__':main()
