"""
사용자 관련 JSON RPC 컨트롤러
실제 핸들러 함수 구현
"""

from typing import Dict, Any

from ...application.user.services.user_service import UserService


class UserController:
    """사용자 관련 JSON RPC 핸들러"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    async def get_user_aggregates(self, params: Dict[str, Any]) -> tuple[Dict[str, Any] | None, str | None]:
        """
        getUserAggregates 메서드 처리
        
        Args:
            params: RPC 파라미터 {"userId": "user123"}
            
        Returns:
            tuple[Dict[str, Any] | None, str | None]: (결과, 에러)
        """
        user_id = params.get("userId")
        
        if not user_id:
            return None, "400: userId parameter is required"
        
        # 서비스 호출
        user_aggregates, error = await self.user_service.get_user_aggregates(user_id)
        
        if error:
            return None, error
        
        if not user_aggregates:
            return None, "0x001001: User not found"
        
        # UserAggregates를 딕셔너리로 변환
        result = user_aggregates.to_dict()
        
        return result, None