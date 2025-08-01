from dataclasses import dataclass
from typing import Any, List, Optional, TypeVar, Type, cast, Callable
from enum import Enum


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


@dataclass
class RateLimit:
    max_requests: int
    """Maximum requests per window"""

    window_ms: int
    """Rate limit window in milliseconds"""

    @staticmethod
    def from_dict(obj: Any) -> 'RateLimit':
        assert isinstance(obj, dict)
        max_requests = from_int(obj.get("max_requests"))
        window_ms = from_int(obj.get("window_ms"))
        return RateLimit(max_requests, window_ms)

    def to_dict(self) -> dict:
        result: dict = {}
        result["max_requests"] = from_int(self.max_requests)
        result["window_ms"] = from_int(self.window_ms)
        return result


@dataclass
class API:
    base_path: str
    """API base path"""

    rate_limit: RateLimit
    swagger_enabled: bool
    """Enable Swagger documentation"""

    version: str
    """API version"""

    @staticmethod
    def from_dict(obj: Any) -> 'API':
        assert isinstance(obj, dict)
        base_path = from_str(obj.get("base_path"))
        rate_limit = RateLimit.from_dict(obj.get("rate_limit"))
        swagger_enabled = from_bool(obj.get("swagger_enabled"))
        version = from_str(obj.get("version"))
        return API(base_path, rate_limit, swagger_enabled, version)

    def to_dict(self) -> dict:
        result: dict = {}
        result["base_path"] = from_str(self.base_path)
        result["rate_limit"] = to_class(RateLimit, self.rate_limit)
        result["swagger_enabled"] = from_bool(self.swagger_enabled)
        result["version"] = from_str(self.version)
        return result


class AllowedMethod(Enum):
    DELETE = "DELETE"
    GET = "GET"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"


@dataclass
class Cors:
    allow_credentials: bool
    """Allow credentials in CORS requests"""

    allowed_headers: List[str]
    """Allowed HTTP headers"""

    allowed_methods: List[AllowedMethod]
    """Allowed HTTP methods"""

    allowed_origins: List[str]
    """Allowed CORS origins"""

    @staticmethod
    def from_dict(obj: Any) -> 'Cors':
        assert isinstance(obj, dict)
        allow_credentials = from_bool(obj.get("allow_credentials"))
        allowed_headers = from_list(from_str, obj.get("allowed_headers"))
        allowed_methods = from_list(AllowedMethod, obj.get("allowed_methods"))
        allowed_origins = from_list(from_str, obj.get("allowed_origins"))
        return Cors(allow_credentials, allowed_headers, allowed_methods, allowed_origins)

    def to_dict(self) -> dict:
        result: dict = {}
        result["allow_credentials"] = from_bool(self.allow_credentials)
        result["allowed_headers"] = from_list(from_str, self.allowed_headers)
        result["allowed_methods"] = from_list(lambda x: to_enum(AllowedMethod, x), self.allowed_methods)
        result["allowed_origins"] = from_list(from_str, self.allowed_origins)
        return result


class Environment(Enum):
    """Current environment"""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class Version(Enum):
    """JSON-RPC version"""

    THE_20 = "2.0"


@dataclass
class Jsonrpc:
    batch_limit: int
    """Maximum batch request size"""

    timeout: int
    """Request timeout in milliseconds"""

    version: Version
    """JSON-RPC version"""

    @staticmethod
    def from_dict(obj: Any) -> 'Jsonrpc':
        assert isinstance(obj, dict)
        batch_limit = from_int(obj.get("batch_limit"))
        timeout = from_int(obj.get("timeout"))
        version = Version(obj.get("version"))
        return Jsonrpc(batch_limit, timeout, version)

    def to_dict(self) -> dict:
        result: dict = {}
        result["batch_limit"] = from_int(self.batch_limit)
        result["timeout"] = from_int(self.timeout)
        result["version"] = to_enum(Version, self.version)
        return result


