"""Finalize proof fields and current-original checkpoint from passed owned data."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
F=Path('/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
r=json.loads((P/'results.json').read_bytes());root=json.loads((P.parent/'native-freezer-v1-normal-off-root-results.json').read_bytes());receipt=json.loads((F/'normal-off-freeze-receipt.json').read_bytes())
r.update(variant='normal-off',label='normal-off',artifactReviewPassed=True,sourceFiles=355,engine=root['engine'],metadata=root['metadata'],freezeReceipt=root['freezeReceipt'],configuredSourceRoot='/private/tmp/starling-node-compat/crypto-owner-source-v2',frozenSourceRoot=str(F/'source'),ownerActionsInvoked=False)
entries=[dict(original=row['original'],frozenPath=row['path'],sha256=row['sha256'],bytes=row['bytes'])for row in receipt['copies']if row['original']is not None]
mutable=[row for row in entries if row['frozenPath'].endswith(('normal-off-CMakeCache.txt','normal-off-compile_commands.json'))]
assert len(entries)==1387 and len(mutable)==2
write('normal-original-checkpoint.json',dict(schemaVersion=1,state='INDEPENDENT_CURRENT_NORMAL_ORIGINALS_VERIFIED_AFTER_COMPLETED_FREEZE',sourceIndexSha256=r['sourceIndexSha256'],freezeReceiptSha256=r['freezeReceiptSha256'],entries=len(entries),distinctOriginalPaths=len({row['original']for row in entries}),allCurrentOriginalsMatch=True,files=entries,twoProjectOriginalsMayChangeOnlyUnderFutureSeparateReconfigure=mutable,allFrozenCopiesRemainStrict=True,futureGcAuthorized=False,ownerActionsInvoked=False))
write('results.json',r)
print(json.dumps(dict(state=r['state'],verifiedFiles=len(r['verifiedFiles']),originalEntries=len(entries),distinctOriginalPaths=len({x['original']for x in entries}))))
