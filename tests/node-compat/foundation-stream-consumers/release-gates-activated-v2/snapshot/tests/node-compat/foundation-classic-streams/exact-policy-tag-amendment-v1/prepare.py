"""Derive exact342 host guards only. No native/guest/host execution."""
from pathlib import Path
import difflib
import hashlib
import json

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
PARENT=BASE/'production-regression-candidate-v1'
OLD='sm-uncaught-event-v3-protected-abort-v2-private-ticks-v1'
NEW=OLD+'-classic-streams-source-v1'
FILES=['release/runners/events.mjs','common/runners/allocator-gc.mjs','off/runners/sync.mjs','off/runners/runtime.mjs','off/runners/callbacks.mjs']
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    records=[];patch=[]
    for name in FILES:
        before=(PARENT/name).read_text()
        assert before.count("'"+OLD+"'")==1
        edits=[{'old':"'"+OLD+"'",'new':"'"+NEW+"'"}]
        if name=='common/runners/allocator-gc.mjs':
            edits.extend([
              {'old':'const pinsPath=admitted.pinsPath,pinBytes=admitted.pinBytes,pins=admitted.pin;','new':'const pins=admitted.pin;'},
              {'old':"assert.equal(pins.state,'reviewed-real-production-freeze');",'new':"assert.equal(pins.state,'reviewed-real-classic-production-freeze');\nassert.equal(hash(await readFile(pins.freezeReceiptPath)),pins.freezeReceiptSha256);"},
              {'old':'const commandsPath=admitted.report.commandsPath;','new':'const commandsPath=pins.commandsPath;'},
              {'old':'fixedGCAdmission:{path:pinsPath,sha256:hash(pinBytes),pins}',
               'new':"fixedGCAdmission:{variant:admitted.report.variant,pinState:pins.state,pins,freezeReceiptPath:pins.freezeReceiptPath,freezeReceiptSha256:pins.freezeReceiptSha256,scope:'Actual classic freeze pin; delegated classicPreflight/recheck owns the authority bytes. No old pin-schema projection.'}"},
              {'old':'const report={schema:1,state:', 'new':'await admitted.recheck();\nconst report={schema:1,state:'}])
        after=before
        for edit in edits:
            assert after.count(edit['old'])==1
            after=after.replace(edit['old'],edit['new'])
        reverse=after
        for edit in reversed(edits):
            assert reverse.count(edit['new'])==1
            reverse=reverse.replace(edit['new'],edit['old'])
        assert reverse==before
        for prefix,text in [('before',before),('proposed',after)]:
            target=HERE/prefix/name;target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('x')as stream:stream.write(text)
        patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
        records.append({'path':name,'beforeSha256':sha(before.encode()),'afterSha256':sha(after.encode()),'edits':edits,'exactReverseProof':True})
    (HERE/'exact-policy-tags.UNAPPLIED.patch').write_text(''.join(patch))
    (HERE/'transformation-proof.json').write_text(json.dumps({'schemaVersion':1,'state':'FIVE_EXACT342_POLICY_GUARDS_AND_ACTUAL_GC_PIN_FIELDS','oldStrictPolicyVersion':OLD,'newStrictPolicyVersion':NEW,
      'parentSourceIndexSha256':'81c55887dc5e767db27477ba28f0e7a26a948435c7ddc61c70da329d4bd7f029','registrarAmendmentStillRequired':'7462f1255f4fd5048e345a96d58908c8e6251158bf36e5ab4450dab97be193b4',
      'records':records,'previousChangedHostBodies':2,'additionalChangedHostBodies':5,'totalChangedHostBodies':7,'oldBodiesByteIdentical':57,
      'guestOrOracleBytesChanged':False,'engineMetadataRewritten':False,'nativeOrGuestExecuted':False},indent=2)+'\n')
if __name__=='__main__':main()
