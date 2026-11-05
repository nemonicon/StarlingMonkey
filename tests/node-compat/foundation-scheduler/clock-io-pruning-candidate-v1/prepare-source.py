"""Read/hash Source preparation only. No adapter publication or build action."""
from pathlib import Path
import difflib,hashlib,json,os,re,stat,tarfile
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
BASE=Path('/private/tmp/starling-node-compat/import-abi-clock-v2-build/source')
RUST=Path('/Users/dan/.rustup/toolchains/1.96.1-aarch64-apple-darwin')
TOOLS=Path('/private/tmp/starling-node-compat/toolchain')
REG=Path('/Users/dan/.cargo/registry/cache/index.crates.io-1949cf8c6b5b557f')
NEW=Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-source')
WORK=Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-build')
PACKAGE=Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-package')


def d(path):
    p=Path(path);assert p.is_file()and not p.is_symlink(),str(p);a=p.stat();h=hashlib.sha256()
    with p.open('rb')as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
    z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)


def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def tree(root):
    rows=[];links=[]
    for p in sorted(root.rglob('*')):
        relative=str(p.relative_to(root))
        if p.is_symlink():
            target=p.resolve();assert target.is_relative_to(root.resolve())and target.is_file();links.append(dict(path=relative,target=os.readlink(p),resolved=d(target)));continue
        if p.is_file():rows.append(dict(relativePath=relative,mode=stat.S_IMODE(p.stat().st_mode),descriptor=d(p)))
        else:assert p.is_dir()
    return dict(root=str(root),files=rows,symlinks=links)


def pair(folder):return dict(index=d(folder/'index.json'),result=d(folder/'results.json'))


def locked_packages(text):
    packages=[];seen=set()
    for block in text.split('[[package]]')[1:]:
        row={key:re.findall(r'(?m)^'+key+r' = "([^"]+)"$',block)for key in['name','version','source','checksum']}
        assert all(len(row[key])==1 for key in['name','version'])and all(len(row[key])<=1 for key in['source','checksum'])
        row={key:value[0]for key,value in row.items()if value};key=(row['name'],row['version']);assert key not in seen;seen.add(key);packages.append(row)
    return packages


