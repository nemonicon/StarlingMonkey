"""Independent source/hash/data reader. No candidate imports or action calls."""
import ast
import collections
import difflib
import hashlib
import json
import os
from pathlib import Path
import re

P = Path(__file__).resolve().parent
K = P.parent
D = K / 'ownership-component-candidate-v3'
SOURCE_SHA = '593a0e02239fcc3b66bfc35549b6c574c2aee8cb67a273c2d8aea9c7ce22c492'
seen = {}
checks = []

def need(value, label):
    if not value:
        raise AssertionError(label)
    checks.append(label)

def save(name, value):
    (P / name).write_text(json.dumps(value, indent=2) + '\n')

def file_row(path):
    path = Path(path)
    h = hashlib.sha256()
    size = 0
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
            size += len(block)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=size)

def verify(row, role):
    path = Path(row['path'])
    before = path.stat()
    need(not path.is_symlink() and path.is_file(), 'Ordinary input leaf: ' + str(path))
    actual = file_row(path)
    after = path.stat()
    need(all(actual[k] == row[k] for k in ['path', 'sha256', 'bytes']), 'Exact input: ' + str(path))
    need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) ==
         (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'Stable read: ' + str(path))
    if str(path) in seen:
        need(all(seen[str(path)][k] == row[k] for k in ['path', 'sha256', 'bytes']), 'Consistent duplicate: ' + str(path))
        seen[str(path)]['roles'].add(role)
    else:
        seen[str(path)] = dict(actual, roles={role})
    return actual

def data(row, role):
    verify(row, role)
    return json.loads(Path(row['path']).read_bytes())

def local(name):
    need(isinstance(name, str) and name and not name.startswith('/') and '\\' not in name and '\0' not in name and
         all(part not in ['', '.', '..'] for part in name.split('/')), 'Finite local source name')
    return name

def index(row, count=None):
    value = data(row, 'finite-index')
    need(value['schemaVersion'] == 1 and isinstance(value['files'], list), 'Finite indexed family')
    if count is not None:
        need(len(value['files']) == count, 'Exact indexed count ' + str(count))
    names = set()
    rows = []
    for r in value['files']:
        name = local(r['path'])
        need(name not in names, 'Unique source member ' + name)
        names.add(name)
        absolute = dict(path=str(Path(row['path']).parent / name), sha256=r['sha256'], bytes=r['bytes'])
        verify(absolute, 'indexed-member')
        rows.append(absolute)
    return value, rows

own_row = file_row(D / 'index.json')
need(own_row['sha256'] == SOURCE_SHA, 'Exact reviewed v3 source index')
own, own_rows = index(own_row, 25)
need({str(p.relative_to(D)) for p in D.rglob('*') if p.is_file()} ==
     {r['path'] for r in own['files']} | {'index.json'}, 'Exact physical v3 source membership')
freeze = data(next(r for r in own_rows if r['path'].endswith('/input-freeze.json')), 'preparation-seal')
need(len(freeze['files']) == 6825 and freeze['originalPreparationReferencesAreNotRelocated'] is True,
     '6825 original/configured/frozen references retain original contexts')
need(len({r['path'] for r in freeze['files']}) == 6825, 'Unique preparation paths')
for r in freeze['files']:
    verify(r, r['role'])

lineage = json.loads((D / 'lineage.json').read_bytes())
parent, parent_rows = index(lineage['previousSourceIndex'], 20)
donor, donor_rows = index(lineage['originalSourceIndex'], 28)
held, held_rows = index(lineage['sourceHold']['index'], 5)
held_result = data(lineage['sourceHold']['result'], 'preserved-context-HOLD')
need(held_result['sourceReviewPassed'] is False and held_result['adapterFindingM1Resolved'] is True,
     'V2 M2 HOLD and resolved adapter finding stay historical')

deriv = json.loads((D / 'source-derivations.json').read_bytes())
g = deriv['guard']
verify(g['origin'], 'guard-parent')
before = Path(g['origin']['path']).read_text()
after = before
need(len(g['edits']) == 12, 'Exactly twelve v3 guard edits')
for e in g['edits']:
    need(after.count(e['old']) == 1 and after.index(e['old']) == e['afterOffsetAtEdit'], 'Exact singleton forward edit')
    at = e['afterOffsetAtEdit']
    after = after[:at] + e['new'] + after[at + len(e['old']):]
