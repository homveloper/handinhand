# Hand in Hand Python Server

JSON RPC 2.0 기반 게임 서버 - Python FastAPI 구현

## 🚀 빠른 시작

### 1. uv 설치 (권장)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 또는 pip으로
pip install uv
```

### 2. 서버 실행 (한 줄로!)

```bash
# 기본 설정으로 실행
./start.sh

# 커스텀 설정으로 실행  
./start.sh /path/to/config.json

# 또는 직접 uv run 사용
uv run python cmd/server.py --config ../shared/config/server-config.json
```

**uv의 장점:**
- ⚡ **초고속**: pip보다 10-100배 빠름
- 🔒 **자동 가상환경**: 별도 설정 불필요
- 📦 **자동 의존성**: 필요한 패키지 자동 설치
- 🎯 **간단함**: 복잡한 스크립트 불필요

### 3. 전통적인 방법 (pip)

```bash
# Python 가상환경 생성
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install fastapi redis uvicorn

# 서버 실행
python cmd/server.py --config ../shared/config/server-config.json
```

### 4. API 테스트

서버가 실행되면 다음 엔드포인트를 사용할 수 있습니다:

- **Root**: `GET http://localhost:3002/`
- **Health Check**: `GET http://localhost:3002/health`
- **JSON RPC**: `POST http://localhost:3002/api/jsonrpc`
- **📚 API 문서**: `GET http://localhost:3002/docs/jsonrpc` ⭐

**JSON RPC API 문서:**
- Swagger와 비슷한 인터랙티브 문서
- 모든 메서드, 파라미터, 응답 예시 포함
- 실시간 API 테스트 가능

#### JSON RPC 2.0 API 예시

**getUserAggregates 요청:**
```json
{
  "jsonrpc": "2.0",
  "method": "getUserAggregates",
  "params": {
    "userId": "user123"
  },
  "id": 1
}
```

**성공 응답:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "profile": {
      "nickname": "플레이어123",
      "level": 15,
      "exp": 2450,
      "avatar": "warrior_01",
      "created_at": "2024-01-01T00:00:00Z"
    },
    "inventory": {
      "items": [],
      "gold": 1500,
      "gems": 75,
      "capacity": 50
    }
  },
  "id": 1
}
```

**에러 응답:**
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": "0x001001",
    "message": "User not found"
  },
  "id": 1
}
```

## 📁 프로젝트 구조

```
python-server/
├── cmd/                    # 서버 애플리케이션 진입점
│   └── server.py          # FastAPI 서버 메인
├── src/                   # 소스 코드
│   ├── api/              # API 레이어
│   │   ├── controllers/  # JSON RPC 컨트롤러
│   │   └── jsonrpc_handler.py
│   ├── application/      # 서비스 레이어
│   │   └── user/
│   │       └── services/
│   ├── domain/           # 도메인 레이어
│   │   └── user/
│   │       ├── entities/ # 엔티티 (비즈니스 로직)
│   │       └── repositories/
│   └── config/           # 설정 관리
├── run.sh                # 실행 스크립트
└── README.md
```

## ⚙️ 설정 파일

서버는 `../shared/config/server-config.json` 파일에서 설정을 로드합니다.

**주요 설정 항목:**
- **servers.python**: Python 서버 설정 (포트, 호스트, 이름)
- **redis**: Redis 연결 정보
- **environment**: 실행 환경 (development/testing/production)
- **debug**: 디버그 모드 활성화 여부

## 🏗️ 아키텍처

### 4-Tier 아키텍처
1. **API Layer**: FastAPI + JSON RPC 2.0
2. **Application Layer**: 비즈니스 유스케이스
3. **Domain Layer**: 엔티티 및 비즈니스 로직
4. **Infrastructure Layer**: Redis Repository

### 에러 핸들링
- **튜플 방식**: `(결과, 에러)` 패턴 사용
- **HTTP 상태코드**: 시스템 에러 (400, 404, 500 등)
- **도메인 코드**: 비즈니스 에러 (0x001001 등)

### 데이터 모델
- **JSON Schema 기반**: 4개 언어 통합 데이터 표준
- **자동 생성**: `*_schema.py` (수정 금지)
- **비즈니스 로직**: `*.py` (자유 수정)

## 🛠️ 개발 가이드

### 새로운 JSON RPC 메서드 추가

1. **Controller에 핸들러 함수 추가**:
```python
# src/api/controllers/user_controller.py
async def new_method(self, params: Dict[str, Any]) -> tuple[Any | None, str | None]:
    # 구현
    pass
```

2. **JsonRpcHandler에 메서드 등록**:
```python
# src/api/jsonrpc_handler.py
self.methods = {
    "getUserAggregates": self.user_controller.get_user_aggregates,
    "newMethod": self.user_controller.new_method,  # 추가
}
```

### 데이터 모델 수정

1. JSON Schema 수정: `../shared/schemas/*.json`
2. 코드 재생성: `../scripts/generate-models.sh`
3. 비즈니스 로직 업데이트: `src/domain/user/entities/*.py`

## 🧪 테스트

```bash
# cURL로 API 테스트
curl -X POST http://localhost:3002/api/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "getUserAggregates",
    "params": {"userId": "test123"},
    "id": 1
  }'
```

## 📋 요구사항

- Python 3.7+
- Redis 서버
- FastAPI
- Redis Python 클라이언트
- Uvicorn

## 🔧 트러블슈팅

### uv 관련 문제
```bash
# uv 설치 확인
uv --version

# 캐시 정리
uv cache clean

# 의존성 재설치
uv sync --reinstall
```

### Redis 연결 실패
- Redis 서버가 실행 중인지 확인
- 설정 파일의 Redis 연결 정보 확인
- 방화벽 설정 확인

### 포트 충돌
- 설정 파일에서 다른 포트로 변경
- 기존 프로세스 종료: `lsof -ti:3002 | xargs kill`