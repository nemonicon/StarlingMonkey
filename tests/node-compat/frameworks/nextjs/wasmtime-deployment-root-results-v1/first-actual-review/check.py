"""Portable read-only failure-baseline checker; no originals or runtime needed."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def match(p,r):
    b=p.read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],p
def main():
    index=read(HERE/'index.json');names=[r['path'] for r in index['files']];assert len(names)==len(set(names))
    assert set(names)|{'index.json'}=={p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()}
    for r in index['files']:
        q=Path(r['path']);assert not q.is_absolute() and '..'not in q.parts and not(HERE/q).is_symlink();match(HERE/q,r)
    for r in read(HERE/'portable-files.json')['files']:match(HERE/r['retained']['path'],r['original'])
    summary=read(HERE/'results.json');r=read(HERE/'actual/result.json');c=read(HERE/'actual/client/result.json');t=read(HERE/'monitor/terminal.json');o=read(HERE/'monitor/observation.json')
    assert summary['state']=='ACTUAL_NEXT_WASMTIME_FIRST_FAILURE_BASELINE_VALIDATED_V1' and not summary['workloadPassed'] and not summary['full24And2SuiteCompleted']
    assert r['state']=='NEXT_WASMTIME_DEPLOYMENT_FAILED_UNACCEPTED_V2' and r['passed']is False and c['passed']is False
    assert len(c['http'])==23 and all(x['status']==500 and x['passed']is False for x in c['http'])
    assert len(c['errors'])==1 and '0 !== 1'in c['errors'][0]['message']
    for x in c['http']:match(HERE/'actual/client/responses'/(x['id']+'.txt'),dict(bytes=x['bodyBytes'],sha256=x['bodySha256']))
    assert all(k not in c for k in ['cacheInvalidation','streaming','browser','browserExit'])
    assert not(HERE/'actual/client/responses/server-action-submit.txt').exists() and not(HERE/'actual/client/stream-chunks.json').exists() and not(HERE/'actual/client/browser').exists()
    log=(HERE/'actual/wasmtime.stderr.log').read_text();assert log.splitlines()[1]=='global is not defined'
    for text in ['global is not defined','Redirecting call to abort()','guest never invoked `response-outparam::set` method']:assert log.count(text)==23
    assert '@/app/node_modules/next/dist/server/node-polyfill-crypto.js:4:5'in log
    assert t['rawExitCode']==1 and t['allObservedOwnedGroupsGone'] and t['parentOwnedGroupGone'] and not t['timeout'] and not t['forcedCleanup']
    assert all(t[k]==[]for k in ['errors','signals','interruptedSignals','remainingObservedPids']);assert o['ownedGroupsClean'] and o['protectedInputsPreserved'] and not o['passed']
    assert r['server']['exit']==dict(code=0,signal=None,error=None) and r['server']['sigintSent'] and not r['server']['forcedCleanup']
    print(json.dumps(dict(observationsValidated=True,workloadPassed=False,baseHttpAttempted=23,baseHttpPassed=0,browserExecuted=False,firstFailure='global is not defined',rawExitCode=1,ownedGroupsClean=True)))
if __name__=='__main__':main()
