import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
/** A shared capability must retain every user's callbacks and dependency files. */
export function mergeNodeWitRequirement(previous, current) {
    if (!previous) {
        return current;
    }
    return {
        ...previous,
        ...current,
        witExport: current.witExport ?? previous.witExport,
        guestExports: [
            ...new Map([...(previous.guestExports ?? []), ...(current.guestExports ?? [])].map((value) => [
                value.jsExport,
                value,
            ])).values(),
        ],
        dependencySources: [...new Set([...previous.dependencySources, ...current.dependencySources])],
        dependencyPackages: [...(previous.dependencyPackages ?? []), ...(current.dependencyPackages ?? [])],
    };
}
/** Types the Node API interfaces share; every interface file depends on it. */
const SHARED_TYPES_SOURCE = fileURLToPath(new URL("../lib/wit/builtin/jco-node-0.1.0/types.wit", import.meta.url));
/**
 * Build the requirement for one `jco:node/<interface>@0.1.0` import.
 *
 * Every Node API interface lives in `jco-node-0.1.0/<interface>.wit`; those that `use` the shared
 * `types` interface also install `types.wit` beside it. Mirrors `wasiRequirement` below for the
 * WASI side.
 */
function nodeRequirement(nodeSpecifier, witInterface, extra = {}) {
    const { sharedTypes = false, ...rest } = extra;
    const source = fileURLToPath(new URL(`../lib/wit/builtin/jco-node-0.1.0/${witInterface}.wit`, import.meta.url));
    return {
        nodeSpecifier,
        witImport: `jco:node/${witInterface}@0.1.0`,
        ...rest,
        dependencyDirectory: "jco-node-0.1.0",
        dependencySources: sharedTypes ? [SHARED_TYPES_SOURCE, source] : [source],
    };
}
export const CHILD_PROCESS_WIT_REQUIREMENT = nodeRequirement("node:child_process", "child-process", {
    sharedTypes: true,
});
export const WORKER_THREADS_WIT_REQUIREMENT = nodeRequirement("node:worker_threads", "worker-threads", {
    guestExports: [
        {
            witExport: "jco:node/worker-threads-callbacks@0.1.0",
            jsExport: "workerThreadsCallbacks",
            moduleSpecifier: "jco:node-worker-threads-callbacks",
        },
    ],
});
export const CLUSTER_WIT_REQUIREMENT = nodeRequirement("node:cluster", "cluster", { sharedTypes: true });
export const TRACE_EVENTS_WIT_REQUIREMENT = nodeRequirement("node:trace_events", "trace-events");
export const CONSOLE_WIT_REQUIREMENT = nodeRequirement("node:console", "console");
export const DGRAM_WIT_REQUIREMENT = nodeRequirement("node:dgram", "dgram", {
    guestExports: [
        {
            witExport: "jco:node/dgram-callbacks@0.1.0",
            jsExport: "dgramCallbacks",
            moduleSpecifier: "jco:node-dgram-callbacks",
        },
    ],
});
export const DNS_WIT_REQUIREMENT = nodeRequirement("node:dns", "dns");
export const DNS_PROMISES_WIT_REQUIREMENT = {
    ...DNS_WIT_REQUIREMENT,
    nodeSpecifier: "node:dns/promises",
};
export const FS_WIT_REQUIREMENT = nodeRequirement("node:fs", "fs");
/** VFS reuses the filesystem host protocol and its deny-by-default mapping. */
export const VFS_WIT_REQUIREMENT = { ...FS_WIT_REQUIREMENT, nodeSpecifier: "node:vfs" };
export const PROCESS_WIT_REQUIREMENT = nodeRequirement("node:process", "process");
export const SQLITE_WIT_REQUIREMENT = nodeRequirement("node:sqlite", "sqlite");
export const TLS_WIT_REQUIREMENT = {
    ...nodeRequirement("node:tls", "tls", {
        guestExports: [
            {
                witExport: "jco:node/tls-callbacks@0.1.0",
                jsExport: "tlsCallbacks",
                moduleSpecifier: "jco:node-tls-callbacks",
            },
        ],
    }),
    dependencyPackages: [
        {
            dependencyDirectory: "wasi-io-0.2.12",
            dependencySources: [
                fileURLToPath(new URL("../lib/wit/builtin/0.2.12/wasi-io/package.wit", import.meta.url)),
            ],
        },
        {
            dependencyDirectory: "wasi-tls-0.2.0-draft",
            dependencySources: ["world.wit", "types.wit"].map((name) => fileURLToPath(new URL(`../lib/wit/builtin/wasi-tls-0.2.0-draft/${name}`, import.meta.url))),
        },
    ],
};
export const V8_WIT_REQUIREMENT = nodeRequirement("node:v8", "v8");
export const OS_WIT_REQUIREMENT = nodeRequirement("node:os", "os");
export const ZLIB_WIT_REQUIREMENT = nodeRequirement("node:zlib", "zlib");
export const TTY_WIT_REQUIREMENT = nodeRequirement("node:tty", "tty", { sharedTypes: true });
/** The `node:wasi` builtin's host interface (initialisation only), not a `wasi:` package. */
export const WASI_WIT_REQUIREMENT = nodeRequirement("node:wasi", "wasi", { sharedTypes: true });
export const FFI_WIT_REQUIREMENT = nodeRequirement("node:ffi", "ffi");
export const INSPECTOR_WIT_REQUIREMENT = nodeRequirement("node:inspector", "inspector", {
    witExport: "jco:node/inspector-callbacks@0.1.0",
    guestExports: [
        {
            witExport: "jco:node/inspector-callbacks@0.1.0",
            jsExport: "inspectorCallbacks",
            moduleSpecifier: "jco:node-inspector-callbacks",
        },
    ],
});
export const INSPECTOR_PROMISES_WIT_REQUIREMENT = {
    ...INSPECTOR_WIT_REQUIREMENT,
    nodeSpecifier: "node:inspector/promises",
};
export const HTTP_WIT_REQUIREMENT = nodeRequirement("node:http", "http", {
    guestExports: [
        {
            witExport: "jco:node/http-callbacks@0.1.0",
            jsExport: "httpCallbacks",
            moduleSpecifier: "jco:node-http-callbacks",
            asyncMembers: ["handle", "start", "poll", "upgrade", "socket-event"],
        },
    ],
});
export const TIMERS_WIT_REQUIREMENT = nodeRequirement("node:timers", "timers", {
    guestExports: [
        {
            witExport: "jco:node/timers-callbacks@0.1.0",
            jsExport: "timersCallbacks",
            moduleSpecifier: "jco:node-timer-callbacks",
            asyncMembers: ["dispatch"],
        },
    ],
});
export const CRYPTO_KDF_WIT_REQUIREMENT = nodeRequirement("node:crypto", "crypto-kdf");
/**
 * `node:https` is `node:http` with TLS terminated by the same host interface, so it shares the
 * import and the callback export; only the comment naming the importing builtin differs, and
 * injection dedupes by `witImport` when a guest uses both.
 */
