from pathlib import Path
import ast,hashlib,json,os,re,stat
HERE=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-zlib/independent-cost-tooling-v3-source-review-v1')
OWNER=HERE.with_name('cost-tooling-candidate-v3')
EXPECTED='ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8'
checks=[];cache={};identities={}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def hashfile(path):
 path=Path(path);s=path.stat();key=(str(path.resolve()),s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 if key not in cache:
  h=hashlib.sha256()
  with path.open('rb')as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  t=path.stat();assert(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns)
  cache[key]=h.hexdigest()
 identities[str(path)]={'path':str(path),'realpath':str(path.resolve()),'sha256':cache[key],'bytes':s.st_size}
 return cache[key]
def verify(row,path=None):
 path=Path(path or row.get('path')or row.get('source'));assert path.is_file()and not path.is_symlink(),path
 assert hashfile(path)==row['sha256']and path.stat().st_size==row['bytes'],path
 return path
def indexed(root,expected):
 assert hashfile(root/'index.json')==expected
 d=json.loads((root/'index.json').read_bytes())
 for r in d['files']:verify(r,root/r['path'])
 return d
index=indexed(OWNER,EXPECTED);assert len(index['files'])==286;checks.append('all286OwnerIndexedFiles')
inputs=json.loads((OWNER/'input-freeze.json').read_bytes());assert len(inputs['files'])==5357
for r in inputs['files']:verify(r)
checks.append('all5357PreparationRowsStreamRehashedNoOriginalManifestReinterpretation')
plan=json.loads((OWNER/'publication-plan.json').read_bytes());assert len(plan['objects'])==5072 and len(plan['links'])==22
assert len({r['destination']for r in plan['objects']})==5072
for r in plan['objects']:verify(r)
assert sum(r['bytes']for r in plan['objects'])==353570253
checks.append('all5072FuturePublicationPhysicalObjectsIncludingNativeWasmSourceAdapterAndToolFiles')
trees=json.loads((OWNER/'tool-trees.json').read_bytes())['trees'];treeFiles=treeLinks=treeDirs=0
for tree in trees:
 root=Path(tree['originalRoot']);assert root.resolve()==root and not root.is_symlink()
 expected={r['path']:r for r in tree['entries']};actual={}
 for directory,dirs,files in os.walk(root,followlinks=False):
  for name in dirs+files:
   p=Path(directory)/name;rel=str(p.relative_to(root));s=p.lstat();r=expected[rel];actual[rel]=True
   if stat.S_ISLNK(s.st_mode):
    assert r['kind']=='symlink'and os.readlink(p)==r['sourceLinkText']and str(p.resolve())==r['resolvedOriginal'];treeLinks+=1
   elif stat.S_ISDIR(s.st_mode):assert r['kind']=='directory';treeDirs+=1
   else:
    assert stat.S_ISREG(s.st_mode)and r['kind']=='file'and stat.S_IMODE(s.st_mode)==r['mode'];verify(r,p);treeFiles+=1
 assert set(actual)==set(expected)
assert treeFiles==4890 and treeLinks==22
for row in plan['links']:
 p=Path(row['source']);assert p.is_symlink()and os.readlink(p)==row['sourceLinkText']and str(p.resolve())==row['resolvedOriginal']
 prefix=next(t['publicationRoot']for t in trees if row['destination'].startswith(t['publicationRoot']+'/'))
 dest=Path('/PROPOSED_PRIVATE_PUBLICATION')/row['destination'];target=os.path.normpath(str(dest.parent/row['newLinkText']));assert target==str(Path('/PROPOSED_PRIVATE_PUBLICATION')/row['mappedTarget'])
checks.append('completeTwoPhysicalToolTrees4890Files22LinksAndDirectoryMembershipNoExecution')
guest=indexed(HERE.with_name('cost-guest-oracle-candidate-v2'),'ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8');assert len(guest['files'])==38
for r in guest['files']:assert(OWNER/'image/guest'/r['path']).read_bytes()==(HERE.with_name('cost-guest-oracle-candidate-v2')/r['path']).read_bytes()
peer=indexed(HERE.with_name('independent-cost-guest-oracle-v2-source-review-v1'),'259a7a31b972aa30eb5be2f82d5f29da91b4f36d7d5fc7aac3aa0f561d0636ed')
checks.append('correctedGuest38ByteIdenticalAndRootPeerIndexedNotOriginal473Positive')
facts=json.loads((OWNER/'image/metadata/native-facts.json').read_bytes());frozen=[]
for fact in facts['variants']:
 meta=json.loads(verify(fact['metadata']).read_bytes());fr=json.loads(verify(fact['freezeReceipt']).read_bytes());assert meta['engineSha256']==fact['engineSha256']and meta['engineBytes']==fact['engineBytes'];assert len(fr['copies'])==1024
 for row in fr['copies']:verify(row)
 assert len(meta['sourceManifest'])==350 and len(meta['componentizeSourceManifest'])==3
 assert meta['zlibPolicy']['runtimeBackendProof']['verified']is False
 assert fr['actualLayoutCompileCommands']==(62 if fact['label']=='normal-off'else 61)and fr['actualEmbeddingCompileCommands']==1
 assert fact['label']in ['normal-off','disabled-off']and fact['gcStress']is False and fact['costPairAdmission']is False
 assert fr['sourceRoot']==fact['sourceRoot']
 for row in meta['sourceManifest']:verify({'sha256':row['sha256'],'bytes':(Path(fr['sourceRoot'])/row['path']).stat().st_size},Path(fr['sourceRoot'])/row['path'])
 frozen.append({'label':fact['label'],'copies':1024,'engineSha256':fact['engineSha256'],'metadataSha256':fact['metadata']['sha256'],'nativeInputs':350,'externalEmbeddingInputs':3,'actualLayout':fr['actualLayoutCompileCommands'],'backendMetadataVerified':False})
checks.append('twoGenuine350FrozenDataFacts1024CopiesEach62or61PlusEmbedding1UnmodifiedMetadataNoAdmission')
map=json.loads((OWNER/'packaging-source-map.json').read_bytes());assert map['functionalPackagingModules']==12 and map['inheritedLocalJsModules']==11
for edge in map['inheritedStaticEdges']:
 a=OWNER/'image/packaging'/edge['importer'];b=OWNER/'image/packaging'/edge['target'];assert a.is_file()and b.is_file();assert str((a.parent/edge['request']).resolve())==str(b.resolve())
assert map['selectorOperationalAdmission']=='CLOSED'and map['normalRawModelOnly']=='validateZlibBuildSourceAdmission'
checks.append('elevenLiteralPackagingModuleEdgesAndBuildOnlyRawManifestBoundary')
for p in OWNER.glob('*.py'):ast.parse(p.read_bytes())
for name in ['authority.mjs','context.mjs','native.mjs','preflight.mjs','bundle.mjs','node-oracle-action.mjs','collector.mjs','durable.mjs','environment.mjs','publish.py']:
 p=OWNER/name;hashfile(p)
checks.append('sourceReadCriticalTenModulesNoModuleImportsOrActionCalls')
reports={}
for name in ['pure','publication','source','syntax']:
 d=json.loads((OWNER/'evidence'/(name+'-results.json')).read_bytes());reports[name]=d
checks.append('owner87Pure31TinyCopy20975Source56ParseReportsAuthenticatedOnlyNotRerun')
# Read the actual selected loader, not a hand-written model of the environment.
loader=Path('/private/tmp/starling-node-compat/native-toolchain-lock/node_modules/rolldown/dist/shared/binding-BXYS21Tf.mjs');text=loader.read_text();assert 'if (process.env.NAPI_RS_NATIVE_LIBRARY_PATH)'in text and '__require(process.env.NAPI_RS_NATIVE_LIBRARY_PATH)'in text;hashfile(loader)
env=(OWNER/'environment.mjs').read_text()
for key in ['NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK']:
 assert key in env
bundle=(OWNER/'bundle.mjs').read_text();assert bundle.index('assertPackagingEnvironment(admitted)')<bundle.index('const {loadToolchain}=await import')
checks.append('M1FourActualRolldownOverridesRejectedBeforeDynamicLoaders')
authority=(OWNER/'authority.mjs').read_text();context=(OWNER/'context.mjs').read_text();preflight=(OWNER/'preflight.mjs').read_text()
assert authority.index('row=descriptor(row)')<authority.index('const canonicalParent=await realpath')
section=authority[authority.index('export async function actionAuthority'):authority.index('export async function reviewedPair')]
assert section.index('const captured=Object.freeze')<section.index('await regular(captured)')and section.index('const fixedOptions=Object.freeze')<section.index('await regular(captured)')
assert context.index('row=descriptor(row)')<context.index('const parent=await realpath')
section=context[context.index('export async function loadPublication'):context.index('export async function loadOracleRender')]
assert section.index('indexDescriptor=descriptor(indexDescriptor)')<section.index('await authority.recheck()')
assert preflight.index('rootAction=descriptor(rootAction);publicationIndex=descriptor(publicationIndex)')<preflight.index('await actionAuthority')
assert 'rootActionSha256:authority.descriptor.sha256'in preflight
checks.append('M2PrivatePrimitiveDescriptorsAndAuthenticatedRootShaCapturedBeforeAwaits')
parent=OWNER.with_name('cost-tooling-candidate-v2');indexed(parent,'6793721e6781bf045825f2a1c83108f97136f682fdae4d725ece4c31c750891b')
hold=HERE.with_name('independent-cost-source-publication-v2-failure-review-v1');indexed(hold,'064b8d4415f6444291db78f485a4b9052c691c90a3818a761a887473e2fa5bd5')
checks.append('ImmutableV2All254AndM3FailurePeer6Unchanged')
import difflib,copy
changes=json.loads((OWNER/'source-deltas.json').read_bytes());assert len(changes['files'])==9
for row in changes['files']:
 before=(parent/row['path']).read_bytes();after=(OWNER/row['path']).read_bytes()
 assert sha(before)==row['beforeSha256']and sha(after)==row['afterSha256']
 assert ''.join(difflib.restore(row['ndiff'],1)).encode()==before
 assert ''.join(difflib.restore(row['ndiff'],2)).encode()==after
for name in changes['unchangedCopiedSourceMembers']:assert(parent/name).read_bytes()==(OWNER/name).read_bytes()
assert len(changes['unchangedCopiedSourceMembers'])==227
checks.append('NineExactForwardReverseSourceDeltasAnd227UnchangedMembers')
parent_plan=json.loads((parent/'publication-plan.json').read_text().replace(str(parent),str(OWNER)).replace('/tmp/starling-node-compat/zlib-cost-source-v2','/tmp/starling-node-compat/zlib-cost-source-v3'))
parent_plan['objects']+=[r for r in plan['objects']if r.get('role')=='historical-parent-M3-precopy-failure-not-current-admission']
for row in parent_plan['objects']:
 if 'mode'in row:row['sourceMode']=row.pop('mode');row['outputMode']=row['sourceMode']
 if Path(row['source']).is_relative_to(OWNER):
  f=Path(row['source']);row.update(sha256=hashfile(f),bytes=f.stat().st_size,sourceMode=stat.S_IMODE(f.stat().st_mode))
for key in ['copyPermissionSchemaVersion','historicalToolingV2IndexSha256','historicalPublicationM3FailurePeerIndexSha256']:parent_plan[key]=plan[key]
parent_plan['logicalCopyBytesBeforeProofCapsules']=sum(r['bytes']for r in parent_plan['objects'])
assert parent_plan==plan and plan['copyPermissionSchemaVersion']==2
for row in plan['objects']:
 assert 'mode'not in row and type(row['sourceMode'])is int and type(row['outputMode'])is int
 assert row['sourceMode']==stat.S_IMODE(Path(row['source']).stat().st_mode)
checks.append('ExactParentPlanRebaseExplicitSourceOutputPermissionSchema2AndFailureCapsules')
for name in ['authority.mjs','context.mjs','environment.mjs','preflight.mjs','native.mjs','bundle.mjs','collector.mjs','durable.mjs','tool-trees.json']:
 assert(parent/name).read_bytes()==(OWNER/name).read_bytes()
assert plan['configuredNativeRoot']=='/private/tmp/starling-node-compat/zlib-source-v4'and plan['frozenNativeRoot']=='/private/tmp/starling-node-compat/production-zlib-v4/native-freeze'
assert '/zlib-cost-source-v3' in (OWNER/'publish.py').read_text()and '/zlib-cost-node-oracle-v3'in(OWNER/'node-oracle-action.mjs').read_text()
checks.append('AllGuardNative350CodecGuestToolPayloadsUnchangedFreshSourceOracleV3Only')
receipt=json.loads((OWNER/'source-receipt.json').read_bytes())
assert [receipt[k]for k in ['pureChecks','ownedTextPublisherChecks','sourceDataChecks','parseChecks']]==[87,31,20975,56]
assert receipt['ownerActionMainsInvoked']is False and receipt['allPositiveActionAuthorities']is None
future=json.loads((OWNER/'future-authority.json').read_bytes());assert future['actionsAllowed']is False and all(v is None for k,v in future.items()if k not in ['schemaVersion','state','actionsAllowed','operationalAdmission'])
assert "['source-publication','node-oracle','bundle-source']" in authority and 'IMPLEMENTED_ACTIONS.includes(action)'in authority
checks.append('OnlyThreeImplementedSourceActionsAllActualPositiveAuthorityNullFutureFourActionsRefuse')
root_pair=OWNER.with_name('reviewed-cost-native-pair-v1');pair_index=indexed(root_pair,'58c622760959e3078d9f0ebdb6b95946e54d770a12bfca41a555ec778e066077');assert len(pair_index['files'])==10
pair=json.loads((root_pair/'results.json').read_bytes());assert hashfile(root_pair/'results.json')=='7194d9c16afe28f0e20009add3f025a992088bfd8c8c2a2301601c1fe03b5bed'
assert pair['state']=='ROOT_REVIEWED_GENUINE_ZLIB350_COST_PAIR_V1'and pair['nativeInputs']==350 and pair['operationalAdmission']is False and pair['sourcePromotionAllowed']is False and pair['actionAuthorityIssued']is False
for fact in facts['variants']:
 chosen=pair['nativeOn'if fact['label']=='normal-off'else'nativeOff'];assert chosen['engine']['sha256']==fact['engineSha256']and chosen['engine']['bytes']==fact['engineBytes']
 for key in ['metadata','freezeReceipt']:
  for field in ['path','sha256','bytes']:assert chosen[key][field]==fact[key][field]
 meta=json.loads(Path(fact['metadata']['path']).read_bytes());sdk=[meta['zlibPolicy']['codecWitness']['archive'],*meta['zlibPolicy']['codecWitness']['headers']]
 assert [{k:row[k]for k in ['path','sha256','bytes']}for row in sdk]==pair['selectedSDKReferences']
for row in pair['selectedSDKReferences']:verify(row)
checks.append('LateRootDataOnlyPair10AndSelectedSDKArchiveFourHeadersAgreeWithFiniteGuardNoActionAuthority')
publisher=(OWNER/'publish.py').read_text();test=(OWNER/'test-publication.py').read_text()
assert "need('mode'not in row,'Ambiguous source/output mode field refuses')"in publisher
assert "stat.S_IMODE(before.st_mode)==row['sourceMode']"in publisher and "mode=row['outputMode']"in publisher
assert "'sourceMode':row['sourceMode'],'outputMode':row['outputMode']"in publisher
assert "'sourceMode':row['mode']"in publisher and "objects.append(capsule_copy_row(r,"in publisher
assert "'sourceMode':stat.S_IMODE(Path(row['source']).lstat().st_mode),'outputMode':0o600"in publisher
assert 'source.chmod('not in test and 'Actual0644 fixture required'in test and "row['sourceMode']==0o644 and row['outputMode']==0o600"in test
assert "m.source({**row,'sourceMode':0o600})"in test and "m.source({**row,'mode':0o600})"in test
assert 'Original identity/hash/mode unchanged; no chmod'in test
checks.append('M3DistinctPermissionRolesAllReadCopyVerifyAndDynamicCapsulePathsNoOriginalChmodOrHashWeakening')
publication=reports['publication'];assert publication['returncode']==0 and publication['report']['checks']==31
scratch=Path(publication['report']['scratch']);original=scratch/'input.txt';copyfile=scratch/'owned/data/source.txt'
assert original.is_file()and copyfile.is_file()and original.read_bytes()==copyfile.read_bytes()==b'only ordinary text'
assert stat.S_IMODE(original.stat().st_mode)==0o644 and stat.S_IMODE(copyfile.stat().st_mode)==0o600
assert original.stat().st_ino!=copyfile.stat().st_ino and copyfile.stat().st_nlink==1
hashfile(original);hashfile(copyfile)
checks.append('ActualSavedOwnedTinyTest0644Source0600OutputEqualBytesDistinctInodes31ChecksSupportedBySourceAndTerminal')
assert not Path('/tmp/starling-node-compat/zlib-cost-source-v2').exists()and not Path('/tmp/starling-node-compat/zlib-cost-source-v3').exists()
checks.append('FailedV2AndFutureV3PublicationTargetsAbsentAtReview')
result={'schemaVersion':1,'state':'INDEPENDENT_ZLIB_COST_TOOLING_SOURCE_REVIEW_PASSED','toolingSourceIndexSha256':EXPECTED,'sourceOnly':True,'sourceReviewPassed':True,'ownerActionsInvoked':False,'checks':checks,'passedDataAndSourceChecks':len(checks),'indexedFiles':286,'preparationInputs':5357,'futurePublicationObjects':5072,'toolFiles':treeFiles,'toolLinks':treeLinks,'toolDirectories':treeDirs,'frozenFacts':frozen,'closedFindings':['COST-TOOLING-M3'],'inheritedM1AndM2CorrectionsByteIdentical':True,'remainingConcreteSourceBlockers':[],'scope':'First-cut publication/parent guards/untimed Node-oracle body/source bundler/collector models only; no action authorization or runtime proof','knownUnimplemented':['component-build','guest-correctness','pilot','timing'],'futureAllPositiveAuthority':None,'allRecordsStreamHashed':True,'uniquePhysicalContentHashReads':len(cache),'lexicalPathsObserved':len(identities),'runtimeOrReadinessOrAcceptanceClaim':False,'ownerTestsOrPublisherOrPreflightOrNativeGateOrOracleOrBundlerOrCodecOrGuestOrHostExecuted':False,'wasmtimeExecutableCurrentActionDependency':False,'allFutureActualABIStringParserLargestArgvCorrectnessPilotTimingGatesClosed':True}
(HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n');(HERE/'rehashed-files.json').write_text(json.dumps({'schemaVersion':1,'files':sorted(identities.values(),key=lambda r:r['path']),'streamBlockBytes':1048576},indent=2)+'\n');print(json.dumps({'state':result['state'],'checks':len(checks),'paths':len(identities),'physicalHashReads':len(cache),'blockers':0}))
