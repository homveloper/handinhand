# 2025-08-02 개발 일지: WASM 기반 다중 언어 도메인 로직 통합 실험

**프로젝트**: Hand in Hand 게임 서버  
**날짜**: 2025년 8월 2일  
**작업자**: 사용자 + Claude Code  
**목표**: 4개 언어(Python, Go, Rust, TypeScript)에서 동일한 비즈니스 로직 공유  

---

## 📋 작업 개요

### 초기 목표
- Rust로 작성한 도메인 로직을 WASM으로 컴파일
- Python, Go, C#, Node.js에서 동일한 WASM 모듈 사용
- `AddExpToProfile` 같은 게임 비즈니스 로직 통합

### 최종 결과
**부분적 성공**: WASM 빌드 및 로딩 완료, 하지만 문자열 처리 복잡성으로 인한 실용성 한계 확인

---

## 🛠️ 기술적 구현 과정

### 1단계: Rust WASM 도메인 로직 구현 ✅
```rust
// shared/domain-rust/src/lib.rs
#[no_mangle]
pub extern "C" fn add_exp_to_profile_json(profile_json_ptr: *const c_char, exp_to_add: u32) -> *mut c_char {
    // ProfileEntity 경험치 추가 로직
    // JSON 직렬화/역직렬화 처리
    // 레벨업 계산 (100 * (level-1)^1.5 공식)
}
```

**성과:**
- 게임 비즈니스 로직을 Rust로 성공적으로 구현
- C FFI 스타일 인터페이스 설계
- wasm32-wasip1 타겟으로 순수 WASI 빌드 완료

### 2단계: Python-WASM 통합 🟡
```python
# python-server/src/application/user/services/user_domain_service.py
from wasmtime import Store, Module, Instance, Linker

class UserDomainService:
    def __init__(self, wasm_instance: Instance):
        self.wasm_instance = wasm_instance
    
    async def AddExpToProfile(self, profile: ProfileEntity, exp_to_add: int):
        # WASM 함수 호출 로직
```

**도전 과제:**
- ✅ wasmtime 라이브러리 통합 완료
- ✅ 의존성 주입 아키텍처 구현
- ⚠️ 문자열 포인터 전달의 복잡성
- ⚠️ JSON 직렬화/역직렬화 오버헤드

### 3단계: 기술적 장애물 🔴

#### 문제 1: WASM 함수명 불일치
```bash
# 오류: AddExpToProfileJson function not found in WASM exports
# 해결: add_exp_to_profile_json으로 함수명 통일
```

#### 문제 2: datetime JSON 직렬화
```python
# 오류: Object of type datetime is not JSON serializable
# 해결: profile.created_at.isoformat() 변환 추가
```

#### 문제 3: WASM 문자열 포인터 처리
```bash
# 오류: don't know how to convert 'JSON_STRING' to i32
# 시도: wasmtime 메모리 직접 조작, ctypes 포인터 연산
# 결과: 복잡성 증가, 실용성 저하
```

---

## 📊 성과 및 한계점

### ✅ 성공한 부분
1. **WASM 빌드 시스템 구축**
   - wasm32-wasip1 타겟 성공적 빌드
   - 137KB 크기의 최적화된 WASM 모듈 생성

2. **Python 서버 통합**
   - wasmtime 런타임 성공적 통합
   - 의존성 주입 기반 아키텍처 완성
   - OpenRPC API 스펙 업데이트

3. **프로젝트 구조 확장**
   - 4개 언어 서버 디렉토리 준비
   - 중앙화된 도메인 로직 관리 구조

### ❌ 한계점 및 문제점
1. **WASM 문자열 처리 복잡성**
   - C 스타일 포인터 조작 필요
   - 메모리 관리 오버헤드
   - 디버깅 어려움

2. **개발 생산성 저하**
   - 단순한 비즈니스 로직도 복잡한 FFI 처리
   - JSON 직렬화 오버헤드
   - 타입 안전성 부족

3. **기술 성숙도 부족**
   - WASM-호스트 언어 간 문자열 처리 표준 부재
   - wasmtime 생태계의 제한적 문서화

---

