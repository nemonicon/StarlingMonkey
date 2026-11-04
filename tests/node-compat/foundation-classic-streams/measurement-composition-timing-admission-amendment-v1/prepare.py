"""Derive admission-only afterimages. No measurement/action imports or calls."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'measurement-execution-activated-v2'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 raw=value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode()
 with(HERE/name).open('xb')as stream:stream.write(raw)
def derive(source,target,edits):
 before=(PARENT/source).read_text();current=before;proof=[]
 for old,new in edits:
  count=current.count(old);assert count>0,(source,old)
  current=current.replace(old,new);proof.append({'old':old,'new':new,'count':count})
 reverse=current
 for row in reversed(proof):assert reverse.count(row['new'])==row['count'];reverse=reverse.replace(row['new'],row['old'])
 assert reverse==before
 put(target,current.encode());put(target+'.proof.json',{'schemaVersion':1,'beforePath':str(PARENT/source),'beforeSha256':sha(before.encode()),'afterSha256':sha(current.encode()),'edits':proof,'reverseExact':True})
 return before,current
def wrapper(body):
 return """// Only Node built-ins load before exact amendment/parent/collector authentication.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve,relative,isAbsolute,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url)),hash=raw=>createHash('sha256').update(raw).digest('hex');
const worker=process.argv[2]==='--worker'||process.argv[2]==='--calibrate',ownSha=process.argv[worker?3:2];assert(/^[0-9a-f]{64}$/.test(ownSha??''));
async function check(root,digest){const info=await lstat(join(root,'index.json'));assert(info.isFile()&&!info.isSymbolicLink());const raw=await readFile(join(root,'index.json'));assert.equal(hash(raw),digest);const index=JSON.parse(raw);assert.equal(index.schemaVersion,1);const seen=new Set();for(const row of index.files){const path=resolve(root,row.path),name=relative(root,path);assert(name!==''&&name!=='..'&&!name.startsWith('..'+sep)&&!isAbsolute(name)&&!seen.has(name));seen.add(name);const stat=await lstat(path);assert(stat.isFile()&&!stat.isSymbolicLink());const bytes=await readFile(path);assert.equal(hash(bytes),row.sha256);assert.equal(bytes.length,row.bytes);}}
await check(here,ownSha);
await check(resolve(here,'../measurement-execution-activated-v2'),'1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612');
await check(resolve(here,'../measurement-stock-composition-candidate-v1'),'257e3800c86c3d2eb2af9cdebc3ee0421f97b947166e853bb70dc95a188033da');
await import('./"""+body+"""');
"""
def main():
 derive('phase.mjs','phase.mjs',[
  ("from './protocol.mjs'", "from '../measurement-execution-activated-v2/protocol.mjs'"),
  ('ROOT_REVIEWED_COMMON_BYTE_MEASUREMENT_INPUTS_V1','ROOT_REVIEWED_COMPOSED_COMMON_BYTE_MEASUREMENT_INPUTS_V2'),
  ("assert(SHA.test(value.sourceFamilyIndexSha256)&&SHA.test(value.pairPinsSha256));", "assert.equal(value.sourceFamilyIndexSha256,'1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612');assert.equal(value.pairPinsSha256,'f36268516df72ac5b0d5b5ae8fd808d1ce94d40ca364dc533c522fe399b2681e');assert(SHA.test(value.timingAdmissionSourceIndexSha256));assert.equal(value.collectorSourceIndexSha256,'257e3800c86c3d2eb2af9cdebc3ee0421f97b947166e853bb70dc95a188033da');"),
 ])
 before=(PARENT/'measure.mjs').read_text()
 old_correctness=before[before.index("const correctness=JSON.parse"):before.index("for(const record of correctness.records)")]
 common_imports=[(f"from './{name}'",f"from '../measurement-execution-activated-v2/{name}'")for name in ['protocol.mjs','instantiate.mjs','compact-oracle.mjs','collect-worker.mjs','deadline-policy.mjs','runtime-preflight.mjs']]
 _,after=derive('measure.mjs','measure-body.mjs',common_imports+[
  ("const here=dirname(fileURLToPath(import.meta.url)),hash=", "import {parentRoot,parentIndexSha256,verifyTimingSources,auditComposedCorrectness} from './admission.mjs';\nconst admissionHere=dirname(fileURLToPath(import.meta.url)),here=parentRoot,hash="),
  ("assert.equal(hash(sourceIndexRaw),ownSha)","assert.equal(hash(sourceIndexRaw),parentIndexSha256)"),
  ("assert.equal(phase.sourceFamilyIndexSha256,ownSha)","assert.equal(phase.sourceFamilyIndexSha256,parentIndexSha256);assert.equal(phase.timingAdmissionSourceIndexSha256,ownSha)"),
  ("async function auditPhase(){assert.equal", "async function auditPhase(){await verifyTimingSources(admissionHere,ownSha);await auditComposedCorrectness(phase,ownSha);assert.equal"),
  ("hash(await readFile(join(here,'index.json'))),ownSha", "hash(await readFile(join(here,'index.json'))),parentIndexSha256"),
  (old_correctness,"const correctness=await auditComposedCorrectness(phase,ownSha);\n"),
  ("for(const record of correctness.records)","for(const {record} of correctness.records)"),
  ("collectWorker(fileURLToPath(import.meta.url)","collectWorker(join(admissionHere,'measure.mjs')"),
  ("collectWorker(join(here,'audit-inputs.mjs')", "collectWorker(join(admissionHere,'audit-inputs.mjs')"),
  ('sourceIndexSha256:ownSha','sourceIndexSha256:parentIndexSha256,timingAdmissionSourceIndexSha256:ownSha,collectorSourceIndexSha256:phase.collectorSourceIndexSha256'),
 ])
 worker_before=before[before.index('if(worker){'):before.index('}else{\n const on=')]
 worker_after=after[after.index('if(worker){'):after.index('}else{\n const on=')]
 assert worker_before==worker_after
 pilot_before=before[before.index('  for(const comparison of comparisons)'):before.index(' }catch(error){failure=error;')]
 pilot_after=after[after.index('  for(const comparison of comparisons)'):after.index(' }catch(error){failure=error;')]
 assert pilot_before==pilot_after
 put('timing-body-identity.json',{'schemaVersion':1,'workerBodySha256':sha(worker_before.encode()),'workerBodyBytes':len(worker_before.encode()),'pilotAndSamplingLoopSha256':sha(pilot_before.encode()),'pilotAndSamplingLoopBytes':len(pilot_before.encode()),'bothByteIdenticalToParent':True,'protocolChanged':False,'deadlinePolicyChanged':False,'calibrationOrSampleCountsChanged':False})
 audit=(PARENT/'audit-inputs.mjs').read_text();start=audit[audit.index("const here=dirname"):audit.index("const {executionPreflight}")]
 derive('audit-inputs.mjs','audit-body.mjs',[
  ("{fileURLToPath}","{fileURLToPath,pathToFileURL}"),
  (start,"import {parentRoot,parentIndexSha256,verifyTimingSources,auditComposedCorrectness} from './admission.mjs';\nimport {selectTimingPhase} from './phase.mjs';\nconst here=parentRoot,admissionHere=dirname(fileURLToPath(import.meta.url)),hash=raw=>createHash('sha256').update(raw).digest('hex');\nconst[indexSha,phasePath,phaseSha]=process.argv.slice(2);await verifyTimingSources(admissionHere,indexSha);\n"),
  ("await import('./runtime-preflight.mjs')","await import(pathToFileURL(join(here,'runtime-preflight.mjs')))"),
  ("const phase=JSON.parse(bytes);assert.equal(phase.sourceFamilyIndexSha256,indexSha);", "const phase=selectTimingPhase(JSON.parse(bytes));assert.equal(phase.sourceFamilyIndexSha256,parentIndexSha256);assert.equal(phase.timingAdmissionSourceIndexSha256,indexSha);await auditComposedCorrectness(phase,indexSha);"),
  ("sourceFamilyIndexSha256:indexSha", "sourceFamilyIndexSha256:parentIndexSha256,timingAdmissionSourceIndexSha256:indexSha"),
 ])
 put('measure.mjs',wrapper('measure-body.mjs').encode());put('audit-inputs.mjs',wrapper('audit-body.mjs').encode())
 future=json.loads((PARENT/'future-measurement-phase.json').read_bytes());future['state']='UNCONFIGURED_COMPOSED_COMMON_BYTE_TIMING_PHASE_V2';future['sourceFamilyIndexSha256']='1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612';future['timingAdmissionSourceIndexSha256']=None;future['collectorSourceIndexSha256']='257e3800c86c3d2eb2af9cdebc3ee0421f97b947166e853bb70dc95a188033da';put('future-measurement-phase.json',future)
 print(json.dumps({'sourceAfterimages':3,'timingWorkerAndPilotBodiesUnchanged':True,'actionExecuted':False}))
if __name__=='__main__':main()
