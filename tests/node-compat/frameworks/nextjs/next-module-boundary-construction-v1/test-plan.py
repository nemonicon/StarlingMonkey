"""Inert plan and genuine metadata DATA checks; no constructor/API/tool import."""
from pathlib import Path
import argparse
import ast
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'next-entry-fixes-construction-v6'
FULL = 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1'
DELTAS = {'state', 'priorCallerSourceIndex', 'nodeWorkingDirectory', 'outputPrefix',
          'inputDelta', 'metadata', 'expectedEngineForRootAuthority',
          'expectedNativeMetadataForRootAuthority'}


def row(path):
    path = Path(path); raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def full_shape(v):
    return (v.get('metadataKind') == FULL
            and all(type(v.get(k)) is int and v[k] == n for k, n in [
                ('schemaVersion', 1), ('nativePolicyInputCount', 435),
                ('buildSupportInputCount', 387), ('embeddingInputCount', 3)])
            and type(v.get('actualCompileRows')) is list and len(v['actualCompileRows']) == 80
            and type(v.get('actualSeparateEmbeddingCompileRows')) is list
            and len(v['actualSeparateEmbeddingCompileRows']) == 1)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--metadata', help='Optional genuine selected metadata, read only as DATA')
    args = cli.parse_args(); checks = 0

    def need(value, reason):
        nonlocal checks
        assert value is True, reason
        checks += 1

    p = json.loads((HERE / 'plan.json').read_bytes())
    old = json.loads((PARENT / 'plan.json').read_bytes())
    need(set(p) == set(old), 'No invented plan API fields')
    need({k for k in p if p[k] != old[k]} == DELTAS, 'Eight declared plan deltas')
    for name in ['run.py', 'entry.mjs', 'capture.mjs']:
        need((HERE / name).read_bytes() == (PARENT / name).read_bytes(), name + ' exact V6 bytes')
    need(p['priorCallerSourceIndex'] == row(PARENT / 'index.json'), 'Genuine V6 ancestry')
    need(p['nodeWorkingDirectory'] == str(HERE), 'Own held caller cwd')
    need(p['outputPrefix'] == '/private/tmp/starling-node-compat/next-module-boundary-component-v1', 'Fresh fixed output prefix')
    need(p['nativeMetadataKindRequiredInRootFixedValues'] == FULL, 'Existing full kind requirement')
    for name in ['engine', 'nativeMetadata', 'actualRootAuthority', 'actualComponent',
                 'actualRuntime', 'expectedNativeMetadataFixedValuesForRootAuthority']:
        need(p[name] is None, 'No operational binding: ' + name)
    for name in ['pins', 'packageRoot', 'packageInventory', 'inputSourceIndex', 'entries',
                 'witDirectory', 'worldSourceIndex', 'worldName', 'selectedInterfaces',
                 'toolParserPreopens', 'api', 'componentizeNodeCapSeconds', 'dataToolCapSeconds',
                 'noOrdinaryGuestExecution', 'noProductionProfilePromotion']:
        need(p[name] == old[name], name + ' unchanged')
    need(len(set(p['selectedInterfaces'])) == len(p['selectedInterfaces']) == 13
         and all(v.endswith('@0.2.10') for v in p['selectedInterfaces']), 'Exact13 selected standard interfaces')
    need(p['toolParserPreopens'] == {p['witDirectory']: p['witDirectory']}, 'Only official WIT parser preopen')
    need(p['expectedEngineForRootAuthority']['sha256'] == 'ca84baa11cf88bd6c6aa96b2806df05baef11f9ba89edb5f6dc5c66e0d035eb7'
         and p['expectedEngineForRootAuthority']['bytes'] == 31326382, 'Genuine new reported engine selection')
    need(p['expectedNativeMetadataForRootAuthority']['sha256'] == 'e674f7d2eebefd9f7885589344c9bf04e71e599ecf6ec1dfdea75ba7cee7ecbd'
         and p['expectedNativeMetadataForRootAuthority']['bytes'] == 4839816, 'Genuine new reported metadata selection')
    model = dict(schemaVersion=1, metadataKind=FULL, nativePolicyInputCount=435,
                 buildSupportInputCount=387, embeddingInputCount=3,
                 actualCompileRows=[{}]*80, actualSeparateEmbeddingCompileRows=[{}])
    need(full_shape(model), 'Full arrays prospective Root rule')
    for key, value in [('metadataKind', 'EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1'),
                       ('schemaVersion', True), ('actualCompileRows', 80),
                       ('actualSeparateEmbeddingCompileRows', 1)]:
        changed = copy.deepcopy(model); changed[key] = value
        need(not full_shape(changed), 'Reject wrong full shape: ' + key)
    actual = None
    if args.metadata:
        path = Path(args.metadata)
        need(path.is_absolute() and path.resolve() == path, 'Canonical genuine DATA path')
        before = row(path)
        need(before == p['expectedNativeMetadataForRootAuthority'], 'Exact selected genuine metadata bytes')
        v = json.loads(path.read_bytes())
        need(full_shape(v), 'Actual80 native TUs plus separate embedding arrays')
        guards = [r for r in v['nativePolicyInputManifest'] if r['path'] == 'runtime/script_loader.cpp']
        need(len(guards) == 1 and guards[0]['sha256'] == 'fbc1d13eebc66d20b01b1828008f3918609752e060320dbd16837722d4216ab8'
             and guards[0]['bytes'] == 22292, 'Guard-only loader selected; interop prototype absent')
        need(v['engine'] == p['expectedEngineForRootAuthority'], 'Genuine metadata engine joins prospective pin')
        need(row(path) == before, 'Original metadata unchanged')
        actual = dict(metadata=before, dataOnly=True, independentBuildReviewAccepted=False,
                      actualConstructorOrEngineInvoked=False)
    for path in HERE.glob('*.py'):
        ast.parse(path.read_bytes())
    print(json.dumps(dict(sourceOnly=True, passed=True, checks=checks,
        genuineMetadataData=actual, constructorOrApiOrMonitorOrEngineInvoked=False,
        rootAuthorityIssued=False, actualComponent=None, actualRuntime=None)))


if __name__ == '__main__':
    main()
