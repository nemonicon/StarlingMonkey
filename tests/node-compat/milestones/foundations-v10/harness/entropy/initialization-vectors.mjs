// Inputs for real componentization with the selected native entropy policy.
// All negative vectors must fail during Wizer or bindExports, not only run().
export const initializationVectors = [
  { name: 'direct-random-values', source: "crypto.getRandomValues(new Uint8Array(16)); export function run() {}" },
  { name: 'direct-random-uuid', source: "crypto.randomUUID(); export function run() {}" },
  { name: 'direct-object-url', source: "URL.createObjectURL(new Blob(['x'])); export function run() {}" },
  { name: 'direct-multipart', source: "const form = new FormData(); form.append('x','y'); new Response(form); export function run() {}" },
  { name: 'awaited-random-values', source: "await Promise.resolve().then(() => crypto.getRandomValues(new Uint8Array(16))); export function run() {}" },
  { name: 'detached-random-values', source: "Promise.resolve().then(() => crypto.getRandomValues(new Uint8Array(16))); export function run() {}" },
  { diagnosticOnly: true, reason: 'Finalization is not guaranteed without an explicit GC hook; do not count as a rejection gate', name: 'finalizer-random-values', source: "const r = new FinalizationRegistry(() => { crypto.getRandomValues(new Uint8Array(16)); }); function register() { r.register({}, 0); } register(); export function run() {}" },
  { name: 'late-export-getter', source: "export const api = { get run() { crypto.getRandomValues(new Uint8Array(16)); return () => {}; } };", wit: 'package test:late-entropy; world test { export api: interface { run: func(); } }' },
];
