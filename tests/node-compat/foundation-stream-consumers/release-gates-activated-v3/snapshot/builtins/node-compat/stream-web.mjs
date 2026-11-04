// Uninstalled m0.9 production candidate. Exactly one private native record;
// capture/registration/CMake remain separately reviewed integration work.
import {createCodecModule} from './stream-web-codecs.mjs';
import {installReadableIteration} from './stream-web-readable-iteration.mjs';
import {installDataViewBYOB} from './stream-web-byob.mjs';
export function createStreamWebModule(record){
  // Validate every private field before reading any possibly untrusted getter.
  // createCodecModule performs exact own-data/function record validation first.
  const module=createCodecModule(record);
  const nativeRead=record.ReadableStreamBYOBReader.prototype.read;
  installReadableIteration(record);
  installDataViewBYOB(record,nativeRead);
  return module;
}
