import {number,change}from './pkg.cjs';export function observe(){const before=number;change();return {before,after:number};}
