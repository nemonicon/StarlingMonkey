"""Independent post-promotion DATA-only verification. No old owner is invoked."""
import hashlib,importlib.util,json,os,stat,subprocess
from pathlib import Path
HERE=Path(__file__).parent
CLASSIC=HERE.parent
REPO=Path('/Users/dan/dev/StarlingMonkey')
ADOPTION=CLASSIC/'production-adoption-v1'
PLAN=ADOPTION/'artifact-closure-plan-v1'
ARCHIVE=Path('/tmp/starling-node-compat/classic-artifact-preservation-pending-v1').resolve(strict=True)
checks=[];witnesses={}
def need(v,m):
    if not v:raise AssertionError(m)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path,expected=None,size=None):
    path=Path(path);before=path.lstat();need(stat.S_ISREG(before.st_mode),'Regular witness')
    h=hashlib.sha256();data=[]
    with path.open('rb')as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b);data.append(b)
    after=path.lstat();need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'Stable witness')
    need(expected is None or h.hexdigest()==expected,'Witness hash: '+str(path));need(size is None or before.st_size==size,'Witness bytes')
    witnesses[str(path)]={'path':str(path),'sha256':h.hexdigest(),'bytes':before.st_size};return b''.join(data)
def load(p,h=None,n=None):return json.loads(read(p,h,n))
def record(name,**v):checks.append({'check':name,'passed':True,**v})
review=load(ADOPTION/'five-file-corrected-classic-source-promotion-root-review-v1.json','30bdf0dc728ca7fa516f6964ed4a701be4fc4dc9b8de756cf6b39cd8f14604f9')
result=load(ADOPTION/'five-file-corrected-classic-source-promotion-root-results-v1.json','879aa3e2b4f0b60df69563839957f40b14cd0497ec33aae53078034fbdbdce7d')
need(review['sourcePromotionAllowed']is True and review['releaseCheckpointAcceptanceAllowed']is False and review['consumers355OrZlib350PromotionAllowed']is False,'Exact five-only authority')
need(result['priorGitApplyCheckRawExitCode']==result['gitApplyRawExitCode']==0 and result['commitCreated']is False,'Root exact successful source action')
mapping=load(PLAN/'rollforward-map.json')
need(len(mapping['files'])==len(review['changes'])==len(result['exactPromotedFiles'])==5,'Exact five paths')
for target,authorized,observed in zip(mapping['files'],review['changes'],result['exactPromotedFiles']):
    path=REPO/target['path'];need(authorized['path']==target['path']and observed['path']==str(path),'Same finite path')
    now=read(path,target['afterSha256'],target['afterBytes'])
    need(now==read(PLAN/target['afterStagedPath'],target['afterSha256'],target['afterBytes']),'Exact staged afterimage')
    read(PLAN/target['beforeStagedPath'],target['beforeSha256'],target['beforeBytes'])
    need(oct(stat.S_IMODE(path.lstat().st_mode))==authorized['modeBefore'],'Mode preserved')
    need(observed['sha256']==target['afterSha256']and observed['bytes']==target['afterBytes'],'Root observed afterimage')
record('exactFiveAfterimagesModesAndTenOriginalStagedImages',paths=[r['path']for r in mapping['files']])
baseline='54b3329b3ce818fd1f244e871e9c259b63667cda'
head=subprocess.run(['git','rev-parse','HEAD'],cwd=REPO,text=True,capture_output=True,check=True)
need(head.stdout.strip()==review['baselineHead']==result['baselineGitHead']==baseline,'HEAD unchanged')
selector=mapping['unchangedSelector'];read(REPO/selector['path'],selector['sha256'])
record('unchangedHeadAndSelector',gitHead=baseline,newCommitCreated=False,selectorSha256=selector['sha256'])

metadata=[]
for row in review['productionMetadata']:
    metadata.append(load(row['path'],row['sha256'],row['bytes']))
