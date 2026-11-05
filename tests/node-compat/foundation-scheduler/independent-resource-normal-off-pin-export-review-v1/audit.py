"""Actual export DATA review only; no owner guard/verifier/export/bootstrap import."""
from pathlib import Path
import ast,copy,hashlib,json,stat
O=Path(__file__).resolve().parent;S=O.parent;D=S/'resource-pin-tooling-candidate-v1';checks=[];verified={}
def need(v,label):assert v,label;checks.append(label)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def actual(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def verify(r):
 p=Path(r['path']);physical=Path('/private'+str(p))if str(p).startswith('/tmp/')else p
 need(p.is_absolute()and str(p)==r['path']and '..'not in p.parts,'actual absolute lexical descriptor')
 for q in(physical,*physical.parents):need(not q.is_symlink(),'ordinary descriptor ancestor')
 a=physical.lstat();need(stat.S_ISREG(a.st_mode)and actual(p)=={k:r[k]for k in('path','sha256','bytes')},'exact streamed bytes')
 b=physical.lstat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns),'stable streamed read');verified[str(p)]={k:r[k]for k in('path','sha256','bytes')};return p
def load(p):return json.loads(p.read_bytes())
def family(row):
 p=verify(row);v=load(p);names=set()
 for r in v['files']:
  n=r['path'];need(n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/'))and n not in names,'unique local indexed member');names.add(n);verify(dict(r,path=str(p.parent/n)))
 need(not any(x.is_symlink()for x in p.parent.rglob('*')),'no indexed family symlinks');need({x.relative_to(p.parent).as_posix()for x in p.parent.rglob('*')if x.is_file()}==names|{'index.json'},'whole family exact membership');return len(names)
root_row=dict(path=str(S/'resource-normal-off-pin-export-v1-root-results.json'),sha256='29e20ccfd30da0cad21645130add4d8e2fe7c4494ff5eb50d9ca1d7daa82e769',bytes=4572);root=load(verify(root_row));need(root['rawExporterExitCode']==0,'Root observed export zero')
counts={}
for key,row in [('source',root['toolingIndex']),('sourcePeer',root['sourceReview']['index'])]:counts[key]=family(row)
refs=load(D/'references.json')
for key,row in [('resource',refs['resourceSourceIndex']),('freezer',refs['freezerIndex']),('artifactPeer',refs['actualArtifactReview']['index']),('freezerSourcePeer',refs['freezerSourceReview']['index'])]:counts[key]=family(row)
for r in load(D/'input-freeze.json')['files']:verify(r)
source_peer=load(verify(root['sourceReview']['result']));need(source_peer['state']=='INDEPENDENT_SCHEDULER_RESOURCE342_PIN_TOOLING_SOURCE_REVIEW_PASSED_V1'and source_peer['toolingSourceIndexSha256']==root['toolingIndex']['sha256']and source_peer['sourceOnly']is source_peer['sourceReviewPassed']is True,'actual source-peer exact state and tooling identity')
authority=load(verify(root['rootAuthority']));config=load(verify(root['config']));need(authority['phase']=='export'and authority['state']=='ROOT_REVIEWED_SCHEDULER_RESOURCE342_PIN_TOOLING_PHASE_V1'and authority['exportAllowed']is True,'actual export-only Root scope')
need(config['rootAuthority']==root['rootAuthority']and config['toolingIndex']==root['toolingIndex']==authority['toolingIndex']and config['resourceSourceIndex']==refs['resourceSourceIndex']and config['freezerIndex']==refs['freezerIndex'],'source/config/Root roles agree')
need(authority['sourceIndependentReview']==root['sourceReview']and authority['actualArtifactReview']==refs['actualArtifactReview']and authority['actualArtifactContract']==refs['actualArtifactContract'],'actual source/artifact proof pairs exact')
for key in('bootstrapAllowed','buildAllowed','freezeAllowed','gcReconfigureAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed'):need(authority[key]is False,'unrelated authority remains false '+key)
for key in('actualExportCandidate','independentExportReview','reviewedPins','rootPinReview'):need(authority[key]is None,'no ahead-of-result authority '+key)
family(authority['externalMonitorIndex']);verify(authority['externalController'])
terminal=load(verify(root['externalTerminal']));external=Path(root['externalTerminal']['path']).parent
need({p.name for p in external.iterdir()}=={'started.json','owned-0000.json','stdout.log','stderr.log','terminal.json'}and all(p.is_file()and not p.is_symlink()for p in external.iterdir()),'exact five external evidence files')
for p in external.iterdir():verify(actual(p))
stdout=verify(terminal['stdout']).read_bytes();need(verify(terminal['stderr']).read_bytes()==b'','complete raw exporter stderr empty')
out= json.loads(stdout);need(out==root['exportResult'],'whole raw exporter stdout equals Root embedded record')
need(terminal['rawExitCode']==0 and terminal['timeout']is terminal['forcedCleanup']is False and terminal['parentOwnedGroupGone']is terminal['allObservedOwnedGroupsGone']is True,'authentic external zero/no timeout/forced cleanup')
need(all(terminal[k]==[]for k in('signals','errors','interruptedSignals','remainingObservedPids'))and all(g['alive']is False for g in terminal['finalGroups']),'all captured groups gone and no error/signal')
need(terminal['authority']==root['rootAuthority']and terminal['pid']==44303 and len(terminal['observedProcesses'])==1,'actual observed parent identity and Root authority')
started=load(external/'started.json');owned=load(external/'owned-0000.json');need(started['pid']==terminal['pid']==owned['process']['pid']and owned['process']==terminal['observedProcesses'][0],'raw start/observed/terminal process identities agree')
need(started['argv']==[refs['python']['path'],'-B','-I',str(D/'action.py'),'export',json.dumps(root['config'],separators=(',',':'))]and started['authority']==root['rootAuthority']and started['timeoutSeconds']==authority['externalParentDeadlineSeconds']==600,'exact actual authenticated export command and bound')
candidate=load(verify(root['candidate']));need(root['candidate']==out['candidate']and authority['candidateOutput']==root['candidate']['path'],'actual candidate identity binds stdout/Root')
receipt=load(verify(refs['freezeReceipt']));metadata_bytes=verify(refs['metadata']).read_bytes();metadata=json.loads(metadata_bytes);verify(refs['engine'])
# Source-authenticated extracted pure functions only: no operational module import.
tree=ast.parse((D/'pin_model.py').read_bytes());nodes=[n for n in tree.body if isinstance(n,ast.Assign)or(isinstance(n,ast.FunctionDef)and n.name in('candidate','unreviewed_document'))];env={'copy':copy};exec(compile(ast.Module(body=nodes,type_ignores=[]),'authenticated-extracted-pin-DATA-only','exec'),env)
expected=env['unreviewed_document'](env['candidate'](receipt,metadata,refs,root['toolingIndex']));need(candidate==expected,'whole actual candidate equals exact source-authenticated pure construction')
need(candidate['reviewRequired']is True and set(candidate['variants'])=={'normal-off','normal-runtime','gc-off','disabled-off'}and all(candidate['variants'][n]is None for n in('normal-runtime','gc-off','disabled-off')),'one unreviewed normal-only candidate; other three NULL')
pin=candidate['variants']['normal-off'];need(pin['reviewRequired']is True and pin['state']=='unreviewed-scheduler-resource342-normal-off-freeze-v1','inner review state unchanged')
need(pin['sourceManifest']==metadata['sourceManifest']and len(pin['sourceManifest'])==342 and pin['componentizeSourceManifest']==metadata['componentizeSourceManifest']and len(pin['componentizeSourceManifest'])==3 and pin['selectedModuleManifests']==metadata['selectedModuleManifests']and len(pin['selectedModuleManifests'])==9,'all actual342/3/nine records complete')
need(pin['resourceOwnershipPolicy']==metadata['resourceOwnershipPolicy']and pin['resourceOwnershipPolicy']['nativeRuntimeValidation']is None and pin['classicTraceSourcePolicy']==metadata['classicTraceSourcePolicy'],'untouched source-coupled policy and no invented runtime proof')
need(pin['enginePath']==refs['engine']['path']and pin['metadataPath']==refs['metadata']['path']and metadata['enginePath']!=pin['enginePath'],'genuine frozen selection separate from unchanged original raw metadata enginePath')
freeze=Path(refs['freezeRoot']);need(stat.S_IMODE(freeze.lstat().st_mode)==0o700,'actual private freeze root');copies={};originals=0
for r in receipt['copies']:
 p=verify(r);relative=p.relative_to(freeze).as_posix();need(relative not in copies,'unique frozen copy member');copies[relative]=r;a=p.lstat();need(a.st_nlink==1 and stat.S_IMODE(a.st_mode)==0o600,'ordinary private independent copied inode')
 if r['original']is not None:
  q=verify(r['original']);b=q.lstat();need((a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'copy and original distinct inodes');originals+=1
need(len(copies)==666 and originals==663,'all666 frozen copies plus663 original identities rehashed')
need({p.relative_to(freeze).as_posix()for p in freeze.rglob('*')if p.is_file()}==set(copies)|{'normal-off-freeze-receipt.json'}and not any(p.is_symlink()for p in freeze.rglob('*')),'complete667 frozen membership/no links')
for key,prefix in(('sourceManifest','source'),('componentizeSourceManifest','componentize-source')):
 for r in metadata[key]:need(copies[prefix+'/'+r['path']]['sha256']==r['sha256'],'actual frozen native/external manifest hash')
full_manifests=[]
for r in pin['selectedModuleManifests']:
 c=copies['source/'+r['path']];need(c['sha256']==r['sha256'],'selected manifest exact source hash');m=load(Path(c['path']));need(m['profileVersion']==r['profileVersion'],'full manifest actual profile');full_manifests.append(dict(path=c['path'],sha256=c['sha256'],bytes=c['bytes'],profileVersion=m['profileVersion']))
need(pin['frozenFiles']==[{k:r[k]for k in('path','sha256','bytes')}for r in receipt['copies']],'all666 pin frozen-file descriptors preserved exactly')
target=Path(root['candidate']['path']);s=target.lstat();need(stat.S_IMODE(target.parent.lstat().st_mode)==0o700 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and not target.is_symlink(),'exclusive private candidate actual modes/inode')
need({p.name for p in target.parent.iterdir()}=={target.name},'only intended actual candidate output')
need(sha(Path(refs['metadata']['path']))==refs['metadata']['sha256']and metadata_bytes==Path(refs['metadata']['path']).read_bytes(),'raw metadata bytes remained unchanged')
for key in('engineExecuted','bootstrapExecuted','componentOrGuestExecuted','operationalAdmission','runtimeAcceptanceClaim'):need(root[key]is False,'actual result closed '+key)
need(out['engineExecuted']is out['bootstrapInvoked']is out['operationalAdmission']is out['runtimeAcceptanceClaim']is False and out['requiresIndependentExportAndNewRootValidationPinReview']is True,'raw export result makes no bootstrap/runtime grant')
result=dict(schemaVersion=1,state='INDEPENDENT_ACTUAL_RESOURCE342_PIN_EXPORT_DATA_AUDIT_PASSED',checks=len(checks),familyMemberCounts=counts,uniqueReadHashPaths=len(verified),candidateTopLevelFields=len(candidate),normalPinFields=len(pin),frozenCopies=666,originalsRehashed=663,nativeSourceFiles=342,externalEmbeddingSources=3,selectedManifests=full_manifests,rawExporterExitCode=0,wholeCandidateExact=True,wholeRawStdoutExact=True,rawMetadataUnchanged=True,allObservedOwnedGroupsGone=True,operationalOwnerModuleImported=False,guardActionVerifierExportOrBootstrapInvoked=False,engineComponentGuestNodeProcessRerun=False)
with(O/'audit-results.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
with(O/'input-hashes.json').open('x')as f:json.dump(dict(schemaVersion=1,files=[verified[p]for p in sorted(verified)]),f,indent=2);f.write('\n')
print(json.dumps(result))
