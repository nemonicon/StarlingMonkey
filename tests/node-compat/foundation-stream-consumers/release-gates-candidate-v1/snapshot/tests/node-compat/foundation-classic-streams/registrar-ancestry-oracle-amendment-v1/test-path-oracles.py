"""Run only existing safe Node source oracles into an owned directory; no guest."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
SOURCE=REPO/'tests/node-compat/foundation-scheduler/production-release-runner-v3/oracles'
ORIGINAL=REPO/'tests/node-compat/foundation-path'
def row(path):
    assert path.is_file() and not path.is_symlink()
    data=path.read_bytes()
    return {'path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
def main():
    assert len(sys.argv)==2
    output=Path(sys.argv[1]).absolute()
    assert output.is_relative_to(Path('/tmp/starling-node-compat')) and not output.exists()
    assert row(NODE)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
    originals=[ORIGINAL/n for n in ['lexical-vectors.json','semantic-results.json','glob-vectors.json','glob-differences.json','glob-results.json']]
    before=[row(p)for p in originals]
    source_before=[row(SOURCE/n)for n in ['semantic.mjs','glob.mjs']]
    text=(HERE/'proposed/release/runners/path.mjs').read_text()
    assert "const oracleScripts = resolve(here, '../foundation-scheduler/production-release-runner-v3/oracles');" in text
    assert "cwd: repository" in text and 'NODE_COMPAT_PATH_ORACLE_OUTPUT: oracleOutput' in text
    assert all(x['sha256']in text for x in source_before)
    output.mkdir()
    environment=dict(os.environ,NODE_COMPAT_PATH_ORACLE_OUTPUT=str(output))
    for key in ['NODE_OPTIONS','NODE_PATH']:
        assert not environment.get(key),key
    commands=[]
    for name,flags in [('semantic.mjs',[]),('glob.mjs',['--expose-internals'])]:
        argv=[str(NODE),*flags,str(SOURCE/name)]
        result=subprocess.run(argv,cwd=REPO,env=environment,capture_output=True,timeout=55)
        (output/(name+'.stdout.txt')).write_bytes(result.stdout)
        (output/(name+'.stderr.txt')).write_bytes(result.stderr)
        assert result.returncode==0,(name,result.stderr.decode())
        commands.append({'argv':argv,'cwd':str(REPO),'outputEnvironment':{'NODE_COMPAT_PATH_ORACLE_OUTPUT':str(output)},'exitCode':result.returncode,
            'stdoutSha256':hashlib.sha256(result.stdout).hexdigest(),'stderrSha256':hashlib.sha256(result.stderr).hexdigest()})
    assert [row(p)for p in originals]==before
    assert [row(SOURCE/n)for n in ['semantic.mjs','glob.mjs']]==source_before
    names=sorted(p.name for p in output.iterdir())
    expected=sorted([p.name for p in originals]+[n+'.'+s+'.txt'for n in ['semantic.mjs','glob.mjs']for s in ['stdout','stderr']])
    assert names==expected
    for p in originals:
        assert json.loads((output/p.name).read_bytes())==json.loads(p.read_bytes()),p.name
    report={'schemaVersion':1,'state':'TWO_REAL_NODE_ORACLE_SUBPROCESSES_FRESH_OUTPUT_NO_OLD_WRITES_PASSED','checkedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'node':row(NODE),'sourceFiles':source_before,'commands':commands,'outputs':[row(p)for p in sorted(output.iterdir())],
        'oldOracleOutputsUnchanged':before,'nodeScriptsRewritten':False,'guestOrComponentizerOrNativeBuildExecuted':False,
        'allSixOptionalRunnersSourceAudit':{'path':'Only Node oracle entrypath/cwd and pre/post script hash checks change; exact inherited oracle bodies.',
            'events':'Child processes only Wasmtime; application and fixture sources use explicit foundation-events here.',
            'string-decoder':'Child processes only Wasmtime; source here is explicit foundation-string-decoder.',
            'assert':'Uses nativeHarness; no Node oracle subprocess entry.', 'querystring':'Uses nativeHarness; no Node oracle subprocess entry.',
            'util':'Uses nativeHarness; no Node oracle subprocess entry.'},
        'scope':'Bounded public Node source oracle execution only. Historical glob hostile-domain vectors run only in the profile matcher, as inherited; no vulnerable historical oracle expansion.'}
    (output/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'state':report['state'],'output':str(output),'subprocesses':2,'oldOutputsUnchanged':5}))
if __name__=='__main__':main()
