"""Finite future native-build bootstrap for codec VALIDATION only.

No activation, output creation, componentizer or guest. Reviewed data must be
supplied explicitly; the checked-in four-null document cannot authorize bytes.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode=True
if not __debug__:raise RuntimeError('Bootstrap validation requires Python assertions enabled')
HERE=Path(__file__).resolve().parent
LABELS=('normal-off','normal-runtime','gc-off','disabled-off')
FIELDS=('engineSha256','engineBytes','receiptSha256','freezeReceiptSha256')
def sha(data):return hashlib.sha256(data).hexdigest()
def read(path,expected):
 path=Path(path);assert path.is_file()and not path.is_symlink()
 data=path.read_bytes();assert sha(data)==expected,str(path);return data
def select_pin(document,review,variant,pins_sha,contract):
 assert document.get('schemaVersion')==1 and document.get('state')=='ROOT_REVIEWED_STREAM_CONSUMERS355_VALIDATION_BOOTSTRAP_V1','Reviewed bootstrap pins required before artifact access'
 assert set(document['variants'])==set(LABELS)and variant in LABELS
 pin=document['variants'][variant];assert isinstance(pin,dict),'Requested bootstrap pin is unconfigured'
 assert pin.get('state')=='reviewed-consumers355-native-build-for-validation'and pin.get('reviewRequired')is False
 assert pin.get('sourceFiles')==355 and pin.get('recipeSha256')==contract['productionRecipeSha256']
 assert pin.get('sourceContractVersion')=='sm-stream-consumers-text-json-source-v1'and pin.get('variant')==variant
 assert pin.get('runtimeBackendProof')=={'verified':False,'version':None,'vernum':None}
 assert pin.get('runtimeAcceptanceClaim')is False
 for field in FIELDS:
  if field=='engineBytes':assert type(pin[field])is int and pin[field]>0
  else:assert re.fullmatch('[a-f0-9]{64}',pin[field])
 assert review.get('schemaVersion')==1 and review.get('state')=='ROOT_REVIEWED_STREAM_CONSUMERS355_BUILD_INPUTS_FOR_CODEC_VALIDATION_V1'
 assert review['reviewedPinsSha256']==pins_sha and review['sourceFiles']==355 and review['externalSources']==3
 for field,key in [('recipeSha256','productionRecipeSha256'),('policySha256','policySha256'),('helperSha256','helperSha256')]:assert review[field]==contract[key]
 assert review['runtimeAcceptanceClaim']is False and review['operationalAdmission']is False
 assert set(review['variants'])==set(LABELS)
 authority=review['variants'][variant];assert isinstance(authority,dict)
 for field in FIELDS:assert authority[field]==pin[field],field
 for field in ['independentProofIndexSha256','independentProofResultSha256']:assert re.fullmatch('[a-f0-9]{64}',authority[field])and pin[field]==authority[field]
 return json.loads(json.dumps(pin))
def bootstrap(pins_path,pins_sha,review_path,review_sha,variant):
 pins_bytes=read(pins_path,pins_sha);review_bytes=read(review_path,review_sha)
 contract=json.loads((HERE.parent/'admission-pins.json').read_bytes())
 review=json.loads(review_bytes);pin=select_pin(json.loads(pins_bytes),review,variant,pins_sha,contract)
 # Root review binds this exact proposal before importing its frozen verifier.
 index_bytes=read(HERE.parent/'index.json',review['proposalIndexSha256']);index=json.loads(index_bytes)
 for row in index['files']:assert len(read(HERE.parent/row['path'],row['sha256']))==row['bytes']
 for key,digest in [('independentProofIndexPath','independentProofIndexSha256'),('independentProofResultPath','independentProofResultSha256')]:read(pin[key],pin[digest])
 spec=importlib.util.spec_from_file_location('reviewed_consumers355_artifact_common',HERE/'artifact_common.py')
 common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
 assert pin['freezeRoot']==str(common.OUTPUT)
 receipt_path,receipt,metadata,receipt_sha=common.verify_frozen_variant(variant,return_receipt_digest=True)
 assert receipt_sha==pin['freezeReceiptSha256']and str(receipt_path)==pin['freezeReceiptPath']
 for field in ['engineSha256','engineBytes','receiptSha256']:assert receipt[field]==pin[field]
 expected_files=[{key:row[key]for key in ['path','sha256','bytes']}for row in receipt['copies']]
 assert pin['frozenFiles']==expected_files
 assert pin['enginePath']==str(common.OUTPUT/(variant+'.engine.wasm'))and pin['sourceRoot']==str(common.OUTPUT/'source')
 assert pin['componentizeSourceRoot']==str(common.OUTPUT/'componentize-source')
 for field,name in [('cachePath',variant+'-CMakeCache.txt'),('commandsPath',variant+'-compile_commands.json'),('recipePath','build-engine.sh')]:assert pin[field]==str(common.OUTPUT/name)
 for field in ['gcStress','entropyPolicy','classicStreamsEnabled','zlibEnabled','streamConsumersEnabled','classicTraceSourcePolicy','zlibSourcePolicy','streamConsumersSourcePolicy','cmakeCacheSha256','compileCommandsSha256']:assert pin[field]==metadata[field],field
 assert pin['parentEmbeddingCommandPath']==receipt['postBuildEmbeddingEvidence']['path']and pin['parentEmbeddingCommandSha256']==receipt['postBuildEmbeddingEvidence']['sha256']
 assert pin['coreSources']==receipt['coreSources']
 metadata_path=common.OUTPUT/(variant+'.engine.wasm.build.json')
 command=['/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',str(HERE/'metadata-admission.mjs'),str(metadata_path),variant,str(common.REPO)]
 node=Path(command[0]);assert sha(node.read_bytes())=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
 process=subprocess.run(command,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=55)
 admission=json.loads(process.stdout);assert admission['validationBootstrapOnly']is True and admission['operationalAdmission']is False
 assert admission['sourceFiles']==355 and admission['engineBytesRead']is False
 # Reauthenticate immutable primitive digests after all original/frozen reads.
 read(pins_path,pins_sha);read(review_path,review_sha);read(HERE.parent/'index.json',review['proposalIndexSha256'])
 return {'schemaVersion':1,'state':'ROOT_REVIEWED_STREAM_CONSUMERS355_BUILD_VALIDATION_BOOTSTRAP_PASSED',
  'variant':variant,'enginePath':pin['enginePath'],'sourceRoot':pin['sourceRoot'],'configuredSourceRoot':str(common.REPO),
  'pin':pin,'metadata':metadata,'manifestPaths':admission['selectedManifestPaths'],
  'proposalIndexSha256':review['proposalIndexSha256'],'reviewedPinsSha256':pins_sha,'rootReviewSha256':review_sha,
  'runtimeBackendProof':{'verified':False,'version':None,'vernum':None},'validationBootstrapOnly':True,'operationalAdmission':False,'guestExecuted':False}
def main():
 assert len(sys.argv)==6,'REVIEWED_PINS PINS_SHA ROOT_REVIEW REVIEW_SHA VARIANT'
 print(json.dumps(bootstrap(*sys.argv[1:])))
if __name__=='__main__':main()
