"""Read-only recovery observation after the completed ONE syntax command; no retry."""
from pathlib import Path
import ast,hashlib,json,os,shlex,shutil,stat,subprocess,sys
OWN=Path(__file__).resolve().parent
STAGE=Path('/private/tmp/starling-node-compat/node-builtin-namespace-identity-v1-sdk-syntax')
OBS=Path('/private/tmp/starling-node-compat/node-builtin-namespace-identity-v1-sdk-syntax-observation')
SOURCE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')
def desc(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def read(p):return json.loads(Path(p).read_bytes())
def save(p,v):
 p=Path(p);p.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 with p.open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
assert not(OWN/'index.json').exists()and not OBS.exists();OBS.mkdir(mode=0o700)
plan=read(STAGE/'plan.json');before=read(STAGE/'protection-before.json');terminal=read(STAGE/'command/terminal.json')
assert terminal['rawExitCode']==0 and terminal['allObservedOwnedGroupsGone']and terminal['parentOwnedGroupGone']
assert not terminal['forcedCleanup']and not terminal['timeout']and not terminal['signals']and not terminal['errors']and not terminal['remainingObservedPids']
assert(STAGE/'command/stdout.log').read_bytes()==(STAGE/'command/stderr.log').read_bytes()==b''
for path,r in before['files'].items():
 p=Path(path);s=p.stat();actual=desc(p);assert actual['sha256']==r['sha256']and actual['bytes']==r['bytes']and(stat.S_IMODE(s.st_mode),s.st_dev,s.st_ino,s.st_nlink)==(r['mode'],r['device'],r['inode'],r['links']),path
for a in before['sdkAliases']:assert Path(a['path']).is_symlink()and os.readlink(a['path'])==a['linkText']and str(Path(a['path']).resolve())==a['resolved']
expected={p for p in before['files']if p.startswith(str(SOURCE)+'/')}
observed={str(p)for p in SOURCE.rglob('*')if '.git'not in p.relative_to(SOURCE).parts and not p.is_symlink()and p.is_file()}
assert expected==observed and len(observed)==2147
dep=STAGE/'script-loader.d';raw=dep.read_text().replace('\\\n',' ');deps=shlex.split(raw.split(':',1)[1]);assert deps
matched=[]
for path in deps:
 p=Path(path).resolve();r=desc(p)
 if str(p)==plan['privateMainInput']['path']:assert r==plan['privateMainInput'];kind='private-afterimage'
 else:
  prior=before['files'].get(str(p));assert prior,p
  assert r['sha256']==prior['sha256']and r['bytes']==prior['bytes'];kind='authenticated-before-frontend'
 matched.append(dict(reportedPath=path,resolved=r,kind=kind))
final=dict(schemaVersion=1,state='READ_ONLY_POST_SYNTAX_INPUT_PROTECTION_CONFIRMED',protectedFiles=len(before['files']),configuredRegularFiles=len(observed),allOriginalHashesModesInodesLinksUnchanged=True,exactMembershipSetsUnchanged=True,sdkAliasesUnchanged=len(before['sdkAliases']),actualDependencyOccurrences=len(deps),uniqueActualDependencyFiles=len({r['resolved']['path']for r in matched}),compilerOrProcessOrGuestRerun=False)
save(OBS/'observation.json',final);save(OBS/'dependencies.json',dict(schemaVersion=1,dependencyFile=desc(dep),files=matched))
save(OWN/'original-driver-failure.json',dict(schemaVersion=1,kind='Assistant-tool-observed-driver-exit-not-clang-terminal',toolSessionId=68282,rawToolDriverExitCode=1,clangRawExitCode=0,phase='post-action membership observation',exactFailedSource="assert sorted(str(p)for p in SOURCE.rglob('*')if '.git'not in p.relative_to(SOURCE).parts and not p.is_symlink()and p.is_file())==source_files",cause='Initial list uses sorted(Path) while final list uses sorted(str), whose ordering differs for some directory/file path components. Actual2147 membership sets are identical.',executedDriver=plan['driverSource'],failurePreserved=True,compilerRerun=False))
copy_map=[]
for name in ['plan.json','overlay.json','command/terminal.json','command/started.json','command/stdout.log','command/stderr.log','script-loader.d']:
 src=STAGE/name;dst=OWN/'syntax-evidence'/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes());copy_map.append(dict(original=desc(src),copy=desc(dst)))
