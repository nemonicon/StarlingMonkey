"""Source/data preparation only. No freeze, owner helper, copy, subprocess or build."""
from pathlib import Path
import hashlib,json,os,shlex,stat
OWN=Path(__file__).resolve().parent;S=OWN.parent;REPO=S.parents[2]
SOURCE=Path('/private/tmp/starling-node-compat/combined-native355-v1-source')
WORK=Path('/private/tmp/starling-node-compat/combined-native355-v2-build')
FREEZE=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze')
EXTERNAL=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze-external-root')

def data(p):return json.loads(Path(p).read_bytes())
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def desc(p):
 p=Path(p);return dict(path=str(p),sha256=digest(p),bytes=p.stat().st_size)
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def family(row):
 root=Path(row['path']).parent;value=data(row['path']);return [row]+[dict(path=str(root/r['path']),sha256=r['sha256'],bytes=r['bytes']) for r in value['files']]

def prepare(build_pair,build_contract,ledger,aliases,hardlinks):
 assert build_pair is not None and build_contract is not None and ledger is not None,'Actual independent BUILD review must be sealed first'
 proof=data(build_pair['result']['path']);assert proof['schemaVersion']==1 and proof['state']=='INDEPENDENT_COMBINED355_NATIVE_BUILD_V2_RESULTS_REVIEW_PASSED_V1' and proof['verifiedPassed'] is True
 assert build_pair['result'] in family(build_pair['index']) and build_contract in family(build_pair['index'])
 contract=data(build_contract['path'])
 for k,v in contract['requiredFixedValues'].items():assert proof[k]==v
 root_desc=desc(S/'combined-native355-v2-build-root-results.json');root=data(root_desc['path']);meta=data(root['metadata']['path']);native=data(S/'combined-native-build-controller-candidate-v2/references.json');policy=data(native['policy']['path'])
 assert meta['engineSha256']==root['engine']['sha256']=='355550f1d0bdc7455fd81ffbd739ac1453a56f3537b277eb644441d87434af3b' and root['metadata']['sha256']=='5f3be8851739635beaee6550ad03c7afed9e6eebb0607840ebd12e4a095354d3'
 assert len(meta)==80 and len(meta['sourceManifest'])==355 and len(meta['componentizeSourceManifest'])==3 and len(meta['selectedModuleManifests'])==11
 original_rows=data(ledger['path'])['files'];assert len(original_rows)==len({r['path'] for r in original_rows});expected={r['path']:r for r in original_rows}
 captures=[];destinations=set()
 def add(path,name,role,expected_sha=None):
  row=desc(path);assert expected_sha is None or row['sha256']==expected_sha
  assert name and not name.startswith('/') and '\\' not in name and all(v not in ('','.','..') for v in name.split('/')) and name not in destinations;destinations.add(name)
  assert not Path(path).is_symlink();captures.append(dict(source=row,destination=name,role=role));return row
 project=Path(meta['cmakeCachePath']).parent;external=Path(meta['combinedNativeSourcePolicy']['externalConfiguredSourceRoot']);database=data(meta['compileCommandsPath'])
 add(root['engine']['path'],'normal-off.engine.wasm','raw-native-engine',root['engine']['sha256']);add(root['metadata']['path'],'normal-off.engine.wasm.build.json','raw-native-metadata80-byte-exact',root['metadata']['sha256'])
 for path,name,role,sha in [(meta['cmakeCachePath'],'normal-off-CMakeCache.txt','actual-cmake-cache',meta['cmakeCacheSha256']),(meta['compileCommandsPath'],'build-evidence/compile_commands.json','actual-68-row-compile-database',meta['compileCommandsSha256']),(project/'build.ninja','build-evidence/build.ninja','actual-Ninja-DATA',None),(project/'CMakeFiles/rules.ninja','build-evidence/rules.ninja','actual-Ninja-rules-DATA',None),(project/'cxx-wrapper','build-evidence/cxx-wrapper','actual-compiler-wrapper-DATA',None),(project/'starling-raw.wasm/null.cpp','build-evidence/null.cpp','actual-generated-null-source',None)]:add(path,name,role,sha)
 for key,name in [('actualBuildResult','result.json'),('buildLog','build.log'),('ownedWorkerTerminal','external-parent-terminal.json')]:
  row=root.get(key) or proof.get(key)
  if row is None and key=='buildLog':row=data(root['actualBuildResult']['path'])['buildLog']
  add(row['path'],'build-evidence/'+name,'actual-build-process-DATA',row['sha256'])
 add(root_desc['path'],'build-evidence/root-observation.json','actual-Root-build-observation',root_desc['sha256'])
 stage=data(native['stageResult']['path']);assert len(stage['copies'])==1613
 for row in stage['copies']:
  path=SOURCE/row['path'];add(path,'source/'+row['path'],'current-native355-source' if any(r['path']==row['path'] for r in meta['sourceManifest']) else 'configured-tool-origin-DATA',row['sha256'])
 for row in meta['componentizeSourceManifest']:add(external/row['path'],'componentize-source/'+row['path'],'actual-external-embedding-source',row['sha256'])
 add(native['policy']['path'],'build-evidence/combined355-policy.json','actual-retry-policy',native['policy']['sha256'])
 for key in ('recipe','helper','metadataModel'):add(native[key]['path'],'build-evidence/retry-producer/'+Path(native[key]['path']).name,'actual-retry-producer-DATA',native[key]['sha256'])
 # Derive the actual selected static libraries from the real Ninja link edge,
 # not by importing a historical classifier or listing every cached archive.
 link=[line for line in (project/'build.ninja').read_text().splitlines() if line.startswith('build starling-raw.wasm/starling-raw.wasm:')];assert len(link)==1
 tokens=shlex.split(link[0].split(' || ',1)[0]);libs=[]
 for token in tokens:
  if token.endswith('.a'):
   path=Path(token);path=path if path.is_absolute() else project/path
   if path not in libs:libs.append(path)
 assert len(libs)==proof['coverage']['uniqueLinkedArchives']==29
 for i,path in enumerate(libs):add(path,'static-libraries/'+str(i)+'-'+path.name,'selected-static-library')
 objects=[]
 for row in database:
  words=shlex.split(row['command']);out=Path(words[words.index('-o')+1]);out=out if out.is_absolute() else Path(row['directory'])/out;objects.append(out)
 for command in meta['actualEmbeddingCompileCommands']:
  words=shlex.split(command);out=Path(words[words.index('-o')+1]);out=out if out.is_absolute() else project/out;objects.append(out)
 assert len(objects)==len(set(objects))==69
 for path in objects:add(path,'build-evidence/objects/'+path.relative_to(project).as_posix(),'actual-compiled-object-DATA')
 selected=[('timer-installation',meta['resourceOwnershipPolicy']['timerInstallation']['path']),('fresh-ABI-preconfigure',meta['combinedNativeSourcePolicy']['freshAbiEvidenceFile']['path']),('Rust-Cargo.toml',meta['generatedRustProject']['manifestPath']),('Rust-Cargo.lock',meta['generatedRustProject']['lockPath']),('OpenSSL-before',meta['openssl']['completeSourceAudit']['beforeReportPath']),('OpenSSL-receipt',meta['openssl']['receiptPath']),('OpenSSL-configure',meta['openssl']['configureRecipe']['path']),('OpenSSL-configdata',meta['openssl']['configdata']['path'])]
 for role,path in selected:add(path,'build-evidence/'+role+'-'+Path(path).name,'actual-'+role+'-DATA')
 for path in sorted(WORK.glob('source-inputs-*'))+sorted(WORK.glob('componentize-native-inputs-*'))+sorted(WORK.glob('recipe-*.sha256')):add(path,'build-evidence/prebuild/'+path.name,'actual-prebuild-capture-DATA')
 for i,row in enumerate(meta['wasiSdkVersionFiles']):add(row['path'],'build-evidence/sdk-VERSION-'+str(i),'actual-SDK30-version-DATA')
 rust=meta['privateRustupBootstrapPolicy'];add(rust['beforeInstallRecord']['path'],'build-evidence/private-rustup-settings-before-install.json','historical-preinstall-record-DATA',rust['beforeInstallRecord']['sha256']);add(rust['settingsAtBuildCompletion']['path'],'build-evidence/private-rustup-settings-at-build-completion.toml','actual-current-private-Rustup-settings',rust['settingsAtBuildCompletion']['sha256'])
 for row in meta['zlibSelectedCodecInput']['headers']:add(row['path'],'build-evidence/selected-codec/'+Path(row['path']).name,'actual-selected-MOZ_Z-header',row['sha256'])
 for row in family(build_pair['index']):add(row['path'],'build-proof/'+Path(row['path']).relative_to(Path(build_pair['index']['path']).parent).as_posix(),'actual-independent-BUILD-proof-DATA',row['sha256'])
 # Record expected copy inputs exactly; whole original ledger is still checked
 # separately and is explicitly NOT represented as fully copied by this plan.
 for row in captures:
  value=row['source']
  if row['role']=='actual-independent-BUILD-proof-DATA':assert value in family(build_pair['index'])
  else:assert value['path'] in expected and expected[value['path']]==value,'Planned actual origin absent from independent BUILD ledger: '+value['path']
 tools=native['hostTools'];python=next(t['executable'] for t in tools if t['name']=='python3');ninja=next(t['executable'] for t in tools if t['name']=='ninja')
 for role,row in [('admission-python',python),('commands-ninja',ninja)]:add(row['path'],'tool-data/'+role,'selected-resolved-tool-DATA',row['sha256'])
 fixed_descriptors={key:proof[key] for key in ('actualBuildResult','rootObservation','rootAuthority','rootConfig','ownedWorkerTerminal','engine','metadata','buildLog')}
 families=[dict(role='actual-independent-build-review',index=build_pair['index']),dict(role='genuine-retry-producer',index=root['controllerIndex']),dict(role='genuine-freezer-primitives-donor',index=desc(S/'task-selection-freezer-candidate-v1/index.json'))]
 for item in native['families']:
  assert set(item)=={'path','sha256','bytes'}
  if not any(v['index']==item for v in families):families.append(dict(role='inherited-authenticated-build-source-family',index=item))
 refs=dict(schemaVersion=1,state='COMBINED355_FREEZER_SOURCE_REFERENCES_NOT_AUTHORITY_V1',nativeSourceIndex=native['integrationIndex'],buildControllerIndex=root['controllerIndex'],actualBuildReview=build_pair,actualBuildContract=build_contract,buildInputLedger=ledger,verifiedBuildReferenceCount=len(original_rows),buildProofDescriptors=fixed_descriptors,actualBuildResult=root['actualBuildResult'],actualBuildRootObservation=root_desc,engine=root['engine'],metadata=root['metadata'],policy=native['policy'],layer=native['helper'],recipe=native['recipe'],configuredModel=native['metadataModel'],externalSourceManifest=meta['componentizeSourceManifest'],externalSourceRoot=str(external),selectedManifests=meta['selectedModuleManifests'],selectedManifestValues=[data(SOURCE/r['path']) for r in meta['selectedModuleManifests']],cmakeCache=desc(meta['cmakeCachePath']),compileCommands=desc(meta['compileCommandsPath']),privateRustupBootstrapPolicy=rust,rustupBeforeRecord=rust['beforeInstallRecord'],rustupBeforeValue=data(rust['beforeInstallRecord']['path']),rustupCurrentSettings=rust['settingsAtBuildCompletion'],rustupCurrentSettingsText=Path(rust['settingsAtBuildCompletion']['path']).read_text(),copiedMetadataPolicyKeys=[key for key in meta if key.endswith('Policy') and key!='privateRustupBootstrapPolicy'],referenceAliasWitness=proof['referenceAliases'],referenceAliases=aliases,declaredArchiveHardlinks=hardlinks,python=python,ninja=ninja,configuredSourceRoot=str(SOURCE),workRoot=str(WORK),freezeRoot=str(FREEZE),externalOutputRoot=str(EXTERNAL),families=families,files=[root_desc,*fixed_descriptors.values(),native['stageResult'],*native['protectedTreeInventories']],sourceIndependentReview=None,rootAuthority=None,actualFreezeResult=None,reviewedEnginePins=None,bootstrapFrame=None,runtimeAuthority=None,operationalAdmission=False)
 save('references.json',refs);prepare_protection(original_rows,native);save('capture-plan.json',dict(schemaVersion=1,state='PROSPECTIVE_EXPLICIT_COMBINED355_COPY_PLAN_NOT_EXECUTED_V1',baseCopies=len(captures),staticLibraries=len(libs),objectFiles=69,verifiedReferenceCount=len(original_rows),notAllVerifiedInputsPhysicallyCopied=True,baseCopyBytes=sum(r['source']['bytes'] for r in captures),copies=captures))
 return refs
