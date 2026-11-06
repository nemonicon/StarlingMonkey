"""Thin installed-inventory packaging correction; no native/guest action."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
OWN=Path(__file__).resolve().parent;PARENT=OWN.parent/'node-module-candidate-v1'
assert not(OWN/'index.json').exists()
def read(p):return json.loads(Path(p).read_bytes())
def d(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
parent_index=d(PARENT/'index.json');assert parent_index['sha256']=='29f603f7652acabef8adfa12217c70cec177d8aaf07f177f0d09031f2a99009e'
parent_rows=[]
for r in read(PARENT/'index.json')['files']:p=PARENT/r['path'];assert d(p)==dict(r,path=str(p));parent_rows.append(d(p))
hold=OWN.parent/'independent-source-review-v1/results.json';assert read(hold)['sourceReviewPassed']is False
inventory_name='module-builtin-inventory.node-v22.14.0.json'
inventory=dict(schemaVersion=1,inventoryVersion='node-module-builtin-exports-v22.14.0-v1',**read(PARENT/'node-inventory.json'))
save(inventory_name,inventory)
old=(PARENT/'generate-module-factory.mjs').read_text();text=old
changes=[
 ("const inventory=JSON.parse(await readFile(new URL('./node-inventory.json',import.meta.url),'utf8'));",f"const inventorySource=await readFile(new URL('./{inventory_name}',import.meta.url),'utf8');\nconst inventory=JSON.parse(inventorySource);\nif(inventory.schemaVersion!==1||inventory.inventoryVersion!=='node-module-builtin-exports-v22.14.0-v1')throw new Error('Unexpected versioned builtin inventory');"),
 ("createHash('sha256').update(source).digest('hex')",f"createHash('sha256').update('module-core.mjs\\0'+source+'\\0{inventory_name}\\0'+inventorySource+'\\0').digest('hex')")]
for a,b in changes:assert text.count(a)==1;text=text.replace(a,b)
(OWN/'generate-module-factory.mjs').write_text(text)
inverse=text
for a,b in reversed(changes):assert inverse.count(b)==1;inverse=inverse.replace(b,a)
assert inverse==old
node=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node');node_row=d(node);assert node_row['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
temp=Path(tempfile.mkdtemp(prefix='node-module-v2-packaging-',dir='/private/tmp/starling-node-compat'));oldroot=temp/'old/builtins/node-compat';newroot=temp/'new/builtins/node-compat'
oldroot.mkdir(parents=True);newroot.mkdir(parents=True)
for root in [oldroot,newroot]:(root/'module-core.mjs').write_bytes((PARENT/'module-core.mjs').read_bytes())
for name in ['generate-module-factory.mjs','module-factory.generated.h']:(oldroot/name).write_bytes((PARENT/name).read_bytes())
(newroot/'generate-module-factory.mjs').write_bytes((OWN/'generate-module-factory.mjs').read_bytes());(newroot/inventory_name).write_bytes((OWN/inventory_name).read_bytes())
commands=[]
def command(label,args,want):
 argv=[str(node),*map(str,args)];r=subprocess.run(argv,capture_output=True,timeout=45)
 (OWN/(label+'.stdout.log')).write_bytes(r.stdout);(OWN/(label+'.stderr.log')).write_bytes(r.stderr)
 row=dict(label=label,argv=argv,rawExitCode=r.returncode,expectedRawExitCode=want,stdout=d(OWN/(label+'.stdout.log')),stderr=d(OWN/(label+'.stderr.log')),hostPackagingOnly=True,nativeOrGuestExecuted=False)
 commands.append(row);assert r.returncode==want,(label,r.stderr.decode(errors='replace'));return r
command('grammar',['--check',OWN/'generate-module-factory.mjs'],0)
failure=command('old-installed-cut-missing-inventory',[oldroot/'generate-module-factory.mjs','--check'],1);assert b'ENOENT'in failure.stderr and b'node-inventory.json'in failure.stderr
(oldroot/'node-inventory.json').write_bytes((PARENT/'node-inventory.json').read_bytes());command('old-complete-context',[oldroot/'generate-module-factory.mjs','--check'],0)
mutation=read(oldroot/'node-inventory.json');mutation['constructorOwnKeys'].append('unused-source-mutation');(oldroot/'node-inventory.json').write_text(json.dumps(mutation)+'\n')
command('old-unused-inventory-mutation-not-covered',[oldroot/'generate-module-factory.mjs','--check'],0)
command('new-genuine-generation',[newroot/'generate-module-factory.mjs'],0);command('new-installed-cut-check',[newroot/'generate-module-factory.mjs','--check'],0)
header=(newroot/'module-factory.generated.h').read_bytes();(OWN/'module-factory.generated.h').write_bytes(header)
assert header.split(b'static constexpr',1)[1]==(PARENT/'module-factory.generated.h').read_bytes().split(b'static constexpr',1)[1]
mutation=read(newroot/inventory_name);mutation['constructorOwnKeys'].append('unused-source-mutation');(newroot/inventory_name).write_text(json.dumps(mutation)+'\n')
failure=command('new-unused-inventory-mutation-refused',[newroot/'generate-module-factory.mjs','--check'],1);assert b'Stale module factory'in failure.stderr
(newroot/inventory_name).write_bytes((OWN/inventory_name).read_bytes());command('new-restored-inventory-check',[newroot/'generate-module-factory.mjs','--check'],0)
(newroot/'module-core.mjs').write_bytes((PARENT/'module-core.mjs').read_bytes()+b'\n// changed canonical Source\n')
failure=command('new-core-mutation-refused',[newroot/'generate-module-factory.mjs','--check'],1);assert b'Stale module factory'in failure.stderr
(newroot/'module-core.mjs').write_bytes((PARENT/'module-core.mjs').read_bytes());command('new-final-installed-cut-check',[newroot/'generate-module-factory.mjs','--check'],0)
manifest=read(PARENT/'prospective-source-manifest.json');assert manifest['nativeSourceFiles']==363
overrides=[dict(path='builtins/node-compat/'+name,origin=d(OWN/name))for name in ['generate-module-factory.mjs','module-factory.generated.h',inventory_name]]
mapping={r['path']:r['sha256']for r in manifest['files']}
for row in overrides:mapping[row['path']]=row['origin']['sha256']
assert len(mapping)==364
manifest.update(nativeSourceFiles=364,retainedNativeFiles=351,changedNativeFiles=6,newNativeFiles=7,files=[dict(path=k,sha256=mapping[k])for k in sorted(mapping)])
save('prospective-source-manifest.json',manifest)
save('native-mappings.json',dict(schemaVersion=1,parentSourceIndex=parent_index,parentMappings=d(PARENT/'derivations.json'),overrides=overrides,retainedParentMappingRule='For unchanged native rows use the actual parent357 frozen source from v1 parentMetadata. Six existing afterimage paths and the six original added paths retain exact v1 mappings unless overridden above.',actualFutureInstalledFiles=[row['path']for row in overrides],versionedInventoryRole='Seventh new native Source path, installed beside module-core/generator/header; no implicit author-only node-inventory.json dependency.',nativeSourceFiles=364,newNativePaths=7,authoringLayoutRoot=str(newroot),stageOrNativeBuildExecuted=False))
save('derivations.json',dict(schemaVersion=1,parentIndex=parent_index,generatorBefore=d(PARENT/'generate-module-factory.mjs'),generatorAfter=d(OWN/'generate-module-factory.mjs'),edits=[dict(before=a,after=b,count=1)for a,b in changes],canonicalInventoryBefore=d(PARENT/'node-inventory.json'),versionedInventory=d(OWN/inventory_name),headerBefore=d(PARENT/'module-factory.generated.h'),headerAfter=d(OWN/'module-factory.generated.h'),generatedFunctionBodyByteIdentical=True,guestCoreAndKernelAndSixExistingAfterimagesByteIdentical=True))
save('checks.json',dict(schemaVersion=1,commands=commands,oldInstalledMissingInventoryRefused=True,newInstalledLayoutPassed=True,canonicalDigestCoversWholeInventoryAndCore=True,unusedInventoryMutationOldPassNewFail=True,generatedFunctionBodyByteIdentical=True,oldHost42AndGeneratedFactory8HeldAsAncestryNotRerun=True,nativeOrGuestInvoked=False))
for r in parent_rows:assert d(r['path'])==r
assert d(PARENT/'index.json')==parent_index and d(node)==node_row
save('references.json',dict(schemaVersion=1,parentSourceIndex=parent_index,parentHold=d(hold),parentCore=d(PARENT/'module-core.mjs'),parentKernel=d(PARENT/'module-kernel.cpp'),parentInputs=d(PARENT/'input-hashes.json'),node=node_row,sourcePeer=None,rootAuthority=None,actualNativeBuild=None,actualGuest=None))
save('results.json',dict(schemaVersion=1,state='NODE_MODULE_COMMONJS_INVENTORIED_SOURCE_READY_FOR_REVIEW_V2',sourceOnly=True,sourceChecksPassed=True,parentSourceIndex=parent_index,parentHeldReason='Missing installed inventory and incomplete canonical digest; original v1 remains held.',nativeSourceFiles=364,retainedNativeFiles=351,changedNativeFiles=6,newNativeFiles=7,externalEmbeddingSources=3,actualInstalledGeneratorLayoutPassed=True,wholeInventoryAndCoreDigestCovered=True,guestCodeFunctionBodyUnchanged=True,hostDifferential42InheritedNotRerun=True,sourcePeer=None,rootAuthority=None,actualNativeBuild=None,actualGuest=None,compilerActionsInvoked=False,guestActionsInvoked=False,nextServerExecuted=False,operationalAdmission=False))
save('source-receipt.json',dict(schemaVersion=1,result=d(OWN/'results.json'),checks=d(OWN/'checks.json'),derivations=d(OWN/'derivations.json'),parentSourceIndex=parent_index,allFutureAuthoritiesNull=True,nativeActionsInvoked=False))
print(json.dumps(dict(state='SOURCE_PACKAGING_CORRECTION_COMPLETE_UNSEALED',nativeFiles=364,commands=len(commands),nativeActions=False)))
