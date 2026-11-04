"""Read-only timing integrity/provenance reader. No owner or benchmark actions."""
from pathlib import Path
from collections import Counter
from datetime import datetime
import hashlib,json,os,re,stat,math
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;ADOPTION=FAMILY/'production-adoption-v1'
OUTPUT=Path('/tmp/starling-node-compat/production-common-byte-composed-timing-v1')
SOURCE=FAMILY/'measurement-execution-activated-v2';SOURCE_SHA='1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612'
ADMISSION=FAMILY/'measurement-composition-timing-admission-amendment-v1';ADMISSION_SHA='78b3e5a0e3389f3d347a9b5700852361aae59cdbdc26813d9ff290f8ddf3e538'
COLLECTOR=FAMILY/'measurement-stock-composition-candidate-v1';COLLECTOR_SHA='257e3800c86c3d2eb2af9cdebc3ee0421f97b947166e853bb70dc95a188033da'
PHASE_SHA='a822a7b02e0b81aae15504dd90d439be789c884336bfab7a7eddcccc0aec6890'
WINDOW_SHA='82c941b25bbece67c93f318025e8fed451e630158fe33e48877393ab3fc57506'
seen={};identities={}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path,h=None,size=None,capture=True,force=False):
 path=Path(path);a=path.lstat();assert stat.S_ISREG(a.st_mode)and not path.is_symlink(),path
 path=path.resolve(strict=True);key=str(path);identity=(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)
 if not capture and not force and key in seen:
  assert identities[key]==identity,path;row=seen[key];assert h is None or row['sha256']==h,path;assert size is None or row['bytes']==size,path;return row
 digest=hashlib.sha256();blocks=[]if capture else None
 with path.open('rb')as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):
   digest.update(block)
   if capture:blocks.append(block)
 b=path.stat();assert identity==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns),path
 assert h is None or digest.hexdigest()==h,path;assert size is None or b.st_size==size,path
 row={'path':key,'sha256':digest.hexdigest(),'bytes':b.st_size};assert key not in seen or seen[key]==row,path;seen[key]=row;identities[key]=identity
 return b''.join(blocks)if capture else row
def doc(path,h=None):return json.loads(read(path,h))
def encoded(value):return(json.dumps(value,indent=2)+'\n').encode()
def indexed(root,digest,count=None):
 value=doc(root/'index.json',digest);assert count is None or len(value['files'])==count;names=set()
 for row in value['files']:
  name=row['path'];assert name not in names and not Path(name).is_absolute()and all(p not in('','.','..')for p in name.split('/'));names.add(name);read(root/name,row['sha256'],row['bytes'],False)
 return value
assert not(HERE/'results.json').exists()
root=doc(ADOPTION/'common-byte-composed-timing-root-results-v1.json','fc51ab670f64745453f5a23fb399b9e8ea36a7327ed05460e618505922bd5e55');assert root['rawExitCode']==0 and root['timedWorkers']==126 and root['calibrationWorkers']==42
for row in root['references']:read(row['path'],row['sha256'],row['bytes'],False)
outer=doc(root['references'][0]['path']);assert outer['rawExitCode']==0 and outer['selectedEnvironment']['NODE_COMPAT_COMMON_BYTE_TIMING_APPROVED']=='1'
phase_path=ADOPTION/'reviewed-composed-timing-phase-v1.json';phase=doc(phase_path,PHASE_SHA);window=doc(ADOPTION/'composed-timing-window-root-review-v1.json',WINDOW_SHA)
assert phase['timingAllowed']is True and phase['coordinatedWindow']==window['coordinatedWindow']=='ROOT_EXPLICIT_SINGLE_MEASUREMENT_WINDOW'
candidate=doc(window['candidate']['path'],window['candidate']['sha256']);assert sorted(k for k in phase if phase[k]!=candidate[k])==['coordinatedWindow','state','timingAllowed']
assert phase['sourceFamilyIndexSha256']==SOURCE_SHA and phase['timingAdmissionSourceIndexSha256']==ADMISSION_SHA and phase['collectorSourceIndexSha256']==COLLECTOR_SHA
assert outer['argv'][1:]==[str(ADMISSION/'measure.mjs'),ADMISSION_SHA,str(phase_path),PHASE_SHA]
closure=doc(ADOPTION/'common-byte-composed-timing-output-closure-v1.json','adaff03059c935da603a1314c67c9aeaed3b1941964765430caa236f8fc31b3a');assert len(closure['regularOutputFiles'])==1037 and closure['outputLinks']==[]
for row in closure['regularOutputFiles']:read(row['path'],row['sha256'],row['bytes'],False)
physical=[]
for directory,dirs,files in os.walk(OUTPUT,followlinks=False):
 for name in dirs+files:
  path=Path(directory)/name;assert not path.is_symlink(),path
  if path.is_file():physical.append(str(path))
