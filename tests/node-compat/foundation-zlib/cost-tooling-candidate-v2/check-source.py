"""Read/hash source and declared physical tree data; no package/helper actions."""
import hashlib,json,os,re,stat
from pathlib import Path
HERE=Path(__file__).parent.resolve();checks=[]
def check(v,name):
    if not v:raise AssertionError(name)
    checks.append(name)
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as f:
        for raw in iter(lambda:f.read(1024*1024),b''):h.update(raw)
    return h.hexdigest()
plan=json.loads((HERE/'publication-plan.json').read_text());objects={r['destination']:r for r in plan['objects']}
check(len(objects)==len(plan['objects']),'unique physical publication destinations')
check(plan['guestSourceIndexSha256']=='ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8','corrected guestv2 only')
check(plan['context']['guestSourceIndexSha256']==plan['guestSourceIndexSha256'],'context exact guest binding')
check(plan['context']['maxRenderedInputUtf8Bytes']==33554432==plan['context']['maxBundleUtf8Bytes'],'separate approved32MiB UTF8 bounds')
check(plan['sourceProtocolDecisionSha256']=='0025c7a1083d9291effe0cf51bbfef4e154353db75d433dae07f296d46d61cc6','formal source-only protocolv2')
for name,r in objects.items():
    p=Path(r['source']);s=p.lstat();check(s.st_size==r['bytes']and stat.S_ISREG(s.st_mode)and not p.is_symlink()and stat.S_IMODE(s.st_mode)==r['mode']and sha(p)==r['sha256'],'physical source '+name)
check(sum(r['bytes']for r in objects.values())==plan['logicalCopyBytesBeforeProofCapsules'],'logical copy total')
live5={'builtins/node-compat/classic-streams/classic-core.generated.mjs','builtins/node-compat/classic-streams/transformation-receipt.json','builtins/node-compat/classic-streams/factories.generated.h','tests/node-compat/build-engine.sh','tests/node-compat/classic-streams-admission.mjs'}
repo=Path('/Users/dan/dev/StarlingMonkey')
check(not any(r['source']==str(repo/name)for r in objects.values()for name in live5),'no direct live Root5 copy inputs')
for r in objects.values():
    if r['destination'].startswith('packaging/')and 'imagePath'in r:check(Path(r['source']).is_relative_to(HERE/'image'),'packaging physical snapshot, not old mutable origin')
