"""Seal consumed source/corpus identities; no runner, compiler or guest executes."""
from pathlib import Path
import hashlib
import json
import os
import re
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
SCHEDULER=REPO/'tests/node-compat/foundation-scheduler'
CLASSIC=HERE.parent/'integration-candidate-v1'
PARENTS={'common':SCHEDULER/'production-regression-candidate-v5','off':SCHEDULER/'production-followon-off-v3',
 'release':SCHEDULER/'production-release-runner-v3','capability':SCHEDULER/'production-followon-capability-v3'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    assert not(HERE/'input-freeze.json').exists()and not(HERE/'native-preflight.mjs').exists()
    policy=json.loads((CLASSIC/'policy.json').read_bytes());contract=json.loads((CLASSIC/'admission-pins.json').read_bytes())
    native={row['path']:row['sha256']for row in policy['expectedNativeSourceManifest']}
    changed={**native,'tests/node-compat/build-engine.sh':contract['productionRecipeSha256'],
      'tests/node-compat/module-selection.mjs':sha(CLASSIC/'source/tests/node-compat/module-selection.mjs'),
      'tests/node-compat/classic-streams-admission.mjs':sha(CLASSIC/'source/tests/node-compat/classic-streams-admission.mjs')}
    paths={};lineage=[];skipped=[]
    def add(path,role):
        path=Path(path).resolve();assert path.is_file()and not path.is_symlink(),path
        rel=os.path.relpath(path,HERE);data=path.read_bytes();row={'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
        if rel in paths:assert paths[rel]==row
        paths[rel]=row;return row
    for label,parent in PARENTS.items():
        index_path=parent/'index.json';index=json.loads(index_path.read_bytes());manifest=parent/'input-freeze.json'
        pin=next(row for row in index['files']if row['path']=='input-freeze.json');assert sha(manifest)==pin['sha256']
        add(index_path,'immutable-parent-source-index');add(manifest,'immutable-parent-source-manifest')
        lineage.append({'label':label,'indexPath':str(index_path.relative_to(REPO)),'indexSha256':sha(index_path),'manifestSha256':sha(manifest)})
        for row in json.loads(manifest.read_bytes())['inputs']:
            original=(parent/row['path']).resolve();mapped=None
            for name,root in PARENTS.items():
                if original.is_relative_to(root):mapped=HERE/name/original.relative_to(root);break
            if mapped is not None:
                if mapped.is_file():add(mapped,'derived-runtime-source')
                else:skipped.append({'path':str(original),'sha256':row['sha256'],'reason':'Old packet pin/guard/index/history is not imported by the derived runtime; new fixed342 pin/seal is separate.'})
                continue
            if original.is_relative_to(REPO)and str(original.relative_to(REPO))in changed:
                expected=changed[str(original.relative_to(REPO))];assert sha(original)==expected;add(original,'actual-installed-classic342-source')
                continue
            assert sha(original)==row['sha256']and original.stat().st_size==row['bytes'],original
            add(original,'unchanged-shared-source-or-explicit-historical-control')
    for row in policy['expectedNativeSourceManifest']:
        path=REPO/row['path'];assert sha(path)==row['sha256'];add(path,'actual-installed-native342')
    for name in ['admission-pins.json','policy.json','layer-policy.py','index.json','runtime-preflight.template.mjs']:
        add(CLASSIC/name,'immutable-classic-integration-contract')
    for path in sorted(HERE.rglob('*')):
        if not path.is_file()or'history'in path.relative_to(HERE).parts:continue
        if path.name in['index.json','source-receipt.json','input-freeze.json','native-preflight.mjs','syntax-results.json','host-test-results.json','path-check-results.json']:continue
        add(path,'new-source-replay-payload')
    # The eight live computed inputs must be these physical repository files;
    # an old frozen control or metadata hash cannot substitute for them.
    computed=['host-apis/wasi-0.2.10/wit/deps/'+name+'/package.wit'for name in['wasi-cli-0.2.10','wasi-clocks-0.2.10','wasi-filesystem-0.2.10','wasi-http-0.2.10','wasi-io-0.2.10','wasi-random-0.2.10','wasi-sockets-0.2.10']]
    computed+=['host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm']
    for name in computed:add(REPO/name,'exact-LIVE-computed-HTTP-input')
    for name in ['tests/node-compat/module-selection.mjs','tests/node-compat/classic-streams-admission.mjs']:
        assert sha(REPO/name)==changed[name];add(REPO/name,'actual-installed-finite342-admission')
    # Capability's local closure is emitted first. The hard-coded root seal then
    # binds that entire manifest before it can be parsed by the HTTP builder.
    base={'schemaVersion':1,'state':'SEALED_CLASSIC342_SOURCE_REPLAY_INPUTS_ONLY','nativeSources':342,
      'parentLineage':lineage,'excludedOldPacketInputs':skipped,'actualEnginePins':None,'actualHTTPPins':None,
      'compatibilityAcceptance':False,'guestOrBuildExecuted':False,'liveComputedInputs':computed}
    cap=HERE/'capability/input-freeze.json'
    cap_rows=[{**row,'path':os.path.relpath((HERE/row['path']).resolve(),cap.parent)}for row in paths.values()]
    with cap.open('x')as stream:json.dump({**base,'inputs':sorted(cap_rows,key=lambda row:row['path'])},stream,indent=2);stream.write('\n')
    add(cap,'capability-manifest-bound-by-root-seal')
    with(HERE/'input-freeze.json').open('x')as stream:json.dump({**base,'inputs':[paths[key]for key in sorted(paths)]},stream,indent=2);stream.write('\n')
    template=(CLASSIC/'runtime-preflight.template.mjs').read_text()
    rendered=template.replace('@PINS_SHA@',sha(HERE/'runtime-pins.json')).replace('@INPUTS_SHA@',sha(HERE/'input-freeze.json')).replace('@RECIPE_SHA@',contract['productionRecipeSha256']).replace('@SELECTOR_SHA@',changed['tests/node-compat/module-selection.mjs']).replace('@ADMISSION_SHA@',changed['tests/node-compat/classic-streams-admission.mjs'])
    with(HERE/'native-preflight.mjs').open('x')as stream:stream.write(rendered)
    print(json.dumps({'rootInputs':len(paths),'capabilityInputs':len(cap_rows),'parents':len(lineage),'oldPacketInputsExcluded':len(skipped),'inputSha256':sha(HERE/'input-freeze.json'),'nativePreflightSha256':sha(HERE/'native-preflight.mjs')}))
if __name__=='__main__':main()
