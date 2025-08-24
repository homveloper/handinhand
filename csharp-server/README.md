# 🚀 Functional C# Game Server

**차세대 함수형 프로그래밍 + IoC 패턴 기반 게임 서버**

## 🎯 주요 특징

### **🔥 혁신적인 아키텍처**
- **완전 함수형**: 모든 비즈니스 로직이 순수 함수
- **IoC 패턴**: 비즈니스 로직을 함수로 주입
- **서비스 계층 제거**: 불필요한 추상화 완전 삭제
- **Go 스타일 에러 처리**: `WrapRecover(func()) -> (result, error)`

### **⚡ 핵심 기술 스택**
- **REST API + JSON-RPC 2.0**: REST URL + JSON-RPC 요청 바디 하이브리드 방식
- **ASP.NET Core 8.0**: 최신 웹 프레임워크
- **Redis**: 영속성 + 낙관적 동시성 제어
- **Swagger UI**: 완전 자동화된 API 문서
- **Serilog**: 구조화된 로깅
- **함수형 DI**: 클래스 대신 함수를 의존성 주입

## 🏗️ 프로젝트 구조

```
csharp-server/
├── Program.cs                    # 함수형 DI 설정
├── GlobalUsings.cs               # Go 스타일 global import
├── csharp-server.csproj          # .NET 8.0 프로젝트
└── src/
    ├── Domain/                   # 🧠 순수 도메인 함수들
    │   ├── User.cs               # 사용자 비즈니스 로직
    │   ├── Character.cs          # 캐릭터 비즈니스 로직
    │   └── Inventory.cs          # 인벤토리 비즈니스 로직
    ├── Infrastructure/           # 🗄️ 영속성 함수들
    │   └── Persistence.cs        # FindOneAndUpsert, Redis 구현
    ├── Utils/                    # 🛠️ 유틸리티 함수들
    │   └── ErrorHandling.cs      # WrapRecover (Go 스타일)
    └── Api/                      # 🌐 API 계층
        ├── Controllers/          # 함수형 + IoC 컨트롤러들
        │   ├── UserController.cs
        │   ├── InventoryController.cs
        │   └── SystemController.cs
        ├── Middleware/           # 전역 예외 처리
        │   └── GlobalExceptionHandlingMiddleware.cs
        └── Models/               # JSON-RPC 모델들
            └── JsonRpcModels.cs
```

## 🚀 빠른 시작

### 1. 의존성 설치
```bash
cd csharp-server

# NuGet 패키지 복원 및 빌드
dotnet restore
dotnet build
```

### 2. Redis 서버 시작
```bash
# Docker로 Redis 실행
docker run -d -p 6379:6379 redis:7-alpine
```

### 3. 서버 실행
```bash
# 개발 모드로 실행
dotnet run

# 또는 특정 환경으로 실행
dotnet run --environment Development
```

서버는 **http://localhost:3004** 에서 실행됩니다.

## 🌟 Swagger UI 접속

서버 실행 후 브라우저에서 접속하여 모든 API를 테스트할 수 있습니다:

- **Swagger UI**: `http://localhost:3004/swagger` 🎯
- **메인 페이지**: `http://localhost:3004/` (자동 리다이렉트)
- **API 스펙**: `http://localhost:3004/swagger/v1/swagger.json`

## 📡 API 사용 방식

**REST + JSON-RPC 2.0 하이브리드 구조:**

```
URL은 직관적 (REST 스타일)     ➜  POST /api/character/addExp
Body는 구조적 (JSON-RPC 형식)   ➜  {"jsonrpc":"2.0","params":{...},"id":1}
```

- URL로 **어떤 기능**인지 명확하게 알 수 있고
- Body로 **구조화된 데이터**를 안전하게 전달합니다

## 🏛️ 함수형 아키텍처의 특징

### **1. 서비스 계층 제거**
기존의 `UserService`, `InventoryService` 클래스들을 모두 제거하고, 
**도메인 함수 + 영속성 함수**를 컨트롤러에서 직접 조합합니다.