def main():
    assert not(HERE/'index.json').exists()and all(not p.exists()for p in[NEW,WORK,PACKAGE])
    old=json.loads((HERE/'source-derivation.json').read_bytes());changes=[];patch=[]
    old.pop('adapterTransformRun',None)
    old.pop('sourceUnitTestsExecuted',None)
    names=['crates/spidermonkey-embedding-splicer/src/stub_wasi.rs','crates/spidermonkey-embedding-splicer/src/bin/splicer.rs','crates/spidermonkey-embedding-splicer/Cargo.toml','Cargo.lock']
    for name in names:
        before=d(BASE/name);after=d(HERE/'after'/name);changes.append(dict(path=name,before=before,after=dict(after,path='after/'+name)))
        patch.extend(difflib.unified_diff((BASE/name).read_text().splitlines(keepends=True),(HERE/'after'/name).read_text().splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
    (HERE/'io-policy.patch').write_text(''.join(patch))
    old.update(baselinePath=changes[0]['before']['path'],baselineSha256=changes[0]['before']['sha256'],baselineBytes=changes[0]['before']['bytes'],afterPath=changes[0]['after']['path'],afterSha256=changes[0]['after']['sha256'],afterBytes=changes[0]['after']['bytes'],cliBaseline=changes[1]['before'],cliAfter=changes[1]['after'],files=changes,normalizerPureWriterPrivateAndFsync=True,normalizerPureFunctionsExecuted=True,normalizedBytesComputedInMemory=True,normalizedArtifactPublished=False,adapterPrunerExecuted=False,rustCompiled=False,rustUnitTestDefinitions=4,rustUnitTestsExecuted=False)
    write('source-derivation.json',old)
    source=tree(BASE);assert not source['symlinks']
    replacements={r['path']:r for r in changes};expected=[]
    for row in source['files']:
        name=row['relativePath'];selected=replacements.get(name);payload=selected['after']if selected else row['descriptor']
        expected.append(dict(path=name,sha256=payload['sha256'],bytes=payload['bytes'],origin='CORRECTED_AFTERIMAGE'if selected else'UNCHANGED_BASELINE',baseline=row['descriptor'],futureConfiguredPath=str(NEW/name)))
    assert set(replacements)<=set(r['relativePath']for r in source['files'])
    write('source-cut.json',dict(schemaVersion=1,state='UNAPPLIED_CLOCK_IO_FULL_SOURCE_CUT_V1',baseline=source,futureSourceRoot=str(NEW),futureWorkRoot=str(WORK),futurePackageRoot=str(PACKAGE),files=expected,sourceFiles=len(expected),changedFiles=4,unchangedFiles=len(expected)-4,actualCutStaged=False,originalSourceModified=False))
    rust_files=[]
    for folder in[RUST/'bin',RUST/'lib']:
        for p in sorted(folder.rglob('*')):
            assert not p.is_symlink()
            if p.is_file():rust_files.append(d(p))
    locked=locked_packages((HERE/'after/Cargo.lock').read_text());archives=[];missing=[]
    for package in locked:
        if package.get('source','').startswith('registry+'):
            path=REG/(package['name']+'-'+package['version']+'.crate')
            if path.is_file():
                row=d(path);assert row['sha256']==package['checksum'];archives.append(dict(name=package['name'],version=package['version'],descriptor=row))
            else:missing.append(dict(name=package['name'],version=package['version'],sha256=package['checksum'],expectedPath=str(path)))
    predicates=[]
    for package,needle,edge in[('anstream-0.6.18','[target."cfg(windows)".dependencies.anstyle-wincon]','anstream -> anstyle-wincon'),('termcolor-1.4.1','[target."cfg(windows)".dependencies.winapi-util]','termcolor -> winapi-util')]:
        archive=REG/(package+'.crate')
        with tarfile.open(archive,'r:gz')as source:
            member=package+'/Cargo.toml';text=source.extractfile(member).read();assert needle.encode()in text
        predicates.append(dict(edge=edge,targetPredicate='cfg(windows)',archive=d(archive),member=member,memberSha256=hashlib.sha256(text).hexdigest(),memberBytes=len(text),exactManifestHeading=needle))
    missing_status=dict(directWindowsEdges=predicates,transitiveEdge='anstyle-wincon -> once_cell from Cargo.lock; missing anstyle-wincon manifest not independently read',activationEvaluated=False,offlineReadinessProved=False,globalSourceBlocker=False,existingCachesModified=False,fetchPerformed=False,versionOrResolutionChanged=False,futureRootOptions=['Actual locked/offline host/wasm validation under new authority','If required, fetch exact locked archives into a fresh private cache and verify listed checksums'])
    tools=tree(TOOLS)
    node=d('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node');assert node['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
    write('tool-cut-references.json',dict(schemaVersion=1,state='EXISTING_TOOL_BYTES_DATA_NOT_FUTURE_BUILD_AUTHORITY_V1',rustToolchainRoot=str(RUST),rustVersionRole='Retained prior build.log reports1.96.1; tools only read/hash here',rustBinAndLibFiles=rust_files,cargo=d(RUST/'bin/cargo'),rustc=d(RUST/'bin/rustc'),rustdoc=d(RUST/'bin/rustdoc'),cargoLock=d(HERE/'after/Cargo.lock'),lockedRegistryArchives=archives,missingLockedRegistryArchives=missing,missingArchiveStatus=missing_status,registryActivationResolved=False,node=node,jsToolchain=tools,jcoEntry=d(TOOLS/'node_modules/@bytecodealliance/jco/dist/jco.js'),hostLinkerAndSdkSelection=None,privateCargoHomePreparation=None,completeBuildController=None,buildAction=None,toolsExecuted=False))
    archive_path=BASE.parent/'componentize-source.tar.gz';archive=d(archive_path.resolve())
    refs=dict(schemaVersion=1,baselineRoot=str(BASE),baselineSourceArchive=archive,baselineSourceArchiveAlias=dict(path=str(archive_path),target=os.readlink(archive_path),resolved=archive)if archive_path.is_symlink()else None,baselineArchiveShaText=d(BASE/'.source-archive-sha256'),baselineSourceObservation=d(BASE.parent/'source-verification.observed-after-build.json'),baselineBuildLog=d(BASE.parent/'build.log'),provenanceReport=pair(HERE.parent/'clock-adapter-provenance-v1'),independentDesignNotes=pair(HERE.parent/'clock-io-pruning-design-review-v1'),designNotesAreSourceApproval=False,adapter=d(REPO/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'),rootPureNormalizerObservation=d(HERE/'normalizer-results.json'),rootPureNormalizerObservationIsArtifactPublication=False,sourceIndependentReview=None,rootAuthority=None,stageAction=None,buildAction=None,normalizationPublication=None,pruningAction=None,actualPackage=None,actualPrunedAdapter=None,componentAction=None,runtimeAction=None)
    write('references.json',refs)
    cargo=str(RUST/'bin/cargo');target=str(WORK/'target');jco=str(TOOLS/'node_modules/@bytecodealliance/jco/dist/jco.js');node_path=node['path']
    plan=dict(schemaVersion=1,state='DORMANT_CLOCK_IO_FRESH_BUILD_PLAN_NOT_CONTROLLER_V1',sourceRoot=str(NEW),workRoot=str(WORK),packageRoot=str(PACKAGE),sourceCut='source-cut.json',sourceDerivation='source-derivation.json',toolReferences='tool-cut-references.json',freshPrivateDirectoriesRequired=True,noOriginalOutputsReused=True,allInputsAuthenticatedBeforeAnyFutureTool=True,
        futureEnvironment=dict(RUSTC=str(RUST/'bin/rustc'),RUSTDOC=str(RUST/'bin/rustdoc'),RUSTUP_TOOLCHAIN='1.96.1-aarch64-apple-darwin',CARGO_HOME=None,hostLinkerAndSdk=None),
        commandPlans=[dict(role='HOST_CLI_BUILD',cwd=str(NEW),argv=[cargo,'build','--locked','--offline','--release','-p','spidermonkey-embedding-splicer','--bin','splicer','--target','aarch64-apple-darwin','--target-dir',target]),dict(role='WASM_SPLICER_COMPONENT_BUILD',cwd=str(NEW),argv=[cargo,'build','--locked','--offline','--release','-p','splicer-component','--lib','--target','wasm32-wasip1','--target-dir',target]),dict(role='WASI_COMPONENT_WRAPPER',cwd=str(NEW),argv=[node_path,jco,'new',str(WORK/'target/wasm32-wasip1/release/splicer_component.wasm'),'--wasi-reactor','-o',str(WORK/'splicer.wasm')]),dict(role='SPLICER_JS_BINDINGS',cwd=str(NEW),argv=[node_path,jco,'transpile','-q','--name','spidermonkey-embedding-splicer',str(WORK/'splicer.wasm'),'-o',str(PACKAGE/'lib'),'--','-O1'])],
        packageSourceFiles=['package.json','types.d.ts','src/componentize.js','src/platform.js','src/cli.js'],packageDependencyMechanism='Future authenticated private copy of declared JS tool cut under new package/node_modules; no old package/source mutation or fake loader',selectedEngineMechanism='Existing componentize options.engine selects separately reviewed native engine; no native engine build/copy authorized by this packet',adapterSelectionMechanism='Existing componentize options.preview2Adapter; new Root caller must normalize original988 to fresh private file, invoke only new host CLI, authenticate actual output and supply that actual path',
        forbiddenConvenienceTargets=['make release','npm run build','npm pack without reviewed prepack handling'],reason='They can build native engines or invoke unreviewed prepack actions',
        missingSeams=['Owned build/stage/controller source and independent Source peer','Root authority, resource budgets, raw collectors and final/failure protection','Explicit host linker/SDK and private Cargo-home preparation; registry activation/availability check','Fresh private package materialization and actual dependency resolution/artifact review','Separate normalized/pruned adapter publication authority and actual structural validation','Component/runtime action and independent result review'],controllerImplemented=False,sourceIndependentReview=None,rootAuthority=None,allActionsAllowed=False)
    write('future-build-plan.json',plan)
    write('future-source-review-contract.json',dict(schemaVersion=1,requiredState='INDEPENDENT_SCHEDULER_CLOCK_IO_PRUNING_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=None,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,rustCompilerInvoked=False,adapterArtifactPublished=False,adapterPrunerExecuted=False,guestExecuted=False,sourceIndependentReview=None,rootAuthority=None,issuesNoAuthority=True))
    print(json.dumps(dict(sourceFiles=len(expected),changedFiles=4,rustBinLibFiles=len(rust_files),jsToolFiles=len(tools['files']),registryArchives=len(archives),missingRegistryArchives=len(missing),actionsInvoked=False)))


if __name__=='__main__':main()
