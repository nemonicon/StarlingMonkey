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


P=HERE.parent/'measurement-correctness-candidate-v1'
A=HERE.parent/'measurement-correctness-reporting-amendment-v1'
def tree(root):
 result=[]
 def visit(path):
  for child in sorted(path.iterdir()):
   s=child.lstat();kind='symlink'if stat.S_ISLNK(s.st_mode)else'directory'if stat.S_ISDIR(s.st_mode)else'file'if stat.S_ISREG(s.st_mode)else None
   assert kind is not None
   result.append({'path':str(child.relative_to(root)),'kind':kind})
   if kind=='directory':visit(child)
 visit(root)
 return sorted(result,key=lambda x:x['path'])
def index(r,root,pin,count):
 doc=r.document(root/'index.json',pin,root);assert len(doc['files'])==count
 for row in doc['files']:r.checked(root/relative(row['path']),row['sha256'],row['bytes'],root)
 return doc
def main():
 r=Reader();index(r,P,'138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da',36)
 index(r,A,'0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350',14)
 parent=index(r,HERE.parent/'measurement-producer-candidate-v3','46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc',40)
 inherited=r.document(P/'inherited-inputs.json',anchor=P);assert inherited['noWorkloadOrOracleSemanticsChanged']is True and len(inherited['files'])==5
 for row in inherited['files']:
  assert r.checked(P/relative(row['path']),row['sha256'],row['bytes'],P,capture=True)==r.checked(REPO/relative(row['origin']),row['sha256'],row['bytes'],REPO,capture=True)
 workload=r.document(P/'node-workload-oracle.json',anchor=P);encoding=r.document(P/'node-encoding-oracle.json',anchor=P)
 assert workload['node']=='v22.14.0'and len(workload['expected'])==20 and workload['iterationBounds']==[1,16]
 assert workload['queueCheckpointBudget']==65536 and workload['budgetRaised']is False and len(workload['canonicalHostCounterexamples'])==14
 assert len({(x['id'],x['iterations'])for x in workload['expected']})==20
 assert {x['iterations']for x in workload['expected']}=={1,16}and len({x['id']for x in workload['expected']})==10
 assert len(encoding['expected'])==len(encoding['cases'])==14 and encoding['sameRealNodeDependenciesAndNextTick']is True
 assert encoding['traceNormalized']is encoding['liveSourceModified']is encoding['nativeOrGuestOrTargetHostExecuted']is False
 config=r.document(P/'activation-template.json',anchor=P)
 assert config['state']=='UNCONFIGURED_CLASSIC_DIAGNOSTIC_CORRECTNESS_SOURCE_ONLY'
 for k in ['producerRoot','sourceRoot','reviewedPinsPath','reviewedPinsSha256','reviewedActualEngine']:assert config[k]is None,k
 assert config['runtimeAcceptanceClaim']is config['timingAllowed']is False
 seal=r.document(P/'input-freeze.json',anchor=P);assert len(seal['inputs'])==6849 and len(seal['toolTrees'])==2 and len(seal['toolLinks'])==22
 for document,root,count in [(seal,P,6849),(r.document(A/'input-freeze.json',anchor=A),A,49)]:
  assert len(document['inputs'])==count;seen=set()
  for row in document['inputs']:
   path=(root/row['path']).absolute();assert str(path)not in seen;seen.add(str(path))
   r.checked(path,row['sha256'],row['bytes'])
 for row in seal['toolTrees']:
  root=Path(row['path']);assert str(root.resolve(strict=True))==row['realPath']
  assert root.is_dir()and not root.is_symlink();assert tree(root)==row['entries']
 import os
 roots=[Path(x['realPath'])for x in seal['toolTrees']]
 for row in seal['toolLinks']:
  path=Path(row['path']);assert path.is_symlink()and os.readlink(path)==row['linkText']
  target=path.resolve(strict=True);assert str(target)==row['resolvedTarget']and any(target.is_relative_to(x)for x in roots)
  assert ('directory'if target.is_dir()else'file')==row['targetKind']
  if row['targetKind']=='file':r.checked(target,row['targetSha256'],row['targetBytes'])
 template=(P/'runtime-preflight.template.mjs').read_text()
 rendered=template.replace('@CONFIG_SHA@',digest((P/'activation-template.json').read_bytes())).replace('@INPUTS_SHA@',digest((P/'input-freeze.json').read_bytes()))
 assert rendered==(P/'runtime-preflight.mjs').read_text()
 assert template.index('selectActivation(JSON.parse(raw))')<template.index('await seal();')<template.index("await import(pathToFileURL(join(producer,'runtime-preflight.mjs')))")
 assert template.index("await regular(join(producer,'index.json'),PRODUCER_INDEX)")<template.index("await import(pathToFileURL(join(producer,'runtime-preflight.mjs')))")
 assert "const pinsPath=config.reviewedPinsPath,pinsSha=config.reviewedPinsSha256" in template
 guest=(P/'guest.mjs').read_text();provider=(P/'native-provider.mjs').read_text();bundle=(P/'bundle-diagnostic.mjs').read_text()
 assert 'const workload=createWorkload(provider)'in guest and 'scenarioIds.flatMap(id=>[1,16]'in guest
 assert 'index>=20'in guest and '++calls'in guest and "result:await workload.run(iterations,{trace:true})"in guest
 assert "from 'starling:test-classic-benchmark'"in provider and 'dependencies={Buffer,EventEmitter,StringDecoder,nextTick}'in provider
 assert 'Buffer!==globalThis.Buffer'in provider
 assert 'queueMicrotask'not in provider and 'process'not in provider and 'createClassicStreams'not in provider
 assert "resolveId(id){return id==='starling:test-classic-benchmark'?{id,external:true}:null;}"in bundle
 expected_imports=['node:stream','node:stream/promises','node:buffer','node:events','node:string_decoder','starling:test-classic-benchmark']
 actual_bundle=r.document(P/'evidence/bundle-tests.json',anchor=P)
 assert sorted(actual_bundle['imports'])==sorted(expected_imports)and len(actual_bundle['moduleIds'])==5
 assert set(actual_bundle['moduleIds'])=={str(P.resolve()/x)for x in ['guest.mjs','native-provider.mjs','workload.mjs','encoding-cases.mjs']}|{'\0rolldown/runtime.js'}
 assert digest((P/'evidence/guest.bundle.mjs').read_bytes())==actual_bundle['bundleSha256']
 assert actual_bundle['componentizerOrGuestOrNativeBuildOrTargetHostExecuted']is False
 proof=r.document(A/'transformation-proof.json',anchor=A);assert len(proof['edits'])==9
 before=(P/'component-driver.mjs').read_text();after=(A/'proposed/component-driver.mjs').read_text()
 assert digest(before.encode())==proof['beforeSha256']and digest(after.encode())==proof['afterSha256']
 forward=before
 for row in proof['edits']:assert forward.count(row['old'])==row['count'];forward=forward.replace(row['old'],row['new'])
 assert forward==after
 reverse=after
 for row in reversed(proof['edits']):assert reverse.count(row['new'])==row['count'];reverse=reverse.replace(row['new'],row['old'])
 assert reverse==before
 assert 'assert.deepEqual(value.result,expected.oracle)'in before and 'assert.deepEqual(value.observed,encoding.expected)'in before and 'assert.deepEqual(freshJco,retained[0])'in before
 assert all(x not in after for x in ['assert.deepEqual(value.result','assert.deepEqual(value.observed','assert.deepEqual(freshJco'])
 assert 'for(let round=0;round<3;round++)'in after and 'index<20' in after and 'index<=20'in after
 assert after.count('if(error instanceof RecordedMismatch)throw error;')==3
 assert 'await requireExactJSON({label:'in after and 'fresh-Jco-full-rotation'in after
 helper=(A/'bounded-comparison.mjs').read_text()
 assert 'JSON.stringify(actual)===JSON.stringify(expected)'in helper
 assert helper.index('await writeCounterexample(')<helper.index('throw new RecordedMismatch(label)')
 assert 'node:assert'not in helper and 'inspect'not in helper.split('// Preserve complete records')[0]
 assert 'stdout:actual.stdout,stderr:actual.stderr'in after
 assert "emittedImports,[]"in after and "export run: func(case-index: u32) -> string;"in after and "export boundaries: func() -> string;"in after
 assert "selected.componentize(bundle.code" in after and "disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]"in after
 assert '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'in after
 assert after.count('await admission.recheck()')>=3 and 'await publishCompletion' in after
 source_result=r.document(P/'evidence/source-tests.json',anchor=P);tests=r.document(A/'test-results.json',anchor=A)
 assert source_result['passed']==13 and source_result['actualReviewedPins']is None and tests['passed']==4
 assert tests['ownerGuestOrWorkloadOrNativeOrPackagerOrHostInvoked']is False
 r.finish()
 result={'schemaVersion':1,'state':'INDEPENDENT_CORRECTNESS_COMPANION_AND_MANDATORY_REPORTING_AMENDMENT_SOURCE_REVIEW_PASSED',
 'parentIndexSha256':'138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da',
 'mandatoryAmendmentIndexSha256':'0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350',
 'originalPacketActivationAllowedWithoutAmendment':False,'parentFiles':36,'amendmentFiles':14,'parentInputRows':6849,'amendmentInputRows':49,
 'originalWorkloadCases':20,'originalBoundaryCases':14,'sourceBundleResidualImports':6,'guestPhysicalSources':4,'rolldownRuntimeHelpers':1,
 'driverReversals':9,'toolTrees':2,'toolLinks':22,'configurationPinsRemainNull':True,
 'nativeBuildOrGuestOrHostOrNodeWorkloadOrBundleRerun':False,'ownerCodeImported':False,'timingAllowed':False,'runtimeAcceptance':False,
 'limitations':['Unamended138a4 driver has large assert-formatting risk; only mandatory0558 afterimage is eligible for future activation.',
 'Source review does not execute current null preflight, producer/raw-artifact verifier, workloads, source test or bundler.',
 'A new independently reviewed activation must seal actual Root diagnostic authority/ON tuple, mandatory amended driver/helper, native342/addon2 and live adapter/tool closure.',
 'Actual20+14 retained/fresh/Jco/Wasmtime semantics, cumulative65536 callback budget and empirical cost remain unproved.'],
 'verifiedFiles':sorted(r.files.values(),key=lambda x:x['path'])}
 with(HERE/'results.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({'state':result['state'],'paths':len(r.files),'unamendedActivationAllowed':False,'guestExecuted':False}))
if __name__=='__main__':main()
