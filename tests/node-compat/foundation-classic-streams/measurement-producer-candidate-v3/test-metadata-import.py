"""Tiny stand-in import tests only; never imports the real diagnostic policy."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'measurement-producer-candidate-v2'
def sha(b):return hashlib.sha256(b).hexdigest()
before=(OLD/'build-classic-benchmark-engine.sh').read_text()
after=(HERE/'build-classic-benchmark-engine.sh').read_text()
insertion="sys.path.insert(0, str(pathlib.Path(packet_root)))\n"
expected=before.replace('classic-bench-trace-v2','classic-bench-trace-v3').replace('classic-benchmark-trace-v2','classic-benchmark-trace-v3')
assert after.count(insertion)==1 and after.replace(insertion,'',1)==expected
needle="benchmark_spec = importlib.util.spec_from_file_location('classic_benchmark_build_policy',pathlib.Path(packet_root)/'benchmark-policy.py')\n"
start=before.index(needle);end=before.index('metadata = benchmark.decorate',start)
old_fragment=before[start:end]
new_fragment=after[after.index(insertion):after.index('metadata = benchmark.decorate',after.index(insertion))]
assert new_fragment==insertion+old_fragment
ast.parse(new_fragment)
cases=['exact one-line insertion and unchanged recipe bytes','exact extracted import-only fragment parses']
with tempfile.TemporaryDirectory(prefix='classic-benchmark-import-path-')as tmp:
 root=Path(tmp);packet=root/'packet';packet.mkdir();cwd=root/'external';cwd.mkdir()
 (packet/'benchmark_common.py').write_text("VALUE='owned-packet'\n")
 (packet/'benchmark-policy.py').write_text("from benchmark_common import VALUE\nIMPORTED=VALUE\ndef decorate(*args):raise AssertionError('decorate must not run')\n")
 (cwd/'benchmark_common.py').write_text("VALUE='wrong-cwd'\n")
 def run(fragment,expect,path=None,expose_cwd=False):
  setup="import importlib.util,pathlib,sys\nsys.dont_write_bytecode=True\npacket_root="+repr(str(path or packet))+"\n"
  if expose_cwd:setup+="sys.path.insert(0,"+repr(str(cwd))+")\n"
  code=setup+fragment+"\nassert benchmark.IMPORTED=='owned-packet'\n"
  done=subprocess.run([sys.executable,'-I','-c',code],cwd=cwd,capture_output=True,text=True)
  assert (done.returncode==0)is expect,(done.returncode,done.stderr)
  return done
 old=run(old_fragment,False);assert"ModuleNotFoundError: No module named 'benchmark_common'"in old.stderr
 cases.append('old stdin loader reproduces missing sibling in isolated tiny stand-ins')
 run(new_fragment,True);cases.append('new loader resolves exact sibling outside packet cwd')
 run(new_fragment,True,expose_cwd=True);cases.append('packet prefix takes precedence over owned foreign cwd sentinel')
 missing=root/'missing';missing.mkdir();(missing/'benchmark-policy.py').write_text((packet/'benchmark-policy.py').read_text())
 bad=run(new_fragment,False,missing);assert"ModuleNotFoundError: No module named 'benchmark_common'"in bad.stderr
 cases.append('missing sibling still fails, no fallback or fabricated helper')
done=subprocess.run(['bash','-n',str(HERE/'build-classic-benchmark-engine.sh')],capture_output=True,text=True);assert done.returncode==0,done.stderr
cases.append('proposed shell syntax only passes')
for source in [HERE/'test-metadata-import.py',OLD/'benchmark-policy.py',OLD/'benchmark_common.py']:ast.parse(source.read_text())
cases.append('three Python sources parse without import')
result={'schemaVersion':1,'state':'TINY_IMPORT_PATH_SOURCE_TESTS_PASSED_NO_BUILD','passed':len(cases),'cases':cases,'originalRecipeSha256':sha(before.encode()),'proposedRecipeSha256':sha(after.encode()),'realPolicyImported':False,'buildOrGuestExecuted':False}
assert len(sys.argv)==2
output=Path(sys.argv[1]).absolute();assert str(output).startswith('/tmp/starling-node-compat/')and not output.exists()
output.mkdir(parents=True)
with(output/'results.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
