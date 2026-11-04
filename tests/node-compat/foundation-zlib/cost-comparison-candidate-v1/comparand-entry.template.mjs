// Not an executable entry: placeholders require a NEW reviewed activation.
// Explicit browser file; NEVER package-root fflate or a Jco nodeBuiltinPlugin.
import {zlibSync,unzlibSync,gzipSync,gunzipSync,deflateSync,inflateSync} from '@PINNED_FFLATE_BROWSER_ENTRY@';
import {Buffer} from 'node:buffer';
import {createFFlateComparand} from './providers.template.mjs';
export const comparand=createFFlateComparand({Buffer,fflate:{zlibSync,unzlibSync,gzipSync,gunzipSync,deflateSync,inflateSync}});
