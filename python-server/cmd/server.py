"""
FastAPI 서버 설정
JSON RPC 2.0 엔드포인트 제공
"""

import json
import sys
import argparse
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.api.openrpc_server import OpenRpcServer, setup_openrpc_routes
from src.application.user.services.user_service import UserService
from src.application.user.services.user_domain_service import UserDomainService
from src.domain.user.repositories.redis_user_repository import RedisUserRepository
from src.config.server_config import ServerConfig
from src.infrastructure.wasm.wasm_instance import CreateWasmInstance

import redis.asyncio as redis
import os
from pathlib import Path

# 전역 변수
server_config: ServerConfig = None
openrpc_server: OpenRpcServer = None
wasm_file_path: Optional[str] = None

# Pydantic 모델 정의
class JsonRpcRequestBody(BaseModel):
    """JSON-RPC 2.0 요청 본문"""
    jsonrpc: str = Field("2.0", description="JSON-RPC 버전", example="2.0")
    method: str = Field(..., description="호출할 메서드명", example="calculator.add")
    params: Dict[str, Any] = Field({}, description="메서드 파라미터", example={"a": 10, "b": 20})
    id: Any = Field(1, description="요청 ID", example=1)

class JsonRpcResponseBody(BaseModel):
    """JSON-RPC 2.0 응답 본문"""
    jsonrpc: str = Field("2.0", description="JSON-RPC 버전")
    result: Any = Field(None, description="성공 결과")
    error: Dict[str, Any] = Field(None, description="에러 정보")
    id: Any = Field(None, description="요청 ID")

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
    
    # WASM 경로 결정
    global wasm_file_path
    if wasm_file_path:
        # 명령행 인자로 지정된 경로 사용
        wasm_path = Path(wasm_file_path)
    else:
        # 기본 경로 사용 (WASI WASM)
        project_root = Path(__file__).parent.parent.parent  # python-server의 부모 디렉토리
        wasm_path = project_root / "shared" / "domain-rust" / "pkg-wasmtime" / "domain_rust.wasm"
    
    print(f"🔍 Looking for WASM file at: {wasm_path}")
    
    # WASM 파일 존재 여부 확인
    if not wasm_path.exists():
        error_msg = f"❌ CRITICAL: WASM file not found at: {wasm_path}"
        print(error_msg)
        print("💡 To build WASM module, run: cd shared/domain-rust && ./build.sh")
        print("💡 Or specify WASM path with: --wasm /path/to/domain_rust.wasm")
        raise RuntimeError(f"WASM module is required but not found: {wasm_path}")
    
    # WASM 인스턴스 생성
    wasm_instance, wasm_error = CreateWasmInstance(str(wasm_path))
    if wasm_error:
        error_msg = f"❌ CRITICAL: WASM initialization failed: {wasm_error}"
        print(error_msg)
        print("💡 Check if wasmer-python is installed: pip install wasmer wasmer-compiler-cranelift")
        raise RuntimeError(f"WASM module initialization failed: {wasm_error}")
    
    print("✅ WASM instance created successfully")
    
    # 의존성 주입
    user_repository = RedisUserRepository(redis_client)
    user_domain_service = UserDomainService(wasm_instance)
    user_service = UserService(user_repository, user_domain_service)
    openrpc_server = OpenRpcServer(user_service)
    
    # OpenRPC 라우트 설정
    setup_openrpc_routes(app, openrpc_server)


@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료시 정리"""
    # Redis 클라이언트 정리 등
    pass


# JSON RPC 엔드포인트는 setup_openrpc_routes에서 처리

# Swagger UI용 JSON-RPC 테스트 엔드포인트 추가
@app.post("/api/jsonrpc", 
    summary="JSON-RPC 2.0 Endpoint",
    description="JSON-RPC 2.0 엔드포인트. 완전한 JSON-RPC 기능은 OpenRPC Playground (/docs)를 사용하세요.",
    response_model=JsonRpcResponseBody,
    tags=["JSON-RPC"])
async def swagger_jsonrpc_endpoint(request_body: JsonRpcRequestBody):
    """
    Swagger UI용 JSON-RPC 엔드포인트
    
    **사용 가능한 메서드:**
    - `calculator.add`: 두 숫자 덧셈 (Rust WASM)
    - `getUserAggregates`: 사용자 데이터 조회
    
    **calculator.add 예시:**
    - params: `{"a": 10, "b": 20}`
    - 결과: `{"result": 30, "implementation": "rust_wasm", "wasm_enabled": true}`
    
    **getUserAggregates 예시:**
    - params: `{"userId": "user123"}`
    """
    global openrpc_server
    if not openrpc_server:
        raise HTTPException(status_code=500, detail="OpenRPC server not initialized")
    
    # Pydantic 모델을 dict로 변환
    request_dict = request_body.model_dump()
    response_data = await openrpc_server.handle_request(request_dict)
    return response_data


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
    global server_config, wasm_file_path
    
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description="Hand in Hand Game Server - Python")
    parser.add_argument("--config", required=True, help="Config file path")
    parser.add_argument("--wasm", 
                       help="WASM module file path (default: ../shared/domain-rust/pkg-wasmtime/domain_rust.wasm)")
    args = parser.parse_args()
    
    # 설정 파일 로드
    config, error = ServerConfig.load_from_file(args.config)
    if error:
        print(f"❌ Failed to load config: {error}", file=sys.stderr)
        sys.exit(1)
    
    server_config = config
    wasm_file_path = args.wasm  # WASM 경로 저장
    
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