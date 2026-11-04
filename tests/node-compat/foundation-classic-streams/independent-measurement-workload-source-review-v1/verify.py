"""Read sealed source/Node-host evidence only. No owner helper or workload run."""
from pathlib import Path
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
PACKET=BASE/'measurement-workload-candidate-v1'
verified={}
def sha(data):return hashlib.sha256(data).hexdigest()
def checked(path,digest=None,size=None):
    path=Path(path);assert path.is_file()and not path.is_symlink(),path
    data=path.read_bytes();assert digest is None or sha(data)==digest,path
    assert size is None or len(data)==size,path
    verified[str(path)]={'path':str(path),'sha256':sha(data),'bytes':len(data)};return data
def doc(path,digest=None):return json.loads(checked(path,digest))
def indexed(path,digest):
    value=doc(path/'index.json',digest)
    for row in value['files']:checked(path/row['path'],row['sha256'],row['bytes'])
    return value
def compact(value):return json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()
def first(left,right,path='$'):
    if type(left)is not type(right):return{'path':path,'node':left,'other':right}
    if isinstance(left,dict):
        if left.keys()!=right.keys():return{'path':path,'nodeKeys':list(left),'otherKeys':list(right)}
        for key in left:
            value=first(left[key],right[key],path+'.'+key)
            if value:return value
    elif isinstance(left,list):
        for i,(a,b)in enumerate(zip(left,right)):
            value=first(a,b,path+'['+str(i)+']')
            if value:return value
        if len(left)!=len(right):return{'path':path+'.length','node':len(left),'other':len(right)}
    elif left!=right:return{'path':path,'node':left,'other':right}
