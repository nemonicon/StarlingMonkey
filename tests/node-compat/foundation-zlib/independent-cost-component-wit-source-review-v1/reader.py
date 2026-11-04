#!/usr/bin/env python3
"""Read/hash and finite pinned-source inspection only. No owner imports/actions."""
import difflib
import hashlib
import json
from pathlib import Path
import re
import stat

HERE = Path(__file__).resolve().parent
Z = HERE.parent
C = Z / 'cost-component-wit-amendment-v1'
D = Z / 'cost-component-candidate-v1'
T = Z / 'cost-tooling-candidate-v3'
records = {}

def need(value, text):
    if not value:
        raise AssertionError(text)

def row(p, expected=None):
    p = Path(p)
    s = p.lstat()
    need(stat.S_ISREG(s.st_mode), 'regular final file ' + str(p))
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    r = {'path': str(p), 'sha256': h.hexdigest(), 'bytes': s.st_size}
    if expected:
        need(all(r[k] == expected[k] for k in ('sha256', 'bytes')), 'exact tuple ' + str(p))
    records[str(p)] = r
    return r

def read(p):
    return json.loads(Path(p).read_text())

def indexed(root, pin):
    r = row(root / 'index.json')
    need(r['sha256'] == pin, 'pinned source index')
    d = read(root / 'index.json')
    names = set()
    for item in d['files']:
        n = item['path']
        need(not Path(n).is_absolute() and all(v not in ('', '.', '..') for v in n.split('/')) and '\\' not in n, 'safe finite source member')
        need(n not in names, 'unique source member')
        names.add(n)
        row(root / n, item)
    return d

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')

