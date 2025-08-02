# Hand in Hand 프로젝트 - 코딩 핵심 규칙

## 에러 핸들링 전략

### 예외(Exception) 사용 금지
모든 언어(Python, TypeScript, Go, C#)에서 예외 사용 절대 금지. 모든 함수는 Go 언어 스타일의 명시적 에러 핸들링 패턴을 사용.

### 함수 반환 규칙
- Python: `tuple[결과타입 | None, str | None]`
- TypeScript: `[결과타입 | null, string | null]`
- Go: `(결과타입, error)`
- C#: `(결과타입?, string?)`

### 에러 코드 체계
- HTTP 상태코드: 400, 401, 403, 404, 409, 500, 502, 503
- 도메인별 에러 코드: 0xAAA001 형식 (사용자: 0x001xxx, 인벤토리: 0x002xxx)

### 에러 전파 원칙
모든 에러는 반환값으로만 전파. try-catch 사용 금지.

## 의존성 역전 원칙

### 계층별 의존성 방향
1. API Layer → Application Layer만 의존
2. Application Layer → Domain Layer만 의존  
3. Domain Layer → 어떤 레이어에도 의존하지 않음
4. Infrastructure Layer → Domain 인터페이스 구현

### 의존성 주입 필수
모든 서비스는 생성자에서 의존성을 주입받아야 함. Infrastructure 계층의 구현체를 Domain 인터페이스로 추상화.

### UserAggregates 패턴 준수
단일 Redis 키로 전체 사용자 데이터 관리. IoC 기반 동시성 제어 사용. find_one_and_update, find_one_and_upsert 패턴 필수.

### WASM 의존성 주입
서버 시작 시 WASM 인스턴스 생성 후 서비스에 주입. WASM 로딩 실패 시 서버 시작 중단.

## 코딩 컨벤션

### Golang 스타일 네이밍 사용
모든 언어에서 함수명, 메서드명은 Golang 스타일 PascalCase 사용. AddExpToProfile, CalculateRequiredExp, GetUserAggregates 등.