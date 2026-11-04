from pathlib import Path
import ast,hashlib,json,os,re,stat
HERE=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-zlib/independent-cost-tooling-source-review-v1')
OWNER=HERE.with_name('cost-tooling-candidate-v1')
EXPECTED='f5f13bfa0256a3e89d87827ea40d12dfbf617a23c304ba3b8335167c02bc3049'
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
index=indexed(OWNER,EXPECTED);assert len(index['files'])==224;checks.append('all224OwnerIndexedFiles')
inputs=json.loads((OWNER/'input-freeze.json').read_bytes());assert len(inputs['files'])==5089
for r in inputs['files']:verify(r)
checks.append('all5089PreparationRowsStreamRehashedNoOriginalManifestReinterpretation')
plan=json.loads((OWNER/'publication-plan.json').read_bytes());assert len(plan['objects'])==5047 and len(plan['links'])==22
assert len({r['destination']for r in plan['objects']})==5047
for r in plan['objects']:verify(r)
assert sum(r['bytes']for r in plan['objects'])==350823776
checks.append('all5047FuturePublicationPhysicalObjectsIncludingNativeWasmSourceAdapterAndToolFiles')
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
checks.append('owner80Pure22TinyCopy15851Source52ParseReportsAuthenticatedOnlyNotRerun')
# Read the actual selected loader, not a hand-written model of the environment.
loader=Path('/private/tmp/starling-node-compat/native-toolchain-lock/node_modules/rolldown/dist/shared/binding-BXYS21Tf.mjs');text=loader.read_text();assert 'if (process.env.NAPI_RS_NATIVE_LIBRARY_PATH)'in text and '__require(process.env.NAPI_RS_NATIVE_LIBRARY_PATH)'in text;hashfile(loader)
env=(OWNER/'environment.mjs').read_text();assert 'NAPI_RS_NATIVE_LIBRARY_PATH'not in env
bundle=(OWNER/'bundle.mjs').read_text();assert bundle.index('assertPackagingEnvironment(admitted)')<bundle.index('const {loadToolchain}=await import')
findings=[{'id':'COST-TOOLING-M1','disposition':'HOLD','source':'environment.mjs:10','evidence':'actual selected Rolldown binding-BXYS21Tf.mjs:69-70','cause':'NAPI_RS_NATIVE_LIBRARY_PATH is consumed by __require before normal binding selection. Environment guard rejects NODE_OPTIONS/NODE_PATH only, permitting native code outside copied authenticated tool trees before later module graph audit.','requiredCorrection':'New immutable successor rejects this binding override and unreviewed NAPI_RS_FORCE_WASI/NAPI_RS_WASI_FLAVOR before dynamic loaders; pure negative environment checks and coherent publication closure.'}, {'id':'COST-TOOLING-M2','disposition':'HOLD_FOR_PRIVATE_CAPTURE_CORRECTION','source':'context.mjs loadPublication / preflight.mjs costPreflight','cause':'Recheck closes over caller-owned publicationIndex descriptor; costPreflight returns rootActionSha256 from caller-owned descriptor after awaits. Existing actionAuthority captures its own copy, but these other advertised bindings do not.','requiredCorrection':'Capture private immutable path/SHA/bytes and authenticated Root-action SHA before awaits; return/recheck these fixed primitives, with pure mutation tests.'}]
result={'schemaVersion':1,'state':'INDEPENDENT_ZLIB_COST_TOOLING_SOURCE_REVIEW_HELD','toolingSourceIndexSha256':EXPECTED,'sourceOnly':True,'sourceReviewPassed':False,'ownerActionsInvoked':False,'checks':checks,'passedDataChecks':len(checks),'indexedFiles':224,'preparationInputs':5089,'futurePublicationObjects':5047,'toolFiles':treeFiles,'toolLinks':treeLinks,'toolDirectories':treeDirs,'frozenFacts':frozen,'findings':findings,'draftFindingClosedBeforeSeal':'native.mjs local freeze receipt shadowed deep-freeze helper; owner changed helper and genuine pure return seam before f5f13 seal','knownUnimplemented':['component-build','guest-correctness','pilot','timing'],'futureAllPositiveAuthority':None,'allRecordsStreamHashed':True,'uniquePhysicalContentHashReads':len(cache),'lexicalPathsObserved':len(identities),'runtimeOrReadinessOrAcceptanceClaim':False,'ownerTestsOrPublisherOrPreflightOrNativeGateOrOracleOrBundlerOrCodecOrGuestOrHostExecuted':False}
(HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n');(HERE/'rehashed-files.json').write_text(json.dumps({'schemaVersion':1,'files':sorted(identities.values(),key=lambda r:r['path']),'streamBlockBytes':1048576},indent=2)+'\n');print(json.dumps({'state':result['state'],'checks':len(checks),'paths':len(identities),'physicalHashReads':len(cache),'findings':len(findings)}))
