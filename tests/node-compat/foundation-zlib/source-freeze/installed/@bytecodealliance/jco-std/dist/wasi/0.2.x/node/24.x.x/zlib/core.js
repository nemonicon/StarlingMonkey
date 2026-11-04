/** Node-compatible stream/callback orchestration over the explicit compression capability.
 * Contract: Node.js v24.20.0, lib/zlib.js, commit
 * 71b8b174857e25106d39b61a9e6f30d927da8b01 (MIT). Compression stays in the host. */
import { Buffer } from "node:buffer";
import { Transform } from "../stream/index.js";
import { nextTick } from "../stream/scheduler.js";
import { toUint8Array } from "../stream/shared.js";
import { callHost, decodeErrno } from "../internal/host-error.js";
import { codedError, deprecatedNodeApi, invalidArgType, outOfRange } from "../errors/core.js";
import { constants, codes } from "./constants.js";
function restoreError(record) {
    const Constructor = record.name === "TypeError" ? TypeError : record.name === "RangeError" ? RangeError : Error;
    const error = new Constructor(record.message);
    error.name = record.name;
    if (record.code !== undefined) {
        Object.assign(error, { code: record.code });
    }
    if (record.errno !== undefined) {
        Object.assign(error, { errno: decodeErrno(record.errno) });
    }
    return error;
}
const call = (operation) => callHost(operation, restoreError);
const asError = (error) => error instanceof Error ? error : new Error(String(error));
function inputBytes(value, name = "buffer") {
    return typeof value === "string" ? Buffer.from(value) : toUint8Array(value, name);
}
function optionsForHost(options = {}) {
    const result = {};
    for (const key of [
        "flush",
        "finishFlush",
        "chunkSize",
        "windowBits",
        "level",
        "memLevel",
        "strategy",
        "maxOutputLength",
        "pledgedSrcSize",
    ]) {
        const value = options?.[key];
        if (value !== undefined) {
            if (typeof value !== "number") {
                throw invalidArgType(`options.${key}`, "number", value);
            }
            result[key] = value;
        }
    }
    if (options?.rejectGarbageAfterEnd !== undefined) {
        if (typeof options.rejectGarbageAfterEnd !== "boolean") {
            throw invalidArgType("options.rejectGarbageAfterEnd", "boolean", options.rejectGarbageAfterEnd);
        }
        result.rejectGarbageAfterEnd = options.rejectGarbageAfterEnd;
    }
    if (options?.dictionary !== undefined) {
        if (!(options.dictionary instanceof ArrayBuffer) && !ArrayBuffer.isView(options.dictionary)) {
            throw invalidArgType("options.dictionary", ["Buffer", "TypedArray", "DataView", "ArrayBuffer"], options.dictionary);
        }
        result.dictionary = toUint8Array(options.dictionary);
    }
    if (options?.params !== undefined) {
        result.params = Object.entries(options.params).map(([key, value]) => {
            if (typeof value !== "number" && typeof value !== "boolean") {
                throw invalidArgType(`options.params[${key}]`, ["number", "boolean"], value);
            }
            return [key, Number(value)];
        });
    }
    return result;
}
/** Build an isolated module; importing it never calls the provider. */
export function createZlib(host) {
    // An empty write carrying a flush marker preserves writable queue ordering/backpressure.
    const flushes = new WeakMap();
    const completed = Symbol("completed compression");
    class Base extends Transform {
        bytesWritten = 0;
        #engine;
        #fullFlush;
        #maxFlush;
        constructor(algorithm, options, state) {
            const native = optionsForHost(options);
            super({
                ...options,
                flush: undefined,
                encoding: undefined,
                objectMode: false,
                writableObjectMode: false,
            });
            this.#engine = state === completed ? undefined : call(() => host.open(algorithm, native));
            this.#maxFlush = algorithm.startsWith("brotli") ? 3 : algorithm.startsWith("zstd") ? 2 : 5;
            this.#fullFlush = algorithm.startsWith("brotli") ? 1 : algorithm.startsWith("zstd") ? 1 : 3;
        }
        get bytesRead() {
            throw deprecatedNodeApi("zlib.bytesRead", "zlib.bytesWritten");
        }
        engine() {
            if (!this.#engine) {
                throw codedError(new Error("zlib binding closed"), "ERR_ASSERTION");
            }
            return this.#engine;
        }
        output(result) {
            this.bytesWritten = result.bytesWritten;
            if (result.data.length) {
                this.push(Buffer.from(result.data));
            }
        }
        _transform(chunk, _encoding, callback) {
            try {
                const bytes = toUint8Array(chunk);
                const kind = chunk instanceof Uint8Array ? flushes.get(chunk) : undefined;
                this.output(call(() => (kind === undefined ? this.engine().write(bytes) : this.engine().flush(kind))));
            }
            catch (error) {
                callback(asError(error));
                return;
            }
            callback();
        }
        _flush(callback) {
            try {
                this.output(call(() => this.engine().finish()));
            }
            catch (error) {
                callback(asError(error));
                return;
            }
            callback();
        }
        _destroy(error, callback) {
            const engine = this.#engine;
            this.#engine = undefined;
            try {
                if (engine) {
                    call(() => engine.close());
                    engine[Symbol.dispose]?.();
                }
            }
            catch (closeError) {
                callback(error ?? asError(closeError));
                return;
            }
            callback(error);
        }
        close(callback) {
            if (callback !== undefined) {
                if (typeof callback !== "function") {
                    throw invalidArgType("callback", "function", callback);
                }
                if (this.closed) {
                    nextTick(callback);
                }
                else {
                    this.once("close", callback);
                }
            }
            this.destroy();
        }
        reset() {
            call(() => this.engine().reset());
        }
        flush(kind, callback) {
            if (typeof kind === "function") {
                callback = kind;
                kind = undefined;
            }
            kind ??= this.#fullFlush;
            if (typeof kind !== "number") {
                throw invalidArgType("kind", "number", kind);
            }
            if (kind < 0 || kind > this.#maxFlush || Number.isNaN(kind)) {
                throw outOfRange("kind", `>= 0 and <= ${this.#maxFlush}`, kind);
            }
            if (callback !== undefined && typeof callback !== "function") {
                throw invalidArgType("callback", "function", callback);
            }
            if (this.writableFinished) {
                if (callback) {
                    nextTick(callback);
                }
                return;
            }
            if (this.writableEnded) {
                if (callback) {
                    this.once("end", callback);
                }
                return;
            }
            const marker = Buffer.alloc(0);
            flushes.set(marker, kind);
            this.write(marker, callback);
        }
    }
    class WithParams extends Base {
        params(level, strategy, callback) {
            if (typeof level !== "number") {
                throw invalidArgType("level", "number", level);
            }
            if (typeof strategy !== "number") {
                throw invalidArgType("strategy", "number", strategy);
            }
            if (level < -1 || level > 9 || Number.isNaN(level)) {
                throw outOfRange("level", ">= -1 and <= 9", level);
            }
            if (strategy < 0 || strategy > 4 || Number.isNaN(strategy)) {
                throw outOfRange("strategy", ">= 0 and <= 4", strategy);
            }
            if (typeof callback !== "function") {
                throw invalidArgType("callback", "function", callback);
            }
            this.flush(constants.Z_SYNC_FLUSH, (error) => {
                if (error) {
                    callback(error);
                    return;
                }
                try {
                    this.output(call(() => this.engine().params(level, strategy)));
                }
                catch (cause) {
                    callback(asError(cause));
                    return;
                }
                callback();
            });
        }
    }
    function family(name, algorithm, params) {
        const Parent = params ? WithParams : Base;
        class Compression extends Parent {
            constructor(options, state) {
                super(algorithm, options, state);
            }
        }
        Object.defineProperty(Compression, "name", { value: name });
        const Callable = new Proxy(Compression, {
            apply(target, _this, args) {
                return Reflect.construct(target, args);
            },
        });
        Object.defineProperty(Compression.prototype, "constructor", {
            value: Callable,
            writable: true,
            configurable: true,
        });
        // All constructors implement the same stream contract; params selects the stronger prototype.
        const Constructor = Callable;
        function sync(input, options) {
            const result = call(() => host.compress(algorithm, inputBytes(input), optionsForHost(options)));
            const buffer = Buffer.from(result.data);
            if (!options?.info) {
                return buffer;
            }
            const engine = new Compression(options, completed);
            engine.bytesWritten = result.bytesWritten;
            engine.destroy();
            return { buffer, engine: engine };
        }
        function asyncMethod(input, optionsOrCallback, callback) {
            const options = typeof optionsOrCallback === "function" ? undefined : optionsOrCallback;
            if (typeof optionsOrCallback === "function") {
                callback = optionsOrCallback;
            }
            if (typeof callback !== "function") {
                throw invalidArgType("callback", "function", callback);
            }
            const cb = callback;
            // Node constructs before scheduling: malformed options and a missing capability throw now.
            const data = inputBytes(input);
            const stream = new Constructor(options);
            nextTick(() => {
                let result;
                try {
                    result = call(() => host.compress(algorithm, data, optionsForHost(options)));
                }
                catch (error) {
                    stream.destroy();
                    cb(asError(error));
                    return;
                }
                stream.bytesWritten = result.bytesWritten;
                stream.destroy();
                const buffer = Buffer.from(result.data);
                cb(null, options?.info ? { buffer, engine: stream } : buffer);
            });
        }
        return {
            Constructor,
            create: (options) => new Constructor(options),
            sync: sync,
            async: asyncMethod,
        };
    }
    const deflate = family("Deflate", "deflate", true);
    const inflate = family("Inflate", "inflate", true);
    const gzip = family("Gzip", "gzip", true);
    const gunzip = family("Gunzip", "gunzip", true);
    const deflateRaw = family("DeflateRaw", "deflateraw", true);
    const inflateRaw = family("InflateRaw", "inflateraw", true);
    const unzip = family("Unzip", "unzip", true);
    const brotliCompress = family("BrotliCompress", "brotlicompress", false);
    const brotliDecompress = family("BrotliDecompress", "brotlidecompress", false);
    const zstdCompress = family("ZstdCompress", "zstdcompress", false);
    const zstdDecompress = family("ZstdDecompress", "zstddecompress", false);
    const module = {
        constants,
        codes,
        crc32(data, value = 0) {
            if (typeof data !== "string" && !ArrayBuffer.isView(data)) {
                throw invalidArgType("data", ["Buffer", "TypedArray", "DataView", "string"], data);
            }
            if (typeof value !== "number") {
                throw invalidArgType("value", "number", value);
            }
            if (!Number.isInteger(value) || value < 0 || value > 0xffffffff) {
                throw outOfRange("value", ">= 0 and <= 4294967295", value);
            }
            // Normalize engines that lift a WIT u32 through a signed i32.
            return call(() => host.crc32(inputBytes(data), value)) >>> 0;
        },
        Deflate: deflate.Constructor,
        createDeflate: deflate.create,
        deflate: deflate.async,
        deflateSync: deflate.sync,
        Inflate: inflate.Constructor,
        createInflate: inflate.create,
        inflate: inflate.async,
        inflateSync: inflate.sync,
        Gzip: gzip.Constructor,
        createGzip: gzip.create,
        gzip: gzip.async,
        gzipSync: gzip.sync,
        Gunzip: gunzip.Constructor,
        createGunzip: gunzip.create,
        gunzip: gunzip.async,
        gunzipSync: gunzip.sync,
        DeflateRaw: deflateRaw.Constructor,
        createDeflateRaw: deflateRaw.create,
        deflateRaw: deflateRaw.async,
        deflateRawSync: deflateRaw.sync,
        InflateRaw: inflateRaw.Constructor,
        createInflateRaw: inflateRaw.create,
        inflateRaw: inflateRaw.async,
        inflateRawSync: inflateRaw.sync,
        Unzip: unzip.Constructor,
        createUnzip: unzip.create,
        unzip: unzip.async,
        unzipSync: unzip.sync,
        BrotliCompress: brotliCompress.Constructor,
        createBrotliCompress: brotliCompress.create,
        brotliCompress: brotliCompress.async,
        brotliCompressSync: brotliCompress.sync,
        BrotliDecompress: brotliDecompress.Constructor,
        createBrotliDecompress: brotliDecompress.create,
        brotliDecompress: brotliDecompress.async,
        brotliDecompressSync: brotliDecompress.sync,
        ZstdCompress: zstdCompress.Constructor,
        createZstdCompress: zstdCompress.create,
        zstdCompress: zstdCompress.async,
        zstdCompressSync: zstdCompress.sync,
        ZstdDecompress: zstdDecompress.Constructor,
        createZstdDecompress: zstdDecompress.create,
        zstdDecompress: zstdDecompress.async,
        zstdDecompressSync: zstdDecompress.sync,
    };
    for (const key of Object.keys(module)) {
        if (key.startsWith("create")) {
            Object.defineProperty(module, key, { writable: false, configurable: true });
        }
    }
    Object.defineProperty(module, "constants", { writable: false, configurable: false });
    Object.defineProperty(module, "codes", { writable: false, configurable: false });
    for (const key of Object.keys(constants)) {
        if (!key.startsWith("BROTLI")) {
            Object.defineProperty(module, key, {
                get() {
                    throw deprecatedNodeApi(`zlib.${key}`, `zlib.constants.${key}`);
                },
            });
        }
    }
    return module;
}