class Format(Enum):
    """Log format"""

    JSON = "json"
    TEXT = "text"


class Level(Enum):
    """Logging level"""

    DEBUG = "debug"
    ERROR = "error"
    INFO = "info"
    WARN = "warn"


@dataclass
class Logging:
    console_enabled: bool
    """Enable console logging"""

    file_enabled: bool
    """Enable file logging"""

    format: Format
    """Log format"""

    level: Level
    """Logging level"""

    @staticmethod
    def from_dict(obj: Any) -> 'Logging':
        assert isinstance(obj, dict)
        console_enabled = from_bool(obj.get("console_enabled"))
        file_enabled = from_bool(obj.get("file_enabled"))
        format = Format(obj.get("format"))
        level = Level(obj.get("level"))
        return Logging(console_enabled, file_enabled, format, level)

    def to_dict(self) -> dict:
        result: dict = {}
        result["console_enabled"] = from_bool(self.console_enabled)
        result["file_enabled"] = from_bool(self.file_enabled)
        result["format"] = to_enum(Format, self.format)
        result["level"] = to_enum(Level, self.level)
        return result


@dataclass
class Nginx:
    health_check_path: str
    """Health check endpoint path"""

    port: int
    """NGINX listen port"""

    upstream_name: str
    """NGINX upstream name"""

    @staticmethod
    def from_dict(obj: Any) -> 'Nginx':
        assert isinstance(obj, dict)
        health_check_path = from_str(obj.get("health_check_path"))
        port = from_int(obj.get("port"))
        upstream_name = from_str(obj.get("upstream_name"))
        return Nginx(health_check_path, port, upstream_name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["health_check_path"] = from_str(self.health_check_path)
        result["port"] = from_int(self.port)
        result["upstream_name"] = from_str(self.upstream_name)
        return result


@dataclass
class Redis:
    db: int
    """Redis database number"""

    host: str
    """Redis host address"""

    port: int
    """Redis port number"""

    max_retries_per_request: Optional[int] = None
    """Maximum retry attempts per request"""

    password: Optional[str] = None
    """Redis password (optional)"""

    retry_delay_on_failover: Optional[int] = None
    """Retry delay in milliseconds"""

    @staticmethod
    def from_dict(obj: Any) -> 'Redis':
        assert isinstance(obj, dict)
        db = from_int(obj.get("db"))
        host = from_str(obj.get("host"))
        port = from_int(obj.get("port"))
        max_retries_per_request = from_union([from_int, from_none], obj.get("max_retries_per_request"))
        password = from_union([from_str, from_none], obj.get("password"))
        retry_delay_on_failover = from_union([from_int, from_none], obj.get("retry_delay_on_failover"))
        return Redis(db, host, port, max_retries_per_request, password, retry_delay_on_failover)

    def to_dict(self) -> dict:
        result: dict = {}
        result["db"] = from_int(self.db)
        result["host"] = from_str(self.host)
        result["port"] = from_int(self.port)
        if self.max_retries_per_request is not None:
            result["max_retries_per_request"] = from_union([from_int, from_none], self.max_retries_per_request)
        if self.password is not None:
            result["password"] = from_union([from_str, from_none], self.password)
        if self.retry_delay_on_failover is not None:
            result["retry_delay_on_failover"] = from_union([from_int, from_none], self.retry_delay_on_failover)
        return result


@dataclass
class ServerInfo:
    host: str
    """Server host address"""

    name: str
    """Server name"""

    port: int
    """Server port number"""

    @staticmethod
    def from_dict(obj: Any) -> 'ServerInfo':
        assert isinstance(obj, dict)
        host = from_str(obj.get("host"))
        name = from_str(obj.get("name"))
        port = from_int(obj.get("port"))
        return ServerInfo(host, name, port)

    def to_dict(self) -> dict:
        result: dict = {}
        result["host"] = from_str(self.host)
        result["name"] = from_str(self.name)
        result["port"] = from_int(self.port)
        return result


@dataclass
class Servers:
    csharp: ServerInfo
    golang: ServerInfo
    nodejs: ServerInfo
    python: ServerInfo

    @staticmethod
    def from_dict(obj: Any) -> 'Servers':
        assert isinstance(obj, dict)
        csharp = ServerInfo.from_dict(obj.get("csharp"))
        golang = ServerInfo.from_dict(obj.get("golang"))
        nodejs = ServerInfo.from_dict(obj.get("nodejs"))
        python = ServerInfo.from_dict(obj.get("python"))
        return Servers(csharp, golang, nodejs, python)

    def to_dict(self) -> dict:
        result: dict = {}
        result["csharp"] = to_class(ServerInfo, self.csharp)
        result["golang"] = to_class(ServerInfo, self.golang)
        result["nodejs"] = to_class(ServerInfo, self.nodejs)
        result["python"] = to_class(ServerInfo, self.python)
        return result


@dataclass
class SSE:
    heartbeat_interval: int
    """SSE heartbeat interval in milliseconds"""

    max_connections: int
    """Maximum SSE connections"""

    reconnect_timeout: int
    """SSE reconnect timeout in milliseconds"""

    @staticmethod
    def from_dict(obj: Any) -> 'SSE':
        assert isinstance(obj, dict)
        heartbeat_interval = from_int(obj.get("heartbeat_interval"))
        max_connections = from_int(obj.get("max_connections"))
        reconnect_timeout = from_int(obj.get("reconnect_timeout"))
        return SSE(heartbeat_interval, max_connections, reconnect_timeout)

    def to_dict(self) -> dict:
        result: dict = {}
        result["heartbeat_interval"] = from_int(self.heartbeat_interval)
        result["max_connections"] = from_int(self.max_connections)
        result["reconnect_timeout"] = from_int(self.reconnect_timeout)
        return result


@dataclass
class ServerConfigSchema:
    """Configuration schema for all 4 language servers (Node.js, Python, Go, C#)"""

    api: API
    cors: Cors
    debug: bool
    """Enable debug mode"""

    environment: Environment
    """Current environment"""

    jsonrpc: Jsonrpc
    logging: Logging
    nginx: Nginx
    redis: Redis
    servers: Servers
    sse: SSE

    @staticmethod
    def from_dict(obj: Any) -> 'ServerConfigSchema':
        assert isinstance(obj, dict)
        api = API.from_dict(obj.get("api"))
        cors = Cors.from_dict(obj.get("cors"))
        debug = from_bool(obj.get("debug"))
        environment = Environment(obj.get("environment"))
        jsonrpc = Jsonrpc.from_dict(obj.get("jsonrpc"))
        logging = Logging.from_dict(obj.get("logging"))
        nginx = Nginx.from_dict(obj.get("nginx"))
        redis = Redis.from_dict(obj.get("redis"))
        servers = Servers.from_dict(obj.get("servers"))
        sse = SSE.from_dict(obj.get("sse"))
        return ServerConfigSchema(api, cors, debug, environment, jsonrpc, logging, nginx, redis, servers, sse)

    def to_dict(self) -> dict:
        result: dict = {}
        result["api"] = to_class(API, self.api)
        result["cors"] = to_class(Cors, self.cors)
        result["debug"] = from_bool(self.debug)
        result["environment"] = to_enum(Environment, self.environment)
        result["jsonrpc"] = to_class(Jsonrpc, self.jsonrpc)
        result["logging"] = to_class(Logging, self.logging)
        result["nginx"] = to_class(Nginx, self.nginx)
        result["redis"] = to_class(Redis, self.redis)
        result["servers"] = to_class(Servers, self.servers)
        result["sse"] = to_class(SSE, self.sse)
        return result


def server_config_schema_from_dict(s: Any) -> ServerConfigSchema:
    return ServerConfigSchema.from_dict(s)


def server_config_schema_to_dict(x: ServerConfigSchema) -> Any:
    return to_class(ServerConfigSchema, x)
