import { fileURLToPath } from 'node:url';
/** @type {import('next').NextConfig} */
const config = {
  output: 'standalone',
  outputFileTracingRoot: fileURLToPath(new URL('.', import.meta.url)),
  experimental: { cpus: 1 },
  outputFileTracingIncludes: { '/api/fs-crypto': ['./fixtures/message.txt'] },
};
export default config;
