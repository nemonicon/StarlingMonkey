"""Pure data/source and owned tiny-copy tests; never launch build/configure tools."""
import sys
sys.dont_write_bytecode=True
import ast,copy,importlib.util,json,re,tempfile
from pathlib import Path
from benchmark_common import *

assert len(sys.argv)==3,'READ_ONLY_CORRECTED_SOURCE_ROOT FRESH_TEST_OUTPUT'
SOURCE_ROOT=Path(sys.argv[1]).resolve(strict=True)
OUT=Path(sys.argv[2]).absolute();assert str(OUT).startswith('/tmp/starling-node-compat/')
assert not OUT.exists()and not OUT.is_symlink();OUT.mkdir(parents=True)
cases=[]
def check(name,fn):fn();cases.append(name)
def rejected(fn):
    try:fn()
    except (AssertionError,KeyError,TypeError,ValueError,FileExistsError):return
    raise AssertionError('Unexpected data admission')

old=json.loads(Path('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze/normal-off.engine.wasm.build.json').read_bytes())
def model(label='benchmark-classic-on'):
    value={key:True for key in ('profileEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','internalTicksEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled')}
    value.update({key:False for key in ('gcStress','oomTesting','debuggerEnabled','wptSupportEnabled')});value['entropyPolicy']='off'
    value['diagnosticOnly']=True;value['buildRecipeSha256']=RECIPE
    value['classicStreamsEnabled']=label=='benchmark-classic-on'
    value['classicTraceSourcePolicy']=copy.deepcopy(CONTRACT['classicTraceSourcePolicy'])
    value['classicBenchmarkDiagnosticPolicy']={'version':CONTRACT['diagnosticVersion'],'moduleId':CONTRACT['moduleId'],'exports':CONTRACT['exports'],
      'addonSources':CONTRACT['addonSources'],'nativeInputs':342,'addonInputs':2,'totalDeclaredNativeAndBuildInputs':344,'externalEmbeddingInputs':3,
      'noPublicProcess':True,'namespace':CONTRACT['namespace'],'linkerFlags':'','noGuestExecutionByProducer':True}
    return value
check('synthetic source-shape ON model classification only',lambda:classify(model(),'benchmark-classic-on'))
check('synthetic source-shape OFF model classification only',lambda:classify(model('benchmark-classic-off'),'benchmark-classic-off'))
check('actual production342 metadata rejected before engine access',lambda:rejected(lambda:classify(old,'benchmark-classic-on')))
changed=model();changed.pop('classicTraceSourcePolicy')
check('old342 diagnostic shape missing trace contract rejected',lambda:rejected(lambda:classify(changed,'benchmark-classic-on')))
changed=model();changed['classicTraceSourcePolicy']['schedulerChanged']=True
check('trace policy substitution rejected before artifacts',lambda:rejected(lambda:classify(changed,'benchmark-classic-on')))
for field,value in [('diagnosticOnly',False),('syntheticMetadataOnly',True),('buildRecipeSha256',CONTRACT['parentRecipeSha256']),('entropyPolicy','runtime-only'),('gcStress',True),('oomTesting',True),('debuggerEnabled',True),('classicStreamsEnabled',False),('internalTicksEnabled',False),('eventsEnabled',False),('stringDecoderEnabled',False)]:
    changed=model();changed[field]=value
    check('reject wrong '+field,lambda changed=changed:rejected(lambda:classify(changed,'benchmark-classic-on')))
for key,value in [('moduleId','node:process'),('nativeInputs',344),('addonInputs',0),('totalDeclaredNativeAndBuildInputs',342),('externalEmbeddingInputs',0),('namespace','builtins::node_compat'),('linkerFlags','-Wl,--threads=1')]:
    changed=model();changed['classicBenchmarkDiagnosticPolicy'][key]=value
    check('reject wrong diagnostic '+key,lambda changed=changed:rejected(lambda:classify(changed,'benchmark-classic-on')))
