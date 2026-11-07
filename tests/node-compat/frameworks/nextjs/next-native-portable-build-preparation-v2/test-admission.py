"""Source/data tests only. No generator, package, compiler, engine or guest."""
from pathlib import Path
import ast
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).absolute().parent
REPO = HERE.parents[4]
spec = importlib.util.spec_from_file_location('tested_portable_admission', HERE / 'portable.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
checks = 0
parser = argparse.ArgumentParser()
parser.add_argument('--materialization', type=Path)
args = parser.parse_args()


def check(value):
    global checks
    assert value
    checks += 1


def refused(call):
    global checks
    try:
        call()
    except (ValueError, OSError, KeyError, AssertionError):
        checks += 1
    else:
        raise AssertionError('Expected refusal')


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def ref(path):
    b = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))


plan = json.loads((HERE / 'plan.json').read_text())
policy = plan['portableSourcePolicy']
template = json.loads((HERE / 'root-authority.template.json').read_text())
check(plan['disk'] == dict(startBytes=3221225472, stopBytes=1073741824))
check(all(template[k] is None for k in ['portableSelection', 'generatorNode',
    'installedGeneratorResult', 'installedGeneratorCallerIndex', 'installedGeneratorRootAuthority',
    'cargo', 'rustc', 'reusedTrees', 'workRoot', 'configureAllowed', 'buildAllowed']))
check(policy['expectedCounts'] == {'native-policy-source': 435, 'build-support': 387, 'componentize-embedding': 3})
base = (REPO / 'tests/node-compat/frameworks/nextjs/next-native-build-candidate-v4/run.py').read_text()
current = (HERE / 'run.py').read_text()
old_ast = ast.parse(base)
new_ast = ast.parse(current)
old_functions = {n.name: ast.get_source_segment(base, n) for n in old_ast.body if isinstance(n, ast.FunctionDef)}
new_functions = {n.name: ast.get_source_segment(current, n) for n in new_ast.body if isinstance(n, ast.FunctionDef)}
for name in ['phase', 'phase_worker', 'phase_succeeded', 'command_plan', 'environment',
             'tree_snapshot', 'authenticate_tree', 'safe_extract', 'copy_exclusive', 'validate_configured']:
    check(old_functions[name] == new_functions[name])
check('portable_admission(a,spec)' in new_functions['effective_plan'])
check('portable_admission(a,spec)' in new_functions['inputs'])
check('check_family(a[\'installedGeneratorCallerIndex\']);portable_admission(a,spec)' in new_functions['main'])
check("extraction['engineCandidate']" not in new_functions['inputs'] and "extraction['sourceAfter']" not in new_functions['inputs'])

