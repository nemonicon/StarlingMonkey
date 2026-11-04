"""Owned pure host-source hardening; no actions are imported or executed."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;S=H/'snapshot';P=H/'afterimage-proof.json';proof=json.loads(P.read_bytes())
rel='tests/node-compat/foundation-classic-streams/production-trace-regression-activated-v1/common/preflight.mjs'
p=S/rel;before=p.read_text();after=before.replace('validationPreflight,verifyFamily,hash','validationPreflight,verifyFamily,assertActionContext,hash').replace(' const native=await validationPreflight({variant});',' await assertActionContext({variant});\n const native=await validationPreflight({variant});')
assert before!=after
preimage='preimages/'+str(len(proof['edits'])+1)+'/'+rel;target=H/preimage;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(before);p.write_text(after)
proof['edits'].append({'path':rel,'beforeSha256':hashlib.sha256(before.encode()).hexdigest(),'afterSha256':hashlib.sha256(after.encode()).hexdigest(),'beforeBytes':len(before.encode()),'afterBytes':len(after.encode()),'preimage':preimage,'reason':'Require separate external Root runtime-action authority before genuine owner preflight or any inherited runner body import; native pins alone do not grant action'})
P.write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'afterimages':len(proof['edits']),'actionsExecuted':False}))
