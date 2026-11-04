"""Future SOURCE-only versioned publication. Never invokes owner code/helpers."""
from pathlib import Path
import argparse,hashlib,json,os,shutil
HERE=Path(__file__).parent.resolve();BASE=HERE.with_name('release-gates-candidate-v1');BASE_SHA='a74dc603f7e42384892c9f4b69a2ba131a87a80daa38da19e91bbc2c099e5372';CONTEXT=HERE.with_name('release-gates-context-amendment-v1');CONTEXT_SHA='9080e48fbccaf74835bfb8c8ef54c91b8df54ff5eb6e4c2cdc1c83443ad79b70'
def h(raw):return hashlib.sha256(raw).hexdigest()
def need(value,message):
    if not value:raise ValueError(message)
def safe(root,name):
    need(type(name)is str and name and not Path(name).is_absolute()and '\0'not in name and '\\'not in name and all(part not in('','.','..')and len(part.encode())<=255 for part in name.split('/')),'Finite local path');p=root
    for part in name.split('/'):p/=part;need(not p.is_symlink(),'No local symlink')
    return p
def checked(path,sha=None,bytes=None,collect=True):
    p=Path(path);need(p.is_file()and not p.is_symlink(),'Ordinary input');s=p.stat();need(bytes is None or s.st_size==bytes,'Exact bytes');digest=hashlib.sha256();pieces=[]
    with p.open('rb')as f:
        for raw in iter(lambda:f.read(1048576),b''):
            digest.update(raw)
            if collect:pieces.append(raw)
    after=p.stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'Stable input');need(sha is None or digest.hexdigest()==sha,'Exact SHA');return b''.join(pieces)if collect else None
