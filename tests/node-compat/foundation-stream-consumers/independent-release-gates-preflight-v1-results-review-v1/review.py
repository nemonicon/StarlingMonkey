"""Read-only actual failure audit; never imports a preflight/owner helper."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).parent.resolve();S=HERE.parent;OUT=Path('/tmp/starling-node-compat/consumers355-release-gates-preflight-v1-root');FAMILY=S/'release-gates-activated-v1';rows=[]
def h(raw):return hashlib.sha256(raw).hexdigest()
def read(path,expected=None):
    p=Path(path);assert p.is_file()and not p.is_symlink();raw=p.read_bytes();assert expected is None or h(raw)==expected;rows.append({'path':str(p.resolve()),'sha256':h(raw),'bytes':len(raw)});return raw
def load(path,sha=None):return json.loads(read(path,sha))
root=load(S/'release-gates-preflight-v1-root-failure-v2.json','bc1cd16985850ef243dc14295d75af655bed9eb6fe06e66bfb414d0565efbcf7')
read(root['recordFieldCorrection']['original'],root['recordFieldCorrection']['sha256']);assert root['readOnlyAdmissionHelpersExecuted']is True
for key in['externalTerminal','externalStdout','externalStderr','sourceAuthority']:
    r=root[key];assert len(read(r['path'],r['sha256']))==r['bytes']
aggregate=load(OUT/'terminal.json');normal=load(OUT/'normal-off/terminal.json');stderr=read(OUT/'normal-off/stderr.log','f9ba1a9e7798bd753f6b7baf959d5cf3d93dbcb2525ee5a791d0fb4c797a5a57');stdout=read(OUT/'normal-off/stdout.log')
assert normal['rawExitCode']==1 and normal['pid']==25354 and not normal['timeout']and not stdout and normal['readOnly']is True and normal['guestOrComponentExecuted']is False
assert 'STOPPED_AFTER_FIRST' in str(aggregate.get('state',''))
assert not(OUT/'normal-runtime/terminal.json').exists()and not(OUT/'gc-off/terminal.json').exists()
assert normal['argv'][1]==str(FAMILY/'entry.mjs')and normal['argv'][-2:]==['preflight','normal-off']
assert b"ENOENT"in stderr and b"native-freeze/source/tests"in stderr and b"metadata-admission.mjs:39"in stderr
config=load(FAMILY/'activation.json');pins=load(FAMILY/'reviewed-pins.json');pin=pins['variants']['normal-off'];assert pin['sourceRoot'].endswith('/native-freeze/source')and not(Path(pin['sourceRoot'])/'tests').exists()
boot=Path(config['bootstrapRoot']);admission=read(boot/'artifact-tools/metadata-admission.mjs').decode();bootstrap=read(boot/'artifact-tools/bootstrap-preflight.mjs').decode();classifier=read(boot/'artifact-tools/bootstrap-classifier.py').decode();build=read(boot/'artifact-tools/build-manifests.mjs').decode();template=read(FAMILY/'native-preflight.template.mjs').decode()
assert 'for(const row of tools.toolDependencies)await regularBelow(sourceRoot' in admission
assert 'await admit(native.metadata,variant,native.sourceRoot)'in template
assert 'sourceRoot:actual.sourceRoot'in bootstrap and 'configuredSourceRoot'not in bootstrap
assert "'configuredSourceRoot':str(common.REPO)"in classifier and "str(common.REPO)"in classifier
assert "const core=validateCoreExpectations({schema:1"in build and 'sourceHashes' in build
tools=load(boot/'artifact-tools/tool-pins.json');tooltests=[r for r in tools['toolDependencies']if r['path'].startswith('tests/')];assert tooltests
missing=tooltests[0];actual=Path(config['nativeConfiguredSourceRoot'])/missing['path'];assert h(read(actual))==missing['sha256']
source_index=load(FAMILY/'index.json','10d6df0205a17394343be49864f4ed82847292397732b5f821090ec78d94289b')
assert source_index['schemaVersion']==1
result={'schemaVersion':1,'state':'INDEPENDENT_CONSUMERS355_PREFLIGHT_CONTEXT_FAILURE_VERIFIED_V1','generatedSourceIndexSha256':'10d6df0205a17394343be49864f4ed82847292397732b5f821090ec78d94289b','normalOffRawExitCode':1,'normalOffStdoutBytes':0,'normalOffStderrBytes':len(stderr),'normalRuntimeStarted':False,'gcOffStarted':False,'threeModePreflightPassed':False,'failureKind':'caller-passed-native-only-frozen-root-to-full-configured-native-and-tool-admission','configuredAdmissionRoot':config['nativeConfiguredSourceRoot'],'frozenRuntimeRoot':pin['sourceRoot'],'actualAdmissionRequiresToolDependencies':len(tools['toolDependencies']),'bootstrapConfiguredAdmissionInferredFromControlFlowOnly':True,'standaloneBootstrapResultPersistedByThisAttempt':False,'nativeArtifactOrCodecSemanticFailureEstablished':False,'metadataProjection':False,'rootAdmissionHelpersExecuted':True,'reviewerOwnerHelpersImported':False,'guestComponentNativeBuildHostOrTimingExecutedByReviewer':False,'runtimeAcceptanceClaim':False,'oldSourceAndRootAttemptUnmodified':True}
(HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n');(HERE/'source-references.json').write_text(json.dumps({'schemaVersion':1,'files':rows},indent=2)+'\n');print(json.dumps(result))
