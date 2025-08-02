"""
계산기 관련 JSON RPC 컨트롤러
Rust WASM 도메인 로직을 Python에서 사용하는 예시
"""

from typing import Dict, Any, Tuple, Optional
import os
import asyncio
import subprocess
from pathlib import Path
import json
import logging
from datetime import datetime

from src.application.user.services.user_domain_service import UserDomainService
from src.domain.user.aggregates.user_aggregates import ProfileEntity

logger = logging.getLogger(__name__)


class CalculatorController:
    """계산기 관련 JSON RPC 핸들러 (Go-style naming)"""
    
    def __init__(self, user_domain_service: UserDomainService):
        self.wasm_enabled = True
        self.domain_service = user_domain_service
    
    
    async def _CallRustAdd(self, a: float, b: float) -> float:
        """Rust WASM add 함수 호출"""
        try:
            # Node.js 스크립트 호출
            wasm_caller_path = str(Path(__file__).parent.parent / "infrastructure" / "wasm" / "wasm_caller.js")
            
            result = await asyncio.create_subprocess_exec(
                'node', wasm_caller_path, 'add', str(a), str(b),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise Exception(f"Node.js script failed: {stderr.decode()}")
            
            response = json.loads(stdout.decode())
            
            if not response.get('success'):
                raise Exception(f"WASM call failed: {response.get('error')}")
            
            return float(response['result'])
            
        except Exception as e:
            logger.error(f"WASM call failed: {e}")
            # Fallback to Python implementation
            return a + b
    
    def _CallRustAddExpToProfile(self, profile_json: str, exp_to_add: int) -> dict:
        """Rust WASM add_exp_to_profile 함수 호출 (실제 구현 대기)"""
        # TODO: 실제 WASM 함수 호출 구현
        # 현재는 Python fallback 사용
        try:
            import json
            profile = json.loads(profile_json)
            
            # Simple level calculation for fallback
            old_level = profile.get("level", 1)
            current_exp = profile.get("exp", 0) + exp_to_add
            
            # Basic level up logic: 100 * (level-1)^1.5
            new_level = old_level
            while new_level < 100:
                required_exp = int(100 * ((new_level) ** 1.5)) if new_level > 1 else 100
                if current_exp >= required_exp:
                    new_level += 1
                else:
                    break
            
            profile["level"] = new_level
            profile["exp"] = current_exp
            
            level_increased = new_level > old_level
            exp_to_next = 0
            if new_level < 100:
                required_exp = int(100 * ((new_level) ** 1.5))
                exp_to_next = max(0, required_exp - current_exp)
            
            progress = 0.0
            if new_level < 100:
                current_level_exp = int(100 * ((new_level - 1) ** 1.5)) if new_level > 1 else 0
                next_level_exp = int(100 * ((new_level) ** 1.5))
                if next_level_exp > current_level_exp:
                    progress = ((current_exp - current_level_exp) / (next_level_exp - current_level_exp)) * 100
            
            return {
                "profile": profile,
                "level_increased": level_increased,
                "exp_to_next_level": exp_to_next,
                "level_progress_percentage": progress,
                "success": True,
                "implementation": "python_fallback"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process profile: {str(e)}",
                "implementation": "python_fallback"
            }
    
    async def Add(self, params: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        두 숫자를 더하는 메서드 (Rust WASM 사용)
        
        Args:
            params: RPC 파라미터 {"a": 10, "b": 20}
            
        Returns:
            tuple[Dict[str, Any] | None, str | None]: (결과, 에러)
        """
        a = params.get("a")
        b = params.get("b")
        
        if a is None or b is None:
            return None, "400: Both 'a' and 'b' parameters are required"
        
        try:
            a_float = float(a)
            b_float = float(b)
            
            # Rust WASM 함수 호출
            if self.wasm_enabled:
                try:
                    result = await self._CallRustAdd(a_float, b_float)
                    implementation = "rust_wasm"
                except Exception as e:
                    logger.warning(f"WASM call failed, using fallback: {e}")
                    result = a_float + b_float
                    implementation = "python_fallback"
            else:
                result = a_float + b_float
                implementation = "python_fallback"
            
            return {
                "result": result,
                "implementation": implementation,
                "wasm_enabled": self.wasm_enabled
            }, None
            
        except (TypeError, ValueError) as e:
            return None, f"400: Invalid number format: {str(e)}"
    
    async def AddExpToProfile(self, params: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        ProfileEntity에 경험치를 추가하는 메서드 (Rust WASM 사용)
        내부에서 기본 프로파일을 생성하고 경험치만 추가
        
        Args:
            params: RPC 파라미터 {"exp_to_add": 100}
            
        Returns:
            tuple[Dict[str, Any] | None, str | None]: (결과, 에러)
        """
        exp_to_add = params.get("exp_to_add")
        
        if exp_to_add is None:
            return None, "400: 'exp_to_add' parameter is required"
        
        try:
            exp_to_add_int = int(exp_to_add)
            if exp_to_add_int < 0:
                return None, "400: 'exp_to_add' must be non-negative"
            
            # 기본 ProfileEntity 객체 생성 (빈 프로파일)
            profile_entity = ProfileEntity(
                nickname="TestPlayer",
                level=1,
                exp=0,
                avatar="default_avatar",
                created_at=datetime.now()
            )
            
            # Application Layer를 통해 도메인 서비스 호출
            domain_result = await self.domain_service.AddExpToProfile(profile_entity, exp_to_add_int)
            
            # 결과 변환
            result = {
                "profile": {
                    "nickname": domain_result.profile.nickname,
                    "level": domain_result.profile.level,
                    "exp": domain_result.profile.exp,
                    "avatar": domain_result.profile.avatar,
                    "created_at": domain_result.profile.created_at.isoformat()
                },
                "level_increased": domain_result.level_increased,
                "exp_to_next_level": domain_result.exp_to_next_level,
                "level_progress_percentage": domain_result.level_progress_percentage,
                "implementation": domain_result.implementation,
                "wasm_enabled": domain_result.wasm_enabled,
                "success": domain_result.success
            }
            
            if domain_result.success:
                return result, None
            else:
                return None, "400: Failed to add experience to profile"
            
        except (TypeError, ValueError, json.JSONEncodeError) as e:
            return None, f"400: Invalid input format: {str(e)}"
        except Exception as e:
            return None, f"500: Internal server error: {str(e)}"
    
    async def Multiply(self, params: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        두 숫자를 곱하는 메서드
        
        Args:
            params: RPC 파라미터 {"a": 10, "b": 20}
            
        Returns:
            tuple[Dict[str, Any] | None, str | None]: (결과, 에러)
        """
        a = params.get("a")
        b = params.get("b")
        
        if a is None or b is None:
            return None, "400: Both 'a' and 'b' parameters are required"
        
        try:
            # 실제로는 Go WASM을 호출하지만, 지금은 Python으로 구현
            result = float(a) * float(b)
            
            return {"result": result}, None
            
        except (TypeError, ValueError) as e:
            return None, f"400: Invalid number format: {str(e)}"
    
    async def CalculateTax(self, params: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        세금을 계산하는 메서드
        
        Args:
            params: RPC 파라미터 {"amount": 100, "taxRate": 10}
            
        Returns:
            tuple[Dict[str, Any] | None, str | None]: (결과, 에러)
        """
        amount = params.get("amount")
        tax_rate = params.get("taxRate")
        
        if amount is None:
            return None, "400: 'amount' parameter is required"
        
        if tax_rate is None:
            return None, "400: 'taxRate' parameter is required"
        
        try:
            amount_float = float(amount)
            tax_rate_float = float(tax_rate)
            
            if amount_float < 0:
                return None, "400: Amount must be non-negative"
            
            if tax_rate_float < 0 or tax_rate_float > 100:
                return None, "400: Tax rate must be between 0 and 100"
            
            # 실제로는 Go WASM을 호출하지만, 지금은 Python으로 구현
            tax = amount_float * (tax_rate_float / 100)
            total = amount_float + tax
            
            result = {
                "amount": amount_float,
                "taxRate": tax_rate_float,
                "tax": round(tax, 2),
                "total": round(total, 2)
            }
            
            return result, None
            
        except (TypeError, ValueError) as e:
            return None, f"400: Invalid number format: {str(e)}"