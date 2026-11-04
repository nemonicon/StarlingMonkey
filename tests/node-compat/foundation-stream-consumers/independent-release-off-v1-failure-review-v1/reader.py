#!/usr/bin/env python3
"""Read-only retained failure/source/artifact audit; never calls owner code."""
import hashlib,json,os,stat
from pathlib import Path
P=Path(__file__).resolve().parent
S=P.parent
F=S/'release-gates-activated-v2'
O=Path('/tmp/starling-node-compat/production-consumers355-release-gates-v2/release-off-v1')
seen={}
def need(v,m):
 if not v:raise AssertionError(m)
def row(p,e=None):
 p=Path(p);s=p.lstat();need(stat.S_ISREG(s.st_mode),'ordinary final file '+str(p));h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 r=dict(path=str(p),sha256=h.hexdigest(),bytes=s.st_size)
 if e:need(all(r[k]==e[k] for k in ('sha256','bytes')),'exact tuple '+str(p))
 seen[str(p)]=r;return r
def data(p):return json.loads(Path(p).read_text())
def nested(v):
 if isinstance(v,dict):
  if {'path','sha256','bytes'}<=v.keys():row(v['path'],v)
  for x in v.values():nested(x)
 elif isinstance(v,list):
  for x in v:nested(x)
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
def main():
 rp=S/'release-gates-release-off-v1-failure-root-results-v2.json';r=data(rp);row(rp);nested(r)
 prior=Path(r['priorRootReportClarification']['path']);need(row(prior)['sha256']==r['priorRootReportClarification']['sha256'],'prior mislabel receipt preserved')
 need(row(F/'index.json')['sha256']=='562e4236c8f99a34323c57c26f92749dba4aaf3e5dc1a509d33ababd97d79250','actual source family');ix=data(F/'index.json');names=set()
 for x in ix['files']:
  need(x['path'] not in names and not Path(x['path']).is_absolute() and '..' not in Path(x['path']).parts,'safe source index');names.add(x['path']);row(F/x['path'],x)
 parent=data(r['externalTerminal']['path']);controller=data(r['ownedControllerTerminal']['path']);child=data(r['ownedChildTerminal']['path']);need(parent['rawExitCode']==1 and parent['pid']==33623 and not parent['timeout'],'parent raw1 no timeout')
 need(controller['code']==child['code']==1 and controller['signal'] is None and child['signal'] is None and not controller['timeout'] and controller['spawnError'] is None,'controller/selected child1')
 need(all(x['result']=='group-absent' for x in controller['cleanup']),'recorded owned group absent after cleanup')
 batch=data(r['batchReport']['path']);optional=data(r['optionalReport']['path']);need(batch['state']==optional['state']=='failed','failed enclosing reports')
 need([[x['name'],x['code']] for x in batch['jobs']]==r['topJobRawStatuses']==[['core',0],['allocator',0],['stream-web',0],['optional',1]],'actual four top jobs')
 need([[x['name'],x['code']] for x in optional['modules']]==r['optionalModuleRawStatuses']==[['path',0],['events',0],['string-decoder',0],['assert',0],['querystring',0],['util',1]],'actual optional statuses')
 need(batch['reusedResults']==0 and batch['resumeSupported'] is False and batch['sourceFiles']==355,'no resume/prior result adoption')
 reports=[]
 for x in batch['jobs']+optional['modules']:
  need(row(x['runner'])['sha256']==x['runnerSha256'] and row(x['logPath'])['sha256']==x['logSha256'],'recorded runner/log bytes')
  if x['code']==0:
   need(row(x['reportPath'])['sha256']==x['reportSha256'] and row(x['completionPath'])['sha256']==x['completionSha256'],'retained partial completed report/seal')
   reports.append(dict(name=x['name'],report=row(x['reportPath']),completion=row(x['completionPath']),rawStatus=0,independentFullSemanticPassIssuedHere=False))
 need(len(reports)==8,'three top and five optional completed reports only')
 members=[];links=[]
 for p in sorted(O.rglob('*')):
  st=p.lstat()
  if stat.S_ISLNK(st.st_mode):links.append(dict(path=str(p),linkText=os.readlink(p),resolvedTarget=str(p.resolve())));continue
  if stat.S_ISDIR(st.st_mode):continue
  need(stat.S_ISREG(st.st_mode),'ordinary output member');members.append(row(p))
 need(len(members)==195,'observed195 regular output files')
 components=[x for x in members if x['path'].endswith('.component.wasm')];need(len(components)==16,'observed16 actual partial components; no inferred global uniqueness')
 family_context=data(F/'tool-context.json');toolroot=family_context['invocation']['toolchainRoot'];need(all(x['resolvedTarget']==str((Path(toolroot)/'node_modules').resolve()) for x in links),'output links resolve to authenticated tool tree')
 classic=F/'snapshot/tests/node-compat/foundation-classic-streams/production-trace-regression-activated-v1'
 runner=classic/'release/runners/util.mjs';source=runner.read_text();lines=source.splitlines();need('run-native-node.mjs' in lines[38] and 'const sourceFiles=await Promise.all' in lines[38],'line39 explicit late sourceFiles list')
 need(source.index("await h.build('native_util'")<source.index('await instance.run()')<source.index("await h.build('native_util_dynamic'")<source.index('await h.offAdmission(')<source.index('const sourceFiles=await Promise.all'),'actual sequential source ordering before failure')
 need('oracle.sources' not in lines[38] and 'oracle.sources' in lines[11],'separate oracle builtin-source check')
 missing=Path(r['missingSnapshotFile']);need(not missing.exists() and not missing.is_symlink(),'actual missing snapshot datum')
 err=Path(r['utilLog']['path']).read_text();need("code: 'ENOENT'" in err and str(missing) in err and 'util.mjs:39:232' in err,'retained ENOENT final-source-capture stack')
 util=O/'optional/util';need((util/'native_util.component.wasm').is_file() and (util/'native_util_dynamic.component.wasm').is_file(),'actual util main and dynamic components retained')
 need(not (util/'results.json').exists() and not (util/'release-module-admission-complete.json').exists(),'no util completed report/admission seal')
 need(all(not (O/n).exists() for n in r['notStarted']),'four strict stages not started')
 need(not (O/'release-scope-admission-complete.json').exists(),'no whole release completion')
 util_origin=F/'snapshot/tests/node-compat/foundation-util/native-component-results.json';old=data(util_origin);expected=next(x['sha256'] for x in old['sourceFiles'] if x['name']=='run-native-node.mjs')
 frozen=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-util/native-source-freeze-v7/run-native-node.mjs');need(row(frozen)['sha256']==expected=='fe48fc8049fffbc7d60010f617369e498608db6e69cce05dbc4e06ed96a3c4ba','immutable producer data recovery')
 current_oracle=F/'snapshot/tests/node-compat/foundation-util/native-node-results.json';need(row(current_oracle)['sha256']=='489cb9cf4fbe256201f70e385d4326ea32552d2f2a1f187211d9409e73838816','actual current Node oracle remains exact')
 old_oracle=frozen.with_name('native-node-results.json');need(row(old_oracle)['sha256']=='de89a86eb30de6abe994df17a56e29109eb0269f411505b218f579bef62509f5','different older oracle must not replace current oracle')
 result=dict(schemaVersion=1,state='INDEPENDENT_CONSUMERS355_RELEASE_FAILURE_ATTRIBUTION_VERIFIED',finding='CONSUMERS-RELEASE-DATA-CLOSURE-M2',rootReceipt=row(rp),priorRootReceipt=row(prior),actualFamilyIndex=row(F/'index.json'),rootReportedSession=6561,parentRawExitCode=1,selectedChildRawExitCode=1,timeout=False,recordedOwnedGroupAbsent=True,topJobStatuses=r['topJobRawStatuses'],optionalModuleStatuses=r['optionalModuleRawStatuses'],notStarted=r['notStarted'],actualRegularOutputFiles=195,actualOutputLinks=len(links),actualComponentFiles=16,utilComponentizationReached=True,utilRuntimeCallsReachedBySourceControlFlowInference=True,allUtilReturnedValuesIndependentlyRetainedOrDecoded=False,utilPassIssued=False,overallReleasePassIssued=False,partialRuntimePassAdoptionAllowed=False,lateMissingDatum=str(missing),actualFailureList='explicit final sourceFiles array, not oracle.sources',sourceOnlyRecovery=dict(producer=row(frozen),expectedHashAuthority=row(util_origin),currentOracle=row(current_oracle),differentOldOracle=row(old_oracle),producerExecuted=False,oracleRegenerated=False),nativeGuestOrHostActionsRerun=False,operationalAdmission=False,sourcePromotionAllowed=False,performanceClaim=False,sourceIndexedFilesRehashed=len(ix['files']),uniqueInputsRehashed=len(seen))
 write('completed-partial-report-references.json',reports);write('partial-output-membership.json',members);write('output-links.json',links);write('rehashed-inputs.json',[seen[k] for k in sorted(seen)]);write('results.json',result);print(json.dumps(dict(state=result['state'],outputs=len(members),components=len(components),links=len(links),inputs=len(seen))))
if __name__=='__main__':main()
