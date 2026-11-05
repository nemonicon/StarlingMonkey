"""Actual output/raw/provenance DATA only. No construction or guest APIs."""
from pathlib import Path
import hashlib,json,os,stat
P=Path(__file__).resolve().parent;S=P.parent/'clock-v13-component-candidate-v1';BASE=P.parent
checks=0
def need(v):
 global checks
 assert v;checks+=1
def read(p):return json.loads(Path(p).read_bytes())
def row(p):
 p=Path(p);need(p.is_file()and not p.is_symlink());a=p.stat();h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 z=p.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns));return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
def verify(r):need(row(r['path'])==r)
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
rootrow=row(BASE/'clock-v13-component-v1-root-results.json');root=read(rootrow['path']);outerrow=row(BASE/'clock-v13-component-v1-root-enclosing-results.json');outer=read(outerrow['path']);invrow=row(BASE/'clock-v13-component-v1-root-invocation.json');inv=read(invrow['path']);refs=read(S/'references.json')
for k in ['sourceIndex','rootAuthority','config','launcher','environmentPolicy','terminal','stdout','stderr']:verify(root[k])
need(root['error']is root['rootInputProtectionError']is None and root['operationalPhaseBudgetSatisfied']is True and root['returnedEnvelope']['completeUnreviewed']is True)
auth=read(root['rootAuthority']['path']);cfg=read(root['config']['path']);peer=auth['sourceIndependentReview'];verify(peer['index']);verify(peer['result'])
need(auth['sourceIndex']==root['sourceIndex']==inv['sourceIndex']and auth['rootLauncher']==root['launcher']==inv['rootLauncher'])
need(cfg['rootAuthority']==root['rootAuthority']and cfg['loaderConfig']==auth['loaderConfig']==inv['loaderConfig'])
verify(cfg['loaderConfig']);verify(auth['loaderRootAuthority']);lc=read(cfg['loaderConfig']['path']);lr=read(auth['loaderRootAuthority']['path']);need(lc['rootAuthority']==auth['loaderRootAuthority']and lc['sourceIndex']==refs['loaderSourceIndex'])
for k in ['nativeEngine','nativeMetadata','guestSourceSha256','witWorldSha256','worldName','selectedInterfaces','disableFeatures','privateTemporaryRoot']:need(lr[k]==auth[k])
need(lr['sourceIndependentReview']==refs['loaderSourcePeer']and lr['packageRoot']==refs['loaderPackageRoot'])
env=read(root['environmentPolicy']['path']);need(env['selectedEnvironment']==refs['requiredNativeReadOnlyEnvironment']==auth['requiredNativeReadOnlyEnvironment']and env['wholeEnvironmentRetained']is False and env['homeValuesPreserved']is True)
out=Path(root['returnedEnvelope']['root']);ix=root['returnedEnvelope']['index'];completion=root['returnedEnvelope']['completion'];verify(ix);verify(completion);index=read(ix['path']);members=index['files'];need(len(members)==22)
rows={};names={'index.json','completion.json'}
for r in members:
 n=r['path'];need(n not in names and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')));names.add(n);rows[n]=dict(r,path=str(out/n));verify(rows[n])
actual=set()
for p in out.rglob('*'):
 need(not p.is_symlink());s=p.stat()
 if p.is_dir():need(stat.S_IMODE(s.st_mode)==0o700)
 else:need(stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1);actual.add(p.relative_to(out).as_posix())
need(actual==names and len(actual)==24)
comp=read(completion['path']);result=read(out/'results.json');need(comp['index']==ix and comp['result']==rows['results.json']and comp['component']==result['component']and comp['state']=='COMPLETE_UNREVIEWED_EXTERNAL_RAW_ZERO_REQUIRED')
need(result['state']=='CLOCK_V13_COMPONENT_CONSTRUCTED_UNREVIEWED_V1'and result['primaryError']is None and result['finalProtectionErrors']==[]and result['componentizationAttempted']is True)
need(result['componentSourceIndexSha256']==root['sourceIndex']['sha256']and result['rootAuthority']==root['rootAuthority']and result['config']==root['config'])
for k in ['ordinaryGuestExportsInvoked','generatedModuleImported','keyOrCryptoWorkloadsInvoked','operationalAdmission','runtimeAcceptanceClaim']:need(result[k]is False)
native=read(out/'native-frame-data.json');meta=read(refs['nativeMetadata']['path']);need(native['enginePath']==refs['nativeEngine']['path']and native['sourceRoot']==refs['nativeSourceRoot']and native['metadata']==meta and native['variant']=='normal-off')
need(len(native)==5 and len(meta)==64 and len(meta['sourceManifest'])==342 and len(meta['componentizeSourceManifest'])==3 and len(meta['selectedModuleManifests'])==9)
need(meta['engineSha256']==refs['nativeEngine']['sha256']and native['pin']['receiptSha256']==refs['nativeMetadata']['sha256']and native['pin']['sourceFiles']==342)
pins=read(refs['nativePins']['path']);need(native['pin']==pins['variants']['normal-off'])
manifests=read(out/'selected-whole-manifests.json');need(len(manifests)==9)
for declared,m in zip(meta['selectedModuleManifests'],manifests):
 p=Path(refs['nativeSourceRoot'])/declared['path'];need(read(p)==m and hashlib.sha256(p.read_bytes()).hexdigest()==declared['sha256'])
shape=read(out/'native-frame-shape.json');need(len(shape)==6 and shape['recheck']==dict(type='function',writable=False,configurable=False,enumerable=True))
need((out/'guest.mjs').read_bytes()==Path(refs['guest']['path']).read_bytes()and(out/'bundle.mjs').read_bytes()==Path(refs['bundle']['path']).read_bytes())
need((out/'public-abi.wit').read_bytes()==Path(refs['wit']['path']).read_bytes())
provenance=read(out/'selected-package-provenance.json');lrefs=read(refs['loaderReferences']['path']);need(provenance['kind']=='experimental-clock-package-v2'and provenance['sourceIndex']==refs['loaderSourceIndex'])
for k in ['toolsBuildReview','failedAdapterPhaseReview','metadataReview','actualArtifacts','splicerCore','encodedTypePackage']:need(provenance[k]==lrefs[{'encodedTypePackage':'metadataPayload'}.get(k,k)])
need(provenance['explicitAdapter']==refs['prunedAdapter']and provenance['oldAdapterPhasePassed']is provenance['adapterPromoted']is False)
policy=read(out/'interface-audit.json');g=read(P/'callable-type-core-graph.json');need(policy['componentSha256']==result['component']['sha256']==g['component']['sha256']=='5c002f8da675016fd7061d245074965413d6914e4f40eb2a32a8141c1f3b7460')
need(policy['selectedInterfaces']==policy['emittedImports']==refs['selectedInterfaces']==g['rootInterfaces']and policy['unusedSelectedInterfaces']==[])
options=read(out/'component-options.json');need(options['engine']==refs['nativeEngine']['path']and options['preview2Adapter']==refs['prunedAdapter']['path']and options['selectedInterfaces']==refs['selectedInterfaces']and options['disableFeatures']==refs['disableFeatures']and options['enableAot']is False and options['env']=={})
need(options['witWorld']==Path(refs['wit']['path']).read_text())
wit=(out/'emitted.wit').read_text();need('export run: func() -> string;'in wit and sum('  import '+x+';'in wit for x in refs['selectedInterfaces'])==3)
ast=read(P/'ast.stdout.log');need(ast['source']==rows['transpiled/clock_v13.js']and ast['exports']==[dict(name='run',kind='function',arity=0),dict(name='_util',kind='terminal-empty-object')])
need(sorted(x['source']for x in ast['imports'])==['wasi:clocks/monotonic-clock','wasi:clocks/wall-clock','wasi:io/poll']and ast['dynamicImports']==['node:fs/promises']and ast['coreUrls']==['./clock_v13.core.wasm']and ast['topLevelAwaitNames']==['$init'])
need((out/'transpiled/package.json').read_bytes()==b'{"type":"module"}\n')
metaJ=read(out/'transpile-metadata.json');need(sorted(metaJ['imports'])==sorted(x['source']for x in ast['imports'])and metaJ['exports']==[['run','function']])
need(set(metaJ['files'])=={n[len('transpiled/'):]for n in rows if n.startswith('transpiled/')and n!='transpiled/package.json'})
need('export function run(): string;'in(out/'transpiled/clock_v13.d.ts').read_text())
pre=read(P/'pre-parser-input-checks.json');post=read(P/'post-parser-input-checks.json');need(pre==post and pre['allHashesAndBookendsPassed']is True)
for command in read(P/'parser-observation.json')['commands']:
 need(command['rawExitCode']==0 and command['stderr']['bytes']==0 and command['generatedModuleImported']is command['targetComponentOrEngineInstantiated']is False);verify(command['stdout']);verify(command['stderr'])
rawfiles=[];layers=[]
for base,argv,deadline,authority in [(Path(root['terminal']['path']).parent,root['actualArgv'],1800,auth),(Path(inv['enclosingRoot']),inv['actualOuterArgv'],2400,root['rootAuthority'])]:
 t=read(base/'terminal.json');started=read(base/'started.json');need(t['rawExitCode']==0 and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True and t['timeout']is t['forcedCleanup']is False)
 for k in ['remainingObservedPids','signals','errors','interruptedSignals']:need(t[k]==[])
 need(all(x['alive']is False for x in t['finalGroups'])and started['argv']==argv and started['timeoutSeconds']==deadline and t['authority']==started['authority']==authority)
 verify(t['stdout']);verify(t['stderr']);need(t['stderr']['bytes']==0)
 records=sorted(base.glob('owned-*.json'));need([read(p)['sequence']for p in records]==list(range(len(records))))
 observed={json.dumps(x,sort_keys=True)for x in t['observedProcesses']};need(all(json.dumps(read(p)['process'],sort_keys=True)in observed for p in records))
 rawfiles+=sorted(base.iterdir());layers.append(dict(root=str(base),pid=t['pid'],rawExitCode=0,ownedRecords=len(records),groups=[x['pgid']for x in t['finalGroups']],operationalSeconds=t['operationalElapsedSeconds']))
need(outer['terminal']==read(Path(inv['enclosingRoot'])/'terminal.json')and read(root['terminal']['path'])['pid']==1798)
need(json.loads(Path(root['stdout']['path']).read_text())==root['returnedEnvelope'])
lines=Path(inv['enclosingRoot'],'stdout.log').read_text().splitlines();need(len(lines)==2 and json.loads(lines[-1])==root)
copies=[];dest=P/'captured-data';dest.mkdir()
sources=[(rootrow,'root/results.json'),(outerrow,'root/enclosing-results.json'),(invrow,'root/invocation.json'),(root['rootAuthority'],'root/authority.json'),(root['config'],'root/config.json'),(root['launcher'],'root/launcher.py'),(root['environmentPolicy'],'root/environment-policy.json'),(cfg['loaderConfig'],'root/loader-config.json'),(auth['loaderRootAuthority'],'root/loader-authority.json')]
for p in rawfiles:
 tag='inner'if p.parent==Path(root['terminal']['path']).parent else'outer';sources.append((row(p),'raw/'+tag+'/'+p.name))
for n in sorted(actual):
 if not n.endswith('.wasm'):sources.append((row(out/n),'output/'+n))
for original,n in sources:
 p=dest/n;p.parent.mkdir(parents=True,exist_ok=True);b=Path(original['path']).read_bytes()
 with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 copy=row(p);need(copy['sha256']==original['sha256']and copy['bytes']==original['bytes']);copies.append(dict(original=original,copy=copy))
write('evidence-copies.json',dict(schemaVersion=1,copies=copies,binariesRemainAtAuthenticatedOriginalPaths=True,codeCopiesAreDataNotRelocatedExecutionContext=True))
artifacts={k:rows[n]for k,n in dict(component='clock-v13.component.wasm',core='transpiled/clock_v13.core.wasm',glue='transpiled/clock_v13.js',dts='transpiled/clock_v13.d.ts',wit='emitted.wit',transpileMetadata='transpile-metadata.json',packageJson='transpiled/package.json',interfaceAudit='interface-audit.json',bundle='bundle.mjs',guest='guest.mjs',selectedManifests='selected-whole-manifests.json',packageProvenance='selected-package-provenance.json',nativeFrameData='native-frame-data.json',componentOptions='component-options.json').items()}
generated={n[len('transpiled/'):]:r for n,r in rows.items()if n.startswith('transpiled/')}
write('artifact-intake.json',dict(schemaVersion=1,artifacts=artifacts,generatedFiles=generated,rootResult=rootrow,enclosingRootResult=outerrow,sourceIndex=root['sourceIndex'],sourcePeer=peer,nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],nativePins=refs['nativePins'],loaderSourceIndex=refs['loaderSourceIndex'],loaderSourcePeer=refs['loaderSourcePeer'],prunedAdapter=refs['prunedAdapter'],splicerCore=lrefs['splicerCore'],innerTerminal=root['terminal'],outerTerminal=row(Path(inv['enclosingRoot'])/'terminal.json'),rootAuthority=root['rootAuthority'],constructionConfig=root['config'],loaderConfig=cfg['loaderConfig'],loaderRootAuthority=auth['loaderRootAuthority'],actualIndex=ix,actualCompletion=completion,actualResult=rows['results.json']))
write('artifact-checks.json',dict(schemaVersion=1,checks=checks,outputIndexed=22,outputActual=24,sourceInputPreAndPost=pre,rootRawLayers=layers,copiedTextFiles=len(copies),wholeNativeFrameFields=5,nativeMetadataFields=64,nativeSourceFiles=342,externalEmbeddingSources=3,selectedManifests=9,pairedRootsVerified=True,original772GuestAnd487929BundleExact=True,experimentalPackage61685And87777RolesExact=True,rawOutputsAndCleanupPassed=True,componentCoreTypeGraphFreshlyDecoded=True,hostOnlyAstAndGrammarRawZero=True,generatedModuleImported=False,ordinaryGuestExportsInvoked=False))
print(json.dumps({k:v for k,v in read(P/'artifact-checks.json').items()if k!='sourceInputPreAndPost'}))