def main():
    assert not(HERE/'results.json').exists()
    index=indexed(PACKET,'39774bbadae98f70e777edb8801ed0ea70d50430f7193f0f4a7fce3630cca41c');assert len(index['files'])==58
    reader=indexed(BASE/'measurement-workload-verification-v1','5c3f917839c5bb4b0ae0354563da02b046cbda2924791f4c2a297aebfa23ed2b')
    manifest=doc(PACKET/'input-freeze.json','dea003e6b395a301e683c572175284b9a508bf7a447a1160c8d6ce688a608654');assert len(manifest['inputs'])==5297
    for row in manifest['inputs']:checked((PACKET/row['path']).resolve(),row['sha256'],row['bytes'])
    producer=indexed(BASE/'measurement-producer-candidate-v1','35ed348529d3b8c1bfa5d57343b784b3c0b5ee442603e570d72a696e45134ebc')
    policy=doc(BASE/'integration-candidate-v1/policy.json','137a35959131d5cb5125bb5fc97324dfa4ba2ce18441818dd95cf83d19c88d6f')
    assert len(policy['expectedNativeSourceManifest'])==342
    for row in policy['expectedNativeSourceManifest']:checked(REPO/row['path'],row['sha256'])
    node=doc(PACKET/'evidence/node-results.json');stock=doc(PACKET/'evidence/stock-results.json');graph=doc(PACKET/'evidence/bundle-results.json')
    assert node['node']=='v22.14.0'and node['iterationBounds']==[1,16]and len(node['expected'])==20
    checked(node['nodeExecutable'],node['nodeExecutableSha256']);assert node['nodeExecutableSha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
    ids=['pipeline-view-64','pipeline-copy-64','pipeline-view-524288','pipeline-copy-524288','fragmented-utf8','object-backpressure','handled-cancellation','checksum-input-only','byte-input-and-copy-construction-only','stream-construction-and-clean-close-only']
    assert[(row['id'],row['iterations'])for row in node['expected']]==[(name,n)for name in ids for n in [1,16]]
    units=dict(zip(ids,[8192,8192,4194304,4194304,48,64,4,8192,4194304,0]))
    def records(value,name,iterations):
        assert value['totalUnits']==units[name]*iterations and value['iterations']==iterations and value['scenario']==name
        assert len(value['records'])==iterations and value['unsignedChecksum']==value['checksum']%(2**32)
        for record in value['records']:
            assert record['units']==units[name]and record['callbacks']<=128 and len(record['events'])<=4096
            if name=='fragmented-utf8':assert ''.join(row[1]for row in record['events']if row[0]=='output-string')=='A¢€😀Z'*8
            if name in ['object-backpressure','handled-cancellation']:assert[row[1]for row in record['events']if row[0]=='output-object']==list(range(units[name]))
            if name.startswith('pipeline-')or name in ['checksum-input-only','byte-input-and-copy-construction-only']:
                assert sum(row[1]for row in record['events']if row[0]=='output-bytes')==units[name]
    for row in node['expected']:records(row['oracle'],row['id'],row['iterations'])
    assert len(node['canonicalHostCounterexamples'])==len(stock['traceCounterexamples'])==14
    assert len(stock['comparisons'])==20
    actual_differences=[]
    for row in node['canonicalHostCounterexamples']:
        expected=node['expected'][row['oracleIndex']];assert(row['id'],row['iterations'])==(expected['id'],expected['iterations'])
        oracle=expected['oracle'];observed=row['observed'];records(observed,row['id'],row['iterations']);assert observed['unsignedChecksum']==oracle['unsignedChecksum']
        assert sha(compact(oracle))==row['oracleTraceSha256']and sha(compact(observed))==row['observedTraceSha256']
        actual_differences.append({'provider':'canonical-with-real-Node-dependencies-and-nextTick','id':row['id'],'iterations':row['iterations'],'oracleIndex':row['oracleIndex'],'checksum':oracle['unsignedChecksum'],'firstDifference':first(oracle,observed)})
    for i,row in enumerate(stock['comparisons']):
        expected=node['expected'][i];assert(row['id'],row['iterations'])==(expected['id'],expected['iterations']);assert not row.get('failed')and row['checksumEqual']
        records(row['observed'],row['id'],row['iterations']);assert row['observed']['unsignedChecksum']==expected['oracle']['unsignedChecksum']
        assert row['exactTraceEqual']==(compact(row['observed'])==compact(expected['oracle']))
        if not row['exactTraceEqual']:actual_differences.append({'provider':'actual-locked-stock-Jco-host-bundle','id':row['id'],'iterations':row['iterations'],'oracleIndex':i,'checksum':expected['oracle']['unsignedChecksum'],'firstDifference':first(expected['oracle'],row['observed'])})
    diffs=doc(PACKET/'first-differences.json');assert diffs['rows']==actual_differences and diffs['canonicalCases']==diffs['stockCases']==14
    for name in ids[-3:]:
        assert not any(row['id']==name for row in node['canonicalHostCounterexamples'])
        assert all(row['exactTraceEqual']for row in stock['comparisons']if row['id']==name)
    assert [row['arm']for row in graph['reports']]==['native','canonical','stock']
    assert [len(row['moduleIds'])for row in graph['reports']]==[3,5,102]
    tools=doc(PACKET/'tool-inputs.json');assert len(tools['inputs'])==4863
    before={row['path']:row for row in graph['sourceInputsCheckedBeforeAfter']+tools['inputs']}
    assert len(graph['sourceInputsCheckedBeforeAfter'])==407
    physical=[]
    for row in graph['reports']:
        checked(row['bundlePath'],row['bundleSha256'],row['bundleBytes']);assert checked(PACKET/'evidence/bundles'/(row['arm']+'.mjs'))==checked(row['bundlePath'])
        for item in row['physicalSources']:
            checked(item['path'],item['sha256'],item['bytes']);assert before[item['path']]['sha256']==item['sha256']and before[item['path']]['bytes']==item['bytes'];physical.append(item)
    assert len(physical)==78
    selected=graph['reports'][2];scheduler=selected['scheduler'];checked(scheduler['path'],scheduler['sha256']);assert scheduler['override']is False and selected['imports']==[]
    process=[row for row in selected['resolutions']if row['request']=='process/'];assert len(process)==7
    assert all(row['result']==scheduler['path']and'/readable-stream/lib/'in row['importer']for row in process)
    assert sum(name.endswith('/stream/scheduler.js')for name in selected['moduleIds'])==1 and selected['moduleIds'].count(scheduler['path'])==1
    assert next(row for row in selected['resolutions']if row['request']=='benchmark:stock-scheduler')['result']==scheduler['path']
    scheduler_text=checked(scheduler['path']).decode();assert'queueMicrotask(flush)'in scheduler_text and'queue.shift()()'in scheduler_text and'const queue = []'in scheduler_text
    source=checked(PACKET/'bundle-source.mjs').decode();assert'nodeBuiltinPlugin({imports:[],exports:[]},{})'in source and'streamSchedulerModule'not in source
    assert graph['stockProviderOptions']=={}and graph['stockSchedulerOverride']is False
    core=checked(REPO/'builtins/node-compat/classic-streams/classic-core.generated.mjs').decode();facade=checked(REPO/'builtins/node-compat/classic-streams/classic-streams.mjs').decode()
    facade=re.sub(r'^export function ','function ',facade.replace("import {createClassicCore} from './classic-core.generated.mjs';\n",''),flags=re.M)
    factory="(function(dependencies){\n'use strict';\n"+re.sub(r'^export function ','function ',core,flags=re.M)+'\n'+facade+'\nreturn createClassicStreams(dependencies);\n})'
    header=checked(REPO/'builtins/node-compat/classic-streams/factories.generated.h').decode();assert header.split('R"SM_NODE_PROFILE(')[1].split(')SM_NODE_PROFILE";')[0]==factory
    assert sha(factory.encode())==graph['canonicalFactorySourceSha256']and graph['canonicalFactoryHeaderExact']
    notices=doc(PACKET/'provider-notices.json')
    for package in notices['packages']:
        metadata=doc(package['metadataPath'],package['metadataSha256']);assert metadata['name']==package['name']and metadata['version']==package['version']and metadata['license']==package['license']
        for notice in package['notices']:assert checked(notice['path'],notice['sha256'],notice['bytes'])==checked(PACKET/notice['copy'],notice['sha256'],notice['bytes'])
    pins=doc(PACKET/'future-pins.json');plan=doc(PACKET/'component-plan.json')
    assert pins['benchmarkClassicOn']is pins['benchmarkClassicOff']is pins['components']is None and pins['timingAllowed']is False
    assert plan['reviewedNativePins']is plan['reviewedComponentPins']is None and plan['currentTimingAllowed']is False and plan['callbackCheckpointLimit']==65536 and plan['budgetMayBeRaised']is False and plan['actualGuestBudgetProof']is False
    workload=checked(PACKET/'workload.mjs').decode()
    for text in ['Exact output byte mismatch','Exact decoded text mismatch','Exact object value/order mismatch','events.length<4096','callbacks<=128','iterations<=16','type:\'undefined\'']:
        assert text in workload,text
    assert not re.search(r'getMemBuffer|WebAssembly\.Memory|performance\.|Date\.|\.now\(',workload)
    assert'JSON.stringify(observed)!==JSON.stringify(oracle)'in checked(PACKET/'run-node.mjs').decode()
    histories=[]
    for name in ['attempt1','attempt2','bundle-attempt1','bundle-attempt2']:
        value=doc(PACKET/'history'/name/'failure.json');assert value['rawExitCode']in [1,134];histories.append({'name':name,**value})
    raw_logs=[];supplement=HERE/'bundle-observer-raw-history';supplement.mkdir(exist_ok=False)
    for attempt in [1,2]:
        for stream in ['stdout','stderr']:
            path=Path('/tmp/starling-node-compat')/('classic-measurement-workload-bundles-v'+str(attempt)+'.'+stream+'.log');data=checked(path)
            target=supplement/path.name
            with target.open('xb')as output:output.write(data)
            raw_logs.append({'original':str(path),'copy':str(target.relative_to(HERE)),'sha256':sha(data),'bytes':len(data)})
    for row in list(verified.values()):checked(row['path'],row['sha256'],row['bytes'])
    result={'schemaVersion':1,'state':'INDEPENDENT_WORKLOAD_SOURCE_REVIEW_NO_BLOCKER_COUNTEREXAMPLES_BLOCK_GUEST_TIMING',
      'sourceIndexSha256':'39774bbadae98f70e777edb8801ed0ea70d50430f7193f0f4a7fce3630cca41c','ownerPostsealReaderIndexSha256':'5c3f917839c5bb4b0ae0354563da02b046cbda2924791f4c2a297aebfa23ed2b',
      'indexedSourceFiles':58,'sourceRows':5297,'pinnedHostToolFiles':4863,'parentSourceBeforeAfterRows':407,'bundleModuleCounts':[3,5,102],'physicalGraphRowsBoundBeforeAfter':78,'physicalUniquePaths':len({r['path']for r in physical}),
      'canonicalHeaderExact':True,'defaultStockSchedulerIdentities':1,'readableStreamProcessResolutions':7,'schedulerSourceAndOptionsUnchanged':True,
      'nodeCases':20,'iterationBounds':[1,16],'canonicalTraceCounterexamples':14,'stockTraceCounterexamples':14,'matchedControlFamilies':3,'canonicalAndStockExactOutputUnitsAndChecksumCases':20,
      'onlineOutputChecksVerifiedInSourceAndSavedData':True,'boundedTracesNoRetainedLargePayloads':True,'actualGuestBudgetProof':False,'futurePinsNull':True,'timingReady':False,
      'actualLiveNativeSourceHashesRechecked':342,'approvedProducerIndexUnchanged':'35ed348529d3b8c1bfa5d57343b784b3c0b5ee442603e570d72a696e45134ebc','approvedProducerIndexedFiles':len(producer['files']),
      'failureHistories':histories,'supplementalRawBundleObserverLogs':raw_logs,
      'nodeHeapFailureRawProvenanceLimit':'Attempts1/2 original stderr was returned only in tool history (sessions2021/17365); no durable raw stdout/stderr files exist. Indexed source snapshots and failure facts were checked; full raw stderr was not independently rehashed or fabricated.',
      'sourceFindings':['Seven ordinary scenarios and three controls share one finite workload; byte/text/object outputs are checked positionally online, full unit counts and checksums are independently consistent with saved data.',
        'Snapshot setup creates fixed unshared offset8 backing windows, bounded UTF8 fragments and64objects. Stream construction/jobs begin inside run. This is source inspection, not actual snapshot proof.',
        'Canonical factory mechanically reproduces the actual installed header; host model uses Node dependencies/nextTick and is not guest/native-queue evidence.',
        'Stock uses the actual empty-options Jco plugin, one canonical physical FIFO scheduler and seven process/ resolutions; explicit workload scheduler identity matches internal streams without source replacement or streamSchedulerModule override.',
        'Both14 trace counterexample sets and typed undefined encoding are retained exactly. Three controls match and are reported without subtraction; no timing/promotion claim follows.',
        'Provider package metadata and available notices are byte-bound; Jco missing top-level notice remains explicitly recorded.',
        'Current bundles are common-entry source graphs, not final component size/import or separate correctness/timing carrier proof. Future actual artifacts, fresh/retained correctness, unchanged65536 budget and coordinated measurement remain mandatory.'],
      'verifiedFiles':list(verified.values()),'reviewerExecutedNodeWorkloadBundleGuestNativeOrHost':False,'runtimeAcceptanceClaim':False}
    with(HERE/'results.json').open('x')as output:json.dump(result,output,indent=2);output.write('\n')
    print(json.dumps({'state':result['state'],'verifiedPaths':len(verified),'resultsSha256':sha((HERE/'results.json').read_bytes())}))
if __name__=='__main__':main()
