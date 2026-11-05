"""Read/hash retained failure and exact Source seam; no owner imports/actions."""
from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parent;K=HERE.parent;SOURCE=K/'ownership-secret-component-candidate-v1'
def read(p):return json.loads(Path(p).read_bytes())
def row(p):
 p=Path(p);assert p.is_file()and not p.is_symlink();a=p.stat();b=p.read_bytes();z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns);return dict(path=str(p.resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def verify(r):assert row(r['path'])==r;return r
def write(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
root=K/'ownership-secret-component-v1-root-results.json';r=read(root);rootrow=row(root)
assert rootrow['sha256']=='3a3886f89998f24ad299f49236a47cae2200258c4d7c3aaae4e0d735bf14dafc'
for k in ['invocation','sourceIndex','rootAuthority','rootConfig','ownedNodeTerminal','stdout','stderr']:verify(r[k])
for m in read(r['sourceIndex']['path'])['files']:verify(dict(m,path=str(SOURCE/m['path'])))
peer=r['sourcePeer'];verify(peer['index']);verify(peer['result']);assert peer['result']in[dict(x,path=str(Path(peer['index']['path']).parent/x['path']))for x in read(peer['index']['path'])['files']]
refs=read(SOURCE/'references.json');inv=read(r['invocation']['path']);authority=read(r['rootAuthority']['path']);cfg=read(r['rootConfig']['path']);terminal=read(r['ownedNodeTerminal']['path']);base=Path(r['ownedNodeTerminal']['path']).parent
assert sorted(p.name for p in base.iterdir())==['owned-0000.json','started.json','stderr.log','stdout.log','terminal.json']
started=read(base/'started.json');owned=read(base/'owned-0000.json')
assert terminal['schemaVersion']==1 and terminal['rawExitCode']==r['rawExitCode']==1 and terminal['authority']==r['rootAuthority']
assert terminal['parentOwnedGroupGone']is terminal['allObservedOwnedGroupsGone']is True
assert terminal['timeout']is terminal['forcedCleanup']is False and all(terminal[k]==[] for k in ['interruptedSignals','remainingObservedPids','signals','errors'])
assert terminal['finalGroups']and all(g['alive']is False for g in terminal['finalGroups'])
assert terminal['stdout']==r['stdout']and terminal['stderr']==r['stderr']and r['stdout']['bytes']==0 and r['stderr']['bytes']==1485
assert started['argv']==inv['argv']and started['timeoutSeconds']==1800 and started['authority']==r['rootAuthority']and started['pid']==terminal['pid']==87446
assert cfg['rootAuthority']==r['rootAuthority']and cfg['sourceIndex']==r['sourceIndex']and authority['sourceIndex']==r['sourceIndex']and authority['sourceIndependentReview']==r['sourcePeer']
assert authority['componentBuildAllowed']is authority['componentInitializationAllowed']is True
assert all(authority[k]is False for k in ['ordinaryGuestExportsAllowed','keyOrCryptoOperationsAllowed','gcPressureAllowed','originalOneShotApiAllowed','originalHelperAllowed','historicalCallableAllowed','generatedModuleImportAllowed','operationalAdmission','runtimeAcceptanceClaim'])
stderr=Path(r['stderr']['path']).read_text();assert 'Error: Exact explicit packaging roots'in stderr and 'packaging.mjs:42:2'in stderr and 'build.mjs:109:150'in stderr and 'finalErrors: []'in stderr and 'Node.js v22.14.0'in stderr
body=(SOURCE/'build.mjs').read_text();helper=Path(refs['packagingHelper']['path']).read_text()
assert 'packaging=await loadPackaging(refs.packagingMap);packagingEnvironment(packaging);'in body
assert body.index('packagingEnvironment(packaging);')<body.index('out=await DurableOutput.create(refs.outputRoot)')<body.index('await selected.componentize(bundle.code,options)')
assert "env.NODE_COMPAT_TOOLCHAIN===context.toolchainRoot&&env.NODE_COMPAT_COMPONENTIZE_MODULE===join(context.packagerRoot,'src/componentize.js'),'Exact explicit packaging roots'"in helper
assert not Path(refs['outputRoot']).exists()and not Path(refs['outputRoot']).is_symlink()
assert r['state']=='ROOT_OBSERVED_SECRET355_COMPONENT_CONSTRUCTION_FAILED_V1'and r['returnedEnvelope']is None and r['rootInputProtectionError']is None
expected=dict(NODE_COMPAT_TOOLCHAIN=refs['physicalRoles']['toolchainRoot'],NODE_COMPAT_COMPONENTIZE_MODULE=refs['physicalRoles']['packagerRoot']+'/src/componentize.js')
evidence=[rootrow,r['invocation'],r['rootAuthority'],r['rootConfig'],*map(row,sorted(base.iterdir())),row(Path(inv['observerRoot'])/'root-observation.json')]
copies=[];(HERE/'evidence').mkdir(exist_ok=False)
for i,d in enumerate(evidence):
 verify(d);dest=HERE/'evidence'/(str(i).zfill(2)+'-'+Path(d['path']).name);raw=Path(d['path']).read_bytes();fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
 actual=row(dest);assert actual['sha256']==d['sha256']and actual['bytes']==d['bytes'];copies.append(dict(original=d,copy=actual))
write('evidence-copies.json',dict(schemaVersion=1,copies=copies,wholeOriginalExternalMembership=['owned-0000.json','started.json','stderr.log','stdout.log','terminal.json'],componentOutputRootAbsent=refs['outputRoot']))
fixed=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_COMPONENT_CONSTRUCTION_FAILURE_REVIEW_PASSED_V1',verifiedPassed=True,componentSourceIndexSha256=r['sourceIndex']['sha256'],actualConstructionPassed=False,componentizationReached=False,componentArtifactAvailable=False,guestInitializationExecuted=False,ordinaryGuestExportsInvoked=False,keyOperationsInvoked=False,generatedModuleImported=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
result=dict(fixed,rootObservation=rootrow,actualOwnedNodeTerminal=r['ownedNodeTerminal'],actualStarted=row(base/'started.json'),actualOwnedRecord=row(base/'owned-0000.json'),actualStdout=r['stdout'],actualStderr=r['stderr'],sourceIndex=r['sourceIndex'],sourcePeer=peer,rootAuthority=r['rootAuthority'],rootConfig=r['rootConfig'],rootInvocation=r['invocation'],actualArgv=started['argv'],ownedNodePid=87446,rawExitCode=1,allObservedOwnedGroupsGone=True,timeoutOrForcedCleanupOrSignalsOrErrors=False,rootOperationalWallSeconds=r['operationalWallSeconds'],componentOutputRootAbsent=refs['outputRoot'],exactFailure=dict(category='EXPLICIT_PACKAGING_ENVIRONMENT_GUARD',message='Exact explicit packaging roots',guardSource=row(refs['packagingHelper']['path']),guardLine=42,callerSource=row(SOURCE/'build.mjs'),callerLine=109,requiredEnvironment=expected,actualChildEnvironmentRetained=False,whichConjunctionOperandFailedKnown=False,environmentGuardRefusalObserved=True),sourceCoupledBoundaries=dict(retainedApiAndLoadPackagingReturnedBeforeRefusal=True,retainedFinalRecheckAndSourcePackagingFinalChecksReturnedWithoutRecordedErrors=True,perInternalCallRawReturnOrCountIndependentlyRetained=False,durableOutputCreationReached=False,loadToolchainOrBundlerReached=False,componentizerOrWizerOrEngineReached=False,fullFourCaseGuardedWorkloadInvoked=False),qualification='Root report and raw owned terminal establish failed construction/clean process completion. Stack and unchanged Source place the failure before all output/bundle/componentization. Exact actual environment values were not retained; no missing-versus-wrong operand attribution is made. Internal read/hash calls are Source-coupled, not individually logged.',eligibleSuccessor=dict(kind='SEPARATE_ROOT_INVOCATION_CORRECTION_NOT_SOURCE_OR_METADATA_PROJECTION',requirements=['Preserve old Source, Source peer, authority/config, raw failure and all external evidence.','Bind both exact required packaging environment values from the authenticated physical map in a fresh explicit Root construction phase.','Use fresh owned monitor/observer output paths and retain actual nonsecret selected environment values plus complete streams/terminal.','Preserve strict same normal355 engine/metadata/full11/guest/WIT/packaging/adapter roles and all ordinary export/key/runtime prohibitions.','Output root is still unused, but any future use must pass existing exclusive absent-root guard; never erase failed evidence.','No native rebuild or Source/ABI/helper change is justified by this guard refusal alone; any actual Source successor would need explicit derivation/review.'],grantsRetryAuthority=False),evidenceCopies=row(HERE/'evidence-copies.json'),reviewerActions=dict(readHashSourceAndCopiesOnly=True,ownerApiInvoked=False,packagerOrEngineOrGuestInvoked=False,processControlInvoked=False),actualComponentReview=None,actualRuntimeAuthority=None)
write('results.json',result)
write('result-contract.json',dict(schemaVersion=1,requiredFixedValues=fixed,results=row(HERE/'results.json'),requiredExactDescriptors=dict(rootObservation=rootrow,terminal=r['ownedNodeTerminal'],stderr=r['stderr'],stdout=r['stdout'],sourceIndex=r['sourceIndex']),requiredEnvironmentForAnySeparatelyAuthorizedSuccessor=expected,actualEnvironmentOperandAttributionAllowed=False,grantsRetryOrRuntimeAuthority=False))
rows=[]
for p in sorted(HERE.rglob('*')):
 if p.is_file()and p.name!='index.json':d=row(p);d['path']=p.relative_to(HERE).as_posix();rows.append(d)
write('index.json',dict(schemaVersion=1,files=rows))
for n in ['index.json','results.json','result-contract.json']:print(json.dumps(row(HERE/n)))
