"""Full actual-capture parser regression plus owned response/negative fixtures.

No captured command, compiler, optimizer, native binary or guest is executed.
"""
import argparse,hashlib,importlib.util,json,shlex
from pathlib import Path
HERE=Path(__file__).resolve().parent
RAW=Path('/tmp/starling-node-compat/zlib-v3-build/codec-starlingmonkey_embedding.abi-i32-i64-v1.zlib-v3.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.z350v1.evidence/link.after.commands.txt')
BUILD=Path('/tmp/starling-node-compat/zlib-v3-build/engine-abi-fixed-bigint-v1-zlib-v3.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1')
ARCHIVE=Path('/tmp/starling-node-compat/zlib-v3-build/spidermonkey-dist-release/libspidermonkey.a')
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False)
 spec=importlib.util.spec_from_file_location('actual_chain_parser',HERE/'codec-evidence.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 raw=RAW.read_bytes();assert len(raw)==128787 and hashlib.sha256(raw).hexdigest()=='7ddded912805c4147cd30e7594ce31a372eca88d0085b8f4781f60f30c361fba'
 parsed=m.link_commands(raw,BUILD,ARCHIVE);assert len(parsed['commands'])==1
 record=parsed['commands'][0];assert record['kind']=='compiler-cd-inplace-wasm-opt-v1'and record['sameWasmOutputProved']is True
 assert record['compilerOutputPath']==record['postOptimizerInputPath']==record['postOptimizerOutputPath']==str(BUILD/'starling-raw.wasm/starling-raw.wasm')
 line=record['rawCommand'];assert shlex.split(line).count('-o')==2
 checks=['full actual128787B capture parsed; no line reconstruction substitutes','one archive-bearing compiler/optimizer chain','compiler output equals optimizer input/output; full argv retained']
 def reject(name,body,build=BUILD,archive=ARCHIVE):
  try:m.link_commands(body.encode(),build,archive)
  except(AssertionError,ValueError,FileNotFoundError):checks.append('negative:'+name);return
  raise AssertionError('Expected rejection '+name)
 groups=line.split(' && ');assert len(groups)==4
 for name,parts in [
  ('wrong cd',[groups[0],groups[1],'cd '+str(BUILD/'other'),groups[3]]),
  ('wrong compiler',[groups[0],groups[1].replace(str(BUILD/'cxx-wrapper'),str(BUILD/'unknown-compiler')),groups[2],groups[3]]),
  ('duplicate compiler output',[groups[0],groups[1]+' -o other.wasm',groups[2],groups[3]]),
  ('second codec',[groups[0],groups[1]+' -Wl,-lz',groups[2],groups[3]]),
  ('unknown optimizer',[groups[0],groups[1],groups[2],groups[3].replace('wasm-opt','unknown-opt')]),
  ('unknown optimizer option',[groups[0],groups[1],groups[2],groups[3].replace('--strip-debug','--unknown')]),
  ('optimizer output mismatch',[groups[0],groups[1],groups[2],groups[3].replace('-o starling-raw.wasm','-o other.wasm')]),
  ('optimizer input mismatch',[groups[0],groups[1],groups[2],groups[3].removesuffix('starling-raw.wasm')+'other.wasm']),
  ('leading command',['echo unexpected',groups[1],groups[2],groups[3]]),
 ]:reject(name,' && '.join(parts))
 for name,suffix in [('extra command',' && echo unexpected'),('pipeline',' | cat'),('or operator',' || true'),('semicolon','; true'),('substitution',' $(echo bad)'),('backtick',' `echo bad`'),('shell comment',' # hidden'),('subshell',' (echo bad)'),('quoted operator'," '&&' echo bad")]:reject(name,line+suffix)
 build=a.output/'response-build';build.mkdir();archive=build/'libspidermonkey.a';archive.write_text('SOURCE FIXTURE ONLY')
 rsp=build/'link.rsp';rsp.write_text(str(archive)+' -o target.wasm')
 direct='clang++ @'+str(rsp);assert m.link_commands(direct.encode(),build,archive)['commands'][0]['kind']=='direct-compiler-link-v1';checks.append('explicit direct response fixture stays separate')
 rsp.write_text(str(archive)+' -o target.wasm && echo hidden');reject('response cannot introduce shell stage',direct,build,archive)
 rsp.write_text(str(archive)+' -o target.wasm $(echo hidden)');reject('response substitution refused',direct,build,archive)
 outside=a.output/'outside.rsp';outside.write_text(str(archive)+' -o target.wasm')
 reject('response traversal refused','clang++ @'+str(build/'../outside.rsp'),build,archive)
 (build/'linked.rsp').symlink_to(outside);reject('response symlink refused','clang++ @'+str(build/'linked.rsp'),build,archive)
 result={'schemaVersion':1,'state':'ACTUAL_FULL_COMPILER_OPTIMIZER_CHAIN_GRAMMAR_PASSED','count':len(checks),'checks':checks,'actualCapture':{'path':str(RAW),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)},'parsedActualWitness':parsed,'compilerOptimizerOrNativeOrGuestExecuted':False,'runtimeAcceptanceClaim':False}
 (a.output/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'checks':len(checks),'actualCaptureBytes':len(raw),'output':str(a.output)}))
if __name__=='__main__':main()
