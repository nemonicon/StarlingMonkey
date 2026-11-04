// Finite resolver must bind this ID to the exact pinned browser.js copy.
import {Buffer} from 'node:buffer';
import {zlibSync,unzlibSync,gzipSync,gunzipSync,deflateSync,inflateSync} from 'codec:fflate-browser';
import {createFFlateComparand} from './providers.mjs';
export const provider=Object.freeze({id:'fflate',sourceVersion:'fflate-browser-0.8.3',Buffer,methods:createFFlateComparand({Buffer,fflate:{zlibSync,unzlibSync,gzipSync,gunzipSync,deflateSync,inflateSync}})});
