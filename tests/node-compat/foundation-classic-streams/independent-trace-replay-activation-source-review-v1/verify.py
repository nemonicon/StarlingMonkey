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


P=HERE.parent/'trace-replay-activation-candidate-v1'
BASE=HERE.parent/'production-regression-activated-v3'
RUNTIME=HERE.parent/'production-trace-runtime-activated-v1'
HTTP=HERE.parent/'classic-http-candidate-v1'
STAGE=Path('/tmp/starling-node-compat/classic-trace-source-v1')
CANON=STAGE.resolve(strict=True)
REPLAY=CANON/'tests/node-compat/foundation-classic-streams/production-trace-regression-activated-v1'
HTTP_OUT=CANON/'tests/node-compat/foundation-classic-streams/production-trace-http-activated-v1'
PINS='182e8b724d94ebf73450c0ffcea81fb19b902028e2839bd2a9d1452ab7fab5eb'
REVIEW='ce88ac3495afdf97718a34f7bf2c2360613f95a91f5c193e556c87269b4a8be0'
RUNTIME_INDEX='e1f87cd6a2fd09ff34055187bfb938c2b094c3fd333ef9f57b6a1eea4c175b78'
def indexed(r,root,pin,count):
 index=r.document(root/'index.json',pin,root);assert len(index['files'])==count
 for x in index['files']:r.checked(root/relative(x['path']),x['sha256'],x['bytes'],root)
 return index
def proof(r,row,path):
 before=r.checked(row['origin'],row['beforeSha256'],capture=True).decode()
 after=r.checked(path,row['afterSha256'],capture=True).decode()
 forward=before
 for edit in row['edits']:assert forward.count(edit['old'])==edit['count'];forward=forward.replace(edit['old'],edit['new'])
 assert forward==after
 backward=after
 for edit in reversed(row['edits']):assert backward.count(edit['new'])==edit['count'];backward=backward.replace(edit['new'],edit['old'])
 assert backward==before
