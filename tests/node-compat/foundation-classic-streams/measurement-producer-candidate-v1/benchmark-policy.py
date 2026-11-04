"""Build-time diagnostic capture/decorate helper. main is not a source test."""
import sys
sys.dont_write_bytecode=True
import json,subprocess,shlex,os
from pathlib import Path
from benchmark_common import (HERE,REPO,CONTRACT,RECIPE,capture_addons,capture_regular,digest,sha,cache_values,validate_observations,required_cache,validate_link,validate_external_sources,adapter)

def write(path,data):
    with Path(path).open('xb')as stream:stream.write(data)

def collect(build):
    build=Path(build);cache_raw,_=capture_regular(build/'CMakeCache.txt');cache=cache_values(cache_raw)
    install=Path(cache['INSTALL_BUILTINS'])
    results={'CMakeCache.txt':cache_raw,'compile_commands.json':capture_regular(build/'compile_commands.json')[0],
      'builtins.incl':capture_regular(install)[0]}
    commands={'parent-targets.commands.txt':['ninja','-C',str(build),'-t','commands','builtin_componentize_embedding',CONTRACT['target']],
      'final-link.commands.txt':['ninja','-C',str(build),'-t','commands','starling-raw.wasm/starling-raw.wasm']}
    for name,command in commands.items():
        result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        results[name]=result.stdout
        results[name+'.stderr']=result.stderr
    final=validate_link(results['final-link.commands.txt'])
    compiler_lines=[line for line in results['parent-targets.commands.txt'].decode().splitlines()if' -c 'in line]
    paths={Path(shlex.split(line)[0])for line in compiler_lines}
    paths.update(Path(command[0])for command in (final['linkCommand'],final['postLinkWasmOptCommand']))
    paths.update(Path(value)for key,value in cache.items()if key in ('CMAKE_LINKER','CMAKE_CXX_COMPILER_AR','CMAKE_CXX_COMPILER_RANLIB'))
    tools=[]
    for path in sorted(paths):
        assert path.is_absolute();target=path.resolve(strict=True);assert target.is_file()and not target.is_symlink()
        tools.append({'path':str(path),'symlink':path.is_symlink(),'linkText':os.readlink(path)if path.is_symlink()else None,
          'resolvedPath':str(target),'sha256':sha(target),'bytes':target.stat().st_size,
          'frozenCopyRequired':target.stat().st_size<1048576})
    results['tool-witnesses.json']=(json.dumps(tools,indent=2)+'\n').encode()
    return results,commands

def before(build,artifact,addon_manifest):
    adapter()
    assert json.loads(Path(addon_manifest).read_bytes())==capture_addons()
    root=Path(str(artifact)+'.benchmark-before');assert not root.exists()and not root.is_symlink();root.mkdir()
    results,commands=collect(build)
    for name,data in results.items():write(root/name,data)
    document={'schemaVersion':1,'recipeSha256':sha(HERE/'build-classic-benchmark-engine.sh'),'addonSources':capture_addons(),
      'files':[{'name':name,'path':str(root/name),'sha256':digest(data),'bytes':len(data)}for name,data in results.items()],
      'collectionCommands':commands,'buildDirectory':str(build),'addonManifestPath':str(addon_manifest)}
    assert document['recipeSha256']==RECIPE
    write(root/'capture.json',(json.dumps(document,indent=2)+'\n').encode())

def decorate(metadata,artifact):
    root=Path(str(artifact)+'.benchmark-before');raw,pre_sha=capture_regular(root/'capture.json');previous=json.loads(raw)
    assert previous['recipeSha256']==RECIPE==sha(HERE/'build-classic-benchmark-engine.sh')
    assert previous['addonSources']==capture_addons()==json.loads(Path(previous['addonManifestPath']).read_bytes())
    results,commands=collect(previous['buildDirectory']);assert commands==previous['collectionCommands']
    post=Path(str(artifact)+'.benchmark-after');assert not post.exists()and not post.is_symlink();post.mkdir()
    after=[]
    for row in previous['files']:
        data=results[row['name']];assert capture_regular(row['path'])[0]==data
        assert digest(data)==row['sha256']and len(data)==row['bytes']
        write(post/row['name'],data);after.append({'name':row['name'],'path':str(post/row['name']),'sha256':digest(data),'bytes':len(data)})
    cache=cache_values(results['CMakeCache.txt']);classic=metadata['classicStreamsEnabled']
    validate_external_sources(metadata['componentizeSourceManifest'],Path(cache['CMAKE_HOME_DIRECTORY']))
    for key,value in required_cache(classic).items():assert cache.get(key)==value,key
    for key in ('CMAKE_EXE_LINKER_FLAGS','CMAKE_PROJECT_ComponentizeJS_INCLUDE','ENABLE_BUILTIN_DIAGNOSTICS_CLASSIC_BENCHMARK'):
        metadata['requestedCMakeOptions'][key]=required_cache(classic)[key];metadata['observedCMakeOptions'][key]=cache[key]
    metadata['diagnosticOnly']=True
    metadata['classicBenchmarkDiagnosticPolicy']={'version':CONTRACT['diagnosticVersion'],'moduleId':CONTRACT['moduleId'],'exports':CONTRACT['exports'],
      'namespace':CONTRACT['namespace'],'addonSources':capture_addons(),'nativeInputs':342,'addonInputs':2,'totalDeclaredNativeAndBuildInputs':344,
      'externalEmbeddingInputs':3,'noPublicProcess':True,'linkerFlags':'','noGuestExecutionByProducer':True,
      'evidence':{'version':'benchmark-before-after-command-config-v1','beforeCapturePath':str(root/'capture.json'),'beforeCaptureSha256':pre_sha,
        'before':previous['files'],'after':after,'collectionCommands':commands,'buildDirectory':previous['buildDirectory'],'exactBytesUnchanged':True},
      'scope':'Test-only nextTick binding; not a production selector input, runtime acceptance or measurement.'}
    observations=validate_observations(metadata,'benchmark-classic-on'if classic else'benchmark-classic-off',cache,
      json.loads(results['compile_commands.json']),results['parent-targets.commands.txt'],results['builtins.incl'],results['final-link.commands.txt'])
    metadata['classicBenchmarkDiagnosticPolicy']['actualDiagnosticCompileCommands']=observations['diagnostic']
    metadata['classicBenchmarkDiagnosticPolicy']['actualEmbeddingCompileCommands']=observations['embedding']
    return metadata

if __name__=='__main__':
    if sys.argv[1]=='capture':assert len(sys.argv)==3;write(sys.argv[2],(json.dumps(capture_addons(),indent=2)+'\n').encode())
    elif sys.argv[1]=='before':assert len(sys.argv)==5;before(*sys.argv[2:])
    elif sys.argv[1]=='external':assert len(sys.argv)==3;validate_external_sources(CONTRACT['externalSources'],Path(sys.argv[2]))
    else:raise AssertionError('Unknown build-policy action')