assert set(physical)=={row['path']for row in closure['regularOutputFiles']}
report=doc(OUTPUT/'results.json','eded2bdba1703712682fab9a0c8e93dd6a80a5551b3b6c727028729df62f1f65');assert report['state']=='COMMON_BYTE_THREE_COMPARISON_TIMING_COMPLETE'and len(report['samples'])==126 and len(report['calibrations'])==len(report['summaries'])==21
protocol={'freshProcessesPerArmCaseComparison':3,'warmups':3,'samples':7,'maxIterations':16,'comparisons':3,'commonCorrectnessCases':8,'controlCorrectnessCases':6,'measurementFamilies':7,'timedWorkerProcesses':126,'calibrationWorkers':42,'totalWorkerProcesses':168,'calibrationTargetMs':25,'guestImports':[],'schedulerBudgetRaised':False}
assert report['protocol']==phase['protocol']==protocol and report['controlsSubtracted']is False
for path,digest,count in[(SOURCE,SOURCE_SHA,35),(ADMISSION,ADMISSION_SHA,22),(COLLECTOR,COLLECTOR_SHA,20)]:
 indexed(path,digest,count);freeze=doc(path/'input-freeze.json')
 for row in freeze['inputs']:read(path/row['path'],row['sha256'],row['bytes'],False)
 for tree in freeze.get('toolTrees',[]):
  members=[];toolroot=Path(tree['path'])
  for directory,dirs,files in os.walk(toolroot,followlinks=False):
   for name in sorted(dirs+files):
    target=Path(directory)/name;kind='symlink'if target.is_symlink()else'directory'if target.is_dir()else'file'if target.is_file()else None;assert kind;members.append({'path':str(target.relative_to(toolroot)),'kind':kind})
    if kind=='file':read(target,capture=False)
   dirs[:]=[name for name in dirs if not(Path(directory)/name).is_symlink()]
  assert sorted(members,key=lambda row:row['path'])==tree['entries']
 for row in freeze.get('toolLinks',[]):assert os.readlink(row['path'])==row['linkText']and str(Path(row['path']).resolve(strict=True))==row['resolvedTarget']
for row in window['sourceAndReviewReferences']:read(row['path'],row['sha256'],row['bytes'],False)
for prerequisite in window['prerequisites']:
 for key in['report','rootReview']:
  row=prerequisite[key];read(row['path'],row['sha256'],row['bytes'],False)
 review=doc(prerequisite['rootReview']['path']);assert review['state']=='ROOT_REVIEWED_COMMON_BYTE_PREREQUISITE_V1'and review['reviewedPassed']is True and review['performanceClaim']is False

# Preserve the composition boundary and each actual origin, including raw1 parent.
composition=doc(phase['actualCorrectness']['reportPath'],phase['actualCorrectness']['reportSha256']);assert composition['state']=='COMPOSED_COMMON_BYTE_FOUR_ARM_CORRECTNESS_EVIDENCE'and len(composition['records'])==4
assert composition['failedParent']['rawOuterExit']==1 and composition['failedParent']['wholeParentGatePassed']is False and composition['unaffectedThreeArmsRerun']is False
failed=doc(composition['failedParent']['receiptPath'],composition['failedParent']['receiptSha256']);assert failed['rawOuterExit']==1 and failed['wholeFourArmGatePassed']is False
origins=[]
for i,entry in enumerate(composition['records']):
 origin=entry['origin'];original=doc(origin['recordPath'],origin['recordSha256']);read(origin['recordPath'],origin['recordSha256'],origin.get('recordBytes'),False)
 if i<3:assert origin['originalParentRawOuterExit']==1 and origin['wholeOriginalParentGatePassed']is False and original==entry['record']
 else:assert origin['rawOuterExit']==0 and original['records'][0]==entry['record']
 rec=entry['record'];selected=phase['components'][rec['arm']]
 for key in['arm','componentPath','componentSha256','componentBytes','enginePath','engineSha256','modulePath','bundleSha256','transpiledFiles','coreFiles','identity','checkpointProbe']:assert selected[key]==rec[key]
 origins.append({'arm':rec['arm'],**origin})
