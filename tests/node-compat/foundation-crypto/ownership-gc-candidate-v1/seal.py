"""Seal this unreviewed SOURCE proposal. DATA reads/hashes only."""
from pathlib import Path
import ast,hashlib,json,os
HERE=Path(__file__).resolve().parent
def descriptor(p):
    p=Path(p);before=p.stat();h=hashlib.sha256();assert p.is_file()and not p.is_symlink()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    after=p.stat();assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=before.st_size)
def write(name,v):
    with (HERE/name).open('x')as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    return descriptor(HERE/name)
assert not(HERE/'index.json').exists()
inputs=json.loads((HERE/'input-freeze.json').read_bytes())
for r in inputs['files']:assert descriptor(r['path'])==r
protection=json.loads((HERE/'normal-protection.json').read_bytes())
freeze=Path(protection['freezeReceipt']['path']).parent
assert {p.relative_to(freeze).as_posix()for p in freeze.rglob('*')if p.is_file()}==set(protection['requiredNormalFreezeMembership'])
derivations=json.loads((HERE/'guest-derivations.json').read_bytes());guest=(HERE/'guest.GC.UNEXECUTED.mjs').read_text()
for edit in reversed(derivations['edits']):assert guest.count(edit['after'])==1;guest=guest.replace(edit['after'],edit['before'])
assert guest==Path(derivations['source']['path']).read_text()
for p in ['plan.py','prepare.py','seal.py']:ast.parse((HERE/p).read_text())
result=json.loads((HERE/'results.json').read_bytes());assert result['sourcePreparationPassed']is True and result['sourceIndependentReview']is None and result['rootAuthority']is None and result['reviewedGcPin']is None
write('source-receipt.json',dict(schemaVersion=1,state='SEALED_CRYPTO_OWNER355_GC_SOURCE_PROPOSAL_UNREVIEWED_V1',sourceOnly=True,result=descriptor(HERE/'results.json'),sourcePreparationPassed=True,sourceIndependentReview=None,rootAuthority=None,reviewedGcPin=None,sourceInputsRehashed=len(inputs['files']),normalOriginalReferenceEntries=1387,normalFrozenMembers=1391,exactGuestReversals=len(derivations['edits']),pythonSourceAstChecks=3,newGuestJsSyntaxParsed=False,ownerHelpersPreflightBuildFreezeBootstrapNodeCompilerGuestCryptoKeyPrototypeGcActionsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,actionAuthorityIssued=False,unimplementedGates='follow-on-contract.json'))
files=[]
for p in sorted(HERE.rglob('*')):
    if p.is_file():r=descriptor(p);r['path']=p.relative_to(HERE).as_posix();files.append(r)
    else:assert p.is_dir()and not p.is_symlink()
index=write('index.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_CRYPTO_OWNER355_GC_PROPOSAL_V1',files=files,sourceOnly=True,ownerActionsInvoked=False,sourceReviewRequired=True,actionAuthorityIssued=False))
for r in files:
    actual=descriptor(HERE/r['path']);assert actual['sha256']==r['sha256']and actual['bytes']==r['bytes']
assert {p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()}=={r['path']for r in files}|{'index.json'}
print(json.dumps(dict(index=index,result=descriptor(HERE/'results.json'),contract=descriptor(HERE/'follow-on-contract.json'),receipt=descriptor(HERE/'source-receipt.json'),indexedFiles=len(files),actualFiles=len(files)+1,sourceInputs=len(inputs['files']),normalOriginalEntries=1387,normalFrozenMembers=1391,sourceOnly=True,independentReview=None,rootAuthority=None)))
