#!/usr/bin/env python3
"""
Rust WASM Calculator JSON-RPC 테스트 스크립트
"""

import asyncio
import json
from src.api.controllers.calculator_controller import CalculatorController
from src.api.openrpc_server import OpenRpcServer
from src.application.user.services.user_service import UserService


async def test_calculator_controller():
    """CalculatorController 직접 테스트"""
    print("🧪 Testing CalculatorController directly...")
    
    controller = CalculatorController()
    
    # 테스트 케이스들
    test_cases = [
        {"a": 10, "b": 20},
        {"a": 5.5, "b": 4.5}, 
        {"a": -1, "b": 1},
        {"a": 0, "b": 0},
        {"a": "invalid", "b": 20},  # 에러 케이스
        {"a": 10},  # 누락된 파라미터
    ]
    
    for i, params in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {params}")
        try:
            result, error = await controller.add(params)
            if error:
                print(f"❌ Error: {error}")
            else:
                print(f"✅ Result: {result}")
        except Exception as e:
            print(f"💥 Exception: {e}")


async def test_jsonrpc_server():
    """JSON-RPC 서버 테스트"""
    print("\n\n🌐 Testing JSON-RPC Server...")
    
    # MockUserService 생성 (실제 서비스 대신)
    class MockUserService:
        async def get_user_aggregates(self, user_id: str):
            return None, "Mock service - not implemented"
    
    user_service = MockUserService()
    rpc_server = OpenRpcServer(user_service)
    
    # JSON-RPC 요청 테스트
    test_requests = [
        {
            "jsonrpc": "2.0",
            "method": "calculator.add",
            "params": {"a": 15, "b": 25},
            "id": 1
        },
        {
            "jsonrpc": "2.0", 
            "method": "calculator.add",
            "params": {"a": 3.14, "b": 2.86},
            "id": 2
        },
        {
            "jsonrpc": "2.0",
            "method": "calculator.add", 
            "params": {"a": "invalid", "b": 10},
            "id": 3
        },
        {
            "jsonrpc": "2.0",
            "method": "calculator.add",
            "params": {"a": 10},  # 누락된 b 파라미터
            "id": 4
        },
        {
            "jsonrpc": "2.0",
            "method": "nonexistent.method",
            "params": {},
            "id": 5
        }
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n📋 JSON-RPC Test {i}:")
        print(f"📤 Request: {json.dumps(request, indent=2)}")
        
        try:
            response = await rpc_server.handle_request(request)
            print(f"📥 Response: {json.dumps(response, indent=2)}")
        except Exception as e:
            print(f"💥 Exception: {e}")


async def test_openrpc_spec():
    """OpenRPC 스펙 테스트"""
    print("\n\n📋 Testing OpenRPC Specification...")
    
    class MockUserService:
        pass
    
    user_service = MockUserService()
    rpc_server = OpenRpcServer(user_service)
    
    spec = rpc_server.get_openrpc_spec()
    
    print("📋 OpenRPC Specification:")
    print(json.dumps(spec, indent=2, ensure_ascii=False))
    
    # calculator.add 메서드가 포함되었는지 확인
    methods = spec.get("methods", [])
    calculator_method = None
    for method in methods:
        if method.get("name") == "calculator.add":
            calculator_method = method
            break
    
    if calculator_method:
        print(f"\n✅ calculator.add 메서드가 OpenRPC 스펙에 포함되었습니다!")
        print(f"📝 Summary: {calculator_method.get('summary')}")
        print(f"📝 Description: {calculator_method.get('description')}")
    else:
        print(f"\n❌ calculator.add 메서드가 OpenRPC 스펙에 없습니다!")


async def main():
    """메인 테스트 함수"""
    print("🦀 Rust WASM Calculator JSON-RPC Integration Test")
    print("=" * 60)
    
    await test_calculator_controller()
    await test_jsonrpc_server()
    await test_openrpc_spec()
    
    print(f"\n🎉 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(main())