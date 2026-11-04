"""Null/unreviewed/schema/hash negatives only. No actual frozen verifier called."""
import argparse,copy,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False)
 spec=importlib.util.spec_from_file_location('source_bootstrap',HERE/'artifact-tools/bootstrap-classifier.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 contract=json.loads((HERE/'admission-pins.json').read_bytes());null=json.loads((HERE/'bootstrap-pins.json').read_bytes());checks=[]
 def reject(name,fn):
  try:fn()
  except(AssertionError,KeyError,TypeError,ValueError):checks.append(name);return
  raise AssertionError('Expected refusal: '+name)
 for label in module.LABELS:reject('unconfigured '+label,lambda label=label:module.select_pin(null,{},label,'0'*64,contract))
 reviewed=copy.deepcopy(null);reviewed['state']='ROOT_REVIEWED_ZLIB350_VALIDATION_BOOTSTRAP_V1'
 for label in module.LABELS:reject('requested null reviewed variant '+label,lambda label=label:module.select_pin(reviewed,{},label,'0'*64,contract))
 reject('unknown label before artifact',lambda:module.select_pin(reviewed,{},'invented','0'*64,contract))
 fake=copy.deepcopy(reviewed);fake['variants']['normal-off']={'state':'unreviewed-zlib350-production-freeze-pin-candidate','reviewRequired':True}
 reject('exporter unreviewed state',lambda:module.select_pin(fake,{},'normal-off','0'*64,contract))
 legacy=json.loads((HERE.parents[1]/'foundation-classic-streams/production-adoption-v1/reviewed-trace-runtime-pins-v1.json').read_bytes())
 reject('genuine reviewed342 authority not350 approval',lambda:module.select_pin(legacy,{},'normal-off','0'*64,contract))
 pins=a.output/'null-pins.json';pins.write_bytes(json.dumps(null).encode());review=a.output/'review.json';review.write_text('{}')
 h=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
 reject('bootstrap null refuses before own index or frozen inputs',lambda:module.bootstrap(str(pins),h(pins),str(review),h(review),'normal-off'))
 malformed=a.output/'malformed.json';malformed.write_text('not JSON')
 reject('wrong digest before JSON parse',lambda:module.bootstrap(str(malformed),'0'*64,str(review),h(review),'normal-off'))
 alias=a.output/'link.json';alias.symlink_to(pins);reject('authority symlink refused',lambda:module.read(alias,h(pins)))
 source=(HERE/'artifact-tools/bootstrap-classifier.py').read_text();assert source.index('pin=select_pin(')<source.index("spec=importlib.util.spec_from_file_location('reviewed_zlib350_artifact_common'");checks.append('private frozen verifier import occurs after reviewed pin gate')
 assert source.index("index_bytes=read(")<source.index("spec=importlib.util.spec_from_file_location('reviewed_zlib350_artifact_common'");checks.append('Root-bound proposal SHA before verifier import')
 result={'schemaVersion':1,'state':'BOOTSTRAP_SOURCE_AND_REFUSAL_CHECKS_PASSED','count':len(checks),'checks':checks,'actualEngineOrFrozenVerifierOrGuestOrToolExecuted':False}
 (a.output/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'checks':len(checks),'output':str(a.output)}))
if __name__=='__main__':main()