### **2. IoC 패턴으로 비즈니스 로직 주입**
영속성 함수에 비즈니스 로직을 함수로 주입합니다.

### **3. Go 스타일 에러 처리**
Go 언어와 유사한 패턴으로 에러를 처리합니다.

### **4. 순수 도메인 함수**
모든 비즈니스 로직이 순수 함수로 구현되어 사이드 이펙트가 없습니다.

## ⚙️ 설정

### **Redis 연결 설정**
`../shared/config/server-config.json`:
```json
{
  "redis": {
    "host": "localhost",
    "port": 6379,
    "db": 0
  },
  "servers": {
    "csharp": {
      "host": "localhost",
      "port": 3004,
      "name": "C# Functional Server"
    }
  }
}
```

## 🔧 고급 기능

### **1. 낙관적 동시성 제어**
Redis 기반 버전 체크로 동시 업데이트 충돌을 방지합니다.

### **2. 전역 예외 처리**
Go의 `panic/recover`와 동일한 패턴으로 모든 예외를 안전하게 처리합니다.

### **3. 함수 조합 (Decorators)**
기본 영속성 함수에 재시도, 로깅, 캐싱 등의 기능을 데코레이터 패턴으로 추가할 수 있습니다.

## 🤔 왜 이 아키텍처인가?

### **기존 문제점**
- ❌ 서비스 계층의 불필요한 복잡성
- ❌ 클래스 기반 의존성 주입의 경직성  
- ❌ 테스트하기 어려운 사이드 이펙트
- ❌ 비즈니스 로직과 인프라 로직의 혼재

### **함수형 아키텍처의 장점**
- ✅ **극단적 단순성**: 3개 계층만 존재
- ✅ **완벽한 테스트 가능성**: 모든 로직이 순수 함수
- ✅ **높은 재사용성**: 함수들을 자유자재로 조합
- ✅ **Go와 유사한 개발 경험**: 친숙하고 직관적
- ✅ **타입 안전성**: C#의 강타입 시스템 완전 활용

## 🚀 성능 및 확장성

- **비동기 처리**: .NET의 async/await 완전 활용
- **Redis 영속성**: 고성능 인메모리 데이터베이스
- **낙관적 동시성**: 높은 동시 접속 처리
- **구조화 로깅**: Serilog로 상세 모니터링
- **함수 조합**: 런타임에 기능 확장 가능

## 🤝 다른 서버와의 호환성

이 C# 함수형 서버는 다음 서버들과 완전히 호환됩니다:

- **Node.js** (포트 3001) - Express + TypeScript
- **Python** (포트 3002) - FastAPI  
- **Go** (포트 3003) - Gin

모든 서버는 동일한 JSON-RPC 2.0 API와 Redis 데이터 형식을 공유합니다.

## 📚 학습 리소스

### **C# 함수형 프로그래밍**
- [Microsoft - Functional Programming](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/functional-programming/)
- [F# for Fun and Profit](https://fsharpforfunandprofit.com/)

### **사용된 기술**
- [ASP.NET Core 8.0](https://docs.microsoft.com/en-us/aspnet/core/)
- [StackExchange.Redis](https://stackexchange.github.io/StackExchange.Redis/)
- [Serilog](https://serilog.net/)
- [Swashbuckle.AspNetCore](https://github.com/domaindrivendev/Swashbuckle.AspNetCore)

---

## 💡 결론

**이 프로젝트는 전통적인 C# 웹 개발의 패러다임을 완전히 바꾼 혁신적인 아키텍처입니다.**

- **함수형 프로그래밍의 순수성**
- **Go 언어의 단순함과 직관성**  
- **C#의 타입 안전성과 성능**
- **현대적인 웹 API의 편의성**

**모든 것을 하나로 통합한 차세대 게임 서버 아키텍처입니다!** 🎉

---
*Made with ❤️ by Functional Programming Enthusiasts*