check(objects['packaging/host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm']['sha256']=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0','actual adapter separate physical tooling input')
wit=[k for k in objects if k.startswith('packaging/host-apis/wasi-0.2.10/wit/deps/')and k.endswith('/package.wit')];check(len(wit)==7,'all actual standardWIT7 copied')
source_map=json.loads((HERE/'packaging-source-map.json').read_text());check(source_map['inheritedLocalJsModules']==11 and source_map['functionalPackagingModules']==12,'eleven inherited plus finite bundler; guards counted separately')
for e in source_map['inheritedStaticEdges']:check('packaging/'+e['importer']in objects and 'packaging/'+e['target']in objects,'literal JS edge '+e['request'])
for r in objects.values():
    if r['destination'].startswith('packaging/')and r['destination'].endswith('.mjs'):
        text=Path(r['source']).read_text()
        for part in re.findall(r"new URL\(['\"]([^'\"]+)['\"],\s*import\.meta\.url\)",text):
            if part.startswith('.'):
                target=os.path.normpath(str(Path(r['destination']).parent/part));check(target in objects or target=='packaging','literal packaging file or declared repository-root context '+target)
trees=plan['toolTrees'];check(len(trees)==2,'two separate complete tool trees');file_count=link_count=0
for tree in trees:
    root=Path(tree['originalRoot']);expected={e['path']:e for e in tree['entries']};found=set()
    for directory,dirs,names in os.walk(root,followlinks=False):
        for name in dirs+names:
            p=Path(directory)/name;rel=str(p.relative_to(root));check(rel in expected,'no extra original tool member '+rel);found.add(rel);e=expected[rel];s=p.lstat()
            if e['kind']=='file':file_count+=1;check(stat.S_ISREG(s.st_mode)and e['destination']in objects,'tool ordinary file')
            elif e['kind']=='directory':check(stat.S_ISDIR(s.st_mode)and not p.is_symlink(),'tool ordinary directory')
            else:link_count+=1;check(p.is_symlink()and os.readlink(p)==e['sourceLinkText']and str(p.resolve())==e['resolvedOriginal'],'exact known tool link')
    check(found==set(expected),'whole original tree membership')
check(file_count==4890 and link_count==22==len(plan['links']),'actual physical tool/link counts')
guest_index=json.loads((HERE/'image/guest/index.json').read_text());check(len(guest_index['files'])==38,'whole corrected guest index')
for r in guest_index['files']:check(objects['guest/'+r['path']]['sha256']==r['sha256'],'guest source '+r['path'])
check('guest/output-stability.mjs'in objects,'new full prior-output stability helper included')
bundle=(HERE/'bundle.mjs').read_text();check("bundleComponentChunk(entryPath,{plugins:[finite,profile,witness],config:{treeshake:true}})"in bundle,'actual Jco bundle API');check("Buffer.byteLength(chunk.code,'utf8')<=32*1024*1024"in bundle,'final bundle UTF8 bound');check('assertPackagingEnvironment(admitted)'in bundle,'loader environment binding')
binding=Path(objects['tools/toolchain/node_modules/rolldown/dist/shared/binding-BXYS21Tf.mjs']['source']).read_text();switches=set(re.findall(r'process\.env\.(NAPI_RS_[A-Z_]+)',binding));check(switches=={'NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK'},'actual pinned Rolldown binding-switch vocabulary')
environment=(HERE/'environment.mjs').read_text();check(all("'"+key+"'"in environment for key in switches),'all actual provider overrides refused before loaders')
context=(HERE/'context.mjs').read_text();check(context.index('indexDescriptor=descriptor(indexDescriptor);')<context.index('await authority.recheck();'),'publication descriptor captured before await')
preflight=(HERE/'preflight.mjs').read_text();check('rootAction=descriptor(rootAction);publicationIndex=descriptor(publicationIndex);'in preflight and 'rootActionSha256:authority.descriptor.sha256'in preflight,'Root/publication descriptors and authenticated returned SHA captured privately')
action=(HERE/'node-oracle-action.mjs').read_text();check(action.index('await costPreflight(')<action.index('DurableOutput.create(')<action.index("import('node:zlib')"),'full guard/output before codec import');check("await output.write('node-oracle.json'"in action and "renderNodeInputs(oracleRaw,oracleRow.sha256)"in action,'actual renderer input hash comes from durable raw oracle')
check("loadOracleRender(authority.authority.nodeOracleRenderProof,authority,context)"in preflight,'derived oracle is a separate bound context')
future=json.loads((HERE/'future-authority.json').read_text());check(future['actionsAllowed']is False and future['operationalAdmission']is False,'no checked-in action or operational authority')
check(not Path('/tmp/starling-node-compat/zlib-cost-source-v2').exists(),'no actual source publication created');check(not Path('/tmp/starling-node-compat/zlib-cost-node-oracle-v2').exists(),'no actual Node-oracle action output')
print(json.dumps({'schemaVersion':1,'state':'SOURCE_CLOSURE_AND_DATA_CHECKS_PASSED','checks':len(checks),'objects':len(objects),'logicalCopyBytes':sum(r['bytes']for r in objects.values()),'toolFiles':file_count,'toolLinks':link_count,'guestIndexedFiles':len(guest_index['files']),'actualCodecOrOracleOrBundleOrNativeOrGuestOrHostOrTimingActions':False}))
