"""Pure text/AST/derivation tests. No owner helper import, factory, native or guest."""
from pathlib import Path
import ast,difflib,hashlib,json,re
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
BASE=Path('/tmp/starling-node-compat/zlib-source-v4')
checks=[]
def check(name,condition):
    assert condition,name
    checks.append(name)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(name):return(HERE/name).read_text()
def main():
    policy=json.loads(read('policy.json'));native=json.loads(read('native-derivations.json'))
    parent=json.loads((REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4/policy.json').read_bytes())
    before={r['path']:r['sha256']for r in parent['expectedNativeSourceManifest']}
    after={r['path']:r['sha256']for r in policy['expectedNativeSourceManifest']}
    check('exact350to355',len(before)==350 and len(after)==355 and len(set(after)-set(before))==5)
    check('348unchanged2replacements',sum(after[p]==before[p]for p in before)==348 and len(native['changes'])==2)
    check('noNewCpp',not any(p.endswith('.cpp')for p in set(after)-set(before)))
    for path,digest in after.items():
        source=HERE/'proposed'/path if(HERE/'proposed'/path).exists()else BASE/path
        assert sha(source.read_bytes())==digest,path
    check('all355ActualSourceBytes',True)
    for row in native['changes']:
        old=(BASE/row['path']).read_text();value=old
        for edit in row['edits']:
            if edit.get('kind')=='append':value+=edit['new']
            else:
                assert value.count(edit['old'])==edit['count'];value=value.replace(edit['old'],edit['new'])
        assert value==read('proposed/'+row['path'])
        for edit in reversed(row['edits']):
            if edit.get('kind')=='append':assert value.endswith(edit['new']);value=value[:-len(edit['new'])]
            else:assert value.count(edit['new'])==edit['count'];value=value.replace(edit['new'],edit['old'])
        check('nativeReverse:'+row['path'],value==old)
    patch=''
    for path in native['addedSources']+[r['path']for r in native['changes']]:
        old=(BASE/path).read_text()if path in before else'';new=read('proposed/'+path)
        patch+=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+path if path in before else'/dev/null',tofile='b/'+path))
    check('nativePatchExact',patch==read('native.UNAPPLIED.patch'))
    for row in json.loads(read('host-derivations.json'))['changes']:
        old=Path(row['source']).read_text();value=old
        for edit in row['edits']:
            assert value.count(edit['old'])==edit['count'];value=value.replace(edit['old'],edit['new'])
        assert value==read(row['target'])and sha(value.encode())==row['afterSha256']
        for edit in reversed(row['edits']):
            assert value.count(edit['new'])==edit['count'];value=value.replace(edit['new'],edit['old'])
        check('hostReverse:'+row['target'],value==old)
    facade=read('proposed/builtins/node-compat/stream-consumers/facade.mjs')
    original=(REPO/'tests/node-compat/foundation-stream-consumers/metadata-v2/create-module.mjs').read_text()
    original=original.replace('// ISOLATED SOURCE CANDIDATE ONLY. Native guest/registration gates have not run.','// UNAPPLIED optional production text/JSON source. Fresh355 native/registration/guest gates pending.').replace("'stream-consumers-prototype-v1'","'sm-node-22.14.0-m0.14'").replace('createConsumersModule(web = globalThis)','createConsumersModule(web)')
    check('metadataV2AlgorithmExactExceptDeclaredCaptureVersionComment',facade==original)
    check('noGlobalFallbackOrBlobInvocation','globalThis'not in facade and 'new Blob'not in facade and '.getReader('not in facade)
    check('capturedNativeDecoder','const Decoder = web.TextDecoder, Decode = Decoder.prototype.decode;'in facade)
    check('mutableDefaultFiniteRecord','const defaultObject = { arrayBuffer, blob, buffer, text, json };'in facade and 'Freeze(defaultObject)'not in facade)
    check('threeCallAndConstructRefusals',all('function '+name+'(stream) { deferred(\''+name+'\'); }'in facade for name in['arrayBuffer','blob','buffer']))
    check('finiteCaps',all('export const '+key+' = '+str(value)+';'in facade for key,value in{'MAX_BYTE_INPUT':1048576,'MAX_STRING_INPUT_CODE_UNITS':1048576,'MAX_OUTPUT_CODE_UNITS':1048576,'MAX_CHUNKS':4096}.items()))
    register=read('proposed/builtins/node-compat/register.cpp')
    check('rootedArgumentImmediateAllocationCheck','JS::RootedObject argument(cx, JS_NewPlainObject(cx));\n  if (!argument) return false;'in register)
    check('sameModuleCanonicalAlias','define_builtin_module("node:stream/consumers", module) &&'in register and 'define_builtin_module("stream/consumers", module)'in register)
    cmake=read('proposed/cmake/builtins.cmake')
    check('defaultOffIndependentFlag','option(NODE_COMPAT_STREAM_CONSUMERS "Enable bounded node:stream/consumers text/json" OFF)'in cmake)
    consumers=cmake[cmake.index('# Independent optional consumers:'):]
    check('onlyNodeAndTextCodecPrereqs','NODE_COMPAT_CLASSIC_STREAMS'not in consumers and 'NODE_COMPAT_INTERNAL_TICKS'not in consumers and 'NODE_COMPAT_STREAM_WEB'not in consumers)
    check('declarationOrderDecoderBeforeNode',cmake.index('builtins::web::text-codec')<cmake.index('builtins::node_compat'))
    add_builtin=(BASE/'cmake/add_builtin.cmake').read_text();install=(BASE/'builtins/install_builtins.cpp').read_text()
    check('actualNSAppendMechanism','string(REPLACE "-" "_" NS ${NS})'in add_builtin and 'file(APPEND $CACHE{INSTALL_BUILTINS} "NS_DEF(${NS})\\n")'in add_builtin)
    check('actualSequentialInstallAbort','#include "builtins.incl"'in install and 'if (!ns::install(engine))'in install and 'return false;'in install)
    helper=read('layer-policy.py');tree=ast.parse(helper)
    allowed={'_macro','_release'};module=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in allowed],type_ignores=[]);scope={};exec(compile(module,'<pure-extracted-macro-model>','exec'),scope)
    for enabled in[False,True]:scope['_macro'](['-DNODE_COMPAT_STREAM_CONSUMERS=1']if enabled else[],'NODE_COMPAT_STREAM_CONSUMERS',enabled)
    check('syntheticMacroOnOff',True)
    for words,enabled in[(['-D','NODE_COMPAT_STREAM_CONSUMERS=1'],True),(['-DNODE_COMPAT_STREAM_CONSUMERS=1','-U','NODE_COMPAT_STREAM_CONSUMERS'],True),(['-DNODE_COMPAT_STREAM_CONSUMERS=0'],False),(['-DNODE_COMPAT_STREAM_CONSUMERS=1']*2,True),(['-UNODE_COMPAT_STREAM_CONSUMERS'],False)]:
        try:scope['_macro'](words,'NODE_COMPAT_STREAM_CONSUMERS',enabled)
        except AssertionError:pass
        else:raise AssertionError('Synthetic malformed macro accepted')
    check('syntheticMalformedMacroRefusal5',True)
    for web in[False,True]:
        for zlib in[False,True]:
            active=[p for p in policy['privateTargetCpp']if(web or p!='builtins/node-compat/stream-web-kernel.cpp')and(zlib or p!='builtins/node-compat/zlib/kernel.cpp')]
            assert len(active)==(5 if web else 4)+int(zlib)
    check('syntheticPrivate6or5SubtractWebKernel',True)
    check('macroAbsentOtherNativeAndEmbedding',"metadata['streamConsumersEnabled']and name in POLICY['privateTargetCpp']"in helper and "_macro(words,'NODE_COMPAT_STREAM_CONSUMERS',False)"in helper)
    recipe=read('proposed/tests/node-compat/build-engine.sh')
    inline=list(re.finditer(r"<<'([A-Z][A-Z0-9_]*)'\n(.*?)\n\1(?:\n|$)",recipe,re.S))
    assert inline
    for match in inline:ast.parse(match.group(2))
    check('embeddedPythonAST:'+str(len(inline)),True)
    for path in sorted(HERE.glob('*.py')):ast.parse(path.read_bytes())
    check('ownedPythonAST',True)
    pins=json.loads(read('admission-pins.json'))
    check('actualFuturePinsNull',pins['reviewedFutureEnginePins']is None)
    check('explicitActualInstallOrderCapture',all(x in helper for x in["values['INSTALL_BUILTINS']","install_text.index(decoder_ns)<install_text.index(node_ns)","'aliasRegistrationTransactional':False"]))
    successor=json.loads(read('successor-derivations.json'));old=HERE.with_name('production-text-json-candidate-v1')
    original=(old/'proposed/tests/node-compat/build-engine.sh').read_text();value=original
    for edit in successor['recipe']['edits']:
        assert value.count(edit['old'])==edit['count'];value=value.replace(edit['old'],edit['new'])
    assert value==recipe
    for edit in reversed(successor['recipe']['edits']):
        assert value.count(edit['new'])==edit['count'];value=value.replace(edit['new'],edit['old'])
    check('v1ToV2RecipeExactThreeEditsReverse',value==original and [e['count']for e in successor['recipe']['edits']]==[3,3,2])
    print(json.dumps({'schemaVersion':1,'state':'PURE_SOURCE_CONTRACT_CHECKS_PASSED','checks':checks,'passed':len(checks),'syntheticMetadataOnly':True,'factoryNativeGuestOrHostExecuted':False}))
if __name__=='__main__':main()
