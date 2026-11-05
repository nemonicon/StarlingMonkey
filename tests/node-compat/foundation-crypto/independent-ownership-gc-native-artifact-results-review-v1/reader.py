"""Completed GC freeze DATA audit only. No producer/helper/CLI/engine import/call."""
from pathlib import Path
import ast,collections,hashlib,json,os,re,shlex
import review_io as I
import artifact_model as M
HERE=Path(__file__).resolve().parent;K=HERE.parent;N=K/'ownership-gc-native-candidate-v2';A=K/'ownership-gc-freezer-helper-amendment-v1';F=Path(M.FREEZE);S=Path(M.SOURCE);TOOLS=Path(M.TOOLS)
def row(p):return I.descriptor(str(p))
def measured(p):d=row(p);I.verify(d,'independent measured original input');return d
def load(p):return I.read(measured(p))
def eq(a,b,label):M.equal(a,b,label)
def write(name,v):
    with(HERE/name).open('xb')as f:f.write((json.dumps(v,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
families={}
def family(d):
    value,children=I.indexed(d,'genuine finite native/helper/artifact context');rows=[d,*children];families[d['path']]=dict(index=d,indexedMembers=len(children));return rows
root_row=dict(path=str(K/'ownership-gc-v2-freeze-helper-v1-root-results.json'),sha256='d9d547354c6431aaacbc908c20248f30dac4f32a5da29338fb7a733ec90a2259',bytes=4962)
root=I.read(root_row);I.need(root['rootObservedToolRawExitCode']==0 and root['rootToolSessionId']==70920 and root['pythonParentPid']==79716,'final actual Root raw0 tuple received before read')
I.verify_descriptors(root,'whole original actual Root freeze observation')
f=I.read(root['freezeReceipt']);eq(root['freezeReceipt']['sha256'],'7567f60f9212f28c8d5052de4e0e395373f5dd0ff08149f497677846591bf669','actual completed immutable receipt')
native_root=I.read(root['nativeRootAuthority']);amend_root=I.read(root['helperAmendmentAuthority']);config=I.read(root['config']);ext=I.read(root['externalParentTerminal']);started=I.read(root['externalParentStarted'])
eq(config,dict(schemaVersion=1,sourceIndex=root['nativeSourceIndex'],rootAuthority=root['nativeRootAuthority'],helperAmendmentIndex=root['helperAmendmentIndex'],helperAmendmentAuthority=root['helperAmendmentAuthority']),'genuine exact dual-source dual-authority config')
I.need(native_root['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PHASE_V1'and native_root['phase']=='freeze'and native_root['freezeAllowed']is True,'genuine native freeze-only authority')
I.need(amend_root['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_GC_FREEZER_HELPER_AMENDMENT_V1'and amend_root['freezeAllowed']is True,'genuine distinct helper amendment authority')
for k,d in [('helperAmendmentIndexed',root['helperAmendmentIndex']),('nativeSourceIndexed',root['nativeSourceIndex']),('nativeRootAuthority',root['nativeRootAuthority'])]:eq(amend_root[k],d,'separate authentic amendment role '+k)
for k in ['stageAllowed','buildAllowed','exportAllowed','bootstrapAllowed','guestAllowed','keyOperationsAllowed','nativeSourceChangesAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:I.need(native_root[k]is False and amend_root[k]is False,'closed both-authority scope '+k)
for k in ['reviewedGcPins','gcNativeRootReview','independentGcNativeReview','pinCandidateOutput']:I.need(native_root[k]is None,'no actual pin/artifact/bootstrap authority '+k)
I.need(native_root['sourceIndexSha256']==root['nativeSourceIndex']['sha256']=='ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05','native frame identity never projected onto helper source')
I.need(root['helperAmendmentIndex']['sha256']=='09ce7fb237998c54af5a3849ae798421e3ccb736492cf5cc426967d15285ee79','actual corrected helper source')
for k,v in dict(configuredSourceRoot=M.SOURCE,workRoot=M.WORK,freezeRoot=M.FREEZE,artifactToolsRoot=M.TOOLS,nativeSourceFiles=355,externalEmbeddingSources=3,variant='gc-off',externalParentDeadlineSeconds=2400).items():eq(native_root[k],v,'actual native physical context '+k)
I.verify_descriptors(native_root,'entire actual native authority context');I.verify_descriptors(amend_root,'entire actual helper authority context')
native_rows=family(root['nativeSourceIndex']);own_rows=family(root['helperAmendmentIndex']);native_peer_rows=family(native_root['independentSourceReview']['index']);helper_peer_rows=family(amend_root['independentSourceReview']['index'])
np=I.read(native_root['independentSourceReview']['result']);hp=I.read(amend_root['independentSourceReview']['result']);I.need(np['sourceReviewPassed']is True and np['sourceIndexSha256']==root['nativeSourceIndex']['sha256']and hp['sourceReviewPassed']is True and hp['sourceIndexSha256']==root['helperAmendmentIndex']['sha256']and hp['nativeSourceIndexSha256']==root['nativeSourceIndex']['sha256'],'separate actual source peers/source-only flags')
I.need(np['ownerActionsInvoked']is False and hp['ownerActionsInvoked']is False,'source-only peers do not themselves grant actions')
build=I.read(native_root['independentBuildReview']['result']);bc=load(K/'independent-ownership-gc-v2-native-build-review-v1/result-contract.json')
for k,v in bc['requiredFixedValues'].items():eq(build[k],v,'full BUILD-only fixed data preserved '+k)
for k,d in bc['requiredExactDescriptors'].items():eq(build[k],d,'full actual BUILD-only tuple '+k);I.verify(d,'original build evidence unchanged')
for k in ['engine','metadata']:eq(native_root[k],build[k],'freeze uses same actual build '+k)
m=I.read(native_root['metadata']);policy=load(TOOLS.parent/'policy.json');native,external=M.metadata(m,policy);M.receipt(f,m,native_root['metadata']['sha256'],native_root['engine']['sha256'],native_root['engine']['bytes'])
eq(m['cryptoKeyOwnershipPolicy'],policy['cryptoKeyOwnershipSourcePolicy'],'whole original owner/prototype guard policy, runtimeValidation remains null')
tool_pins=load(TOOLS/'tool-pins.json');tool_rows=tool_pins['toolDependencies'];I.need(len(tool_rows)==922,'actual full922 tool closure')
# Entire previous build input/witness closure is rehashed as DATA, not rerun.
for d in I.read(build['auditData'])['inputs']:I.verify(d,'complete actual BUILD-only native/source/library witness input')
bw=I.read(build['witnessReview'])
for d in bw['externalEvidenceInventory']+bw['extraFileReads']:I.verify(d,'all raw build/tool witness records')
# Reconstruct captured controller descriptors in actual inspected source order.
captured=[root['config'],root['nativeRootAuthority'],*own_rows,*native_rows];refs=load(A/'references.json')
for item in refs['families']:captured+=family(item['index'])
for d in refs['files']:I.verify(d,'actual amendment inherited source/build/failure input');captured.append(d)
build_peer_rows=family(native_root['independentBuildReview']['index']);captured+=build_peer_rows
for k in ['actualBuildResult','actualBuildExternalTerminal','actualBuildRootObservation','metadata']:captured.append(native_root[k])
captured += [build['buildLog'],native_root['engine']];build_outer=I.read(native_root['actualBuildExternalTerminal']);captured += [build_outer['stdout'],build_outer['stderr']]
captured += helper_peer_rows
captured += [root['helperAmendmentAuthority'],*helper_peer_rows]
helper_inputs=load(A/'input-freeze.json')['files'];I.need(len(helper_inputs)==3017,'complete explicit helper-source input freeze')
for d in helper_inputs:I.verify(d,'whole helper preparation input in original context');captured.append(d)
capsules=[*native_rows,root['nativeRootAuthority'],*native_peer_rows]
capsule_roots=[A,Path(amend_root['independentSourceReview']['index']['path']).parent,Path(native_root['independentBuildReview']['index']['path']).parent,K/'independent-ownership-gc-v2-freeze-failure-review-v1']
selected=[captured[0],root['helperAmendmentAuthority']]+[d for d in captured if any(Path(d['path']).is_relative_to(base)for base in capsule_roots)]
# The inspected source computes its entire comprehension before extending the
# native list. Repeated controller captures therefore remain repeated capsules.
capsules += [d for d in selected if d not in capsules]
correction=I.read(root['helperCorrectionProof']);eq(f['freezerSourceCorrection'],{**root['helperCorrectionProof'],'nativeSourceIndexSha256':root['nativeSourceIndex']['sha256'],'helperAmendmentSourceIndexSha256':root['helperAmendmentIndex']['sha256']},'exact real dual-source correction descriptor')
control_copies=[dict(original=d['path'],path=str(F/('gc-off-freezer-correction-control/'+str(n)+'-'+Path(d['path']).name)),sha256=d['sha256'],bytes=d['bytes'])for n,d in enumerate(capsules)]
expected_correction=dict(schemaVersion=1,state='ACTUAL_AUTHORIZED_CRYPTO_GC_FREEZER_HELPER_AMENDMENT_CAPTURE_V1',nativeSourceIndexed=root['nativeSourceIndex'],helperAmendmentIndexed=root['helperAmendmentIndex'],donorSourceIndexSha256='68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575',nativeRootAuthority=root['nativeRootAuthority'],nativeIndependentSourceReview=native_root['independentSourceReview'],helperAmendmentRootAuthority=root['helperAmendmentAuthority'],helperAmendmentIndependentSourceReview=amend_root['independentSourceReview'],selectedCommonHelper=root['correctSelectedCommonHelper'],configuredSourceRoot=M.SOURCE,stagedArtifactToolsRoot=M.TOOLS,freezeRoot=M.FREEZE,activeSource=amend_root['activeFreezerEntry'],donorSourceData=measured(TOOLS/'freeze-engine.py'),copies=control_copies,nativeRecipePolicyHelperAnd922ToolsUnchanged=True,engineExecuted=False)
if correction!=expected_correction:
    detail={k:dict(actual=correction[k],expected=v)for k,v in expected_correction.items()if k!='copies'and correction.get(k)!=v}
    aa=correction['copies'];bb=expected_correction['copies'];detail['copyLengths']=[len(aa),len(bb)];detail['firstCopyDifferences']=[dict(n=n,actual=a,expected=b)for n,(a,b)in enumerate(zip(aa,bb))if a!=b][:3]
    raise AssertionError(json.dumps(detail))
expected_bytes=(json.dumps(expected_correction,indent=2)+'\n').encode();I.need(expected_bytes==I.verify(root['helperCorrectionProof']).read_bytes(),'generated correction bytes exactly from actual source/phase capsules')
licenses=[]
for p in sorted((S/'builtins/node-compat').rglob('*')):
    if p.is_file()and p.name.startswith(('LICENSE','NOTICE')):licenses.append(dict(name='source/'+p.relative_to(S).as_posix(),original=str(p),sha256=measured(p)['sha256']))
ssl_license=Path(m['openssl']['sourceDir'])/'LICENSE.txt';licenses.append(dict(name='dependency-licenses/openssl-LICENSE.txt',original=str(ssl_license),sha256=measured(ssl_license)['sha256']))
ancestry=[measured(p)for p in sorted((TOOLS/'ancestry/production-artifacts-v1').iterdir())]
plan=M.expected_plan(m,f,tool_rows,capsules,str(A/'freeze.py'),str(A/'amendment-guard.py'),measured,licenses,ancestry)
copies={};original_count=0;copy_bytes=0
for d in f['copies']:
    relative=Path(d['path']).relative_to(F).as_posix();I.member(relative);I.need(relative not in copies,'unique finite freeze copy');copies[relative]=d;I.verify(d,'every actual complete frozen copy')
    current=I.canonical(d['path']).stat();I.need(current.st_nlink==1,'copy independently owns regular inode')
    if d['original']is not None:
        original=dict(path=d['original'],sha256=d['sha256'],bytes=d['bytes']);p=I.verify(original,'every original actual freeze input');st=p.stat();I.need((st.st_dev,st.st_ino)!=(current.st_dev,current.st_ino),'frozen copy distinct original inode');original_count+=1
    copy_bytes+=d['bytes']
eq(list(copies),list(plan),'entire finite ordered copy plan reconstructed, not only critical rows')
for name,d in copies.items():eq({k:d[k]for k in ['path','original','sha256','shared']},plan[name],'whole original/copy/role tuple '+name)
I.need(len(copies)==1462 and original_count==1459,'1462 complete copies and three explicitly generated rows');I.exact_tree(F,[*copies,'gc-off-freeze-receipt.json'])
for key,name,role in [('activeFreezerTooling','artifact-tools/freeze-engine.py','ACTUAL_ACTIVE_CORRECTED_FREEZER'),('donorFreezerTooling','artifact-tools/donor-data/freeze-engine.py','IMMUTABLE_STAGED_DONOR_DATA_NOT_ACTIVE')]:
    d=f[key];I.need(d['role']==role and d['path']==str(F/name)and d['sha256']==copies[name]['sha256']and d['original']==copies[name]['original'],'actual active-vs-donor wrapper role '+key)
eq(f['activeFreezerTooling'],root['activeFreezer'],'Root active actual amendment wrapper');eq(f['donorFreezerTooling'],root['donorFreezerData'],'Root donor DATA role');eq(f['helperSha256'],measured(A/'freeze.py')['sha256'],'active entry exact actual hash, not old native freeze.py')
eq(root['correctSelectedCommonHelper'],dict(path=str(TOOLS/'artifact_common.py'),sha256='fff7bed72aec0c592e7a788060a5c1ecf6a0b0694ca519dbfa00e230584123ab',bytes=19299),'unique exact crypto helper now actual selected')
stage=load(N/'stage-inputs.json');I.need(len(stage['files'])==1311,'all declared source overlays unchanged')
for d in stage['files']:I.verify(d['original'],'all original native source overlay');I.verify(dict(path=str(S/d['path']),sha256=d['original']['sha256'],bytes=d['original']['bytes']),'all actual isolated native source overlay')
# Full actual metadata and selected manifests are retained unchanged as whole DATA.
I.need(I.verify(dict(path=str(F/'gc-off.engine.wasm.build.json'),sha256=root['metadataSha256'],bytes=376978)).read_bytes()==I.verify(native_root['metadata']).read_bytes(),'whole frozen/original metadata exact bytes')
I.need(I.verify(dict(path=str(F/'gc-off.engine.wasm'),sha256=root['engineSha256'],bytes=root['engineBytes'])).read_bytes()[:8]==b'\0asm\x01\0\0\0','actual core Wasm header only, no execution/decoder')
manifests=[]
for d in m['selectedModuleManifests']:
    source=load(S/d['path']);frozen=load(F/'source'/d['path']);eq(source,frozen,'all whole original selected manifest DATA');eq(source['profileVersion'],d['profileVersion'],'actual selected manifest version');manifests.append(dict(descriptor=measured(F/'source'/d['path']),data=frozen))
admission=load(F/'gc-off-source-admission.json');I.need(admission['state']=='ACTUAL_FINITE_CRYPTO_OWNER355_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'and admission['sourceFiles']==355 and admission['toolDependenciesVerified']==922 and admission['engineBytesRead']is False and admission['guestExecuted']is False and admission['validationBootstrapOnly']is True and admission['operationalAdmission']is False,'genuine actual metadata selector output, no fabricated state')
eq(admission['classicSourceAdmission']['cryptoKeyOwnershipSourcePolicy'],m['cryptoKeyOwnershipPolicy'],'whole owner and prototype-guard source contract retained');eq(admission['selectedManifestPaths'],[d['path']for d in m['selectedModuleManifests']],'all eleven actual selected manifest paths')
eq(admission['options'],dict(gcStress=True,entropyPolicy='off',classicStreamsEnabled=True,zlibEnabled=True,streamConsumersEnabled=True),'actual source selector variant options')
# Full original native ReleaseGC compile layout, including exact private-only macro scope.
db=load(F/'gc-off-compile_commands.json');mapped={}
for d in db:
    if d['file'].startswith((str(S/'builtins')+'/',str(S/'runtime')+'/'))and d['file'].endswith('.cpp'):name=Path(d['file']).relative_to(S).as_posix();I.need(name not in mapped,'unique selected native cpp');mapped[name]=d['command']
cpp={p for p in native if p.endswith('.cpp')and p.startswith(('builtins/','runtime/'))};eq(sorted(mapped),sorted(cpp),'all62 actual native compiler rows');private=set(policy['privateTargetCpp']);I.need(len(mapped)==62 and len(private)==6,'bounded actual compile layout')
w=m['zlibPolicy']['codecWitness'];include=m['zlibSelectedCodecInput']['requiredForcedInclude']['path']
for name,command in mapped.items():M.compile_scope(command,str(S/name),name in private,False,include)
embedding=load(F/'gc-off-CMakeCache.txt')if False else f['postBuildEmbeddingEvidence'];raw_embedding=I.verify(dict(path=embedding['path'],sha256=embedding['sha256'],bytes=embedding['bytes'])).read_text();I.need(embedding['exitCode']==0 and embedding['stderr']==''and embedding['beforeBuildCaptureExists']is False,'actual post-build embedding evidence')
lines=[line for line in raw_embedding.splitlines()if' -c 'in line and embedding['sourcePath']in line];eq(lines,embedding['compileCommands'],'all actual embedding Ninja DATA lines');eq(lines,m['actualEmbeddingCompileCommands'],'same noLTO embedding build command');I.need(len(lines)==1,'one actual embedding command');M.compile_scope(lines[0],embedding['sourcePath'],False,True,include)
eq(list(mapped.values()),m['internalTickPolicy']['actualLayoutCompileCommands'],'exact metadata native layout');eq(list(mapped.values()),m['protectedAbortListenerPolicy']['actualLayoutCompileCommands'],'exact protected actual layout')
eq(sorted(mapped[n]for n in private),sorted(m['classicStreamsPolicy']['actualPrivateTargetCompileCommands']),'all6 actual private commands')
normal=load(N/'normal-protection.json');I.need(len(normal['originals'])==1387,'all original normal references')
for d in normal['originals']:I.verify(d['original'],'normal original preservation');I.verify(d['frozen'],'normal frozen preservation')
for d in normal['frozenCopyEntries']:I.verify(d,'normal whole protected membership bytes')
I.verify(normal['freezeReceipt']);I.exact_tree(I.canonical(normal['freezeReceipt']['path']).parent,normal['requiredNormalFreezeMembership'])
# Full raw terminal/streams and every observed ownership event; no new process scan.
for k,v in dict(pid=79716,rawExitCode=0,timeout=False,forcedCleanup=False,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True).items():eq(ext[k],v,'actual clean freeze external '+k)
for k in ['errors','signals','interruptedSignals','remainingObservedPids']:eq(ext[k],[],'no failed outer cleanup '+k)
eq(ext['authority'],root['nativeRootAuthority'],'actual raw native authority');I.need(ext['stderr']['bytes']==0 and all(g['alive']is False for g in ext['finalGroups']),'all recorded final groups gone')
I.verify_descriptors(ext,'full raw freeze streams');stdout=I.read(ext['stdout']);eq(stdout,dict(receiptPath=root['freezeReceipt']['path'],receipt=f),'whole complete raw stdout equals all written receipt fields')
eq(started['authority'],root['nativeRootAuthority'],'started actual native authority');I.need(started['pid']==79716 and started['timeoutSeconds']==2400 and started['argv'][1]==str(A/'freeze.py'),'actual new wrapper launch');eq(I.decode(started['argv'][2].encode()),root['config'],'exact actual dual-authority config argv')
ex=Path(root['externalParentTerminal']['path']).parent;observed=[]
for p in sorted(ex.iterdir()):
    I.need(p.is_file()and not p.is_symlink(),'ordinary final external evidence');I.verify(measured(p),'full freeze external inventory')
    if p.name.startswith('owned-'):e=load(p);I.need(e['sequence']==len(observed),'ordered actual ownership events');observed.append(e['process'])
eq(observed,ext['observedProcesses'],'all recorded observed identity fields');I.exact_tree(ex,['terminal.json','started.json','stdout.log','stderr.log',*[f'owned-{n:04d}.json'for n in range(len(observed))]])
for p in [A/'freeze.py',A/'amendment-guard.py',A/'controller.py',A/'freezer-body.py',TOOLS/'artifact_common.py']:ast.parse(I.verify(measured(p)).read_text())
guard=(A/'amendment-guard.py').read_text();body=(A/'freezer-body.py').read_text();I.need('if r[\'path\'] == NATIVE_RELATIVE'in guard and 'common.OUTPUT == Path(\'/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze\')'in guard,'actual exact helper selection and unchanged donor globals')
I.need('validate_plan(plan, receipt_path, output=output_root)'in body and 'execute_plan(plan, output=output_root)'in body,'actual existing explicit output-root APIs used')
I.final_rehash();I.exact_tree(F,[*copies,'gc-off-freeze-receipt.json']);I.exact_tree(I.canonical(normal['freezeReceipt']['path']).parent,normal['requiredNormalFreezeMembership'])
write('full-native-data.json',dict(schemaVersion=1,metadata=m,selectedManifests=manifests,actualSourceAdmission=admission,independentlyExpectedCorrection=expected_correction,plannedCopies=list(plan.values())))
write('rehashed-inputs.json',dict(schemaVersion=1,files=list(I.ROWS.values()),families=list(families.values()),allFinalHashesStable=True,allFrozenMembershipExact=True,allNormalMembershipExact=True,producerCodeExecuted=False))
write('data-results.json',dict(schemaVersion=1,state='BOUNDED_FROZEN_GC_NATIVE_DATA_AUDIT_PASSED_PENDING_WITNESS_SUPPLEMENT',root=root_row,actualFreezeReceipt=root['freezeReceipt'],sourceIndex=root['nativeSourceIndex'],helperAmendmentIndex=root['helperAmendmentIndex'],frozenCopies=len(copies),frozenRegularFiles=1463,originalCopyRows=original_count,indexedControlCapsules=len(capsules),copiedBytes=copy_bytes,nativeSourceFiles=355,externalEmbeddingSources=3,toolRows=922,selectedManifests=11,nativeCompileRows=62,privateGcNodeTUs=6,embeddingCompileRows=1,rawFreezeExitCode=0,allWholeMetadataAndOriginalCopiesVerified=True,completeDualAuthorityCorrectionBytesReconstructed=True,allDeclaredSourceBuildInputsAndNormalProtectionRehashed=True,independentHashChecks=I.CHECKS,independentModelChecks=M.CHECKS,physicalInputs=len(I.ROWS),noNativeArtifactVerdictIssuedYet=True,reviewerHelpersCliNodeNinjaNmEngineGuestOrGcActionsInvoked=False))
print(json.dumps(dict(state='CORE_FROZEN_DATA_AUDIT_PASSED_WITNESS_PENDING',files=len(I.ROWS),copies=len(copies),capsules=len(capsules),ownerActionsInvoked=False)))
