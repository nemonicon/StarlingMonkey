"""Owned pure host report-label corrections; guest/test behavior is unchanged."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;S=H/'snapshot';P=H/'afterimage-proof.json';proof=json.loads(P.read_bytes())
B='tests/node-compat/foundation-classic-streams/production-trace-regression-activated-v1/'
for rel,old,new in [
 (B+'off/preflight.mjs','classic342-off-followon','consumers355-validation-off-followon'),
 (B+'capability/focused/run-gc.mjs','NEW_CLASSIC342_RELEASE','NEW_CONSUMERS355_VALIDATION_RELEASE'),
 (B+'capability/focused/run-callback-return.mjs','Classic342 is newly source/config pinned','Consumers355 is bound through the genuine validation-only source/config gate'),
 (B+'common/runners/allocator-gc.mjs','Actual classic freeze pin; delegated classicPreflight/recheck owns the authority bytes. No old pin-schema projection.','Actual consumers355 freeze pin; genuine consumersBootstrapPreflight/recheck owns the authority bytes. No old pin-schema projection.')]:
 p=S/rel;before=p.read_text();assert old in before;after=before.replace(old,new)
 preimage='preimages/'+str(len(proof['edits'])+1)+'/'+rel;target=H/preimage;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(before);p.write_text(after)
 proof['edits'].append({'path':rel,'beforeSha256':hashlib.sha256(before.encode()).hexdigest(),'afterSha256':hashlib.sha256(after.encode()).hexdigest(),'beforeBytes':len(before.encode()),'afterBytes':len(after.encode()),'preimage':preimage,'reason':'Truthful355 validation-only host report label/scope; case/oracle inputs and assertions unchanged'})
P.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'afterimageEdits':len(proof['edits']),'actionsExecuted':False}))
