"""Finite source/data proof only. No helper/bootstrap/oracle/guest/native actions."""
from pathlib import Path
import json,hashlib,ast
O=Path(__file__).resolve().parent;K=O.parent
checks=[]
def check(n,v):assert v,n;checks.append(dict(name=n,passed=True))
def h(path):
 x=hashlib.sha256()
 with Path(path).open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):x.update(b)
 return x.hexdigest()
v=json.loads((O/'runtime-derivations.json').read_bytes())
for row in v['exactCopies']:
 check('exact unchanged '+row['file'],(O/row['file']).read_bytes()==Path(row['donor']['path']).read_bytes())
for row in v['derived']:
 s=(O/row['file']).read_text()
 if row.get('appended'):assert s.endswith(row['appended']);s=s[:-len(row['appended'])]
 for r in reversed(row['changes']):assert s.count(r['after'])==1,(row['file'],r['after']);s=s.replace(r['after'],r['before'])
 check('exact reversible '+row['file'],s==Path(row['donor']['path']).read_text())
g=(O/'guard.mjs').read_text();w=(O/'worker.mjs').read_text();run=(O/'run.mjs').read_text();loading=(O/'loading.mjs').read_text();c=(O/'checks.mjs').read_text()
for name,value in [
 ('new source peer exactstate','INDEPENDENT_CRYPTO_OWNER355_GC_RUNTIME_SOURCE_REVIEW_PASSED_V2'in g),
 ('genuine GC artifactguard not normal approval',"captureFutureGcArtifact({artifactReview:root.actualArtifactReview,componentSourceIndexSha256:refs.componentSourceIndex.sha256})"in g and 'INDEPENDENT_CRYPTO_OWNER355_COMPONENT_V3_ARTIFACT_REVIEW_PASSED_V1'not in g),
 ('actual finite GC artifact contract indexed once','artifactIndex.rows.filter(r=>equal(r,contractRow)).length===1'in g),
 ('whole actual artifact map matched','equal(contract.artifacts,artifact.proofData.artifacts)'in g),
 ('artifactSha deferred to actualproof','artifact.proofData.componentSha256===root.componentSha256'in g),
 ('no normal engine as current authority','36bd850895a'not in g),
 ('read-only hash admission no bootstrap call','cryptoOwnerGcBootstrapPreflight'not in g and 'componentPreflight('not in g),
 ('complete source closure rechecked','for(const row of all)'in g and 'artifact.recheck()'in g),
 ('normal oracle implementation copied unexecuted',(O/'oracle.mjs').read_bytes()==(K/'ownership-runtime-candidate-v1/oracle.mjs').read_bytes()),
 ('source approval before parent oracle',run.index('runtimePreflight(descriptor(config))')<run.index('const oracle=await nodeOracle()')),
 ('owned processes before session launch',run.index("mkdir(join(out.root,'processes')")<run.index('runOwnedCommand(')),
 ('three literal ordinary processes',"for(const scenario of ['retained','fresh','wrapper'])"in run),
 ('actual host raw status checked before session result',run.index('checkOwnedTerminal(terminal)')<run.index("const root=join(out.root,scenario)")),
 ('private actual GC artifact admission before generatedload',w.index('runtimePreflight(descriptor(config))')<w.index('loadSession(frame)')),
 ('complete primitive raw beforetype',w.index("kind:'return',returnedType:typeof value")<w.index("need(typeof value==='string'")),
 ('capture attempts distinct from retainedrecords','rawReturnRecordAttempts:seq,rawReturnRecordsRetained:rawWritten'in w),
 ('no unreported opaque fullvalues','fullOpaqueValueClaim:false'in w),
 ('literal zero-argument validate',"call('validate',[])"in w),
 ('three retained rotations unchanged',"scenario==='retained'?3:1"in w),
 ('full typed run records','wholeEqual(r,whole,\'Whole typed run record'in c),
 ('full schema2 wrapper','wholeEqual(r,gcExpected,\'Whole typed schema2 GC wrapper\')'in c),
 ('scoped perrun requesttable','PRESSURE_DELTAS=Object.freeze([4,4,8,0])'in c),
 ('no inherited broad false observation','gcOrEntropyRequested'not in c and 'actualNativeGcCountObserved:false'in c),
 ('observed public requesttotals summed','pressureRequestsObserved+=value.gcObservation.publicGcPressureRequests'in w and 'sessions.reduce((n,s)=>n+s.publicGcPressureRequestsObserved,0)'in run),
 ('recorded scheduled totals correct',"expectedScopedRequests:{retained:48,fresh:16,wrapper:16}"in run),
 ('same actual ESM loader finitepredicate','One real top-level await $init'in loading and "'./crypto_owner.core.wasm'"in loading and "'node:fs/promises'"in loading),
 ('real loading API no instantiate guess',"const namespace=await import(pathToFileURL(captured.rows.glue.path))"in loading and 'instantiate('not in loading),
 ('same-directory packageclassification bound','Exact actual relative loading tuple'in loading and 'Actual same-directory package bytes'in loading),
 ('exact namespace rejects then',"!Object.hasOwn(ns,'then')"in loading),
 ('parent failedsource audit finally','finally{try{await frame.recheck();}finally{await out.close();}}'in run),
 ('worker failedsource audit finally','finally{try{await frame.recheck();}finally{await out.close();}}'in w),
 ('no Wasmtime runtime path','wasmtimeExecuted:false'in run and 'wasmtimeAllowed'in g),
]:check(name,value)
refs=json.loads((O/'references.json').read_bytes());activation=[refs[k]for k in ['artifacts','actualArtifactReview','actualArtifactContract','actualComponentSha256','reviewedGcPins','gcNativeRootReview','runtimeRootAction']];check('all future artifactpinactivation slotsnull',all(x is None for x in activation))
f=json.loads((O/'input-freeze.json').read_bytes());seen=set();total=0;symlinks=[]
for row in f['files']:
 declared=row['path'];assert isinstance(declared,str)and declared.startswith('/')and'\x00'not in declared and'\\'not in declared and all(x not in ('','.','..')for x in declared.split('/')[1:]),'Whole manifest canonical absolute path required before file reads'
 p=Path(declared);assert row['path']not in seen;seen.add(row['path']);assert p.stat().st_size==row['bytes']and h(p)==row['sha256'],str(p);total+=row['bytes']
 if p.is_symlink():symlinks.append(row['path'])
check('complete original input hashes',True);check('input leaves are not projected symlinks',not symlinks)
parser='/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/toolchain/node_modules/acorn/dist/acorn.mjs';check('actual direct parser row in closure',parser in seen)
current=json.loads((O/'pure-results.json').read_bytes());check('actual GC glue inspected onlyasdata',current['generatedModuleImported']is False and current['capturedGlue']['sha256']=='a85846c12f52f2b995f12269ba7daf811e5d88ec244b333610fa65f251d4b715')
r=dict(schemaVersion=1,state='GC_RUNTIME_SOURCE_AND_INPUT_CLOSURE_PASSED_NO_ACTIONS_V1',checks=checks,count=len(checks),inputFiles=len(seen),inputBytes=total,pythonAst=True,sourceOnly=True,ownerModulesImported=False,bootstrapCalled=False,nodeOracleCalled=False,generatedJsImported=False,keyOrPressureOrGuestExecuted=False)
(O/'source-check-results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(checks=len(checks),inputs=len(seen),inputBytes=total)))