## 🔍 대안 기술 분석

### 1. JSON Logic ⭐⭐⭐⭐⭐
```json
{
  "calculate_required_exp": {
    "if": [
      {"<=": [{"var": "target_level"}, 1]},
      0,
      {"*": [100, {"^": [{"-": [{"var": "target_level"}, 1]}, 1.5]}]}
    ]
  }
}
```
**장점**: 성숙한 생태계, 간단한 구현, 모든 언어 지원  
**적용성**: 계산 공식, 조건부 로직에 최적

### 2. Schema-Driven Code Generation ⭐⭐⭐⭐
```typescript
// TypeScript 마스터 소스 → Python/Go/Rust 변환
export class ProfileService {
  static addExpToProfile(profile: ProfileEntity, expToAdd: number): ProfileExpResult {
    // 비즈니스 로직
  }
}
```
**장점**: 타입 안전성, 컴파일 타임 검증  
**적용성**: 복잡한 도메인 로직에 적합

### 3. 트랜스컴파일러 ⭐⭐⭐⭐
- **TypeScript → Python** (py-ts)
- **TypeScript → Go** (gots)
- **Kotlin Multiplatform**

---

## 🎯 결론 및 향후 방향

### 핵심 학습
1. **WASM은 아직 도메인 로직 공유에는 성숙하지 않음**
   - 숫자 계산: 적합 ✅
   - 문자열/구조체 처리: 부적합 ❌

2. **실용적 대안 존재**
   - JSON Logic: 비즈니스 규칙
   - Code Generation: 복잡한 로직
   - 트랜스컴파일러: 타입 안전성

### 다음 단계 계획
```
Phase 1: JSON Logic 도입 (1-2일)
├── shared/domain-json-logic/ 폴더 생성
├── 계산 공식을 JSON Logic으로 정의
└── 각 언어별 JSON Logic 인터프리터 통합

Phase 2: 하이브리드 접근 (3-5일)
├── 단순 규칙: JSON Logic
├── 복잡 로직: 언어별 구현
└── 공통 테스트 케이스로 일관성 보장
```

---

## 📈 프로젝트 영향

### 긍정적 영향
- **아키텍처 개선**: 의존성 주입, 모듈화 설계 완성
- **기술 스택 확장**: WASM, wasmtime 경험 획득
- **다중 언어 준비**: 4개 언어 프로젝트 구조 완성

### 기술 부채
- **WASM 코드 정리 필요**: 사용하지 않는 WASM 관련 코드 제거
- **API 단순화**: AddExpToProfile 인터페이스 최적화
- **문서화**: 새로운 아키텍처 문서 업데이트

---

## 🔧 기술 스택 변화

### 추가된 기술
- **Rust**: 도메인 로직 구현 언어
- **wasmtime**: WASM 런타임
- **WASI**: WebAssembly System Interface

### 라이브러리 변경
```toml
# pyproject.toml
[dependencies]
+ wasmtime = "20.0.0"
+ wasmer = "1.1.0"  # 최종적으로 미사용
```

---

## 📚 교훈 및 베스트 프랙티스

### 1. 기술 선택 시 고려사항
- **성숙도**: 프로덕션 준비 상태 확인
- **생태계**: 문서, 커뮤니티, 도구 지원
- **복잡성**: 구현 및 유지보수 비용

### 2. 실험적 기술 도입 방법
- **단계적 접근**: 작은 기능부터 시작
- **대안 준비**: 복수의 솔루션 사전 조사
- **롤백 계획**: 실패 시 복구 방안 마련

### 3. 다중 언어 프로젝트 관리
- **공통 스키마**: 데이터 일관성 보장
- **공통 테스트**: 동작 일관성 검증
- **중앙화된 문서**: 아키텍처 명세 통합

---

**총 작업 시간**: 약 6시간  
**커밋 해시**: `dca7969`  
**다음 작업**: JSON Logic 기반 비즈니스 규칙 공유 시스템 구현

---

*이 문서는 실험적 기술 도입 과정의 솔직한 기록입니다. 실패한 부분도 포함하여 향후 기술 선택에 참고하기 위해 작성되었습니다.*