export const HTTPS_WIT_REQUIREMENT = {
    ...HTTP_WIT_REQUIREMENT,
    nodeSpecifier: "node:https",
};
export const HTTP2_WIT_REQUIREMENT = {
    nodeSpecifier: "node:http2",
    witImport: "jco:node/http2@0.1.0",
    guestExports: [
        {
            witExport: "jco:node/http2-callbacks@0.1.0",
            jsExport: "http2Callbacks",
            moduleSpecifier: "jco:node-http2-callbacks",
        },
    ],
    dependencyDirectory: "jco-node-0.1.0",
    dependencySources: [
        SHARED_TYPES_SOURCE,
        fileURLToPath(new URL("../lib/wit/builtin/jco-node-0.1.0/http2.wit", import.meta.url)),
    ],
};
const WASI_0_2_12_ROOT = new URL("../lib/wit/builtin/0.2.12/", import.meta.url);
const WASI_0_2_10_ROOT = new URL("../lib/wit/builtin/0.2.10/", import.meta.url);
export const RANDOM_WIT_REQUIREMENT = wasiRequirement("wasi:random/random@0.2.12", [wasiDependency("wasi-random")]);
function wasiDependency(name, version = "0.2.12") {
    const root = version === "0.2.10" ? WASI_0_2_10_ROOT : WASI_0_2_12_ROOT;
    return {
        dependencyDirectory: `${name}-${version}`,
        dependencySources: [fileURLToPath(new URL(`${name}/package.wit`, root))],
    };
}
const WASI_IO_DEPENDENCY = wasiDependency("wasi-io");
const WASI_CLOCKS_DEPENDENCY = wasiDependency("wasi-clocks");
const WASI_SOCKETS_DEPENDENCIES = [WASI_IO_DEPENDENCY, WASI_CLOCKS_DEPENDENCY, wasiDependency("wasi-sockets")];
const WASI_HTTP_DEPENDENCIES = [
    WASI_IO_DEPENDENCY,
    WASI_CLOCKS_DEPENDENCY,
    wasiDependency("wasi-random"),
    wasiDependency("wasi-filesystem"),
    wasiDependency("wasi-sockets"),
    wasiDependency("wasi-cli"),
    wasiDependency("wasi-http"),
];
function wasiRequirement(witImport, dependencies) {
    const [primary, ...additional] = dependencies;
    return {
        nodeSpecifier: "node:http",
        witImport,
        dependencyDirectory: primary.dependencyDirectory,
        dependencySources: primary.dependencySources,
        dependencyPackages: additional,
    };
}
export const VFS_WASI_FILESYSTEM_WIT_REQUIREMENTS = [
    "wasi:filesystem/preopens@0.2.12",
    "wasi:filesystem/types@0.2.12",
].map((witImport) => ({
    ...wasiRequirement(witImport, [wasiDependency("wasi-filesystem"), WASI_IO_DEPENDENCY, WASI_CLOCKS_DEPENDENCY]),
    nodeSpecifier: "node:vfs",
}));
export const HTTP_WASI_SOCKETS_WIT_REQUIREMENTS = [
    wasiRequirement("wasi:sockets/instance-network@0.2.12", WASI_SOCKETS_DEPENDENCIES),
    wasiRequirement("wasi:sockets/network@0.2.12", WASI_SOCKETS_DEPENDENCIES),
    wasiRequirement("wasi:sockets/ip-name-lookup@0.2.12", WASI_SOCKETS_DEPENDENCIES),
    wasiRequirement("wasi:sockets/tcp-create-socket@0.2.12", WASI_SOCKETS_DEPENDENCIES),
    wasiRequirement("wasi:sockets/tcp@0.2.12", WASI_SOCKETS_DEPENDENCIES),
    wasiRequirement("wasi:io/streams@0.2.12", WASI_SOCKETS_DEPENDENCIES),
    wasiRequirement("wasi:io/poll@0.2.12", WASI_SOCKETS_DEPENDENCIES),
];
const WASI_SOCKETS_0_2_10_DEPENDENCIES = [
    wasiDependency("wasi-io", "0.2.10"),
    wasiDependency("wasi-clocks", "0.2.10"),
    wasiDependency("wasi-sockets", "0.2.10"),
];
export const HTTP_WASI_SOCKETS_0_2_10_WIT_REQUIREMENTS = [
    wasiRequirement("wasi:sockets/instance-network@0.2.10", WASI_SOCKETS_0_2_10_DEPENDENCIES),
    wasiRequirement("wasi:sockets/network@0.2.10", WASI_SOCKETS_0_2_10_DEPENDENCIES),
    wasiRequirement("wasi:sockets/ip-name-lookup@0.2.10", WASI_SOCKETS_0_2_10_DEPENDENCIES),
    wasiRequirement("wasi:sockets/tcp-create-socket@0.2.10", WASI_SOCKETS_0_2_10_DEPENDENCIES),
    wasiRequirement("wasi:sockets/tcp@0.2.10", WASI_SOCKETS_0_2_10_DEPENDENCIES),
    wasiRequirement("wasi:io/streams@0.2.10", WASI_SOCKETS_0_2_10_DEPENDENCIES),
    wasiRequirement("wasi:io/poll@0.2.10", WASI_SOCKETS_0_2_10_DEPENDENCIES),
];
/**
 * The environment `node:path` reads the working directory from.
 *
 * Unlike the host-backed builtins this is a plain WASI interface, but it is injected the same
 * way: an application that reaches `node:path` -- usually through a dependency rather than
 * directly -- should not have to hand-write the import and vendor its WIT to build.
 */
