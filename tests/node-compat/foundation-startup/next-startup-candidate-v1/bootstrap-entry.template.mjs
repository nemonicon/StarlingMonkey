// UNEXECUTED native guest entry fragment. Raw component input may retain these
// two REAL builtin imports; public node:-only builtinMap is not widened.
import {bootstrap} from 'starling:node-startup';
import Module from 'node:module';
export function initializeServerRoot({applicationDirectory,entryFilename}) {
  // Invoke from neutral deployed server root, before app.prepare and before
  // a fresh request ALS boundary/body construction. INIT must reject this.
  const process=bootstrap();
  process.chdir(applicationDirectory); // actual shared direct-P2 directory check
  return {process,require:Module.createRequire(entryFilename)};
}
