"""Seal corrected SOURCE/template/data packet, no workload actions."""
from pathlib import Path
import ast,hashlib,json,os
HERE=Path(__file__).resolve().parent
def descriptor(p):
    p=Path(p);s=p.stat();h=hashlib.sha256();assert p.is_file()and not p.is_symlink()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    t=p.stat();assert(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns)
    return dict(path=str(p.resolve()),sha256=h.hexdigest(),bytes=s.st_size)
def write(name,v):
    with(HERE/name).open('x')as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    return descriptor(HERE/name)
assert not(HERE/'index.json').exists()
inputs=json.loads((HERE/'input-freeze.json').read_bytes())['files']
for r in inputs:assert descriptor(r['path'])==r
derived=json.loads((HERE/'correction-derivations.json').read_bytes());guest=(HERE/'guest.GC.UNEXECUTED.mjs').read_text();back=guest
for e in reversed(derived['edits']):assert back.count(e['after'])==1;back=back.replace(e['after'],e['before'])
assert back==Path(derived['source']['path']).read_text()and 'gcOrEntropyRequested'not in guest
inherited=json.loads((HERE/'inherited-source.json').read_bytes());old_root=Path(inherited['heldSourceIndex']['path']).parent
old_deriv=json.loads((old_root/'guest-derivations.json').read_bytes())
for e in reversed(old_deriv['edits']):assert back.count(e['after'])==1;back=back.replace(e['after'],e['before'])
assert back==Path(old_deriv['source']['path']).read_text()
normal=json.loads((Path(inherited['normalProtection']['path'])).read_bytes());freeze=Path(normal['freezeReceipt']['path']).parent
assert {p.relative_to(freeze).as_posix()for p in freeze.rglob('*')if p.is_file()}==set(normal['requiredNormalFreezeMembership'])
for name in ['collector.py','prepare.py','parse-source.py','seal.py']:ast.parse((HERE/name).read_text())
pure=json.loads((HERE/'pure-results.json').read_bytes());syntax=json.loads((HERE/'syntax-results.json').read_bytes());assert pure['checks']==35 and syntax['terminal']['rawExitCode']==0 and syntax['moduleImported']is False
assert descriptor(HERE/'guest.GC.UNEXECUTED.mjs')['sha256']==syntax['terminal']['targetSha256']
contract=json.loads((HERE/'follow-on-contract.json').read_bytes());assert contract['actualNativeGcCountObserved']is False and contract['sourceIndependentReview']is None
model=json.loads((HERE/'expected-complete-gc-record.json').read_bytes());assert [r['gcObservation']['publicGcPressureRequests']for r in model['records']]==[4,4,8,0]
result=write('results.json',dict(schemaVersion=1,state='CRYPTO_OWNER355_GC_SOURCE_CORRECTION_PREPARED_UNREVIEWED_V2',sourceOnly=True,sourceCorrectionPrepared=True,sourceIndependentReview=None,rootAuthority=None,reviewedGcPin=None,actualGcResult=None,heldSourceIndex=inherited['heldSourceIndex'],holdReviewIndex=inherited['holdReviewIndex'],nativeSourceIndex=inherited['nativeSourceIndex'],oldSourceUnchanged=True,normalNoKeyInitGuestUnchanged=True,oldGcOrEntropyRequestedRemoved=True,noDirectOnlyReinterpretation=True,observationVersion='public-buffer-gc-pressure-v1',outerSchemaVersion=2,outerKind='crypto-owner-within-export-gc-validation-v2',perRunPressureRequests=[4,4,8,0],perRunPressureRecords=[4,4,8,0],perRunPublicGcPressureRequested=[True,True,True,False],outerPublicGcPressureRequested=True,outerPressureRequests=16,outerPressureRecords=16,entropyRequested=False,actualNativeGcCountObserved=False,partialPressureRequestCounterBeforeBufferCall=True,failedRunObservationRetained=True,allOriginalHmacKeyRefusalWindowSentinelFieldsUnchanged=True,oldExactEditsReversed=8,newExactEditsReversed=6,pureDataChecks=35,pythonAstChecks=4,pinnedNodeSyntaxChecks=1,pinnedNodeSyntaxParserInvoked=True,guestModuleImported=False,sourceInputSpellingsFinallyRehashed=len(inputs),normalOriginalReferenceEntries=1387,normalFrozenMembers=1391,ownerNativeHelperPreflightBuildFreezerBootstrapGuestCryptoKeyPrototypeGcActionsInvoked=False,newRootOrPhaseAuthorityIssued=False,gcNativeOrComponentResultsAdopted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False))
receipt=write('source-receipt.json',dict(schemaVersion=1,state='SEALED_UNREVIEWED_CRYPTO_OWNER355_GC_SOURCE_CORRECTION_V2',result=result,sourceOnly=True,sourceIndependentReview=None,rootAuthority=None,reviewedGcPin=None,oldSourceAndHoldPreserved=True,ownerActionsInvoked=False,pinnedNodeSyntaxOnlyInvoked=True))
files=[]
for p in sorted(HERE.rglob('*')):
    if p.is_file():r=descriptor(p);r['path']=p.relative_to(HERE).as_posix();files.append(r)
    else:assert p.is_dir()and not p.is_symlink()
index=write('index.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_CRYPTO_OWNER355_GC_CORRECTION_V2',files=files,sourceOnly=True,ownerActionsInvoked=False,sourceReviewRequired=True,actionAuthorityIssued=False))
for r in files:
    d=descriptor(HERE/r['path']);assert d['sha256']==r['sha256']and d['bytes']==r['bytes']
assert {p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()}=={r['path']for r in files}|{'index.json'}
print(json.dumps(dict(index=index,result=result,contract=descriptor(HERE/'follow-on-contract.json'),receipt=receipt,indexedFiles=len(files),actualFiles=len(files)+1,sourceInputs=len(inputs),oldExactEdits=8,newExactEdits=6,pureChecks=35,syntaxOnlyChecks=1,ownerActionsInvoked=False)))