need(after == (D / 'guard.mjs').read_text(), 'Forward guard afterimage exact')
reverse = after
for e in reversed(g['edits']):
    at = e['afterOffsetAtEdit']
    need(reverse[at:at + len(e['new'])] == e['new'], 'Exact reverse edit segment')
    reverse = reverse[:at] + e['old'] + reverse[at + len(e['new']):]
need(reverse == before, 'Guard reversal recovers immutable v2')
need(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                fromfile='a/guard.mjs', tofile='b/guard.mjs')) ==
     (D / 'configured-bootstrap.UNAPPLIED.patch').read_text(), 'Patch is exact guard difference')
for r in deriv['unchangedCopies']:
    verify(r['origin'], 'unchanged-v2-copy')
    need(Path(r['origin']['path']).read_bytes() == (D / r['afterimage']).read_bytes(), 'Unchanged v2 ' + r['afterimage'])

prereq = json.loads((K / 'ownership-component-candidate-v1/prerequisites.json').read_bytes())
c = json.loads((D / 'bootstrap-context.json').read_bytes())
proof_index, proof_rows = index(c['actualBootstrapReview']['index'], 32)
proof = data(c['actualBootstrapReview']['result'], 'actual-read-only-bootstrap-result')
contract = data(c['actualContract'], 'actual-two-context-contract')
frame = data(c['actualFrame'], 'actual-retained-full-frame')
need(sum(r == c['actualContract'] for r in proof_rows) == 1, 'Stable actual contract indexed exactly once')
need(proof['state'] == contract['state'] == 'INDEPENDENT_CRYPTO_OWNER355_NORMAL_OFF_PIN_AND_JS_BOOTSTRAP_RESULTS_REVIEW_PASSED_V1' and
     proof['verifiedPassed'] is True and proof['configuredToolDependencyRowsRehashed'] == 922 and
     proof['otherVariantsNull'] is True and proof['positiveKeyOperationsInvoked'] is False,
     'Actual c3fb completed normal-only read-only proof retained')
need(contract['readOnlyBootstrapOnly'] is True and contract['futureComponentRootAuthority'] is None and
     contract['operationalAdmission'] is False and contract['runtimeAcceptanceClaim'] is False,
     'Actual read-only proof grants no component/operational approval')
need(contract['configuredSourceRoot'] == c['configuredSourceRoot'] == '/private/tmp/starling-node-compat/crypto-owner-source-v2' and
     contract['sourceRoot'] == c['sourceRoot'] == '/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze/source' and
     contract['contextsAreDistinct'] is True, 'Exact distinct configured/frozen path spellings')
for key, value in [('sourceIndex', prereq['nativeSourceIndex']), ('reviewedPins', prereq['reviewedNativePins']),
                   ('rootNativeReview', prereq['nativeRootReview']), ('independentNativeReview', prereq['nativeReview']),
                   ('actualJsBootstrapFrame', c['actualFrame']), ('configuredSourceIndex', c['configuredSourceIndex'])]:
    need(contract[key] == value, 'Authentic actual contract provenance ' + key)

configured, configured_rows = index(c['configuredSourceIndex'], 44)
configured_names = {r['path']: r for r in configured_rows}
for name in ['configuredBootstrapEntry', 'configuredToolPins', 'configuredPolicy']:
    need(configured_names.get(c[name]['path']) == c[name], 'Configured indexed role ' + name)
need(c['configuredBootstrapEntry']['sha256'] == prereq['bootstrapEntry']['sha256'] and
     c['configuredBootstrapEntry']['bytes'] == prereq['bootstrapEntry']['bytes'] and
     c['configuredBootstrapEntry']['path'] != prereq['bootstrapEntry']['path'], 'Same source bytes, distinct executable locations')
root = Path(c['configuredSourceRoot'])
common = Path(c['configuredBootstrapEntry']['path']).parent / 'artifact_common.py'
old_common = Path(prereq['bootstrapEntry']['path']).parent / 'artifact_common.py'
need(common.parent.parents[4] == root and old_common.parent.parents[4] != root,
     'Actual Python __file__ derives staged355 rather than original repository')
need('REPO = HERE.parents[4]' in common.read_text(), 'Actual helper root derivation witnessed as source')
tools = data(c['configuredToolPins'], 'configured-tool-manifest')
policy = data(c['configuredPolicy'], 'configured-native-policy')
need(len(tools['toolDependencies']) == 922 and len(policy['expectedNativeSourceManifest']) == 355, 'Full tool922/native355 sets')
for r in tools['toolDependencies']:
    verify(dict(path=str(root / local(r['path'])), sha256=r['sha256'], bytes=r['bytes']), 'configured-tool922')
