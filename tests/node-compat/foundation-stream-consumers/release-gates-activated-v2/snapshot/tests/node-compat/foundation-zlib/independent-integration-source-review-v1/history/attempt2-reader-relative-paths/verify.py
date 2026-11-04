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
PACKET = HERE.parent / 'trace-integration-candidate-v1'
SOURCE = Path('/private/tmp/starling-node-compat/classic-trace-source-v1')
ROOT = Path('/tmp/starling-node-compat/production-classic-trace-v1/native-freeze')
LABELS = ('normal-off', 'normal-runtime', 'gc-off', 'disabled-off')
RECIPE = '3694c88b7d000f27e11ffcac835fe0b205b2075f5b1d8d29c61f5b0038ba1cf3'
POLICY = '891a4c53dd4a7b7d776c21003acdd12c7944c6a3eca019a1d9b2be620ed8b11c'
HELPER = '43bae8056534c1a6f384961e0b054a68d44d30030e21897bd9688a8fc8b65bc9'
TOOL_PINS = 'd50e7d7ad946a80c7d7f58c23395ed1bb40ab437e53fc0f84c3a64a9c16e39f1'
PACKET_INDEX = '224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b'
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


P=HERE.parent/'integration-candidate-v1'
CLASSIC=REPO/'tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1'
SDK=Path('/tmp/starling-node-compat/improved-build/spidermonkey-dist-release/include')
STAGE=Path('/tmp/starling-node-compat/classic-trace-source-v1')
def index(r,root,pin,count=None):
 d=r.document(root/'index.json',pin,root)
 if count is not None:assert len(d['files'])==count
 for x in d['files']:r.checked(root/relative(x['path']),x['sha256'],x['bytes'],root)
 return d
