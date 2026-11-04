"""Prepare finite342 dispatch while leaving the306 admission module unchanged."""
from pathlib import Path
import hashlib
import json
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    recipe=HERE/'source/tests/node-compat/build-engine.sh'
    pins={'schemaVersion':1,'state':'UNAPPLIED_CLASSIC_SOURCE_ADMISSION_CONTRACT',
      'productionRecipeSha256':sha(recipe.read_bytes()),'policySha256':sha((HERE/'policy.json').read_bytes()),'helperSha256':sha((HERE/'layer-policy.py').read_bytes()),
      'parentRecipeSha256':'869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173',
      'parentPolicySha256':'98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0',
      'parentHelperSha256':'78521feeefe299360228e5db76bfde0b11e6eeee93bd2374cd39b2fe695b610c',
      'parentAdmissionPinsSha256':sha((REPO/'tests/node-compat/foundation-scheduler/admission-candidate-v1/pins.json').read_bytes()),
      'current306AdmissionSha256':sha((REPO/'tests/node-compat/private-ticks-admission.mjs').read_bytes()),
      'nativeSourceInputs':342,'addsEmbeddingPatch':False,'reviewedFutureEnginePins':None}
    with(HERE/'admission-pins.json').open('x')as stream:json.dump(pins,stream,indent=2);stream.write('\n')
    parent=(REPO/'tests/node-compat/private-ticks-admission.mjs').read_text()
    utilities=parent[parent.index('function entries('):parent.index('export function validatePrivateTickSourceAdmission')]
    preamble="""//342-source admission, not runtime proof.306 branch remains in its unchanged module.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync,lstatSync} from 'node:fs';
import {resolve,join} from 'node:path';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
"""
    preamble+=f"const PINS_SHA='{sha((HERE/'admission-pins.json').read_bytes())}';\nconst RECIPE_SHA='{pins['productionRecipeSha256']}';\n"
    code=preamble+utilities+(HERE/'admission-body.mjs').read_text()
    target=HERE/'source/tests/node-compat/classic-streams-admission.mjs'
    with target.open('x')as stream:stream.write(code)
    selection=(REPO/'tests/node-compat/module-selection.mjs').read_text();before=selection;edits=[]
    def replace(a,b):
        nonlocal selection
        assert selection.count(a)==1,(a,selection.count(a));selection=selection.replace(a,b);edits.append({'old':a,'new':b})
    line="import {validatePrivateTickSourceAdmission} from './private-ticks-admission.mjs';"
    replace(line,line+"\nimport {validateClassicSourceAdmission} from './classic-streams-admission.mjs';")
    line="export const STREAM_WEB_MANIFEST = 'builtins/node-compat/export-manifest.stream-web.node-v22.14.0.json';"
    replace(line,line+"\nexport const CLASSIC_STREAMS_MANIFEST = 'builtins/node-compat/classic-streams/export-manifest.classic-streams.node-v22.14.0.json';")
    line="  const privateTicks = validatePrivateTickSourceAdmission(metadata, {sourceRoot,\n    parentProtectedSources:protectedAbortV1Sources,parentProtectedPatch:protectedAbortV1Patch});"
    replace(line,"  const classic = validateClassicSourceAdmission(metadata, {sourceRoot,\n    parentProtectedSources:protectedAbortV1Sources,parentProtectedPatch:protectedAbortV1Patch});\n  const privateTicks = classic ?? validatePrivateTickSourceAdmission(metadata, {sourceRoot,\n    parentProtectedSources:protectedAbortV1Sources,parentProtectedPatch:protectedAbortV1Patch});")
    line="    ['streamWebEnabled', 'NODE_COMPAT_STREAM_WEB', STREAM_WEB_MANIFEST],"
    replace(line,line+"\n    ['classicStreamsEnabled', 'NODE_COMPAT_CLASSIC_STREAMS', CLASSIC_STREAMS_MANIFEST],")
    with(HERE/'source/tests/node-compat/module-selection.mjs').open('x')as stream:stream.write(selection)
    with(HERE/'selector-transformations.json').open('x')as stream:json.dump({'state':'FINITE_DISPATCH_306_BRANCH_UNCHANGED','beforeSha256':sha(before.encode()),'afterSha256':sha(selection.encode()),'unchanged306AdmissionSha256':pins['current306AdmissionSha256'],'edits':edits},stream,indent=2);stream.write('\n')
    print(json.dumps({'admissionPinsSha256':sha((HERE/'admission-pins.json').read_bytes()),'admissionSha256':sha(code.encode()),'selectorSha256':sha(selection.encode()),'selectorEdits':len(edits)}))
if __name__=='__main__':main()
