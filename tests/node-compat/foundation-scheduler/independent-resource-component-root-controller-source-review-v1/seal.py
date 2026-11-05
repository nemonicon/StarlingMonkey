"""Seal independent Source review only; no owner module imports or actions."""
import hashlib,json,os
from pathlib import Path
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
    assert v['state']=='INDEPENDENT_RESOURCE342_COMPONENT_ROOT_CONTROLLER_SOURCE_REVIEW_PASSED_V1'and v['sourceOnly']is v['sourceReviewPassed']is True
    assert v['controllerSourceIndexSha256']=='453f220f83887dcd53b8dd8a9db330840dd094a6e096668a095254384cda167c'
    assert v['ownerActionsInvoked']is False and v['actualRootAuthority']is None and v['actualConstruction']is None
    for row in json.loads((HERE/'input-hashes.json').read_bytes())['files']:assert d(row['path'])==row
    write('result-contract.json',dict(schemaVersion=1,requiredReviewState=v['state'],requiredFixedValues={k:v[k]for k in['schemaVersion','state','controllerSourceIndexSha256','componentSourceIndexSha256','componentSourceReviewIndexSha256','sourceOnly','sourceReviewPassed','ownerActionsInvoked','grantsAnyActionAuthority']},actualRootAuthority=None,actualConstruction=None,issuesNoAuthority=True))
    write('receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_RESOURCE342_COMPONENT_ROOT_CONTROLLER_SOURCE_REVIEW_V1',result=d(HERE/'results.json'),contract=d(HERE/'result-contract.json'),sourceAudit=d(HERE/'source-audit.json'),inputHashes=d(HERE/'input-hashes.json'),pureReview=d(HERE/'pure-review-results.json'),sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,actualRootAuthority=None,actualConstruction=None))
    rows=[]
    for p in sorted(HERE.rglob('*')):
        assert not p.is_symlink()
        if p.is_file():
            r=d(p);rows.append(dict(path=str(p.relative_to(HERE)),sha256=r['sha256'],bytes=r['bytes']))
    write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_RESOURCE342_COMPONENT_ROOT_CONTROLLER_SOURCE_REVIEW_FAMILY_V1',files=rows))
    assert{r['path']for r in rows}|{'index.json'}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()}
    for r in rows:assert d(HERE/r['path'])==dict(r,path=str(HERE/r['path']))
    print(json.dumps(dict(index=d(HERE/'index.json'),result=d(HERE/'results.json'),contract=d(HERE/'result-contract.json'),receipt=d(HERE/'receipt.json'),members=len(rows))))


if __name__=='__main__':main()