native=metadata[0]['sourceManifest'];need(len(native)==342 and all(m['sourceManifest']==native for m in metadata),'Same four actual342 manifests')
new_three={r['path']for r in mapping['files']if r['native']}
need(len(new_three)==3,'Three native changes')
for row in native:read(REPO/row['path'],row['sha256'])
need(len(review['unchangedNativeInputs'])==339,'Original unchanged339 witness')
for row in review['unchangedNativeInputs']:read(row['path'],row['sha256'],row['bytes'])
for scope in ['foundation-zlib/native-integration-candidate-v4','foundation-stream-consumers/production-text-json-candidate-v2']:
    policy=load(REPO/'tests/node-compat'/scope/'policy.json')
    extras={r['path']for r in policy['expectedNativeSourceManifest']}-{r['path']for r in native}
    need(len(extras)==(8 if scope.startswith('foundation-zlib/') else 13),'Exact child extension paths')
    need(not any((REPO/p).exists()for p in extras),'No live350/355 additional native file overlay')
record('current342AllMatchFourProductionMetadataAnd339Unchanged',currentNativeInputs=342,unchangedOtherNativeInputs=339,zlibOrConsumersRootOverlay=False)

archive_before=ARCHIVE.lstat();need(stat.S_IMODE(archive_before.st_mode)==0o700,'Private root mode')
index=load(ARCHIVE/'index.json','1934c03e75e23a24e35e944502692a7cde774e5f49a132a63c1686cc5d7babde')
completion=load(ARCHIVE/'completion.json','0177ec7f2c9daf2f2376af997dd7a798ebe7e96e8068ee3c68fc005a773b1b1b')
load(ARCHIVE/'results.json','306ae3e4516f13870f821d3ceb33cf2ee8206528abaa0abc7d7c8af2a4cbf86f')
need(completion['rootIdentity']=={'device':archive_before.st_dev,'inode':archive_before.st_ino},'Same archive root')
expected={r['path']:r for r in index['files']};need(len(expected)==21680,'Archive index count')
actual=set();hashed=0
for directory,dirs,files in os.walk(ARCHIVE,followlinks=False):
    need(not any((Path(directory)/n).is_symlink()for n in dirs+files),'No archive symlinks')
    for name in files:
        path=Path(directory)/name;relative=str(path.relative_to(ARCHIVE));actual.add(relative)
        info=path.lstat();need(stat.S_ISREG(info.st_mode)and info.st_nlink==1 and stat.S_IMODE(info.st_mode)==0o600,'Archive regular private copy')
        if relative in('index.json','completion.json'):continue
        row=expected[relative];h=hashlib.sha256()
        with path.open('rb')as f:
            for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
        after=path.lstat();need((info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'Stable archive bytes')
        need(h.hexdigest()==row['sha256']and info.st_size==row['bytes'],'Archive byte drift')
        hashed+=info.st_size
need(actual==set(expected)|{'index.json','completion.json'}and len(actual)==21682,'Whole unchanged archive membership')
record('all21682PrivateArchiveFilesStillMatchActualIndex',regularFiles=21682,indexedBytesRehashed=hashed,oldOriginsRehashed=False)
print(json.dumps({'stage':'allArchiveBytesStillUnchanged','regularFiles':21682}),flush=True)
objects=load(ARCHIVE/'maps/original-paths.json')
for r in mapping['files']:
    old=[v for v in objects if v['descriptor']['path']==str(REPO/r['path'])and v['descriptor']['sha256']==r['beforeSha256']]
    need(len(old)==1,'Original five path descriptor retained')
    read(ARCHIVE/old[0]['storage']['archivePath'],r['beforeSha256'],r['beforeBytes'])
packet=load(PLAN/'index.json','96b4536ddb54484d665d93d64b6bc1af794dda977c189f50222238bad73a716e')
for r in packet['files']:read(PLAN/r['path'],r['sha256'],r['bytes'])
patch=read(PLAN/'rollforward.UNAPPLIED.patch').decode()
need({line[6:]for line in patch.splitlines()if line.startswith('+++ b/')}=={r['path']for r in mapping['files']},'Patch only exact five destinations')
record('originalBeforeFiveArchiveCopiesTenImagesAndOriginal96bPatchUnchanged',beforeGenerationsRemainArchived=True,historicalAppliedFalseLabelsNotRewritten=True)

policy=load(ADOPTION/'root-source-context-rollforward-policy-v1.json','20a32c37de8fc1fe3bcbdecaa751377918d921f79ba6bcef91eb8943895eecc6')
need(policy['sourcePromotionAllowed']is False and policy['archiveAcceptanceAllowed']is False and len(policy['acceptedTypedHoldDecisions'])==12,'Historical20a not rewritten')
acceptance=review['preservationAcceptance'];accepted=load(acceptance['path'],acceptance['sha256'],acceptance['bytes'])
reader_path=ADOPTION/'artifact-closure-current-context-amendment-v1/archive-context-reader.py'
read(reader_path,'adb38b97aff2ddcd6fe7e5128e483efd1017405ca5ade34bb0e79e3865139800')
spec=importlib.util.spec_from_file_location('postpromotion_data_only_reader',reader_path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
maprow=expected['maps/context-map.json'];old_tuples=[]
with module.ArchiveContextReader(str(ARCHIVE),'maps/context-map.json',maprow['sha256'])as reader:
    for (context,path,digest),row in reader.entries.items():
        if not context.startswith('zlib-old-five-'):continue
        need(path in{str(REPO/r['path'])for r in mapping['files']},'Exact old Root five literal context path')
        old_tuples.append(reader.verify(context,path,digest))
need(len(old_tuples)==60 and len({r['contextId']for r in old_tuples})==12,'All12 old contexts preserve five bytes each')
record('all12OldZlibContextsHeldAnd60OldTuplesResolveOnlyArchivedBytes',selectedOldTuples=60,originalFilesystemOpenedByArchiveReader=False,oldPreflightsInvoked=False,historicalPolicyPermissionUnchanged=True,separateNewPromotionReviewSha256='30bdf0dc728ca7fa516f6964ed4a701be4fc4dc9b8de756cf6b39cd8f14604f9')
for p,h in [(REPO/'tests/node-compat/milestones/foundations-v12/index.json','d841065dd1ce8337520d461f7e041aa33438c3df693a1c5ef6137af430e8cd6d'),(ADOPTION/'process-rss-supplement-v2-root-results.json','203b7e6b7b1bee8675bc52280c7b30fb8b8da82461e4e5b9167535862fd08be5'),(CLASSIC/'independent-process-rss-supplement-v2-results-review-v1/index.json','14611521cb3f44d5ec0cea7ef61eb8821d8fe7f8d8a53aab197209467bca2fe5')]:read(p,h)
need((ARCHIVE.lstat().st_dev,ARCHIVE.lstat().st_ino)==(archive_before.st_dev,archive_before.st_ino),'Archive root remains same')
record('v12AndMemoryEvidenceDigestsRemainHistoricalNoNewReleaseAcceptance',runtimeExecuted=False,releaseCheckpointAccepted=False)
out={'schemaVersion':1,'state':'INDEPENDENT_EXACT_FIVE_CLASSIC_SOURCE_PROMOTION_VERIFIED','verifiedPassed':True,'rootPromotionResultSha256':'879aa3e2b4f0b60df69563839957f40b14cd0497ec33aae53078034fbdbdce7d','rootPromotionReviewSha256':'30bdf0dc728ca7fa516f6964ed4a701be4fc4dc9b8de756cf6b39cd8f14604f9','checks':checks,'currentNativeSourceInputs':342,'unchangedOtherNativeInputs':339,'changedRootPaths':5,'archiveFilesRehashed':21682,'oldSourcePhysicalInputsRehashed':False,'oldZlibContextsHeld':12,'oldContextTupleBytesVerified':60,'ownerHelpersOrPreflightsInvoked':False,'nativeGuestHostOrTimingActionsInvoked':False,'sourcePromotionPerformedByReviewer':False,'archiveOrHistoricalEvidenceModified':False,'runtimeAcceptanceClaim':False,'releaseCheckpointAcceptanceIssued':False}
for name,value in [('results.json',out),('byte-witnesses.json',{'schemaVersion':1,'files':list(witnesses.values())}),('old-zlib-archived-tuples.json',{'schemaVersion':1,'rows':old_tuples,'oldProgramsRerunnable':False})]:
    with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps({'passed':len(checks),'nativeSourceInputs':342,'ownerActions':False}))
