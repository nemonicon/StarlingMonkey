"""Read/hash/JSON/arithmetic only. Never execute owner code or artifacts."""
from pathlib import Path
import csv,hashlib,json,math,os,statistics
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ADOPTION=BASE/'production-adoption-v1'
OUT=Path('/tmp/starling-node-compat/production-common-byte-process-rss-supplement-v2')
SOURCE=BASE/'measurement-memory-probe-candidate-v2'
SOURCE_SHA='6b0b82df31d13d530ce1541ccedcecb1fa99573f7671aa1b48b97c3bd682def0'
ROOT_SHA='203b7e6b7b1bee8675bc52280c7b30fb8b8da82461e4e5b9167535862fd08be5'
REPORT_SHA='606346356502ed8824b54677f825cdccec2bc8d48a4e23c34558384e18b8367f'
PHASE_SHA='a822a7b02e0b81aae15504dd90d439be789c884336bfab7a7eddcccc0aec6890'
witnesses={};cache={};checks=[]
COMPARISONS=[('same-engine-binding',['native-on','canonical-on']),('whole-profile',['canonical-on','canonical-off']),('different-stock-provider',['canonical-on','stock-on'])]
SNAPSHOTS=['bootstrap-before-descriptor','pre-critical-file-hash','post-critical-file-hash','after-compile-and-binding-load','after-instantiate','after-identity','after-identity-and-probe','after-small-setup','after-small','after-large-setup','after-large','after-final-probe','after-final-critical-file-hash']
STAGES=['compile-and-binding-load','instantiate','first-identity-export','first-checkpoint-probe','small-setup','small-single-batch','large-setup','large-single-batch','final-checkpoint-probe']
CALLS=[('identity','identity',[]),('probe-before','checkpointProbe',[]),('small-setup','setup',[1]),('small-batch','batch',[1,1]),('large-setup','setup',[5]),('large-batch','batch',[5,1]),('probe-after','checkpointProbe',[])]
def sha(path):
    info=path.stat();key=(info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns)
    if key not in cache:
        h=hashlib.sha256()
        with path.open('rb')as f:
            for block in iter(lambda:f.read(1048576),b''):h.update(block)
        after=path.stat();assert key==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
        cache[key]=h.hexdigest()
    return cache[key]
def row(path,expected=None,size=None):
    path=Path(path);assert path.is_file()and not path.is_symlink(),path
    digest=sha(path);count=path.stat().st_size
    if expected is not None:assert digest==expected,path
    if size is not None:assert count==size,path
    witnesses[str(path)]={'path':str(path),'sha256':digest,'bytes':count};return witnesses[str(path)]
def load(path,expected=None,size=None):row(path,expected,size);return json.loads(Path(path).read_bytes())
def check(name,condition):assert condition,name;checks.append(name)
def packet(root,expected):
    data=load(root/'index.json',expected)
    for r in data['files']:row(root/r['path'],r['sha256'],r['bytes'])
    return data
def put(name,data):
    with(HERE/name).open('x')as f:json.dump(data,f,indent=2);f.write('\n')
def csvput(name,data):
    with(HERE/name).open('x',newline='')as f:
        writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
def finite(value):return type(value)in(int,float)and math.isfinite(value)
def compact(oracle,index):
    one=oracle[index-index%2]['expected'];assert one['iterations']==1 and len(one['records'])==1
    sample=one['records'][0];value=2166136261
    for operand in[sample['checksum'],sample['units']]:value=((value^(operand&0xffffffff))*16777619)&0xffffffff
    return{'result':{'scenario':one['scenario'],'iterations':1,'checksum':value if value<0x80000000 else value-0x100000000,'unsignedChecksum':value,'totalUnits':one['totalUnits'],'scheduledCallbacks':one['scheduledCallbacks'],'records':[]}}
