"""Source-only selection data for Root's future genuine Next producer."""
from pathlib import Path
import hashlib
import json

OWN=Path(__file__).resolve().parent
REPO=OWN.parents[3]
def digest(data): return hashlib.sha256(data).hexdigest()
def row(path):
    data=path.read_bytes();return {'path':str(path),'sha256':digest(data),'bytes':len(data)}
def main():
    edits=json.loads((OWN/'localized-edits.json').read_text())
    policy_row=edits['basePolicy'];assert row(Path(policy_row['path']))==policy_row
    policy=json.loads(Path(policy_row['path']).read_text())
    base={r['path']:r['sha256']for r in policy['expectedNativeSourceManifest']}
    assert len(base)==357
    proposed=dict(base);overlay=[];added=[]
    for path in sorted((OWN/'after').rglob('*')):
        if not path.is_file():continue
        relative=str(path.relative_to(OWN/'after'));observed=row(path)
        overlay.append({'path':relative,'source':observed,'baselineSha256':base.get(relative)})
        if relative not in base:added.append(relative)
        proposed[relative]=observed['sha256']
    assert len(added)==10 and len(proposed)==367
    canonical=[{'path':p,'sha256':s}for p,s in sorted(proposed.items())]
    manifest_path=OWN/'after/builtins/node-compat/export-manifest.async-hooks.node-v22.14.0.json'
    manifest=json.loads(manifest_path.read_text())
    selection={'path':'builtins/node-compat/export-manifest.async-hooks.node-v22.14.0.json',
               'sha256':row(manifest_path)['sha256'],'profileVersion':manifest['profileVersion']}
    result={'schemaVersion':1,'state':'SOURCE_ONLY_NATIVE_ALS_V2_SELECTION_FOR_NEW_NEXT_GENERATION',
      'basePolicy':policy_row,'localizedEdits':row(OWN/'localized-edits.json'),
      'overlay':overlay,'addedPaths':added,'onlyAlsDeltaSourceFiles':367,
      'onlyAlsDeltaCanonicalManifestSha256':digest(json.dumps(canonical,separators=(',',':')).encode()),
      'onlyAlsDeltaPolicyCpp':policy['expectedCompilation']['policyCpp']+3,
      'onlyAlsDeltaCompileDatabaseRows':policy['expectedCompilation']['compileDatabaseRows']+3,
      'arithmeticIsObservedNewBuild':False,
      'retainedBaseWholeManifestSelections':policy['selectedModuleManifests'],
      'addedWholeManifestSelection':selection,'onlyAlsDeltaWholeManifestSelections':13,
      'requiredRequestedAndObservedCMakeOptions':{'ENABLE_BUILTIN_NODE_COMPAT':'ON',
         'NODE_COMPAT_ASYNC_LOCAL_STORAGE':'ON','NODE_COMPAT_INTERNAL_TICKS':'ON',
         'NODE_COMPAT_STRICT_INITIALIZATION':'ON','ENABLE_JS_DEBUGGER':'OFF'},
      'requiredAbsentCompilerDefinitions':['DEBUG','ENABLE_JS_DEBUGGER','NODE_COMPAT_GC_STRESS',
          'NODE_COMPAT_OOM_TESTING','NODE_CRYPTO_AUDITED_BORROW'],
      'requiredDefinition':'NODE_COMPAT_ASYNC_LOCAL_STORAGE=1',
      'definitionConsumers':['all engine/runtime and builtin extension_api consumers',
         'host_api explicit private definition','separate ComponentizeJS embedding via extension_api'],
      'newRawMetadataFields':['nativeAsyncLocalStorageEnabled','nativeAsyncLocalStoragePolicy'],
      'newPolicyMustBind':['all source/manifest/factory/header/generator pins and canonical native list',
         'requested AND observed CMake flag; all actual CPP and separate embedding command definitions',
         'selected whole async_hooks manifest; exact7named/default8 and63 metadata provider constants',
         'legacy Promise queue selection before self-hosted/application initialization and actual SM pin',
         'neutral server entry/fresh owner boundary/registration context/private pinned job ABI',
         'fatal allocation metadata OOM; fail-closed no off-thread/delayed dispatch and explicit limits',
         'original exception/tick/event policy and quiescent pre-snapshot/reset guards'],
      'finalNextSourceCountsAndRawFieldSet':None,
      'requiredFutureProducer':'Root-owned genuine source composer/build emitter/admission model in fresh Source/WORK roots',
      'old83FrameOrBootstrapMayBeRelabeled':False,'oldModuleSelectionMayBeCountCast':False,
      'oldSourcesOrFreezesMayBeOverwritten':False,
      'rootAuthority':None,'nativeBuild':None,'nativeMetadata':None,'component':None,'runtime':None}
    (OWN/'profile-selection.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'overlayFiles':len(overlay),'addedSourceFiles':len(added),
                      'onlyAlsDeltaSourceFiles':367,'onlyAlsDeltaWholeManifestSelections':13,'nativeBuildInvoked':False}))
if __name__=='__main__':main()
