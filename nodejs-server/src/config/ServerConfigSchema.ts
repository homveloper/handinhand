// To parse this data:
//
//   import { Convert, ServerConfigSchema } from "./file";
//
//   const serverConfigSchema = Convert.toServerConfigSchema(json);
//
// These functions will throw an error if the JSON doesn't
// match the expected interface, even if the JSON is valid.

/**
 * Configuration schema for all 4 language servers (Node.js, Python, Go, C#)
 */
export interface ServerConfigSchema {
    api:  API;
    cors: Cors;
    /**
     * Enable debug mode
     */
    debug: boolean;
    /**
     * Current environment
     */
    environment: Environment;
    jsonrpc:     Jsonrpc;
    logging:     Logging;
    nginx:       Nginx;
    redis:       Redis;
    servers:     Servers;
    sse:         SSE;
    [property: string]: any;
}

export interface API {
    /**
     * API base path
     */
    basePath:  string;
    rateLimit: RateLimit;
    /**
     * Enable Swagger documentation
     */
    swaggerEnabled: boolean;
    /**
     * API version
     */
    version: string;
    [property: string]: any;
}

export interface RateLimit {
    /**
     * Maximum requests per window
     */
    maxRequests: number;
    /**
     * Rate limit window in milliseconds
     */
    windowMS: number;
    [property: string]: any;
}

export interface Cors {
    /**
     * Allow credentials in CORS requests
     */
    allowCredentials: boolean;
    /**
     * Allowed HTTP headers
     */
    allowedHeaders: string[];
    /**
     * Allowed HTTP methods
     */
    allowedMethods: AllowedMethod[];
    /**
     * Allowed CORS origins
     */
    allowedOrigins: string[];
    [property: string]: any;
}

export enum AllowedMethod {
    Delete = "DELETE",
    Get = "GET",
    Head = "HEAD",
    Options = "OPTIONS",
    Patch = "PATCH",
    Post = "POST",
    Put = "PUT",
}

/**
 * Current environment
 */
export enum Environment {
    Development = "development",
    Production = "production",
    Testing = "testing",
}

export interface Jsonrpc {
    /**
     * Maximum batch request size
     */
    batchLimit: number;
    /**
     * Request timeout in milliseconds
     */
    timeout: number;
    /**
     * JSON-RPC version
     */
    version: Version;
    [property: string]: any;
}

/**
 * JSON-RPC version
 */
export enum Version {
    The20 = "2.0",
}

export interface Logging {
    /**
     * Enable console logging
     */
    consoleEnabled: boolean;
    /**
     * Enable file logging
     */
    fileEnabled: boolean;
    /**
     * Log format
     */
    format: Format;
    /**
     * Logging level
     */
    level: Level;
    [property: string]: any;
}

/**
 * Log format
 */
export enum Format {
    JSON = "json",
    Text = "text",
}

/**
 * Logging level
 */
export enum Level {
    Debug = "debug",
    Error = "error",
    Info = "info",
    Warn = "warn",
}

export interface Nginx {
    /**
     * Health check endpoint path
     */
    healthCheckPath: string;
    /**
     * NGINX listen port
     */
    port: number;
    /**
     * NGINX upstream name
     */
    upstreamName: string;
    [property: string]: any;
}

export interface Redis {
    /**
     * Redis database number
     */
    db: number;
    /**
     * Redis host address
     */
    host: string;
    /**
     * Maximum retry attempts per request
     */
    maxRetriesPerRequest?: number;
    /**
     * Redis password (optional)
     */
    password?: string;
    /**
     * Redis port number
     */
    port: number;
    /**
     * Retry delay in milliseconds
     */
    retryDelayOnFailover?: number;
    [property: string]: any;
}

export interface Servers {
    csharp: ServerInfo;
    golang: ServerInfo;
    nodejs: ServerInfo;
    python: ServerInfo;
    [property: string]: any;
}

export interface ServerInfo {
    /**
     * Server host address
     */
    host: string;
    /**
     * Server name
     */
    name: string;
    /**
     * Server port number
     */
    port: number;
    [property: string]: any;
}

export interface SSE {
    /**
     * SSE heartbeat interval in milliseconds
     */
    heartbeatInterval: number;
    /**
     * Maximum SSE connections
     */
    maxConnections: number;
    /**
     * SSE reconnect timeout in milliseconds
     */
    reconnectTimeout: number;
    [property: string]: any;
}

// Converts JSON strings to/from your types
// and asserts the results of JSON.parse at runtime
export class Convert {
    public static toServerConfigSchema(json: string): ServerConfigSchema {
        return cast(JSON.parse(json), r("ServerConfigSchema"));
    }

