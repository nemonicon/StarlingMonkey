"""Independent finite source review. No bootstrap, packaging, engine or guest call."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'resource-component-candidate-v1'
EXPECTED = '74413aa9d1520139dc2ac4d8e43f0d99bab06477b8d8eb6e9d2db6bb58580055'
SEED = HERE.parents[1] / 'foundation-crypto/independent-ownership-secret-integration-source-review-v1'
SEED_SHA = '8665997e4edab561a0e0e63235104b8e358072995725002704f25e4499dfca45'


def row(path):
    data = Path(path).read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def write(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    assert __debug__ and sys.dont_write_bytecode
    # Authenticate the complete generic-reader seed before importing it at its
    # real original context. Its SOURCE/HERE and native-policy main are untouched.
    seed = row(SEED / 'index.json')
    assert seed['sha256'] == SEED_SHA
    seed_index = json.loads((SEED / 'index.json').read_bytes())
    seed_names = {'index.json'}
    for member in seed_index['files']:
        name = member['path']
        assert name and not Path(name).is_absolute() and '..' not in Path(name).parts
        assert name not in seed_names
        seed_names.add(name)
        assert row(SEED / name) == dict(member, path=str(SEED / name))
    assert {p.relative_to(SEED).as_posix() for p in SEED.rglob('*') if p.is_file()} == seed_names
    assert not any(p.is_symlink() for p in SEED.rglob('*'))
    spec = importlib.util.spec_from_file_location('authenticated_generic_source_reader', SEED / 'read-source.py')
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    need, regular, load, family = reader.need, reader.regular, reader.load, reader.family
    family(seed)
    source = row(SOURCE / 'index.json')
    need(source['sha256'] == EXPECTED and source['bytes'] == 16052, 'exact744 source seal')
    own = family(source)
    need(len(own['files']) == 99, 'exact99 source members')
    refs = json.loads((SOURCE / 'references.json').read_bytes())
    inputs = json.loads((SOURCE / 'input-freeze.json').read_bytes())
    need(len(inputs['files']) == len({r['path'] for r in inputs['files']}) == 5399, 'complete5399 declared original-context rows')
    for value in inputs['files']:
        regular(value)
    for value in refs['families']:
        family(value['index'])
    for key in ['bootstrapEntry', 'bootstrapConfig', 'bootstrapRootObservation', 'reviewedPins', 'rootPinReview', 'actualBootstrapWholeFrame', 'engine', 'metadata', 'freezeReceipt', 'node', 'jcoEntry']:
        regular(refs[key])
    peer = load(refs['actualBootstrapReview']['result'])
    need(peer['state'] == 'INDEPENDENT_SCHEDULER_RESOURCE342_NORMAL_OFF_BOOTSTRAP_REVIEW_PASSED_V1' and peer['verifiedPassed'], 'actual e9a bootstrap DATA peer')
    need(peer['resourceSourceIndexSha256'] == refs['resourceSourceIndex']['sha256'] and peer['toolingSourceIndexSha256'] == refs['toolingIndex']['sha256'], 'separate resource20e/toolingc55 identities')
    for key, value in [('engineSha256', refs['engine']), ('metadataSha256', refs['metadata']), ('freezeReceiptSha256', refs['freezeReceipt'])]:
        need(peer[key] == value['sha256'], 'actual bootstrap native identity ' + key)
    frame = load(refs['actualBootstrapWholeFrame'])
    native = json.loads((SOURCE / 'native-source-data.json').read_bytes())
    need(native['allNineManifests'] == frame['selectedManifests'] and len(frame['selectedManifests']) == 9, 'whole nine manifests')
    need(len(native['files']) == len(frame['metadata']['sourceManifest']) == 342, 'whole342 native source inventory')
    for value in native['files']:
        regular(value)
    need(frame['sourceRoot'] == refs['frozenSourceRoot'] and frame['configuredSourceRoot'] == refs['configuredSourceRoot'] and frame['sourceRoot'] != frame['configuredSourceRoot'], 'unprojected frozen/configured roles')
    need(frame['metadata']['engineSha256'] == refs['engine']['sha256'] and frame['metadata']['resourceOwnershipPolicy']['nativeRuntimeValidation'] is None, 'no runtime evidence fabricated')
    packaging = load(refs['packagingMap'])
    published = load(packaging['publicationIndex'])
    need(packaging['publicationIndex']['sha256'] == '4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b', 'genuine original packaging publication')
    need(packaging['originalZlibNativeFactsConsumed'] is False and packaging['costActionStatesReused'] is False, 'physical packaging roles only')
    need(len(packaging['files']) == 4934 and len(packaging['links']) == 22, 'whole4934/22 package boundary')
    root = Path(packaging['publicationRoot'])
    root_stat = root.stat()
    need((root_stat.st_dev, root_stat.st_ino) == (packaging['rootIdentity']['device'], packaging['rootIdentity']['inode']), 'actual immutable publication root')
    expected = {v['path']: v for v in packaging['files']}
    links = {v['destination']: v for v in packaging['links']}
    need(len(expected) == 4934 and len(links) == 22, 'unique full package roles')
    observed_files, observed_links = set(), set()
    for prefix in packaging['roleRoots']:
        for path in [root / prefix, *(root / prefix).rglob('*')]:
            name = path.relative_to(root).as_posix()
            st = path.lstat()
            if stat.S_ISLNK(st.st_mode):
                need(name in links and os.readlink(path) == links[name]['newLinkText'] and path.resolve() == root / links[name]['mappedTarget'], 'exact physical package link')
                observed_links.add(name)
            elif stat.S_ISDIR(st.st_mode):
                need(stat.S_IMODE(st.st_mode) == 0o700, 'private package directories')
            else:
                need(name in expected and stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and stat.S_IMODE(st.st_mode) == expected[name]['mode'], 'exact package regular member/mode')
                regular(dict(expected[name], path=str(path)))
                observed_files.add(name)
    need(observed_files == set(expected) and observed_links == set(links), 'no omitted physical package files or links')
    indexed = {v['path']: v for v in published['files']}
    for name, value in expected.items():
        need(all(indexed[name][k] == value[k] for k in ['sha256', 'bytes', 'mode']), 'every package role retained unchanged')
    need(published['links'] == packaging['links'] == refs['toolLinks'], 'entire typed link inventory')
    derivations = json.loads((SOURCE / 'fixture-derivations.json').read_bytes())['entries']
    for item in derivations:
        original = regular(item['original']).read_bytes()
        after = (SOURCE / item['afterimage']).read_bytes()
        if item['kind'].startswith('BYTE_EXACT'):
            need(after == original, 'exact original guest/WIT bytes')
        else:
            need(original.decode().count("const scalarWit='" + item['literal'] + "';") == 1 and after == (item['literal'] + '\n').encode(), 'exact existing scalar WIT literal')
    need(len(derivations) == 6, 'five copies/one exact literal')
    texts = {p.name: p.read_text() for p in SOURCE.glob('*.mjs')}
    entry, parent, worker, bundle, models = (texts[n] for n in ['entry.mjs', 'build.mjs', 'build-worker.mjs', 'bundle.mjs', 'models.mjs'])
    need(all(v.startswith('node:') for v in re.findall(r"^import .* from '([^']+)';", entry, re.M)), 'standard-only primitive entry')
    auth = entry[entry.index('async function authenticate('):entry.index('export async function resourceComponentPreflight(')]
    for token in ['await family(ownRow)', 'for(const r of manifest.files)await streamHash(r)', 'for(const r of refs.families)await family(r.index)', 'await packagingPhysical(refs.packagingMap)', 'await peer(root.sourceIndependentReview', 'authorityModel(root,sourceSha)']:
        need(token in auth, 'pre-body full authentication ' + token)
    need('resourceBootstrapPreflight({configDescriptor:source.refs.bootstrapConfig})' in entry and 'isDeepStrictEqual(comparison,expected)' in entry and 'delete comparison.recheck' in entry and 'delete native.' not in entry, 'genuine API and whole data frame comparison')
    need('constructionFrames.has(v)' in entry and 'workerFrames.has(v)' in entry and 'requireConstructionFrame(frame)' in parent and 'requireWorkerFrame(frame)' in worker, 'private object capabilities gate dormant bodies')
    for name in ['fixtureModel', 'authorityModel']:
        start = models.index('export function ' + name + '(')
        end = models.index('\n}', start) + 2
        need(models[start:end].replace('export function ', 'function ', 1) in entry, 'entry/pure exact contract agreement')
    external = {str(Path(v['path']).resolve()) for v in inputs['files']}
    import_edges = []
    for name, text in texts.items():
        for target in re.findall(r"(?:from\s*|import\s*\()(['\"])(\.[^'\"]+)\1", text):
            resolved = (SOURCE / name).parent / target[1]
            resolved = resolved.resolve()
            need(resolved.is_file() and (resolved.is_relative_to(SOURCE) or str(resolved) in external), 'literal custom import authenticated before bodies')
            import_edges.append(dict(source=name, specifier=target[1], resolved=str(resolved)))
    need(parent.index("await mkdir(join(output.root,'processes')") < parent.index('await runOwnedCommand(') < parent.index('checkOwnedTerminal(outcome)'), 'owned process namespace and raw terminal collection order')
    need('2*1024*1024*1024' in parent and '800*1024*1024' in parent and 'timeoutMs:root.workerTimeoutMs' in parent, 'bounded worker and disk point checks')
    need('builtinManifests:selectedManifests' in bundle and 'value.imports' in bundle and 'value.globalBufferPolicy' in bundle and 'Unobserved virtual source refuses' in bundle, 'explicit native selection/full graph residual policy')
    need('selectedManifestsForEngine' not in entry + parent + worker + bundle, 'no older engine selector applied to new metadata')
    need(worker.index("componentRow=await output.write('component.wasm'") < worker.index('const emitted=await componentWit(result.component)') < worker.index('return result.component;'), 'full bytes retained before later interface audit')
    packaging_componentizer = (Path(packaging['packagingRoot']) / 'tests/node-compat/componentizer.mjs').read_text()
    need(packaging_componentizer.index('const final = await finalizeComponent(result)') < packaging_componentizer.index('const interfaceAudit = await auditSelectedInterfaces(toolchain, result.component, interfacePolicy);', packaging_componentizer.index('const final = await finalizeComponent(result)')), 'actual existing callback precedes final audit')
    need('need(threw&&!captured' in worker and 'uniqueInitializationCauseProved:false' in worker, 'initializer control cannot accept post-build interface failure')
    need('for(const[name,bytes]of Object.entries(generated.files))' in worker and 'generatedModuleImported:false' in worker and 'loadingProtocolReviewRequired:true' in worker, 'whole observed transpilation retained without loading')
    need("disableFeatures:['stdio','random','http','fetch-event'" in models and "'wasi:clocks/monotonic-clock@0.2.10','wasi:io/poll@0.2.10'" in models, 'selected standard-only clocks policy')
    template = json.loads((SOURCE / 'future-root-authority.template.json').read_bytes())
    for key in ['state', 'sourceIndexSha256', 'phase', 'fixture', 'outputRoot', 'sourceIndependentReview', 'bootstrapConfig', 'bootstrapRootObservation', 'reviewedPins', 'rootPinReview']:
        need(template[key] is None, 'unissued Root slot ' + key)
    for key, value in template.items():
        if key.endswith('Allowed') or key in ['operationalAdmission', 'runtimeAcceptanceClaim', 'metadataProjectionAllowed']:
            need(value is False, 'closed action slot ' + key)
    ast_files = []
    for path in SOURCE.glob('*.py'):
        ast.parse(path.read_bytes(), filename=str(path))
        ast_files.append(path.name)
    for name in refs['fixtures']:
        need(not Path('/private/tmp/starling-node-compat/scheduler-resource-component-v1-' + name).exists(), 'no actual construction output')
    write('source-audit.json', dict(schemaVersion=1, state='INDEPENDENT_RESOURCE_COMPONENT_SOURCE_FINITE_AUDIT_PASSED_V1', checks=reader.checks, uniquePaths=len(reader.checked), sourceIndex=source, sourceMembers=99, inputRows=5399, nativeSourceFiles=342, selectedManifests=9, packagingFiles=4934, toolLinks=22, literalCustomImportEdges=import_edges, pythonAst=ast_files, fixtureDerivations=6, originalContextsPreserved=True, sourceOnly=True, ownerActionsInvoked=False))
    write('input-hashes.json', dict(schemaVersion=1, files=[{k: v for k, v in value.items() if k != 'identity'} for _, value in sorted(reader.checked.items())]))
    for path, value in reader.checked.items():
        regular(value)
    print(json.dumps(dict(state='INDEPENDENT_RESOURCE_COMPONENT_SOURCE_FINITE_AUDIT_PASSED_V1', checks=reader.checks, uniquePaths=len(reader.checked), ownerActionsInvoked=False)))


if __name__ == '__main__':
    main()
