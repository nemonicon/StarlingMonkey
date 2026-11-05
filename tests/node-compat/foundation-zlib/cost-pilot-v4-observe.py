"""Root read/hash observation of the completed pilot; no worker/helper rerun."""
from pathlib import Path
import hashlib,json,stat
REPO=Path('/Users/dan/dev/StarlingMonkey')
Z=REPO/'tests/node-compat/foundation-zlib'
OUT=Path('/private/tmp/starling-node-compat/zlib-cost-pilot-v4')
EXTERNAL=Path('/private/tmp/starling-node-compat/zlib-cost-pilot-v4-external-root')

def row(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)

def local(name):
 assert isinstance(name,str)and name and not name.startswith('/')and '\\'not in name and '\0'not in name and all(x not in('','.','..')for x in name.split('/'))
 return OUT/name

def main():
 terminal_row=row(EXTERNAL/'terminal.json');terminal=json.loads((EXTERNAL/'terminal.json').read_bytes())
 assert terminal['rawExitCode']==0 and terminal['allObservedOwnedGroupsGone']is True
 assert terminal['timeout']is terminal['forcedCleanup']is False
 assert terminal['signals']==terminal['errors']==terminal['interruptedSignals']==terminal['remainingObservedPids']==[]
 assert terminal['stderr']['bytes']==0
 for r in [terminal['stdout'],terminal['stderr']]:assert row(r['path'])==r
 records=[json.loads(line)for line in Path(terminal['stdout']['path']).read_text().splitlines()]
 assert len(records)==3 and all(r['event']=='codec-phase-operational-heartbeat'and r['partialObservationOnly']is True for r in records[:-1])
 published=records[-1];assert set(published)=={'index','completion'}
 assert published['index']['path']=='index.json'and published['completion']['path']=='completion.json'
 for r in published.values():assert row(local(r['path']))==dict(r,path=str(local(r['path'])))
 index=json.loads((OUT/'index.json').read_bytes());completion=json.loads((OUT/'completion.json').read_bytes())
 assert completion['index']==published['index']and completion['sourceIndexSha256']=='b5b4c9e9279022f63dc72f20bf9a44c831ba277017d9dc72867eafd6a24f89d1'
 assert len(index['files'])==33066
 names=set();total=0;by_name={}
 for r in index['files']:
  assert r['path']not in names;names.add(r['path']);p=local(r['path'])
  assert not p.is_symlink()and stat.S_ISREG(p.stat().st_mode)
  assert row(p)==dict(r,path=str(p));total+=r['bytes'];by_name[r['path']]=r
 actual=set()
 for p in OUT.rglob('*'):
  assert not p.is_symlink()
  if p.is_file():actual.add(p.relative_to(OUT).as_posix())
 assert actual==names|{'index.json','completion.json'}
 assert completion['result']==by_name['results.json']
 result=json.loads((OUT/'results.json').read_bytes());matched=json.loads((OUT/'matched-n-plan.json').read_bytes())
 assert result['phase']=='pilot-candidate'and result['actualWorkers']==892
 assert len(result['origins'])==len(result['observations'])==892 and len(result['calibrations'])==60
 assert result['rawN1ControlOperations']==5352==892*6 and result['codecBatchCalls']==3568==892*4
 assert result['sourceRecheckPassed']is result['allOwnedWorkersRawZeroClean']is True
 assert result['controlsSubtracted']is result['operationalAdmission']is result['runtimeAcceptanceClaim']is result['timingAcceptanceClaim']is False
 pids=set()
 for origin in result['origins']:
  t=json.loads(local(origin['terminal']).read_bytes())
  assert t['status']==0 and t['ownedGroupGone']is t['closed']is True
  assert t['timedOut']is t['outputLimitExceeded']is False
  assert t['signal']is t['spawnError']is t['externalSignal']is None
  assert t['signals']==t['errors']==[]and t['pid']==origin['pid']and t['pid']not in pids
  pids.add(t['pid'])
 comparisons={'same-engine-provider':['native-on','fflate-on'],'unused-profile':['fflate-on','fflate-off']}
 selected={}
 for r in result['calibrations']:
  key=(r['comparison'],r['caseId']);assert key not in selected and r['comparison']in comparisons and 0<=r['caseId']<30
  cap=32768 if r['caseId']<18 else 128
  assert 1<=r['n']<=cap and r['n']&(r['n']-1)==0 and r['targetMs']==50
  assert r['empiricalMatchedN']is True and r['authorizesTiming']is False
  curve=json.loads((OUT/'calibration'/(r['comparison']+'-c'+str(r['caseId'])+'.json')).read_bytes())
  assert curve['selected']==r and [v['n']for v in curve['curve']]==[1<<i for i in range(r['n'].bit_length())]
  for j,c in enumerate(curve['curve']):
   assert c['comparison']==r['comparison']and c['caseId']==r['caseId']and [v['arm']for v in c['arms']]==comparisons[r['comparison']]
   both=all(v['sampleMs']>=50 for v in c['arms']);assert both==(j==len(curve['curve'])-1)
  selected[key]=r
 assert set(selected)=={(c,i)for c in comparisons for i in range(30)}
 assert matched['state']=='ACTUAL_MATCHED_N_PLAN_DATA_V1'and matched['independentReviewStillRequired']is True and len(matched['rows'])==120
 matched_keys=set()
 for r in matched['rows']:
  key=(r['comparison'],r['caseId'],r['arm']);assert key not in matched_keys;matched_keys.add(key)
  assert r['arm']in comparisons[r['comparison']]and r['n']==selected[(r['comparison'],r['caseId'])]['n']
 assert len(matched_keys)==120
 observed=dict(schemaVersion=1,state='ROOT_OBSERVED_CODEC_CALIBRATION_V4_COMPLETE_UNREVIEWED_V1',sourceIndexSha256=result['sourceIndexSha256'],calibrationDecisionSha256=result['calibrationDecisionSha256'],rootAuthority=terminal['authority'],rootConfig=row(Z/'cost-pilot-v4-root-config.json'),externalTerminal=terminal_row,externalStdout=terminal['stdout'],externalStderr=terminal['stderr'],rawOperationalHeartbeats=records[:-1],originalRelativePublicationRows=published,
  actualIndex=row(OUT/'index.json'),completion=row(OUT/'completion.json'),actualResults=row(OUT/'results.json'),matchedNPlan=row(OUT/'matched-n-plan.json'),windowCompletion=row(Z/'cost-pilot-v4-quiet-window-completion.json'),rawParentExitCode=0,rootSession=2880,observedParentPid=terminal['pid'],allObservedOwnedGroupsGone=True,operationalElapsedSeconds=terminal['operationalElapsedSeconds'],indexedFilesRehashed=len(names),indexedBytes=total,actualRegularFiles=len(actual),actualWorkers=892,uniqueWorkerPids=len(pids),calibratedComparisonCases=60,matchedPlanRows=120,pilotN1Controls=5352,pilotCodecBatches=3568,allFirstBothTargetCurvesChecked=True,
  independentPilotReviewRequired=True,rawTypedReturnAndFNVReplayByRoot=False,timingAuthorized=False,performanceConclusion=False,runtimeAcceptanceClaim=False,operationalAdmission=False,reader=row(Path(__file__).resolve()))
 with(Z/'cost-pilot-v4-root-results.json').open('x')as f:f.write(json.dumps(observed,indent=2)+'\n')
 print(json.dumps(dict(result=row(Z/'cost-pilot-v4-root-results.json'),workers=892,calibrations=60,matchedRows=120,indexedFiles=len(names))))

if __name__=='__main__':main()
