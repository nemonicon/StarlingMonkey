import * as host from "jco:node/zlib@0.1.0";
import { createZlib } from "./zlib/core.js";
const zlib = createZlib(host);
export default zlib;
export const { constants, codes, crc32, Deflate, createDeflate, deflate, deflateSync, Inflate, createInflate, inflate, inflateSync, Gzip, createGzip, gzip, gzipSync, Gunzip, createGunzip, gunzip, gunzipSync, DeflateRaw, createDeflateRaw, deflateRaw, deflateRawSync, InflateRaw, createInflateRaw, inflateRaw, inflateRawSync, Unzip, createUnzip, unzip, unzipSync, BrotliCompress, createBrotliCompress, brotliCompress, brotliCompressSync, BrotliDecompress, createBrotliDecompress, brotliDecompress, brotliDecompressSync, ZstdCompress, createZstdCompress, zstdCompress, zstdCompressSync, ZstdDecompress, createZstdDecompress, zstdDecompress, zstdDecompressSync, } = zlib;