def prepare_protection(original_rows,native):
 files=[];pairs=[];trees=[];known={r['path']:r for r in original_rows}
 def physical(path):return Path('/private'+path) if path.startswith('/tmp/') else Path(path)
 for row in original_rows:
  p=physical(row['path']);s=p.stat();assert not p.is_symlink() and stat.S_ISREG(s.st_mode)
  files.append(dict(descriptor=row,mode=stat.S_IMODE(s.st_mode),nlink=s.st_nlink))
 stage=data(native['stageResult']['path'])
 for row in stage['copies']:
  a=dict(path=str(SOURCE/row['path']),sha256=row['sha256'],bytes=row['bytes']);b=dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes'])
  assert known[a['path']]==a and known[b['path']]==b
  pairs.append(dict(copy=a,original=b,copyMode=stat.S_IMODE(physical(a['path']).stat().st_mode),originalMode=row['sourceMode']))
 def tree(root,expected=None):
  root=Path(root);files=[];links={}
  for p in root.rglob('*'):
   name=p.relative_to(root).as_posix()
   if p.is_symlink():links[name]=os.readlink(p)
   elif p.is_file():files.append(name)
  if expected is not None:assert set(files)==set(expected) and not links
  trees.append(dict(root=str(root),mode=stat.S_IMODE(root.stat().st_mode),files=sorted(files),links=links))
 for row in native['protectedTreeInventories']:
  inv=data(row['path']);root=Path(inv['root']);tree(root,[r['path'] for r in inv['files']])
  for r in inv['files']:
   current=dict(path=str(root/r['path']),sha256=r['sha256'],bytes=r['bytes']);assert known[current['path']]==current and stat.S_IMODE((root/r['path']).stat().st_mode)==r['mode']
 # Stage membership includes the real detached clone, not merely plan destinations.
 tree(SOURCE)
 save('protection.json',dict(schemaVersion=1,state='EXACT_CURRENT_ORIGINAL_AND_PRIOR_FROZEN_PROTECTION_DATA',files=files,modePairs=pairs,trees=trees,stageCopies=1613,failedWorkFiles=755,allOriginalReferencesProtected=True,sourceAndWorkContextsNotRewritten=True,oldNormalScope='Only the actual 4515-row controller closure, including356 secret-frozen source rows and4 selector-frozen rows; no new recursive whole historical frozen-receipt/original claim'))

if __name__=='__main__':
 raise SystemExit('Source/data preparation API only: requires explicit genuine sealed independent BUILD descriptors; no automatic intake or action')