save(OWN/'syntax-raw-copy-map.json',dict(schemaVersion=1,files=copy_map,originalSyntaxRootUnchanged=True))
metadata=read(plan['actualMetadata']['path']);manifest=metadata['sourceManifest'];proposed=[dict(r,sha256=read(OWN/'derivation.json')['after']['sha256'])if r['path']=='runtime/script_loader.cpp'else r for r in manifest]
assert len(proposed)==357 and sum(a==b for a,b in zip(manifest,proposed))==356
save(OWN/'prospective-source-manifest.json',dict(schemaVersion=1,unapplied=True,baseMetadata=plan['actualMetadata'],nativeSourceFiles=357,retainedNativeFiles=356,changedNativeFiles=1,newNativeFiles=0,manifest=proposed,externalEmbeddingSources=metadata['componentizeSourceManifest'],actualNewEngine=None,actualNewMetadata=None,productionOrStagedSourceChanged=False))
pure=subprocess.run([sys.executable,'-B',str(OWN/'test-model.py')],capture_output=True,timeout=30);(OWN/'model-test.stdout.json').write_bytes(pure.stdout);(OWN/'model-test.stderr.log').write_bytes(pure.stderr);assert pure.returncode==0 and not pure.stderr
node=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node');assert desc(node)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
grammar=[]
for name in ['bare-first.mjs','prefixed-first.mjs']:
 argv=[str(node),'--check',str(OWN/name)];p=subprocess.run(argv,env={k:v for k,v in os.environ.items()if k not in ['NODE_OPTIONS','NODE_PATH']},capture_output=True,timeout=30)
 (OWN/(name+'.grammar.stdout.log')).write_bytes(p.stdout);(OWN/(name+'.grammar.stderr.log')).write_bytes(p.stderr);assert p.returncode==0 and not p.stdout and not p.stderr;grammar.append(dict(argv=argv,rawExitCode=0,stdoutBytes=0,stderrBytes=0))
for p in OWN.glob('*.py'):ast.parse(p.read_bytes())
save(OWN/'grammar-results.json',dict(schemaVersion=1,records=grammar,pythonAsts=len(list(OWN.glob('*.py'))),fixtureImportedOrExecuted=False))
save(OWN/'results.json',dict(schemaVersion=1,state='UNAPPLIED_BUILTIN_NAMESPACE_ALIAS_SOURCE_WITH_ONE_FRONTEND_CHECK_V1',sourceOnly=True,sourcePrepared=True,productionOrStagedSourceChanged=False,baseEngineSha256='9aec9297122c33b60790fcf4e1ce909db0200a426c04de98074e39046aa0f16e',before=read(OWN/'derivation.json')['before'],after=read(OWN/'derivation.json')['after'],nativeSourceFiles=357,retainedNativeFiles=356,changedNativeFiles=1,newNativeFiles=0,externalEmbeddingSources=3,publicExportOrCMakeFlagChanges=False,aliasCondition='Requested bare builtin and node:-prefixed builtin are both explicitly registered to the exact same rooted JSObject.',canonicalKeyRemainsRegistered=True,rootedCanonicalIdAcrossCompilation=True,jsStringConcatenationPreservesUnicodeAndNuls=True,defineBuiltinApiUnchanged=True,syntheticModelCases=read(OWN/'model-test.stdout.json')['checks'],nodeGrammarChecks=2,sdkFrontendCommandsExecuted=1,clangRawExitCode=0,clangStreamsEmpty=True,allCompilerOwnedGroupsGone=True,originalDriverToolExitCode=1,originalDriverFailure=desc(OWN/'original-driver-failure.json'),postFailureReadOnlyObservation=desc(OBS/'observation.json'),actualDependencyEvidence=desc(OBS/'dependencies.json'),syntaxPlan=desc(STAGE/'plan.json'),sdkRegularFilesAuthenticatedBeforeAndAfter=plan['sdkRegularFiles'],smHeadersAuthenticatedBeforeAndAfter=plan['spidermonkeyHeaders'],protectedOriginalFiles=final['protectedFiles'],allOriginalHashesModesInodesLinksAndMembershipPreserved=True,objectCodeOrLinkOrNativeBuildInvoked=False,fixtureOrGuestOrEngineOrCryptoOperationInvoked=False,actualNewEngine=None,actualNewMetadata=None,sourceIndependentReview=None,rootNativeBuildAuthority=None,publicProfileAdmission=False,namespaceFixRuntimeObserved=False,liveEvpSnapshotOrZeroizationOrReuseOrSecurityOrCostAcceptance=False,limits=['One host SDK frontend check proves syntax/type acceptance only, not link/ABI/GC correctness or runtime alias identity.','Original driver failed only at its own final list-order assertion; exact original source is retained and no compiler retry occurred. New read-only observation checks hashes/modes/inodes and exact sets.','Fixtures are raw-native-import future differential inputs, not executed observations; host provider/version values remain separate.','A genuine new native357 generation/metadata and actual two-import-order guest checks remain required before any adoption.']))
save(OWN/'source-receipt.json',dict(schemaVersion=1,result=desc(OWN/'results.json'),derivation=desc(OWN/'derivation.json'),futureSourceManifest=desc(OWN/'prospective-source-manifest.json'),fixtures=desc(OWN/'fixture-plan.json'),syntaxRawCopyMap=desc(OWN/'syntax-raw-copy-map.json'),originalDriverFailure=desc(OWN/'original-driver-failure.json'),postFailureObservation=desc(OBS/'observation.json'),operationalGuestOrNativeBuildAcceptance=False))
rows=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():r=desc(p);r['path']=p.relative_to(OWN).as_posix();rows.append(r)
save(OWN/'index.json',dict(schemaVersion=1,state='SEALED_UNAPPLIED_NATIVE_ALIAS_SOURCE_SYNTAX_ONLY_NO_ADMISSION_V1',files=rows))
assert {r['path']for r in rows}|{'index.json'}=={p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}
for n in ['index.json','results.json','source-receipt.json']:print(json.dumps(desc(OWN/n)))
