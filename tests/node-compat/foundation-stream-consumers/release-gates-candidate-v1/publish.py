"""Future source-only exclusive publisher. No owner/helper/module/action imports.

This main has NOT run during preparation. It reads/copies authenticated bytes only.
Native and guest execution require a separately reviewed generated family and a
separate Root runtime-action document; native pins do not grant runtime authority.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil
HERE=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def raw(path,digest=None,size=None):
 p=Path(path);assert p.is_file()and not p.is_symlink(),p
 value=p.read_bytes();assert digest is None or sha(value)==digest,p;assert size is None or len(value)==size,p
 return value
def safe(root,name):
 assert isinstance(name,str)and not Path(name).is_absolute()and'\\'not in name and'\0'not in name
 assert all(part not in ['','.','..']and len(part.encode())<=255 for part in name.split('/'))
 p=root
 for part in name.split('/'):
  p=p/part;assert not p.is_symlink(),p
 return p
def checked(path,digest,size):
 p=Path(path)
 if size<=64*1024*1024:return raw(p,digest,size)
 assert p.is_file()and not p.is_symlink();h=hashlib.sha256();observed=0
 with p.open('rb')as stream:
  for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk);observed+=len(chunk)
 assert h.hexdigest()==digest and observed==size,p
def encoded(document):return(json.dumps(document,indent=2)+'\n').encode()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--index-sha256',required=True);parser.add_argument('--source-review',required=True);parser.add_argument('--source-review-sha256',required=True);parser.add_argument('--reviewed-pins',required=True);parser.add_argument('--reviewed-pins-sha256',required=True);parser.add_argument('--native-root-review',required=True);parser.add_argument('--native-root-review-sha256',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
 index=json.loads(raw(HERE/'index.json',args.index_sha256));private=[dict(row)for row in index['files']]
 def own():
  raw(HERE/'index.json',args.index_sha256)
  for row in private:raw(safe(HERE,row['path']),row['sha256'],row['bytes'])
  for row in json.loads(raw(HERE/'source-inputs.preparation.json'))['files']:checked(row['path'],row['sha256'],row['bytes'])
 own()
 source_review=json.loads(raw(args.source_review,args.source_review_sha256));assert source_review['state']=='ROOT_REVIEWED_CONSUMERS355_RELEASE_SOURCE_PROPOSAL_V1';assert source_review['proposalIndexSha256']==args.index_sha256 and source_review['sourceActivationApproved']is True
 assert source_review['runtimeActionsApproved']is False and source_review['operationalAdmission']is False
 pins_bytes=raw(args.reviewed_pins,args.reviewed_pins_sha256);review_bytes=raw(args.native_root_review,args.native_root_review_sha256);pins=json.loads(pins_bytes);review=json.loads(review_bytes)
 assert pins['state']=='ROOT_REVIEWED_STREAM_CONSUMERS355_VALIDATION_BOOTSTRAP_V1'and review['reviewedPinsSha256']==args.reviewed_pins_sha256 and review['proposalIndexSha256']=='9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378'
 assert not pins['operationalAdmission']and not review['operationalAdmission']
 for label in ['normal-off','normal-runtime','gc-off','disabled-off']:
  p=pins['variants'][label];assert p and p['reviewRequired']is False and p['variant']==label
  for key in ['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']:assert p[key]==review['variants'][label][key]
 requirements=json.loads(raw(HERE/'external-authority-requirements.json'))['reviewedCurrentNativeFact']
 assert args.reviewed_pins_sha256==requirements['pinsSha256']and args.native_root_review_sha256==requirements['reviewSha256'],'Fresh source amendment required for a changed native authority'
 output=Path(args.output).resolve();assert output.parent==HERE.parent.resolve()and output.name=='release-gates-activated-v1','New immutable source sibling only'
 temporary=output.with_name(output.name+'.partial');assert not output.exists()and not temporary.exists()
 # Every basename (including sidecars) is bounded BEFORE any output/copy.
 for name in [output.name,temporary.name,*[row['path']for row in private]]:assert all(len(part.encode())<=255 for part in Path(name).parts)
 payload=json.loads(raw(HERE/'payload-files.json'))['files'];own();assert shutil.disk_usage(output.parent).free>=2*1024**3
 # mkdir is the exclusive final-name reservation. Rename may only replace this
 # owned empty reservation, never a pre-existing source family.
 output.mkdir();temporary.mkdir()
 try:
  for name in payload:
   assert shutil.disk_usage(output.parent).free>=800*1024**2
   source=safe(HERE,name);target=safe(temporary,name);target.parent.mkdir(parents=True,exist_ok=True)
   with target.open('xb')as stream:stream.write(raw(source))
  (temporary/'reviewed-pins.json').write_bytes(pins_bytes);(temporary/'root-review.json').write_bytes(review_bytes)
  (temporary/'source-root-review.json').write_bytes(raw(args.source_review,args.source_review_sha256))
  context=json.loads(raw(HERE/'context.json'))
  config={'schemaVersion':1,'state':'REVIEWED_CONSUMERS355_RELEASE_SOURCE_ACTIVATED_V1','proposalIndexSha256':args.index_sha256,'sourceReviewSha256':args.source_review_sha256,'bootstrapRoot':context['bootstrapRoot'],'bootstrapIndexSha256':context['bootstrapIndexSha256'],'nativeConfiguredSourceRoot':context['nativeConfiguredSourceRoot'],'nativeFrozenSourceRoot':context['nativeFrozenSourceRoot'],'componentToolRoot':str(output/'snapshot'),'pinsSha256':args.reviewed_pins_sha256,'rootReviewSha256':args.native_root_review_sha256,'lineageSha256':sha(raw(HERE/'lineage.json')),'operationalAdmission':False,'runtimeActionAuthority':None,'guestExecuted':False,'nativeExecuted':False}
  config_bytes=encoded(config);(temporary/'activation.json').write_bytes(config_bytes)
  # Boundary outputs are authenticated by the external generated index, avoiding
  # a self-hash cycle. Everything consumed is recorded with original context.
  inputs={}
  def add(path,digest,size,local=False):
   key=('L:'if local else'E:')+str(path);row={'path':str(path),'sha256':digest,'bytes':size,'local':local}
   if key in inputs:assert inputs[key]==row
   else:inputs[key]=row
  prep=json.loads(raw(HERE/'source-inputs.preparation.json'))
  for row in prep['files']:add(row['path'],row['sha256'],row['bytes'])
  for row in private:add(str(HERE/row['path']),row['sha256'],row['bytes'])
  add(str(HERE/'index.json'),args.index_sha256,len(raw(HERE/'index.json')))
  for path,digest in [(args.reviewed_pins,args.reviewed_pins_sha256),(args.native_root_review,args.native_root_review_sha256),(args.source_review,args.source_review_sha256)]:add(str(Path(path).absolute()),digest,len(raw(path,digest)))
  for p in sorted(temporary.rglob('*')):
   if p.is_file()and p!=temporary/'activation.json':add(str(p.relative_to(temporary)),sha(raw(p)),len(raw(p)),True)
  seal={'schemaVersion':1,'state':'ACTUAL_ORIGINAL_CONTEXT_AND_PUBLISHED_SOURCE_UNION','originalPreparationRoot':str(HERE),'inputs':list(inputs.values()),'snapshotMembers':sorted(str(p.relative_to(temporary/'snapshot'))for p in(temporary/'snapshot').rglob('*')if p.is_file()),'toolContextSha256':sha(raw(HERE/'tool-context.json')),'packageEndpointsSha256':sha(raw(HERE/'package-endpoints.json')),'selectedClosureSha256':sha(raw(HERE/'selected-closure.json')),'historicalControls':json.loads(raw(HERE/'historical-controls.sealed.json'))['controls'],'boundaryOutputs':['activation.json','native-preflight.mjs','input-freeze.json','source-receipt.json','index.json'],'oldNestedPreparationRowsFollowed':False}
  seal_bytes=encoded(seal);(temporary/'input-freeze.json').write_bytes(seal_bytes)
  compiled=raw(HERE/'native-preflight.template.mjs').decode().replace('@CONFIG_SHA@',sha(config_bytes)).replace('@INPUTS_SHA@',sha(seal_bytes));(temporary/'native-preflight.mjs').write_text(compiled)
  # Validate actual published bytes, not relocated original preparation rows.
  for row in seal['inputs']:checked(safe(temporary,row['path'])if row['local']else row['path'],row['sha256'],row['bytes'])
  own();raw(args.reviewed_pins,args.reviewed_pins_sha256);raw(args.native_root_review,args.native_root_review_sha256);raw(args.source_review,args.source_review_sha256)
  receipt={'schemaVersion':1,'state':'SOURCE_ONLY_CONSUMERS355_RELEASE_GATES_PUBLISHED','proposalIndexSha256':args.index_sha256,'configSha256':sha(config_bytes),'inputFreezeSha256':sha(seal_bytes),'consumedInputs':len(seal['inputs']),'sourcePublicationRoot':str(output),'originalInputContext':str(HERE),'nativeConfiguredSourceRoot':context['nativeConfiguredSourceRoot'],'componentToolRoot':str(output/'snapshot'),'operationalAdmission':False,'guestExecuted':False,'runtimeActionAuthority':None,'allInputsRecheckedBeforePublication':True,'priorPassReused':False}
  (temporary/'source-receipt.json').write_bytes(encoded(receipt))
  rows=[{'path':str(p.relative_to(temporary)),'sha256':sha(raw(p)),'bytes':len(raw(p))}for p in sorted(temporary.rglob('*'))if p.is_file()]
  (temporary/'index.json').write_bytes(encoded({'schemaVersion':1,'state':'CONSUMERS355_RELEASE_SOURCE_FAMILY','files':rows}))
  own();assert output.is_dir()and not output.is_symlink()and not any(output.iterdir());os.rename(temporary,output);print(json.dumps({'state':receipt['state'],'output':str(output),'indexSha256':sha(raw(output/'index.json')),'files':len(rows),'inputs':len(seal['inputs']),'guestExecuted':False,'operationalAdmission':False}))
 except BaseException:
  # An incomplete exclusive sibling is retained as failed preparation evidence.
  raise
if __name__=='__main__':main()
