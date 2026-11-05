"""Seal independent Source review only; no action module or monitor import."""
from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parent


def d(path):
    p=Path(path);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)


def write(name,value):
    with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())


def main():
    assert not(HERE/'index.json').exists()
    v=json.loads((HERE/'results.json').read_bytes())
    assert v['state']=='INDEPENDENT_ZLIB_COST_TIMING_V5_CONTROLLER_SOURCE_REVIEW_PASSED_V1'and v['sourceOnly']is v['sourceReviewPassed']is True and v['ownerActionsInvoked']is False
    assert v['controllerSourceIndexSha256']=='ae8e1f2398fa524bd8058540521da4ee827eb2bf06117281c6be4108aecb9efb'
    for name in['actualRootAuthority','actualPhase','actualQuietWindow','actualGlobalBudget','actualTimingResult']:assert v[name]is None
    inputs=json.loads((HERE/'input-hashes.json').read_bytes())
    # The complete original ledger was independently rehashed initially/finally
    # by review.py. Recheck its exact immutable bytes and all additional inputs.
    assert d(inputs['fullActualPlanLedger']['path'])==inputs['fullActualPlanLedger']and inputs['fullActualPlanLedgerRows']==59878
    for r in inputs['files']:assert d(r['path'])==r
    write('result-contract.json',dict(schemaVersion=1,requiredReviewState=v['state'],requiredFixedValues={k:v[k]for k in['schemaVersion','state','controllerSourceIndexSha256','sourceOnly','sourceReviewPassed','ownerActionsInvoked','measurementApproval','grantsAnyActionAuthority']},actualRootAuthority=None,actualPhase=None,actualQuietWindow=None,actualTimingResult=None,issuesNoAuthority=True))
    write('receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_TIMING_V5_CONTROLLER_SOURCE_REVIEW_V1',result=d(HERE/'results.json'),contract=d(HERE/'result-contract.json'),sourceAudit=d(HERE/'source-audit.json'),inputHashes=d(HERE/'input-hashes.json'),pureResults=d(HERE/'pure-results.json'),sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,actualRootAuthority=None,actualTimingResult=None))
    rows=[]
    for p in sorted(HERE.rglob('*')):
        assert not p.is_symlink()
        if p.is_file():
            r=d(p);rows.append(dict(path=str(p.relative_to(HERE)),sha256=r['sha256'],bytes=r['bytes']))
    write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_TIMING_V5_CONTROLLER_SOURCE_REVIEW_FAMILY_V1',files=rows))
    assert {r['path']for r in rows}|{'index.json'}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()}
    for r in rows:assert d(HERE/r['path'])==dict(r,path=str(HERE/r['path']))
    print(json.dumps(dict(index=d(HERE/'index.json'),result=d(HERE/'results.json'),contract=d(HERE/'result-contract.json'),receipt=d(HERE/'receipt.json'),members=len(rows))))


if __name__=='__main__':main()