native_paths = []
for r in policy['expectedNativeSourceManifest']:
    native_paths.append(local(r['path']))
    for prefix in [root, Path(c['sourceRoot'])]:
        verify(dict(path=str(prefix / r['path']), sha256=r['sha256'], bytes=(prefix / r['path']).stat().st_size), 'configured-or-frozen-native355')
need(len(set(native_paths)) == 355 and
     [dict(path=r['path'], sha256=r['sha256']) for r in frame['metadata']['sourceManifest']] == policy['expectedNativeSourceManifest'],
     'Actual whole frame binds full355 policy without source projection')
need(frame['configuredSourceRoot'] == contract['configuredSourceRoot'] and frame['sourceRoot'] == contract['sourceRoot'] and
     frame['enginePath'] == contract['engine']['path'], 'Genuine retained frame exact context and engine spellings')
pin = data(prereq['reviewedNativePins'], 'genuine-reviewed-native-pins')
need(pin['variants']['normal-off'] == frame['pin'] and
     all(pin['variants'][v] is None for v in ['normal-runtime', 'gc-off', 'disabled-off']), 'Genuine normal36bd pin; other three NULL')
metadata = data(contract['metadata'], 'actual-native-metadata')
verify(contract['engine'], 'actual-native-engine')
need(frame['metadata'] == metadata and len(metadata['sourceManifest']) == 355,
     'Retained complete metadata equals actual frozen metadata')
for name in frame['selectedManifests']:
    need(isinstance(name, dict), 'Actual selected manifest is data')
need(len(frame['selectedManifests']) == 11, 'Eleven actual selected manifests retained')

# Existing publication and tooling are data roles, never old native admission.
map_row = next(r for r in donor_rows if r['path'].endswith('/packaging-context.json'))
pack = data(map_row, 'immutable-packaging-roles')
pub, pub_rows = index(pack['publicationIndex'])
need(pack['toolFiles'] == 4890 and pack['packagingFiles'] == 44 and len(pack['files']) == 4934 and len(pack['links']) == 22,
     'Complete 4934 packaging/tool roles and 22 declared links')
pub_by_name = {r['path']: r for r in pub['files']}
physical_files = set()
physical_links = set()
pack_rows = {}
for r in pack['files']:
    need(all(pub_by_name[r['path']][key] == r[key] for key in ['path', 'sha256', 'bytes', 'mode']),
         'Packaging digest/size/mode fields equal actual publication row')
    path = Path(pack['publicationRoot']) / local(r['path'])
    need(path.stat().st_nlink == 1 and (path.stat().st_mode & 0o7777) == r['mode'], 'Packaging ordinary inode/mode')
    rr = dict(path=str(path), sha256=r['sha256'], bytes=r['bytes'])
    verify(rr, 'packaging-role')
    pack_rows[str(path)] = rr
for prefix in pack['roleRoots']:
    for path in (Path(pack['publicationRoot']) / prefix).rglob('*'):
        if path.is_symlink():
            physical_links.add(str(path.relative_to(pack['publicationRoot'])))
        elif path.is_file():
            physical_files.add(str(path.relative_to(pack['publicationRoot'])))
need(physical_files == {r['path'] for r in pack['files']}, 'Exact physical packaging regular-file membership')
need(physical_links == {r['destination'] for r in pack['links']}, 'Exact physical tooling symlink membership')
for r in pack['links']:
    path = Path(pack['publicationRoot']) / r['destination']
    need(os.readlink(path) == r['newLinkText'] and path.resolve() == (Path(pack['publicationRoot']) / r['mappedTarget']), 'Exact declared link target')
for key in ['device', 'inode']:
    need(pack['rootIdentity'][key] == getattr(Path(pack['publicationRoot']).stat(), 'st_dev' if key == 'device' else 'st_ino'), 'Actual publication root ' + key)
adapter = next(r for r in pack_rows.values() if r['path'].endswith('/preview1-adapter-release/wasi_snapshot_preview1.wasm'))
need(adapter['sha256'] == '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0' and adapter['bytes'] == 53512,
     'Actual repository 53512-byte adapter; no npm fallback')

