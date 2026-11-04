#!/usr/bin/env python3
"""Static exact afterimage/lineage checks, never imports or executes action modules."""
import json,hashlib,difflib
from pathlib import Path
D=Path(__file__).resolve().parent;old=D.parent/'ownership-component-candidate-v1';checks=[]
def need(v,m):
 if not v:raise AssertionError(m)
 checks.append(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
need(sha(old/'index.json')=='eb648e19274c055968557227221627e2ced5dd35a2c0fb17af941dbc9a8b5c30','immutable original source seal')
for r in json.loads((old/'index.json').read_bytes())['files']:need(sha(old/r['path'])==r['sha256'] and (old/r['path']).stat().st_size==r['bytes'],'original member '+r['path'])
proof=json.loads((D/'source-derivations.json').read_bytes());patch=[]
for f in proof['files']:
 a=Path(f['origin']['path']).read_text();s=a;need(sha(f['origin']['path'])==f['origin']['sha256'],'exact afterimage origin')
 for e in f['edits']:
  need(s.count(e['old'])==1,'singleton change');at=s.index(e['old']);need(at==e['afterOffsetAtEdit'],'edit offset exact');s=s[:at]+e['new']+s[at+len(e['old']):]
 need(s==(D/f['afterimage']).read_text(),'forward exact');b=s
 for e in f['edits'][::-1]:
  at=e['afterOffsetAtEdit'];need(b[at:at+len(e['new'])]==e['new'],'reverse segment exact');b=b[:at]+e['old']+b[at+len(e['new']):]
 need(b==a,'reverse exact');patch+=difflib.unified_diff(a.splitlines(keepends=True),s.splitlines(keepends=True),fromfile='a/'+f['afterimage'],tofile='b/'+f['afterimage'])
need(''.join(patch)==(D/'adapter-options.UNAPPLIED.patch').read_text(),'exact patch')
worker=(D/'build-worker.mjs').read_text();guard=(D/'guard.mjs').read_text();need('componentOptions({engine:d.engine,adapter:packaging.adapter},wit)' in worker and 'const options=workerOptions(d,packaging,wit)' in worker,'authenticated actual options seam used by future constructor')
need("sha256:'eb648e19274c055968557227221627e2ced5dd35a2c0fb17af941dbc9a8b5c30'" in guard and 'await donor.recheck()' in guard,'original helper/data whole source pin/recheck')
need('ROOT_REVIEWED_CRYPTO_OWNER355_COMPONENT_BUILD_V2' in guard and 'INDEPENDENT_CRYPTO_OWNER355_COMPONENT_SOURCE_REVIEW_PASSED_V2' in guard,'separate action/source review states')
need('cryptoOwnerBootstrapPreflight({' in guard and 'costPreflight(' not in guard,'genuine crypto bootstrap still used')
need('ordinaryGuestExportsInvoked:false' in worker and 'generatedModuleImported:false' in worker,'construction only')
print(json.dumps({'schemaVersion':1,'state':'CRYPTO_COMPONENT_V2_SOURCE_DATA_CHECKS_PASSED','checks':len(checks),'ownerActionsInvoked':False}))
