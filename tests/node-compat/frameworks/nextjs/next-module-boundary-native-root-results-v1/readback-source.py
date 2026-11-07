"""Independently rehash the finite825 copies and donors; no tools or writes."""
import collections
import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
ROOT = Path('/private/tmp/starling-node-compat/next-native-portable-source-v2-materialization-v1')
PRIOR = Path('/private/tmp/starling-node-compat/next-native-portable-source-v1-materialization-v1')


def checked(path):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1
    assert not path.is_symlink() and path.resolve() == path
    data = path.read_bytes()
    assert path.lstat() == before
    return data, before, dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    raw, _, summary_ref = checked(ROOT / 'source-materialization.json')
    now = json.loads(raw)
    old = json.loads(checked(PRIOR / 'source-materialization.json')[0])
    rows = {(r['role'], r['relativePath']): r for r in now['filesCopied']}
    prior = {(r['role'], r['relativePath']): r for r in old['filesCopied']}
    assert len(rows) == 825 and rows.keys() == prior.keys()
    fingerprint, changes, identities = [], [], set()
    modes = collections.Counter()
    for key, row in rows.items():
        target, target_stat, actual = checked(row['source']['path'])
        donor_path = REPO / row['repositoryDonor']
        donor, donor_stat, donor_ref = checked(donor_path)
        assert actual == row['source'] and target == donor
        assert (actual['sha256'], actual['bytes']) == (donor_ref['sha256'], donor_ref['bytes'])
        assert stat.S_IMODE(target_stat.st_mode) == row['mode']
        identity = (target_stat.st_dev, target_stat.st_ino)
        assert identity not in identities and identity != (donor_stat.st_dev, donor_stat.st_ino)
        assert Path(actual['path']).lstat() == target_stat and donor_path.lstat() == donor_stat
        identities.add(identity); modes[(key[0], row['mode'])] += 1
        before = prior[key]
        if (actual['sha256'], actual['bytes'], row['mode']) != (before['source']['sha256'], before['source']['bytes'], before['mode']):
            changes.append(dict(role=key[0], path=key[1], before=before['source'], after=actual))
        fingerprint.append(dict(role=key[0], path=key[1], sha256=actual['sha256'], bytes=actual['bytes'], mode=row['mode']))
    fingerprint.sort(key=lambda r: (r['role'], r['path']))
    digest = hashlib.sha256(json.dumps(fingerprint, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert digest == now['roleContentSha256'] == 'cfbd75be70aeaa36006009fa6580b8f0f4bb789852e8d8201eefefd09d0a1550'
    assert len(changes) == 1 and changes[0]['path'] == 'runtime/script_loader.cpp'
    print(json.dumps(dict(state='ROOT_INDEPENDENT_SOURCE_AND_DONOR_READBACK_V2_PASSED',
        verifier=checked(Path(__file__).resolve())[2], materializationSummary=summary_ref,
        files=825, bytes=sum(r['bytes'] for r in fingerprint), distinctTargetInodes=825,
        allTargetAndDonorBytesHashesModesIdentitiesAndReadBookendsVerified=True,
        unchangedRows=824, changes=changes, roleContentSha256=digest,
        modeCounts=[dict(role=k[0], mode=k[1], files=v) for k, v in sorted(modes.items())],
        priorV1RedundantConditionalAssertionNotReliedUpon=True,
        compilerOrGeneratorOrGuestInvoked=False)), flush=True)


if __name__ == '__main__':
    main()
