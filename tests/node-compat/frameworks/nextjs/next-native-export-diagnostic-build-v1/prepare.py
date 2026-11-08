"""Read-only by default; explicit --output writes unissued preparation JSON only.
No source copy, Cargo, generator, CMake, compiler, engine or guest invocation.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]


def need(value, message):
    if not value:
        raise ValueError(message)


def descriptor(path):
    path = Path(path)
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def canonical(path, exists=True):
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts and path.resolve(strict=exists) == path,
         'Canonical absolute path without aliases required')
    return path


def own_family():
    canonical(HERE / 'index.json')
    need((HERE / 'index.json').is_file() and (HERE / 'index.json').stat().st_nlink == 1,
         'Regular independent Source index')
    index_ref = descriptor(HERE / 'index.json')
    index = json.loads((HERE / 'index.json').read_text())
    expected = {r['path']: r for r in index['files']}
    need(len(expected) == len(index['files']) and
         {p.name for p in HERE.iterdir()} == set(expected) | {'index.json'}, 'Own Source membership')
    refs = [index_ref]
    for name, row in expected.items():
        need(Path(name).name == name and name not in ('', '.', '..', 'index.json'), 'Flat Source member')
        path = canonical(HERE / name)
        need(path.is_file() and path.stat().st_nlink == 1, 'Regular independent Source member')
        ref = descriptor(path)
        need(all(ref[k] == row[k] for k in ('sha256', 'bytes')), 'Own Source bytes')
        refs.append(ref)
    return refs


def load():
    plan = json.loads((HERE / 'plan.json').read_text())
    need(plan['prospectiveSourceBindingsPending'] is False, 'Unbound diagnostic build Source')
    need(plan['actionsAllowed'] is False and plan['state'] ==
         'DORMANT_PORTABLE_SOURCE_AND_CARGO_NEXT_INTL_NATIVE_BUILD_PLAN_V3', 'Unissued Source plan')
    need(descriptor(Path(sys.executable).resolve()) == plan['wrapperPython'], 'Pinned wrapperPython3.11 required')
    own_refs = own_family()
    run_ref = descriptor(HERE / 'run.py')
    spec = importlib.util.spec_from_file_location('genuine_portable_build_v3_source', HERE / 'run.py')
    run = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run)
    run.check_family(own_refs[0])
    external = plan['portableAdmissionSourceIndex']
    external_ref = dict(path=str(REPO / external['repositoryPath']), sha256=external['sha256'], bytes=external['bytes'])
    index = run.check_family(external_ref)
    member = plan['portableAdmissionModule']
    row = next(r for r in index['files'] if r['path'] == member['relativePath'])
    need(all(row[k] == member[k] for k in ('sha256', 'bytes')), 'External portable member')
    module = run.load_utility(dict(path=str(Path(external_ref['path']).parent / member['relativePath']),
                                  sha256=row['sha256'], bytes=row['bytes']), 'held_original_portable_source_admission')
    helper = plan['cargoAdmissionModule']
    cargo = run.load_utility(dict(path=str(HERE / helper['relativePath']), sha256=helper['sha256'],
                                 bytes=helper['bytes']), 'genuine_portable_cargo_source_admission')
    return plan, module, cargo, run, own_refs + [run_ref]


def write_new(path, value):
    raw = (json.dumps(value, indent=2) + '\n').encode()
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fchmod(stream.fileno(), 0o600)
        os.fsync(stream.fileno())
    need(path.stat().st_nlink == 1, 'Exclusive independent output')
    return descriptor(path)


def prepare(config_path=None, output=None):
    plan, portable, cargo, run, own_refs = load()
    summary = dict(schemaVersion=1, state='PORTABLE_SOURCE_CARGO_PREPARATION_READ_ONLY_V3',
                   sourceCounts=dict(native=435, support=387, embedding=3),
                   wrapperPython=plan['wrapperPython'], buildToolPythonUnchanged=True,
                   originalFullBuildStartBytes=plan['disk']['startBytes'],
                   originalFullBuildStopBytes=plan['disk']['stopBytes'],
                   sourceCopiesOrCommandsOrBuildOrGuestInvoked=False,
                   issuedAuthority=None, actualBuild=None, outputRoot=None)
    portable.authenticate_policy(plan['portableSourcePolicy'], REPO)
    if config_path is None:
        need(output is None, '--output requires explicit --config')
        return summary
    config_path = canonical(config_path)
    need(config_path.is_file() and config_path.stat().st_nlink == 1 and
         config_path.stat().st_size <= 65536, 'Small regular independent late config')
    config_ref = descriptor(config_path)
    config = json.loads(config_path.read_text())
    need(set(config) == {'portableSelection', 'cargoMetadataResult', 'cargo', 'rustc'}, 'Exact late preparation config roles')
    selected = portable.admit(config['portableSelection'], plan['portableSourcePolicy'], REPO)
    tools = {k: config[k] for k in ('cargo', 'rustc')}
    admitted = cargo.inspect(config['cargoMetadataResult'], selected, tools, plan['portableCargoPolicy'], REPO)
    summary.update(state='PORTABLE_SOURCE_CARGO_INPUTS_AUTHENTICATED_UNISSUED_V3',
                   preparationConfig=config_ref, portableSelection=config['portableSelection'],
                   composition=selected['composition'], actualCargoMetadataResult=config['cargoMetadataResult'],
                   currentCargoSourcesAdmitted=True)
    if output is None:
        need(descriptor(config_path) == config_ref, 'Config changed')
        for ref in own_refs:
            run.checked(ref)
        return summary
    output = canonical(output, exists=False)
    need(not output.exists() and output.parent.is_dir(), 'Fresh preparation output')
    source_root = Path(selected['sourceRoot']).parent
    protected_roots = [REPO, source_root, Path(admitted['intlLockfile']['path']).parent.parent]
    need(all(output != root and output not in root.parents and root not in output.parents
             for root in protected_roots), 'Preparation output disjoint from Source/inputs')
    output.mkdir(mode=0o700)
    # The helper exclusively owns this nested three-JSON namespace. Root-level
    # unissued draft/receipt do not weaken its strict membership admission.
    prepared = cargo.prepare(config['cargoMetadataResult'], selected, tools, plan['portableCargoPolicy'],
                             REPO, output=output / 'cargo')
    cargo_ref = prepared['portableCargoSelection']
    current = cargo.admit(cargo_ref, selected, tools, plan['portableCargoPolicy'], REPO)
    draft = json.loads((HERE / 'root-authority.template.json').read_text())
    draft.update(entry=descriptor(HERE / 'run.py'), plan=descriptor(HERE / 'plan.json'), callerIndex=own_refs[0],
                 composition=selected['composition'], portableSelection=config['portableSelection'],
                 portableCargoSelection=cargo_ref, wrapperPython=plan['wrapperPython'],
                 componentizeSources=portable.role_copies(selected, 'componentize-embedding'),
                 supportAdditions=[r for r in portable.role_copies(selected, 'build-support')
                                  if r['relativePath'] == 'runtime/crates/staticlib-template/Cargo.intl.toml.in'],
                 cargo=config['cargo'], rustc=config['rustc'],
                 intlLockfile=current['intlLockfile'], offlineCargoConfig=current['offlineCargoConfig'],
                 intlCargoAudit=current['intlCargoAudit'], reusedTrees=current['reusedTrees'])
    need(draft['configureAllowed'] is draft['buildAllowed'] is None and
         draft['workRoot'] is None and draft['installedGeneratorResult'] is None,
         'Draft remains unissued with other late roles null')
    draft_ref = write_new(output / 'root-authority.unissued.json', draft)
    after_source = portable.admit(config['portableSelection'], plan['portableSourcePolicy'], REPO)
    after_cargo = cargo.admit(cargo_ref, after_source, tools, plan['portableCargoPolicy'], REPO)
    need(selected == after_source and current == after_cargo and descriptor(config_path) == config_ref,
         'Source/config/Cargo physical inputs changed during preparation')
    for ref in own_refs:
        run.checked(ref)
    summary.update(outputRoot=str(output), portableCargoSelection=cargo_ref,
                   unissuedAuthority=draft_ref, originalInputsPreserved=True)
    write_new(output / 'preparation.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.config, args.output), indent=2))


if __name__ == '__main__':
    main()