check('unknown label rejected',lambda:rejected(lambda:classify(model(),'gc-off')))
compiler='/selected/clang++ --target=wasm32-wasi -O3 -DNDEBUG -DNODE_COMPAT_INTERNAL_TICKS=1 -DNODE_COMPAT_STRICT_INITIALIZATION=1 -DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1 -DNODE_COMPAT_ENTROPY_POLICY=1 -c /selected/test.cpp'
check('synthetic exact Release/public-macro command as data only',lambda:exact_release_command(compiler))
for name,bad in [('O0 after O3',compiler.replace('-O3','-O3 -O0')),('duplicate O3',compiler.replace('-O3','-O3 -O3')),('missing NDEBUG',compiler.replace('-DNDEBUG ','')),
 ('duplicate NDEBUG',compiler.replace('-DNDEBUG','-DNDEBUG -DNDEBUG')),('DEBUG definition',compiler.replace('-DNDEBUG','-DNDEBUG -DDEBUG')),('NDEBUG undefine',compiler.replace('-DNDEBUG','-DNDEBUG -UNDEBUG')),
 ('OOM enabled',compiler.replace('-DNDEBUG','-DNDEBUG -DNODE_COMPAT_OOM_TESTING=1')),('OOM zero definition',compiler.replace('-DNDEBUG','-DNDEBUG -DNODE_COMPAT_OOM_TESTING=0')),('OOM undefine',compiler.replace('-DNDEBUG','-DNDEBUG -UNODE_COMPAT_OOM_TESTING')),
 ('conflicting ticks definition',compiler.replace('-DNODE_COMPAT_INTERNAL_TICKS=1','-DNODE_COMPAT_INTERNAL_TICKS=1 -DNODE_COMPAT_INTERNAL_TICKS=0')),
 ('strict undefine',compiler.replace('-DNODE_COMPAT_STRICT_INITIALIZATION=1','-DNODE_COMPAT_STRICT_INITIALIZATION=1 -UNODE_COMPAT_STRICT_INITIALIZATION')),
 ('missing events-abort',compiler.replace('-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1 ','')),('duplicate entropy definition',compiler.replace('-DNODE_COMPAT_ENTROPY_POLICY=1','-DNODE_COMPAT_ENTROPY_POLICY=1 -DNODE_COMPAT_ENTROPY_POLICY=1'))]:
    check('reject compiler '+name,lambda bad=bad:rejected(lambda:exact_release_command(bad)))
check('pinned external3 source declarations accepted as data',lambda:validate_external_sources(CONTRACT['externalSources']))
for name in ('embedding/embedding.h','CMakeLists.txt','embedding/embedding.cpp'):
    changed=copy.deepcopy(CONTRACT['externalSources']);next(row for row in changed if row['path']==name)['sha256']='0'*64
    check('reject stable wrong external hash '+name,lambda changed=changed:rejected(lambda:validate_external_sources(changed)))
check('live adapter exact repository53512 bytes/hash',adapter)

link=': && /selected/cxx --target=wasm32-wasi -O3 -DNDEBUG -flto=thin -o starling-raw.wasm/starling-raw.wasm libbuiltin_diagnostics_classic_benchmark.a && cd /selected/build/starling-raw.wasm && /selected/wasm-opt --strip-debug -O3 -o starling-raw.wasm starling-raw.wasm\n'
check('synthetic final-link grammar accepted as data only',lambda:validate_link(link.encode()))
for name,bad in [('missing diagnostic archive',link.replace('libbuiltin_diagnostics_classic_benchmark.a','libother.a')),('duplicate stage',link+link),('wrong optimization',link.replace('-O3 -DNDEBUG','-O0 -DNDEBUG')),('extra optimization',link.replace('-O3 -DNDEBUG','-O0 -O3 -DNDEBUG')),('DEBUG flag',link.replace('-DNDEBUG','-DNDEBUG -DDEBUG')),('different LTO',link.replace('-flto=thin','-flto=full')),('link1 change',link.replace('-flto=thin','-flto=thin -Wl,--threads=1,--thinlto-jobs=1')),('post-opt drift',link.replace('--strip-debug -O3','--strip-debug -O2')),('pipeline',link.replace('&& cd','| cd'))]:
    check('reject '+name,lambda bad=bad:rejected(lambda:validate_link(bad.encode())))

proof=json.loads((HERE/'producer-transformations.json').read_bytes());source=(HERE/'build-classic-benchmark-engine.sh').read_text();restored=source
for edit in reversed(proof['edits']):assert restored.count(edit['new'])==edit['count'];restored=restored.replace(edit['new'],edit['old'])
check('all17 producer edits reverse to exact corrected production3694',lambda:(_ for _ in ()).throw(AssertionError())if len(proof['edits'])!=17 or sha(HERE/'before/build-engine.sh')!=CONTRACT['parentRecipeSha256']or restored!=(HERE/'before/build-engine.sh').read_text()else None)
check('stdin metadata imports resolve packet siblings before spec loading',lambda:(_ for _ in ()).throw(AssertionError())if source.count("sys.path.insert(0, str(pathlib.Path(packet_root)))\nbenchmark_spec = ")!=1 else None)
check('explicit actual corrected342 stage matches new policy read-only',lambda:layer().validate_sources(SOURCE_ROOT))
check('original old342 bytes rejected by corrected policy',lambda:rejected(lambda:layer().validate_sources(REPO)))
check('original containing old checkout refused before actions',lambda:rejected(lambda:require_source_root(REPO)))
check('foreign corrected checkout cannot stand in for containing packet checkout',lambda:rejected(lambda:require_source_root(SOURCE_ROOT)))
check('exact2 immutable add-on source hashes',capture_addons)
check('actual corrected parent tool dependency closure hashes read-only',lambda:tool_dependencies(SOURCE_ROOT))
for name in ('artifact_common.py','build-one.py','tool-pins.json'):
    check('byte-identical corrected ancestor '+name,lambda name=name:checked(HERE/'ancestry'/name,sha(HERE.parent/'trace-integration-candidate-v1/artifact-tools'/name)))
