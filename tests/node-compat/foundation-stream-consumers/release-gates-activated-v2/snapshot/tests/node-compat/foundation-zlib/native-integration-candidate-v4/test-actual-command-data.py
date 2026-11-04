"""Read-only genuine captured-command regression. Never invokes a compiler."""
import argparse,hashlib,importlib.util,json,shlex
from pathlib import Path
HERE=Path(__file__).resolve().parent
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False)
 h=lambda path:hashlib.sha256(path.read_bytes()).hexdigest();checks=[];inputs=[]
 def read(path,expected=None):
  path=Path(path);assert path.is_file()and not path.is_symlink();data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()
  if expected is not None:assert digest==expected
  inputs.append({'path':str(path),'sha256':digest,'bytes':len(data)});return data
 root=Path('/tmp/starling-node-compat/production-classic-trace-v1/native-freeze')
 db=json.loads(read(root/'normal-off-compile_commands.json','05d3667f92647d7042160988d3cc20bf27a2bd04e478a7992e3c37baedf1e57f'))
 metadata=json.loads(read(root/'normal-off.engine.wasm.build.json'))
 repo=Path('/private/tmp/starling-node-compat/classic-trace-source-v1')
 native=[row for row in db if row['file'].startswith((str(repo/'builtins')+'/',str(repo/'runtime')+'/'))and row['file'].endswith('.cpp')];assert len(native)==61
 codec=load('corrected350_codec',HERE/'codec-evidence.py');layer=load('corrected350_layer',HERE/'layer-policy.py')
 dist=Path('/tmp/starling-node-compat/classic-trace-v1-build/spidermonkey-dist-release')
 selected=codec.selected_compile_input(dist);checks.append('actual selected distribution/archive/four headers hash-authenticated')
 for row in [selected['archive'],*selected['headers']]:inputs.append(row)
 # Compiler-data model only. No original engine metadata is rewritten/projected
 # to350; these booleans select the command grammar for actual61+embedding data.
 features={'syntheticCompilerDataOnly':True,'internalTicksEnabled':True,'classicStreamsEnabled':True,'streamWebEnabled':True,'eventsEnabled':True,'stringDecoderEnabled':True,'gcStress':False,'entropyPolicy':'off','zlibEnabled':False,'zlibSelectedCodecInput':selected}
 layout,queue,private=layer.validate_classic_compilation(db,metadata['actualEmbeddingCompileCommands'],repo,features)
 assert len(layout)==61 and len(queue)==1 and len(private)==5;checks.append('genuine61 native plus separateembedding1 accepted by corrected full compiler grammar in zlibOFF data domain')
 records=[{'kind':'actual-frozen-native','source':row['file'],'command':row['command']}for row in native]
 records.append({'kind':'actual-frozen-embedding','source':'embedding/embedding.cpp','command':metadata['actualEmbeddingCompileCommands'][0]})
 sdk=json.loads(read(HERE.parent/'sdk-syntax-v1/results.json'))
 for row in sdk['commands']:
  assert row['rawExitCode']==0;records.append({'kind':'actual-recorded-sdk-syntax','source':row['label'],'command':shlex.join(row['command'])})
 assert len(records)==64
 for record in records:
  tokens=shlex.split(record['command']);codec.no_second_codec(tokens,selected);record['tokens']=tokens;record['commandSha256']=hashlib.sha256(record['command'].encode()).hexdigest()
 checks.append('all64 actual compile/syntax command records accept exactly pinned forced include; SDK remains syntax evidence only')
 actual_link=Path('/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze/benchmark-classic-on-final-link.commands.txt')
 lines=[line for line in read(actual_link).decode().splitlines()if'libspidermonkey.a'in line and' -c 'not in line];assert len(lines)==1
 codec.no_second_codec(shlex.split(lines[0]));checks.append('actual captured link has no forced include and passes separate link grammar')
 rejected=[]
 base=records[0]['tokens'];at=base.index('-include')
 variants={'missing':base[:at]+base[at+2:],'extra':base+['-include',selected['requiredForcedInclude']['path']],
  'same-name-other-root':base[:at+1]+['/tmp/elsewhere/js-confdefs.h']+base[at+2:],
  'joined':base[:at]+['-include'+selected['requiredForcedInclude']['path']]+base[at+2:],
  'PCH':base+['-include-pch','/tmp/not-a-pch'],'imacros':base+['-imacros','/tmp/not-a-header'],'prefix':base+['-DZ_PREFIX=1'],
  'preprocessor-comma-wrapper':base+['-Wp,-include,/tmp/not-a-header'],'preprocessor-wrapper':base+['-Xpreprocessor','-include'],'clang-wrapper':base+['-Xclang','-include']}
 for name,tokens in variants.items():
  try:codec.no_second_codec(tokens,selected)
  except AssertionError:rejected.append(name)
  else:raise AssertionError('Expected rejection '+name)
 try:codec.no_second_codec(base)
 except AssertionError:rejected.append('forced-include-in-link-context')
 else:raise AssertionError('Compile include accepted by link context')
 result={'schemaVersion':1,'state':'ACTUAL_CAPTURED_COMMAND_DATA_REGRESSION_PASSED','count':len(checks)+len(rejected),'checks':checks,'negativeChecks':rejected,
  'actualCommandRecords':records,'selectedCompileInput':selected,'actualInputs':inputs,'compilerOrBuildOrEngineOrGuestExecuted':False,'actual342ReceiptProjectedTo350':False}
 (a.output/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'checks':result['count'],'actualCommands':64,'output':str(a.output)}))
if __name__=='__main__':main()
