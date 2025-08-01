"""
서버 설정 관리
JSON Schema 기반 설정 로드 및 관리
"""

import json
import os
from typing import Optional
from dataclasses import dataclass

from .server_config_schema import (
    ServerConfigSchema as SchemaServerConfig,
    server_config_schema_from_dict
)


@dataclass
class ServerInfo:
    """서버 정보"""
    port: int
    host: str
    name: str


@dataclass
class RedisConfig:
    """Redis 설정"""
    host: str
    port: int
    db: int
    password: Optional[str] = None
    retry_delay_on_failover: Optional[int] = None
    max_retries_per_request: Optional[int] = None


@dataclass
class ServerConfig:
    """서버 설정 (비즈니스 로직 포함)"""
    environment: str
    debug: bool
    python_server: ServerInfo
    redis: RedisConfig
    
    @classmethod
    def from_schema(cls, schema_config: SchemaServerConfig) -> 'ServerConfig':
        """스키마 객체에서 비즈니스 객체로 변환"""
        # Python 서버 정보 추출
        python_server = ServerInfo(
            port=schema_config.servers.python.port,
            host=schema_config.servers.python.host,
            name=schema_config.servers.python.name
        )
        
        # Redis 설정 추출
        redis_config = RedisConfig(
            host=schema_config.redis.host,
            port=schema_config.redis.port,
            db=schema_config.redis.db,
            password=getattr(schema_config.redis, 'password', None),
            retry_delay_on_failover=getattr(schema_config.redis, 'retry_delay_on_failover', None),
            max_retries_per_request=getattr(schema_config.redis, 'max_retries_per_request', None)
        )
        
        return cls(
            environment=schema_config.environment,
            debug=schema_config.debug,
            python_server=python_server,
            redis=redis_config
        )
    
    @classmethod
    def load_from_file(cls, config_path: str) -> tuple['ServerConfig | None', str | None]:
        """
        JSON 파일에서 설정 로드
        
        Args:
            config_path: 설정 파일 경로
            
        Returns:
            tuple[ServerConfig | None, str | None]: (설정 객체, 에러)
        """
        try:
            # 파일 존재 확인
            if not os.path.exists(config_path):
                return None, f"400: Config file not found: {config_path}"
            
            # JSON 파일 읽기
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # JSON Schema 검증 및 객체 생성
            schema_config = server_config_schema_from_dict(config_data)
            
            # 비즈니스 객체로 변환
            server_config = cls.from_schema(schema_config)
            
            return server_config, None
            
        except json.JSONDecodeError as e:
            return None, f"400: Invalid JSON in config file: {str(e)}"
        except Exception as e:
            return None, f"500: Failed to load config: {str(e)}"
    
    def is_development(self) -> bool:
        """개발 환경 여부"""
        return self.environment == "development"
    
    def is_production(self) -> bool:
        """운영 환경 여부"""
        return self.environment == "production"
    
    def get_redis_url(self) -> str:
        """Redis 연결 URL 생성"""
        if self.redis.password:
            return f"redis://:{self.redis.password}@{self.redis.host}:{self.redis.port}/{self.redis.db}"
        else:
            return f"redis://{self.redis.host}:{self.redis.port}/{self.redis.db}"