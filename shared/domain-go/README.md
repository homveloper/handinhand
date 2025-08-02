# Go WASM Domain Module

Go로 작성된 공통 도메인 로직을 WebAssembly로 컴파일하여 모든 언어에서 사용할 수 있도록 합니다.

## 빌드 방법

```bash
# 일반 Go 테스트 실행
go test -v

# 벤치마크 테스트 실행
go test -bench=.

# WASM 빌드
./build.sh
```

## 생성되는 파일

- `calculator.wasm` - WebAssembly 바이너리
- `wasm_exec.js` - Go WASM 런타임 지원 파일

## 사용 가능한 함수

- `add(a, b)` - 두 숫자의 합
- `multiply(a, b)` - 두 숫자의 곱
- `calculateTax(amount, taxRate)` - 세금 계산