for path in sorted(HERE.rglob('*.py')):ast.parse(path.read_text())
blocks=re.findall(r"<<'(PY[A-Z]*)'\n(.*?)\n\1",source,re.S)
for marker,code in blocks:ast.parse(code)
check('all Python source/embedded blocks parse',lambda:None)
assert [marker for marker,_ in blocks]==['PY','PYINPUT','PYEMBED','PY']
check('producer checks namespace basename before fetch',lambda:(_ for _ in ()).throw(AssertionError())if source.index('exceeds255bytes')>source.index('fetch_checked "https://')else None)
check('exact source gate precedes output/fetch',lambda:(_ for _ in ()).throw(AssertionError())if source.index('verify-packet.py')>source.index('mkdir -p "$work_root/cache"')else None)
check('external3 authentication precedes configure',lambda:(_ for _ in ()).throw(AssertionError())if source.index('external "$source_dir"')>source.index('cmake -S "$source_dir"')else None)

scratch=OUT/'tiny-copy';scratch.mkdir();src=scratch/'source.txt';src.write_text('owned plain text only');target=scratch/'new.txt'
plan=[{'original':src,'target':target,'sha256':sha(src),'shared':False}]
check('exclusive copy plan accepts owned tiny text',lambda:validate_plan(plan,scratch/'receipt.json',scratch))
check('exclusive copy writes exact bytes with no engine data',lambda:execute_plan(plan,scratch))
check('existing unshared target rejected',lambda:rejected(lambda:validate_plan(plan,scratch/'receipt.json',scratch)))
check('duplicate copy destinations rejected',lambda:rejected(lambda:validate_plan(plan+plan,scratch/'receipt.json',scratch)))
outside=[{**plan[0],'target':OUT/'escape.txt'}]
check('outside copy destination rejected',lambda:rejected(lambda:validate_plan(outside,scratch/'receipt.json',scratch)))
link_target=scratch/'link.txt';link_target.symlink_to(src)
check('symlink copy target rejected',lambda:rejected(lambda:validate_plan([{**plan[0],'target':link_target}],scratch/'receipt.json',scratch)))
gate=OUT/'own-seal';gate.mkdir();(gate/'verify-packet.py').write_bytes((HERE/'verify-packet.py').read_bytes())
spec=importlib.util.spec_from_file_location('owned_benchmark_packet_gate',gate/'verify-packet.py');sealed=importlib.util.module_from_spec(spec);spec.loader.exec_module(sealed)
payload=gate/'payload.txt';payload.write_text('owned original')
frozen={'preparationContext':{'pathResolution':'absolute-original-preparation-context-not-relocated'},'inputs':[{'path':str(payload),'sha256':sha(payload),'bytes':payload.stat().st_size}]};seal_bytes=(json.dumps(frozen)+'\n').encode();(gate/'input-freeze.json').write_bytes(seal_bytes)
own_index={'files':[{'path':'input-freeze.json','sha256':digest(seal_bytes),'bytes':len(seal_bytes)}]};index_bytes=(json.dumps(own_index)+'\n').encode();(gate/'index.json').write_bytes(index_bytes);expected=digest(index_bytes)
check('captured owned packet/index and input seal passes',lambda:sealed.verify(expected))
payload.write_text('changed')
check('owned consumed-file tamper refused',lambda:rejected(lambda:sealed.verify(expected)));payload.write_text('owned original')
(gate/'input-freeze.json').write_text('{broken')
def assert_hash_before_parse():
    try:sealed.verify(expected)
    except AssertionError:return
    raise AssertionError('Expected manifest digest failure before JSON parse')
check('changed input manifest refused by index digest before JSON parse',assert_hash_before_parse)
(gate/'input-freeze.json').write_bytes(seal_bytes);(gate/'index.json').write_text('{broken')
check('changed index refused by captured primitive before JSON parse',assert_hash_before_parse)
result={'schemaVersion':1,'state':'PURE_SOURCE_DATA_AND_OWNED_TINY_COPY_CHECKS_PASSED','passed':len(cases),'cases':cases,'output':str(OUT),
  'syntheticPositiveModelsAreNotArtifactProof':True,'actualEngineBytesRead':False,'embeddedPythonBlocksParsed':len(blocks),
  'configureCompilerLauncherGuestOrTargetHostInvoked':False}
(OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
