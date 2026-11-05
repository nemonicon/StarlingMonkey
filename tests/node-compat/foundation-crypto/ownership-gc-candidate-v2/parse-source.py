"""Authorized syntax-only pinned Node child. No module import/evaluation."""
from pathlib import Path
import hashlib,json,os,subprocess,tempfile
HERE=Path(__file__).resolve().parent
NODE=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node');h=hashlib.sha256()
with NODE.open('rb')as f:
    for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
assert h.hexdigest()=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
target=HERE/'guest.GC.UNEXECUTED.mjs';output=Path(tempfile.mkdtemp(prefix='crypto-owner355-gc-guest-v2-syntax-',dir='/private/tmp/starling-node-compat'))
argv=[str(NODE),'--check',str(target)];p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30,env={k:v for k,v in os.environ.items()if k not in ['NODE_OPTIONS','NODE_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH']})
for name,b in [('stdout.log',p.stdout),('stderr.log',p.stderr)]:
    with(output/name).open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
terminal=dict(schemaVersion=1,argv=argv,rawExitCode=p.returncode,targetSha256=hashlib.sha256(target.read_bytes()).hexdigest(),targetBytes=target.stat().st_size,syntaxOnly=True,moduleImported=False,guestOrCryptoOrGcInvoked=False)
with(output/'terminal.json').open('x')as f:json.dump(terminal,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
assert p.returncode==0 and p.stdout==b''and p.stderr==b''
(HERE/'syntax-evidence').mkdir()
for path in output.iterdir():
    with(HERE/'syntax-evidence'/path.name).open('xb')as f:f.write(path.read_bytes());f.flush();os.fsync(f.fileno())
with(HERE/'syntax-results.json').open('x')as f:json.dump(dict(schemaVersion=1,state='PINNED_NODE_SYNTAX_ONLY_PASSED',externalOutput=str(output),terminal=terminal,pinnedNodeSyntaxParserInvoked=True,moduleImported=False,ownerHelpersBuildBootstrapCryptoKeyPrototypeGuestGcInvoked=False),f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(dict(state='SYNTAX_ONLY_PASSED',rawExitCode=0,externalOutput=str(output),moduleImported=False)))