composition_review=doc(phase['actualCorrectness']['rootReviewPath'],phase['actualCorrectness']['rootReviewSha256']);assert composition_review['origins']==origins
proof=composition_review['compositionProof']
for name in['terminal','completion','stdout','stderr','independentProofIndex','independentProofResult','stockIndependentProofIndex','stockIndependentProofResult']:
 row=proof[name];read(row['path'],row['sha256'],row['bytes'],False)
assert doc(proof['terminal']['path'])['returncode']==0
for name in['independentProofIndex','stockIndependentProofIndex']:row=proof[name];indexed(Path(row['path']).parent,row['sha256'])
pair=doc(SOURCE/'reviewed-pair.json','f36268516df72ac5b0d5b5ae8fd808d1ce94d40ca364dc533c522fe399b2681e');pair_review=doc(SOURCE/'root-pair-review.json','2bfa334981d1fc63ae05280fcb0c2afb9d8ea22e5e1451ae796d7c756479950e')
native_counts={}
for variant,pin in pair['variants'].items():
 assert len(pin['frozenFiles'])==525
 for row in pin['frozenFiles']:read(row['path'],row['sha256'],row['bytes'],False)
 frozen=Path(pin['freezeRoot']);receipt=doc(frozen/(variant+'-freeze-receipt.json'),pin['freezeReceiptSha256']);meta=doc(frozen/(variant+'.engine.wasm.build.json'),pin['metadataSha256'])
 assert len(receipt['copies'])==525 and receipt['nativeInputsVerified']==342 and receipt['addonInputsVerified']==2 and receipt['externalEmbeddingInputsVerified']==3 and len(meta['sourceManifest'])==342
 for row in receipt['copies']:read(row['path'],row['sha256'],row['bytes'],False)
 read(frozen/(variant+'.engine.wasm'),pin['engineSha256'],pin['engineBytes'],False)
 assert receipt['diagnosticOnly']is True and receipt['productionSelectorRefused']is True and receipt['classicStreamsEnabled']==(variant=='benchmark-classic-on')
 native_counts[variant]={'frozenCopies':525,'nativeSourceRows':342,'addonRows':2,'externalEmbeddingRows':3,'engineSha256':pin['engineSha256']}
component_audits=[]
for arm,rec in phase['components'].items():
 component=read(rec['componentPath'],rec['componentSha256'],rec['componentBytes']);read(rec['enginePath'],rec['engineSha256']);read(rec['enginePath']+'.build.json',rec['engineMetadataSha256'])
 for file in rec['transpiledFiles']:read(Path(rec['modulePath']).parent/file['name'],file['sha256'],file['bytes'],False)
 assert len(rec['coreFiles'])==1;core=read(Path(rec['modulePath']).parent/rec['coreFiles'][0]);assert component.find(core)==13
 wit=read(HERE/(arm+'.fresh.wit')).decode();assert not re.search(r'\bimport\b',wit);exports=set(re.findall(r'export\s+([\w-]+):\s*(func\([^;]+);',wit));assert exports=={('setup','func(index: u32) -> s32'),('inspect','func(index: u32) -> string'),('batch','func(index: u32, iterations: u32) -> string'),('identity','func() -> string'),('checkpoint-probe','func() -> string')}
 matches=[]
 for path in Path(rec['componentPath']).parent.glob('*.mjs'):
  if sha(read(path))==rec['bundleSha256']:matches.append(str(path))
 assert len(matches)==1
 glue=read(rec['modulePath']).decode();assert rec['coreFiles'][0]in glue and 'instantiate' in glue
 component_audits.append({'arm':arm,'componentSha256':rec['componentSha256'],'coreExactOffset':13,'bundlePath':matches[0],'imports':[],'publicScalarExports':5})
assert phase['components']['native-on']['engineSha256']==phase['components']['canonical-on']['engineSha256']==phase['components']['stock-on']['engineSha256']!=phase['components']['canonical-off']['engineSha256']
assert phase['components']['canonical-on']['bundleSha256']==phase['components']['canonical-off']['bundleSha256']
assert 'createClassicStreams({...dependencies,events,AbortSignal,AbortController,disposeSymbol:Symbol.dispose,asyncDisposeSymbol:Symbol.asyncDispose})'in read(SOURCE/'canonical-provider.mjs').decode()
assert "from 'starling:test-classic-benchmark'"in read(SOURCE/'native-provider.mjs').decode()and"from 'benchmark:stock-scheduler'"in read(SOURCE/'stock-provider.mjs').decode()

