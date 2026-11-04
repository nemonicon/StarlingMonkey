// Source and bundler checks only. Never import/evaluate the HTTP guest on Node.
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { runInNewContext } from 'node:vm';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const json=async path=>JSON.parse(await readFile(path));
const stripFirstComment=text=>text.slice(text.indexOf('\n')+1);

export async function checkHTTPRebase({here,source,base,tc,policies,selected,receipt}) {
  const v10='tests/node-compat/foundations/http-v10.mjs',v11='tests/node-compat/foundations/http-v11.mjs';
  assert.equal(stripFirstComment(await readFile(join(source,v11),'utf8')),stripFirstComment(await readFile(join(base,v10),'utf8')),'Complete v10 body retained');
  for(const path of[
    'tests/node-compat/foundations/assert-http-report.mjs',
    'tests/node-compat/foundations/assert-protected-abort-report.mjs',
    'tests/node-compat/foundation-add-abort/production-native-m0.10/preflight.mjs',
    'tests/node-compat/foundation-add-abort/production-native-m0.10/component.mjs',
    'tests/node-compat/foundation-add-abort/production-native-m0.10/public-cases.mjs',
    'tests/node-compat/foundation-add-abort/production-native-m0.10/node-results.json',
    'tests/node-compat/foundation-add-abort/production-native-m0.10/require.cjs',
  ])assert.equal(hash(await readFile(join(source,path))),hash(await readFile(join(base,path))),path);
  const protectedDirectory=join(source,'tests/node-compat/foundation-add-abort/production-native-m0.10');
  const oracle=await json(join(protectedDirectory,'node-results.json'));
  assert.equal(hash(await readFile(join(protectedDirectory,'public-cases.mjs'))),oracle.sourceSha256);
  assert.deepEqual(oracle.passed,{public:16,nested:4,receivers:9,total:29});
  assert.equal(oracle.publicCases.length+oracle.nestedOnceCases.length+oracle.receiverCases.length,29);
  const gapBytes=await readFile(join(protectedDirectory,'callback-return-results.json')),gap=JSON.parse(gapBytes);
  assert.equal(gap.observationCompleted,true);assert.equal(gap.nodeCompatibilityPassed,false);
  assert.deepEqual(gap.node.observed,{ordinary:1,protectedSignal:1,alreadyAborted:0});
  for(const target of [gap.jco,gap.wasmtime])assert.deepEqual(target.observed,{ordinary:0,protectedSignal:0,alreadyAborted:0});
  const inheritedGap={path:'tests/node-compat/foundation-add-abort/production-native-m0.10/callback-return-results.json',
    sha256:hash(gapBytes),node:gap.node.observed,jco:gap.jco.observed,wasmtime:gap.wasmtime.observed,
    kind:'Getter READ COUNTS only: getters return undefined; no callable-then or rejection test',closedByM011:false};

  const builderPath='tests/node-compat/wasmcloud/build-http.mjs';
  const builder=await readFile(join(source,builderPath),'utf8');
  assert(builder.indexOf('const admitted = await preflight();') < builder.indexOf('await componentizeSelectedHTTP('));
  for(const marker of ['assert.equal(admitted.report.engineSha256, hash(engineBytes));',
    'assert.equal(admitted.sourceRoot, engineSourceRoot);',
    "if (protectedAbortFoundationsFixture) assert.deepEqual(emittedImports, selectedInterfaces",
    'foundationOracles.protectedAbort = {',
    'receiverCases:oracle.receiverCases, nodeSymbol:oracle.targetSymbolInfo,',
  ])assert(builder.includes(marker),marker);
  const expression=/const protectedAbortFoundationsFixture = ([^;]+);/.exec(builder)?.[1];assert(expression);
  const fixtureSelection=[];
  for(const [file,expected]of [['http-v9.mjs',false],['http-v10.mjs',true],['http-v11.mjs',true],['http-v12.mjs',false]]) {
    const actual=runInNewContext(expression,{httpEntry:join(source,'tests/node-compat/foundations',file),resolve,here:join(source,'tests/node-compat/wasmcloud')});
    assert.equal(actual,expected,file);fixtureSelection.push({file,protectedGuardSelected:actual});
  }
  const allManifests=async root=>Promise.all(['node-v22.14.0','path.node-v22.14.0','events.node-v22.14.0','string-decoder.node-v22.14.0',
    'assert.node-v22.14.0','querystring.node-v22.14.0','util.node-v22.14.0','stream-web.node-v22.14.0']
    .map(name=>json(join(root,'builtins/node-compat/export-manifest.'+name+'.json'))));
  const bundleReports=[];
  const actualAudit=await json('/tmp/starling-node-compat/foundations-v10/http-joint/component-audit.json');
  for(const [variant,root,entry]of [['base',base,v10],['source',source,v11]]) {
    const manifests=await allManifests(root);
    const core=variant==='source'?selected:policies.validateCoreExpectations({...selected,
      coreVersion:'sm-node-22.14.0-m0.8',allocUnsafePolicy:'zeroed-no-pool-v1',
      manifestSha256:receipt.changes.find(file=>file.path==='builtins/node-compat/export-manifest.node-v22.14.0.json').before,
      sourceHashes:Object.fromEntries(Object.keys(selected.sourceHashes).map(path=>[path,receipt.ancestry.find(file=>file.path===path).sha256]))});
    const {makeOracleCorpus}=await import(pathToFileURL(join(root,'tests/node-compat/oracle.mjs')));
    const lexical=await json(join(root,'tests/node-compat/foundation-path/lexical-vectors.json')),
      globs=await json(join(root,'tests/node-compat/foundation-path/glob-vectors.json')),
      globReport=await json(join(root,'tests/node-compat/foundation-path/glob-results.json'));
    const pathManifest=manifests.find(value=>Object.hasOwn(value.modules,'node:path'));
    const streamManifest=manifests.find(value=>Object.hasOwn(value.modules,'node:stream/web'));
    const stream={names:streamManifest.modules['node:stream/web'].exports.slice().sort()};
    for(const [key,path]of Object.entries({codecs:'candidate/codec-node-results.json',guards:'candidate/byob-node-results.json',
      views:'candidate/typed-view-node-results.json',controllers:'candidate/controller-node-results.json',
      iteration:'iteration/node-results.json',data:'dataview/node-results.json'}))
      stream[key]=await json(join(root,'tests/node-compat/foundation-stream-web',path));
    assert.equal(hash(JSON.stringify(stream)),actualAudit.foundationOracles.streamWeb.oracleCorpusSha256);
    const virtual={
      'node-compat:core-expectations':policies.coreExpectationsForGuest(core),
      'node-compat:oracle-vectors':makeOracleCorpus(),'node-compat:entropy-policy':'runtime-only',
      'node-compat:path-oracles':{lexical,globs,denied:globReport.denied,acceptedAdversarial:globReport.acceptedAdversarial,
        exportNames:pathManifest.modules['node:path'].exports.slice().sort()},
      'node-compat:string-decoder-oracles':await json(join(root,'tests/node-compat/foundation-string-decoder/component-corpus.json')),
      'node-compat:stream-web-installed-oracles':stream,
    };
    const {createProfilePlugin}=await import(pathToFileURL(join(root,'tests/node-compat/profile-bundler.mjs')));
    const build=await tc.rolldown({input:join(root,entry),platform:'neutral',treeshake:false,plugins:[
      {name:'explicit-standard-http-only',resolveId(id){if(id==='wasi:http/types@0.2.10')return{id,external:true};if(id.startsWith('wasi:'))throw Error('Unselected WASI '+id);}},
      createProfilePlugin(tc.parseAst,{builtinManifests:manifests,virtualModules:Object.fromEntries(Object.entries(virtual).map(([id,value])=>[id,'export default '+JSON.stringify(value)+';']))}),
    ]});
    let bundle;try{const generated=await build.generate({format:'esm',codeSplitting:false});assert.equal(generated.output.length,1);bundle=generated.output[0];}finally{await build.close();}
    assert.deepEqual(bundle.imports.slice().sort(),actualAudit.bundleImports.slice().sort());
    const normalize=(id,prefix)=>id.replace(prefix,'<ROOT>').replace('/http-v11.mjs','/http-v10.mjs');
    const sourceIds=Object.keys(bundle.modules),actualPrefix=actualAudit.httpEntry.slice(0,-v10.length-1);
    assert.deepEqual(sourceIds.map(id=>normalize(id,root)).sort(),actualAudit.bundledModules.map(id=>normalize(id,actualPrefix)).sort(),'All prior source modules retained');
    assert(sourceIds.some(id=>id.endsWith('/foundation-add-abort/production-native-m0.10/component.mjs')));
    assert(sourceIds.some(id=>id.endsWith('/foundation-add-abort/production-native-m0.10/public-cases.mjs')));
    assert(sourceIds.some(id=>id.endsWith('/foundation-add-abort/production-native-m0.10/require.cjs.native-profile.mjs')));
    assert(sourceIds.every(id=>!/(?:run-component|harness|gc-component|run-gc)\.mjs|(?:^|\/)builtins\/node-compat\//.test(id)),'No fatal runner or builtin facade bundled');
    assert(!/reference-kernel|buffer-facade|createBufferModule|__require/.test(bundle.code));
    assert.match(bundle.code,/import\(id\)/);
    assert.match(bundle.code,/schema: 5/);
    await writeFile(join(here,'http-'+variant+'.source-bundle.mjs'),bundle.code);
    bundleReports.push({variant,entry,imports:bundle.imports,moduleIds:sourceIds,sha256:hash(bundle.code),
      allPriorModulesRetained:true,protected29Included:true,fatalRunnersExcluded:true,nativeAdaptersExcluded:true,componentized:false,
      virtualCorpora:Object.fromEntries(Object.entries(virtual).map(([id,value])=>[id,hash(JSON.stringify(value))]))});
  }
  const checker=await import(pathToFileURL(join(source,'tests/node-compat/foundations/assert-http-report.mjs')));
  const hostControls=[];
  for(const path of ['/tmp/starling-node-compat/foundations-v10/http-joint/wasmtime-v2/wasmtime-results.json',
    '/tmp/starling-node-compat/foundations-v10/http-joint-wasmcloud-results.json']) {
    const bytes=await readFile(path),report=JSON.parse(bytes);
    for(const response of report.responses)checker.checkFoundationsHTTPReport(response.body,actualAudit);
    hostControls.push({path,sha256:hash(bytes),existingM010ResponsesChecked:report.responses.length,m011RuntimeClaim:false});
  }
  return {schema:5,groups:oracle.passed,oracleSha256:hash(await readFile(join(protectedDirectory,'node-results.json'))),
    protectedFixtureBodyUnchanged:true,sharedCheckerAndPreflightUnchanged:true,guardBeforePackaging:true,fixtureSelection,
    bundles:bundleReports,hostControls,newHostImports:[],newEngineMetadataFabricated:false,
    inheritedGap,
    pending:'Actual combined m0.11 engine, guest, GC, final imports and both unmodified host gates remain mandatory'};
}
