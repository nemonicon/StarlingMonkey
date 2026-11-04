"""Source/reversal reader only; no action or command-collection helper import."""
from pathlib import Path
import ast,hashlib,json,sys
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'measurement-execution-candidate-v1'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
 assert len(sys.argv)==2;output=Path(sys.argv[1]);assert str(output).startswith('/tmp/starling-node-compat/')and not output.exists();output.mkdir(parents=True,exist_ok=False)
 checks=[]
 def check(name,value=True):assert value,name;checks.append(name)
 raw=(BASE/'index.json').read_bytes();check('immutable4b6 index',sha(raw)=='4b6fdfa51d41120865114b0e8558dbc6e97fdd63007e108a35c264d20bc0280d')
 for row in json.loads(raw)['files']:assert sha((BASE/row['path']).read_bytes())==row['sha256']
 check('all43 original indexed bytes unchanged')
 helper_root=HERE.parent/'measurement-correctness-persistence-amendment-v1';raw=(helper_root/'index.json').read_bytes();check('bounded persistence helper parent sealed60a',sha(raw)=='60a8687e9b6bfff4c68df2a36e9dd47ad0f5cd327441f8cf32d63caa67518ba8')
 for row in json.loads(raw)['files']:assert sha((helper_root/row['path']).read_bytes())==row['sha256']
 check('35 helper parent rows unchanged inherited17host checks not replayed')
 proof=json.loads((HERE/'owned-host-derivation.json').read_bytes());before=(helper_root/'durable-host.mjs').read_text();after=(HERE/'owned-host.mjs').read_text()
 assert sha(before.encode())==proof['beforeSha256']and sha(after.encode())==proof['afterSha256'];s=before
 for e in proof['edits']:assert s.count(e['old'])==e['count'];s=s.replace(e['old'],e['new'])
 assert s==after
 for e in reversed(proof['edits']):assert s.count(e['new'])==e['count'];s=s.replace(e['new'],e['old'])
 check('owned helper only permitted ceiling delta and exact reverse',s==before and len(proof['edits'])==1)
 check('owned group TERM KILL ESRCH and bounded reap retained',all(v in after for v in["detached:true","process.kill(-pid","error.code==='ESRCH'","signal('SIGTERM')","signal('SIGKILL')","const ceiling=timeoutMs+2*graceMs+1000","process.removeListener('SIGTERM'"]))
 check('structured terminal persists before owned helper return',after.index('await persistFile({output,write,path:terminalPath')<after.index('return{...outcome,terminalPath'))
 proof=json.loads((HERE/'activation-derivation.json').read_bytes());source=(BASE/'activate.py').read_text();before=source
 for e in proof['edits']:assert source.count(e['old'])==e['count'];source=source.replace(e['old'],e['new'])
 check('concrete activation five edits exact',source==(HERE/'activate.py').read_text()and len(proof['edits'])==5)
 for e in reversed(proof['edits']):assert source.count(e['new'])==e['count'];source=source.replace(e['new'],e['old'])
 check('activation exact reverse to4b6',source==before)
 host=json.loads((HERE/'host-derivations.json').read_bytes())
 for row in host['files']:
  a=(BASE/row['path']).read_text();b=(HERE/'proposed'/row['path']).read_text();assert sha(a.encode())==row['beforeSha256']and sha(b.encode())==row['afterSha256'];aa=a.splitlines(keepends=True);bb=b.splitlines(keepends=True);forward=[];reverse=[]
  for tag,i,j,k,l in row['opcodes']:forward.extend(aa[i:j]if tag=='equal'else bb[k:l]);reverse.extend(bb[k:l]if tag=='equal'else aa[i:j])
  assert ''.join(forward)==b and ''.join(reverse)==a
 check('all three full host afterimages reverse exactly',len(host['files'])==3)
 source=(HERE/'activate.py').read_text();check('mandatory4b6 plus own amendment authenticated before verifier',source.index('base_rows=indexed(BASE,BASE_INDEX)')<source.index("spec_from_file_location('benchmark_common'"))
 check('new output only and mandatory amendment receipt',"measurement-execution-activated-v2"in source and "'mandatoryDeadlineAmendmentIndexSha256':own_sha"in source)
 check('all26 old payloads copied before host-only overrides','payload={name:regular(BASE/name)for name in names}'in source and"for name in['prepare-correctness.mjs','collect-worker.mjs','measure.mjs']"in source)
 check('authority parser byte exact no new positive pins',(HERE/'authority.py').read_bytes()==(BASE/'authority.py').read_bytes())
 driver=(HERE/'proposed/prepare-correctness.mjs').read_text();wt=driver[driver.index('const wt=[];'):]
 check('no old55s sync Wasmtime collection','spawnSync'not in driver and'timeout:55000'not in driver)
 check('WT terminal source persistence before exit assertions',wt.index('await runOwnedCommand(')<wt.index("'fresh-Wasmtime-collected'")<wt.index('assert.equal(actual.terminalExitZeroObserved'))
 check('WT observed full value before validation',wt.index("'.observed.json'")<wt.index('await requireExactJSON'))
 observe=driver[driver.index('async function observeCall'):driver.index('async function identity')]
 check('Jco raw and full observed persisted before return',observe.index("'.raw.txt'")<observe.index("'.observed.json'")<observe.index('return value'))
 check('case progress includes arm index call scenario iterations','scenario:index===null?null:cases[index].id'in driver and"'fresh-Wasmtime-start'"in driver and'deadlineMs:deadlinePolicy.publicCaseMs'in driver)
 check('all14cases three rotations fresh no skip',all(v in driver for v in['i<14','round<3','rotation(fresh,1)','i=-2;i<14']))
 for line in(BASE/'prepare-correctness.mjs').read_text().splitlines():
  if 'const wit='in line or 'assert.deepEqual(exports,'in line or 'const expectedIdentity='in line:assert line in driver
 check('WIT world imports and provider identity contract unchanged')
 check('initial2GiB and800MiB guards cover correctness afterimage','initialDisk.bavail*initialDisk.bsize>=2*1024**3'in driver and'disk.bavail*disk.bsize>=800*1024**2'in driver)
 check('failure persisted before source audit and original retained',driver.index("'failure-before-source-audit.json'")<driver.index("name:'post-operation-source-audit'")and'if(!operationFailure)operationFailure=auditError;else'in driver)
 measure=(HERE/'proposed/measure.mjs').read_text();check('pilot count sample counts and source oracles unchanged',all(v in measure for v in['samples.length,126','calibrations.length,21','row.batchMs.length,7','repetition<3','chooseBatch(pilots[0].firstBatchMs,pilots[1].firstBatchMs)']))
 check('derived budget serialized before refusal and workers',measure.index("'.budget-plan.json'")<measure.index("assert(Object.values(budgets)")<measure.index("child('--worker'"))
 check('no cap clamp or N change on inadequate deadline','budgets[arm].requestedMs'in measure and'workerBudget(row,iterations)'in measure and'no clipping or N change'in measure)
 check('raw pilot and worker parsed values saved immediately',"label+'.observed.json'"in measure)
 check('bounded source audit preserves original failure',"collectWorker(join(here,'audit-inputs.mjs')"in measure and'originalFailure,sourceAuditFailure,auditTerminalPath'in measure)
 collect=(HERE/'proposed/collect-worker.mjs').read_text();check('explicit deadline no fixed300s timer','timeout:300000'not in collect and'timeoutMs:deadlineMs'in collect and'outcome.terminalExitZeroObserved&&outcome.ownedGroupGone'in collect)
 audit=(HERE/'audit-inputs.mjs').read_text();check('postfailure child source-only no guest API imports',audit.index('hash(raw),indexSha')<audit.index("await import('./runtime-preflight.mjs')")and'exports.'not in audit)
 witness=(HERE/'public-case5-deadline-witness.json').read_bytes();check('exact Root793 case5 witness',sha(witness)=='793a2f0de42b931fac12c55c570a888add9ced3c2e9b25b09e8bef70363ce45e')
 for path in HERE.glob('*.py'):ast.parse(path.read_text());check('Python AST '+path.name)
 future=HERE.parent/'measurement-execution-activated-v2';check('new output absent',not future.exists()and not future.is_symlink()and not future.with_name(future.name+'.staging').exists())
 result={'schemaVersion':1,'state':'SOURCE_PERSISTENCE_AND_MANDATORY_ACTIVATION_AMENDMENT_CHECKS_PASSED','passed':len(checks),'checks':checks,'ownerCommandsOrProbesOrActionMainsOrArtifactVerifiersOrGuestOrTimingExecuted':False,'inherited17BenignHostChecksAuthenticatedOnly':True}
 (output/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':len(checks),'output':str(output)}))
if __name__=='__main__':main()
