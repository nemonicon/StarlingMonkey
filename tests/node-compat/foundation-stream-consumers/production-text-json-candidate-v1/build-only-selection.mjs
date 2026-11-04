// Future source/build evidence only. Never opens an engine or admits execution.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {validateStreamConsumersBuildSourceAdmission} from '../../stream-consumers-admission.mjs';
export function selectConsumerBuildManifests(metadata,options){
  const result=validateStreamConsumersBuildSourceAdmission(metadata,options);
  assert(result&&result.sourceInputs===355);
  const choices=[
    [true,'builtins/node-compat/export-manifest.node-v22.14.0.json'],
    [metadata.pathEnabled,'builtins/node-compat/export-manifest.path.node-v22.14.0.json'],
    [metadata.eventsEnabled,'builtins/node-compat/export-manifest.events.node-v22.14.0.json'],
    [metadata.stringDecoderEnabled,'builtins/node-compat/export-manifest.string-decoder.node-v22.14.0.json'],
    [metadata.assertEnabled,'builtins/node-compat/export-manifest.assert.node-v22.14.0.json'],
    [metadata.querystringEnabled,'builtins/node-compat/export-manifest.querystring.node-v22.14.0.json'],
    [metadata.utilEnabled,'builtins/node-compat/export-manifest.util.node-v22.14.0.json'],
    [metadata.streamWebEnabled,'builtins/node-compat/export-manifest.stream-web.node-v22.14.0.json'],
    [metadata.classicStreamsEnabled,'builtins/node-compat/classic-streams/export-manifest.classic-streams.node-v22.14.0.json'],
    [metadata.zlibEnabled,'builtins/node-compat/export-manifest.zlib.node-v22.14.0.json'],
    [metadata.streamConsumersEnabled,'builtins/node-compat/export-manifest.stream-consumers.node-v22.14.0.json'],
  ];
  const paths=choices.filter(([enabled])=>enabled).map(([,path])=>path);
  assert.deepEqual(metadata.selectedModuleManifests.map(row=>row.path),paths);
  const rows=new Map(metadata.sourceManifest.map(row=>[row.path,row.sha256]));
  return paths.map(path=>{
    const raw=readFileSync(resolve(options.sourceRoot,path));
    assert.equal(createHash('sha256').update(raw).digest('hex'),rows.get(path));
    return JSON.parse(raw);
  });
}
