"""Synthetic command/parser tests, source hashing, and filename arithmetic only."""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json
import re
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def main():
    parser=argparse.ArgumentParser();parser.add_argument('source_root');parser.add_argument('output');args=parser.parse_args()
    root=Path(args.source_root).resolve();spec=importlib.util.spec_from_file_location('classic342',HERE/'layer-policy.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    checks=[]
    def positive(name,action):action();checks.append({'name':name,'passed':True})
    def negative(name,action):
        try:action()
        except (AssertionError,FileNotFoundError):checks.append({'name':name,'passed':True,'expectedRejection':True})
        else:raise AssertionError('Expected rejection: '+name)
    positive('actual staged342 source bytes',lambda:module.validate_sources(root))
    names=[row['path']for row in module.POLICY['expectedNativeSourceManifest']if row['path'].endswith('.cpp')and row['path'].startswith(('runtime/','builtins/'))]
    def model(classic=True,ticks=True,web=True,events=True,entropy='off',gc=False):
        meta={'syntheticMetadataOnly':True,'classicStreamsEnabled':classic,'internalTicksEnabled':ticks,'streamWebEnabled':web,'eventsEnabled':events,'stringDecoderEnabled':True,'entropyPolicy':entropy,'gcStress':gc}
        def command(name):
            flags=['-O3','-DNDEBUG','-DNODE_COMPAT_STRICT_INITIALIZATION=1','-DNODE_COMPAT_ENTROPY_POLICY=1']
            for key,on in [('NODE_COMPAT_INTERNAL_TICKS',ticks),('NODE_COMPAT_CLASSIC_STREAMS',classic and name in module.POLICY['privateTargetCpp']),('NODE_COMPAT_STREAM_WEB',web and name.startswith('builtins/node-compat/')),('NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER',events),('NODE_COMPAT_ENTROPY_RUNTIME_ONLY',entropy=='runtime-only'),('NODE_COMPAT_GC_STRESS',gc and name in module.POLICY['privateTargetCpp'])]:
                if on:flags.append('-D'+key+'=1')
            return '/synthetic/NOT-A-COMPILER/clang++ '+' '.join(flags)+' -c '+str(root/name)+' -o /synthetic/NO-OBJECT.o'
        active=[name for name in names if(ticks or name!='runtime/node_tick_queue.cpp')and(web or name!='builtins/node-compat/stream-web-kernel.cpp')]
        return[{'file':str(root/name),'command':command(name)}for name in active],[command('embedding/embedding.cpp')],meta
    def validate(value):return module.validate_classic_compilation(value[0],value[1],root,value[2])
    for options in[{},dict(classic=False),dict(classic=False,web=False),dict(web=False),dict(classic=False,ticks=False,web=False),dict(entropy='runtime-only'),dict(gc=True)]:
        value=model(**options);positive('synthetic compile model '+json.dumps(options,sort_keys=True),lambda value=value:validate(value))
    for extra in[' -D NODE_COMPAT_CLASSIC_STREAMS=1',' -U NODE_COMPAT_CLASSIC_STREAMS',' -UNODE_COMPAT_CLASSIC_STREAMS',' -DNODE_COMPAT_CLASSIC_STREAMS=0',' -DNODE_COMPAT_CLASSIC_STREAMS=1',' -DDEBUG=1',' -UNDEBUG']:
        value=model();row=next(row for row in value[0]if row['file'].endswith('/register.cpp'));row['command']+=extra;negative('native malformed flags '+extra,lambda value=value:validate(value))
    for token in[' -O3',' -DNDEBUG']:
        value=model();value[0][0]['command']=value[0][0]['command'].replace(token,'');negative('Release token required '+token,lambda value=value:validate(value))
    for extra in[' -DNODE_COMPAT_CLASSIC_STREAMS=1',' -U NODE_COMPAT_INTERNAL_TICKS',' -DDEBUG=1']:
        value=model();value[1][0]+=extra;negative('embedding malformed flags '+extra,lambda value=value:validate(value))
    for name in['runtime/node_tick_queue.cpp','builtins/node-compat/stream-web-kernel.cpp']:
        value=model();value[0][:]=[row for row in value[0]if not row['file'].endswith('/'+name)];negative('missing active TU '+name,lambda value=value:validate(value))
        value=model(classic=False,ticks=False,web=False);value[0].append(next(row for row in model()[0]if row['file'].endswith('/'+name)));negative('extra inactive TU '+name,lambda value=value:validate(value))
    value=model();value[0].append(copy.deepcopy(value[0][0]));negative('duplicate native TU',lambda:validate(value))
    value=model();value[0].append({'file':str(root/'runtime/unreviewed.cpp'),'command':value[0][0]['command']});negative('unknown native TU',lambda:validate(value))
    negative('unsupported runtimeGC',lambda:validate(model(entropy='runtime-only',gc=True)))
    for options in[dict(ticks=False),dict(events=False)]:negative('classic prerequisites '+str(options),lambda options=options:validate(model(**options)))
    manifest=copy.deepcopy(module.POLICY['expectedNativeSourceManifest']);manifest[0]['sha256']='0'*64;negative('manifest before-image mismatch',lambda:module.validate_sources(root,manifest))
    recipe=(HERE/'source/tests/node-compat/build-engine.sh').read_text();assert recipe.index('RuntimeOnly+GC is not a selected classic producer variant')<recipe.index('mkdir -p "$work_root/cache"')
    assert 'artifact_name="$artifact_name.classic-v1.$entropy_mode.p$path_enabled.e$events_enabled.d$string_decoder_enabled.a$assert_enabled.q$querystring_enabled.u$util_enabled.w$stream_web_enabled.t$ticks_enabled.c$classic_enabled"'in recipe
    filenames=[]
    for label,mode,gc,classic in[('normal-off','OFF',False,1),('normal-runtime','RUNTIME_ONLY',False,1),('gc-off','OFF',True,1),('disabled-off','OFF',False,0)]:
        name='starlingmonkey_embedding.abi-i32-i64-v1'+('.gc-stress'if gc else'')+'.classic-v1.'+mode+'.p1.e1.d1.a1.q1.u1.w1.t1.c'+str(classic)+'.p342v1'
        entries=[name+'.wasm',name+'.wasm.build.json','componentize-native-inputs-'+name+'.json','source-inputs-'+name+'.json','openssl-source-'+name+'.before.json','configure-'+name+'.log','build-'+name+'.log','recipe-'+name+'.sha256']
        suffix='entropy-entry-v1-strict-callback-v3-protected-abort-v2.'+mode+'.path-1.events-1.string-decoder-1.assert-1.querystring-1.util-1.stream-web-1.private-ticks-v1-1.classic-v1-'+str(classic)
        source_dir='componentize-abi-fixed-bigint-v1-'+suffix;build_dir='engine-abi-fixed-bigint-v1-'+suffix
        assert all(len(value.encode())<=255 for value in entries+[source_dir,build_dir]);filenames.append({'variant':label,'artifactTag':'p342v1','engineBasenameBytes':len(entries[0]),'sidecarBasenameBytes':len(entries[1]),'longestGeneratedBasenameBytes':max(map(len,entries)),'sourceDirectoryBasenameBytes':len(source_dir),'buildDirectoryBasenameBytes':len(build_dir)})
    checks.append({'name':'all four actual variants engine/sidecar/input/log basenames fit NAME_MAX; RuntimeGC refused before mkdir','passed':True})
    result={'schemaVersion':1,'state':'CLASSIC_PYTHON_SOURCE_AND_SYNTHETIC_COMMAND_TESTS_PASSED','checks':len(checks),'passed':len(checks),'failures':0,'syntheticMetadataOnly':True,'compilerInvoked':False,'componentizerInvoked':False,'guestInvoked':False,'variantFilenames':filenames,'observations':checks}
    with Path(args.output).open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'checks':len(checks),'output':args.output,'variantFilenames':filenames}))
if __name__=='__main__':main()
