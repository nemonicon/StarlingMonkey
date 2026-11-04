"""Synthetic source-parser fixture only. No production receipt or engine data."""
import importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('source_generation',HERE/'prepare.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
edits=[('classic=true,ticks=true','zlib=true,classic=true,ticks=true'),('[classic,ticks,web,events,stringDecoder,gc]','[zlib,classic,ticks,web,events,stringDecoder,gc]'),
 ('length,342','length,350'),('length,36','length,44'),('policy.privateTargetCpp.length,5','policy.privateTargetCpp.length,6'),('allCpp.length,61','allCpp.length,62'),
 ("&&(web||path!=='builtins/node-compat/stream-web-kernel.cpp')","&&(web||path!=='builtins/node-compat/stream-web-kernel.cpp')&&(zlib||path!=='builtins/node-compat/zlib/kernel.cpp')"),
 ("if(classic&&policy.privateTargetCpp.includes(path))", "if(zlib&&path.startsWith('builtins/node-compat/'))flags.push('-DNODE_COMPAT_ZLIB=1');\n    if(classic&&policy.privateTargetCpp.includes(path))"),
 ('privateCommands.length,web?5:4','privateCommands.length,(web?5:4)+Number(zlib)'),
 ("NODE_COMPAT_CLASSIC_STREAMS:on(classic),","NODE_COMPAT_CLASSIC_STREAMS:on(classic),NODE_COMPAT_ZLIB:on(zlib),"),
 ('addedSourcePaths:copy(policy.addedSourcePaths)','addedSourcePaths:copy(policy.classicAddedSourcePaths)'),
 ('classicStreamsEnabled:classic,internalTicksEnabled:ticks','zlibEnabled:zlib,classicStreamsEnabled:classic,internalTicksEnabled:ticks'),
 ("import assert from 'node:assert/strict';","import assert from 'node:assert/strict';\nimport {CODEC_HEADERS} from './compile-input.mjs';"),
 ('  function command(path){', '''  const distribution='/synthetic/NO-BUILD/distribution';
  const selected={version:'sm-selected-moz-z-compile-input-v1',selectedDistribution:distribution,
    archive:{path:distribution+'/libspidermonkey.a',sha256:'298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc',bytes:538170426},
    headers:CODEC_HEADERS.map(([name,sha256,bytes])=>({path:distribution+'/include/'+name,sha256,bytes}))};selected.requiredForcedInclude=copy(selected.headers[3]);
  function command(path){'''),
 ("const flags=['-O3'","const flags=['-include',selected.requiredForcedInclude.path,'-O3'"),
 ('  // No validator import/call here:', '''  metadata.zlibSelectedCodecInput=copy(selected);
  metadata.zlibSourcePolicy=copy(policy.zlibSourcePolicy);
  metadata.zlibPolicy={version:'sm-bounded-zlib-install-v1',enabled:zlib,policyFileSha256:pins.policySha256,helperSha256:pins.helperSha256,
    moduleManifest:policy.zlibManifest,moduleManifestSha256:policy.zlibManifestSha256,requiredHostInterfaces:[],
    actualKernelCompileCommands:zlib?[layout.get('builtins/node-compat/zlib/kernel.cpp')]:[],runtimeBackendProof:{verified:false,version:null,vernum:null}};
  // No validator import/call here:''')]
g.transform(g.PARENT/'source-model-fixture.mjs','source-model-fixture.mjs',edits)
g.dump('model-transformations.json',{'records':g.records,'syntheticOnly':True,'engineIdentifiersPresent':False})
