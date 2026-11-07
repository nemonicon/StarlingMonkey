"""Read-only by default. Explicit --output writes only fresh preparation JSON.
Never invokes materialization, generators, CMake, Cargo, compilers or a runtime.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True

HERE = Path(__file__).absolute().parent
REPO = HERE.parents[4]


def descriptor(path):
    p = Path(path)
    b = p.read_bytes()
    return dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))


def load():
    plan = json.loads((HERE / 'plan.json').read_bytes())
    expected = plan['portableAdmissionModule']
    actual = descriptor(HERE / 'portable.py')
    if any(actual[k] != expected[k] for k in ['sha256', 'bytes']):
        raise ValueError('Admission module changed')
    spec = importlib.util.spec_from_file_location('portable_next_build_source', HERE / 'portable.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, plan


def write_new(path, value):
    data = (json.dumps(value, indent=2) + '\n').encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fchmod(stream.fileno(), 0o600)
        os.fsync(stream.fileno())
    return descriptor(path)


def prepare(materialization=None, output=None):
    module, plan = load()
    policy = plan['portableSourcePolicy']
    summary = dict(schemaVersion=1, state='PORTABLE_BUILD_PREPARATION_SOURCE_ONLY_V1',
                   roleCounts=policy['expectedCounts'], files=policy['expectedFiles'],
                   roleContentSha256=policy['roleContentSha256'], buildOrToolOrGuestInvoked=False,
                   actualRootAuthority=None, actualGenerators=None, actualBuild=None,
                   buildStartBytes=plan['disk']['startBytes'], buildStopBytes=plan['disk']['stopBytes'],
                   outputRoot=None)
    refs = module.authenticate_policy(policy, REPO)
    if materialization is None:
        module.require(output is None, '--output requires --materialization')
        return summary
    materialization = module.canonical(materialization)
    ref = descriptor(materialization)
    selected = module.inspect_layout(ref, policy, refs)
    summary.update(state='PORTABLE_BUILD_INPUTS_AUTHENTICATED_NOT_BUILT_V1',
                   sourceMaterialization=ref, composition=selected['composition'],
                   freshPhysicalFiles=len(selected['physicalRecords']))
    if output is None:
        return summary
    # Own Source bytes are authenticated before publishing a usable draft.
    own_index = json.loads((HERE / 'index.json').read_bytes())
    own_files = {'index.json', *[r['path'] for r in own_index['files']]}
    module.require({str(q.relative_to(HERE)) for q in HERE.rglob('*') if q.is_file()} == own_files,
                   'Preparation Source membership changed')
    own_refs = [descriptor(HERE / 'index.json')]
    for r in own_index['files']:
        own_ref = dict(path=str(HERE / module.relative(r['path'])), sha256=r['sha256'], bytes=r['bytes'])
        module.file_row(own_ref['path'], own_ref)
        own_refs.append(own_ref)
    output = Path(output)
    module.require(output.is_absolute() and '..' not in output.parts and not output.exists()
                   and not output.is_symlink(), 'Fresh canonical absolute output required')
    module.canonical(output.parent)
    module.require(output.resolve() == output, 'Output alias')
    input_root = Path(selected['sourceRoot']).parent
    module.require(not (output == REPO or REPO in output.parents or output == input_root
                        or input_root in output.parents or output in input_root.parents),
                   'Preparation output must be disjoint from checkout and materialized inputs')
    output.mkdir(mode=0o700)
    selection_ref = write_new(output / 'portable-selection.json', selected)
    draft = json.loads((HERE / 'root-authority.template.json').read_bytes())
    draft.update(entry=descriptor(HERE / 'run.py'), plan=descriptor(HERE / 'plan.json'),
                 callerIndex=descriptor(HERE / 'index.json'), composition=selected['composition'],
                 portableSelection=selection_ref,
                 componentizeSources=module.role_copies(selected, 'componentize-embedding'),
                 supportAdditions=[r for r in module.role_copies(selected, 'build-support')
                                   if r['relativePath'] == 'runtime/crates/staticlib-template/Cargo.intl.toml.in'])
    # This remains UNISSUED: no tools, generator result, work root or action grant.
    draft_ref = write_new(output / 'root-authority.unissued.json', draft)
    receipt_template = dict(schemaVersion=1, state='UNISSUED_PORTABLE_GENERATOR_RECEIPT_TEMPLATE_V1',
                            composition=selected['composition'], node=None, passed=None,
                            sourceRoot=selected['sourceRoot'], materializationSummary=ref,
                            roleContentSha256=selected['roleContentSha256'],
                            rootAuthority=None, sourceIndex=None, plan=None,
                            sourceFiles=policy['expectedCounts']['native-policy-source'],
                            sourceBefore=None, sourceAfter=None, sourceBeforeAfterUnchanged=None,
                            wholePortableBefore=None, wholePortableAfter=None,
                            portableDirectoriesBefore=None, portableDirectoriesAfter=None,
                            portableInputsPreserved=None,
                            nativeOrGuestExecuted=False, commands=None,
                            actualGeneratorAction=None,
                            plannedArgvOnly=module.generator_argv(policy, selected['sourceRoot'],
                                                                 dict(path='$PINNED_NODE_22_14')))
    generator_ref = write_new(output / 'generator-receipt.template.json', receipt_template)
    # Final read-only verification is separate from publication. On failure the
    # partial preparation is retained; it is never a build or granted action.
    actual = module.inspect_layout(ref, policy, module.authenticate_policy(policy, REPO))
    module.require(actual == selected, 'Inputs changed during preparation')
    for own_ref in own_refs:
        module.file_row(own_ref['path'], own_ref)
    summary.update(outputRoot=str(output), portableSelection=selection_ref,
                   unissuedAuthority=draft_ref, generatorReceiptTemplate=generator_ref,
                   originalInputsPreserved=True)
    write_new(output / 'preparation.json', summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--materialization', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.materialization, args.output), indent=2))


if __name__ == '__main__':
    main()
