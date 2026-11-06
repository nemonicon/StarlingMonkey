"""Finite Source checks only. Does not import/execute native or guest code."""
from pathlib import Path
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
NATIVE=HERE/'after/builtins/node-compat'

def row(p):
    p=Path(p);b=p.read_bytes()
    return dict(path=str(p.resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))

def read(p):return json.loads(Path(p).read_text())

old=read(HERE/'v1-reference.json')
for r in old['files']:assert row(r['path'])==r
oldroot=HERE.parent/'next-fs-candidate-v1'
assert {r['path'] for r in old['files']}=={str(p.resolve()) for p in oldroot.rglob('*') if p.is_file()}
cpp=(NATIVE/'next-fs.cpp').read_text();header=(NATIVE/'next-fs-native.h').read_text()
bindings=REPO/'host-apis/wasi-0.2.10/bindings/bindings.h';bindingtext=bindings.read_text()
calls=sorted(set(re.findall(r'\b(wasi_\w+)\s*\(',cpp)))
constants=sorted(set(re.findall(r'\bWASI_\w+',cpp)))
for token in calls+constants:assert token in bindingtext,token
assert 'entropy::deployed_execution_started()' in cpp and 'api::EngineState::Initialized' in cpp
assert 'entropy::status()' not in cpp and 'fopen(' not in cpp and 'getcwd(' not in cpp
assert 'if(!integer(cx,args[2],&end,"open"))return false;' in cpp
assert 'if(!integer(cx,args[1],&request,"read"))return false;' in cpp
assert 'const bool trailing_slash=' in cpp and "if(trailing_slash&&write>1)" in cpp
assert "len==1&&out->bytes[start]=='.'" not in cpp
assert 'bool chdir(JSContext* cx, const char* path, size_t path_length);' in header
assert cpp.index('if(!stat_path(cx,canonical.get(),count,true,&stat))return false;')<cpp.index('std::memcpy(selected_cwd,canonical.get(),count)')
assert 'JSCLASS_FOREGROUND_FINALIZE' in cpp and 'JSCLASS_HAS_RESERVED_SLOTS(1)' in cpp
assert 'JS::NewArrayBufferWithContents(cx,length,std::move(bytes))' in cpp
assert 'delete state;' in cpp and 'if(loaded)' in cpp
assert 'wasi_filesystem_types_descriptor_drop_own(value.ptr[i].f0)' in cpp
assert 'wasi_filesystem_preopens_list_tuple2_own_descriptor_string_free(&value)' in cpp
assert cpp.index('wasi_filesystem_types_descriptor_drop_own(value.ptr[i].f0)')<cpp.index('wasi_filesystem_preopens_list_tuple2_own_descriptor_string_free(&value)')
register=(NATIVE/'register.cpp').read_text();cmake=(HERE/'after/cmake/builtins.cmake').read_text()
assert 'JS::MutableHandleValue installed_module)' in register and 'installed_module.set(root)' in register
assert 'JS_GetProperty(cx,streams,"Readable",&readable)' in register
assert 'next_fs::create_kernel(cx)' in register and 'core::EventLoop::create_internal_next_tick(cx)' in register
assert register.index('install_classic_streams(engine, buffer_constructor')<register.index('install_fs(engine,buffer_constructor,streams_module)')
assert 'option(NODE_COMPAT_FS "Enable bounded node:fs/fs-promises and ReadStream" OFF)' in cmake
assert 'target_sources(builtin_node_compat PRIVATE builtins/node-compat/next-fs.cpp)' in cmake
assert "import('./generate-fs-factory.mjs')" in (NATIVE/'generate-factories.mjs').read_text()
inv=read(HERE/'node22-namespace.json');manifest=read(NATIVE/'export-manifest.fs.node-v22.14.0.json')
assert (len(inv['fsExports']),len(inv['promiseExports']),len(inv['constants']))==(106,32,57)
for key,id in [('fsExports','node:fs'),('promiseExports','node:fs/promises')]:assert sorted(inv[key]+['default'])==manifest['modules'][id]['exports']
for k,v in read(HERE/'future-authority.json').items():assert k=='schemaVersion' or v is None
host=read(HERE/'host-results.json');assert host['passed'] and len(host['cases'])==38
assert host['remainingHandles']==0 and host['counts']['opens']==host['counts']['closes']==13
assert host['nativeProviderExecuted'] is host['guestExecuted'] is False
terminal=read(HERE/'host-tests.terminal.json');assert terminal['rawExitCode']==0 and terminal['timeout'] is False
assert (HERE/'host-tests.stderr.log').read_bytes()==b''
assert json.loads((HERE/'host-tests.stdout.log').read_text())==host
base=read(oldroot/'references.json')['before'];deriv=[]
for relative in ['include/node-compat-entropy.h','builtins/node-compat/entropy-policy.cpp','builtins/node-compat/register.cpp','cmake/builtins.cmake']:
    assert row(base[relative]['path'])==base[relative]
    deriv.append(dict(path=relative,before=base[relative],after=row(HERE/'after'/relative)))
deriv.append(dict(path='builtins/node-compat/generate-factories.mjs',before=row(REPO/'builtins/node-compat/generate-factories.mjs'),after=row(NATIVE/'generate-factories.mjs')))
(HERE/'derivations.json').write_text(json.dumps(dict(schemaVersion=1,existingAfterimages=deriv,newPaths=[str(p.relative_to(HERE/'after')) for p in (HERE/'after').rglob('*') if p.is_file() and not (REPO/p.relative_to(HERE/'after')).exists()],contextCopies=['builtins/node-compat/manifest.schema.json','builtins/node-compat/validate-manifest.mjs'],notNativeSourceManifest=True),indent=2)+'\n')
inputs=[row(bindings),row(REPO/'host-apis/wasi-0.2.10/bindings/bindings.c'),row(REPO/'runtime/event_loop.h'),row(REPO/'runtime/event_loop.cpp'),row(REPO/'builtins/node-compat/classic-streams/classic-streams.mjs'),row(REPO/'builtins/node-compat/classic-streams/classic-core.generated.mjs'),row(REPO/'builtins/node-compat/buffer-facade.mjs')]
node=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node');assert row(node)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
source=read(oldroot/'references.json')['nextSources']['dist/server/lib/node-fs-methods.js'];assert row(source['path'])==source
result=dict(schemaVersion=1,state='NEXT_FS_SOURCE_CHECKS_PASSED_V2',sourceOnly=True,nativeCompiled=False,guestExecuted=False,wasiFunctionSpellings=calls,wasiConstantSpellings=constants,primaryInputs=inputs,pinnedNode=row(node),actualNextHelper=source,hostCases=38,hostResult=row(HERE/'host-results.json'),nativeValidation='Source spellings/order/ownership checked only; no SDK frontend or native execution.',allV1FilesPreserved=True)
(HERE/'source-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passed=True,wasiCalls=len(calls),wasiConstants=len(constants),hostCases=38,newPaths=len(read(HERE/'derivations.json')['newPaths']))))
