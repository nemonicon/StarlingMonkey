from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'host-observations.json').read_bytes())
for row in manifest['files']:
 p=HERE/row['path'];b=p.read_bytes();assert len(b)==row['bytes']and hashlib.sha256(b).hexdigest()==row['sha256']
for n,count in [(1,29),(2,31)]:
 root=HERE/'host-observations'/('attempt'+str(n));t=json.loads((root/'terminal.json').read_bytes());x=json.loads((root/'stdout.log').read_bytes())
 assert t['rawExitCode']==0 and t['timeout']is False and t['forcedCleanup']is False and t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True
 for key in ['errors','signals','interruptedSignals','remainingObservedPids']:assert t[key]==[]
 assert (root/'stderr.log').read_bytes()==b''and x['cases']==x['passed']==count and x['failed']==0 and x['failures']==[]
 assert x['listenerInstalls']==x['listenerDisposals']
 if n==2:assert x['oldLockCasesRefused']==2 and x['listenerInstalls']==26
 record=json.loads((HERE/('host-test-attempt'+str(n)+'.json')).read_bytes());assert record['sourceBeforeFinalUnchanged']is True
 for source in record['sourceInputs']:
  original=Path(source['path']);path=HERE/'history/attempt1'/original.name if n==1 else original
  b=path.read_bytes();assert len(b)==source['bytes']and hashlib.sha256(b).hexdigest()==source['sha256']
print(json.dumps(dict(passed=True,hostCases=[29,31],actualOldRefusals=2,guestExecuted=False)))
