"""Benign synthetic source/metadata fixtures; NO Cargo or executable invocation."""
from pathlib import Path
import ast
import importlib.util
import json
import os
import tempfile
import tomllib
import copy

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
COMPANION = REPO/'docs/node-compat/nextjs-intl-build-plan'
spec = importlib.util.spec_from_file_location('inert_intl_resolver_source', HERE/'resolve-aggregate-v2.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cases = []
def need(ok, label):
    assert ok, label
    cases.append(label)
def rejected(call, label):
    try:
        call()
    except (AssertionError, FileNotFoundError):
        cases.append(label)
    else:
        raise AssertionError('Accepted '+label)
with tempfile.TemporaryDirectory(prefix='intl-resolver-v2-source-test-') as temp:
    root = Path(temp).resolve()
    base, ffi = root/'base', root/'ffi'
    for name, rel in module.BASE.items():
        p=base/rel; (p/'src').mkdir(parents=True)
        (p/'Cargo.toml').write_text('[package]\nname='+json.dumps(name)+'\nversion="0.1.0"\nedition="2021"\n')
        (p/'src/lib.rs').write_text('// SYNTHETIC SOURCE DATA: never compiled.\n')
    for rel, name, version in [(module.FFI[0],'icu_capi','2.0.0'),(module.FFI[1],'icu_segmenter_data','2.0.0'),
                               (module.FFI[2],'unicode-bidi-ffi','0.1.0'),(module.FFI[3],'unicode-bidi','0.3.15')]:
        p=ffi/rel;(p/'src').mkdir(parents=True)
        (p/'Cargo.toml').write_text('[package]\nname='+json.dumps(name)+'\nversion='+json.dumps(version)+'\nedition="2021"\n')
        (p/'src/lib.rs').write_text('// SYNTHETIC SOURCE DATA: never compiled.\n')
    ffi_manifest=dict(commit=module.COMMIT,state='EXACT_FOUR_FFI_SOURCE_TREES_FETCHED_AND_HASH_VERIFIED_NO_EXECUTION',
                      privateRoot=str(ffi),files=module.inventory(ffi,module.FFI),syntheticFixture=True)
    base_manifest=dict(files=module.inventory(base,module.BASE.values()),syntheticFixture=True)
    (root/'ffi.json').write_text(json.dumps(ffi_manifest));(root/'base.json').write_text(json.dumps(base_manifest))
    for name in ('cargo','rustc'):
        p=root/name;p.write_text('INERT TEST DATA; NEVER EXECUTED\n');p.chmod(0o700)
    config=dict(work=str(root/'work'),ffiSourceRoot=str(ffi),ffiManifest=module.digest(root/'ffi.json'),
                baseSourceRoot=str(base),baseManifest=module.digest(root/'base.json'),
                oldAggregateLock=module.digest(COMPANION/'inputs/current/actual-aggregate-Cargo.lock'),
                forkConstraints=module.digest(COMPANION/'lock-constraints.json'),
                cargo=module.digest(root/'cargo'),rustc=module.digest(root/'rustc'),locale='C',path=[str(root)])
    (root/'config.json').write_text(json.dumps(config));config_row=module.digest(root/'config.json')
    plan=module.prepare(config,config_row);work=Path(config['work'])
    manifest=tomllib.loads((work/'project/Cargo.toml').read_text())
    need(set(manifest['dependencies'])==set(module.BASE)|{'icu_capi','unicode-bidi-ffi'},'Only four old and two new dependencies')
    need(manifest['dependencies']['icu_capi']['default-features'] is False,'CAPI defaults suppressed')
    need(manifest['dependencies']['icu_capi']['features']==module.FEATURES,'Exact four CAPI features')
    need(manifest['lib']['crate-type']==['staticlib'],'One Rust staticlib output')
    need(manifest['patch']['crates-io']['unicode-bidi']['rev']==module.REV,'Exact patched Bidi revision')
    need(plan['seedIsResolvedLock'] is False and plan['actualCombinedLock'] is None,'No fabricated combined lock')
    need(plan['inputConfig']==config_row and plan['helperSource']==module.digest(HERE/'resolve-aggregate-v2.py'),'Config and actual helper identities retained')
    need(all(c['environment']['HOME']==os.environ['HOME'] for c in plan['commands']),'HOME preserved unchanged')
    need(not(work/'home').exists(),'No replacement HOME created')
    need(len(plan['commands'])==3 and all('build'not in c['argv'] and 'check'not in c['argv'] for c in plan['commands']),'Only metadata/vendor commands planned')
    need(plan['commands'][0]['environment']['CARGO_HOME']!=plan['commands'][-1]['environment']['CARGO_HOME'],'Online and offline Cargo homes separate')
    need(plan['commands'][-1]['argv'][-2:]==['--offline','--locked'],'Actual offline locked command required')
    need(module.recheck(work)['sourceAndPreparedInputsUnchanged'] is True,'Original and exclusive copied sources rechecked')
    for p in (work/'sources').rglob('*'):
        if p.is_file():
            assert p.stat().st_mode & 0o777 == 0o600 and p.stat().st_nlink==1
    need(True,'Private copied regular files have exact mode600 and single links')
    seed=tomllib.loads((work/'project/Cargo.lock').read_text())
    root_row=next(r for r in seed['package'] if r['name']=='rust-staticlib')
    need(len(root_row['dependencies'])==6,'Seed root identifies six actual dependencies')
    old_keys={module.key(r) for r in tomllib.loads((work/'old-aggregate.lock').read_text())['package']}
    seed_keys={module.key(r) for r in seed['package']}
    need(old_keys <= seed_keys,'All49 old identities survive reconciliation')
    for name, (_, version) in module.RECONCILIATION.items():
        need({r['version'] for r in seed['package'] if r['name']==name}=={version},'One reviewed compatible version: '+name)
    need(not any(r['name']=='serde_core' for r in seed['package']),'Unreachable exact SerdeCore family pruned')
    serde=next(r for r in seed['package']if r['name']=='serde')
    need(any(d.startswith('serde_derive 1.0.218 ')for d in serde['dependencies']),'Old exact Serde/derive pair preserved')
    constraints=json.loads((work/'fork-lock-constraints.json').read_text())
    bad_fork=copy.deepcopy(constraints['conservativeUpstreamLockRows'])
    next(r for r in bad_fork if r['name']=='icu_capi')['dependencies'].append('serde_core 1.0.227')
    rejected(lambda:module.merged_seed(tomllib.loads((work/'old-aggregate.lock').read_text())['package'],bad_fork),'Reachable exact SerdeCore conflict refuses instead of rewriting its constraint')

    # Fabricated JSON below is explicitly test DATA, not a Cargo result/proof.
    packages=[]
    for i,row in enumerate(seed['package']):
        packages.append(dict(id='synthetic:'+str(i),name=row['name'],version=row['version'],source=row.get('source'),
                             dependencies=[dict(name=n)for n in module.BASE]+[dict(name='icu_capi'),dict(name='unicode-bidi-ffi')] if row['name']=='rust-staticlib' else [],
                             targets=[dict(crate_types=['staticlib'])] if row['name']=='rust-staticlib' else []))
    nodes=[dict(id=p['id'],features=module.FEATURES if p['name']=='icu_capi' else [],deps=[])for p in packages]
    metadata=dict(packages=packages,resolve=dict(root=next(p['id']for p in packages if p['name']=='rust-staticlib'),nodes=nodes),syntheticFixture=True)
    (work/'online-metadata.json').write_text(json.dumps(metadata))
    report=module.audit(work)
    need(report['dataConsistencyOnly'] and report['rootMustAuthenticateActualCargoTerminals'],'DATA audit cannot claim Cargo execution')
    need(report['lockPolicyPassed'] is True,'Conservative exact seed identities accepted as DATA only')
    original=(work/'project/Cargo.lock').read_bytes()
    with(work/'project/Cargo.lock').open('a')as out:
        out.write('\n[[package]]\nname="icu_calendar"\nversion="2.9.9"\nsource="registry+https://github.com/rust-lang/crates.io-index"\n')
    need(module.audit(work)['lockPolicyPassed'] is False,'New latest ICU identity refused')
    (work/'project/Cargo.lock').write_bytes(original)
    copied=work/'sources/base/crates/rust-hooks/src/lib.rs';old=copied.read_bytes();copied.write_bytes(b'changed')
    rejected(lambda:module.recheck(work),'Changed prepared source refused');copied.write_bytes(old)
    original_source=base/'crates/rust-hooks/src/lib.rs';old=original_source.read_bytes();original_source.write_bytes(b'changed')
    rejected(lambda:module.recheck(work),'Changed original source refused');original_source.write_bytes(old)
    rejected(lambda:module.prepare(config,config_row),'Existing work refused without overwrite')
    target=ffi/module.FFI[0]/'src/lib.rs';old=target.read_bytes();target.unlink();target.symlink_to(ffi/module.FFI[1]/'src/lib.rs')
    rejected(lambda:module.verify_tree(ffi,ffi_manifest['files'],module.FFI),'Symlink source refused');target.unlink();target.write_bytes(old)
    need(module.recheck(work)['sourceAndPreparedInputsUnchanged'] is True,'Restored benign fixtures pass final hashes')
    vendor=root/'vendor-test';v=vendor/'unicode-bidi-0.3.15';(v/'src').mkdir(parents=True)
    (v/'Cargo.toml').write_text('[package]\nname="unicode-bidi"\nversion="0.3.15"\n')
    (v/'src/lib.rs').write_text('// synthetic vendor checksum fixture\n')
    sums={str(p.relative_to(v)):module.digest(p)['sha256'] for p in v.rglob('*')if p.is_file()}
    (v/'.cargo-checksum.json').write_text(json.dumps(dict(package=None,files=sums)))
    bidi_row=next(r for r in seed['package']if r['name']=='unicode-bidi')
    need(module.vendor_checks(vendor,[bidi_row])['allRecordedChecksumsMatch'],'Whole vendor checksum/lock coverage model')
    (v/'src/lib.rs').write_text('tampered')
    rejected(lambda:module.vendor_checks(vendor,[bidi_row]),'Tampered vendor source refused')
ast.parse((HERE/'resolve-aggregate-v2.py').read_text())
need(True,'Helper AST parses')
decision=json.loads((HERE/'cargo-seed-reconciliation-v2.json').read_text())
def allows(requirement, version):
    value=tuple(map(int,version.split('.')))
    if requirement.startswith('='):
        return value==tuple(map(int,requirement[1:].split('.')))
    if requirement.startswith('>='):
        lower=tuple(map(int,requirement[2:].split('.')));return value>=lower+(0,)*(3-len(lower))
    lower=tuple(map(int,requirement.lstrip('^').split('.')));lower=lower+(0,)*(3-len(lower))
    upper=(lower[0]+1,0,0) if lower[0] else (0,lower[1]+1,0) if lower[1] else (0,0,lower[2]+1)
    return lower<=value<upper
for row in decision['declaredRequirements']:
    allowed=allows(row['requirement'],module.RECONCILIATION[row['package']][1])
    if row['parent']=='serde_core':
        need(not allowed and row['requirement']=='=1.0.227','Exact SerdeCore requirement is not falsely claimed compatible')
    else:
        need(allowed,'Selected old version meets declared '+row['parent']+' -> '+row['package']+' '+row['requirement'])
print(json.dumps(dict(passed=True,caseCount=len(cases),cases=cases,syntheticSourceAndMetadataOnly=True,
                     cargoOrNativeOrCompilerOrGuestInvoked=False,allTemporaryFixturesRemoved=True)))
