"""Pure/read-only/AST and tiny generic-copy scratch tests; no producer actions."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,stat,sys,tempfile
sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_bytes())
def row(p):
 b=Path(p).read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
checks=[]
def ok(label,value):assert value,label;checks.append(label)
def refuses(label,fn):
 try:fn()
 except(AssertionError,KeyError,ValueError):checks.append(label);return
 raise AssertionError('Did not refuse '+label)
def main():
 refs=read(OWN/'references.json');e=load('inert_own_freezer_entry',OWN/'entry.py');v=load('inert_frozen_only_verifier',OWN/'verify_frozen.py')
 ok('real OWN context',e.OWN==OWN)
 ok('real freeze context',str(e.FREEZE)==str(v.FREEZE)==refs['freezeRoot'])
 ok('corrected a39 proof, not6125',refs['artifactReview']['index']['sha256']=='a39cce0d73a502f89bb6cd1c48289c08d1e6d3e9b2650db5b0fcca6c655af896')
 p,k,rows=e.whole_proof(refs['artifactReview'],refs['artifactContract']);e.artifact_model(p,refs);checks.append('real full proof/coverage consumer accepted a39')
 for name,value in [('originalBuildAccepted',True),('originalBuildPreservationPassed',True),('originalParentExitCodes',[0,0]),('originalRecipeExitCode',1),('publicationVersion',1),('engineExecuted',True)]:
  bad=copy.deepcopy(p);bad[name]=value;refuses('artifact wire wrong '+name,lambda:e.artifact_model(bad,refs))
 bad=copy.deepcopy(p);bad['coverage']['currentLedgerFiles']-=1;refuses('real fixed-contract coverage mutation',lambda:v.fixed_contract(bad,k))
 model=load('inert_copied_P3_83_model',OWN/'metadata_model.py');hm=load('inert_copied_P3_hash_model',OWN/'hash_model.py')
 producer=read(refs['producerReferences']['path']);metadata=read(refs['metadata']['path']);policy=read(producer['policy']['path'])
 observed=model.validate_metadata(metadata,policy,producer['policy']['sha256'],producer['helper']['sha256'],producer['recipe']['sha256'],policy['expectedComponentizeSourceManifest'],'normal-off')
 ok('actual raw83 DATA passes unchanged pure model',observed['nativeFiles']==357 and observed['grantsAuthority']is False)
 selected=[read(Path(refs['configuredSourceRoot'])/d['path'])for d in metadata['selectedModuleManifests']]
 ok('all12 whole manifests actual DATA',hm.validate_selected_manifests(metadata,policy,selected))
 hm.validate_hash_hmac_commands(read(metadata['compileCommandsPath']),metadata['actualEmbeddingCompileCommands'],Path(refs['configuredSourceRoot']),metadata,policy);checks.append('actual69 compile records pure macro/guest-include DATA check')
 for actual in refs['tmpAliasPolicy']['selectedDescriptorPaths']:
  ok('actual selected/tmp mapping '+actual,e.physical(actual)==Path('/private'+actual))
 for path in ['/tmp/another-file','/tmp/starling-node-compat/unknown','/private/tmp/../etc/passwd','//private/tmp/file','relative/file','/private/tmp/a\\b']:
  refuses('path guard refuses '+path,lambda:e.physical(path))
 refuses('frozen-only guard refuses original metadata before open',lambda:v.checked(refs['metadata']))
 refuses('frozen-only guard refuses original engine before open',lambda:v.checked(refs['engine']))
 root=read(OWN/'root-authority.template.json');own=dict(path=str(OWN/'index.json'),sha256='0'*64,bytes=1)
 root.update(freezerIndex=own,freezeAllowed=True,readOnlyProducerAdmissionAllowed=True,frozenOnlyVerificationAllowed=True,ownedCopiesAllowed=True)
 e.root_model(root,own,refs);checks.append('real new freeze phase Root model')
 for key in ['nativeBuildAllowed','ninjaAllowed','gitAllowed','engineExecutionAllowed','cryptoAllowed','gcAllowed','liveEvpSnapshotAdmission','operationalAdmission']:
  bad=copy.deepcopy(root);bad[key]=True;refuses('Root extra permission '+key,lambda:e.root_model(bad,own,refs))
 for key,value in [('originalParentExitCodes',[0,0]),('originalBuildPreservationPassed',True),('originalBuildAccepted',True),('deadlineSeconds',7201)]:
  bad=copy.deepcopy(root);bad[key]=value;refuses('Root bad historical/budget field '+key,lambda:e.root_model(bad,own,refs))
 work=read(refs['workCopyPlan']['path']);paths={r['source']['path']for r in work['files']}
 ok('169 selected WORK witnesses and bounded bytes',len(work['files'])==169 and work['copyBytes']==557901902)
 ok('every actual .a link role selected',set(v.lexical_link_archives(metadata['nodeCryptoHashHmacPolicy']['actualLinkEvidence']['linkArgv'],str(Path(metadata['cmakeCachePath']).parent)))<=paths)
 ok('selected guest libraries include SM and libcrypto',metadata['zlibSelectedCodecInput']['archive']['path']in paths and metadata['openssl']['library']['path']in paths)
 stage=read(refs['stageJournal']['path']);ok('whole stage1642 plus3 historical reference roles',len(stage['copies'])==1642 and len(stage['embeddingDataCompleted'])==3)
 expected={r['path']for r in stage['copies']};ok('all12 manifests present in fullstaged data',all(r['path']in expected for r in metadata['selectedModuleManifests']))
 # The generic copy API has explicit output arguments. This is a tiny owned
 # scratch file, not a native payload or invocation of run/admit/monitor.
 cp=load('own_generic_copy_fchmod_test',OWN/'copy_io.py')
 body=load('own_inert_freeze_pure_ownership',OWN/'freeze.py')
 with tempfile.TemporaryDirectory(prefix='hash357-freeze-copy-',dir='/private/tmp')as t:
  d=Path(t);source=d/'source';source.write_bytes(b'bounded inert copy fixture\n');source.chmod(0o644);output=d/'output';output.mkdir(mode=0o700);old=os.umask(0o077)
  try:
   fd=os.open(output,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
   try:
    held=os.fstat(fd);expected=(held.st_dev,held.st_ino);ok('actual benign root handle ownership model',body.ownership_model(output.stat(),held,expected))
    refuses('root owner wrong identity',lambda:body.ownership_model(output.stat(),held,(held.st_dev,held.st_ino+1)))
    output.chmod(0o755);refuses('root owner wrong mode',lambda:body.ownership_model(output.stat(),held,expected));output.chmod(0o700)
   finally:os.close(fd)
   target=output/'nested/data';plan=[dict(original=source,target=target,sha256=row(source)['sha256'],shared=False)]
   cp.validate_plan(plan,output/'receipt.json',output);cp.execute_plan(plan,output)
   ok('actual generic exclusive copy explicit fchmod600 under077',target.read_bytes()==source.read_bytes()and stat.S_IMODE(target.stat().st_mode)==0o600 and target.stat().st_ino!=source.stat().st_ino)
   refuses('generic copy rejects existing unshared payload',lambda:cp.validate_plan(plan,output/'receipt.json',output))
  finally:os.umask(old)
 for f in OWN.glob('*.py'):ast.parse(f.read_text());checks.append('Python AST '+f.name)
 tree=ast.parse((OWN/'verify_frozen.py').read_text())
 ok('frozen verifier contains no resolve/original helper/command calls',not any(isinstance(n,ast.Attribute)and n.attr in ['resolve','admit','bootstrap','execute_plan','run','check_output']for n in ast.walk(tree)))
 text=(OWN/'freeze.py').read_text();ok('whole fresh return persisted before caller assertions',text.index("whole=json_write('producer-admission-return.json',returned)")<text.index('assert returned=='))
 ok('new callback, no old bootstrap or BUILD facade',"admission.admit(argument,lambda unused:recheck(frame))"in text and "ownIndex=refs['producerIndex']"in text and 'build_proof('not in text)
 ok('frozen-only lexical library paths do not consult originals',v.lexical_link_archives(['../lib/libcrypto.a','/pinned/libSM.a'],'/work/build')==['/work/lib/libcrypto.a','/pinned/libSM.a'])
 for path in [refs['freezeRoot'],refs['externalRoot']]:ok('fresh action root absent '+path,not Path(path).exists()and not Path(path).is_symlink())
 result=dict(schemaVersion=1,state='HASH_HMAC357_FREEZER_SOURCE_DATA_PURE_AST_AND_BENIGN_COPY_TESTS_PASSED_V1',checks=len(checks),checkNames=checks,actualProducerOrAdmissionOrFreezeOrMonitorInvoked=False,compilerEngineGuestCryptoInvoked=False,realBenignGenericCopyInvoked=True,priorMetadataUnchanged=True)
 (OWN/'test-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