    public static serverConfigSchemaToJson(value: ServerConfigSchema): string {
        return JSON.stringify(uncast(value, r("ServerConfigSchema")), null, 2);
    }
}

function invalidValue(typ: any, val: any, key: any, parent: any = ''): never {
    const prettyTyp = prettyTypeName(typ);
    const parentText = parent ? ` on ${parent}` : '';
    const keyText = key ? ` for key "${key}"` : '';
    throw Error(`Invalid value${keyText}${parentText}. Expected ${prettyTyp} but got ${JSON.stringify(val)}`);
}

function prettyTypeName(typ: any): string {
    if (Array.isArray(typ)) {
        if (typ.length === 2 && typ[0] === undefined) {
            return `an optional ${prettyTypeName(typ[1])}`;
        } else {
            return `one of [${typ.map(a => { return prettyTypeName(a); }).join(", ")}]`;
        }
    } else if (typeof typ === "object" && typ.literal !== undefined) {
        return typ.literal;
    } else {
        return typeof typ;
    }
}

function jsonToJSProps(typ: any): any {
    if (typ.jsonToJS === undefined) {
        const map: any = {};
        typ.props.forEach((p: any) => map[p.json] = { key: p.js, typ: p.typ });
        typ.jsonToJS = map;
    }
    return typ.jsonToJS;
}

function jsToJSONProps(typ: any): any {
    if (typ.jsToJSON === undefined) {
        const map: any = {};
        typ.props.forEach((p: any) => map[p.js] = { key: p.json, typ: p.typ });
        typ.jsToJSON = map;
    }
    return typ.jsToJSON;
}

function transform(val: any, typ: any, getProps: any, key: any = '', parent: any = ''): any {
    function transformPrimitive(typ: string, val: any): any {
        if (typeof typ === typeof val) return val;
        return invalidValue(typ, val, key, parent);
    }

    function transformUnion(typs: any[], val: any): any {
        // val must validate against one typ in typs
        const l = typs.length;
        for (let i = 0; i < l; i++) {
            const typ = typs[i];
            try {
                return transform(val, typ, getProps);
            } catch (_) {}
        }
        return invalidValue(typs, val, key, parent);
    }

    function transformEnum(cases: string[], val: any): any {
        if (cases.indexOf(val) !== -1) return val;
        return invalidValue(cases.map(a => { return l(a); }), val, key, parent);
    }

    function transformArray(typ: any, val: any): any {
        // val must be an array with no invalid elements
        if (!Array.isArray(val)) return invalidValue(l("array"), val, key, parent);
        return val.map(el => transform(el, typ, getProps));
    }

    function transformDate(val: any): any {
        if (val === null) {
            return null;
        }
        const d = new Date(val);
        if (isNaN(d.valueOf())) {
            return invalidValue(l("Date"), val, key, parent);
        }
        return d;
    }

    function transformObject(props: { [k: string]: any }, additional: any, val: any): any {
        if (val === null || typeof val !== "object" || Array.isArray(val)) {
            return invalidValue(l(ref || "object"), val, key, parent);
        }
        const result: any = {};
        Object.getOwnPropertyNames(props).forEach(key => {
            const prop = props[key];
            const v = Object.prototype.hasOwnProperty.call(val, key) ? val[key] : undefined;
            result[prop.key] = transform(v, prop.typ, getProps, key, ref);
        });
        Object.getOwnPropertyNames(val).forEach(key => {
            if (!Object.prototype.hasOwnProperty.call(props, key)) {
                result[key] = transform(val[key], additional, getProps, key, ref);
            }
        });
        return result;
    }

    if (typ === "any") return val;
    if (typ === null) {
        if (val === null) return val;
        return invalidValue(typ, val, key, parent);
    }
    if (typ === false) return invalidValue(typ, val, key, parent);
    let ref: any = undefined;
    while (typeof typ === "object" && typ.ref !== undefined) {
        ref = typ.ref;
        typ = typeMap[typ.ref];
    }
    if (Array.isArray(typ)) return transformEnum(typ, val);
    if (typeof typ === "object") {
        return typ.hasOwnProperty("unionMembers") ? transformUnion(typ.unionMembers, val)
            : typ.hasOwnProperty("arrayItems")    ? transformArray(typ.arrayItems, val)
            : typ.hasOwnProperty("props")         ? transformObject(getProps(typ), typ.additional, val)
            : invalidValue(typ, val, key, parent);
    }
    // Numbers can be parsed by Date but shouldn't be.
    if (typ === Date && typeof val !== "number") return transformDate(val);
    return transformPrimitive(typ, val);
}

