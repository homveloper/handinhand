from abc import ABC, abstractmethod
from typing import Optional, Callable
from dataclasses import dataclass

from ..entities import UserAggregates


@dataclass
class UserRepositoryResult:
    """Repository 작업 결과"""
    data: UserAggregates
    version: int
    created: Optional[bool] = None


@dataclass
class UserRepositoryOptions:
    """Repository 작업 옵션"""
    retries: int = 3


class UserRepository(ABC):
    """
    UserAggregates 저장소 인터페이스
    아키텍처 문서의 IoC 패턴 구현
    """

    @abstractmethod
    async def find_one(self, user_id: str) -> tuple[UserRepositoryResult | None, str | None]:
        """
        사용자 데이터 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            tuple[UserRepositoryResult | None, str | None]: (결과, 에러)
        """
        pass

    @abstractmethod
    async def find_one_and_upsert(
        self,
        user_id: str,
        create_fn: Callable[[str], UserAggregates],
        update_fn: Callable[[UserAggregates, str], UserAggregates],
        options: Optional[UserRepositoryOptions] = None
    ) -> tuple[UserRepositoryResult | None, str | None]:
        """
        사용자 데이터 생성 또는 업데이트 (IoC 패턴)
        
        Args:
            user_id: 사용자 ID
            create_fn: 새 사용자 생성 함수: (user_id) -> UserAggregates
            update_fn: 기존 사용자 업데이트 함수: (current_aggregates, user_id) -> UserAggregates
            options: 추가 옵션 (재시도 횟수 등)
            
        Returns:
            tuple[UserRepositoryResult | None, str | None]: (결과, 에러)
        """
        pass

    @abstractmethod
    async def find_one_and_update(
        self,
        user_id: str,
        update_fn: Callable[[UserAggregates, str], UserAggregates],
        options: Optional[UserRepositoryOptions] = None
    ) -> tuple[UserRepositoryResult | None, str | None]:
        """
        기존 사용자 데이터만 업데이트 (IoC 패턴)
        
        Args:
            user_id: 사용자 ID
            update_fn: 업데이트 함수: (current_aggregates, user_id) -> UserAggregates
            options: 추가 옵션 (재시도 횟수 등)
            
        Returns:
            tuple[UserRepositoryResult | None, str | None]: (결과, 에러)
        """
        pass

    @abstractmethod
    async def upsert_one(
        self,
        user_id: str,
        aggregates: UserAggregates,
        options: Optional[UserRepositoryOptions] = None
    ) -> tuple[UserRepositoryResult | None, str | None]:
        """
        사용자 데이터 직접 생성/업데이트 (UserAggregates 객체 전달)
        
        Args:
            user_id: 사용자 ID
            aggregates: 저장할 데이터
            options: 추가 옵션 (재시도 횟수 등)
            
        Returns:
            tuple[UserRepositoryResult | None, str | None]: (결과, 에러)
        """
        pass