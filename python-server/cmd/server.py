"""
FastAPI 서버 설정
JSON RPC 2.0 엔드포인트 제공
"""

import json
import sys
import argparse
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.api.openrpc_server import OpenRpcServer, setup_openrpc_routes
from src.application.user.services.user_service import UserService
from src.domain.user.repositories.redis_user_repository import RedisUserRepository
from src.config.server_config import ServerConfig

import redis.asyncio as redis

# 전역 변수
server_config: ServerConfig = None
openrpc_server: OpenRpcServer = None

# FastAPI 앱 생성 (설정 로드 후 CORS 설정)
app = FastAPI(
    title="Hand in Hand Game Server - Python",
    description="게임 서버 API - JSON RPC 2.0",
    version="1.0.0"
)


def init_app():
    """앱 초기화 (설정 로드 후)"""
    global server_config
    
    # CORS 설정 (설정 파일 기반으로 추후 확장 가능)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if server_config.is_development() else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("startup")
async def startup_event():
    """서버 시작시 초기화"""
    global openrpc_server, server_config
    
    if not server_config:
        raise RuntimeError("Server config not loaded. Please run with --config argument.")
    
    print(f"🚀 Starting {server_config.python_server.name} in {server_config.environment} mode")
    print(f"📊 Debug mode: {server_config.debug}")
    print(f"🔗 Redis: {server_config.redis.host}:{server_config.redis.port}/{server_config.redis.db}")
    print(f"📚 API Docs: http://{server_config.python_server.host}:{server_config.python_server.port}/docs")
    
    # Redis 클라이언트 생성 (설정 기반)
    redis_client = redis.Redis(
        host=server_config.redis.host,
        port=server_config.redis.port,
        db=server_config.redis.db,
        password=server_config.redis.password,
        decode_responses=True
    )
    
    # 의존성 주입
    user_repository = RedisUserRepository(redis_client)
    user_service = UserService(user_repository)
    openrpc_server = OpenRpcServer(user_service)
    
    # OpenRPC 라우트 설정
    setup_openrpc_routes(app, openrpc_server)


@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료시 정리"""
    # Redis 클라이언트 정리 등
    pass


# JSON RPC 엔드포인트는 setup_openrpc_routes에서 처리


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "hand-in-hand-game-server"}


@app.get("/")
async def root():
    """루트 엔드포인트"""
    global server_config
    return {
        "service": f"Hand in Hand Game Server - {server_config.python_server.name}",
        "version": "1.0.0",
        "environment": server_config.environment,
        "api": "JSON RPC 2.0",
        "endpoint": "/api/jsonrpc",
        "documentation": "/docs",
        "openrpc_spec": "/docs/openrpc.json"
    }


def main():
    """메인 진입점"""
    global server_config
    
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description="Hand in Hand Game Server - Python")
    parser.add_argument("--config", required=True, help="Config file path")
    args = parser.parse_args()
    
    # 설정 파일 로드
    config, error = ServerConfig.load_from_file(args.config)
    if error:
        print(f"❌ Failed to load config: {error}", file=sys.stderr)
        sys.exit(1)
    
    server_config = config
    
    # 앱 초기화
    init_app()
    
    # OpenRPC 라우트 설정 (나중에 startup에서 openrpc_server 초기화 후 설정)
    pass
    
    # 서버 실행
    import uvicorn
    uvicorn.run(
        app,
        host=server_config.python_server.host,
        port=server_config.python_server.port,
        log_level="debug" if server_config.debug else "info"
    )


if __name__ == "__main__":
    main()