# Worker contract and expected compact values; actual batch returns were NOT retained.
body=read(ADMISSION/'measure-body.mjs').decode();assert 'exact(first,index,iterations)'in body and 'exact(await invoke(),index,iterations)'in body and 'exact(value,index,iterations)'in body
assert body.index('elapsed=performance.now()-start')<body.index('exact(value,index,iterations)')and "for(let i=0;i<3;i++)"in body and 'sample<7'in body
oracle=doc(SOURCE/'node-common-oracle.json')['cases']+doc(SOURCE/'node-control-oracle.json')['cases'];assert len(oracle)==14
comparisons=[('same-engine-binding',['native-on','canonical-on']),('whole-profile',['canonical-on','canonical-off']),('different-stock-provider',['canonical-on','stock-on'])];indices=[1,3,5,7,9,11,13]
families=['pipeline-view-64-hwm-plus1','pipeline-copy-64-hwm-plus1','pipeline-view-524288-hwm-plus1','pipeline-copy-524288-hwm-plus1','checksum-input-only','byte-input-and-copy-construction-only','stream-construction-and-clean-close-only']
def compact(index,n):
 one=oracle[index-index%2]['expected'];assert one['iterations']==len(one['records'])==1;record=one['records'][0];value=2166136261
 for i in range(n):
  value=((value^(record['checksum']&0xffffffff))*16777619)&0xffffffff;value=((value^(record['units']&0xffffffff))*16777619)&0xffffffff
 return{'result':{'scenario':one['scenario'],'iterations':n,'checksum':value if value<2**31 else value-2**32,'unsignedChecksum':value,'totalUnits':one['totalUnits']*n,'scheduledCallbacks':one['scheduledCallbacks']*n,'records':[]}}
def budget(pilot,n):
 first=pilot['firstBatchMs'];whole=pilot['wholeProcessElapsedMs'];work=first*n*10;startup=max(0,whole-first);allowance=120000+2*startup;requested=math.ceil(2*work+first*n+allowance)
 return{'iterations':n,'pilotIterationMs':first,'pilotWholeProcessMs':whole,'sampleAndWarmupMs':work,'firstBatchAllowanceMs':first*n,'observedStartupAndEvidenceMs':startup,'startupAllowanceMs':allowance,'workSafetyFactor':2,'requestedMs':requested,'hardMaxMs':7200000,'admitted':requested<=7200000}
def same_budget(actual,expected):
 for key,wanted in expected.items():
  if type(wanted)is float:assert math.isclose(actual[key],wanted,rel_tol=1e-12,abs_tol=1e-9),(key,actual[key],wanted)
  else:assert actual[key]==wanted,(key,actual[key],wanted)
