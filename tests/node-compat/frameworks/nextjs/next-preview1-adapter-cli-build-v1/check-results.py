"""Read-only actual build evidence checker; no CLI/compiler/helper invocation."""
from pathlib import Path
import argparse,hashlib,json,stat
HERE=Path(__file__).resolve().parent
def checked(data,row):
    assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['path'];return data
def external(row):return checked(Path(row['path']).read_bytes(),row)
def clean(t):
    assert type(t['rawExitCode'])is int and t['rawExitCode']==0
    assert t['timeout']is False and t['forcedCleanup']is False
    assert t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True
    assert all(t[k]==[]for k in ('signals','interruptedSignals','errors','remainingObservedPids'))
def run(originals):
    idx=json.loads((HERE/'index.json').read_text());assert len(idx['files'])==len({r['path']for r in idx['files']})
    assert {r['path']for r in idx['files']}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()and p!=HERE/'index.json'}
    for row in idx['files']:checked((HERE/row['path']).read_bytes(),row)
    root=json.loads((HERE/'root-result.json').read_text());a=json.loads((HERE/'authority.json').read_text())
    actual=json.loads(checked((HERE/'raw/worker-result.json').read_bytes(),root['actualWorkerResult']))
    assert actual['passed']is True and actual['compilerError']is None and actual['finalProtectionError']is None
    assert actual['sourceIndex']==a['pinned']['candidateIndex']
    assert (actual['sourceFiles'],actual['sourceChanges'],actual['vendorFiles'],actual['vendorCrates'],actual['rustDistributionFiles'])==(271,2,7264,121,338)
    assert actual['inputBefore']==actual['inputAfter']=={'files':15433,'trees':5,'unchanged':True}
    assert all(actual[k]is False for k in ('nativeCliInvoked','adapterInvoked','wasmSplicerRebuilt','jsPackageRebuilt','engineOrGuestExecuted'))
    disk=actual['disk'];assert disk['startFreeBytes']>=2*1024**3 and disk['minimumObservedFreeBytes']>=800*1024**2 and disk['finalFreeBytes']>=800*1024**2
    assert disk['samples']>0 and disk['stopRequested']is False and disk['errors']==[] and actual['rootSignals']==[]
    inner=json.loads(checked((HERE/'raw/command/terminal.json').read_bytes(),actual['commandTerminal']));clean(inner)
    outer=json.loads(checked((HERE/'raw/root/terminal.json').read_bytes(),root['outerTerminal']));clean(outer)
    assert root['rawExitCode']==0 and root['cleanOwnedGroups']is True and root['adapterOrGuestExecuted']is False
    for name,t,cap in [('command',inner,2200),('root',outer,2400)]:
        for stream in ('stdout','stderr'):checked((HERE/'raw'/name/(stream+'.log')).read_bytes(),t[stream])
        started=json.loads((HERE/'raw'/name/'started.json').read_text());assert started['pid']==t['pid']and started['timeoutSeconds']==cap
    child=json.loads((HERE/'raw/command/started.json').read_text());request=json.loads((HERE/'raw/requested-command.json').read_text())
    assert child['argv']==request['argv'] and request['timeoutSeconds']==2200
    assert child['argv']==[a['pinned']['cargo']['path'],'build','--locked','--offline','--release','-p','spidermonkey-embedding-splicer','--bin','splicer','--target','aarch64-apple-darwin','--jobs','1','--target-dir',a['newWorkRoot']+'/target']
    env=request['environment'];assert env['CARGO_HOME']==a['newWorkRoot']+'/cargo-home'and env['CARGO_NET_OFFLINE']=='true'and env['CARGO_BUILD_JOBS']=='1'
    assert env['RUSTC']==a['pinned']['rustc']['path']and env['RUSTDOC']==a['pinned']['rustdoc']['path']
    lines=[json.loads(x)for x in(HERE/'raw/root/stdout.log').read_text().splitlines()]
    assert len(lines)==2 and lines[0]=={'pid':inner['pid'],'timeoutSeconds':2200}and lines[1]=={'result':root['actualWorkerResult'],'passed':True}
    assert (HERE/'raw/root/stderr.log').read_bytes()==b''and(HERE/'raw/command/stdout.log').read_bytes()==b''
    stderr=(HERE/'raw/command/stderr.log').read_text();assert 'Finished `release` profile [optimized]'in stderr and '\nerror'not in stderr
    if originals:
        external(root['actualWorkerResult']);external(actual['artifact'])
        ledger=json.loads(external(actual['completeInputBefore']));journal=json.loads(external(actual['copyJournal']))
        assert len(ledger['files'])==15433 and len(ledger['trees'])==5 and len(journal['copies'])==7535
        for path,record in ledger['files'].items():
            external(record['descriptor']);s=Path(path).stat();now={'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'bytes':s.st_size,'mtimeNs':s.st_mtime_ns,'ctimeNs':s.st_ctime_ns};assert now==record['identity'],path
        for tree in ledger['trees']:
            rootpath=Path(tree['root']);assert sorted(str(p.relative_to(rootpath))for p in rootpath.rglob('*')if p.is_file())==tree['files']
            assert sorted(str(p.relative_to(rootpath))for p in rootpath.rglob('*')if p.is_dir())==tree['directories']
        assert sum(r['role']=='source'and r['original']['sha256']!=r['destination']['sha256']for r in journal['copies'])==2
        for key in ('sourceIndex','authority','commandTerminal'):external(actual[key])
        external(root['outerTerminal'])
    return dict(passed=True,compilerRawExitCode=0,parentRawExitCode=0,sourceFiles=271,changedFiles=2,vendorFiles=7264,rustFiles=338,protectedInputs=15433,
                originalsRehashed=originals,newCli=actual['artifact'],adapterInvoked=False,guestExecuted=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--originals',action='store_true');args=p.parse_args()
    print(json.dumps(run(args.originals)))
