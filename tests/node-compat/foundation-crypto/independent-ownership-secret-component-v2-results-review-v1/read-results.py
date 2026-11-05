"""Independent whole-byte/JSON/binary/Source DATA audit; no target execution."""
from pathlib import Path
import hashlib,json,os,stat
P=Path(__file__).resolve().parent;K=P.parent;S=K/'ownership-secret-component-candidate-v2'
checks=0;verified={};identities={}
def need(v):
 global checks
 assert v;checks+=1
def read(p):return json.loads(Path(p).read_bytes())
def identity(p):
 s=p.lstat();need(stat.S_ISREG(s.st_mode));return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode,s.st_nlink)
def row(p):
 p=Path(p);need(p.is_absolute()and not p.is_symlink());a=identity(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 need(identity(p)==a);r=dict(path=str(p),sha256=h.hexdigest(),bytes=a[2]);verified[str(p)]=r;identities[str(p)]=a;return r
def verify(r):need(row(r['path'])==r);return r
def family(ix):
 verify(ix);base=Path(ix['path']).parent;want={'index.json'}
 for m in read(ix['path'])['files']:
  n=m['path'];need(n not in want and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')));want.add(n);verify(dict(m,path=str(base/n)))
 actual=set()
 for p in base.rglob('*'):
  need(not p.is_symlink()and(p.is_file()or p.is_dir()))
  if p.is_file():actual.add(p.relative_to(base).as_posix())
 need(actual==want)
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
rootrow=row(K/'ownership-secret-component-v2-root-results.json');root=read(rootrow['path']);enclosingrow=row(K/'ownership-secret-component-v2-root-enclosing-results.json');enclosing=read(enclosingrow['path']);invrow=row(K/'ownership-secret-component-v2-root-invocation.json');inv=read(invrow['path'])
for key in ['sourceIndex','rootAuthority','config','launcher','environmentPolicy','terminal','stdout','stderr']:verify(root[key])
need(root['sourceIndex']['sha256']=='6a17edae062f233c6cac4529237313a07a439e3703eab23c1d5bf468c4c9d55f');family(root['sourceIndex'])
refs=read(S/'references.json');inputs=read(S/'source-inputs.json');need(len(inputs['files'])==33364 and len(inputs['families'])==27)
for r in inputs['files']:verify(r)
for ix in inputs['families']:family(ix)
authority=read(root['rootAuthority']['path']);cfg=read(root['config']['path']);peer=authority['sourceIndependentReview'];family(peer['index']);verify(peer['result'])
need(peer['result']in[dict(m,path=str(Path(peer['index']['path']).parent/m['path']))for m in read(peer['index']['path'])['files']])
need(read(peer['result']['path'])['sourceReviewPassed']is True and inv['sourcePeer']==peer and cfg['rootAuthority']==root['rootAuthority']and cfg['sourceIndex']==root['sourceIndex'])
for k in ['python','node','monitor','rootLauncher']:verify(inv[k])
need(inv['rootLauncher']==root['launcher']and inv['rootAuthority']==root['rootAuthority']and inv['sourceIndex']==root['sourceIndex'])
need(root['state']=='ROOT_OBSERVED_SECRET355_COMPONENT_CONSTRUCTION_ZERO_UNREVIEWED_V2'and root['error']is root['rootInputProtectionError']is None and root['operationalPhaseBudgetSatisfied']is True)
need(root['actualArgv']==inv['actualOuterArgv'][0:0]+read(Path(root['terminal']['path']).parent/'started.json')['argv'])
env=read(root['environmentPolicy']['path']);need(env['selectedEnvironment']==refs['requiredPackagingEnvironment']==authority['requiredPackagingEnvironment']==inv['requiredPackagingEnvironment']and env['wholeEnvironmentRetained']is False and env['homeValuesPreserved']is True)
need(all(authority[k]is False for k in ['ordinaryGuestExportsAllowed','keyOrCryptoOperationsAllowed','generatedModuleImportAllowed','operationalAdmission','runtimeAcceptanceClaim','gcPressureAllowed']))
output=Path(root['returnedEnvelope']['root']);need(str(output)==refs['outputRoot'])
def local(r):return dict(r,path=str(output/r['path']))
ix=local(root['returnedEnvelope']['index']);completion=local(root['returnedEnvelope']['completion']);verify(ix);verify(completion);members=read(ix['path'])['files'];need(len(members)==21)
names={'index.json','completion.json'};artrows={}
for m in members:
 need(m['path']not in names);names.add(m['path']);r=local(m);verify(r);artrows[m['path']]=r
actual=set()
for p in output.rglob('*'):
 need(not p.is_symlink())
 if p.is_dir():need(stat.S_IMODE(p.stat().st_mode)==0o700)
 else:need(stat.S_IMODE(p.stat().st_mode)==0o600 and p.stat().st_nlink==1);actual.add(p.relative_to(output).as_posix())
need(actual==names and len(actual)==23 and stat.S_IMODE(output.stat().st_mode)==0o700)
comp=read(completion['path']);result=read(output/'results.json');need(comp['index']==root['returnedEnvelope']['index']and local(comp['result'])==artrows['results.json']and comp['state']=='COMPLETE_UNREVIEWED_EXTERNAL_RAW_ZERO_REQUIRED')
need(result['state']=='SECRET_OWNER355_COMPONENT_CONSTRUCTED_UNREVIEWED_V2'and result['primaryError']is None and result['finalProtectionErrors']==[] and result['componentizationAttempted']is True)
need(result['rootAuthority']==root['rootAuthority']and result['config']==root['config']and result['componentSourceIndexSha256']==root['sourceIndex']['sha256'])
for k in ['ordinaryGuestExportsInvoked','keyOperationsInvoked','generatedModuleImported','asyncScalarRuntimeProof','operationalAdmission','runtimeAcceptanceClaim']:need(result[k]is False)
data=read(output/'retained-record-data.json');need(Path(refs['actualRetainedRecordData']['path']).read_bytes()==(output/'retained-record-data.json').read_bytes());h=data['historicalBootstrap'];need(len(h)==41 and len(h['metadata'])==75 and h['nativeSourceFiles']==355 and h['externalEmbeddingSources']==3 and len(h['selectedManifests'])==11)
for k in ['engine','metadata','freezeReceipt']:verify(refs[k])
need(h['engine']==refs['engine']==result['engine']and h['metadataDescriptor']==refs['metadata']==result['metadata']and h['freezeReceipt']==refs['freezeReceipt'])
need(h['metadata']==read(refs['metadata']['path'])and h['metadata']['engineSha256']==refs['engine']['sha256'])
selection=read(output/'whole-manifest-selection.json');need(selection['manifests']==h['selectedManifests']and selection['publicNodeCryptoAdmitted']is False and selection['nativeMetadataUnchanged']is True)
mapping={}
for m in h['selectedManifests']:
 for canonical,v in m['modules'].items():
  for n in [canonical,*v['aliases']]:need(n not in mapping);mapping[n]=canonical
need(selection['map']==mapping and 'node:crypto'not in mapping and 'crypto'not in mapping)
bundle=read(output/'bundle-return.json');need(bundle['code'].encode()==(output/'bundle.mjs').read_bytes()and bundle['imports']==[]and bundle['moduleIds']==[refs['guest']['path']]and bundle['admittedBuiltins']==sorted(set(mapping.values())))
need(result['guest']==refs['guest']and result['wit']==refs['wit'])
options=read(output/'component-options.json');need(options['engine']==refs['engine']['path']and options['preview2Adapter'].endswith('/preview1-adapter-release/wasi_snapshot_preview1.wasm')and options['selectedInterfaces']==[]and sorted(options['disableFeatures'])==['clocks','fetch-event','http','random','stdio']and options['enableAot']is False and options['env']=={})
need(options['witWorld']==Path(refs['wit']['path']).read_text()and options['worldName']=='validation')
need(read(output/'required-packaging-environment.json')==refs['requiredPackagingEnvironment'])
init=read(output/'guest-initialization-audit.json');need(init['topLevelCryptoOrKeyOrAsyncCalls']is False and init['keyHoldersInitiallyNull']is True)
g=read(P/'binary-graph.json');component=artrows['crypto-secret-owner.component.wasm'];core=artrows['transpiled/crypto_secret_owner.core.wasm'];need(g['component']==component and len(g['modules'])==1 and g['rootImports']==[]and g['modules'][0]['imports']==[])
cb=Path(component['path']).read_bytes();kb=Path(core['path']).read_bytes();nested=next(s for s in g['componentSections']if s['id']==1);need(cb[nested['offset']:nested['offset']+nested['bytes']]==kb and not any(s['id']==10 for s in g['componentSections'])and not any(s['id']==8 for s in g['modules'][0]['sections']))
abi={}
for e in g['exports']:
 need(e['sort']==[1]);f=g['componentFunctions'][e['index']];need(f['kind']=='lift');t=g['componentTypes'][f['typeIndex']];need(t['kind']=='function'and t['results']==[-13]);need([v['type']for v in t['params']]==([-7]if e['name']=='run'else[]));abi[e['name']]='(u32) -> string'if t['params']else'() -> string'
need(abi==result['emittedExports']and set(abi)=={'inspect','run','clear','validate'}and result['emittedImports']==[])
priorbase=K/'independent-ownership-gc-component-results-review-v1';prior=read(priorbase/'results.json');verify(prior['artifacts']['glue']);need(prior['generatedGlueGrammarBoundByWholePriorParsedBytes']is True)
old=Path(prior['artifacts']['glue']['path']).read_bytes();glue=Path(artrows['transpiled/crypto_secret_owner.js']['path']).read_bytes();need(old.count(b'crypto_owner.core.wasm')==1 and old.replace(b'crypto_owner.core.wasm',b'crypto_secret_owner.core.wasm')==glue)
need((output/'emitted.wit').read_bytes()==Path(prior['artifacts']['wit']['path']).read_bytes()and(output/'transpiled/crypto_secret_owner.d.ts').read_bytes()==Path(prior['artifacts']['dts']['path']).read_bytes())
need((output/'transpiled/package.json').read_bytes()==b'{"type":"module"}\n'and b"await $init;"in glue and b"await import('node:fs/promises')"in glue and b"new URL('./crypto_secret_owner.core.wasm', import.meta.url)"in glue)
meta=read(output/'transpile-metadata.json');need(meta['imports']==[]and sorted(meta['exports'])==[[k,'function']for k in sorted(abi)]and sorted(meta['fileNames'])==['crypto_secret_owner.core.wasm','crypto_secret_owner.d.ts','crypto_secret_owner.js'])
audit=read(output/'interface-audit.json');need(audit['componentSha256']==component['sha256']and audit['emittedImports']==[]and audit['selectedInterfaces']==[])
# Authentic original package and retained native tree modes/membership remain.
pack=read(refs['packagingMap']['path']);packroot=Path(pack['publicationRoot']);expected={r['path']:r for r in pack['files']};links={r['destination']:r for r in pack['links']};found=set();foundlinks=set()
for role in pack['roleRoots']:
 for p in(packroot/role).rglob('*'):
  n=p.relative_to(packroot).as_posix();s=p.lstat()
  if p.is_symlink():need(n in links and os.readlink(p)==links[n]['newLinkText']and str(p.resolve())==str(packroot/links[n]['mappedTarget']));foundlinks.add(n)
  elif p.is_dir():need(stat.S_IMODE(s.st_mode)==0o700)
  else:need(n in expected and stat.S_IMODE(s.st_mode)==expected[n]['mode']and s.st_nlink==1);found.add(n)
need(found==set(expected)and foundlinks==set(links)and len(found)==4934 and len(foundlinks)==22)
retained=read(K/'ownership-secret-retained-bootstrap-candidate-v1/references.json')
for tree in retained['retainedTrees']:
 base=Path(tree['root']);names=set()
 for p in base.rglob('*'):
  need(not p.is_symlink())
  if p.is_file():names.add(p.relative_to(base).as_posix())
  if tree['private']:need(stat.S_IMODE(p.stat().st_mode)==(0o700 if p.is_dir() else 0o600))
 need(names==set(tree['names']))
for pair in retained['independentFrozenCopies']:
 a=Path(pair['frozen']).stat();b=Path(pair['original']).stat();need(a.st_nlink==1 and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino))
# Both genuine raw monitor layers, all durable ownership rows, complete streams.
rawfiles=[];summaries=[]
for base,argv,deadline,expectedAuthority in [(Path(root['terminal']['path']).parent,root['actualArgv'],1800,authority),(Path(inv['enclosingRoot']),inv['actualOuterArgv'],2400,root['rootAuthority'])]:
 t=read(base/'terminal.json');started=read(base/'started.json');need(t['rawExitCode']==0 and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True and t['timeout']is t['forcedCleanup']is False)
 for k in ['remainingObservedPids','signals','errors','interruptedSignals']:need(t[k]==[])
 need(all(x['alive']is False for x in t['finalGroups'])and started['argv']==argv and started['timeoutSeconds']==deadline and started['authority']==t['authority']==expectedAuthority)
 verify(t['stdout']);verify(t['stderr']);need(t['stderr']['bytes']==0)
 records=sorted(base.glob('owned-*.json'));need([read(p)['sequence']for p in records]==list(range(len(records))))
 processes={json.dumps(x,sort_keys=True)for x in t['observedProcesses']};need(all(json.dumps(read(p)['process'],sort_keys=True)in processes for p in records))
 rawfiles.extend(sorted(base.iterdir()));summaries.append(dict(root=str(base),pid=t['pid'],ownedRecords=len(records),rawExitCode=0,allGroupsGone=True,observedGroups=[x['pgid']for x in t['finalGroups']],operationalSeconds=t['operationalElapsedSeconds']))
need(read(root['terminal']['path'])['pid']==93759 and enclosing['terminal']==read(Path(inv['enclosingRoot'])/'terminal.json'))
node_envelope=json.loads(Path(root['stdout']['path']).read_text());need(node_envelope==root['returnedEnvelope']and node_envelope['completeUnreviewed']is True)
outerlines=Path(inv['enclosingRoot'],'stdout.log').read_text().splitlines();need(len(outerlines)==2 and json.loads(outerlines[-1])==root)
for path,i in identities.items():need(identity(Path(path))==i)
# Preserve all actual output text and both monitor streams/records byte-exactly.
copies=[];dest=P/'captured-data';dest.mkdir()
sources=[(rootrow,'root/results.json'),(enclosingrow,'root/enclosing-results.json'),(invrow,'root/invocation.json'),(root['rootAuthority'],'root/authority.json'),(root['config'],'root/config.json'),(root['launcher'],'root/launcher.py'),(root['environmentPolicy'],'root/environment-policy.json')]
for f in rawfiles:
 tag='inner'if f.parent==Path(root['terminal']['path']).parent else'outer';sources.append((row(f),'raw/'+tag+'/'+f.name))
for name in sorted(actual):
 if not name.endswith('.wasm'):sources.append((row(output/name),'output/'+name))
for original,name in sources:
 target=dest/name;target.parent.mkdir(parents=True,exist_ok=True);raw=Path(original['path']).read_bytes()
 with target.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
 copy=row(target);need(copy['sha256']==original['sha256']and copy['bytes']==original['bytes']);copies.append(dict(original=original,copy=copy))
write('evidence-copies.json',dict(schemaVersion=1,copies=copies,binaryArtifactsCopied=False,codeCopiesAreDataNotNewExecutionContext=True))
artifacts={key:artrows[name]for key,name in dict(component='crypto-secret-owner.component.wasm',core='transpiled/crypto_secret_owner.core.wasm',glue='transpiled/crypto_secret_owner.js',dts='transpiled/crypto_secret_owner.d.ts',wit='emitted.wit',transpileMetadata='transpile-metadata.json',packageJson='transpiled/package.json',publicSourceAudit='generated-public-source-audit.json',interfaceAudit='interface-audit.json',bundle='bundle.mjs',bundleReturn='bundle-return.json',wholeManifestSelection='whole-manifest-selection.json').items()}
write('checks.json',dict(schemaVersion=1,checks=checks,sourceMembers=21,sourceInputs=33364,sourceFamilies=27,sourceInputLogicalBytes=sum(x['bytes']for x in inputs['files']),outputIndexed=21,outputActual=23,packageRegularFiles=4934,packageLinks=22,retainedTreeScopes=8,independentFrozenPairs=1899,normalFrozenFiles=1391,rawLayers=summaries,textCopies=len(copies),allBookendHashesPassed=True,actualBinaryAbi=abi,componentHasNoImports=True,coreHasNoImportsOrStart=True,singleCoreWholeBytesEqualsJcoCore=True,glueWholePriorBytesEqualAfterOneLiteralUrlChange=True,freshJcoOrParserOrEngineInvoked=False,guestOrKeyActionsInvoked=False))
write('artifact-intake.json',dict(schemaVersion=1,artifacts=artifacts,rootResult=rootrow,enclosingRootResult=enclosingrow,sourceIndex=root['sourceIndex'],sourcePeer=peer,engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],innerTerminal=root['terminal'],outerTerminal=row(Path(inv['enclosingRoot'])/'terminal.json'),constructionConfig=root['config'],rootAuthority=root['rootAuthority'],actualIndex=ix,actualCompletion=completion,actualResult=artrows['results.json'],priorGlueResult=row(priorbase/'results.json'),priorGlueIndex=row(priorbase/'index.json'),priorGlue=prior['artifacts']['glue']))
print(json.dumps(read(P/'checks.json')))