function cast<T>(val: any, typ: any): T {
    return transform(val, typ, jsonToJSProps);
}

function uncast<T>(val: T, typ: any): any {
    return transform(val, typ, jsToJSONProps);
}

function l(typ: any) {
    return { literal: typ };
}

function a(typ: any) {
    return { arrayItems: typ };
}

function u(...typs: any[]) {
    return { unionMembers: typs };
}

function o(props: any[], additional: any) {
    return { props, additional };
}

function m(additional: any) {
    return { props: [], additional };
}

function r(name: string) {
    return { ref: name };
}

const typeMap: any = {
    "ServerConfigSchema": o([
        { json: "api", js: "api", typ: r("API") },
        { json: "cors", js: "cors", typ: r("Cors") },
        { json: "debug", js: "debug", typ: true },
        { json: "environment", js: "environment", typ: r("Environment") },
        { json: "jsonrpc", js: "jsonrpc", typ: r("Jsonrpc") },
        { json: "logging", js: "logging", typ: r("Logging") },
        { json: "nginx", js: "nginx", typ: r("Nginx") },
        { json: "redis", js: "redis", typ: r("Redis") },
        { json: "servers", js: "servers", typ: r("Servers") },
        { json: "sse", js: "sse", typ: r("SSE") },
    ], "any"),
    "API": o([
        { json: "base_path", js: "basePath", typ: "" },
        { json: "rate_limit", js: "rateLimit", typ: r("RateLimit") },
        { json: "swagger_enabled", js: "swaggerEnabled", typ: true },
        { json: "version", js: "version", typ: "" },
    ], "any"),
    "RateLimit": o([
        { json: "max_requests", js: "maxRequests", typ: 0 },
        { json: "window_ms", js: "windowMS", typ: 0 },
    ], "any"),
    "Cors": o([
        { json: "allow_credentials", js: "allowCredentials", typ: true },
        { json: "allowed_headers", js: "allowedHeaders", typ: a("") },
        { json: "allowed_methods", js: "allowedMethods", typ: a(r("AllowedMethod")) },
        { json: "allowed_origins", js: "allowedOrigins", typ: a("") },
    ], "any"),
    "Jsonrpc": o([
        { json: "batch_limit", js: "batchLimit", typ: 0 },
        { json: "timeout", js: "timeout", typ: 0 },
        { json: "version", js: "version", typ: r("Version") },
    ], "any"),
    "Logging": o([
        { json: "console_enabled", js: "consoleEnabled", typ: true },
        { json: "file_enabled", js: "fileEnabled", typ: true },
        { json: "format", js: "format", typ: r("Format") },
        { json: "level", js: "level", typ: r("Level") },
    ], "any"),
    "Nginx": o([
        { json: "health_check_path", js: "healthCheckPath", typ: "" },
        { json: "port", js: "port", typ: 0 },
        { json: "upstream_name", js: "upstreamName", typ: "" },
    ], "any"),
    "Redis": o([
        { json: "db", js: "db", typ: 0 },
        { json: "host", js: "host", typ: "" },
        { json: "max_retries_per_request", js: "maxRetriesPerRequest", typ: u(undefined, 0) },
        { json: "password", js: "password", typ: u(undefined, "") },
        { json: "port", js: "port", typ: 0 },
        { json: "retry_delay_on_failover", js: "retryDelayOnFailover", typ: u(undefined, 0) },
    ], "any"),
    "Servers": o([
        { json: "csharp", js: "csharp", typ: r("ServerInfo") },
        { json: "golang", js: "golang", typ: r("ServerInfo") },
        { json: "nodejs", js: "nodejs", typ: r("ServerInfo") },
        { json: "python", js: "python", typ: r("ServerInfo") },
    ], "any"),
    "ServerInfo": o([
        { json: "host", js: "host", typ: "" },
        { json: "name", js: "name", typ: "" },
        { json: "port", js: "port", typ: 0 },
    ], "any"),
    "SSE": o([
        { json: "heartbeat_interval", js: "heartbeatInterval", typ: 0 },
        { json: "max_connections", js: "maxConnections", typ: 0 },
        { json: "reconnect_timeout", js: "reconnectTimeout", typ: 0 },
    ], "any"),
    "AllowedMethod": [
        "DELETE",
        "GET",
        "HEAD",
        "OPTIONS",
        "PATCH",
        "POST",
        "PUT",
    ],
    "Environment": [
        "development",
        "production",
        "testing",
    ],
    "Version": [
        "2.0",
    ],
    "Format": [
        "json",
        "text",
    ],
    "Level": [
        "debug",
        "error",
        "info",
        "warn",
    ],
};
