"""
사용자 애플리케이션 서비스
비즈니스 유스케이스 조합 및 흐름 제어
"""

from typing import Optional

from src.domain.user.repositories.user_repository import UserRepository
from src.domain.user.entities import UserAggregates


class UserService:
    """사용자 관련 애플리케이션 서비스"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def get_user_aggregates(self, user_id: str) -> tuple[UserAggregates | None, str | None]:
        """
        사용자 전체 데이터 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            tuple[UserAggregates | None, str | None]: (사용자 데이터, 에러)
        """
        # 입력 검증
        if not user_id or not user_id.strip():
            return None, "400: user_id is required"
        
        # Repository 호출
        result, error = await self.user_repository.find_one(user_id.strip())
        
        if error:
            # Repository 에러를 그대로 전파
            return None, error
        
        if not result or not result.data:
            # 사용자를 찾을 수 없음
            return None, "0x001001: User not found"
        
        return result.data, None
    
    async def create_new_user(self, user_id: str, nickname: str) -> tuple[UserAggregates | None, str | None]:
        """
        새 사용자 생성
        
        Args:
            user_id: 사용자 ID
            nickname: 닉네임
            
        Returns:
            tuple[UserAggregates | None, str | None]: (생성된 사용자 데이터, 에러)
        """
        # 입력 검증
        if not user_id or not user_id.strip():
            return None, "400: user_id is required"
        
        if not nickname or not nickname.strip():
            return None, "400: nickname is required"
        
        if len(nickname.strip()) < 1 or len(nickname.strip()) > 50:
            return None, "400: nickname must be between 1 and 50 characters"
        
        # 새 사용자 생성
        new_user = UserAggregates.create_new_user(user_id.strip(), nickname.strip())
        
        # Repository에 저장
        result, error = await self.user_repository.upsert_one(user_id.strip(), new_user)
        
        if error:
            return None, error
        
        if not result or not result.data:
            return None, "500: Failed to create user"
        
        return result.data, None