// Example code that deserializes and serializes the model.
// extern crate serde;
// #[macro_use]
// extern crate serde_derive;
// extern crate serde_json;
//
// use generated_module::server_config_schema;
//
// fn main() {
//     let json = r#"{"answer": 42}"#;
//     let model: server_config_schema = serde_json::from_str(&json).unwrap();
// }

use serde::{Serialize, Deserialize};

/// Configuration schema for all 4 language servers (Node.js, Python, Go, C#)
#[derive(Serialize, Deserialize)]
pub struct ServerConfigSchema {
    api: Api,

    cors: Cors,

    /// Enable debug mode
    debug: bool,

    /// Current environment
    environment: Environment,

    jsonrpc: Jsonrpc,

    logging: Logging,

    nginx: Nginx,

    redis: Redis,

    servers: Servers,

    sse: Sse,
}

#[derive(Serialize, Deserialize)]
pub struct Api {
    /// API base path
    base_path: String,

    rate_limit: RateLimit,

    /// Enable Swagger documentation
    swagger_enabled: bool,

    /// API version
    version: String,
}

#[derive(Serialize, Deserialize)]
pub struct RateLimit {
    /// Maximum requests per window
    max_requests: i64,

    /// Rate limit window in milliseconds
    window_ms: i64,
}

#[derive(Serialize, Deserialize)]
pub struct Cors {
    /// Allow credentials in CORS requests
    allow_credentials: bool,

    /// Allowed HTTP headers
    allowed_headers: Vec<String>,

    /// Allowed HTTP methods
    allowed_methods: Vec<AllowedMethod>,

    /// Allowed CORS origins
    allowed_origins: Vec<String>,
}

#[derive(Serialize, Deserialize)]
pub enum AllowedMethod {
    #[serde(rename = "DELETE")]
    Delete,

    #[serde(rename = "GET")]
    Get,

    #[serde(rename = "HEAD")]
    Head,

    #[serde(rename = "OPTIONS")]
    Options,

    #[serde(rename = "PATCH")]
    Patch,

    #[serde(rename = "POST")]
    Post,

    #[serde(rename = "PUT")]
    Put,
}

/// Current environment
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Environment {
    Development,

    Production,

    Testing,
}

#[derive(Serialize, Deserialize)]
pub struct Jsonrpc {
    /// Maximum batch request size
    batch_limit: i64,

    /// Request timeout in milliseconds
    timeout: i64,

    /// JSON-RPC version
    version: Version,
}

/// JSON-RPC version
#[derive(Serialize, Deserialize)]
pub enum Version {
    #[serde(rename = "2.0")]
    The20,
}

#[derive(Serialize, Deserialize)]
pub struct Logging {
    /// Enable console logging
    console_enabled: bool,

    /// Enable file logging
    file_enabled: bool,

    /// Log format
    format: Format,

    /// Logging level
    level: Level,
}

/// Log format
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Format {
    Json,

    Text,
}

/// Logging level
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Level {
    Debug,

    Error,

    Info,

    Warn,
}

#[derive(Serialize, Deserialize)]
pub struct Nginx {
    /// Health check endpoint path
    health_check_path: String,

    /// NGINX listen port
    port: i64,

    /// NGINX upstream name
    upstream_name: String,
}

#[derive(Serialize, Deserialize)]
pub struct Redis {
    /// Redis database number
    db: i64,

    /// Redis host address
    host: String,

    /// Maximum retry attempts per request
    max_retries_per_request: Option<i64>,

    /// Redis password (optional)
    password: Option<String>,

    /// Redis port number
    port: i64,

    /// Retry delay in milliseconds
    retry_delay_on_failover: Option<i64>,
}

#[derive(Serialize, Deserialize)]
pub struct Servers {
    csharp: ServerInfo,

    golang: ServerInfo,

    nodejs: ServerInfo,

    python: ServerInfo,
}

#[derive(Serialize, Deserialize)]
pub struct ServerInfo {
    /// Server host address
    host: String,

    /// Server name
    name: String,

    /// Server port number
    port: i64,
}

#[derive(Serialize, Deserialize)]
pub struct Sse {
    /// SSE heartbeat interval in milliseconds
    heartbeat_interval: i64,

    /// Maximum SSE connections
    max_connections: i64,

    /// SSE reconnect timeout in milliseconds
    reconnect_timeout: i64,
}
