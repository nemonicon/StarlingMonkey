"""Authorized pinned SDK frontend-only checks of unapplied source afterimages."""
from pathlib import Path
import hashlib,json,os,shlex,subprocess,time
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3];K=REPO/'tests/node-compat/foundation-crypto'
def descriptor(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
root_path=K/'ownership-gc-v2-build-root-results.json';root=json.loads(root_path.read_bytes());assert descriptor(root_path)['sha256']=='cdde20539a850a2679a91e7db2090d9dc0e1a881c8f17c19ff4664852123e931'
m=json.loads(Path(root['metadata']['path']).read_bytes());assert descriptor(root['metadata']['path'])==root['metadata'];db_path=Path(m['compileCommandsPath']);assert descriptor(db_path)['sha256']==m['compileCommandsSha256'];db=json.loads(db_path.read_bytes())
source=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source');sdk=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build/cache/wasi-sdk/85e6');compiler=sdk/'bin/clang++'
assert descriptor(compiler)['sha256']=='1aca933cc48d7e137804231e0ced1624052fe489562ab496d63ad9a23998c7fe'
records=[];evidence=HERE/'evidence';evidence.mkdir(exist_ok=False)
for name in ['builtins/web/timers.cpp','runtime/event_loop.cpp']:
    original=next(r for r in db if r['file']==str(source/name));words=shlex.split(original['command']);wrapper=Path(words.pop(0));wrapper_text=wrapper.read_text();assert str(compiler)in wrapper_text and '"$@"'in wrapper_text
    assert words.count('-c')==words.count('-o')==1;output_at=words.index('-o');del words[output_at:output_at+2];source_at=words.index('-c');assert words[source_at+1]==str(source/name);del words[source_at:source_at+2]
    after=HERE/'afterimages'/name;assert after.is_file();stem=Path(name).stem
    argv=[str(compiler),*words,'-iquote',str((source/name).parent),'-fsyntax-only','-MD','-MF',str(evidence/(stem+'.d')),'-MT','source-only-'+stem,str(after)]
    assert '-c'not in argv and '-o'not in argv and '-fsyntax-only'in argv
    start=time.monotonic();stdout=evidence/(stem+'.stdout.log');stderr=evidence/(stem+'.stderr.log')
    with stdout.open('xb')as out,stderr.open('xb')as err:
        proc=subprocess.run(argv,cwd=original['directory'],env={**os.environ,'LC_ALL':'C','LANG':'C','PYTHONDONTWRITEBYTECODE':'1'},stdout=out,stderr=err,timeout=60,check=False)
        for f in [out,err]:f.flush();os.fsync(f.fileno())
    terminal=dict(schemaVersion=1,argv=argv,cwd=original['directory'],rawExitCode=proc.returncode,operationalSeconds=time.monotonic()-start,timeout=False,frontendOnly=True,objectOrLinkOrNativeBuildRequested=False,sourceAfterimage=descriptor(after),actualCompileDatabase=descriptor(db_path),originalCompileRow=original,originalWrapper=descriptor(wrapper),actualDirectCompiler=descriptor(compiler),resolvedCompiler=str(compiler.resolve()),stdout=descriptor(stdout),stderr=descriptor(stderr),dependencyFile=descriptor(evidence/(stem+'.d'))if(evidence/(stem+'.d')).exists()else None)
    (evidence/(stem+'.terminal.json')).write_text(json.dumps(terminal,indent=2)+'\n');records.append(terminal)
print(json.dumps(dict(frontendChecks=len(records),rawExitCodes=[r['rawExitCode']for r in records],noObjectsOrLinkRequested=True)))