def main():
    own = indexed(C, 'e7252156f464f3a73621c002d01b95fa309ebc8208934539687d54d885257caa')
    donor = indexed(D, 'a2fa62b3ab63a6aca044aec9a83c1ff5a09edaa208eb615226a13845bf1522f9')
    tooling = indexed(T, 'ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8')
    prep = read(C / 'input-freeze.json')
    need(len(own['files']) == 20 and len(prep['files']) == 48, 'actual finite source/input counts')
    for item in prep['files']:
        row(item['path'], item)
    failure = Z / 'independent-cost-component-native-on-v1-failure-review-v1'
    indexed(failure, '0075de18a03de7156a34277c7a86ea5519d148820f41ee25a1d108f700c610a7')
    pr = Z / 'cost-component-wit-parameter-parser-regression-root-v1'
    indexed(pr, '5fe4a9a5d10941d78f63ff6ce0f7da13871f927663ee69e68f7d452ada7abb4b')
    before = (D / 'public-abi.wit').read_text()
    after = (C / 'public-abi.wit').read_text()
    need(before.count('record: string') == 2 and after == before.replace('record: string', 'input: string'), 'exact two labels and no other WIT change')
    need(after == (pr / 'corrected.wit').read_text(), 'exact already-executed real parser fixture')
    # Types, declaration order, names and arities independently retain the ABI.
    abi_pattern = r'export\s+([a-z]+):\s*func\(([^)]*)\)\s*->\s*(string);'
    def surface(text):
        return [(n, [v.strip().split(':')[1].strip() for v in p.split(',')] if p.strip() else [], r) for n,p,r in re.findall(abi_pattern, text)]
    abi = surface(after)
    need(abi == surface(before) and len(abi) == 7, 'all seven names/types/arities unchanged')
    need((C / 'build-worker.mjs').read_bytes() == (D / 'build-worker.mjs').read_bytes(), 'worker body byte-identical in new physical directory')
    derivations = read(C / 'derivations.json')
    need({x['path'] for x in derivations['files']} == {'guard.mjs','build.mjs','build-worker.mjs','public-abi.wit'}, 'exact finite derivation set')
    for item in derivations['files']:
        old = ''.join(difflib.restore(item['ndiff'], 1)).encode()
        new = ''.join(difflib.restore(item['ndiff'], 2)).encode()
        need(old == (D / item['path']).read_bytes() and new == (C / item['path']).read_bytes(), 'exact reversible source ' + item['path'])
        need(hashlib.sha256(old).hexdigest() == item['beforeSha256'] and hashlib.sha256(new).hexdigest() == item['afterSha256'], 'derivation hashes')

    shims = ['authority.mjs','abi.mjs','collector.mjs','proofs.mjs','durable.mjs','durable-host.mjs']
    for name in shims:
        need((C / name).read_text() == "// Immutable donor mechanism; complete donor source/critical closure is verified.\nexport * from '../cost-component-candidate-v1/" + name + "';\n", 'exact one-donor shim ' + name)
    # This finite regex is for these pinned import forms, not general JS parsing.
    roots = [C / n for n in ['build.mjs','build-worker.mjs','guard.mjs'] + shims]
    queue, seen, edges = roots[:], set(), []
    while queue:
        p = queue.pop(0).resolve()
        if p in seen:
            continue
        seen.add(p)
        for spec in re.findall(r"(?:from\s+|import\s*)['\"]([^'\"]+)['\"]", p.read_text()):
            if spec.startswith('node:'):
                continue
            need(spec.startswith('.'), 'only finite local or Node import')
            target = (p.parent / spec).resolve()
            need(target.parent in (C, D), 'no old HERE or external shim escape')
            need(target.is_file(), 'physical local module ' + str(target))
            row(target)
            edges.append({'source':str(p),'specifier':spec,'target':str(target)})
            queue.append(target)
    need({p for p in seen if p.parent == D} == {D / n for n in shims}, 'complete actual six-donor transitive import closure')

    guard = (C / 'guard.mjs').read_text()
    build = (C / 'build.mjs').read_text()
    worker = (C / 'build-worker.mjs').read_text()
    need("const own=await sourceIndex(join(HERE,'index.json'),componentSourceIndexSha256),donor=await sourceIndex(join(HERE,'../cost-component-candidate-v1/index.json'),COMPONENT_BASE_SHA)" in guard, 'distinct own and full donor index contexts')
    need("value.componentBaseSourceIndexSha256===COMPONENT_BASE_SHA" in guard, 'separate base source authority field required')
    need(guard.index('const own=await sourceIndex(') < guard.index("await import(pathToFileURL(join(baseRoot,'context.mjs')))"), 'own/donor/tool source authentication before dynamic inherited data validators')
    need('await own.recheck();await donor.recheck();await base.recheck();await peer.recheck();' in guard, 'complete source recheck')
    need("'/private/tmp/starling-node-compat/zlib-cost-component-v2-'+arm" in guard and 'zlib-cost-component-v1-' not in guard, 'new exclusive output namespace')
    need("componentSourceIndexSha256===componentSourceIndexSha256" in guard and 'peer.data.componentSourceIndexSha256===componentSourceIndexSha256' in guard, 'new own source value and source peer retained')
    need("join(HERE,'build-worker.mjs')" in build and "readFile(join(HERE,'public-abi.wit'),'utf8')" in worker, 'new HERE worker reads new WIT')
    need("sourceIndex(join(HERE,'../cost-component-candidate-v1/index.json'),componentSourceIndexSha256)" not in guard, 'no own source identity passed to old HERE')
    own_critical = ['authority.mjs','abi.mjs','collector.mjs','build.mjs','build-worker.mjs','guard.mjs','proofs.mjs','durable.mjs','durable-host.mjs','public-abi.wit']
    need(("for(const name of" + str(own_critical)).replace(' ', '') in build.replace(' ', ''), 'all own runtime/source critical tuples')
    need("for(const name of['authority.mjs','abi.mjs','collector.mjs','proofs.mjs','durable.mjs','durable-host.mjs'])critical.push(await rowAt(join(HERE,'../cost-component-candidate-v1',name)))" in build, 'actual donor modules critical tuples')
    need("'control/'" in build, 'all physical publication control modules critical')
    need(build.index('await admitted.recheck();const output=') > build.index('critical.push(descriptor(engine),metadata)'), 'source/auth recheck before exclusive outputs')
    need('componentSourceIndexSha256:admitted.componentSourceIndexSha256' in build and 'rootAction:admitted.rootAction' in build, 'new own source and actual Root authority passed to child')
    need(worker.index('for(const row of d.criticalFiles)await regular(row') < worker.index('await import(pathToFileURL(join(d.publicationRoot'), 'critical files authenticated before selected loader import')
    need('authorityModel(root,{componentSourceIndexSha256:d.componentSourceIndexSha256,arm:d.arm})' in worker, 'child checks new source + base-bound actual Root authority')
    need(worker.count('for(const row of d.criticalFiles)await regular(row') == 2, 'pre/post worker critical checks')
    need("need(workerRow.bytes<=65536" in build and "regular(input,{maxBytes:65536})" in worker, 'actual64KiB descriptor limits')
    need("timeoutMs:admitted.workerTimeoutMs,maxOutputBytes:16*1024*1024" in build, 'unchanged owned child budget and capture')

    # Inventory the proposed worker-critical list against the already sealed
    # real publication. This only reads bytes, it does not build a descriptor/action.
    pubroot = Path('/private/tmp/starling-node-compat/zlib-cost-source-v3')
    need(row(pubroot / 'index.json')['sha256'] == '4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b', 'actual immutable source publication')
    prefixes = ['packaging/tests/node-compat/','tools/packager/src/','tools/packager/lib/','tools/packager/splicer-build.json','tools/packager/package.json','control/']
    selected = [x for x in read(pubroot / 'index.json')['files'] if any(x['path'].startswith(v) for v in prefixes) and x['bytes'] <= 64*1024*1024]
    critical = []
    for item in selected:
        critical.append(row(pubroot / item['path'], item))
    for name in own_critical:
        critical.append(row(C / name))
    for name in shims:
        critical.append(row(D / name))
    for n in ['normal-off.engine.wasm','normal-off.engine.wasm.build.json']:
        critical.append(row(Path('/tmp/starling-node-compat/production-zlib-v4/native-freeze') / n))
    need(len(selected) == 60 and len(critical) == 78, 'actual prospective finite critical list count')
    need(len({x['path'] for x in critical}) == 78, 'no critical duplicates')
    control = [x for x in critical if x['path'].startswith(str(pubroot / 'control') + '/')]
    need(len(control) == 9, 'all nine physical control modules')
    need({p for p in seen}.issubset({Path(x['path']) for x in critical}), 'all statically imported local shim/donor runtime files covered')
    future = read(C / 'future-authority.json')
    need(all(future[k] is None for k in ['ownSourceIndex','rootComponentAction','newComponent','newABI','correctness','timing']), 'closed NULL future fields')
    need(future['actionsAllowed'] is False and future['operationalAdmission'] is False, 'source is no action authority')
    pure = read(C / 'evidence/stdout.log')
    syntax = read(C / 'evidence/syntax-results.json')
    need(pure['checks'] == 8 and pure['authorityModelSyntheticOnly'] is True and pure['actualParserInvokedByAuthor'] is False, 'stored8 pure checks scope')
    need(syntax['checks'] == 11 and all(x.get('nodeCheckExitCode') == 0 or x.get('ASTParsed') is True for x in syntax['files']), 'stored11 syntax checks')
    outputs = ['/private/tmp/starling-node-compat/zlib-cost-component-v2-' + arm for arm in ['native-on','fflate-on','fflate-off']]
    need(all(not Path(p).exists() for p in outputs), 'fresh output roots absent at review')
    result = {
        'schemaVersion':1,
        'state':'INDEPENDENT_ZLIB_COST_COMPONENT_SOURCE_REVIEW_PASSED_V1',
        'componentSourceIndexSha256':row(C / 'index.json')['sha256'],
        'componentBaseSourceIndexSha256':row(D / 'index.json')['sha256'],
        'sourceOnly':True,'sourceReviewPassed':True,'ownerActionsInvoked':False,
        'sourceFilesRehashed':20,'preparationRowsRehashed':48,'donorFilesRehashed':25,'toolingFilesRehashed':len(tooling['files']),
        'correctedWitSha256':row(C / 'public-abi.wit')['sha256'],'witParameterLabelChanges':2,
        'publicNamesTypesAritiesUnchanged':True,'workerByteIdenticalNewPhysicalHere':True,
        'exactReversibleDerivations':4,'actualDonorModules':shims,
        'ownAndDonorStaticRuntimeModules':len(seen),'localImportEdges':len(edges),
        'proposedWorkerCriticalRowsFromActualPublication':78,'publicationControlModulesCovered':9,
        'donorFullAuthenticationAndChildRuntimeCoverage':True,'oldHereOrSourceIdentityRedirection':False,
        'oldFailureReview':row(failure / 'index.json'),'parserRegression':row(pr / 'index.json'),
        'storedAuthorPureChecks':8,'storedAuthorSyntaxChecks':11,'reviewerReranTestsOrParser':False,
        'futureOutputsAbsentAtReview':outputs,'freshRootAuthorityRequired':True,
        'newComponentProduced':False,'newActualAbi':None,'ordinaryGuestExportsInvoked':False,
        'runtimeCodecOrPerformanceProof':False,'operationalAdmission':False,
        'uniqueInputsRehashed':len(records),
    }
    write('source-import-edges.json', edges)
    write('prospective-critical-rows.json', critical)
    write('rehashed-inputs.json', [records[k] for k in sorted(records)])
    write('results.json', result)
    print(json.dumps({'state':result['state'],'uniqueInputsRehashed':len(records),'criticalRows':78,'runtimeModules':len(seen)}))

if __name__ == '__main__':
    main()
