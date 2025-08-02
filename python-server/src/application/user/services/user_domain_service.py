"""
사용자 도메인 서비스
Rust WASM 도메인 로직을 호출하여 비즈니스 로직 처리
CLAUDE.md 규칙 준수: 명시적 에러 처리, Go-style naming
"""

from typing import Tuple, Optional
from dataclasses import dataclass
import logging

from src.domain.user.aggregates.user_aggregates import ProfileEntity

try:
    from wasmtime import Instance
    WASMTIME_AVAILABLE = True
except ImportError:
    WASMTIME_AVAILABLE = False
    Instance = None

logger = logging.getLogger(__name__)


@dataclass
class ProfileExpResult:
    """프로필 경험치 추가 결과"""
    profile: ProfileEntity
    level_increased: bool
    exp_to_next_level: int
    level_progress_percentage: float
    implementation: str
    wasm_enabled: bool
    success: bool


class UserDomainService:
    """사용자 도메인 서비스 - Rust WASM 도메인 로직 호출 (Go-style naming, 명시적 에러 처리)"""
    
    def __init__(self, wasm_instance: Instance):
        self.wasm_instance = wasm_instance
        logger.info(f"UserDomainService initialized with WASM instance")
        
        # 사용 가능한 exports 확인
        try:
            available_exports = list(self.wasm_instance.exports(self.wasm_instance.store).keys())
            logger.info(f"WASM exports available: {available_exports}")
        except Exception as e:
            logger.warning(f"Failed to list WASM exports: {e}")
    
    async def AddExpToProfile(self, profile: ProfileEntity, exp_to_add: int) -> Tuple[Optional[ProfileExpResult], Optional[str]]:
        """
        프로필에 경험치 추가 (Go-style naming, 명시적 에러 처리)
        
        Args:
            profile: 프로필 엔티티
            exp_to_add: 추가할 경험치
            
        Returns:
            Tuple[Optional[ProfileExpResult], Optional[str]]: (결과, 에러메시지)
        """
        
        result, error = await self._CallWasmAddExpToProfile(profile, exp_to_add)
        if error:
            logger.warning(f"WASM call failed, using fallback: {error}")
            # Fallback to Python implementation
            return await self._PythonFallbackAddExpToProfile(profile, exp_to_add)
        
        return result, None
    
    # === WASM 호출 메서드 (private) === #
    
    async def _CallWasmAddExpToProfile(self, profile: ProfileEntity, exp_to_add: int) -> Tuple[Optional[ProfileExpResult], Optional[str]]:
        """Rust WASM AddExpToProfile 함수 호출 (Go-style naming, 명시적 에러 처리)"""
        
        try:
            # WASM 함수 확인 (JSON 버전 사용)
            try:
                wasm_func = self.wasm_instance.exports(self.wasm_instance.store)['add_exp_to_profile_json']
            except KeyError:
                logger.warning("add_exp_to_profile_json function not found in WASM exports")
                return None, "500: add_exp_to_profile_json function not available in WASM"
            
            logger.info(f"Calling WASM add_exp_to_profile_json with exp: {exp_to_add}")
            
            # ProfileEntity를 JSON string으로 변환
            profile_data = {
                "nickname": profile.nickname,
                "level": profile.level,
                "exp": profile.exp,
                "avatar": profile.avatar,
                "created_at": profile.created_at.isoformat() if hasattr(profile.created_at, 'isoformat') else str(profile.created_at)
            }
            
            import json
            profile_json = json.dumps(profile_data)
            
            # WASM 메모리에 문자열 쓰기
            from wasmtime import Caller
            
            # 메모리 접근
            memory = self.wasm_instance.exports(self.wasm_instance.store)["memory"]
            
            # JSON 문자열을 바이트로 변환하고 null terminator 추가
            json_bytes = profile_json.encode('utf-8') + b'\0'
            
            # WASM 메모리에 문자열 쓰기 (간단히 시작 주소에 쓰기)
            memory_data = memory.data_ptr(self.wasm_instance.store)
            memory_size = memory.data_len(self.wasm_instance.store)
            
            if len(json_bytes) > memory_size:
                return None, "500: JSON string too large for WASM memory"
            
            # 메모리에 문자열 복사
            import ctypes
            ctypes.memmove(memory_data, json_bytes, len(json_bytes))
            
            # WASM 함수 호출 (메모리 주소 포인터와 int 인자)
            result_ptr = wasm_func(self.wasm_instance.store, 0, exp_to_add)  # 0은 메모리 시작 주소
            
            # 결과 문자열 읽기 (포인터에서)
            if result_ptr == 0:
                return None, "500: WASM function returned null pointer"
            
            # 포인터에서 문자열 읽기 (ctypes 포인터 연산 수정)
            result_address = ctypes.addressof(memory_data.contents) + result_ptr
            result_json = ctypes.string_at(result_address).decode('utf-8')
            
            # 결과 파싱 (WASM에서 JSON string 반환)
            result_data = json.loads(result_json)
            
            # 에러 체크
            if "error" in result_data:
                error_msg = f"500: WASM function error: {result_data['error']}"
                logger.error(error_msg)
                return None, error_msg
            
            # 결과에서 ProfileEntity 재구성
            updated_profile_data = result_data.get("profile", {})
            updated_profile = ProfileEntity(
                nickname=updated_profile_data.get("nickname", profile.nickname),
                level=updated_profile_data.get("level", profile.level),
                exp=updated_profile_data.get("exp", profile.exp),
                avatar=updated_profile_data.get("avatar", profile.avatar),
                created_at=updated_profile_data.get("created_at", profile.created_at)
            )
            
            # ProfileExpResult 생성
            result_obj = ProfileExpResult(
                profile=updated_profile,
                level_increased=result_data.get("level_increased", False),
                exp_to_next_level=result_data.get("exp_to_next_level", 0),
                level_progress_percentage=result_data.get("level_progress_percentage", 0.0),
                implementation="rust_wasm",
                wasm_enabled=True,
                success=True
            )
            
            logger.info(f"WASM AddExpToProfile completed successfully. New level: {updated_profile.level}")
            return result_obj, None
            
        except Exception as e:
            error_msg = f"500: WASM function call failed: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    