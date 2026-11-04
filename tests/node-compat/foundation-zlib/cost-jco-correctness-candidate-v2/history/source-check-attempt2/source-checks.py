#!/usr/bin/env python3
"""Read/data contract checks only; no owner imports, preflights or actions."""
from pathlib import Path
import argparse,hashlib,json,re
D=Path(__file__).resolve().parent;checks=[]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,label):
 if not ok:raise AssertionError(label)
 checks.append(label)
def main():
 parent=json.loads((D/'parent-copies.json').read_bytes());need(parent['parentIndexSha256']=='610295513e79ffa3a926c466f2b07a05d465694e8ee7de706f3966052f8f305a','exact immutable610 lineage')
 need(len(parent['files'])==13,'thirteen unchanged semantic/corpus/lifecycle files')
 for row in parent['files']:
  p=Path(row['origin']);need(p.read_bytes()==(D/row['copy']).read_bytes()and h(p)==row['sha256']and p.stat().st_size==row['bytes'],'exact unchanged '+row['copy'])
 need((D/'glue-policy.mjs').read_bytes()==(D.parent/'cost-component-glue-amendment-v1/abi.mjs').read_bytes(),'actual cf311 pure7+helper policy byte copy')
 need((D/'proofs.mjs').read_bytes()==(D.parent/'cost-component-candidate-v1/proofs.mjs').read_bytes(),'existing immutable indexed proof reader exact')
 origins=json.loads((D/'observed-source/origins.json').read_bytes());need(origins['parentAndWorkerOverallRawExitCode']==1 and origins['acceptedArtifactProof']is None,'failed-v2 source guidance not accepted artifact')
 for r in origins['files']:need(h(D/'observed-source'/r['copy'])==r['sha256']and(D/'observed-source'/r['copy']).read_bytes()==Path(r['original']).read_bytes(),'captured source original unchanged '+r['copy'])
 need(not any(p.suffix in['.wasm','.a','.o']for p in D.rglob('*')if p.is_file()),'no binary artifacts copied into source proposal')
 authority=json.loads((D/'root-authority.template.json').read_bytes());need(authority['actionAllowed']is False and authority['correctnessSourceIndexSha256']is None and authority['sourceIndependentReview']is None and authority['oracle']is None,'future own authority and proof descriptors NULL')
 need(all(x is None for x in authority['componentBuildAuthorities'].values())and all(x is None for x in authority['actualComponentReviews'].values()),'allthree genuine build authorities and artifact reviews NULL')
 need(authority['nodeMatrixCodecCallsAllowed']is False and authority['ordinaryGuestCallsAllowed']is False and authority['pilotOrTimingAllowed']is False and authority['stockWasmtimeExecutionAllowed']is False,'no source-time codec/guest/timing/WT grants')
 guard=(D/'admission.mjs').read_text();loader=(D/'loading.mjs').read_text();worker=(D/'worker.mjs').read_text();run=(D/'run.mjs').read_text()
 native=(D.parent/'cost-tooling-candidate-v3/native.mjs').read_text();need('metadataSha256:root.metadata.sha256'in native and 'frame.pin.metadataSha256'in guard and 'frame.pin.receiptSha256'not in guard,'genuine actual cost pin API metadataSha256, not historical receipt field')
 need("from './parser-tuple.mjs'"in guard and "from './loading.mjs'"not in guard,'parent guard imports data tuple, not external pure helper chain before source auth')
 need(guard.index('for(const[name,digest]of Object.entries(PARENTS))')<guard.index("await import('../cost-component-glue-amendment-v1/guard.mjs')"),'all parent source indices authenticated before external guard import')
 need('rootAction:authorityRow'in guard and 'componentPreflight({componentSourceIndexSha256:COMPONENT,arm' in guard,'actual unchanged construction authority reused only for real read-only component admission')
 need('artifactModel(r,arm)'in guard and 'checkOwnedTerminal(owned)'in guard and 'parent.rawExitCode===0'in guard,'separate actual review plus real parent/owned terminal checks')
 need('complete.result.sha256===r.workerResult.sha256'in guard and 'Each actual critical artifact worker-indexed exactly once'in guard,'full actual completion/results/artifact indexing')
 need('for(const row of r.evidenceRows)await regular' in guard and 'r.proof.recheck()'in guard,'actual proof capsules and external artifact/terminal evidence rechecked')
 need(loader.index('const rows=captureArtifactRows(artifact)')<loader.index('await regular(row'),'private immutable artifact primitives captured before first await')
 need(loader.index('validateGlueProgram(parser.parse')<loader.index('const namespace=await import'),'actual static shape/no-then check before generated module import')
 need('const namespace=await import(pathToFileURL(rows.glue.path).href)'in loader and 'namespace[name](...args)'in loader,'observed direct ESM/TLA entry and sync public-call wrapper')
 need(not re.search(r'\b(?:instantiate|WebAssembly\.Memory)\s*\(',re.sub(r'//[^\n]*','',loader)),'no direct instantiate/private-memory API call in finite loader code')
 need('codec_cost.core.wasm'in loader and "node.source.value==='node:fs/promises'"in loader and "topAwaits[0]?.name==='$init'"in loader,'finite actual core/builtin/TLA source policy')
 need("!Object.hasOwn(ns,'then')"in loader,'runtime namespace no then guard')
 need("args[0]<30"in loader and "args[1]===1"in loader,'no controls/calibration/timing argument scope')
 need(run.index('await correctnessPreflight(options)')<run.index('DurableOutput.create'),'Root/artifact admission before output creation')
 need('timeoutMs:600000'in run and 'runOwnedCommand({'in run and 'checkOwned(status)'in run,'existing bounded owned-worker lifecycle/terminal gate')
 need(run.index('for(const path of registered)')<run.index('checkOwned(status)'),'raw pipes registered before success assertion')
 need('await admitted.recheck();await output.recheck();'in run and 'EXTERNAL_PARENT_ZERO_AND_REVIEW_REQUIRED' in run,'final recheck before completion plus external parent gate')
 need('postFailureSourceAuditPassed'in run and 'postFailureCriticalFilesAuditPassed'in worker,'postfailure source/critical audit retained')
 need("executable:NODE.path,args:[join(HERE,'worker.mjs'),JSON.stringify(d)]"in run,'small file descriptor CLI, not large staged payload argv')
 need('row.bytes<=4*1024*1024'in run and 'maxBytes:4*1024*1024'in worker,'bounded worker descriptor file')
 need('full45 Node/native/FFON streams captured before matrix'in run and 'executeFreshNodeEdges'in run and 'offNodeEdges.push'in run,'45/135 and separate OFF15/15/45 orchestration')
 need('await session.recheck();await recheck();await output.recheck()'in worker and 'EXTERNAL_OWNED_EXIT_ZERO_REQUIRED'in worker,'child critical postchecks and external0 requirement')
 need("preparedAndStageAndPriorOutputCleared"in(D/'collector.mjs').read_text(),'copied public cleanup model retained')
 for name in['runtime.mjs','native-provider.mjs','fflate-provider.mjs','guest.mjs']:
  need(not(D/name).exists(),'no guest/provider afterimage '+name)
 for p in D.glob('*.mjs'):
  if p.name=='test-loading-pure.mjs':continue
  text=p.read_text();need(not re.search(r"(?:^|\n)import[^\n]*from\s*['\"](?:node:zlib|fflate)",text),'no codec import at initialization '+p.name)
 return{'schemaVersion':1,'state':'BOUNDED_CORRECTNESS_V2_SOURCE_DATA_CHECKS_PASSED','checks':len(checks),'labels':checks,'ownerHelpersOrActionsInvoked':False,'providersCodecsGeneratedModulesOrGuestInvoked':False,'sourceOnly':True,'runtimeAcceptanceClaim':False}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',required=True);o=Path(a.parse_args().output);o.mkdir(mode=0o700)
 try:r=main()
 except Exception as e:r={'state':'SOURCE_CHECKS_FAILED','checks':len(checks),'labels':checks,'errorType':type(e).__name__,'message':str(e),'ownerActionsInvoked':False};(o/'results.json').write_text(json.dumps(r,indent=2)+'\n');raise
 (o/'results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'state':r['state'],'checks':r['checks'],'output':str(o)}))
