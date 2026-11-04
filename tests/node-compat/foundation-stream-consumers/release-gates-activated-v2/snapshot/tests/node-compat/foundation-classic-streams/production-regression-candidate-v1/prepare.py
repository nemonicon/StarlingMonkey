"""Source-only classic342 replay derivation; never launches a runner or a toolchain."""
from pathlib import Path
import hashlib
import json
import os
import re
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
PARENT=REPO/'tests/node-compat/foundation-scheduler'
ORIGINALS={'common':PARENT/'production-regression-candidate-v5','off':PARENT/'production-followon-off-v3',
 'release':PARENT/'production-release-runner-v3','capability':PARENT/'production-followon-capability-v3'}
def sha(data):return hashlib.sha256(data).hexdigest()
def write(name,data):
    path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb')as stream:stream.write(data if isinstance(data,bytes)else data.encode())
def map_path(path):
    for name,root in ORIGINALS.items():
        if path.is_relative_to(root):return HERE/name/path.relative_to(root)
    return path
def rewrite_paths(text,source,destination):
    edits=[]
    pattern=re.compile(r'''(['"])(\.[^'"\n]*)\1''')
    local_names=set(re.findall(r'(?:const|let)\s+(\w+)\s*=\s*dirname\(fileURLToPath\(import\.meta\.url\)\)',text))
    # releaseJobs receives the location of its own sibling entry module.
    if source.name=='job-plan.mjs':local_names.add('here')
    def replace(match):
        value=match.group(2)
        if '\\'in value or '${'in value:return match.group()
        prefix=text[max(0,match.start()-180):match.start()]
        direct=bool(re.search(r'(?:\bfrom\s*|\bimport\s*\(|\bnew\s+URL\s*\()\s*$',prefix))
        direct=direct or bool(re.search(r'\b(?:resolve|join)\(dirname\(fileURLToPath\(import\.meta\.url\)\),\s*$',prefix))
        anchor=re.search(r'\b(?:resolve|join)\((\w+),\s*$',prefix)
        direct=direct or bool(anchor and anchor.group(1)in local_names)
        if not direct:return match.group()
        original=(source.parent/value).resolve()
        if not(original.exists()or original.parent.exists()):return match.group()
        mapped=map_path(original);new=os.path.relpath(mapped,destination.parent)
        if not new.startswith('.'):new='./'+new
        if value.endswith('/')and not new.endswith('/'):new+='/'
        if new==value:return match.group()
        edits.append({'old':match.group(),'new':match.group(1)+new+match.group(1)})
        return match.group(1)+new+match.group(1)
    return pattern.sub(replace,text),edits
def function_end(text,start):
    # Exact established boundaries, never parse/execute source to find them.
    end=text.index('\n}\n',start)+3;return end
def main():
    assert not(HERE/'derivations.json').exists()
    chosen={
      'common':['run-core.mjs','run-allocator.mjs','run-allocator-gc.mjs','runners/allocator.mjs','runners/allocator-gc.mjs'],
      'off':[*(f'run-{name}.mjs'for name in['sync','runtime','late','callbacks','stream-web']),*(f'runners/{name}.mjs'for name in['sync','runtime','late','callbacks','stream-web'])],
      'release':['preflight.mjs','run-release.mjs','run-optional.mjs','serial.mjs','job-plan.mjs','historical-controls.json','helpers/native-scalar-harness.mjs',
        *(f'run-{name}.mjs'for name in['path','events','string-decoder','assert','querystring','util']),*(f'runners/{name}.mjs'for name in['path','events','string-decoder','assert','querystring','util'])],
      'capability':[]}
    for path in sorted(ORIGINALS['capability'].rglob('*')):
        if not path.is_file()or'history'in path.relative_to(ORIGINALS['capability']).parts:continue
        rel=str(path.relative_to(ORIGINALS['capability']))
        if(path.suffix in['.mjs','.cjs','.wit']and rel not in['preflight.mjs','admission.mjs','test-host.mjs','preflight-only.mjs'])or rel=='focused/node-results.json':chosen['capability'].append(rel)
    records=[]
    for name,files in chosen.items():
        root=ORIGINALS[name]
        for relative in files:
            source=root/relative;destination=HERE/name/relative;before=source.read_bytes();text=before.decode();after,edits=rewrite_paths(text,source,destination)
            # Reporting identities describe this new source policy, not an old
            # source-count projection or adoption of a previous result.
            substitutions=[('sourceFiles:306','sourceFiles:342'),('nativeSources:306','nativeSources:342'),('PRODUCTION306_HTTP_','CLASSIC342_HTTP_'),('production306 Events-ON','classic342 Events-ON'),('native306/config','native342/config'),('NEW_PRODUCTION306_','NEW_CLASSIC342_'),('production306 source proposal','classic342 source replay'),('Production306 is newly','Classic342 is newly'),('all 306 source pins','all 342 source pins')]
            for old,new in substitutions:
                count=after.count(old)
                if count:after=after.replace(old,new);edits.append({'old':old,'new':new,'count':count})
            if name=='release'and relative=='preflight.mjs':
                old="import {selectDependencyIndex} from '../common/dependency-bindings.mjs';\n"
                assert old in after;after=after.replace(old,'');edits.append({'old':old,'new':''})
                start=after.index('export async function verifyReleaseOff(){');end=function_end(after,start);old=after[start:end]
                new="""export async function verifyReleaseOff(){
  const production=await verifyProductionTicks({gcStress:false});
  return{production,report:{state:'classic342-release-off-fixed-artifact-admission-passed',production:production.report,runtimeProof:false},recheck:production.recheck};
}
"""
                after=after[:start]+new+after[end:];edits.append({'old':old,'new':new})
            write(name+'/'+relative,after)
            records.append({'sourcePath':str(source.relative_to(REPO)),'destinationPath':name+'/'+relative,'beforeSha256':sha(before),'afterSha256':sha(after.encode()),'edits':edits,'semanticFixtureChanges':False})
    # Preserve the exact path-validation helper, without the stale306 admission.
    old=(ORIGINALS['capability']/'admission.mjs').read_text();start=old.index('export function validatePinBoundary');end=old.index('\nexport function validateProductionMetadata',start)
    write('capability/admission.mjs',"import assert from 'node:assert/strict';\nimport {resolve,relative,isAbsolute} from 'node:path';\n"+old[start:end]+'\n')
    write('runtime-contract.mjs',(HERE.parent/'integration-candidate-v1/runtime-contract.mjs').read_bytes())
    write('runtime-pins.json',(HERE.parent/'integration-candidate-v1/runtime-pins.json').read_bytes())
    write('capability/http-component-pins.json',json.dumps({'schemaVersion':1,'state':'UNCONFIGURED_CLASSIC342_HTTP_COMPONENT','component':None,'actualComponentPins':None,'requiresIndependentReviewAndNewActivationSibling':True},indent=2)+'\n')
    write('derivations.json',json.dumps({'schemaVersion':1,'state':'SOURCE_ONLY_CLASSIC342_REPLAY_DERIVATIONS','nativeBuildOrGuestExecuted':False,'records':records},indent=2)+'\n')
    print(json.dumps({'copiedRuntimeSources':len(records),'guestBodiesChanged':False,'enginePins':None,'httpComponentPins':None}))
if __name__=='__main__':main()
