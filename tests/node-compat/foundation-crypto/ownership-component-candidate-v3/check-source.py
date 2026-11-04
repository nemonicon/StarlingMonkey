#!/usr/bin/env python3
"""Actual source/data/physical role checks only. No helper imports or actions."""
import hashlib,json,difflib
from pathlib import Path
D=Path(__file__).resolve().parent;K=D.parent;old=K/'ownership-component-candidate-v2';checks=[]
def need(v,m):
 if not v:raise AssertionError(m)
 checks.append(m)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(r,label):need(digest(r['path'])==r['sha256'] and Path(r['path']).stat().st_size==r['bytes'],label)
need(digest(old/'index.json')=='b03d1edb70c77eefb3effad27046189d23ff2baa91bb154e05b5eac56d234bc7','unchanged v2 HOLD source')
for r in json.loads((old/'index.json').read_bytes())['files']:verify({**r,'path':str(old/r['path'])},'unchanged v2 member '+r['path'])
proof=json.loads((D/'source-derivations.json').read_bytes());f=proof['guard'];verify(f['origin'],'guard origin');a=Path(f['origin']['path']).read_text();s=a
for e in f['edits']:
 need(s.count(e['old'])==1,'singleton change');at=s.index(e['old']);need(at==e['afterOffsetAtEdit'],'forward offset');s=s[:at]+e['new']+s[at+len(e['old']):]
need(s==(D/'guard.mjs').read_text(),'forward exact');b=s
for e in f['edits'][::-1]:
 at=e['afterOffsetAtEdit'];need(b[at:at+len(e['new'])]==e['new'],'reverse segment');b=b[:at]+e['old']+b[at+len(e['new']):]
need(b==a,'reverse exact');need(''.join(difflib.unified_diff(a.splitlines(keepends=True),s.splitlines(keepends=True),fromfile='a/guard.mjs',tofile='b/guard.mjs'))==(D/'configured-bootstrap.UNAPPLIED.patch').read_text(),'exact patch')
for v in proof['unchangedCopies']:verify(v['origin'],'unchanged copy origin');need(Path(v['origin']['path']).read_bytes()==(D/v['afterimage']).read_bytes(),'same parent/worker '+v['afterimage'])
c=json.loads((D/'bootstrap-context.json').read_bytes());verify(c['actualContract'],'actual stable contract');contract=json.loads(Path(c['actualContract']['path']).read_bytes());verify(c['actualFrame'],'retained actual full frame');need(contract['state']=='INDEPENDENT_CRYPTO_OWNER355_NORMAL_OFF_PIN_AND_JS_BOOTSTRAP_RESULTS_REVIEW_PASSED_V1' and contract['verifiedPassed'],'actual completed read-only proof data')
for r in [c['actualBootstrapReview']['index'],c['actualBootstrapReview']['result'],c['configuredSourceIndex'],c['configuredBootstrapEntry'],c['configuredToolPins'],c['configuredPolicy']]:verify(r,'actual context/index/entry')
ix=json.loads(Path(c['configuredSourceIndex']['path']).read_bytes());rows=ix['files']
for r in rows:verify({**r,'path':str(Path(c['configuredSourceIndex']['path']).parent/r['path'])},'full configured68b6 source '+r['path'])
tools=json.loads(Path(c['configuredToolPins']['path']).read_bytes());policy=json.loads(Path(c['configuredPolicy']['path']).read_bytes());root=Path(c['configuredSourceRoot']);need(len(tools['toolDependencies'])==922 and len(policy['expectedNativeSourceManifest'])==355,'exact full configured tool/native sets')
for r in tools['toolDependencies']:verify({**r,'path':str(root/r['path'])},'actual configured tool '+r['path'])
for r in policy['expectedNativeSourceManifest']:
 for prefix in [root,Path(c['sourceRoot'])]:need(digest(prefix/r['path'])==r['sha256'],'actual configured/frozen native '+str(prefix/r['path']))
oldp=json.loads((K/'ownership-component-candidate-v1/prerequisites.json').read_bytes());need(digest(oldp['bootstrapEntry']['path'])==c['configuredBootstrapEntry']['sha256'] and oldp['bootstrapEntry']['path']!=c['configuredBootstrapEntry']['path'],'same source bytes distinct executable contexts')
# Data-only reconstruction of the real Python helper root, no module execution.
configured_common=Path(c['configuredBootstrapEntry']['path']).parent/'common.py';original_common=Path(oldp['bootstrapEntry']['path']).parent/'common.py';text=configured_common.read_text();need('REPO=HERE.parents[4]' in text or 'REPO = HERE.parents[4]' in text,'actual helper root semantics')
need(configured_common.parent.parents[4]==root and original_common.parent.parents[4]!=root,'actual Python __file__ contexts differ')
need((root/'tests/node-compat/build-engine.sh').stat().st_size==49377 and digest(root/'tests/node-compat/build-engine.sh')=='eec3245841fff07e5bf9c3ff7b488106c94b71705262b22272d60a8ea4d7bfb3','actual configured owner355 recipe')
need("import(pathToFileURL(configured.entry.path))" in s and "import(pathToFileURL(p.bootstrapEntry.path))" not in s,'only configured authenticated entry imports')
need('configured.assertReturned(frame)' in s and 'await configured.recheck()' in s,'unchanged actual returned roots/metadata and full closure recheck')
print(json.dumps({'schemaVersion':1,'state':'CRYPTO_COMPONENT_V3_CONTEXT_SOURCE_DATA_CHECKS_PASSED','checks':len(checks),'genuineHelperInvoked':False,'componentizerInvoked':False,'keyOrCryptoInvoked':False,'ownerActionsInvoked':False}))
