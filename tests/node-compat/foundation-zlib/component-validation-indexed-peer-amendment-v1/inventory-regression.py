"""Explicit READ-ONLY source inventory regression, never a publisher action."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
BOOT=Path('/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/foundation-zlib/native-integration-candidate-v4')
BOOT_SHA='d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def regular(path,digest=None,size=None):
 path=Path(path);assert path.is_file()and not path.is_symlink(),str(path);raw=path.read_bytes();assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path;return raw
def main():
 assert len(sys.argv)==3,'EXACT_SOURCE_INDEX FRESH_EXTERNAL_OUTPUT'
 source_sha=sys.argv[1];index_raw=regular(HERE/'index.json',source_sha);index=json.loads(index_raw)
 for row in index['files']:regular(HERE/row['path'],row['sha256'],row['bytes'])
 spec=importlib.util.spec_from_file_location('readonly_finite_validation_inventory',HERE/'inventory.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 consumed={}
 def add(path,digest=None,size=None):
  path=Path(path).resolve(strict=True);raw=regular(path,digest,size);row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in consumed or consumed[str(path)]==row;consumed[str(path)]=row
 families=module.collect_validation_inventory(HERE,source_sha,BOOT,BOOT_SHA,add)
 assert len(families)==6
 peer=next(row for row in families if row['role']=='peer');assert peer['kind']=='INDEXED_ONLY'and peer['indexedFiles']==5 and peer['preparationManifestRead']is False
 assert not(Path(peer['root'])/'input-freeze.json').exists()
 bootstrap=next(row for row in families if row['role']=='bootstrap');assert bootstrap['preparationRows']==2261 and Path(bootstrap['preparationRoot'])==module.ORIGINAL
 assert all(row['preparationManifestRead']is True for row in families if row['role']!='peer')
 peer_root=Path(peer['root']);target=peer_root/'verify.py';assert target.is_file()
 def deny_indexed(path,digest=None,size=None):
  if Path(path)==target:raise FileNotFoundError('Controlled read-only missing indexed file: '+str(path))
  return regular(path,digest,size)
 indexed_failed=False
 try:module.read_indexed(peer_root,peer['indexSha256'],deny_indexed)
 except FileNotFoundError:indexed_failed=True
 assert indexed_failed,'An omitted indexed peer file must refuse'
 manifest_target=HERE/'input-freeze.json'
 def deny_manifest(path,digest=None,size=None):
  if Path(path)==manifest_target:raise FileNotFoundError('Controlled read-only missing required preparation manifest')
  return regular(path,digest,size)
 prep_failed=False
 try:module.collect_validation_inventory(HERE,source_sha,BOOT,BOOT_SHA,lambda *args:None,deny_manifest)
 except FileNotFoundError:prep_failed=True
 assert prep_failed,'Missing known preparation manifest must refuse'
 first=json.loads(regular(module.ORIGINAL/'input-freeze.json'))['inputs'][0];incorrect=(BOOT/first['path']).resolve();correct=(module.ORIGINAL/first['path']).resolve();assert not incorrect.exists();regular(correct,first['sha256'],first['bytes'])
 # Recheck the complete inventory, not only isolated context examples.
 final={}
 def final_add(path,digest=None,size=None):
  path=Path(path).resolve(strict=True);raw=regular(path,digest,size);final[str(path)]={'path':str(path),'sha256':sha(raw),'bytes':len(raw)}
 assert module.collect_validation_inventory(HERE,source_sha,BOOT,BOOT_SHA,final_add)==families
 assert final==consumed;regular(HERE/'index.json',source_sha)
 output=Path(sys.argv[2]);assert output.is_absolute()and str(output).startswith('/tmp/starling-node-compat/')and not output.exists()and not output.is_symlink();output.mkdir()
 report={'schemaVersion':1,'state':'ACTUAL_FINITE_VALIDATION_INVENTORY_READONLY_REGRESSION_PASSED','sourceIndexSha256':source_sha,'families':families,'completeInventoryVerifiedTwice':True,'consumedFiles':sorted(consumed.values(),key=lambda row:row['path']),'consumedFileCount':len(consumed),'indexedPeerFileOmissionRefused':indexed_failed,'requiredPreparationManifestOmissionRefused':prep_failed,'peerManifestInventedOrRead':False,'originalPreparationRows':2261,'originalAndStagedIndexedBootstrapFiles':85,'latentStagedRow0Absent':True,'latentOriginalRow0Exact':True,'bootstrapOrVerifierOrActivationOrCompilerOrGuestOrHostExecuted':False}
 with(output/'results.json').open('xb')as stream:stream.write((json.dumps(report,indent=2)+'\n').encode())
 print(json.dumps({'reportPath':str(output/'results.json'),'reportSha256':sha((output/'results.json').read_bytes()),'families':6,'filesVerifiedTwice':len(consumed),'negativeCases':2,'actionsExecuted':False}))
if __name__=='__main__':main()