def main():
    root=load(ADOPTION/'process-rss-supplement-v2-root-results.json',ROOT_SHA)
    check('RootObservedParentTerminalZero',root['rawExitCode']==0 and root['workerCount']==18 and root['coordinatedWindowEnded']is True)
    closure=load(root['outputClosure']['path'],root['outputClosure']['sha256'],root['outputClosure']['bytes'])
    check('exact599RegularZeroLinkClosure',closure['regularFiles']==599 and len(closure['files'])==599 and closure['links']==[]and closure['rawExitCode']==0)
    for item in closure['files']:row(item['path'],item['sha256'],item['bytes'])
    actual_files=set()
    for parent,dirs,names in os.walk(OUT,followlinks=False):
        assert all(not(Path(parent)/name).is_symlink()for name in dirs)
        for name in names:
            path=Path(parent)/name;assert path.is_file()and not path.is_symlink();actual_files.add(str(path))
    check('closureMatchesEveryActualOutputFile',actual_files=={item['path']for item in closure['files']})
    for item in root['references']+root['workerTerminals']:row(item['path'],item['sha256'],item['bytes'])
    report=load(OUT/'results.json',REPORT_SHA,159786);completion=load(OUT/'completion.json')
    check('completion598PlusSelfMatches599',len(completion['files'])==598 and {r['path']for r in completion['files']}==actual_files-{str(OUT/'completion.json')}and completion['links']==[])
    for item in completion['files']:row(item['path'],item['sha256'],item['bytes'])
    check('actualReportStateAndPostAudit',report['state']=='PUBLIC_PROCESS_RSS_SUPPLEMENT_OBSERVED_EXTERNAL_EXIT_ZERO_REQUIRED'and report['workerCount']==18 and report['postAudit']=={'passed':True,'ownInputsCount':10348})
    check('separateDurablePostAudit',load(OUT/'post-operation-source-audit.json')==report['postAudit'])
    check('source22StillMatchesReviewedProposal',len(packet(SOURCE,SOURCE_SHA)['files'])==22)
    packet(BASE/'independent-memory-probe-v2-source-review-v1','73fa279b3d5c9b363330716f7bf77d7a0f9360a3144f23f5ecbbcc0fcfa6ca6e')
    authority=load(report['authority']['path'],report['authority']['sha256']);check('actualV2AuthoritySameSourceAndPhase',authority['state']=='ROOT_REVIEWED_COMMON_BYTE_PROCESS_RSS_SUPPLEMENT_V2'and authority['sourceIndexSha256']==SOURCE_SHA and authority['memorySupplementAllowed']is True and authority['throughputReplacement']is False)
    phase=load(authority['phase']['path'],PHASE_SHA)
    for name in['timingReport','timingRootReceipt','integrityIndex']:row(authority[name]['path'],authority[name]['sha256'])
    check('phaseAndOldThroughputIdentityRemainSeparate',report['phaseSha256']==PHASE_SHA and report['timingReportSha256']=='eded2bdba1703712682fab9a0c8e93dd6a80a5551b3b6c727028729df62f1f65'and report['throughputProtocolChanged']is False and report['throughputClaim']is False)
    terminal=load('/tmp/starling-node-compat/common-byte-process-rss-supplement-v2.terminal.json')
    check('parentExternalTerminalMatchesReceipt',terminal['rawExitCode']==0 and terminal['parentPid']==root['parentPid']and terminal['sourceIndexSha256']==SOURCE_SHA and terminal['authoritySha256']==report['authority']['sha256']and terminal['error']is None)
    old=BASE/'measurement-execution-activated-v2';oldindex=load(old/'index.json','1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612')
    oracle=[]
    for name in['node-common-oracle.json','node-control-oracle.json']:
        r=next(r for r in oldindex['files']if r['path']==name);oracle+=load(old/name,r['sha256'],r['bytes'])['cases']
    expected_batches={index:compact(oracle,index)for index in[1,5]}
    check('pinnedNodeExpectedSetupAndUnits',oracle[1]['setup']==151852933 and oracle[5]['setup']==-1502831163 and expected_batches[1]['result']['totalUnits']==8192 and expected_batches[5]['result']['totalUnits']==4194304)
    self_manifest=load(OUT/'worker-self-manifest.json')
    check('workerSelfManifestBoundedThreeFiles',self_manifest['sourceIndexSha256']==SOURCE_SHA and len(self_manifest['files'])==3 and(OUT/'worker-self-manifest.json').stat().st_size<=4096)
    for item in self_manifest['files']:row(item['path'],item['sha256'],item['bytes'])
    expected_schedule=[]
    for comparison,pair in COMPARISONS:
        for rep in range(3):
            order=pair[::-1]if rep==1 else pair
            for position,arm in enumerate(order):expected_schedule.append((comparison,rep,position,arm,order))
    observations=report['observations'];check('eighteenOrderedFreshObservations',len(observations)==len(expected_schedule)==18)
    pids=set();types={'number':0,'string':0};workers=[];raw_metrics=[];control_metrics=[];consistency=[]
    for item,scheduled in zip(observations,expected_schedule):
        comparison,rep,position,arm,order=scheduled;actual=item['actual'];label=comparison+'.rep-'+str(rep)+'.'+arm
        assert(item['comparison'],item['repetition'],item['position'],item['arm'],item['runOrder'])==(comparison,rep,position,arm,order)
        assert item['label']==label and item['workerOutput']==str(OUT/'workers'/label)
        descriptor=load(item['descriptor']['path'],item['descriptor']['sha256'],item['descriptor']['bytes']);assert item['descriptorSha256']==item['descriptor']['sha256']and item['descriptor']['bytes']<=16384
        assert descriptor['sourceIndexSha256']==SOURCE_SHA and descriptor['parentPhaseSha256']==PHASE_SHA
        assert(descriptor['comparison'],descriptor['repetition'],descriptor['position'],descriptor['arm'],descriptor['runOrder'])==(comparison,rep,position,arm,order)
        for f in descriptor['criticalFiles']:row(f['path'],f['sha256'],f['bytes'])
        record=phase['components'][arm];assert descriptor['component']=={'path':record['componentPath'],'sha256':record['componentSha256'],'bytes':record['componentBytes']}
        assert descriptor['modulePath']==record['modulePath']and descriptor['coreFiles']==record['coreFiles']
        t=load(item['terminalPath']);pid=t['pid'];assert type(pid)is int and pid>0 and pid not in pids and pid!=root['parentPid'];pids.add(pid)
        assert t['status']==0 and t['signal']is None and t['timedOut']is False and t['closed']is True and t['ownedGroupGone']is True and t['terminalExitZeroObserved']is True and t['spawnError']is None and t['externalSignal']is None and t['errors']==[]and t['signals']==[]and t['outputLimitExceeded']is False and t['timeoutMs']==600000
        assert t['args']==[str(SOURCE/'worker.mjs'),str(OUT/'worker-self-manifest.json'),sha(OUT/'worker-self-manifest.json'),item['descriptor']['path'],item['descriptor']['sha256'],item['workerOutput']]
        row(t['executable'],'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
        stdout=load(t['stdout']['path'],t['stdout']['sha256'],t['stdout']['bytes']);assert stdout==actual
        row(t['stderr']['path'],t['stderr']['sha256'],t['stderr']['bytes'])
        assert load(Path(item['workerOutput'])/'result.json')==actual
        assert load(OUT/(label+'.observed.json'))==actual
        assert actual['state']=='SMALL_PUBLIC_PROCESS_RSS_WORKER_OBSERVED'and actual['freshProcessPid']==pid and actual['sourceIndexSha256']==SOURCE_SHA and actual['descriptorSha256']==item['descriptor']['sha256']
        assert all(actual[k]==item[k]for k in['comparison','arm','repetition','runOrder','position'])
        assert actual['publicCalls']==7 and actual['iterationsEach']==1 and actual['caseOrder']==[1,5]and len(actual['rawReturns'])==7
        assert actual['capacityBytes']is None and actual['growCount']is None and actual['guestHeapBytes']is None
        assert actual['component']==descriptor['component']and actual['nativeEvidence']==descriptor['nativeEvidence']
        expected=[record['identity'],record['checkpointProbe'],oracle[1]['setup'],expected_batches[1],oracle[5]['setup'],expected_batches[5],record['checkpointProbe']]
        assert [s['stage']for s in actual['snapshots']]==SNAPSHOTS and [s['stage']for s in actual['stages']]==STAGES
        for s in actual['snapshots']:assert type(s['rssBytes'])is int and s['rssBytes']>0 and finite(s['elapsedSinceEntryMs'])and s['elapsedSinceEntryMs']>=0
        assert [s['elapsedSinceEntryMs']for s in actual['snapshots']]==sorted(s['elapsedSinceEntryMs']for s in actual['snapshots'])
        for s in actual['stages']:assert finite(s['elapsedMs'])and s['elapsedMs']>=0
        for i,(call,(call_label,name,args),value)in enumerate(zip(actual['rawReturns'],CALLS,expected)):
            assert(call['label'],call['publicExport'],call['arguments'])==(call_label,name,args)
            assert load(Path(item['workerOutput'])/('raw-'+call_label+'.json'))==call
            assert call['elapsedMs']==actual['stages'][i+2]['elapsedMs']and finite(call['elapsedMs'])and call['elapsedMs']>=0
            assert type(call['rssBytes'])is int and call['rssBytes']>0
            if name=='setup':assert call['rawReturnType']=='number'and type(call['rawReturn'])is int and -2147483648<=call['rawReturn']<=2147483647 and call['rawReturn']==value;types['number']+=1
            else:assert call['rawReturnType']=='string'and type(call['rawReturn'])is str and json.loads(call['rawReturn'])==value;types['string']+=1
        assert load(Path(item['workerOutput'])/'baselines.json')==actual['snapshots'][:3]
        progress=[json.loads(line)for line in Path(t['stderr']['path']).read_text().splitlines()];expected_progress=['before-compile-and-binding-load','compiled','instantiated']+[s for label,_,_ in CALLS for s in['before-'+label,'returned-'+label]]
        assert [v['stage']for v in progress]==expected_progress
        for i,entry in enumerate(progress):assert load(Path(item['workerOutput'])/(str(i+1).zfill(2)+'-'+entry['stage']+'.json'))==entry
        rss={s['stage']:s['rssBytes']for s in actual['snapshots']};before=actual['maxRssBeforeFinalHashKilobytes'];after=actual['terminalMaxRssKilobytes']
        assert type(before)is int and type(after)is int and 0<before<=after
        sampled_before=max([s['rssBytes']for s in actual['snapshots'][:-1]]+[c['rssBytes']for c in actual['rawReturns']]);sampled_all=max(sampled_before,rss['after-final-critical-file-hash'])
        consistency.append({'label':label,'prefinalMaxKiBCoversSampledRss':before*1024>=sampled_before,'terminalMaxKiBCoversSampledRss':after*1024>=sampled_all})
        metrics={**{'rss.'+s['stage']:('bytes',s['rssBytes'])for s in actual['snapshots']},**{'sinceEntry.'+s['stage']:('ms',s['elapsedSinceEntryMs'])for s in actual['snapshots']},**{'stage.'+s['stage']:('ms',s['elapsedMs'])for s in actual['stages']},**{'rawCallRSS.'+c['label']:('bytes',c['rssBytes'])for c in actual['rawReturns']},'maxRSS.beforeFinalHash':('KiB',before),'maxRSS.terminal':('KiB',after),'worker.elapsed':('ms',item['wholeProcessElapsedMs'])}
        controls={'hashIntervalRssChange':('bytes',rss['post-critical-file-hash']-rss['pre-critical-file-hash']),'smallIntervalRssChange':('bytes',rss['after-small']-rss['after-identity-and-probe']),'largeAfterSmallRssChange':('bytes',rss['after-large']-rss['after-small']),'finalHashIntervalRssChange':('bytes',rss['after-final-critical-file-hash']-rss['after-final-probe']),'finalHashMaxRssChange':('KiB',after-before),'sampledPeakBeforeFinalHash':('bytes',sampled_before),'sampledPeakAll':('bytes',sampled_all)}
        workers.append({'comparison':comparison,'repetition':rep,'position':position,'arm':arm,'pid':pid,'label':label,'wholeProcessElapsedMs':item['wholeProcessElapsedMs'],'maxBeforeFinalHashKiB':before,'terminalMaxKiB':after,**{'rss_'+s['stage']:s['rssBytes']for s in actual['snapshots']}})
        for metric,(unit,value)in metrics.items():raw_metrics.append({'comparison':comparison,'repetition':rep,'arm':arm,'pid':pid,'metric':metric,'unit':unit,'value':value})
        for metric,(unit,value)in controls.items():control_metrics.append({'comparison':comparison,'repetition':rep,'arm':arm,'pid':pid,'metric':metric,'unit':unit,'value':value})
    check('18DistinctFreshPidsOrderedABBAAB',len(pids)==18)
    check('126ExactTypedPublicReturns',types=={'number':36,'string':90})
    check('all18TerminalsZeroCleanupAndRawReplicaChecks',True)
    check('all7RawCallsAnd17ProgressRecordsPerWorker',True)
    check('publicMaximumUnitsConsistentWithSampledByteRss',all(all(v is True for k,v in r.items()if k!='label')for r in consistency))
    summary=[]
    for kind,data in[('raw',raw_metrics),('control-not-subtracted',control_metrics)]:
        groups={}
        for r in data:groups.setdefault((r['comparison'],r['arm'],r['metric'],r['unit']),[]).append(r['value'])
        for key,values in sorted(groups.items()):
            assert len(values)==3;comparison,arm,metric,unit=key
            summary.append({'kind':kind,'comparison':comparison,'arm':arm,'metric':metric,'unit':unit,'nProcesses':3,'min':min(values),'median':statistics.median(values),'max':max(values)})
    ratios=[]
    for comparison,pair in COMPARISONS:
        selected=[r for r in raw_metrics if r['comparison']==comparison]
        for rep in range(3):
            a={r['metric']:r for r in selected if r['arm']==pair[0]and r['repetition']==rep};b={r['metric']:r for r in selected if r['arm']==pair[1]and r['repetition']==rep}
            for metric in sorted(a):
                if b[metric]['value']==0:continue
                ratios.append({'comparison':comparison,'repetition':rep,'order':'AB'if rep!=1 else'BA','A':pair[0],'B':pair[1],'metric':metric,'unit':a[metric]['unit'],'Avalue':a[metric]['value'],'Bvalue':b[metric]['value'],'AoverB':a[metric]['value']/b[metric]['value']})
    ratio_summary=[]
    for comparison,pair in COMPARISONS:
        for metric in sorted({r['metric']for r in ratios if r['comparison']==comparison}):
            values=[r['AoverB']for r in ratios if r['comparison']==comparison and r['metric']==metric]
            ratio_summary.append({'comparison':comparison,'A':pair[0],'B':pair[1],'metric':metric,'nPairs':len(values),'minAoverB':min(values),'medianAoverB':statistics.median(values),'maxAoverB':max(values)})
    csvput('workers.csv',workers);csvput('all-raw-metrics.csv',raw_metrics);csvput('controls-not-subtracted.csv',control_metrics);csvput('summary.csv',summary);csvput('paired-ratios.csv',ratios);csvput('paired-ratio-summary.csv',ratio_summary)
    put('numeric-reconstruction.json',{'schemaVersion':1,'state':'INDEPENDENT_PUBLIC_PROCESS_COST_ARITHMETIC_RECONSTRUCTED','summary':summary,'pairedRatioSummary':ratio_summary,'unitConsistency':consistency,'ratios':'A/B per same comparison/repetition; below1 means smaller A for that metric. No significance inference.','controlsSubtracted':False,'withinWorkerStagesCorrelated':True,'throughputReanalysed':False,'guestHeapOrCapacityClaim':False})
    put('byte-witnesses.json',{'schemaVersion':1,'files':sorted(witnesses.values(),key=lambda r:r['path'])})
    put('results.json',{'schemaVersion':1,'state':'INDEPENDENT_PROCESS_RSS_SUPPLEMENT_V2_RESULTS_VERIFIED','checks':checks,'passed':len(checks),'RootReceiptSha256':ROOT_SHA,'reportSha256':REPORT_SHA,'sourceIndexSha256':SOURCE_SHA,'regularOutputFiles':599,'outputLinks':0,'freshWorkerPids':sorted(pids),'workers':18,'typedReturns':types,'publicCalls':126,'source10348PostAuditVerifiedAsDurableData':True,'source10348PriorIndependentProofByHash':True,'full10348SourceRerunByThisReader':False,'statisticsProcessReplicatesPerArmComparison':3,'noIndependentStagePooling':True,'all600sDeadlinesMetInThisObservedRunOnly':True,'failedV1RemainsRaw1':True,'old168WorkerThroughputReportUnchangedAndSeparate':True,'controlsSubtracted':False,'nativeGuestHostParentWorkerOrPreflightRerun':False,'productionPromotionArchiveAcceptanceOrUniversalMemoryWinClaim':False})
    print(json.dumps({'checks':len(checks),'files':599,'workers':18,'typedReturns':types,'numericSummaryRows':len(summary),'pairedRatioRows':len(ratios),'witnessPaths':len(witnesses),'reruns':False}),flush=True)
if __name__=='__main__':main()
