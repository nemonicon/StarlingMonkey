"""Independent read/hash/AST/pure DATA review; no freezer or verifier action."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,stat,sys,time
sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'node-crypto-hash-hmac-freezer-candidate-v1'
WANT='45eef4b6de1e24e450737b66cfc7216e81e39192f8be11be7e80f4312f7c9355'
checks=[]
def check(n,v):assert v,n;checks.append(n)
def reject(n,fn):
 try:fn()
 except(AssertionError,KeyError,ValueError):checks.append(n);return
 raise AssertionError('Accepted negative '+n)
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 started=time.monotonic();ix=desc(SOURCE/'index.json');check('assigned Source seal',ix['sha256']==WANT)
 index=read(ix['path']);names={r['path']for r in index['files']}|{'index.json'}
 check('whole Source membership',names=={p.relative_to(SOURCE).as_posix()for p in SOURCE.rglob('*')if p.is_file()})
 for r in index['files']:check('Source member '+r['path'],desc(SOURCE/r['path'])==dict(r,path=str(SOURCE/r['path']))and not(SOURCE/r['path']).is_symlink())
 refs=read(SOURCE/'references.json');inputs=read(refs['sourceInputs']['path'])
 # These modules have inspected inert stdlib definitions. Only exported
 # read/hash/pure model functions below are used; never bootstrap/run/verify.
 e=load('independent_freezer_original_context_data',SOURCE/'entry.py')
 v=load('independent_frozen_only_pure_contract_data',SOURCE/'verify_frozen.py')
 f=load('independent_freeze_ownership_model_only',SOURCE/'freeze.py')
 check('original OWN genuine',e.OWN==SOURCE)
 check('matching fixed freeze roots',str(e.FREEZE)==str(v.FREEZE)==refs['freezeRoot'])
 captured={};identities={};families={}
 def add(d):
  check('consistent descriptor '+d['path'],d['path']not in captured or captured[d['path']]==d);captured[d['path']]=d
 for d in [ix,*[dict(r,path=str(SOURCE/r['path']))for r in index['files']]]:add(d)
 for d in inputs['files']:add(d)
 for family in inputs['families']:
  for d in e.family(family):add(d)
  families[family['path']]=family
 for d in e.read(refs['artifactLedger'])['files']:add(d)
 for d in e.read(refs['referenceAdditions'])['files']:add(d)
 for path,d in captured.items():p=e.checked(d);identities[path]=e.identity(p)
 trees=e.read(refs['artifactTrees'])['trees'];e.trees(trees,captured)
 check('full11 tree coverage',len(trees)==11)
 aliases=e.read(refs['referenceAliases'])
 for a in aliases['symlinks']:check('current alias '+a['path'],Path(a['path']).is_symlink()and os.readlink(a['path'])==a['linkText']and str(Path(a['path']).resolve(strict=True))==a['resolved'])
 for a in aliases['archiveHardlinks']:
  x=Path(a['path']).stat();y=Path(a['target']).stat();check('declared archive hardlink',(x.st_dev,x.st_ino)==(y.st_dev,y.st_ino))
 proof,contract,proof_rows=e.whole_proof(refs['artifactReview'],refs['artifactContract']);e.artifact_model(proof,refs);checks.append('corrected a39 whole proof/coverage joins')
 for k,value in [('publicationVersion',1),('originalParentExitCodes',[0,0]),('originalBuildPreservationPassed',True),('originalBuildAccepted',True),('engineExecuted',True)]:
  bad=copy.deepcopy(proof);bad[k]=value;reject('artifact model denies '+k,lambda:e.artifact_model(bad,refs))
 bad=copy.deepcopy(proof);bad['coverage']['currentLedgerFiles']-=1;reject('whole coverage mismatch rejected',lambda:v.fixed_contract(bad,contract))
 root=read(SOURCE/'root-authority.template.json');root.update(freezerIndex=ix,freezeAllowed=True,readOnlyProducerAdmissionAllowed=True,frozenOnlyVerificationAllowed=True,ownedCopiesAllowed=True)
 e.root_model(root,ix,refs);checks.append('complete Root pure model')
 for k in ['nativeBuildAllowed','compilerAllowed','ninjaAllowed','gitAllowed','cryptoAllowed','engineExecutionAllowed','liveEvpSnapshotAdmission','operationalAdmission']:
  bad=copy.deepcopy(root);bad[k]=True;reject('Root denies '+k,lambda:e.root_model(bad,ix,refs))
 for k,value in [('originalParentExitCodes',[0,0]),('originalRecipeExitCode',1),('deadlineSeconds',7201),('originalBuildAccepted',True)]:
  bad=copy.deepcopy(root);bad[k]=value;reject('Root history/budget '+k,lambda:e.root_model(bad,ix,refs))
 for path in refs['tmpAliasPolicy']['selectedDescriptorPaths']:check('exact actual/tmp mapping '+path,e.physical(path)==Path('/private'+path))
 for path in ['/tmp/not-selected','relative/a','//private/tmp/x','/private/tmp/../x','/private/tmp/a\\b']:
  reject('path refuses '+path,lambda:e.physical(path))
 reject('frozen reader refuses original metadata before opening',lambda:v.checked(refs['metadata']))
 reject('frozen reader refuses original engine before opening',lambda:v.checked(refs['engine']))
 producer=e.read(refs['producerReferences']);policy=e.read(producer['policy']);metadata=e.read(refs['metadata'])
 model=load('independent_pure83_no_filesystem_model',SOURCE/'metadata_model.py');hm=load('independent_hash_command_DATA_model',SOURCE/'hash_model.py')
 classification=model.validate_metadata(metadata,policy,producer['policy']['sha256'],producer['helper']['sha256'],producer['recipe']['sha256'],policy['expectedComponentizeSourceManifest'],'normal-off')
 check('whole actual raw83 pure classification',classification==dict(state='FINITE_NODE_CRYPTO_HASH_HMAC357_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',nativeFiles=357,engineRead=False,runtimeAccepted=False,grantsAuthority=False))
 database=e.read(dict(path=metadata['compileCommandsPath'],sha256=metadata['compileCommandsSha256'],bytes=Path(metadata['compileCommandsPath']).stat().st_size))
 command=hm.validate_hash_hmac_commands(database,metadata['actualEmbeddingCompileCommands'],Path(producer['configuredSourceRoot']),metadata,policy)
 check('actual69 command DATA with7private COPY-only sites',len(database)==69 and len(command['actualPrivateHashHmacMacroCompileCommands'])==7 and command['defaultCopyOnly'])
 manifests=[e.read(dict(path=str(Path(refs['configuredSourceRoot'])/r['path']),sha256=r['sha256'],bytes=Path(refs['configuredSourceRoot'],r['path']).stat().st_size))for r in metadata['selectedModuleManifests']]
 check('actual12 whole manifest DATA',hm.validate_selected_manifests(metadata,policy,manifests))
 bad=copy.deepcopy(metadata);bad['nodeCryptoAuditedBorrowEnabled']=True;reject('command model denies BORROW',lambda:hm.validate_hash_hmac_commands(database,bad['actualEmbeddingCompileCommands'],Path(producer['configuredSourceRoot']),bad,policy))
 stage=e.read(refs['stageJournal']);check('whole1642 stage plus3 historical references',len(stage['copies'])==1642 and len(stage['embeddingDataCompleted'])==3)
 work=e.read(refs['workCopyPlan']);check('bounded169 WORK witnesses',len(work['files'])==169 and work['copyBytes']==557901902)
 workpaths={r['source']['path']for r in work['files']};archives=v.lexical_link_archives(metadata['nodeCryptoHashHmacPolicy']['actualLinkEvidence']['linkArgv'],str(Path(metadata['cmakeCachePath']).parent))
 check('every actual lexical archive selected',set(archives)<=workpaths and metadata['openssl']['library']['path']in workpaths and metadata['zlibSelectedCodecInput']['archive']['path']in workpaths)
 check('lexical relative/absolute paths no source lookup',v.lexical_link_archives(['../lib/a.a','/absolute/b.a'],'/work/build')==['/work/lib/a.a','/absolute/b.a'])
 # The generic copy afterimage is precisely one fchmod insertion; no copy action.
 deriv=read(SOURCE/'derivations.json');d=deriv['copyIo'];before=Path(d['original']['path']).read_text();after=(SOURCE/'copy_io.py').read_text()
 check('one exact copy-mode edit',before.count(d['before'])==1 and before.replace(d['before'],d['afterText'])==after and after.replace(d['afterText'],d['before'])==before)
 for d in deriv['models'].values():check('byte-identical genuine pure model '+d['after']['path'],Path(d['original']['path']).read_bytes()==Path(d['after']['path']).read_bytes())
 # Synthetic stat records exercise only ownership_model, not root creation.
 current=os.stat_result((stat.S_IFDIR|0o700,2,1,1,0,0,0,0,0,0));held=os.stat_result((stat.S_IFDIR|0o700,2,1,1,0,0,0,0,0,0))
 check('pure current FD ownership tuple',f.ownership_model(current,held,(1,2)))
 reject('pure mismatched root identity',lambda:f.ownership_model(current,held,(1,3)))
 wrong=os.stat_result((stat.S_IFDIR|0o755,2,1,1,0,0,0,0,0,0));reject('pure root mode refusal',lambda:f.ownership_model(wrong,held,(1,2)))
 index_model=load('independent_current_index_pure_decoder',e.checked(refs['indexModel']))
 index=refs['indexException']['currentActual'];check('current index mode600',stat.S_IMODE(e.checked(index).stat().st_mode)==0o600)
 decoded=index_model.decode(e.checked(index).read_bytes(),e.checked(refs['baselineTreeTransport']).read_bytes());check('current742 semantic baseline DATA',decoded['entries']==742)
 for p in SOURCE.glob('*.py'):ast.parse(p.read_bytes());checks.append('Source AST '+p.name)
 text=(SOURCE/'freeze.py').read_text();check('whole admission return before assertions',text.index("whole=json_write('producer-admission-return.json',returned)")<text.index('assert returned=='))
 check('genuine original-owner argument and new callback',"argument=dict(io=io,refs=io.read(refs['producerReferences']),ownIndex=refs['producerIndex'])"in text and 'lambda unused:recheck(frame)'in text)
 check('parent-created-root scope set after absence recheck',"recheck(frame);frame['creationAllowed']=True"in(SOURCE/'entry.py').read_text())
 tree=ast.parse((SOURCE/'verify_frozen.py').read_text());check('no original-resolving/helper/command action call in frozen verifier',not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in ['resolve','admit','bootstrap','execute_plan','run','check_output']for n in ast.walk(tree)))
 check('frozen verifier calls only lexical command validators',not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in ['observe_hash_hmac','link_command']for n in ast.walk(tree)))
 # No synthetic freeze receipt is fabricated or passed to verify_frozen.
 for path,d in captured.items():check('final identity '+path,e.identity(e.checked(d))==identities[path])
 e.trees(trees,captured)
 for family in families.values():e.family(family)
 check('owner Source seal unchanged',desc(SOURCE/'index.json')==ix)
 save('reader-results.json',dict(schemaVersion=1,state='INDEPENDENT_HASH_HMAC357_FREEZER_SOURCE_READ_HASH_PURE_PASSED',sourceIndex=ix,checks=len(checks),uniqueCurrentFiles=len(captured),logicalBytes=sum(r['bytes']for r in captured.values()),declaredFamilies=len(families),completeTrees=len(trees),aliases=len(aliases['symlinks']),archiveHardlinks=len(aliases['archiveHardlinks']),indexSemanticEntries=decoded['entries'],noEntryOrAuthorizeAdmitHelperFreezeVerifyActionMonitorCompilerEngineGuestCalled=True,elapsedOperationalSeconds=time.monotonic()-started))
 print(json.dumps(read(OWN/'reader-results.json')))
if __name__=='__main__':main()
