import * as events from 'node:events';
import {callbackReturnObservation} from './callback-return-cases.mjs';
export async function run(){return JSON.stringify(await callbackReturnObservation(events));}
