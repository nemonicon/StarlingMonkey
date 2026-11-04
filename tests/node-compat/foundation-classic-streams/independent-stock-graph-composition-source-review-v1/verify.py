#!/usr/bin/env python3
"""Read-only source/hash proofs. No owner imports, subprocesses or action mains."""
import hashlib
import difflib
import json
from pathlib import Path
import stat
import sys

HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
GRAPH=FAMILY/'measurement-stock-graph-amendment-v1'
OWNER=FAMILY/'measurement-stock-composition-candidate-v1'
PARENT=FAMILY/'measurement-execution-activated-v2'
GRAPH_SHA='4355ee56baa684cd9c3b4e9e7e15019f422535f63ef0aada0bfbcafca62ee729'
PARENT_SHA='1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612'
PROOF_SHA='bf9fa2a619a92fe6e84b63df8a7650276aa2b13b5d41205835563051b5c3d2ef'
seen={}

def checked(path,digest=None,size=None):
    path=Path(path);before=path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(),str(path)
    h=hashlib.sha256()
    with path.open('rb')as src:
        for block in iter(lambda:src.read(1024*1024),b''):h.update(block)
    after=path.lstat()
    assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
    row={'path':str(path),'sha256':h.hexdigest(),'bytes':before.st_size}
    assert digest is None or row['sha256']==digest,str(path)
    assert size is None or row['bytes']==size,str(path)
    assert str(path)not in seen or seen[str(path)]==row,str(path)
    seen[str(path)]=row;return row['sha256']

def load(path,digest=None):
    digest=checked(path,digest);raw=Path(path).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==digest
    return json.loads(raw)

def indexed(root,digest,count=None):
    data=load(root/'index.json',digest)
    assert count is None or len(data['files'])==count
    names=set()
    for row in data['files']:
        name=row['path'];assert name not in names and not Path(name).is_absolute()and '..'not in Path(name).parts
        names.add(name);checked(root/name,row['sha256'],row['bytes'])
    return data

def closure(root):
    data=load(root/'input-freeze.json');paths=set()
    for row in data['inputs']:
        p=Path(row['path']);p=p if p.is_absolute()else root/p
        assert str(p)not in paths;paths.add(str(p));checked(p,row['sha256'],row['bytes'])
    return len(paths)

def derivation(path,target):
    d=load(path);origin=Path(d['origin'])
    checked(origin,d['beforeSha256']);checked(target,d['afterSha256'])
    before=origin.read_text();after=target.read_text();value=before
    for row in d['edits']:
        assert value.count(row['old'])==row['count'];value=value.replace(row['old'],row['new'],row['count'])
    assert value==after
    for row in reversed(d['edits']):
        assert value.count(row['new'])==row['count'];value=value.replace(row['new'],row['old'],row['count'])
    assert value==before
    return len(d['edits'])

assert len(sys.argv)==2
OWNER_SHA=sys.argv[1];assert len(OWNER_SHA)==64 and all(x in '0123456789abcdef'for x in OWNER_SHA)
g=indexed(GRAPH,GRAPH_SHA,11);o=indexed(OWNER,OWNER_SHA,20)
graph_inputs=closure(GRAPH);owner_inputs=closure(OWNER)
assert graph_inputs==47 and owner_inputs==9163
indexed(PARENT,PARENT_SHA,35)
indexed(FAMILY/'independent-common-byte-v2-three-arm-failure-review-v1',PROOF_SHA,16)
assert derivation(GRAPH/'derivation.json',GRAPH/'bundle-matched.after.mjs')==2
assert derivation(OWNER/'bundle-binding-derivation.json',OWNER/'bundle-stock.mjs')==1
driver_edits=derivation(OWNER/'driver-derivation.json',OWNER/'run-stock-only.mjs')
assert (OWNER/'stock-graph.mjs').read_bytes()==(GRAPH/'stock-graph.mjs').read_bytes()
stock=load(PARENT/'stock-source-graph.json');assert 'provider'not in stock
assert len(stock['sourceBeforeAfter'])==3
assert {Path(x['path']).name for x in stock['sourceBeforeAfter']}=={'entry.mjs','workload.mjs','stock-provider.mjs'}
own={x['path']for x in stock['sourceBeforeAfter']}
assert len(stock['modules'])==102 and len(set(stock['modules']))==102
for row in stock['sourceBeforeAfter']:
    assert stock['modules'].count(row['path'])==1
    assert [x for x in stock['physicalSources']if x['path']==row['path']]==[row]
    checked(row['path'],row['sha256'],row['bytes'])
assert len([x for x in stock['modules']if x not in own])==99
guard=(GRAPH/'stock-graph.mjs').read_text()
for literal in ['sourceBeforeAfter.length===3',"['bytes','path','sha256']",'physical.length,1','prior.length,99']:
    assert literal in guard
future=load(OWNER/'future-three-arm-authority.json')
assert future['state']=='UNCONFIGURED_COMMON_BYTE_THREE_ARM_COMPOSITION_AUTHORITY'
for key in ['failedParentRootReceiptSha256','sourceFamilyIndexSha256','pairPinsSha256','independentProofIndexPath','independentProofIndexSha256','independentProofResultPath','independentProofResultSha256','completedArmRecords']:
    assert future[key]is None
