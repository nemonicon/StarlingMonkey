// Future native guest binding only; no public facade or JS codec is bundled.
import {Buffer} from 'node:buffer';
import * as api from 'node:zlib';
import {createNativeComparand} from './providers.mjs';
export const provider=Object.freeze({id:'native',sourceVersion:'registered-node-zlib-m0.13',Buffer,methods:createNativeComparand({Buffer,api})});
