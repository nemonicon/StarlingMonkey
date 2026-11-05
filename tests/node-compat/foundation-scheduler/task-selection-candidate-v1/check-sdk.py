"""Actual SDK frontend only; never configures, links, builds or runs an engine."""
from pathlib import Path
import hashlib
import json
import shlex
import subprocess
import time

HERE = Path(__file__).resolve().parent
WORK = Path('/private/tmp/starling-node-compat/scheduler-resource-v1-build')
CONFIGURED = Path('/private/tmp/starling-node-compat/scheduler-resource-v1-source')


def row(p):
    p=Path(p); h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
    return dict(path=str(p.resolve()),sha256=h.hexdigest(),bytes=p.stat().st_size)


def main():
    evidence=HERE/'sdk-evidence'; evidence.mkdir()
    metadata_path=next((WORK/'artifacts').glob('*.build.json'))
    metadata_row=row(metadata_path)
    assert metadata_row['sha256']=='51fbc0a06ed2e06c24e6d1fd3190873a5a3190657cfe2d74bf44ff4128b0e80e'
    metadata=json.loads(metadata_path.read_bytes())
    db_path=Path(metadata['compileCommandsPath']); db_row=row(db_path)
    assert db_row['sha256']==metadata['compileCommandsSha256']
    database=json.loads(db_path.read_bytes())
    changes=json.loads((HERE/'source-contract.json').read_bytes())['changes']
    mappings={str(CONFIGURED/c['path']):str(HERE/'afterimages'/c['path']) for c in changes}
    overlay=dict(version=0,**{'use-external-names':False},roots=[dict(type='file',name=k,**{'external-contents':v}) for k,v in mappings.items()])
    overlay_path=evidence/'overlay.json'; overlay_path.write_text(json.dumps(overlay,indent=2)+'\n')
    compiler=WORK/'cache/wasi-sdk/85e6/bin/clang++'
    compiler_row=row(compiler)
    records=[]; dependencies={}
    for name in ['host-apis/wasi-0.2.0/host_api.cpp','runtime/event_loop.cpp']:
        selected=[r for r in database if r['file']==str(CONFIGURED/name)]
        assert len(selected)==1
        source=selected[0]; words=shlex.split(source['command']); donor_wrapper=row(words[0])
        assert '-c' in words and words.count('-o')==1
        output_index=words.index('-o'); words=words[1:output_index]+words[output_index+2:]
        words.remove('-c')
        dep=evidence/(Path(name).stem+'.d')
        argv=[str(compiler),*words,'-fsyntax-only','-ivfsoverlay',str(overlay_path),'-MD','-MF',str(dep),'-MT','source-check']
        start=time.monotonic(); result=subprocess.run(argv,cwd=source['directory'],capture_output=True,timeout=120)
        record=dict(source=name,originalCompileRow=source,donorWrapper=donor_wrapper,argv=argv,rawExitCode=result.returncode,stdout=result.stdout.decode(),stderr=result.stderr.decode(),operationalSeconds=time.monotonic()-start,frontendOnly=True)
        records.append(record)
        (evidence/(Path(name).stem+'-terminal.json')).write_text(json.dumps(record,indent=2)+'\n')
        assert result.returncode==0 and not result.stdout and not result.stderr, record
        names=shlex.split(dep.read_text().replace('\\\n','').split(':',1)[1])
        for path in names:
            logical=Path(path)
            if not logical.is_absolute(): logical=Path(source['directory'])/logical
            physical=Path(mappings.get(str(logical),str(logical)))
            value=dict(logicalPath=str(logical),physical=row(physical))
            if str(logical) in dependencies: assert dependencies[str(logical)]==value
            dependencies[str(logical)]=value
    # Recheck actual source/metadata/database/compiler bytes after both calls.
    assert row(metadata_path)==metadata_row and row(db_path)==db_row and row(compiler)==compiler_row
    for c in changes:
        assert row(c['original']['path'])==c['original'] and row(c['after']['path'])==c['after']
    facts=dict(schemaVersion=1,metadata=metadata_row,compileDatabase=db_row,compiler=compiler_row,overlay=row(overlay_path),calls=records,dependencyFiles=list(dependencies.values()),uniqueDependencies=len(dependencies),frontendOnly=True,engineBuilt=False,engineExecuted=False,componentExecuted=False,sourceApplied=False,operationalAdmission=False)
    (HERE/'sdk-results.json').write_text(json.dumps(facts,indent=2)+'\n')
    print(json.dumps(dict(frontendCalls=len(records),allExitZero=True,dependencies=len(dependencies))))


if __name__=='__main__': main()
