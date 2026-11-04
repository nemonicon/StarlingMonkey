#!/usr/bin/env python3
"""Static/data checks; no genuine control preflight/worker/action invocation."""
import hashlib,json,difflib
from pathlib import Path
D=Path(__file__).resolve().parent;Z=D.parent;checks=[]
def need(v,m):
 if not v:raise AssertionError(m)
 checks.append(m)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=Z/'cost-jco-control-correctness-candidate-v1';need(digest(old/'index.json')=='ad0d651fdb8653a8a708514131bad52cf8cc05b657c6cefd92604aca3c3f7a23','old source index immutable')
for r in json.loads((old/'index.json').read_bytes())['files']:need(digest(old/r['path'])==r['sha256'] and (old/r['path']).stat().st_size==r['bytes'],'old indexed member '+r['path'])
proof=json.loads((D/'source-derivations.json').read_bytes());patch=[]
for f in proof['files']:
 p=Path(f['origin']['path']);a=p.read_text();s=a
 need(digest(p)==f['origin']['sha256'],'exact derivation original')
 for e in f['edits']:
  need(s.count(e['old'])==1,'singleton edit');at=s.index(e['old']);need(at==e['afterOffsetAtEdit'],'exact edit offset');s=s[:at]+e['new']+s[at+len(e['old']):]
 need(s==(D/f['afterimage']).read_text(),'forward exact '+f['afterimage']);b=s
 for e in f['edits'][::-1]:
  at=e['afterOffsetAtEdit'];need(b[at:at+len(e['new'])]==e['new'],'reverse new segment');b=b[:at]+e['old']+b[at+len(e['new']):]
 need(b==a,'reverse exact '+f['afterimage']);patch+=difflib.unified_diff(a.splitlines(keepends=True),s.splitlines(keepends=True),fromfile='a/'+f['afterimage'],tofile='b/'+f['afterimage'])
need(''.join(patch)==(D/'control-v2.UNAPPLIED.patch').read_text(),'exact patch reconstruction')
run=(D/'run.mjs').read_text();need(run.index("mkdir(join(output.root,'processes'),{mode:0o700})")<run.index('await runOwnedCommand('),'processes0700 inside owned root before unchanged helper');need("args:[join(HERE,'../cost-jco-control-correctness-candidate-v1/worker.mjs')" in run,'original full worker reused byte-exact')
need((D/'prerequisites.json').read_bytes()==(old/'prerequisites.json').read_bytes(),'same completed228 original prerequisite data');need((D/'scope.json').read_bytes()==(old/'scope.json').read_bytes(),'same3x30x3x2 schedule/counters/domain')
lineage=json.loads((D/'lineage.json').read_bytes())
for key in ['rootFailure','requiredCorrection']:
 r=lineage[key];need(digest(r['path'])==r['sha256'] and Path(r['path']).stat().st_size==r['bytes'],'actual failure binding '+key)
ix=lineage['failureReview']['index'];need(digest(ix['path'])==ix['sha256'],'actual independent failure index')
for r in json.loads(Path(ix['path']).read_bytes())['files']:need(digest(Path(ix['path']).parent/r['path'])==r['sha256'],'failure review member '+r['path'])
need('ROOT_REVIEWED_ZLIB_COST_JCO_CONTROL_CORRECTNESS_V2' in (D/'admission.mjs').read_text(),'new distinct Root state');a=json.loads((D/'root-authority.template.json').read_bytes());need(a['actionAllowed'] is False and a['controlSourceIndexSha256'] is None and a['sourceIndependentReview'] is None,'future authority NULL/closed')
print(json.dumps({'schemaVersion':1,'state':'CONTROL_V2_SOURCE_DATA_CHECKS_PASSED','checks':len(checks),'actionInvoked':False,'guestInvoked':False,'codecInvoked':False}))