# Finite literal import inspection, not a general JavaScript parser claim.
allowed = {r['path'] for r in own_rows + donor_rows + parent_rows + configured_rows} | set(pack_rows)
edges = []
for source in [D / n for n in ['guard.mjs', 'bootstrap-context.mjs', 'build.mjs', 'build-worker.mjs']] + [
        K / 'ownership-component-candidate-v1' / n for n in ['authority.mjs', 'proofs.mjs', 'packaging.mjs', 'durable.mjs', 'durable-host.mjs', 'abi.mjs']]:
    for spec in re.findall(r"(?:from\s*|import\s*)['\"]([^'\"]+)['\"]", source.read_text()):
        if spec.startswith('.'):
            dest = str((source.parent / spec).resolve())
            need(dest in allowed, 'Physical literal source import in indexed closure ' + dest)
            edges.append(dict(source=str(source), specifier=spec, target=dest))
guard = (D / 'guard.mjs').read_text()
context = (D / 'bootstrap-context.mjs').read_text()
worker = (D / 'build-worker.mjs').read_text()
parent_text = (D / 'build.mjs').read_text()
need('import(pathToFileURL(configured.entry.path))' in guard and 'import(pathToFileURL(p.bootstrapEntry.path))' not in guard,
     'Only authenticated configured bootstrap entry dynamically imports')
need(guard.index('await configured.recheck()') < guard.index('import(pathToFileURL(configured.entry.path))') and
     guard.index('bootstrapEnvironment()') < guard.index('import(pathToFileURL(configured.entry.path))'), 'Complete context/environment guard before bootstrap import')
for literal in ["for(const key of ['PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE'])", 'for(const r of sourceRows)',
                'for(const r of toolRows)', 'for(const r of nativeRows)', "['metadata','pin','selectedManifests']"]:
    need(literal in context, 'Configured context complete authentication/recheck clause ' + literal)
need('configured.assertReturned(frame)' in guard and guard.count('configured.assertReturned(frame)') == 2,
     'Genuine full frame checked before return and after recheck')
need('workerOptions(d,packaging,wit)' in worker and 'componentOptions({engine:d.engine,adapter:packaging.adapter},wit)' in worker,
     'Actual options caller uses genuine packaging adapter')
need('componentOptions(d,wit)' not in worker and 'selected.componentize(source,options)' in worker,
     'Old missing-adapter call absent; actual selected API used')
need(parent_text.index("mkdir(join(output.root,'processes')") < parent_text.index('await runOwnedCommand'), 'Processes0700 created before durable lifecycle caller')
need(parent_text.index('await componentPreflight(options)') < parent_text.index('DurableOutput.create'), 'Full genuine preflight precedes outputs')
for token in ["checkOwnedTerminal(status)", "await frame.recheck();await output.recheck()", "2*1024*1024*1024", "800*1024*1024"]:
    need(token in parent_text, 'Finite ordinary parent lifecycle contract ' + token)
for token in ["await output.write('selected-return-transport.json'", "await output.write('transpile-return-transport.json'",
              'Array.isArray(result.interfaceAudit.emittedImports)&&result.interfaceAudit.emittedImports.length===0',
              'publicJSExports(toolchain.parseAst', 'await recheck();await output.recheck()', "Buffer.from('{\"type\":\"module\"}\\n')"]:
    need(token in worker, 'Component capture and ABI/source audit clause ' + token)
template = json.loads((D / 'future-component-authority.template.json').read_bytes())
need(template['state'] == 'ROOT_REVIEWED_CRYPTO_OWNER355_COMPONENT_BUILD_V3' and template['componentSourceIndexSha256'] is None and
     template['sourceIndependentReview'] is None and template['componentBuildAllowed'] is False and
     template['componentInitializationAllowed'] is False and template['actualBootstrapReview'] == c['actualBootstrapReview'] and
     template['actualBootstrapReviewGrantsComponentAuthority'] is False, 'New authority remains closed/NULL and separately pins read-only proof')
need(template['outputRoot'] == '/private/tmp/starling-node-compat/crypto-owner355-component-v3' and
     not Path(template['outputRoot']).exists(), 'Fresh v3 output absent at review')
for path in D.glob('*.py'):
    ast.parse(path.read_text(), filename=str(path))
stored = {name: json.loads((D / 'evidence' / name).read_bytes()) for name in ['context.stdout.log', 'options.stdout.log', 'source.stdout.log', 'syntax.json']}
need([stored[n]['checks'] for n in ['context.stdout.log', 'options.stdout.log', 'source.stdout.log']] == [25, 15, 1759],
     'Owner stored pure/source counts authenticated as data only')
need(len(stored['syntax.json']['records']) == 8 and stored['syntax.json']['noActionMainsExecuted'] is True, 'Stored parse-only record scope')

save('rehashed-inputs.json', dict(schemaVersion=1, files=[dict(r, roles=sorted(r['roles'])) for r in sorted(seen.values(), key=lambda v: v['path'])],
                               noOwnerImportsOrActions=True))
