#!/usr/bin/env python3
"""Read-only V2 admission for unchanged V1 Cargo-source receipts; Python>=3.11."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import stat

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]


def need(value, message):
    if not value:
        raise ValueError(message)


def checked(path, expected=None):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path, 'canonical source file')
    before = path.stat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= 2 * 1024**2,
         'bounded unaliased source file')
    raw = path.read_bytes()
    after = path.stat()
    identity = lambda s: dict(dev=s.st_dev, ino=s.st_ino, mode=stat.S_IMODE(s.st_mode), nlink=s.st_nlink,
                              bytes=s.st_size, mtimeNs=s.st_mtime_ns, ctimeNs=s.st_ctime_ns)
    need(identity(before) == identity(after), 'source file changed while reading')
    row = dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw), physical=identity(before))
    if expected is not None:
        need(all(row[k] == expected[k] for k in ('sha256', 'bytes')), 'source descriptor')
    return raw, row


def family(root, expected=None):
    raw, index_row = checked(root / 'index.json', expected)
    index = json.loads(raw)
    members = {r['path']: r for r in index['files']}
    need(len(members) == len(index['files']) and
         {p.name for p in root.iterdir()} == set(members) | {'index.json'}, 'complete Source family')
    rows = [index_row]
    for name, ref in members.items():
        need(PurePosixPath(name).name == name and name not in ('', '.', '..', 'index.json'), 'flat source member')
        rows.append(checked(root / name, ref)[1])
    return index, rows


def context():
    own, own_rows = family(HERE)
    need(own['state'] == 'NATIVE_CARGO_RESTORE_ADMISSION_SOURCE_ONLY_V2', 'admission family state')
    plan = json.loads((HERE / 'plan.json').read_text())
    need(plan['state'] == 'READ_ONLY_LOCKED_CARGO_RESTORE_ADMISSION_V2' and
         plan['stableRootIdentityFields'] == ['dev', 'ino', 'mode'], 'fixed V2 policy')
    producer_ref = plan['producerSourceIndex']
    producer_path = PurePosixPath(producer_ref['path'])
    need(not producer_path.is_absolute() and '..' not in producer_path.parts, 'repo-relative producer')
    producer_root = (REPO / producer_path).parent
    producer_index, producer_rows = family(producer_root, producer_ref)
    need(producer_index['state'] == 'NATIVE_CARGO_RESTORE_SOURCE_ONLY_V1', 'original producer state')
    entry = plan['producerEntry']
    need(REPO / entry['path'] == producer_root / 'restore.py', 'original producer entry')
    checked(producer_root / 'restore.py', entry)
    spec = importlib.util.spec_from_file_location('held_cargo_restore_producer_v1', producer_root / 'restore.py')
    producer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)
    # Genuine API calls retain the original module's own HERE/REPO context.
    # No rebinding, patching or replacement of producer functions/globals.
    catalog = producer.load_catalog()
    return producer, catalog, plan, own_rows + producer_rows


def stable_root_identity(current, recorded):
    need(set(recorded) == {'dev', 'ino', 'mode', 'nlink'} and
         all(type(recorded[k]) is int for k in recorded) and
         type(current['nlink']) is int and recorded['nlink'] >= 1 and current['nlink'] >= 1,
         'root observation types')
    need(current['mode'] == 0o700 and
         all(current[k] == recorded[k] for k in ('dev', 'ino', 'mode')), 'owned stable root identity')
    return dict(recordedPrePublicationNlink=recorded['nlink'], currentNlink=current['nlink'],
                crossPublicationNlinkCompared=False, currentFullRootRowGuardedWithinRead=True,
                linkCountsAreNotResourceOrTeardownProof=True)


def admit_restore(receipt_ref):
    """Current DATA consistency only; original V1 producer and receipt unchanged.

    Source/process execution evidence and future Cargo metadata remain separate.
    The sole ownership-policy correction is root nlink across publication.
    """
    p, c, plan, protected = context()
    raw, receipt_row = p.read_file(receipt_ref['path'], receipt_ref)
    value = json.loads(raw)
    need(value['schemaVersion'] == 1 and value['state'] == plan['producerReceiptState'] and
         value['passed'] is True and value['sourceOnly'] is True and
         value['cargoOrCompilerOrNetworkOrGuestExecuted'] is False and
         value['error'] is None and value['finalProtectionError'] is None and
         value.get('publicationError') is None and value['sourceProtection']['unchanged'] is True,
         'successful original source-only receipt required')
    need(all(value[k] is None for k in ('actualCargoMetadata', 'actualNativeBuild', 'actualEngine', 'actualRuntime')),
         'source receipt cannot claim Cargo/build/runtime')
    output = p.physical(value['outputRoot'])
    need(output / 'restore-result.json' == Path(receipt_ref['path']) and
         value['sourceIndex'] == p.plain_descriptor(c['protected'][0]), 'original receipt producer/root binding')
    dirs, rows, generated = p.payload_layout(c, output)
    rows.append(dict(path='restore-result.json', sha256=p.sha(raw), bytes=len(raw), mode=0o600))
    current = p.tree(output, rows, dirs, exact_modes=True)
    fresh = [r for r in current if r['path'] not in (str(output), str(output / 'restore-result.json'))]
    need(json.dumps(fresh, sort_keys=True) == json.dumps(value['freshPhysicalRecords'], sort_keys=True),
         'fresh physical identity/mode/content records')
    root = next(r for r in current if r['path'] == str(output))
    root_observation = stable_root_identity(root['physical'], value['ownedRootIdentity'])
    need(value['sourcePayloadFiles'] == 3502 and value['generatedFiles'] == 4 and
         value['lockSha256'] == c['manifest']['lockSha256'] and
         value['logicalPayloadBytes'] == sum(r['bytes'] for r in rows if r['path'] != 'restore-result.json') and
         sum(r['bytes'] for r in rows) <= c['manifest']['policy']['maximumAcceptedOutputBytes'], 'receipt counts/cap')
    original_bookends = p.recorded_bookends(c, value)
    current_files = {r['path']: r for r in current if r.get('kind') == 'file'}
    lock_descriptor = p.plain_descriptor(current_files[str(output / 'project/Cargo.lock')])
    config_descriptor = p.plain_descriptor(current_files[str(output / 'offline-cargo/config.toml')])
    admission_index = p.plain_descriptor(protected[0])
    # Current root nlink remains in this full within-read guard. Only the
    # historical pre-publication comparison is removed; no post-guard I/O.
    p.guard_sources(current + original_bookends + c['protected'] + protected + [receipt_row])
    return dict(schemaVersion=1, state='RESTORED_CARGO_SOURCE_DATA_CONSISTENT_V2', dataConsistent=True,
                sourceIndex=value['sourceIndex'], admissionSourceIndex=admission_index,
                receipt=p.plain_descriptor(receipt_row), root=str(output),
                intlLockfile=lock_descriptor, offlineCargoConfig=config_descriptor,
                baseRoot=str(output / 'sources/base'), firefoxRoot=str(output / 'sources/firefox'),
                vendorRoot=str(output / 'vendor'), physicalRecords=current,
                rootLinkCountObservation=root_observation, actualCargoMetadata=None,
                nativeBuildOrGuestExecutionProved=False, sourceProcessExecutionAttested=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', action='store_true', help='read-only default; no restored-tree read')
    parser.add_argument('--receipt', type=Path, help='explicit JSON descriptor for an original V1 receipt')
    args = parser.parse_args()
    need(not (args.plan and args.receipt), 'choose plan or explicit receipt descriptor')
    if args.receipt is None:
        p, c, plan, protected = context()
        p.guard_sources(c['protected'] + protected)
        print(json.dumps(dict(state=plan['state'], sourceOnlyReader=True,
                              producerSourceIndex=plan['producerSourceIndex'], stableRootIdentityFields=['dev', 'ino', 'mode'],
                              actualCargoMetadata=None, newRestorationExecuted=False), indent=2))
    else:
        ref = json.loads(checked(args.receipt)[0])
        result = admit_restore(ref)
        print(json.dumps({k: result[k] for k in ('state', 'dataConsistent', 'sourceIndex', 'admissionSourceIndex',
                                               'receipt', 'rootLinkCountObservation', 'actualCargoMetadata',
                                               'sourceProcessExecutionAttested')}, indent=2))


if __name__ == '__main__':
    main()
