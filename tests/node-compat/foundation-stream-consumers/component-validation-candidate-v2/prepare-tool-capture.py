"""Source derivative of the already reviewed physical tool resolver; no imports."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
ORIGIN=REPO/'tests/node-compat/foundation-zlib/component-validation-activated-v8/component-tools.mjs'
def sha(value):return hashlib.sha256(value).hexdigest()
def main():
    old=ORIGIN.read_text();source=old;edits=[]
    def replace(before,after,count=1):
        nonlocal source
        assert source.count(before)==count,before
        edits.append({'old':before,'new':after,'count':count});source=source.replace(before,after)
    replace("import {createRequire} from 'node:module';","import {createRequire} from 'node:module';\nimport {fileURLToPath} from 'node:url';")
    replace("export const componentToolRoot='/Users/dan/dev/StarlingMonkey';","export const componentToolRoot=resolve(dirname(fileURLToPath(import.meta.url)),'packaging-tools');")
    replace("'builtins/node-compat/validate-manifest.mjs'].sort());","'builtins/node-compat/validate-manifest.mjs','tests/node-compat/zlib-admission.mjs','tests/node-compat/stream-consumers-admission.mjs','tests/node-compat/foundation-zlib/native-integration-candidate-v4/compile-input.mjs'].sort());")
    replace('foundation-classic-streams/integration-candidate-v1/','foundation-classic-streams/trace-integration-candidate-v1/',3)
    line=next(line for line in source.splitlines()if line.startswith('const inactiveData='))
    names=re.findall(r"'([^']+)'",line)
    names.extend('tests/node-compat/foundation-zlib/native-integration-candidate-v4/'+name for name in ['admission-pins.json','policy.json','layer-policy.py'])
    names.extend('tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v2/'+name for name in ['admission-pins.json','policy.json','layer-policy.py'])
    replace(line,'const inactiveData=Object.freeze('+json.dumps(names,separators=(',',':'))+'.sort());')
    replace('all nine transitive modules','all twelve transitive modules')
    replace('all six inactive lazy selector reads','all twelve inactive lazy selector reads')
    replace('localModules:9','localModules:12')
    replace('raw350 manifests/engine','genuine355 manifests/engine')
    replace('not invoked for350','not invoked for355')
    replace('PINNED_PUBLIC_ZLIB_COMPONENT_TOOL_CLOSURE_V1','PINNED_CONSUMERS355_COMPONENT_TOOL_SNAPSHOT_CLOSURE_V1')
    value=source
    for row in reversed(edits):assert value.count(row['new'])==row['count'];value=value.replace(row['new'],row['old'])
    assert value==old
    with(HERE/'component-tools.mjs').open('x')as output:output.write(source)
    with(HERE/'component-tools.derivation.json').open('x')as output:json.dump({'schemaVersion':1,'origin':str(ORIGIN),'beforeSha256':sha(old.encode()),'afterSha256':sha(source.encode()),'edits':edits,'reverseExact':True,'ownerModuleExecuted':False},output,indent=2);output.write('\n')
    print(json.dumps({'sourceOnly':True,'edits':len(edits),'modules':12,'inactiveLazyData':12}))
if __name__=='__main__':main()
