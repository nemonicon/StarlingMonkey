import { fileURLToPath } from 'node:url';
/** @type {import('next').NextConfig} */
const config = {
  output: 'standalone',
  cacheHandler: fileURLToPath(new URL('./cache-handler.cjs', import.meta.url)),
  cacheMaxMemorySize: 0,
  outputFileTracingRoot: fileURLToPath(new URL('.', import.meta.url)),
  experimental: { cpus: 1 },
  outputFileTracingIncludes: { '/api/fs-crypto': ['./fixtures/message.txt'] },
  outputFileTracingExcludes: { '/api/cache': ['./.next/cache/**'] },
};
export default config;