assert future['runtimeAcceptanceClaim']is future['timingAllowed']is False
provenance=(OWNER/'provenance.mjs').read_text();driver=(OWNER/'run-stock-only.mjs').read_text();compose=(OWNER/'compose.mjs').read_text()
assert "for(const arm of ['stock-on']){"in driver
assert driver.index('await verifyCollector(collectorHere,indexSha)')<driver.index('await executionPreflight(')
assert driver.index('await verifyThreeArmAuthority(')<driver.index('await executionPreflight(')
assert "guestSourceFamilyIndexSha256:parentIndexSha256,collectorSourceIndexSha256:indexSha"in driver
assert "await save(join(directory,'arm-results.partial.json'),record)"in driver
assert 'retainedRotations:3,rounds,freshRows,wasmtime:wt'in driver
assert 'for(let i=-2;i<14;i++)'in driver
assert "args:[join(here,'audit-inputs.mjs'),parentIndexSha256]"in driver
assert 'await recheckCollector();'in driver
assert 'STOCK_ONLY_OUTPUTS_SEALED_EXTERNAL_EXIT_ZERO_REQUIRED'in driver
assert 'ROOT_REVIEWED_COMMON_BYTE_THREE_ARMS_FOR_STOCK_ONLY_COMPOSITION_V1'in provenance
assert PROOF_SHA in provenance and PARENT_SHA in provenance
assert 'for(const row of failure.evidence)await readPinned' in provenance
assert 'originalParentRawOuterExit:1,wholeOriginalParentGatePassed:false'in provenance
assert 'ROOT_STOCK_ONLY_COMMON_BYTE_CORRECTNESS_TERMINAL_ZERO_V1'in compose
assert 'COMPOSED_COMMON_BYTE_FOUR_ARM_CORRECTNESS_EVIDENCE'in compose
assert 'rawOuterExit:1,sourceFamilyIndexSha256:parentIndexSha256,wholeParentGatePassed:false'in compose
assert 'unaffectedThreeArmsRerun:false,timingAllowed:false,runtimeAcceptanceClaim:false,performanceClaim:false'in compose
assert "await realpath(terminal.command[0]),await realpath(selectedNode)"in compose
assert "readPinned(terminal.command[0],'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')"in compose
assert "exact(terminal.command.slice(1),[join(here,'run-stock-only.mjs'),indexSha,authorityPath,authoritySha]"in compose
assert 'pairPinsSha256:pairSha256,pairSha256)'not in compose
assert "const linkPath=join(output,'node_modules')"in driver
assert 'outputs,links,requiresIndependentRawOuterExitZero:true'in driver
assert 'complete.links.length,1'in compose and 'await readlink(moduleLink.path),moduleLink.linkText'in compose
assert 'await realpath(moduleLink.path),moduleLink.resolvedTarget'in compose
assert 'await verifyConsumedSeal(parentRoot,parentInputsSha256,null,{invocation:false})'in provenance
receipt=load(OWNER/'source-receipt.json')
assert receipt['sourceChecks']==49 and receipt['syntaxChecks']==7 and receipt['preparationInputs']==9163
assert receipt['driverReversibleHostEdits']==driver_edits==20
assert receipt['actionMainsOrBundlerOrArtifactVerifierOrGuestOrNativeExecuted']is False
for row in load(OWNER/'evidence/syntax-results.json')['checks']:
    if 'status'in row:assert row['status']==0
for row in list(seen.values()):checked(row['path'],row['sha256'],row['bytes'])
result={'schemaVersion':1,'state':'INDEPENDENT_STOCK_GRAPH_AND_COMPOSITION_SOURCE_REVIEW_PASSED','graphIndexSha256':GRAPH_SHA,'companionIndexSha256':OWNER_SHA,'graphFiles':len(g['files']),'companionFiles':len(o['files']),'graphInputRows':graph_inputs,'companionInputRows':owner_inputs,'pathsVerified':len(seen),'graphCheckerReversibleEdits':2,'driverReversibleHostEdits':driver_edits,'bundleRootBindingReversibleEdits':1,'originalGuestSourceIndexSha256':PARENT_SHA,'originalFailedParentRawExit':1,'threeArmProofIndexSha256':PROOF_SHA,'oldThreeArmRecordsChanged':False,'originalGuestProviderSchedulerWorkloadOracleChanged':False,'unconfiguredFutureRootAuthority':True,'stockOnlyExecutionAndLaterCompositionSeparate':True,'oldThreeArmsNotReexecuted':True,'exactStockLauncherExecutableAndOutputLinkClosureRequired':True,'separateCollectorVersusGuestSourceOrigin':True,'wholeOldParentGatePassed':False,'timingAllowed':False,'operationalReadinessClaim':False,'concreteSourceBlockers':[],'readerActions':'Only hashes, JSON/text source inspection and independent exact forward/reverse reconstruction. No owner helpers/tests/action imports, Node syntax/test, bundle, preflight, artifact verifier, compiler, native, guest, hosts or timing.'}
with(HERE/'verified-paths.json').open('x')as dst:json.dump(list(seen.values()),dst,indent=2);dst.write('\n')
with(HERE/'results.json').open('x')as dst:json.dump(result,dst,indent=2);dst.write('\n')
print(json.dumps({'state':result['state'],'paths':len(seen),'driverEdits':driver_edits}))
