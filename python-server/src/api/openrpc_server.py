"""
OpenRPC 표준 기반 JSON RPC 2.0 서버
표준 OpenRPC Playground UI 지원
"""

import json
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.application.user.services.user_service import UserService


class JsonRpcRequest(BaseModel):
    """JSON RPC 2.0 요청 모델"""
    jsonrpc: str = Field("2.0", description="JSON RPC 버전")
    method: str = Field(..., description="호출할 메서드명")
    params: Optional[Dict[str, Any]] = Field(None, description="메서드 파라미터")
    id: Optional[Any] = Field(None, description="요청 ID")


class JsonRpcResponse(BaseModel):
    """JSON RPC 2.0 응답 모델"""
    jsonrpc: str = Field("2.0", description="JSON RPC 버전")
    result: Optional[Any] = Field(None, description="성공 결과")
    error: Optional[Dict[str, Any]] = Field(None, description="에러 정보")
    id: Optional[Any] = Field(None, description="요청 ID")


class JsonRpcError:
    """JSON RPC 2.0 표준 에러 코드"""
    PARSE_ERROR = -32700  # JSON 파싱 에러
    INVALID_REQUEST = -32600  # 잘못된 요청
    METHOD_NOT_FOUND = -32601  # 메서드를 찾을 수 없음
    INVALID_PARAMS = -32602  # 잘못된 파라미터
    INTERNAL_ERROR = -32603  # 내부 에러
    
    # 커스텀 에러 코드
    USER_NOT_FOUND = -32001  # 사용자를 찾을 수 없음


class OpenRpcServer:
    """OpenRPC 표준 JSON RPC 2.0 서버"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.methods = {
            "getUserAggregates": self._get_user_aggregates
        }
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        JSON RPC 2.0 요청 처리
        
        Args:
            request_data: JSON RPC 요청 데이터
            
        Returns:
            Dict[str, Any]: JSON RPC 응답
        """
        try:
            # 요청 검증
            rpc_request = JsonRpcRequest(**request_data)
            
            # 메서드 존재 확인
            if rpc_request.method not in self.methods:
                return self._create_error_response(
                    JsonRpcError.METHOD_NOT_FOUND,
                    f"Method '{rpc_request.method}' not found",
                    rpc_request.id
                )
            
            # 메서드 실행
            method = self.methods[rpc_request.method]
            result = await method(rpc_request.params or {})
            
            return self._create_success_response(result, rpc_request.id)
            
        except ValidationError as e:
            return self._create_error_response(
                JsonRpcError.INVALID_REQUEST,
                f"Invalid request: {str(e)}",
                None
            )
        except Exception as e:
            return self._create_error_response(
                JsonRpcError.INTERNAL_ERROR,
                f"Internal server error: {str(e)}",
                request_data.get("id")
            )
    
    async def _get_user_aggregates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        getUserAggregates 메서드 구현
        
        Args:
            params: 메서드 파라미터
            
        Returns:
            Dict[str, Any]: 사용자 전체 데이터
            
        Raises:
            Exception: 에러 발생 시
        """
        # 파라미터 검증
        user_id = params.get("userId")
        if not user_id:
            raise ValueError("userId parameter is required")
        
        # 서비스 레이어 호출
        user_data, error = await self.user_service.get_user_aggregates(user_id)
        
        if error:
            if error.startswith("400"):
                raise ValueError(error.split(": ", 1)[1])
            elif error.startswith("0x001001"):
                raise Exception("USER_NOT_FOUND")
            else:
                raise Exception(f"Service error: {error}")
        
        # 응답 데이터 변환
        return {
            "profile": {
                "nickname": user_data.profile.nickname,
                "level": user_data.profile.level,
                "exp": user_data.profile.exp,
                "avatar": user_data.profile.avatar,
                "created_at": user_data.profile.created_at.isoformat()
            },
            "inventory": {
                "items": user_data.inventory.items,
                "gold": user_data.inventory.gold,
                "gems": user_data.inventory.gems,
                "capacity": user_data.inventory.capacity
            }
        }
    
    def _create_success_response(self, result: Any, request_id: Any) -> Dict[str, Any]:
        """성공 응답 생성"""
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
    
    def _create_error_response(self, code: int, message: str, request_id: Any) -> Dict[str, Any]:
        """에러 응답 생성"""
        # 커스텀 에러 매핑
        if message == "USER_NOT_FOUND":
            code = JsonRpcError.USER_NOT_FOUND
            message = "User not found"
        elif "userId parameter is required" in message:
            code = JsonRpcError.INVALID_PARAMS
        
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        }
    
    def get_openrpc_spec(self) -> Dict[str, Any]:
        """OpenRPC 스펙 반환"""
        try:
            # 공용 OpenRPC 스펙 파일 로드
            spec_path = "/Users/danghamo/Documents/gituhb/handinhand/shared/docs/openrpc.json"
            with open(spec_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            # 기본 스펙 반환
            return {
                "openrpc": "1.2.6",
                "info": {
                    "title": "Hand in Hand Game Server API",
                    "version": "1.0.0",
                    "description": "게임 서버 JSON RPC 2.0 API"
                },
                "methods": [
                    {
                        "name": "getUserAggregates",
                        "summary": "사용자 전체 데이터 조회",
                        "params": [
                            {
                                "name": "userId",
                                "schema": {"type": "string"},
                                "required": True
                            }
                        ],
                        "result": {
                            "name": "UserAggregates",
                            "schema": {"type": "object"}
                        }
                    }
                ]
            }


def setup_openrpc_routes(app: FastAPI, openrpc_server: OpenRpcServer):
    """FastAPI 앱에 OpenRPC 라우트 설정"""
    
    @app.post("/api/jsonrpc")
    async def jsonrpc_endpoint(request: Request):
        """JSON RPC 2.0 엔드포인트"""
        try:
            body = await request.body()
            request_data = json.loads(body)
            
            response_data = await openrpc_server.handle_request(request_data)
            return JSONResponse(content=response_data)
            
        except json.JSONDecodeError:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": JsonRpcError.PARSE_ERROR,
                        "message": "Parse error"
                    },
                    "id": None
                },
                status_code=200
            )
        except Exception as e:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": JsonRpcError.INTERNAL_ERROR,
                        "message": f"Internal server error: {str(e)}"
                    },
                    "id": None
                },
                status_code=200
            )
    
    @app.get("/docs/openrpc.json")
    async def openrpc_spec():
        """OpenRPC 스펙 파일"""
        return openrpc_server.get_openrpc_spec()
    
    @app.get("/docs", response_class=HTMLResponse)
    async def openrpc_playground():
        """OpenRPC Playground UI"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Hand in Hand Game Server - API Documentation</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { margin: 0; padding: 0; }
    </style>
</head>
<body>
    <div id="rpc-playground"></div>
    <script src="https://unpkg.com/@open-rpc/playground@latest/build/static/js/app.js"></script>
    <script>
        const playground = new RPCPlayground({
            openrpcDocument: "/docs/openrpc.json",
            methodPlugins: [],
            requestPlugins: []
        });
        
        playground.render(document.getElementById("rpc-playground"));
    </script>
</body>
</html>
        """
        return html