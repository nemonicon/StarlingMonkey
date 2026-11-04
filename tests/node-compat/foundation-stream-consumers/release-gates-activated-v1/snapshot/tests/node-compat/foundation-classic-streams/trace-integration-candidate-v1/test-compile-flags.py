"""Pure synthetic command-data checks. No compiler or build receipt is produced."""
from pathlib import Path
import copy
import importlib.util
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
    layer=load(HERE/'layer-policy.py','trace_flag_source_layer')
    common=load(HERE/'artifact-tools/artifact_common.py','trace_flag_source_common')
    cpp=[row['path']for row in layer.POLICY['expectedNativeSourceManifest']if row['path'].endswith('.cpp')and row['path'].startswith(('builtins/','runtime/'))]
    root=Path('/synthetic/NOT-A-BUILD/source');checks=[];baseline=None
    for label in common.LABELS:
        meta={'internalTicksEnabled':True,'classicStreamsEnabled':label!='disabled-off','streamWebEnabled':True,'eventsEnabled':True,'stringDecoderEnabled':True,'gcStress':label=='gc-off','entropyPolicy':'runtime-only'if label=='normal-runtime'else'off'}
        def command(path):
            flags=['-O3','-DNDEBUG','-DNODE_COMPAT_INTERNAL_TICKS=1','-DNODE_COMPAT_STRICT_INITIALIZATION=1','-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1','-DNODE_COMPAT_ENTROPY_POLICY=1']
            if path.startswith('builtins/node-compat/'):flags.append('-DNODE_COMPAT_STREAM_WEB=1')
            if path in layer.POLICY['privateTargetCpp']:
                if meta['classicStreamsEnabled']:flags.append('-DNODE_COMPAT_CLASSIC_STREAMS=1')
                if meta['gcStress']:flags.append('-DNODE_COMPAT_GC_STRESS=1')
            if meta['entropyPolicy']=='runtime-only':flags.append('-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1')
            return '/synthetic/NOT-A-COMPILER/clang++ '+' '.join(flags)+' -c '+str(root/path)+' -o /synthetic/NOT-AN-OBJECT.o'
        entries=[{'file':str(root/path),'command':command(path)}for path in cpp];embedding=[command('embedding/embedding.cpp')]
        native,queue,private=layer.validate_classic_compilation(entries,embedding,root,meta)
        assert len(native)==61 and len(queue)==1 and len(private)==5
        for row in entries:common.compile_command(row['command'],meta['entropyPolicy']=='runtime-only',str(Path(row['file']).relative_to(root)),meta['classicStreamsEnabled'],meta['gcStress'])
        common.compile_command(embedding[0],meta['entropyPolicy']=='runtime-only','embedding/embedding.cpp',meta['classicStreamsEnabled'],meta['gcStress'])
        checks.append('synthetic61-native+1-embedding data model '+label)
        if label=='normal-off':baseline=(entries,embedding,meta)
    flags=['-O0','-O3','-Og','-Ofast','-DNDEBUG=0','-UNDEBUG','-DDEBUG','-UDEBUG','-DNODE_COMPAT_OOM_TESTING=1','-UNODE_COMPAT_OOM_TESTING','-DNODE_COMPAT_INTERNAL_TICKS=0','-UNODE_COMPAT_STRICT_INITIALIZATION','-D']
    for flag in flags:
        for target in ['native','embedding']:
            entries,embedding,meta=copy.deepcopy(baseline)
            if target=='native':entries[0]['command']+=' '+flag
            else:embedding[0]+=' '+flag
            try:layer.validate_classic_compilation(entries,embedding,root,meta)
            except AssertionError:checks.append('reject '+target+' '+flag)
            else:raise AssertionError('Accepted '+target+' '+flag)
        for name,validator in [('layer',layer._release),('freezer',common.exact_release)]:
            if flag in ['-DNODE_COMPAT_INTERNAL_TICKS=0','-UNODE_COMPAT_STRICT_INITIALIZATION','-D']:continue
            try:validator(['-O3','-DNDEBUG',flag])
            except AssertionError:checks.append('exact '+name+' rejects '+flag)
            else:raise AssertionError('Accepted release flag '+flag)
    result={'schemaVersion':1,'state':'TRACE_SYNTHETIC_COMPILE_COMMAND_DATA_TESTS_PASSED','passed':len(checks),'checks':checks,
      'nativeCommandsPerModel':61,'embeddingCommandsPerModel':1,'modelsAreSynthetic':True,'compilerInvoked':False,'engineIdentifiersOrBuildReceiptsCreated':False}
    (HERE/'evidence/compile-flag-tests.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'state':result['state'],'passed':len(checks)}))
if __name__=='__main__':main()
