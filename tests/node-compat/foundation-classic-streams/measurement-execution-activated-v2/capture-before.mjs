// First guest dependency; imports nothing. Do not replace or mask any global.
// Ordinary ESM evaluation must run this before the provider dependency.
export const bufferBeforeProvider=globalThis.Buffer;