def main():
 import ast,os
 r=Reader();indexed(r,P,'8851e255cb51ac3db02d25946854fef0c8d9e60fac5db7042e180c2b20b2af58',124)
 indexed(r,BASE,'577dbad5759ef06f075763c2a793ae278fddc15df8f4f61edc9a7d2de51ecb51',82)
 indexed(r,RUNTIME,RUNTIME_INDEX,26)
 indexed(r,HTTP,'ced484750a07c7897b0e40f64da85416d32793bf083082072d304b094ceec982',63)
 seal=r.document(P/'input-freeze.json',anchor=P);assert len(seal['inputs'])==15094
 for x in seal['inputs']:r.checked((P/x['path']).absolute(),x['sha256'],x['bytes'])
 pins=r.document(RUNTIME/'runtime-pins.json',PINS,RUNTIME);review=r.document(RUNTIME/'root-review-receipt.json',REVIEW,RUNTIME)
 assert pins['state']=='REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1'and review['state']=='ROOT_REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1'
 assert review['reviewedPinsSha256']==PINS and review['configuredSourceRoot']==str(STAGE)
 assert review['sourceFiles']==342 and review['recipeSha256']=='3694c88b7d000f27e11ffcac835fe0b205b2075f5b1d8d29c61f5b0038ba1cf3'
 labels={'normal-off','normal-runtime','gc-off','disabled-off'};assert set(pins['variants'])==set(review['variants'])==labels
 runtime_receipt=r.document(RUNTIME/'source-receipt.json',anchor=RUNTIME)
 assert runtime_receipt['state']=='ACTUAL_REVIEWED_CLASSIC_TRACE_RUNTIME_FAMILY_CREATED_NOT_EXECUTED'and runtime_receipt['engineMetadataRewritten']is False
 for label,pin in pins['variants'].items():
  assert pin['state']=='reviewed-real-classic-trace-production-freeze'and pin['variant']==label and pin['sourceFiles']==342
  assert pin['sourceContractVersion']=='sm-classic-trace-source-v1'and pin.get('diagnosticOnly',False)is False
  assert pin['classicStreamsEnabled']is(label!='disabled-off')and pin['gcStress']is(label=='gc-off')
  assert pin['entropyPolicy']==('runtime-only'if label=='normal-runtime'else'off')
  for key in ['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']:
   assert pin[key]==review['variants'][label][key]==runtime_receipt['actualArtifacts'][label][key]
 payload={str(x.relative_to(P/'payload')):x.read_bytes()for x in (P/'payload').rglob('*')if x.is_file()}
 payload['native-preflight.template.mjs']=(P/'native-preflight.template.mjs').read_bytes()
 records=r.document(BASE/'derivations.json',anchor=BASE)['records'];assert len(records)==64
 changed=[x['destinationPath']for x in records if payload[x['destinationPath']]!=(BASE/x['destinationPath']).read_bytes()]
 assert set(changed)=={'release/helpers/native-scalar-harness.mjs','common/runners/allocator-gc.mjs'}and len(records)-len(changed)==62
 bp=r.document(P/'body-transformations.json',anchor=P);assert len(bp['files'])==3
 for x in bp['files']:proof(r,x,P/x['path'])
 hp=r.document(P/'http-transformations.json',anchor=P);assert len(hp['files'])==21
 for x in hp['files']:proof(r,x,P/'http-payload'/x['path'])
 assert bp['guestOrOracleBodiesChanged']is bp['fullStrictAndProtectedTagsChanged']is False
 assert hp['baselineBodyModified']is hp['ordinary19OrNodeOracleModified']is hp['hostAssertionsOrTransportModified']is False
 policy=r.document(HERE.parent/'trace-integration-candidate-v1/policy.json',POLICY,REPO)
 canonical=inventory(policy['expectedNativeSourceManifest'],342)
 tools=r.document(HERE.parent/'trace-integration-candidate-v1/artifact-tools/tool-pins.json',TOOL_PINS,REPO)
 canonical.update({x['path']:x['sha256']for x in tools['toolDependencies']})
 def map_replay(name,pin):
  doc=r.document(BASE/name,pin,BASE);base=(BASE/name).parent;rows={};mapping=[]
  for x in doc['inputs']:
   path=Path(os.path.abspath(base/x['path']))
   if path.is_relative_to(BASE):
    rel=str(path.relative_to(BASE))
    if rel=='capability/input-freeze.json':continue
    if rel in payload:rows[str(REPLAY/rel)]=digest(payload[rel]);continue
   target=path;sha=x['sha256']
   if path.is_relative_to(REPO):
    rel=str(path.relative_to(REPO));target=CANON/rel;sha=canonical.get(rel,sha)
    mapping.append({'before':str(path),'after':str(target),'beforeSha256':x['sha256'],'afterSha256':sha})
   r.checked(target,sha);key=str(target);assert key not in rows or rows[key]==sha;rows[key]=sha
  return doc,rows,mapping
 root_doc,root_rows,root_mapping=map_replay('input-freeze.json','a9c41e39e811620a27d71cce21f084a17c7c0f785ae69dd6b9d2c29085e23a97')
 cap_doc,cap_rows,cap_mapping=map_replay('capability/input-freeze.json','24ade3ad845315b96190b3977c7f7e256faf1e16ba274f46b86445d1a944475a')
 assert len(root_doc['inputs'])==2055 and len(cap_doc['inputs'])==2054
 live=root_doc['liveComputedInputs'];assert len(live)==8
 for name in live:
  expected=canonical[name];assert root_rows[str(CANON/name)]==cap_rows[str(CANON/name)]==expected;r.checked(CANON/name,expected)
 assert json.loads(payload['capability/http-component-pins.json'])['component']is None
 hpayload={str(x.relative_to(P/'http-payload')):x.read_bytes()for x in (P/'http-payload').rglob('*')if x.is_file()}
 assert json.loads(hpayload['capability/component-pins.json'])['component']is None
 hdoc=r.document(HTTP/'input-freeze.json','511723ec0ef2079d3fac2f6a6f78f2fa26c3be7d15cf55f7ec03a411e028193b',HTTP);assert len(hdoc['inputs'])==7518
 oldfreeze=Path('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze');hrows={};hmap=[];skip_old_native=0
 for x in hdoc['inputs']:
  path=Path(os.path.abspath(HTTP/x['path']))
  if path.is_relative_to(HTTP):
   rel=str(path.relative_to(HTTP))
   if rel in hpayload or rel=='capability/preflight.mjs':continue
  if path.is_relative_to(oldfreeze)or path.is_relative_to(oldfreeze.resolve(strict=True)):skip_old_native+=1;continue
  target=path;sha=x['sha256']
  if path.is_relative_to(REPO):
   rel=str(path.relative_to(REPO));target=CANON/rel;sha=canonical.get(rel,sha);hmap.append({'before':str(path),'after':str(target),'beforeSha256':x['sha256'],'afterSha256':sha})
  r.checked(target,sha);assert str(target)not in hrows or hrows[str(target)]==sha;hrows[str(target)]=sha
 for name in live:assert hrows[str(CANON/name)]==canonical[name]
 template=(P/'native-preflight.template.mjs').read_text();act=(P/'activate.py').read_text();ha=(P/'activate-http-source.py').read_text()
 assert template.index('const index=await indexedRuntime(),pins=await authority(index)')<template.index("await import(pathToFileURL(join(RUNTIME,'runtime-preflight.mjs')))")
 assert 'const nativeRecheck=native.recheck;'in template and 'await authority(index);await ownSeal();'in template
 assert "CANONICAL_SOURCE_ROOT = SOURCE_ROOT.resolve(strict=True)"in act and 'CANONICAL_SOURCE_ROOT / FAMILY_RELATIVE'in act
 assert act.index('load_authority(args.pins')<act.index('staging.mkdir(exist_ok=False)')
 assert act.index('indexed(RUNTIME, RUNTIME_SHA)')<act.index('staging.mkdir(exist_ok=False)')
 assert "runtime_receipt['engineMetadataRewritten'] is False"in act
 assert 'recheck(); assert not OUTPUT.exists() and not OUTPUT.is_symlink(); staging.rename(OUTPUT)'in act
 assert "--replay-index-sha256"in ha and "indexed(REPLAY, args.replay_index_sha256)"in ha
 httpcontract=(P/'http-payload/capability/http-contract.mjs').read_text()
 assert 'ROOT_REVIEWED_CLASSIC_TRACE_COMBINED_HTTP_COMPONENT_V1'in httpcontract and 'reviewed-classic-trace-combined-http-component'in httpcontract
 assert "assert.equal(pin.sourceEntryPath,join(here,'http-component.mjs')"in httpcontract
 assert 'resolve(pin.root)===pin.root'in httpcontract and "!pin.root.includes('\\0')"in httpcontract
 assert 'external reviewed component phase path and exact digest'in httpcontract and "Component phase changed before JSON parsing"in httpcontract
 hosts=(P/'http-payload/capability/run-http-wasmtime.mjs').read_text()
 assert hosts.index("NODE_COMPAT_HTTP_REQUIRE_INTRINSICS,'1'")<hosts.index('await verifyHTTPReady()')
 captext=(P/'http-payload/capability/capabilities.mjs').read_text()
 assert all(x in captext for x in ['wasi:clocks/monotonic-clock@0.2.10','wasi:http/types@0.2.10','wasi:io/error@0.2.10','wasi:io/poll@0.2.10','wasi:io/streams@0.2.10'])
 assert "callableImports,[]"in captext and "coreClockImports,[]"in captext
 bundle=(P/'http-payload/test-bundle.mjs').read_text();assert 'const imports=['in bundle and '.sort();'in bundle and "sourceFiles:342"in bundle
 assert "componentizerOperationInvoked:false,bundleExecuted:false,guestExecuted:false,targetHostExecuted:false"in bundle
 assert not REPLAY.exists()and not HTTP_OUT.exists()and not REPLAY.with_name(REPLAY.name+'.staging').exists()and not HTTP_OUT.with_name(HTTP_OUT.name+'.staging').exists()
 stored=r.document(P/'evidence/source-tests.json',anchor=P);http_tests=r.document(P/'evidence/http-source-tests.json',anchor=P);guard=r.document(P/'evidence/guard-tests.json',anchor=P)
 assert stored['passed']==49 and http_tests['passed']==86 and guard['passed']==7
 old_ast={x.removeprefix('Python AST ')for x in stored['checks']if x.startswith('Python AST ')}
 current_ast={str(x.relative_to(P))for x in P.rglob('*.py')}
 assert len(old_ast)==8 and len(current_ast)==9 and current_ast-old_ast=={'seal-source.py'}
 for x in P.rglob('*.py'):ast.parse(x.read_text())
 r.finish()
 result={'schemaVersion':1,'state':'INDEPENDENT_TRACE_REPLAY_AND_HTTP_ACTIVATION_SOURCE_REVIEW_PASSED_NO_ACTIONS',
 'producerIndexSha256':'8851e255cb51ac3db02d25946854fef0c8d9e60fac5db7042e180c2b20b2af58','producerFiles':124,'preparationRows':15094,
 'runtimeIndexSha256':RUNTIME_INDEX,'reviewedPinsSha256':PINS,'rootReviewSha256':REVIEW,'inheritedBodies':64,'unchangedCurrentBodies':62,
 'newChangedHostBodies':2,'replayTemplateAndBodyReverseProofs':3,'httpReverseProofs':21,'parentRootRows':2055,'parentCapabilityRows':2054,'parentHTTPRows':7518,
 'rootMappedPaths':len(root_mapping),'capabilityMappedPaths':len(cap_mapping),'httpMappedPaths':len(hmap),'oldHTTPNativeRowsReplacedByDelegatedRuntime':skip_old_native,
 'canonicalNewTestSourceRoot':str(CANON),'configuredNativeSourceRootUnchanged':str(STAGE),'liveInputsVerifiedAtCanonicalPaths':8,
 'storedSourceChecks':49,'currentSourceChecksPredictedFromAdditionalASTRow':50,'extraASTFile':'seal-source.py','httpSourceChecks':86,'guardDataChecks':7,
 'httpComponentPinsRemainNull':True,'newOutputFamiliesAbsent':True,'ownerImportsOrMainsOrSourceTestsOrPreflightsOrBundleOrGuestOrHostExecuted':False,
 'runtimeAcceptance':False,'performanceClaim':False,'limitations':['Source/authority/hash review only; activation and all fresh regression/followon/HTTP gates remain later actions.',
 'Configured native /tmp identities are unchanged; only actual future test-source files map to canonical /private/tmp.',
 'Original historical1175-row preparation witness context is not relocated or used as a metadata adapter.',
 'HTTP requires a later actual replay index, whole actual-entry bundle, new component and distinct external TRACE phase before either host.',
 'Stored49/current50 source checks differ only by later-added seal-source.py AST enumeration; no owner source or runtime failure is inferred.',
 'No same-request reuse, GC unique-owner, reset/ALS, full Node/Streams parity or empirical cost claim.'],
 'verifiedFiles':sorted(r.files.values(),key=lambda x:x['path'])}
 with(HERE/'results.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({'state':result['state'],'paths':len(r.files),'bodyChanges':2,'runtimeAcceptance':False}))
if __name__=='__main__':main()