def main():
 import ast
 r=Reader();index(r,P,'56a6ee5fecc921ce78e4c4402761c9fc790487eb6f2deeb6297c12cf3597fd2d',38)
 seal=r.document(P/'input-freeze.json',anchor=P);assert len(seal['inputs'])==431 and seal['allNewNativeRuntimeAuthorityNull']is True
 for x in seal['inputs']:r.checked((P/x['path']).absolute(),x['sha256'],x['bytes'])
 c=r.document(P/'contract.json',anchor=P)
 assert c['profileVersion']=='sm-node-22.14.0-m0.13'and c['namedBindings']==39 and c['namespaceBindingsIncludingDefault']==40
 assert len(c['syncOperations'])==6 and len(c['deferredCallables'])==31
 for k in ['linkedArchiveSha256','actualGuestZlibVersion','actualGuestZlibVernum','newProducerRecipeSha256','reviewedEnginePins']:assert c[k]is None,k
 for k in ['newCodecDependency','newHostServiceOrCapability','productionAdmissionOpen','installedSupport','nativeOrGuestExecuted']:assert c[k]is False,k
 for name,pin in c['parentIndices'].items():index(r,HERE.parent/name,pin)
 index(r,CLASSIC,c['classicSourceIndexSha256'],159)
 old=r.document(CLASSIC/'policy.json',c['classicSourcePolicySha256'],CLASSIC)
 before=inventory(old['expectedNativeSourceManifest'],342)
 sp=r.document(P/'source-policy.proposal.json',anchor=P);after=inventory(sp['proposedNativeSourceManifest'],350)
 assert sp['expectedAfterimageSources']==350 and sp['parentCorrectedSources']==342 and sp['old342MetadataProjectionPermitted']is False
 added=set(after)-set(before);changed={n for n in before if before[n]!=after[n]}
 assert len(added)==8 and added==set(sp['addedSourcePaths'])
 assert len(changed)==2 and changed=={x['path']for x in sp['changedParentSources']}=={'builtins/node-compat/register.cpp','cmake/builtins.cmake'}
 for name,h in after.items():
  path=P/'source'/name
  if not path.exists():path=STAGE/name
  r.checked(path,h)
 assert sum(name.endswith('.cpp')and name.startswith(('builtins/','runtime/'))for name in after)==62
 deriv=r.document(P/'source-derivations.json',anchor=P);assert len(deriv['files'])==5
 for x in deriv['files']:
  raw=r.checked(REPO/relative(x['origin']),x['beforeSha256'],capture=True)
  assert raw==r.checked(P/x['preimage'],x['beforeSha256'],capture=True)
  expected=r.checked(P/x['afterimage'],x['afterSha256'],capture=True).decode()
  forward=raw.decode()
  for edit in x['edits']:assert forward.count(edit['old'])==edit['count'];forward=forward.replace(edit['old'],edit['new'])
  assert forward==expected
  # Some CMake replacement is the whole source. Reversing explicit recorded
  # offsets handles nested inserted fragments without a global replace guess.
  reverse=expected
  for edit in reversed(x['edits']):
   for at in reversed(edit['afterOffsets']):
    assert reverse[at:at+len(edit['new'])]==edit['new'];reverse=reverse[:at]+edit['old']+reverse[at+len(edit['new']):]
  assert reverse.encode()==raw
 manifest=r.document(P/'source/builtins/node-compat/export-manifest.zlib.node-v22.14.0.json',anchor=P);module=manifest['modules']['node:zlib']
 inv=r.document(HERE.parent/'inventory.node-v22.14.0.json',anchor=REPO)
 assert set(module['exports'])=={x['name']for x in inv['exports']}|{'default'}and len(set(module['exports']))==40
 assert module['aliases']==['zlib']and module['supportedStatic']==c['syncOperations']and module['importOnlyExports']==c['deferredCallables']
 assert manifest['requiredHostInterfaces']==[] and module['limits']=={'inputBytes':1048576,'outputBytes':16777216}
 z=P/'source/builtins/node-compat/zlib'
 constants=(z/'constant-data.generated.mjs').read_text();facade=(z/'facade.mjs').read_text();kernel=(z/'kernel.cpp').read_text();codec=(z/'bounded-codec.h').read_text()
 assert '"ZLIB_VERNUM":backend.vernum'in constants and '"ZLIB_VERNUM":4865'not in constants and '"ZLIB_VERNUM":4880'not in constants
 assert '"Z_MAX_CHUNK":Infinity'in constants and 'backend.runtimeVersion !== backend.headerVersion'in constants
 assert 'std::strcmp(runtime, ZLIB_VERSION)'in kernel and kernel.count('verify_backend(cx)')==3
 assert 'JS::Int32Value(static_cast<int32_t>(ZLIB_VERNUM))'in kernel
 assert 'defined(Z_PREFIX) || defined(Z_PREFIX_SET)'in kernel
 assert kernel.index('JS_malloc(cx, length)')<kernel.index('JS::AutoCheckCannotGC no_gc(cx)')
 assert kernel.index('current_length != length')<kernel.index('std::memcpy(staging.get(), bytes, length)')
 assert kernel.index('auto result = codec::run')<kernel.index('JS_NewUint8Array(cx, bytes.size())')
 assert 'std::memcpy(destination, bytes.data(), bytes.size())'in kernel
 assert 'JS::UniqueChars staging'in kernel and 'JS::RootedObject backing'in kernel
 assert 'std::realloc(data_, capacity)'in codec and '~Bytes() { std::free(data_); }'in codec
 assert '~Stream()'in codec and 'if (encode_) deflateEnd' in codec and 'else inflateEnd' in codec
 assert 'input.size() > limit - size_'in codec and 'stream.value.avail_in == 0 ? Status::Ok : Status::TrailingData'in codec
 assert 'written == 0 && stream.value.avail_in == before'in codec
 assert 'return bufferFrom(buffer, offset, length);'in facade and 'const run = kernel.run.bind(kernel);'in facade
 for name in c['deferredCallables']:assert 'function '+name+"() { unsupported('"+name+"'); }"in facade
 for name in c['syncOperations']:assert "if (new.target) unsupported('new "+name+"');"in facade
 assert 'Reflective Proxy traps may still run'in facade and 'ordinary-record contract'in facade
 # Independent reconstruction of the exact source-only C++ literal.
 dep="import {createZlibData} from './constant-data.generated.mjs';"
 assert facade.count(dep)==1
 const_script=re.sub(r'^export function ','function ',constants,flags=re.M)
 fac_script=re.sub(r'^export function ','function ',facade.replace(dep,''),flags=re.M)
 factory="(function(argument){\n'use strict';\n"+const_script+'\n'+fac_script+'\nreturn createZlibModule(argument.kernel, argument.Buffer);\n})'
 h=hashlib.sha256()
 for name,source in [('constant-data.generated.mjs',constants),('facade.mjs',facade),('export-manifest.zlib.node-v22.14.0.json',(P/'source/builtins/node-compat/export-manifest.zlib.node-v22.14.0.json').read_text())]:h.update((name+'\0'+source+'\0').encode())
 expected='// Generated unapplied bounded zlib proposal; do not edit.\n// Canonical-source SHA-256: '+h.hexdigest()+'\nstatic constexpr const char kZlibFactorySource[] = R"SM_NODE_PROFILE('+factory+')SM_NODE_PROFILE";\n'
 assert (z/'factories.generated.h').read_text()==expected
 register=(P/'source/builtins/node-compat/register.cpp').read_text();cmake=(P/'source/cmake/builtins.cmake').read_text()
 section=register[register.index('static bool install_zlib'):register.index('bool install(api::Engine')]
 assert section.index('if (!kernel) return false;')<section.index('JS_NewPlainObject(cx)')<section.index('if (!argument) return false;')<section.index('JS_DefineProperty')
 assert 'evaluate_factory(cx, kZlibFactorySource, argument_value, &module)'in section and section.count('define_builtin_module(')==2
 assert 'option(NODE_COMPAT_ZLIB "Enable bounded synchronous node:zlib source proposal" OFF)'in cmake
 assert 'target_sources(builtin_node_compat PRIVATE builtins/node-compat/zlib/kernel.cpp)'in cmake and 'target_compile_definitions(builtin_node_compat PRIVATE NODE_COMPAT_ZLIB=1)'in cmake
 added_cmake=cmake[cmake.index('# Optional bounded zlib proposal;'):]
 assert 'find_package('not in added_cmake.replace('find_package(ZLIB) fallback.','')and ' -lz'not in added_cmake and 'target_link_libraries('not in added_cmake
 guard=(P/'source/tests/node-compat/zlib-admission.mjs').read_text();selector=(P/'source/tests/node-compat/module-selection.mjs').read_text()
 assert "Object.hasOwn(metadata, 'zlibEnabled')"in guard and "'NODE_COMPAT_ZLIB'"in guard and 'ERR_SM_NODE_ZLIB_ACTIVATION_PENDING'in guard
 assert selector.index('validateZlibSourceAdmission(metadata)')<selector.index('const classic = validateClassicSourceAdmission')
 assert '350'not in guard or 'return true'not in guard
 audit=r.document(P/'evidence/prefix-abi-audit.json',anchor=P)
 assert audit['archive']['sha256']=='298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc'and audit['archive']['bytes']==538170426
 r.checked(audit['archive']['path'],audit['archive']['sha256'],audit['archive']['bytes'])
 nm=r.checked(audit['nmRawOutput']['path'],audit['nmRawOutput']['sha256'],audit['nmRawOutput']['bytes'],capture=True).decode()
 header={}
 for x in audit['headers']:header[Path(x['path']).name]=r.checked(x['path'],x['sha256'],x['bytes'],capture=True).decode()
 assert '#include "zconf.h"'in header['zlib.h']and '#include "mozzconf.h"'in header['zconf.h']
 assert len(audit['mappings'])==7
 symbols={}
 for line in nm.splitlines():
  if ']: 'in line:
   parts=line.split(']: ',1)[1].split()
   if len(parts)>1 and parts[1]=='T':symbols.setdefault(parts[0],[]).append(line)
 for x in audit['mappings']:
  assert re.search(r'^#define\s+'+re.escape(x['headerMacro'])+r'\s+'+re.escape(x['linkedArchiveName'])+r'\s*$',header['mozzconf.h'],re.M)
  assert symbols[x['linkedArchiveName']]==x['definedExternalTextSymbols']and len(symbols[x['linkedArchiveName']])==1
  assert x['headerMacro']not in symbols and 'z_'+x['headerMacro']not in symbols
 assert audit['genericZPrefixSelected']is audit['secondCodecAdded']is audit['actualLinkResolved']is audit['runtimeZlibVersionVerified']is False
 assert audit['newGuestVernum']is None
 # Exact supported API/deallocator declaration source, no SDK invocation.
 apis={}
 for rel in ['js/experimental/TypedData.h','js/ArrayBuffer.h','js/Utility.h','js/MemoryFunctions.h']:
  apis[rel]=r.checked(SDK/rel,capture=True).decode()
 assert 'JS_GetObjectAs##Name##Array'in apis['js/experimental/TypedData.h']and 'JS_GetArrayBufferViewBuffer('in apis['js/experimental/TypedData.h']
 assert 'IsResizableArrayBufferView(JSObject* obj)'in apis['js/experimental/TypedData.h']
 assert 'UniqueChars = mozilla::UniquePtr<char[], JS::FreePolicy>'in apis['js/Utility.h']and 'js_free(const_cast<void*>(ptr))'in apis['js/Utility.h']
 assert 'JS_malloc(JSContext* cx, size_t nbytes)'in apis['js/MemoryFunctions.h']
 r.checked(REPO/'include/extension-api.h');r.checked(REPO/'cmake/add_builtin.cmake');r.checked(REPO/'cmake/spidermonkey.cmake')
 src=r.document(P/'evidence/source-model-results.json',anchor=P);assert src['passed']==68
 receipt=r.document(P/'source-receipt.json',anchor=P);assert receipt['newSdkSyntaxPerformed']is receipt['guestExecuted']is receipt['linkedNewModule']is False
 for x in P.rglob('*.py'):ast.parse(x.read_text())
 r.finish()
 result={'schemaVersion':1,'state':'INDEPENDENT_ZLIB_CONDITIONAL_SOURCE_INTEGRATION_REVIEW_PASSED_NO_BUILD',
 'indexSha256':'56a6ee5fecc921ce78e4c4402761c9fc790487eb6f2deeb6297c12cf3597fd2d','proposalFiles':38,'consumedInputs':431,
 'parentSources':342,'childSources':350,'addedNativePaths':8,'changedParentPaths':2,'unchangedParentPaths':340,'sourceDerivations':5,
 'publicBindings':40,'syncOperations':6,'deferredCallables':31,'sourceEchoChecks':68,'requiredMozSymbols':7,
 'selectedArchiveSha256':audit['archive']['sha256'],'actualNewLinkedArchiveAuthority':None,'actualGuestVersion':None,'reviewedFuturePins':None,
 'newNativeOrSdkSyntaxOrLinkOrGuestOrNodeFacadeTestExecuted':False,'installedSupport':False,'positiveProductionAdmission':False,'performanceClaim':False,
 'ownership':'JS input stages under NoGC; codec malloc output explicitly copies to rooted JS Uint8Array, then Buffer shares fresh JS backing. Output cap is not a peak-memory bound.',
 'limitations':['New kernel/backend/header-prefix source has not had SDK syntax, linking or guest execution; historical syntax/vectors do not transfer.',
 'Archive7 MOZ_Z definitions and full zlib/zconf/mozzconf mapping are static witnesses, not link extraction/visibility/runtime identity.',
 'Future350 source/recipe/macro/admission layer, actual zlibVersion/header agreement and observed backendInfo vernum required; all hinted new lineages currently rejected.',
 'Must retain independent optional kernel/queue omission rules; inventoried62 CPP paths does not imply all compile when unrelated features OFF.',
 'Need actual sync byte/error/cap, ESM/aliases/CommonJS/default, retained/fresh/GC and both-host import gates; no complete Node or memory/performance claim.'],
 'verifiedFiles':sorted(r.files.values(),key=lambda x:x['path'])}
 with(HERE/'results.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({'state':result['state'],'files':len(r.files),'guestExecuted':False}))
if __name__=='__main__':main()