nodes=[];expected_values=[];worker_checks=[];pids=[]
def worker_row(comparison,index,arm,label,mode,n,wrapped,deadline):
 name=label.replace('.','_');terminal=doc(OUTPUT/'processes'/(name+'.terminal.json'));launch=doc(OUTPUT/'processes'/(name+'.launch.json'))
 assert terminal['status']==0 and terminal['signal']is terminal['spawnError']is terminal['externalSignal']is None and terminal['timedOut']is terminal['outputLimitExceeded']is False
 assert terminal['closed']is terminal['ownedGroupGone']is terminal['terminalExitZeroObserved']is True and terminal['signals']==terminal['errors']==[]and terminal['timeoutMs']==deadline
 args=[str(ADMISSION/'measure.mjs'),mode,ADMISSION_SHA,str(phase_path),PHASE_SHA,arm,str(index),str(n)];assert terminal['args']==launch['args']==args and launch['detachedOwnedSession']is True and launch['timeoutMs']==deadline
 pids.append(terminal['pid']);nodes.append({'name':name,'pid':terminal['pid'],'startedAtUtc':launch['startedAtUtc'],'args':args,'status':0,'deadlineMs':deadline})
 for stream in['stdout','stderr']:read(terminal[stream]['path'],terminal[stream]['sha256'],terminal[stream]['bytes'],False)
 value=doc(terminal['stdout']['path']);assert value==doc(OUTPUT/(label+'.observed.json'))and {key:val for key,val in wrapped.items()if key not in['comparison','repetition','caseIndex','runOrder','wholeProcessElapsedMs','collection']}==value
 assert wrapped['collection']['terminalPath']==str(OUTPUT/'processes'/(name+'.terminal.json'))and wrapped['wholeProcessElapsedMs']==terminal['operationalElapsedMs']
 assert value['arm']==arm and value['index']==index and value['iterations']==n and value['calibration']==(mode=='--calibrate')
 assert value['scenario']=={'id':families[index//2],'control':index//2>=4,'iterations':1 if mode=='--calibrate'else 16}
 assert value['identity']==phase['components'][arm]['identity']and value['checkpointProbe']==value['afterCheckpointProbe']==phase['components'][arm]['checkpointProbe']
 assert value['capacityBytes']is value['growCount']is value['requestedMemoryHostLimitBytes']is None and value['componentBytes']==phase['components'][arm]['componentBytes']
 expected=compact(index,n);assert value['unitsPerBatch']==expected['result']['totalUnits']
 for key in['firstBatchMs','compileAndBindingLoadMs','instantiateMs','firstIdentityExportMs','setupMs']:assert math.isfinite(value[key])and value[key]>=0
 markers=[json.loads(line)for line in read(terminal['stderr']['path']).decode().splitlines()if line]
 stages=[('compile',0),('calibration-one-iteration'if mode=='--calibrate'else'first-batch',1),('first-complete',1)]
 if mode=='--worker':stages+=[('warmup',i)for i in range(1,4)]+[('timed-sample',i)for i in range(1,8)]
 assert [(row['stage'],row['call'])for row in markers]==stages and all(row['arm']==arm and row['index']==index and row['iterations']==n for row in markers)
 assert len(value['batchMs'])==(0 if mode=='--calibrate'else 7)and all(math.isfinite(x)and x>=0 for x in value['batchMs'])
 expected_labels=['ready','first-batch']+([]if mode=='--calibrate'else['warmed']+['sample-'+str(i)for i in range(7)])
 assert [row['label']for row in value['observations']]==expected_labels
 expected_values.append({'comparison':comparison,'label':label,'arm':arm,'index':index,'iterations':n,'expectedCompact':expected,'actualBatchReturnRetained':False,'authenticatedSourceGuardAndTerminalOnly':True})
 worker_checks.append({'label':label,'mode':mode,'warmupMarkers':0 if mode=='--calibrate'else 3,'sampleMarkers':len(value['batchMs']),'unitsPerBatch':value['unitsPerBatch']})
sample_index=0;calibration_index=0
for comparison,arms in comparisons:
 for index in indices:
  cal=report['calibrations'][calibration_index];calibration_index+=1;assert cal['comparison']==comparison and cal['caseIndex']==index and [row['arm']for row in cal['pilots']]==arms
  assert cal==doc(OUTPUT/f'{comparison}.case-{index}.budget-plan.json')
  chosen=max(1,min(16,math.floor(25/max(row['firstBatchMs']for row in cal['pilots']))));assert cal['chosenIterations']==chosen and cal['requestedMaximum']==16 and cal['targetBatchMs']==25
  for pilot in cal['pilots']:
   arm=pilot['arm'];label=f'{comparison}.case-{index}.calibration.{arm}';worker_row(comparison,index-1,arm,label,'--calibrate',1,pilot,600000)
   same_budget(cal['budgets'][arm],budget(pilot,chosen));assert cal['budgets'][arm]['admitted']is True
  for repetition in range(3):
   order=arms if repetition%2==0 else list(reversed(arms))
   for arm in order:
    row=report['samples'][sample_index];sample_index+=1;assert row['comparison']==comparison and row['caseIndex']==index and row['repetition']==repetition and row['runOrder']==order and row['arm']==arm
    assert row['collection']['budget']==cal['budgets'][arm];label=f'{comparison}.case-{index}.rep-{repetition}.{arm}';worker_row(comparison,index,arm,label,'--worker',chosen,row,cal['budgets'][arm]['requestedMs'])
assert sample_index==126 and calibration_index==21 and len(worker_checks)==168 and len(set(pids))==168
assert [node['startedAtUtc']for node in nodes]==sorted(node['startedAtUtc']for node in nodes)
terminals=list((OUTPUT/'processes').glob('*.terminal.json'));assert len(terminals)==169
audit=doc(OUTPUT/'processes/post-operation-source-audit.terminal.json');assert audit['status']==0 and audit['ownedGroupGone']is audit['terminalExitZeroObserved']is True and audit['timeoutMs']==180000
assert audit['args']==[str(ADMISSION/'audit-inputs.mjs'),ADMISSION_SHA,str(phase_path),PHASE_SHA]
for stream in['stdout','stderr']:read(audit[stream]['path'],audit[stream]['sha256'],audit[stream]['bytes'],False)
assert len(set(pids+[audit['pid']]))==169
audit_report=doc(OUTPUT/'terminal-source-audit.json');assert audit_report['passed']is True and audit_report['successfulTimedWorkers']==126 and audit_report['completedCalibrationPairs']==21 and audit_report['originalFailure']is audit_report['sourceAuditFailure']is audit_report['error']is None
static=doc(HERE/'static-audits.json');read(static['tool']['path'],static['tool']['sha256'],static['tool']['bytes'],False)
with(HERE/'expected-compact-contracts.json').open('x')as stream:json.dump({'scope':'Expected values only, independently recomputed from pinned Node one-iteration oracles. Actual timing batch returns were not retained.','workers':expected_values},stream,indent=2);stream.write('\n')
with(HERE/'worker-integrity-ledger.json').open('x')as stream:json.dump({'sourceSupportedExactGuardCount':42+126*11,'actualCompactBatchReturnsRetained':False,'workers':worker_checks,'chronologicalLaunches':nodes},stream,indent=2);stream.write('\n')
for row in list(seen.values()):read(row['path'],row['sha256'],row['bytes'],False,True)
r={'schemaVersion':1,'state':'INDEPENDENT_COMPOSED_TIMING_INTEGRITY_PROVENANCE_PASSED','rootReceiptSha256':'fc51ab670f64745453f5a23fb399b9e8ea36a7327ed05460e618505922bd5e55','reportSha256':'eded2bdba1703712682fab9a0c8e93dd6a80a5551b3b6c727028729df62f1f65','outputClosureSha256':'adaff03059c935da603a1314c67c9aeaed3b1941964765430caa236f8fc31b3a','regularOutputFilesRehashed':1037,'rootReportedOuterExit':0,'pastRootTerminalObservedByThisReader':False,'issuedPhaseSha256':PHASE_SHA,'issuedWindowSha256':WINDOW_SHA,'sourceFamilyIndexSha256':SOURCE_SHA,'timingAdmissionIndexSha256':ADMISSION_SHA,'collectorIndexSha256':COLLECTOR_SHA,'pilotsDecoded':42,'timedWorkersDecoded':126,'freshWorkerPids':168,'terminalsIncludingPostAudit':169,'comparisons':3,'families':7,'order':'AB/BA/AB, exact chronological168 worker launch order','warmupsPerTimedWorker':3,'correlatedSamplesPerTimedWorker':7,'sharedIterationsRecalculated':True,'operationalBudgetsRecalculatedWithoutClipping':True,'allRawStdoutObservedAndReportRowsAgree':True,'identityAndBeforeAfterProbeObservationsVerified':True,'expectedCompactValuesIndependentlyRecomputed':True,'actualPerBatchCompactValuesRetained':False,'independentlyDecodedActualPerBatchChecksumsClaim':False,'sourceGuardAndSuccessfulTerminalSupportedExactChecks':1428,'checksumEvidenceScope':'Authenticated worker exact() checks execute after first,3warmups,7samples before stdout, but actual per-call batch return values were not retained. Separate raw308 correctness remains distinct.','capacityAndGrowCountsObserved':False,'rssOnly':True,'nativeFrozenVariants':native_counts,'componentAudits':component_audits,'compositionOrigins':origins,'originalFailedParentRawExitPreserved':1,'wholeFailedParentRelabelledPassed':False,'quietWindowScope':'Root-issued coordinated window; not independent proof of desktop/frequency/thermal/background isolation.','controlsSubtracted':False,'numericalInterpretationPerformedByThisReader':False,'ownerHelpersPreflightsNodePackageGuestNativeHostOrBenchmarkActionsExecuted':False,'staticArtifactWitExtractionOnly':True,'runtimeAcceptanceClaim':False,'heapOrReuseOrFullNodeOrCppStateMachineClaim':False,'performanceSignificanceClaim':False,'verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(r,stream,indent=2);stream.write('\n')
print(json.dumps({'state':r['state'],'outputs':1037,'workers':168,'terminals':169,'verifiedPaths':len(seen),'rawChecksumLimitation':True}))
