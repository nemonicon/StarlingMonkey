"""Prepare an unapplied production patch and exact local-input runtime seal."""
from pathlib import Path
import difflib
import hashlib
import json
import os
import re
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
def sha(data):return hashlib.sha256(data).hexdigest()
def write(name,data):
    with(HERE/name).open('xb')as stream:stream.write(data if isinstance(data,bytes)else data.encode())
def main():
    targets={str(path.relative_to(HERE/'source')):path for path in(HERE/'source').rglob('*')if path.is_file()}
    assert len(targets)==41
    patch=[];beforeAfter=[]
    for name,path in sorted(targets.items()):
        original=REPO/name;before=original.read_bytes()if original.exists()else b'';after=path.read_bytes()
        assert before!=after
        patch.extend(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+name if original.exists()else'/dev/null',tofile='b/'+name))
        beforeAfter.append({'path':name,'beforeSha256':sha(before)if original.exists()else None,'afterSha256':sha(after),'bytes':len(after)})
    write('classic-streams.UNAPPLIED.patch',''.join(patch))
    write('patch-files.json',json.dumps({'state':'UNAPPLIED_PRODUCTION342_AND_FINITE_SELECTOR_PATCH','files':beforeAfter,'nativeFiles':38,'producerAndAdmissionFiles':3,'newFiles':sum(row['beforeSha256']is None for row in beforeAfter),'replacedFiles':sum(row['beforeSha256']is not None for row in beforeAfter)},indent=2)+'\n')
    # Resolve source imports against their FUTURE logical location; afterimages
    # are sealed without pretending they already occupy live repository paths.
    rows={};roles={}
    def add(logical,role):
        logical=Path(logical).resolve();physical=targets.get(str(logical.relative_to(REPO)))if logical.is_relative_to(REPO)else None
        physical=physical or logical
        assert physical.is_file()and not physical.is_symlink(),physical
        rel=os.path.relpath(physical,HERE);data=physical.read_bytes()
        rows[rel]={'path':rel,'sha256':sha(data),'bytes':len(data)};roles.setdefault(rel,set()).add(role);return physical
    roots=[HERE/'harness/run.mjs',HERE/'runtime-contract.mjs',REPO/'tests/node-compat/core-expectations.mjs']
    queue=list(roots);seen=set()
    pattern=re.compile(r'''(?:\bfrom\s*|\bimport\s*\(|\bnew\s+URL\s*\()\s*['"]([^'"]+)['"]''')
    while queue:
        logical=Path(queue.pop()).resolve()
        if logical in seen:continue
        seen.add(logical);physical=add(logical,'literal-local-import-or-url')
        if physical.suffix not in['.mjs','.js']:continue
        for match in pattern.finditer(physical.read_text()):
            spec=match.group(1)
            if not spec.startswith('.'):continue
            child=(logical.parent/spec).resolve()
            candidate=targets.get(str(child.relative_to(REPO)))if child.is_relative_to(REPO)else None
            if(candidate or child).is_file():queue.append(child)
    # Computed readers which are not ordinary relative JS imports.
    for name in ['policy.json','layer-policy.py','admission-pins.json','runtime-pins.json','runtime-preflight.template.mjs','harness/component-driver.mjs','harness/guest.mjs','harness/checks.mjs','harness/deferred-snippets.mjs','harness/deployed-fixtures.mjs','harness/node-oracle-results.json']:
        add(HERE/name,'explicit-computed-local-reader')
    for name in ['foundation-scheduler/integration-candidate-v1/policy.json','foundation-scheduler/integration-candidate-v1/layer-policy.py','foundation-scheduler/admission-candidate-v1/pins.json','toolchain/package.json','toolchain/package-lock.json']:
        add(REPO/'tests/node-compat'/name,'explicit-parent-tooling-dependency')
    add(HERE.parent/'implementation-candidate-v1/node-final-acceptance-results.json','exact-consumed-node-oracle')
    add(REPO/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm','LIVE-preview1-adapter-reopened-by-componentizer')
    for path in targets.values():add(REPO/str(path.relative_to(HERE/'source')),'proposed-production-afterimage')
    for row in json.loads((HERE/'policy.json').read_bytes())['expectedNativeSourceManifest']:
        add(REPO/row['path'],'native342-policy-member-or-afterimage')
    document={'schemaVersion':1,'state':'CLASSIC_SOURCE_ONLY_FUTURE_RUNTIME_INPUT_SEAL','inputs':[rows[key]for key in sorted(rows)],
      'logicalAfterimages':[{'logicalPath':name,'physicalPath':os.path.relpath(path,HERE)}for name,path in sorted(targets.items())],
      'scope':'Local source/template inputs, including all342 proposed native files and live Preview1 adapter; no future engine or toolchain binary is fabricated. Actual frozen engine inventory and future reviewed activation remain mandatory.',
      'computedReaderRoles':{key:sorted(value)for key,value in sorted(roles.items())}}
    write('input-freeze.json',json.dumps(document,indent=2)+'\n')
    pins=json.loads((HERE/'admission-pins.json').read_bytes());template=(HERE/'runtime-preflight.template.mjs').read_text()
    runtime=template.replace('@PINS_SHA@',sha((HERE/'runtime-pins.json').read_bytes())).replace('@INPUTS_SHA@',sha((HERE/'input-freeze.json').read_bytes())).replace('@RECIPE_SHA@',pins['productionRecipeSha256']).replace('@SELECTOR_SHA@',sha((HERE/'source/tests/node-compat/module-selection.mjs').read_bytes())).replace('@ADMISSION_SHA@',sha((HERE/'source/tests/node-compat/classic-streams-admission.mjs').read_bytes()))
    write('runtime-preflight.mjs',runtime)
    print(json.dumps({'patchFiles':len(targets),'patchSha256':sha((HERE/'classic-streams.UNAPPLIED.patch').read_bytes()),'inputs':len(rows),'inputFreezeSha256':sha((HERE/'input-freeze.json').read_bytes()),'runtimePreflightSha256':sha(runtime.encode())}))
if __name__=='__main__':main()
