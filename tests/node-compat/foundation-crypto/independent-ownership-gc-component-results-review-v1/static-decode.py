"""Only the explicitly permitted pinned metadata-WIT decoder; never instantiate."""
from pathlib import Path
import json,os,subprocess
import review_io as I
HERE=Path(__file__).resolve().parent
tool=dict(path='/private/tmp/starling-node-compat/native-build/cache/wasm-tools/1448/wasm-tools',sha256='b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d',bytes=17556208)
component=dict(path='/private/tmp/starling-node-compat/crypto-owner355-gc-component-v1/worker/crypto-owner.component.wasm',sha256='52d99f4e95860b686d896c88f39b2fa5734eabeb433f48545ba814b2e45ce5f1',bytes=13118152)
I.verify(tool,'permitted pinned metadata decoder');I.verify(component,'actual newly constructed component DATA')
argv=[tool['path'],'component','wit',component['path']]
timed_out=False
try:
    result=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60,env={'PATH':'/usr/bin:/bin'},cwd=HERE)
    raw_exit=result.returncode;stdout=result.stdout;stderr=result.stderr
except subprocess.TimeoutExpired as error:
    timed_out=True;raw_exit=None;stdout=error.stdout or b'';stderr=error.stderr or b''
for name,raw in [('component-wit.stdout.txt',stdout),('component-wit.stderr.txt',stderr)]:
    with(HERE/name).open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
terminal=dict(schemaVersion=1,argv=argv,tool=tool,component=component,rawExitCode=raw_exit,timedOut=timed_out,timeoutSeconds=60,stdout=I.descriptor(str(HERE/'component-wit.stdout.txt')),stderr=I.descriptor(str(HERE/'component-wit.stderr.txt')),metadataOnly=True,componentInstantiated=False,generatedModuleImported=False,ordinaryGuestKeyOrGcExportInvoked=False,ownerHelpersInvoked=False)
with(HERE/'static-decoder-terminal.json').open('xb')as f:f.write((json.dumps(terminal,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
I.need(raw_exit==0 and timed_out is False and stderr==b'','fresh actual component WIT metadata decoder succeeded')
I.need(stdout==Path('/private/tmp/starling-node-compat/crypto-owner355-gc-component-v1/worker/emitted.wit').read_bytes(),'fresh metadata decode equals complete actual retained emitted WIT')
I.final_rehash()
print(json.dumps(dict(metadataOnlyWitDecodePassed=True,rawExitCode=raw_exit,decodedBytes=len(stdout),componentInstantiated=False)))
