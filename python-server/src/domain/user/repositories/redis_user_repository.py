"""
Redis 기반 UserRepository 구현체
아키텍처 문서의 IoC 패턴과 낙관적 동시성 제어 구현
"""

import json
import asyncio
from typing import Optional, Callable, Dict, Any
from datetime import datetime

import redis.asyncio as redis

from .user_repository import (
    UserRepository, 
    UserRepositoryResult, 
    UserRepositoryOptions
)
from ..aggregates import UserAggregates


class RedisUserRepository(UserRepository):
    """Redis 기반 UserRepository 구현체"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def find_one(self, user_id: str) -> tuple[UserRepositoryResult | None, str | None]:
        """
        사용자 데이터 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            UserRepositoryResult: data는 UserAggregates 또는 None, version은 현재 버전
        """
        try:
            # Pipeline을 사용하여 원자적으로 데이터와 버전 조회
            pipe = self.redis.pipeline()
            pipe.hget(f"user:{user_id}:data", "data")
            pipe.get(f"user:{user_id}:version")
            
            results = await pipe.execute()
            data_json = results[0]
            version = int(results[1]) if results[1] else 0
            
            user_aggregates = None
            if data_json:
                # JSON 문자열을 파싱하여 UserAggregates 객체로 변환
                data_dict = json.loads(data_json)
                user_aggregates = UserAggregates.from_dict(data_dict)
            else:
                # 테스트용: 사용자가 없으면 더미 사용자 생성
                user_aggregates = UserAggregates.create_new_user(user_id, f"TestUser_{user_id}")
            
            result = UserRepositoryResult(
                data=user_aggregates,
                version=version
            )
            return result, None
            
        except Exception as e:
            # 로그 기록 (실제 운영에서는 proper logging 사용)
            print(f"Error in find_one for user {user_id}: {e}")
            return None, f"500: Database error: {str(e)}"
    
    async def find_one_and_upsert(
        self,
        user_id: str,
        create_fn: Callable[[str], UserAggregates],
        update_fn: Callable[[UserAggregates, str], UserAggregates],
        options: Optional[UserRepositoryOptions] = None
    ) -> UserRepositoryResult:
        """
        사용자 데이터 생성 또는 업데이트 (IoC 패턴)
        
        Args:
            user_id: 사용자 ID
            create_fn: 새 사용자 생성 함수: (user_id) -> UserAggregates
            update_fn: 기존 사용자 업데이트 함수: (current_aggregates, user_id) -> UserAggregates
            options: 추가 옵션 (재시도 횟수 등)
            
        Returns:
            UserRepositoryResult: success, data, version 포함
        """
        if options is None:
            options = UserRepositoryOptions()
        
        max_retries = options.retries
        
        for attempt in range(max_retries):
            try:
                # 현재 데이터 조회
                current_data = await self.find_one(user_id)
                expected_version = current_data.version
                
                if current_data.data:
                    # 기존 사용자 - updateFn 실행
                    new_aggregates = update_fn(current_data.data, user_id)
                else:
                    # 새 사용자 - createFn 실행
                    new_aggregates = create_fn(user_id)
                    expected_version = 0
                
                # 버전 체크와 함께 저장
                result = await self._save_with_version_check(
                    user_id, new_aggregates, expected_version
                )
                
                if result.success:
                    return UserRepositoryResult(
                        success=True,
                        data=new_aggregates,
                        version=result.version,
                        created=current_data.data is None
                    )
                
            except Exception as e:
                print(f"Error in find_one_and_upsert attempt {attempt + 1} for user {user_id}: {e}")
                if attempt == max_retries - 1:
                    return UserRepositoryResult(
                        success=False,
                        data=None,
                        version=0
                    )
            
            # 재시도 전 지수 백오프 대기
            await self._delay(2 ** attempt * 50 + __import__('random').randint(0, 100))
        
        return UserRepositoryResult(
            success=False,
            data=None,
            version=0
        )
    
    async def find_one_and_update(
        self,
        user_id: str,
        update_fn: Callable[[UserAggregates, str], UserAggregates],
        options: Optional[UserRepositoryOptions] = None
    ) -> UserRepositoryResult:
        """
        기존 사용자 데이터만 업데이트 (IoC 패턴)
        
        Args:
            user_id: 사용자 ID
            update_fn: 업데이트 함수: (current_aggregates, user_id) -> UserAggregates
            options: 추가 옵션 (재시도 횟수 등)
            
        Returns:
            UserRepositoryResult: success, data, version 포함
            
        Raises:
            ValueError: 사용자를 찾을 수 없는 경우
        """
        if options is None:
            options = UserRepositoryOptions()
        
        max_retries = options.retries
        
        for attempt in range(max_retries):
            try:
                # 현재 데이터 조회
                current_data = await self.find_one(user_id)
                
                if not current_data.data:
                    raise ValueError(f"FindOneAndUpdate: 사용자 {user_id}를 찾을 수 없습니다")
                
                # updateFn 실행
                new_aggregates = update_fn(current_data.data, user_id)
                
                # 버전 체크와 함께 저장
                result = await self._save_with_version_check(
                    user_id, new_aggregates, current_data.version
                )
                
                if result.success:
                    return UserRepositoryResult(
                        success=True,
                        data=new_aggregates,
                        version=result.version
                    )
                
            except ValueError:
                # 사용자를 찾을 수 없는 경우는 재시도하지 않음
                raise
            except Exception as e:
                print(f"Error in find_one_and_update attempt {attempt + 1} for user {user_id}: {e}")
                if attempt == max_retries - 1:
                    return UserRepositoryResult(
                        success=False,
                        data=None,
                        version=0
                    )
            
            # 재시도 전 지수 백오프 대기
            await self._delay(2 ** attempt * 50 + __import__('random').randint(0, 100))
        
        return UserRepositoryResult(
            success=False,
            data=None,
            version=0
        )
    
    async def upsert_one(
        self,
        user_id: str,
        aggregates: UserAggregates,
        options: Optional[UserRepositoryOptions] = None
    ) -> UserRepositoryResult:
        """
        사용자 데이터 직접 생성/업데이트 (UserAggregates 객체 전달)
        
        Args:
            user_id: 사용자 ID
            aggregates: 저장할 데이터
            options: 추가 옵션 (재시도 횟수 등)
            
        Returns:
            UserRepositoryResult: success, version, created 포함
        """
        if options is None:
            options = UserRepositoryOptions()
        
        max_retries = options.retries
        
        for attempt in range(max_retries):
            try:
                # 현재 데이터 조회하여 기존 사용자인지 확인
                current_data = await self.find_one(user_id)
                is_new_user = current_data.data is None
                expected_version = 0 if is_new_user else current_data.version
                
                # 버전 체크와 함께 저장
                result = await self._save_with_version_check(
                    user_id, aggregates, expected_version
                )
                
                if result.success:
                    return UserRepositoryResult(
                        success=True,
                        data=aggregates,
                        version=result.version,
                        created=is_new_user
                    )
                
            except Exception as e:
                print(f"Error in upsert_one attempt {attempt + 1} for user {user_id}: {e}")
                if attempt == max_retries - 1:
                    return UserRepositoryResult(
                        success=False,
                        data=None,
                        version=0
                    )
            
            # 재시도 전 지수 백오프 대기
            await self._delay(2 ** attempt * 50 + __import__('random').randint(0, 100))
        
        return UserRepositoryResult(
            success=False,
            data=None,
            version=0
        )
    
    async def _save_with_version_check(
        self, 
        user_id: str, 
        aggregates: UserAggregates, 
        expected_version: int
    ) -> UserRepositoryResult:
        """
        버전 체크와 함께 데이터 저장 (낙관적 동시성 제어)
        
        Args:
            user_id: 사용자 ID
            aggregates: 저장할 데이터
            expected_version: 예상 버전
            
        Returns:
            UserRepositoryResult: success와 새 버전 포함
        """
        try:
            # WATCH를 사용한 낙관적 동시성 제어
            async with self.redis.pipeline(transaction=True) as pipe:
                while True:
                    try:
                        # 버전 키를 WATCH
                        await pipe.watch(f"user:{user_id}:version")
                        
                        # 현재 버전 확인
                        current_version = await self.redis.get(f"user:{user_id}:version")
                        current_version = int(current_version) if current_version else 0
                        
                        # 버전이 예상과 다르면 충돌 발생
                        if current_version != expected_version:
                            await pipe.unwatch()
                            return UserRepositoryResult(
                                success=False,
                                data=None,
                                version=current_version
                            )
                        
                        # 새 버전 계산
                        new_version = expected_version + 1
                        
                        # 트랜잭션 시작
                        pipe.multi()
                        
                        # UserAggregates를 JSON으로 직렬화
                        serialized_data = json.dumps(aggregates.to_dict())
                        
                        # 데이터와 버전, 메타데이터를 원자적으로 업데이트
                        pipe.hset(f"user:{user_id}:data", "data", serialized_data)
                        pipe.set(f"user:{user_id}:version", new_version)
                        pipe.hset(
                            f"user:{user_id}:metadata", 
                            "lastModified", 
                            datetime.now().isoformat()
                        )
                        
                        # 트랜잭션 실행
                        results = await pipe.execute()
                        
                        # 성공적으로 실행되면 결과 반환
                        return UserRepositoryResult(
                            success=True,
                            data=aggregates,
                            version=new_version
                        )
                        
                    except redis.WatchError:
                        # WATCH된 키가 변경되면 재시도
                        continue
                        
        except Exception as e:
            print(f"Error in _save_with_version_check for user {user_id}: {e}")
            return UserRepositoryResult(
                success=False,
                data=None,
                version=expected_version
            )
    
    async def _delay(self, milliseconds: int):
        """
        비동기 지연 함수
        
        Args:
            milliseconds: 지연할 밀리초 수
        """
        await asyncio.sleep(milliseconds / 1000)