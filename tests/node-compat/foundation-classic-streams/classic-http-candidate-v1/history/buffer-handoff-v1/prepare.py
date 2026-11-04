"""Finite HTTP wrapper afterimages. Never edit the64 replay bodies or baseline."""
from pathlib import Path
import hashlib
import json
import os
import re
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
REPLAY=HERE.parent/'production-regression-candidate-v1'
REPLAY_INDEX='81c55887dc5e767db27477ba28f0e7a26a948435c7ddc61c70da329d4bd7f029'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    assert sha((REPLAY/'index.json').read_bytes())==REPLAY_INDEX
    for row in json.loads((REPLAY/'index.json').read_bytes())['files']:
        assert sha((REPLAY/row['path']).read_bytes())==row['sha256']
    proofs=[]
    def produce(original,target,edits):
        old=original.read_text();text=old;applied=[]
        for before,after in edits:
            assert text.count(before)==1,(before,text.count(before));text=text.replace(before,after);applied.append({'old':before,'new':after})
        restored=text
        for edit in reversed(applied):assert restored.count(edit['new'])==1;restored=restored.replace(edit['new'],edit['old'])
        assert restored==old;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('x')as stream:stream.write(text)
        proofs.append({'original':str(original.relative_to(REPO)),'target':str(target.relative_to(HERE)),
            'beforeSha256':sha(old.encode()),'afterSha256':sha(text.encode()),'edits':applied,'reverseExact':True})
    builder=REPLAY/'capability/runners/http-build.mjs'
    line="import { createProfilePlugin } from '../../../../profile-bundler.mjs';"
    edits=[(line,line+"\nimport {createClassicHTTPPlugin,BASELINE_ENTRY,COMPOSER_SOURCE} from '../composer-plugin.mjs';"),
        ("  plugins: [\n", "  plugins: [\n    createClassicHTTPPlugin(),\n"),
        ("const expectedBundleImports = ['node:buffer', 'node:child_process',", "const expectedBundleImports = ['node:stream', 'node:stream/promises', 'node:buffer', 'node:child_process',"),
        ("audit.currentProductionAdmission=productionAdmission.report;", "audit.currentProductionAdmission=productionAdmission.report;\naudit.classicCombinedHTTP={schema:1,ordinaryGroups:19,nodeOracleSha256:'88bd20781a396e6fd178d3b014a98495fec848eb28adb81c80e7dc838f4686ce',baselineEntry:BASELINE_ENTRY,composerSha256:hash(COMPOSER_SOURCE),scope:'Ordinary19 only; no classic fatal/init/limit/GC or Web bridge cases'};")]
    produce(builder,HERE/'capability/runners/http-build.mjs',edits)
    for name in ['computed-inputs.mjs','focused-preflight.mjs','capabilities.mjs']:
        with(HERE/'capability'/name).open('xb')as stream:stream.write((REPLAY/'capability'/name).read_bytes())
    for name in ['test-wasmtime-http.mjs','run-host.mjs']:
        source=REPO/'tests/node-compat/wasmcloud'/name;target=HERE/'capability/hosts'/name
        old=source.read_text();rewrites=[]
        for match in re.finditer(r"from (['\"])(\.[^'\"]+)\1",old):
            before=match.group(0);new_path=os.path.relpath((source.parent/match.group(2)).resolve(),target.parent)
            if not new_path.startswith('.'):new_path='./'+new_path
            after='from '+match.group(1)+new_path+match.group(1)
            if before!=after:rewrites.append((before,after))
        # Keep all existing per-response assertions, projecting only their input.
        rewrites += [("import { checkEntropyHTTPReport, checkEntropyHTTPSamples }", "import { checkEntropyHTTPReport }"),
          ("const body = JSON.parse(text);", "const combinedBody = JSON.parse(text);\n    const body = projectCombinedHTTPBody(combinedBody,audit);"),
          (", body });", ", body: combinedBody });")]
        if name=='run-host.mjs':rewrites.append(("const here = dirname(fileURLToPath(import.meta.url));", "const here = resolve(dirname(fileURLToPath(import.meta.url)), '../../../../wasmcloud');"))
        marker="import assert from 'node:assert/strict';"
        rewrites.append((marker,marker+"\nimport {projectCombinedHTTPBody,checkCombinedHTTPSamples as checkEntropyHTTPSamples} from '../validate-combined.mjs';"))
        produce(source,target,rewrites)
    # Exact oracle-construction block, extracted without execution or substitutions.
    text=builder.read_text();start=text.index('const virtualModules =');end=text.index('\nconst preview1AdapterPath',start)
    block=text[start:end]
    preamble="""// Host-only exact baseline oracle construction; no engine/package/guest call.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {dirname,resolve,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {selectCoreExpectations,coreExpectationsForGuest} from '../../../core-expectations.mjs';
import {makeOracleCorpus} from '../../../oracle.mjs';
const hash=value=>createHash('sha256').update(value).digest('hex');
export async function loadHTTPOracles(admission,httpEntry){
const here=resolve(dirname(fileURLToPath(import.meta.url)),'../../../wasmcloud');
const engineMetadata=admission.metadata,engineSourceRoot=admission.sourceRoot;
const sourcePaths=new Set(engineMetadata.sourceManifest.map(row=>row.path));
const builtinManifests=admission.builtinManifests;
const entropyPolicy='runtime-only',corpus=makeOracleCorpus();
const coreExpectations=selectCoreExpectations(engineMetadata,{sourceRoot:engineSourceRoot});
const foundationsIntegrationFixture=true,expandedFoundationsFixture=true,utilFoundationsFixture=true,streamWebFoundationsFixture=true,protectedAbortFoundationsFixture=true;
let foundationOracles=null;const protectedAbortAdmission=admission.report;
"""
    out=preamble+block+"\nreturn{virtualModules,foundationOracles,coreExpectations,corpus};\n}\n"
    with(HERE/'capability/oracles.mjs').open('x')as stream:stream.write(out)
    with(HERE/'transformations.json').open('x')as stream:json.dump({'schemaVersion':1,'state':'SOURCE_ONLY_COMBINED_HTTP_WRAPPER_TRANSFORMATIONS',
        'replayIndexSha256':REPLAY_INDEX,'proofs':proofs,'oracleBlockSha256':sha(block.encode()),'oracleBlockByteExact':True,
        'baselineBodyModified':False,'replayBodiesModified':False,'packagingOrGuestExecuted':False},stream,indent=2);stream.write('\n')
if __name__=='__main__':main()