save('source-call-boundaries.json', dict(schemaVersion=1, literalSourceEdges=edges,
    configuredBootstrapEntry=c['configuredBootstrapEntry'], originalPreparationEntryDataOnly=prereq['bootstrapEntry'],
    configuredPythonCommon=str(common), originalPythonCommon=str(old_common),
    actualContexts=dict(configured=contract['configuredSourceRoot'], frozen=contract['sourceRoot']),
    actualFrameDescriptor=c['actualFrame'], authenticReadOnlyContract=c['actualContract'], adapter=adapter,
    guardedCallSequence=['private config/Root primitives', 'own25/donor28/parent20/source peer/native/guest/publication proofs',
      '4934 physical packaging roles and22 links/environment', 'c3fb/d1a59/actual frame/staged68b6 full44/tool922/native355 configured+frozen',
      'configured staged JS import and genuine named bootstrap', 'unaltered full returned contexts/metadata/pin/manifests',
      'parent exclusive outputs/processes0700/owned worker', 'selected componentization with genuine adapter',
      'full raw/artifact/ABI capture and final source/output rechecks'],
    sourceInspectionOnly=True, generalJavaScriptParserClaim=False))
result = dict(schemaVersion=1, state='INDEPENDENT_CRYPTO_OWNER355_COMPONENT_SOURCE_REVIEW_PASSED_V3',
    componentSourceIndexSha256=SOURCE_SHA, sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False,
    sourceIdentityAndClosureVerified=True, sourceMemberCount=25, preparationRowsRehashed=6825,
    originalDonorMembers=28, parentMembers=20, configuredSourceMembers=44, configuredToolDependencies=922,
    configuredNativeSources=355, frozenNativeSources=355, uniqueInputsRehashed=len(seen), guardAfterimages=1,
    exactReversibleGuardEdits=12, unchangedParentWorkerAndOptionsCopies=3,
    packagingRoleFiles=4934, packagingToolLinks=22, actualAdapter=adapter,
    actualBootstrapReviewIndexSha256=c['actualBootstrapReview']['index']['sha256'],
    actualBootstrapContractSha256=c['actualContract']['sha256'], actualReadOnlyFrameSha256=c['actualFrame']['sha256'],
    actualConfiguredSourceRoot=contract['configuredSourceRoot'], actualFrozenSourceRoot=contract['sourceRoot'],
    adapterM1Corrected=True, configuredBootstrapContextM2Corrected=True, sameHashOriginalEntryIsProvenanceDataOnly=True,
    fullReturnedMetadataPinAndSelectedManifestsPreserved=True, otherNativeVariantsRemainNull=True,
    expectedPublicScalarFunctions=['inspect', 'run', 'clear', 'validate'], expectedFinalImports=[],
    storedOwnerPureContextChecks=25, storedOwnerPureOptionsChecks=15, storedOwnerSourceChecks=1759, storedOwnerParseChecks=8,
    ownerChecksIndependentlyExecutedByThisReader=False, pythonAstParsedWithoutImports=True,
    allOldSourceAndHoldDescriptorsUnchanged=True, futureRootComponentAuthority=None,
    actualNewComponent=None, keyExportAuthority=None, operationalAdmission=False, runtimeAcceptanceClaim=False, timingAllowed=False,
    reviewerReadHashDataAndPureAstOnly=True, reviewerHelpersBootstrapPreflightComponentizerNodeJcoWorkerKeysCryptoGcGuestNativeHostActionsInvoked=False,
    concreteBlockers=[], sourceChecks=len(checks), limitations=[
      'Source approval is the exact construction-only V3 peer contract. New Root component authority is still required.',
      'c3fb is prior actual read-only pin/bootstrap evidence read as data; it is not repeated or promoted into component/key approval.',
      'The complete returned frame equality is a future guard requirement, not an observed V3 bootstrap call.',
      'No component construction, emitted ABI/glue/loading, ordinary async scalar or positive key/crypto behavior was executed or proved here.',
      'Native/guest/adapter/tool bytes are unchanged. No source, metadata or path-context projection was used.',
      'Strong application owners, BIGNUM/private-string/OpenSSL-copy/allocation/other-algorithm limits and future key transport requirements remain open.',
      'The literal-source graph inspection is finite and pinned-source-specific; it is not a general JavaScript parser.'])
save('results.json', result)
print(json.dumps(dict(state=result['state'], sourceMembers=25, preparationRows=6825, uniqueInputs=len(seen), sourceChecks=len(checks))))