export const PATH_WIT_REQUIREMENT = {
    nodeSpecifier: "node:path",
    witImport: "wasi:cli/environment@0.2.12",
    dependencyDirectory: WASI_IO_DEPENDENCY.dependencyDirectory,
    dependencySources: WASI_IO_DEPENDENCY.dependencySources,
    dependencyPackages: [
        WASI_CLOCKS_DEPENDENCY,
        wasiDependency("wasi-random"),
        wasiDependency("wasi-filesystem"),
        wasiDependency("wasi-sockets"),
        wasiDependency("wasi-cli"),
    ],
};
export const HTTP_WASI_HTTP_WIT_REQUIREMENTS = [
    wasiRequirement("wasi:http/outgoing-handler@0.2.12", WASI_HTTP_DEPENDENCIES),
    wasiRequirement("wasi:http/types@0.2.12", WASI_HTTP_DEPENDENCIES),
];
function forNodeSpecifier(requirements, nodeSpecifier) {
    return requirements.map((requirement) => ({ ...requirement, nodeSpecifier }));
}
function tlsRequirements() {
    return [{ ...TLS_WIT_REQUIREMENT, nodeSpecifier: "node:https", guestExports: [] }];
}
export const HTTPS_WASI_SOCKETS_0_2_10_WIT_REQUIREMENTS = [
    ...forNodeSpecifier(HTTP_WASI_SOCKETS_0_2_10_WIT_REQUIREMENTS, "node:https"),
    ...tlsRequirements(),
];
export const HTTPS_WASI_SOCKETS_WIT_REQUIREMENTS = [
    ...forNodeSpecifier(HTTP_WASI_SOCKETS_WIT_REQUIREMENTS, "node:https"),
    ...tlsRequirements(),
];
export const HTTPS_WASI_HTTP_WIT_REQUIREMENTS = forNodeSpecifier(HTTP_WASI_HTTP_WIT_REQUIREMENTS, "node:https");
export const NET_WASI_SOCKETS_WIT_REQUIREMENTS = forNodeSpecifier(HTTP_WASI_SOCKETS_WIT_REQUIREMENTS, "node:net");
export const NET_WASI_SOCKETS_0_2_10_WIT_REQUIREMENTS = forNodeSpecifier(HTTP_WASI_SOCKETS_0_2_10_WIT_REQUIREMENTS, "node:net");
export function witInjectionWarnings(result) {
    const messages = [];
    if (result.imports.length > 0) {
        messages.push(`Jco added generated WIT import${result.imports.length === 1 ? "" : "s"} ${result.imports.join(", ")} to ${result.worldFile} because bundled source uses a host-backed Node API. Review and commit this change.`);
    }
    if (result.exports.length > 0) {
        messages.push(`Jco added generated WIT export${result.exports.length === 1 ? "" : "s"} ${result.exports.join(", ")} to ${result.worldFile} because bundled source uses a host-backed Node API. Review and commit this change.`);
    }
    for (const dependencyFile of result.dependencyFiles) {
        messages.push(`Jco added the required WIT dependency at ${dependencyFile}.`);
    }
    return messages;
}
function withoutComments(source) {
    return source
        .replace(/\/\*[\s\S]*?\*\//g, (comment) => " ".repeat(comment.length))
        .replace(/\/\/[^\r\n]*/g, (comment) => " ".repeat(comment.length));
}
function matchingBrace(source, openBrace) {
    let depth = 0;
    let lineComment = false;
    let blockComment = false;
    let quote;
    for (let index = openBrace; index < source.length; index++) {
        const char = source[index];
        const next = source[index + 1];
        if (lineComment) {
            if (char === "\n") {
                lineComment = false;
            }
            continue;
        }
        if (blockComment) {
            if (char === "*" && next === "/") {
                blockComment = false;
                index++;
            }
            continue;
        }
        if (quote) {
            if (char === "\\") {
                index++;
            }
            else if (char === quote) {
                quote = undefined;
            }
            continue;
        }
        if (char === "/" && next === "/") {
            lineComment = true;
            index++;
        }
        else if (char === "/" && next === "*") {
            blockComment = true;
            index++;
        }
        else if (char === '"' || char === "'") {
            quote = char;
        }
        else if (char === "{") {
            depth++;
        }
        else if (char === "}" && --depth === 0) {
            return index;
        }
    }
    throw new Error("unterminated WIT world declaration");
}
function worldsIn(file, source) {
    const visible = withoutComments(source);
    const worlds = [];
    const pattern = /\bworld\s+(%?[A-Za-z][A-Za-z0-9-]*)\s*\{/g;
    for (let match = pattern.exec(visible); match; match = pattern.exec(visible)) {
        const openBrace = visible.indexOf("{", match.index);
        worlds.push({
            name: match[1],
            file,
            source,
            openBrace,
            closeBrace: matchingBrace(source, openBrace),
        });
    }
    return worlds;
}
function selectedWorldName(worldName) {
    if (!worldName) {
        return undefined;
    }
    return worldName
        .split("/")
        .pop()
        .replace(/@\d+(?:\.\d+)*(?:-[A-Za-z0-9.-]+)?$/, "");
}
async function rootWitFiles(witPath) {
    const path = resolve(witPath);
    if ((await stat(path)).isFile()) {
        return [path];
    }
    const entries = await readdir(path, { withFileTypes: true });
    return entries
        .filter((entry) => entry.isFile() && entry.name.endsWith(".wit"))
        .map((entry) => join(path, entry.name));
}
async function findWorld(witPath, worldName) {
    const declarations = (await Promise.all((await rootWitFiles(witPath)).map(async (file) => worldsIn(file, await readFile(file, "utf8"))))).flat();
    const selected = selectedWorldName(worldName);
    if (selected) {
        const matches = declarations.filter(({ name }) => name === selected);
        if (matches.length !== 1) {
            throw new Error(`unable to inject Node WIT imports: selected world ${worldName} was ${matches.length ? "ambiguous" : "not found"}`);
        }
        return matches[0];
    }
    if (declarations.length !== 1) {
        throw new Error(`unable to inject Node WIT imports: specify --world because the WIT package defines ${declarations.length} worlds`);
    }
    return declarations[0];
}
function worldHasDeclaration(world, declaration, witName) {
    const body = withoutComments(world.source.slice(world.openBrace + 1, world.closeBrace));
    const escaped = witName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    return new RegExp(`\\b${declaration}\\s+(?:%?[A-Za-z][A-Za-z0-9-]*\\s*:\\s*)?${escaped}\\s*;`).test(body);
}
function insertionFor(imports, exports, newline) {
    return [
        ...imports.map(({ nodeSpecifier, witImport }) => `${newline}  // Added by Jco because bundled source imports ${nodeSpecifier}.${newline}  import ${witImport};`),
        ...exports.map(({ nodeSpecifier, witExport }) => `${newline}  // Added by Jco so the ${nodeSpecifier} host can invoke guest callbacks.${newline}  export ${witExport};`),
    ].join("");
}
function requirementWitExports(requirement) {
    return [
        ...new Set([
            ...(requirement.witExport ? [requirement.witExport] : []),
            ...(requirement.guestExports ?? []).map(({ witExport }) => witExport),
        ]),
    ];
}
/**
 * Add Node capability imports and companion callback exports to the selected user world in place.
 *
 * This is intentionally visible in source control. Repeated calls are no-ops,
 * and dependency packages supplied by the user are never overwritten.
 */
export async function injectNodeWitImports(witPath, worldName, requirements, options = {}) {
    if (requirements.length === 0) {
        return undefined;
    }
    const world = await findWorld(witPath, worldName);
    const merged = new Map();
    for (const requirement of requirements) {
        merged.set(requirement.witImport, mergeNodeWitRequirement(merged.get(requirement.witImport), requirement));
    }
    const uniqueRequirements = [...merged.values()];
    const missingImports = uniqueRequirements.filter(({ witImport }) => !worldHasDeclaration(world, "import", witImport));
    const missingExports = uniqueRequirements.flatMap((requirement) => requirementWitExports(requirement)
        .filter((witExport) => !worldHasDeclaration(world, "export", witExport))
        .map((witExport) => ({ nodeSpecifier: requirement.nodeSpecifier, witExport })));
    if (missingImports.length === 0 && missingExports.length === 0) {
        return undefined;
    }
    const newline = world.source.includes("\r\n") ? "\r\n" : "\n";
    const root = (await stat(resolve(witPath))).isFile() ? dirname(resolve(witPath)) : resolve(witPath);
    const dependencyFiles = [];
    const dependencies = new Map();
    const changedRequirements = uniqueRequirements.filter((requirement) => missingImports.includes(requirement) ||
        requirementWitExports(requirement).some((witExport) => missingExports.some((missing) => missing.witExport === witExport)));
    for (const requirement of changedRequirements) {
        const packages = [
            {
                dependencyDirectory: requirement.dependencyDirectory,
                dependencySources: requirement.dependencySources,
            },
            ...(requirement.dependencyPackages ?? []),
        ];
        for (const dependency of packages) {
            const previous = dependencies.get(dependency.dependencyDirectory);
            dependencies.set(dependency.dependencyDirectory, {
                ...dependency,
                dependencySources: [
                    ...new Set([...(previous?.dependencySources ?? []), ...dependency.dependencySources]),
                ],
            });
        }
    }
    for (const dependency of dependencies.values()) {
        const dependencyDir = join(root, "deps", dependency.dependencyDirectory);
        await mkdir(dependencyDir, { recursive: true });
        for (const source of dependency.dependencySources) {
            const destination = join(dependencyDir, basename(source));
            try {
                let contents = await readFile(source, "utf8");
                if (options.asyncGuestCallbacks) {
                    for (const requirement of changedRequirements) {
                        for (const guest of requirement.guestExports ?? []) {
                            const iface = guest.witExport.split("/").pop().split("@")[0];
                            if (!guest.asyncMembers?.length) {
                                continue;
                            }
                            const declaration = new RegExp(`\\binterface\\s+${iface}\\s*\\{`).exec(contents);
                            if (!declaration) {
                                continue;
                            }
                            const open = declaration.index + declaration[0].lastIndexOf("{");
                            const close = matchingBrace(contents, open);
                            let body = contents.slice(open + 1, close);
                            for (const member of guest.asyncMembers) {
                                body = body.replace(new RegExp(`(\\b${member}:\\s*)func\\b`, "g"), "$1async func");
                            }
                            contents = contents.slice(0, open + 1) + body + contents.slice(close);
                        }
                    }
                }
                await writeFile(destination, contents, { flag: "wx" });
                dependencyFiles.push(destination);
            }
            catch (error) {
                if (error.code !== "EEXIST") {
                    throw error;
                }
            }
        }
    }
    const updated = world.source.slice(0, world.openBrace + 1) +
        insertionFor(missingImports, missingExports, newline) +
        world.source.slice(world.openBrace + 1);
    await writeFile(world.file, updated);
    return {
        witPath: root,
        worldFile: world.file,
        dependencyFiles,
        imports: missingImports.map(({ witImport }) => witImport),
        exports: missingExports.map(({ witExport }) => witExport),
    };
}
//# sourceMappingURL=node-wit.js.map