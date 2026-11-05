"""Seal this independent retained-DATA review; never run owner or Git code."""
from pathlib import Path
import hashlib,json,os,stat

HERE=Path(__file__).resolve().parent


def d(path):
    path=Path(path);h=hashlib.sha256()
    with path.open('rb')as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
    return dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size)


def write(name,value):
    with(HERE/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())


def main():
    assert not(HERE/'index.json').exists()
    result=json.loads((HERE/'results.json').read_bytes());contract=json.loads((HERE/'result-contract.json').read_bytes())
    assert result['state']==contract['requiredReviewState']=='INDEPENDENT_SCHEDULER_TASK_SELECTION342_SOURCE_STAGE_REVIEW_PASSED_V1'
    assert result['verifiedPassed']is True and result['nativeSourceFiles']==342 and result['nativeReplacements']==3
    for key,value in contract['requiredFixedValues'].items():assert result[key]==value
    for key,value in contract['requiredExactDescriptors'].items():assert result[key]==value
    assert result['coverage']==contract['requiredCoverage']
    inputs=json.loads((HERE/'input-hashes.json').read_bytes())
    for row in inputs['files']:assert d(row['path'])==row
    copies=json.loads((HERE/'copy-review.json').read_bytes())['copies']
    for row in copies:
        a=Path(row['original']['path']);b=Path(row['target']['path'])
        assert stat.S_IMODE(a.stat().st_mode)==stat.S_IMODE(b.stat().st_mode)==row['mode']
        assert(a.stat().st_dev,a.stat().st_ino)==(row['originalDevice'],row['originalInode'])
        assert(b.stat().st_dev,b.stat().st_ino)==(row['targetDevice'],row['targetInode'])
    for name in['workRoot','freezeRoot']:assert not Path(result[name]).exists()and not Path(result[name]).is_symlink()
    write('receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_TASK_SELECTION342_SOURCE_STAGE_DATA_REVIEW_V1',result=d(HERE/'results.json'),contract=d(HERE/'result-contract.json'),inputHashes=d(HERE/'input-hashes.json'),copyReview=d(HERE/'copy-review.json'),externalEvidence=d(HERE/'external-evidence.json'),gitIsolation=d(HERE/'git-isolation-review.json'),oldModeQualification=d(HERE/'old-protection-mode-observations.json'),verifiedPassed=True,reviewerStageOrGitOrHelperActionsInvoked=False,buildExecuted=False,engineExecuted=False,operationalAdmission=False))
    rows=[]
    for path in sorted(HERE.rglob('*')):
        assert not path.is_symlink()
        if path.is_file():
            row=d(path);rows.append(dict(path=str(path.relative_to(HERE)),sha256=row['sha256'],bytes=row['bytes']))
    write('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_TASK_SELECTION342_STAGE_RESULTS_REVIEW_FAMILY_V1',files=rows))
    assert {r['path']for r in rows}|{'index.json'}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()}
    for row in rows:assert d(HERE/row['path'])==dict(row,path=str(HERE/row['path']))
    print(json.dumps(dict(index=d(HERE/'index.json'),result=d(HERE/'results.json'),contract=d(HERE/'result-contract.json'),receipt=d(HERE/'receipt.json'),members=len(rows),actualFiles=len(rows)+1)))


if __name__=='__main__':main()
