"""Independent frozen-byte reader; no producer imports, subprocesses or Wasm.

Default pins are null. Actual invocation needs a separately reviewed pins file
and its externally supplied SHA, then creates a fresh result only after checks.
Mutable original cache/database paths in metadata are never dereferenced.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import shlex
import stat
import sys

if not __debug__:
    raise RuntimeError('Verification requires Python assertions enabled')

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PACKET = HERE.parent / 'measurement-producer-candidate-v3'
SOURCE = Path('/private/tmp/starling-node-compat/classic-benchmark-trace-v2-source')
ROOT = Path('/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze')
LABELS = ('normal-off', 'normal-runtime', 'gc-off', 'disabled-off')
RECIPE = 'd98d1129db0a55abe18c2b96e7fe314ab27d6bc9a2ef481abed3f07d996fbba6'
POLICY = '891a4c53dd4a7b7d776c21003acdd12c7944c6a3eca019a1d9b2be620ed8b11c'
HELPER = '43bae8056534c1a6f384961e0b054a68d44d30030e21897bd9688a8fc8b65bc9'
TOOL_PINS = 'd50e7d7ad946a80c7d7f58c23395ed1bb40ab437e53fc0f84c3a64a9c16e39f1'
PACKET_INDEX = '46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc'
ADAPTER = '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
EXTERNAL = {
    'embedding/embedding.cpp': '9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205',
    'embedding/embedding.h': 'de2c1ae6c7f881902675d79e4bedaeece6953e70e1eac8291165ad0d5cd0eb0e',
    'CMakeLists.txt': '4bd9bb94f5b79a2c9eb8ef7d98bc4b712e7b9cc2702467436a87e1845240c5e8',
}
STRICT = {'runtime/engine.cpp', 'runtime/event_loop.cpp', 'runtime/node_tick_queue.cpp',
          'builtins/web/event/event-target.cpp'}
PRIVATE = {'builtins/node-compat/' + name + '.cpp' for name in
           ('buffer', 'entropy-bridge', 'entropy-policy', 'register', 'stream-web-kernel')}
OLD_LICENSES = {
    'builtins/node-compat/LICENSE.assert': '631987b7616a325a5b97566c232418481ddf7dbb5ecadefb991e791876cc2599',
    'builtins/node-compat/LICENSE.events': '631987b7616a325a5b97566c232418481ddf7dbb5ecadefb991e791876cc2599',
    'builtins/node-compat/LICENSE.querystring': '631987b7616a325a5b97566c232418481ddf7dbb5ecadefb991e791876cc2599',
    'builtins/node-compat/LICENSE.stream-web': '21a82bbee91262a076c2e34533d51d73475d55e889f1c42cf884c86b2a0d5773',
    'builtins/node-compat/LICENSE.string-decoder': '21a82bbee91262a076c2e34533d51d73475d55e889f1c42cf884c86b2a0d5773',
    'builtins/node-compat/LICENSE.util': '36ad6fecf56b110df1453be95d352040f2ad0defcf2e5be1321b4cef353a33da',
    'builtins/node-compat/path-vendor/LICENSES.txt': '0012fedcfc3f90565375c6cd9e9cd2e3bb75502b9ea740b98b45126cf6af1565',
}
OPENSSL_LICENSE = '7d5450cb2d142651b8afa315b5f238efc805dad827d91ba367d8516bc9d49e7a'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def hash_text(value):
    assert isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) and value != '0' * 64
    return value


def relative(value):
    assert isinstance(value, str) and value and '\\' not in value and '\0' not in value
    assert not Path(value).is_absolute() and all(part not in ('', '.', '..') for part in value.split('/'))
    return value


def inventory(rows, count=None):
    assert isinstance(rows, list) and (count is None or len(rows) == count)
    result = {}
    for row in rows:
        assert set(row) == {'path', 'sha256'}
        name = relative(row['path'])
        assert name not in result
        result[name] = hash_text(row['sha256'])
    return result


def macro(words, name, enabled):
    assert '-D' not in words and '-U' not in words, 'Split macro operands are not admitted'
    actual = [word for word in words if word == '-D' + name or word.startswith('-D' + name + '=')]
    assert actual == (['-D' + name + '=1'] if enabled else []), name
    assert '-U' + name not in words, name


def command_words(command, source, runtime, classic, gc, require_thin_lto=True):
    words = shlex.split(command)
    assert words.count('-c') == 1 and words[words.index('-c') + 1] == source
    assert words.count('-o') == 1 and '-fsyntax-only' not in words
    assert '-O3' in words and '-DNDEBUG' in words and '-UNDEBUG' not in words
    assert not any(word.startswith('-DDEBUG') for word in words)
    assert '--target=wasm32-wasi' in words
    if require_thin_lto:
        assert '-flto=thin' in words
    for name in ('NODE_COMPAT_INTERNAL_TICKS', 'NODE_COMPAT_STRICT_INITIALIZATION',
                 'NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER', 'NODE_COMPAT_ENTROPY_POLICY'):
        macro(words, name, True)
    macro(words, 'NODE_COMPAT_ENTROPY_RUNTIME_ONLY', runtime)
    macro(words, 'NODE_COMPAT_CLASSIC_STREAMS', classic)
    macro(words, 'NODE_COMPAT_GC_STRESS', gc)
    macro(words, 'NODE_COMPAT_OOM_TESTING', False)
    return words


class Reader:
    def __init__(self):
        self.files = {}

    def checked(self, path, checksum=None, size=None, anchor=None, capture=False):
        path = Path(path)
        assert path.is_absolute() and '..' not in path.parts
        if anchor is not None:
            anchor = Path(anchor)
            path.relative_to(anchor)
            cursor = path
            while True:
                assert not cursor.is_symlink(), cursor
                if cursor == anchor:
                    break
                cursor = cursor.parent
            assert anchor.is_dir()
        before = path.lstat()
        assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), path
        value = hashlib.sha256()
        chunks = [] if capture else None
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                value.update(chunk)
                if capture:
                    chunks.append(chunk)
        after = path.lstat()
        stable = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
        assert stable(before) == stable(after), path
        checksum = hash_text(checksum) if checksum is not None else None
        assert checksum is None or value.hexdigest() == checksum, path
        assert size is None or after.st_size == size, path
        row = {'path': str(path), 'sha256': value.hexdigest(), 'bytes': after.st_size}
        assert str(path) not in self.files or self.files[str(path)] == row, 'Input changed between reads'
        self.files[str(path)] = row
        return b''.join(chunks) if capture else row

    def document(self, path, checksum=None, anchor=None):
        return json.loads(self.checked(path, checksum, anchor=anchor, capture=True))

    def finish(self):
        for row in list(self.files.values()):
            self.checked(row['path'], row['sha256'], row['bytes'])


LABEL='benchmark-classic-on'
ENGINE='12a8f7dc79e12e8bc3519b3fe72e898b226bbabde6930e63d3a6c30706b88274'
META='f2f67947631136647259b7ba40422d6fb89fe943b1b74d2db4c5754bbfcc2c31'
FREEZE='b12d4ea94a2113214e0768a6ab2012f2fa7f1d62c729c2a898e322fb5f2da3d2'
def verify(r):
 index=r.document(PACKET/'index.json',PACKET_INDEX,PACKET);assert len(index['files'])==40
 for row in index['files']:r.checked(PACKET/relative(row['path']),row['sha256'],row['bytes'],PACKET)
 contract=r.document(PACKET/'contract.json',anchor=PACKET);policy=r.document(PACKET/'policy.json',POLICY,PACKET)
 native=inventory(policy['expectedNativeSourceManifest'],342);addons=inventory(contract['addonSources'],2)
 tools=r.document(PACKET/'ancestry/tool-pins.json',TOOL_PINS,PACKET)
 assert contract['recipeSha256']==RECIPE and contract['reviewedEnginePins']is None
 assert contract['freezeRoot']==str(ROOT)and contract['diagnosticVersion']=='sm-classic-benchmark-trace-diagnostic-v3'
 assert contract['parentRecipeSha256']=='3694c88b7d000f27e11ffcac835fe0b205b2075f5b1d8d29c61f5b0038ba1cf3'
 m=r.document(ROOT/(LABEL+'.engine.wasm.build.json'),META,ROOT);f=r.document(ROOT/(LABEL+'-freeze-receipt.json'),FREEZE,ROOT)
 assert f['schemaVersion']==1 and f['state']=='immutable-classic-trace-benchmark-diagnostic-engine-frozen'
 for k,v in {'label':LABEL,'recipeSha256':RECIPE,'engineSha256':ENGINE,'engineBytes':9973970,'metadataSha256':META,'sourceIndexSha256':PACKET_INDEX,
  'nativeInputsVerified':342,'addonInputsVerified':2,'totalDeclaredNativeAndBuildInputs':344,'externalEmbeddingInputsVerified':3,
  'actualNativeCommands':61,'actualStrictCommands':4,'actualPrivateCommands':5,'actualEmbeddingCommands':1,'actualDiagnosticCommands':1,
  'diagnosticOnly':True,'productionSelectorRefused':True,'classicStreamsEnabled':True,'reviewedPinsCreated':False,'guestExecuted':False,'runtimeAcceptanceClaim':False}.items():assert f[k]==v,k
 assert m['buildRecipeSha256']==RECIPE and m['engineSha256']==ENGINE and m['engineBytes']==9973970
 assert m['diagnosticOnly']is True and not m.get('syntheticMetadataOnly',False)
 for k in ['profileEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled',
  'classicStreamsEnabled','internalTicksEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled','sourceInputsCapturedBeforeBuild',
  'componentizeSourcesCapturedBeforeBuild','buildRecipeCheckedBeforeAndAfterBuild']:assert m[k]is True,k
 for k in ['gcStress','oomTesting','debuggerEnabled','wptSupportEnabled']:assert m[k]is False,k
 assert m['entropyPolicy']=='off'and m['hostApi']=='wasi-0.2.10'
 assert inventory(m['sourceManifest'],342)==native and inventory(m['componentizeSourceManifest'],3)==EXTERNAL
 dp=m['classicBenchmarkDiagnosticPolicy'];ev=dp['evidence']
 for k,v in {'version':contract['diagnosticVersion'],'moduleId':'starling:test-classic-benchmark','exports':['default','nextTick'],
  'namespace':'diagnostics::classic_benchmark','addonSources':contract['addonSources'],'nativeInputs':342,'addonInputs':2,
  'totalDeclaredNativeAndBuildInputs':344,'externalEmbeddingInputs':3,'noPublicProcess':True,'linkerFlags':'','noGuestExecutionByProducer':True}.items():assert dp[k]==v,k
 assert ev['version']=='benchmark-before-after-command-config-v1'and ev['exactBytesUnchanged']is True
 planned={}
 def add(name,h):
  relative(name);hash_text(h);assert name not in planned or planned[name]==h;planned[name]=h
 for name,h in native.items():add('source/'+name,h)
 for name,h in addons.items():add('addon/'+name,h)
 for name,h in EXTERNAL.items():add('componentize-source/'+name,h)
 assert len(tools['toolDependencies'])==92
 for row in tools['toolDependencies']:add('tooling/repository/'+relative(row['path']),row['sha256'])
 assert f['toolDependencyClosure']==[{'path':str(ROOT/'tooling/repository'/x['path']),'sourcePath':x['path'],'sha256':x['sha256'],'bytes':x['bytes']}for x in tools['toolDependencies']]
 licenses={**OLD_LICENSES,**{n:h for n,h in native.items()if Path(n).name.startswith(('LICENSE','NOTICE'))}}
 assert len(licenses)==9
 for name,h in licenses.items():add('source/'+name,h)
 add('licenses/openssl-LICENSE.txt',OPENSSL_LICENSE);add('tooling/wasi_snapshot_preview1.wasm',ADAPTER);add('producer/index.json',PACKET_INDEX)
 for row in index['files']:add('producer/'+row['path'],row['sha256'])
 for suffix,h in {'.engine.wasm':ENGINE,'.engine.wasm.build.json':META,'-CMakeCache.txt':m['cmakeCacheSha256'],'-compile_commands.json':m['compileCommandsSha256']}.items():add(LABEL+suffix,h)
 pre=r.document(ROOT/(LABEL+'-witness/before-capture.json'),ev['beforeCaptureSha256'],ROOT)
 assert pre['recipeSha256']==RECIPE and pre['addonSources']==contract['addonSources']and pre['files']==ev['before']and pre['collectionCommands']==ev['collectionCommands']
 add(LABEL+'-witness/before-capture.json',ev['beforeCaptureSha256'])
 assert len(ev['before'])==len(ev['after'])==8
 for b,a in zip(ev['before'],ev['after']):
  assert b['name']==a['name']and b['sha256']==a['sha256']and b['bytes']==a['bytes']
  assert r.checked(b['path'],b['sha256'],b['bytes'],capture=True)==r.checked(a['path'],a['sha256'],a['bytes'],capture=True)
  for side,row in [('before',b),('after',a)]:add(LABEL+'-witness/'+side+'/'+relative(row['name']),row['sha256'])
 assert {x['name']for x in ev['before']}=={'CMakeCache.txt','compile_commands.json','builtins.incl','parent-targets.commands.txt','parent-targets.commands.txt.stderr','final-link.commands.txt','final-link.commands.txt.stderr','tool-witnesses.json'}
 for name in ['builtins.incl','parent-targets.commands.txt','final-link.commands.txt']:add(LABEL+'-'+name,next(x['sha256']for x in ev['after']if x['name']==name))
 refusal=r.document(ROOT/(LABEL+'-production-refusal.json'),anchor=ROOT)
 assert refusal=={'schemaVersion':1,'state':'RAW_BENCHMARK_METADATA_CLASSIFIED_PRODUCTION_SELECTOR_REFUSED','classicStreamsEnabled':True,'label':LABEL,'productionSelectorRefused':True,'metadataProjected':False,'engineBytesRead':False,'guestExecuted':False}
 add(LABEL+'-production-refusal.json',r.files[str(ROOT/(LABEL+'-production-refusal.json'))]['sha256'])
 tw=r.document(ROOT/(LABEL+'-witness/after/tool-witnesses.json'),anchor=ROOT);assert tw==f['toolWitnesses']and len(tw)==6
 import os
 for i,row in enumerate(tw):
  path=Path(row['path']);assert path.is_symlink()is row['symlink']
  if row['symlink']:assert os.readlink(path)==row['linkText']
  assert str(path.resolve(strict=True))==row['resolvedPath'];r.checked(row['resolvedPath'],row['sha256'],row['bytes'])
  assert row['frozenCopyRequired']is(row['bytes']<1048576)
  if row['frozenCopyRequired']:add(LABEL+'-tools/'+str(i)+'-'+Path(row['resolvedPath']).name,row['sha256'])
 rust,ssl=m['generatedRustProject'],m['openssl'];audit=ssl['completeSourceAudit']
 for name,h in {'Cargo.toml':rust['manifestSha256'],'Cargo.lock':rust['lockSha256'],'openssl-before.json':audit['beforeReportSha256'],
  'openssl-receipt.txt':ssl['receiptSha256'],'openssl-configure.txt':ssl['configureRecipe']['sha256'],'openssl-configdata.pm':ssl['configdata']['sha256'],'libcrypto.a':ssl['library']['sha256']}.items():add(LABEL+'-'+name,h)
 copies={str(Path(x['path']).relative_to(ROOT)):x for x in f['copies']}
 assert len(copies)==len(f['copies'])==len(planned)==525 and {n:x['sha256']for n,x in copies.items()}==planned
 original_count=0
 for name,row in copies.items():
  r.checked(ROOT/name,row['sha256'],row['bytes'],ROOT)
  if row['original']is not None:r.checked(row['original'],row['sha256'],row['bytes']);original_count+=1
 assert original_count==521
 assert {x['path']:x['sha256']for x in f['licenses']}=={str(ROOT/n):h for n,h in planned.items()if Path(n).name.startswith(('LICENSE','NOTICE'))or Path(n).name=='openssl-LICENSE.txt'}
 cache={}
 for line in (ROOT/(LABEL+'-CMakeCache.txt')).read_text().splitlines():
  k,colon,rest=line.partition(':')
  if colon and '='in rest:assert k not in cache;cache[k]=rest.partition('=')[2]
 assert m['requestedCMakeOptions']==m['observedCMakeOptions']
 for k,v in m['observedCMakeOptions'].items():assert cache[k]==v,k
 expected={'CMAKE_BUILD_TYPE':'Release','WEVAL':'OFF','USE_WASM_OPT':'ON','CMAKE_EXE_LINKER_FLAGS':'','NODE_COMPAT_ENTROPY_MODE':'OFF','NODE_COMPAT_GC_STRESS':'OFF','NODE_COMPAT_OOM_TESTING':'OFF','ENABLE_JS_DEBUGGER':'OFF','ENABLE_BUILTIN_WPT_SUPPORT':'OFF','ENABLE_BUILTIN_NODE_COMPAT':'ON','NODE_COMPAT_LOCKED_RUST':'ON','NODE_COMPAT_INTERNAL_TICKS':'ON','NODE_COMPAT_CLASSIC_STREAMS':'ON','ENABLE_BUILTIN_DIAGNOSTICS_CLASSIC_BENCHMARK':'ON','CMAKE_PROJECT_ComponentizeJS_INCLUDE':str(SOURCE/'tests/node-compat/foundation-classic-streams/measurement-extension-candidate-v1/benchmark.cmake'),**{'NODE_COMPAT_'+n:'ON'for n in ['PATH','EVENTS','STRING_DECODER','ASSERT','QUERYSTRING','UTIL','STREAM_WEB']}}
 for k,v in expected.items():assert cache[k]==v,k
 assert cache.get('ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS','OFF')=='OFF'
 db=r.document(ROOT/(LABEL+'-compile_commands.json'),m['compileCommandsSha256'],ROOT);mapped={};layout=[]
 for row in db:
  if row['file'].startswith((str(SOURCE/'runtime')+'/',str(SOURCE/'builtins')+'/'))and row['file'].endswith('.cpp'):
   name=str(Path(row['file']).relative_to(SOURCE));assert name not in mapped;mapped[name]=row['command'];layout.append(row['command'])
 cpp={n for n in native if n.endswith('.cpp')and n.startswith(('runtime/','builtins/'))};assert set(mapped)==cpp and len(mapped)==61
 ticks,classic,strict,protected=[m[x]for x in ['internalTickPolicy','classicStreamsPolicy','strictEventExceptionPolicy','protectedAbortListenerPolicy']]
 assert layout==ticks['actualLayoutCompileCommands']==protected['actualLayoutCompileCommands']
 assert ticks['actualQueueCompileCommands']==[mapped['runtime/node_tick_queue.cpp']]
 assert sorted(strict['actualNativeCompileCommands'])==sorted(mapped[n]for n in STRICT)
 assert sorted(classic['actualPrivateTargetCompileCommands'])==sorted(mapped[n]for n in PRIVATE)
 for name,cmd in mapped.items():command_words(cmd,str(SOURCE/name),False,name in PRIVATE,False)
 static=r.document(PACKET/'parent-policy-values.json',contract['parentPolicyValuesSha256'],PACKET)
 for field,values in static.items():
  for k,v in values.items():assert m[field][k]==v,(field,k)
 parent_sources=[str(Path(cache['CMAKE_HOME_DIRECTORY'])/'embedding/embedding.cpp'),str(SOURCE/'tests/node-compat/foundation-classic-streams/measurement-extension-candidate-v1/benchmark-extension.cpp')]
 parent=[]
 for source in parent_sources:
  commands=[]
  for line in (ROOT/(LABEL+'-parent-targets.commands.txt')).read_text().splitlines():
   words=shlex.split(line)
   if words.count('-c')==1 and words[words.index('-c')+1]==source:commands.append(line)
  assert len(commands)==1;words=command_words(commands[0],source,False,False,False,require_thin_lto=False)
  assert not any(w.startswith('-flto')for w in words)and not any(x['file']==source for x in db);parent.append(commands)
 embedding,diagnostic=parent
 assert embedding==m['actualEmbeddingCompileCommands']==ticks['actualEmbeddingCompileCommands']==protected['actualEmbeddingCompileCommands']==dp['actualEmbeddingCompileCommands']
 assert diagnostic==dp['actualDiagnosticCompileCommands']
 assert ev['collectionCommands']=={'parent-targets.commands.txt':['ninja','-C',str(Path(m['cmakeCachePath']).parent),'-t','commands','builtin_componentize_embedding','builtin_diagnostics_classic_benchmark'],'final-link.commands.txt':['ninja','-C',str(Path(m['cmakeCachePath']).parent),'-t','commands','starling-raw.wasm/starling-raw.wasm']}
 text=(ROOT/(LABEL+'-builtins.incl')).read_text();assert text.count('NS_DEF(diagnostics::classic_benchmark)')==text.count('NS_DEF(builtins::node_compat)')==1
 assert text.index('NS_DEF(diagnostics::classic_benchmark)')>text.index('NS_DEF(builtins::node_compat)')
 links=[]
 for line in (ROOT/(LABEL+'-final-link.commands.txt')).read_text().splitlines():
  words=shlex.split(line)
  if '-o'not in words or 'starling-raw.wasm/starling-raw.wasm'not in words:continue
  assert chr(96)not in line and '$('not in line and not any(w in words for w in ['|',';','||'])
  segments=[[]]
  for word in words:
   if word=='&&':segments.append([])
   else:segments[-1].append(word)
  assert len(segments)==4 and segments[0]==[':']
  cmd,post=segments[1],segments[3];assert cmd.count('-o')==1 and cmd[cmd.index('-o')+1]=='starling-raw.wasm/starling-raw.wasm'
  assert [x for x in cmd if re.fullmatch('-O[0-9sz]',x)]==['-O3']and '-DNDEBUG'in cmd
  assert [x for x in cmd if x.startswith('-flto')]==['-flto=thin']and not any('--threads'in x or '--thinlto-jobs'in x for x in cmd)
  assert sum(x.endswith('libbuiltin_diagnostics_classic_benchmark.a')for x in cmd)==1
  assert len(segments[2])==2 and segments[2][0]=='cd'and post[1:]==['--strip-debug','-O3','-o','starling-raw.wasm','starling-raw.wasm'];links.append((cmd,post))
 assert len(links)==1;cmd,post=links[0]
 tool_paths={shlex.split(x[0])[0]for x in parent}|{cmd[0],post[0]}|{cache[k]for k in ['CMAKE_LINKER','CMAKE_CXX_COMPILER_AR','CMAKE_CXX_COMPILER_RANLIB']}
 assert {x['path']for x in tw}==tool_paths
 trace=policy['classicTraceSourcePolicy'];assert trace==m['classicTraceSourcePolicy']==f['classicTraceSourcePolicy']==contract['classicTraceSourcePolicy']
 old=r.document(HERE.parent/'integration-candidate-v1/policy.json',trace['previousPolicySha256'],REPO);before=inventory(old['expectedNativeSourceManifest'],342)
 changed={n for n in before if before[n]!=native[n]};assert len(changed)==3 and set(before)==set(native)and len(native)-len(changed)==339
 assert changed=={x['path']for x in trace['changes']}and trace['schedulerChanged']is trace['moduleSurfaceChanged']is trace['nativeBoundaryAbiChanged']is False
 assert trace['rawVendorFilesChanged']==0 and trace['newHostInterfaces']==[]
 assert old['strictPolicyVersion']==policy['strictPolicyVersion']==strict['version']and old['protectedPolicyVersion']==policy['protectedPolicyVersion']==protected['version']
 semantic=f['semanticSourceProvenance'];base=ROOT/'tooling/repository/tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1'
 assert semantic['correctedReceiptAnnotationBase']==str(base)and semantic['primaryPinsPath']==str(base/'primary-source-pins.json')and semantic['nodeMitNoticePath']==str(base/'LICENSE.node')
 primary=r.document(semantic['primaryPinsPath'],semantic['primaryPinsSha256'],ROOT);assert primary['release']=='v22.14.0'and len(primary['sources'])==3
 for x in primary['sources']:assert x['url'].startswith('https://raw.githubusercontent.com/nodejs/node/v22.14.0/');r.checked(base/relative(x['path']),x['sha256'],x['bytes'],ROOT)
 r.checked(semantic['nodeMitNoticePath'],semantic['nodeMitNoticeSha256'],anchor=ROOT)
 assert rust['cargoBuildLocked']is rust['manifestAndLockCheckedBeforeAndAfterBuild']is True
 assert rust['lockSha256']==rust['versionedLockSha256']==native['runtime/crates/staticlib-template/Cargo.lock']
 assert audit['sourceFilesVerified']==4650 and audit['beforeAndAfterBuild']is True
 ba=r.document(ROOT/(LABEL+'-openssl-before.json'),audit['beforeReportSha256'],ROOT)
 assert ba['state']=='verified-complete-source'and ba['missingFiles']==ba['unexpectedFiles']==[]
 for k,v in ba.items():assert audit[k]==v
 assert copies[LABEL+'-libcrypto.a']['bytes']==ssl['library']['bytes']
 work=Path(m['enginePath']).parent.parent;stem=Path(m['enginePath']).stem
 assert r.document(work/('source-inputs-'+stem+'.json'),m['sourceInputManifestSha256'])==m['sourceManifest']
 assert r.document(work/('componentize-native-inputs-'+stem+'.json'),m['componentizeInputManifestSha256'])==m['componentizeSourceManifest']
 assert r.document(pre['addonManifestPath'])==contract['addonSources']
 seal=r.document(PACKET/'input-freeze.json',anchor=PACKET);assert len(seal['inputs'])==1817
 for x in seal['inputs']:r.checked(x['path'],x['sha256'],x['bytes'])
 launchroot=ROOT.parent/'builds'/LABEL
 launch=r.document(launchroot/'result.json','9f541be031534995c9a228600698685104712f49952824f7e90d00062d0e84d2',launchroot)
 assert launch['rawChildExitCode']==launch['status']==launch['launcherExitCode']==0 and launch['evidenceComplete']is True
 assert launch['recipeSha256']==RECIPE and launch['sourceIndexSha256']==PACKET_INDEX and launch['ownedGroupCleanup']['complete']is True
 assert launch['requiredStartFreeBytes']==2147483648 and launch['stopBelowFreeBytes']==838860800
 for k in ['NODE_COMPAT_JOBS','BINARYEN_CORES','RAYON_NUM_THREADS','CARGO_BUILD_JOBS']:assert launch['explicitEnvironment'][k]=='1'
 assert '[109/109]'in r.checked(launchroot/'build.log',launch['logSha256'],capture=True).decode()
 rr=r.document(HERE.parent/'production-adoption-v1/measurement-producer-v3-on-native-root-results.json','4f1657ca9ef15db110453e76b105fedc132267e0525cba025b16b75a4ae1325d',REPO)
 for x in rr['files']:r.checked(x['path'],x['sha256'],x['bytes'])
 assert rr['guestExecuted']is rr['runtimeAcceptanceClaim']is rr['oldV2FailedEvidenceReused']is False
 assert r.checked(ROOT/(LABEL+'.engine.wasm'),ENGINE,9973970,ROOT,capture=True)[:8]==b'\0asm\x01\0\0\0'
 assert f['allInputsValidatedBeforeCopies']is f['allCopiesAndOriginalsRehashed']is True
 r.finish()
 return {'schemaVersion':1,'state':'INDEPENDENT_CORRECTED_DIAGNOSTIC_V3_ON_NATIVE_FREEZE_VERIFIED_NO_GUEST','verifiedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'engineSha256':ENGINE,'engineBytes':9973970,'metadataSha256':META,'freezeReceiptSha256':FREEZE,'sourceIndexSha256':PACKET_INDEX,'recipeSha256':RECIPE,
 'frozenCopies':525,'originalCopiesRehashed':521,'nativeInputs':342,'addonInputs':2,'externalEmbeddingInputs':3,'nativeCommands':61,'strictCommands':4,'privateCommands':5,
 'embeddingCommands':1,'diagnosticCommands':1,'beforeAfterWitnessFiles':8,'sourcePreparationWitnesses':1817,'toolSourceClosure':92,
 'recordedProductionSelectorRefused':True,'selectorRerun':False,'diagnosticOnly':True,'nativeBuildRerun':False,'producerOrFreezerImported':False,'guestExecuted':False,'runtimeAcceptance':False,'performanceClaim':False,
 'limitations':['Source/admission/refusal records are authenticated as data, not rerun.','No component imports/exports, JS semantics, callback budget, Node parity, GC/reset or timing verified.',
 'OpenSSL4650 source audit reconciled; full original tree/downloaded archives not reread.','Generated Clang link/post-opt command checked; spawned LLD child argv/thread count not observed.',
 'Before/after tool hashes and aliases authenticated; large binaries remain external references.','Historical source-only annotations preserved; failed v2 output is ancestry only and never relabelled v3 evidence.'],
 'verifiedFiles':sorted(r.files.values(),key=lambda x:x['path'])}
if __name__=='__main__':
 assert len(sys.argv)==1;r=Reader();result=verify(r)
 with(HERE/'native-on-results.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({'state':result['state'],'files':len(r.files),'copies':525,'originals':521,'runtimeAcceptance':False}))