with tempfile.TemporaryDirectory(prefix='portable-build-admission-data-', dir='/private/tmp') as tmp:
    tmp = Path(tmp)
    # Tiny synthetic layouts exercise real parser and filesystem admission code.
    # Their policy is test data only; the production runner pins its own policy.
    root = tmp / 'synthetic-materialized'
    root.mkdir(mode=0o700)
    rows = []
    copied = []
    for role, dirname in policy['roleDirectories'].items():
        d = root / dirname
        d.mkdir(mode=0o700)
        p = d / 'sample.txt'
        p.write_bytes(role.encode())
        p.chmod(0o600)
        rows.append(dict(role=role, path='sample.txt', sha256=ref(p)['sha256'], bytes=p.stat().st_size, mode=0o600))
        copied.append(dict(role=role, relativePath='sample.txt', mode=0o600,
                           source=ref(p), repositoryDonor='synthetic-only/sample.txt'))
    tiny = dict(expectedCounts={r: 1 for r in policy['roleDirectories']},
                roleDirectories=policy['roleDirectories'], expectedFiles=3,
                expectedBytes=sum(r['bytes'] for r in rows), roleContentSha256=m.fingerprint(rows))
    composition = dict(schemaVersion=1, state='NEXT_PORTABLE_SOURCE_COMPOSITION_ONLY_V1',
        sourceRoot=str(root / 'source'), nativeSourceFiles=1,
        files=[{k: rows[0][k] for k in ['path', 'sha256', 'bytes']}], inputs=[],
        engineBuilt=False, guestExecuted=False, legacyMetadataProjected=False,
        selectedManifestsMustBeDerivedFresh=True)
    write(root / 'composition.json', composition)
    summary = dict(schemaVersion=1, state='NEXT_PORTABLE_SOURCE_MATERIALIZED_V1', sourceOnly=True,
        compilerOrGuestExecuted=False, generatedBuildMetadataProjected=False, outputRoot=str(root),
        roleCounts=tiny['expectedCounts'], files=3, bytes=tiny['expectedBytes'],
        roleContentSha256=tiny['roleContentSha256'], composition=ref(root / 'composition.json'),
        inputs=[], filesCopied=copied)
    path = root / 'source-materialization.json'
    write(path, summary)
    valid = m.inspect_layout(ref(path), tiny)
    check(len(valid['physicalRecords']) == 3 and valid['priorCopySequenceObservedByPreparer'] is False)
    for change in [lambda s: s.update(engineBuilt=True, sourceOnly=False),
                   lambda s: s.update(state='OLD_COMPILED_METADATA'),
                   lambda s: s.update(roleContentSha256='0' * 64),
                   lambda s: s['filesCopied'][0].update(relativePath='../escape'),
                   lambda s: s['filesCopied'][0].update(role='invented'),
                   lambda s: s['filesCopied'].append(copy.deepcopy(s['filesCopied'][0])),
                   lambda s: s['filesCopied'][0]['source'].update(path=str(tmp / 'unrelated'))]:
        bad = copy.deepcopy(summary)
        change(bad)
        write(path, bad)
        refused(lambda: m.inspect_layout(ref(path), tiny))
    write(path, summary)
    p = root / 'source/sample.txt'
    p.chmod(0o644)
    refused(lambda: m.inspect_layout(ref(path), tiny))
    p.chmod(0o600)
    (root / 'unexpected').write_bytes(b'extra')
    refused(lambda: m.inspect_layout(ref(path), tiny))
    (root / 'unexpected').unlink()
    (root / 'empty-extra').mkdir()
    refused(lambda: m.inspect_layout(ref(path), tiny))
    (root / 'empty-extra').rmdir()
    alias = root / 'alias'
    alias.symlink_to(p)
    refused(lambda: m.inspect_layout(ref(path), tiny))
    alias.unlink()
    hard = tmp / 'hardlink'
    os.link(p, hard)
    refused(lambda: m.inspect_layout(ref(path), tiny))
    hard.unlink()

    # Relocated real CLI Source closure. No SDK/tools/app or materialized source
    # payloads are copied, and the child is Python reading Source/data only.
    relocated = tmp / 'relocated-repo'
    own_relative = HERE.relative_to(REPO)
    donor_relative = Path(policy['materializerIndex']['repositoryPath']).parent
    for relative in [own_relative, donor_relative]:
        shutil.copytree(REPO / relative, relocated / relative)
    command = [sys.executable, '-B', '-I', str(relocated / own_relative / 'prepare.py')]
    result = subprocess.run(command, capture_output=True)
    check(result.returncode == 0 and result.stderr == b'')
    decoded = json.loads(result.stdout)
    check(decoded['files'] == 825 and decoded['actualBuild'] is None and decoded['buildOrToolOrGuestInvoked'] is False)
    if args.materialization is not None:
        # Optional current real source-only preparation. Metadata JSON only is
        # written into disposable scratch; every source payload remains in place.
        prepared = tmp / 'fresh-preparation'
        argv = command + ['--materialization', str(args.materialization), '--output', str(prepared)]
        result = subprocess.run(argv, capture_output=True)
        check(result.returncode == 0 and result.stderr == b'')
        draft = json.loads((prepared / 'root-authority.unissued.json').read_text())
        check(draft['state'].startswith('UNISSUED_') and draft['buildAllowed'] is None
              and draft['installedGeneratorResult'] is None and draft['generatorNode'] is None)
        selection_ref = ref(prepared / 'portable-selection.json')
        selected = m.admit(selection_ref, policy, relocated)
        check(len(selected['files']) == 825 and len(selected['physicalRecords']) == 825)
        check(len(m.role_copies(selected, 'build-support')) == 387
              and len(draft['componentizeSources']) == 3 and len(draft['supportAdditions']) == 1)
        check(draft['supportAdditions'][0]['relativePath'] == 'runtime/crates/staticlib-template/Cargo.intl.toml.in')
        node = dict(path='/synthetic-node-not-executed', **policy['node'])
        generated = dict(schemaVersion=1, state='ACTUAL_PORTABLE_NEXT_INSTALLED_GENERATORS_CHECKED_V1',
            passed=True, sourceBeforeAfterUnchanged=True, nativeOrGuestExecuted=False,
            composition=selected['composition'], node=node, sourceRoot=selected['sourceRoot'],
            materializationSummary=selected['sourceMaterialization'], roleContentSha256=selected['roleContentSha256'],
            portableInputsPreserved=True, wholePortableBefore=selected['physicalRecords'],
            wholePortableAfter=selected['physicalRecords'], portableDirectoriesBefore=selected['directoryRecords'],
            portableDirectoriesAfter=selected['directoryRecords'], sourceFiles=435,
            sourceBefore=[r['source'] for r in m.role_copies(selected, 'native-policy-source')],
            sourceAfter=[r['source'] for r in m.role_copies(selected, 'native-policy-source')],
            commands=[dict(argv=a, rawExitCode=0, stderrSha256=hashlib.sha256(b'').hexdigest())
                      for a in m.generator_argv(policy, '/old-root/source', node)])
        refused(lambda: m.validate_generators(generated, selected, node, policy, selection_ref))
        bad = copy.deepcopy(generated)
        bad['composition']['sha256'] = '0' * 64
        refused(lambda: m.validate_generators(bad, selected, node, policy, selection_ref))
        bad = copy.deepcopy(generated)
        bad['wholePortableBefore'][0]['mode'] = 0o777
        refused(lambda: m.validate_generators(bad, selected, node, policy, selection_ref))
        refused(lambda: m.validate_generators(generated, selected, dict(node, sha256='0' * 64), policy, selection_ref))
        bad_record = json.loads((prepared / 'portable-selection.json').read_text())
        bad_record['physicalRecords'][0]['mode'] = 0o777
        altered = tmp / 'altered-selection.json'
        write(altered, bad_record)
        refused(lambda: m.admit(ref(altered), policy, relocated))

print(json.dumps(dict(state='PORTABLE_BUILD_ADMISSION_SOURCE_DATA_TESTS_PASSED_V1',
    checks=checks, syntheticLayoutsOnly=args.materialization is None,
    optionalRealMaterializedSourcePreparation=args.materialization is not None,
    relocatedSourceCliReadOnly=True,
    generatorsOrBuildToolsOrGuestExecuted=False, applicationOrSdkOrToolTreeCopied=False)))