def load(path,sha=None):return json.loads(checked(path,sha))
def encoded(value):return(json.dumps(value,indent=2)+'\n').encode()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--index-sha256',required=True);parser.add_argument('--source-review',required=True);parser.add_argument('--source-review-sha256',required=True);parser.add_argument('--reviewed-pins',required=True);parser.add_argument('--reviewed-pins-sha256',required=True);parser.add_argument('--native-root-review',required=True);parser.add_argument('--native-root-review-sha256',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    own=load(HERE/'index.json',args.index_sha256);base=load(BASE/'index.json',BASE_SHA);context_parent=load(CONTEXT/'index.json',CONTEXT_SHA)
    def recheck():
        checked(HERE/'index.json',args.index_sha256);checked(BASE/'index.json',BASE_SHA)
        for root,index in[(HERE,own),(BASE,base),(CONTEXT,context_parent)]:
            for row in index['files']:checked(safe(root,row['path']),row['sha256'],row['bytes'],False)
        for row in load(BASE/'source-inputs.preparation.json')['files']:checked(row['path'],row['sha256'],row['bytes'],False)
        for row in load(HERE/'source-inputs.json')['files']:checked(row['path'],row['sha256'],row['bytes'],False)
    recheck();source_review=load(args.source_review,args.source_review_sha256)
    need(source_review['state']=='ROOT_REVIEWED_CONSUMERS355_RELEASE_REPORT_DATA_AMENDMENT_V1'and source_review['proposalIndexSha256']==args.index_sha256 and source_review['parentProposalIndexSha256']==BASE_SHA and source_review['contextAmendmentIndexSha256']==CONTEXT_SHA,'New exact context amendment authority')
    need(source_review['sourceActivationApproved']is True and source_review['runtimeActionsApproved']is False and source_review['operationalAdmission']is False and source_review['sourcePromotionAllowed']is False,'Source only; no runtime/promotion')
    pins_bytes=checked(args.reviewed_pins,args.reviewed_pins_sha256);review_bytes=checked(args.native_root_review,args.native_root_review_sha256);requirements=load(BASE/'external-authority-requirements.json')['reviewedCurrentNativeFact']
    need(args.reviewed_pins_sha256==requirements['pinsSha256']and args.native_root_review_sha256==requirements['reviewSha256'],'Unchanged actual355 native authority')
    pins=json.loads(pins_bytes);review=json.loads(review_bytes);need(pins['sourceFiles']==355 and pins['externalSources']==3 and pins['operationalAdmission']is False and review['operationalAdmission']is False,'Genuine355 validation only')
    for label in['normal-off','normal-runtime','gc-off','disabled-off']:
        pin=pins['variants'][label];need(pin['reviewRequired']is False and pin['variant']==label,'Reviewed tuple')
        for key in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']:need(pin[key]==review['variants'][label][key],'Actual Root tuple')
    output=Path(args.output).resolve();need(output.parent==HERE.parent and output.name=='release-gates-activated-v3','Fresh versioned output');temporary=output.with_name(output.name+'.partial');need(not output.exists()and not temporary.exists()and not output.is_symlink()and not temporary.is_symlink(),'No existing output/partial/symlink')
    payload=load(BASE/'payload-files.json')['files']+['snapshot/tests/node-compat/foundation-util/run-native-node.mjs','report-data-closure.json'];overrides={'native-preflight.template.mjs':CONTEXT/'native-preflight.template.after.mjs','run-gates.mjs':HERE/'run-gates.after.mjs','selected-closure.json':HERE/'selected-closure.after.json','snapshot-origins.json':HERE/'snapshot-origins.after.json','snapshot/tests/node-compat/foundation-util/run-native-node.mjs':HERE/'data/run-native-node.mjs','report-data-closure.json':HERE/'report-data-closure.json'}
    need(shutil.disk_usage(output.parent).free>=2*1024**3,'Below2GiB source copy guard');output.mkdir();temporary.mkdir()
    for name in payload:
        need(shutil.disk_usage(output.parent).free>=800*1024**2,'Below800MiB during source copy')
        target=safe(temporary,name);target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb')as f:f.write(checked(overrides.get(name,BASE/name)))
    for name,path in[('source-contexts.mjs',CONTEXT/'source-contexts.mjs'),('reviewed-pins.json',Path(args.reviewed_pins)),('root-review.json',Path(args.native_root_review)),('source-root-review.json',Path(args.source_review))]:
        with(temporary/name).open('xb')as f:f.write(checked(path))
    context=load(BASE/'context.json');config={'schemaVersion':1,'state':'REVIEWED_CONSUMERS355_RELEASE_SOURCE_ACTIVATED_V1','proposalIndexSha256':args.index_sha256,'parentProposalIndexSha256':BASE_SHA,'contextAmendmentIndexSha256':CONTEXT_SHA,'reportDataClosureSha256':h(checked(HERE/'report-data-closure.json')),'sourceReviewSha256':args.source_review_sha256,'bootstrapRoot':context['bootstrapRoot'],'bootstrapIndexSha256':context['bootstrapIndexSha256'],'nativeConfiguredSourceRoot':context['nativeConfiguredSourceRoot'],'admissionSourceRoot':context['nativeConfiguredSourceRoot'],'nativeFrozenSourceRoot':context['nativeFrozenSourceRoot'],'runtimeSourceRoot':context['nativeFrozenSourceRoot'],'componentToolRoot':str(output/'snapshot'),'pinsSha256':args.reviewed_pins_sha256,'rootReviewSha256':args.native_root_review_sha256,'lineageSha256':h(checked(BASE/'lineage.json')),'operationalAdmission':False,'runtimeActionAuthority':None,'guestExecuted':False,'nativeExecuted':False}
    config_bytes=encoded(config);(temporary/'activation.json').write_bytes(config_bytes)
    inputs={}
    def add(path,sha,bytes,local=False):
        key=('L:'if local else'E:')+str(path);r={'path':str(path),'sha256':sha,'bytes':bytes,'local':local};need(key not in inputs or inputs[key]==r,'Exact duplicate input');inputs[key]=r
    for r in load(BASE/'source-inputs.preparation.json')['files']:add(r['path'],r['sha256'],r['bytes'])
    for r in load(HERE/'source-inputs.json')['files']:add(r['path'],r['sha256'],r['bytes'])
    for root,index,digest in[(BASE,base,BASE_SHA),(CONTEXT,context_parent,CONTEXT_SHA),(HERE,own,args.index_sha256)]:
        for r in index['files']:add(str(root/r['path']),r['sha256'],r['bytes'])
        add(str(root/'index.json'),digest,(root/'index.json').stat().st_size)
    for path,digest in[(args.source_review,args.source_review_sha256),(args.reviewed_pins,args.reviewed_pins_sha256),(args.native_root_review,args.native_root_review_sha256)]:add(str(Path(path).absolute()),digest,Path(path).stat().st_size)
    for p in sorted(temporary.rglob('*')):
        if p.is_file()and p!=temporary/'activation.json':b=checked(p);add(str(p.relative_to(temporary)),h(b),len(b),True)
    seal={'schemaVersion':1,'state':'ACTUAL_ORIGINAL_CONTEXT_AND_PUBLISHED_SOURCE_UNION','originalPreparationRoot':str(BASE),'sourceAmendmentRoot':str(HERE),'contextAmendmentRoot':str(CONTEXT),'inputs':list(inputs.values()),'snapshotMembers':sorted(str(p.relative_to(temporary/'snapshot'))for p in(temporary/'snapshot').rglob('*')if p.is_file()),'toolContextSha256':h(checked(temporary/'tool-context.json')),'packageEndpointsSha256':h(checked(temporary/'package-endpoints.json')),'selectedClosureSha256':h(checked(temporary/'selected-closure.json')),'historicalControls':load(BASE/'historical-controls.sealed.json')['controls'],'boundaryOutputs':['activation.json','native-preflight.mjs','input-freeze.json','source-receipt.json','index.json'],'oldNestedPreparationRowsFollowed':False}
    seal_bytes=encoded(seal);(temporary/'input-freeze.json').write_bytes(seal_bytes);compiled=checked(CONTEXT/'native-preflight.template.after.mjs').decode().replace('@CONFIG_SHA@',h(config_bytes)).replace('@INPUTS_SHA@',h(seal_bytes));(temporary/'native-preflight.mjs').write_text(compiled)
    for r in seal['inputs']:checked(safe(temporary,r['path'])if r['local']else r['path'],r['sha256'],r['bytes'],False)
    recheck();checked(args.source_review,args.source_review_sha256);checked(args.reviewed_pins,args.reviewed_pins_sha256);checked(args.native_root_review,args.native_root_review_sha256)
    receipt={'schemaVersion':1,'state':'SOURCE_ONLY_CONSUMERS355_RELEASE_GATES_PUBLISHED','proposalIndexSha256':args.index_sha256,'parentProposalIndexSha256':BASE_SHA,'configSha256':h(config_bytes),'inputFreezeSha256':h(seal_bytes),'consumedInputs':len(inputs),'sourcePublicationRoot':str(output),'originalInputContext':str(BASE),'sourceAmendmentContext':str(HERE),'contextAmendmentRoot':str(CONTEXT),'reportDataClosureSha256':h(checked(HERE/'report-data-closure.json')),'admissionSourceRoot':config['admissionSourceRoot'],'runtimeSourceRoot':config['runtimeSourceRoot'],'nativeConfiguredSourceRoot':config['nativeConfiguredSourceRoot'],'componentToolRoot':config['componentToolRoot'],'operationalAdmission':False,'guestExecuted':False,'runtimeActionAuthority':None,'allInputsRecheckedBeforePublication':True,'priorPassReused':False}
    (temporary/'source-receipt.json').write_bytes(encoded(receipt));rows=[{'path':str(p.relative_to(temporary)),'sha256':h(checked(p)),'bytes':p.stat().st_size}for p in sorted(temporary.rglob('*'))if p.is_file()];(temporary/'index.json').write_bytes(encoded({'schemaVersion':1,'state':'CONSUMERS355_RELEASE_SOURCE_FAMILY','files':rows}));recheck()
    need(output.is_dir()and not output.is_symlink()and not any(output.iterdir()),'Owned empty reservation only');os.rename(temporary,output);print(json.dumps({'state':receipt['state'],'output':str(output),'indexSha256':h(checked(output/'index.json')),'files':len(rows),'inputs':len(inputs),'guestExecuted':False,'operationalAdmission':False}))
if __name__=='__main__':main()
