#!/bin/bash

# WASI용 Rust WASM 빌드 스크립트
# wasmtime 호환 WASM 모듈 생성

set -e

echo "🦀 Building Rust WASM for WASI (wasmtime compatible)"

# Rust 환경 설정
export PATH="$HOME/.cargo/bin:$PATH"

# 프로젝트 루트 디렉토리
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# WASI 타겟 확인 (rustup이 있다면)
if command -v rustup &> /dev/null; then
    echo "📦 Adding wasm32-wasip1 target..."
    rustup target add wasm32-wasip1
else
    echo "ℹ️  rustup not found, assuming wasm32-wasip1 target is available"
fi

# 출력 디렉토리 생성
OUTPUT_DIR="pkg-wasmtime"
mkdir -p "$OUTPUT_DIR"

echo "🔨 Building with cargo..."

# WASI 타겟으로 릴리즈 빌드 (module 생성)
cargo build --target wasm32-wasip1 --release

# 빌드된 WASM 파일을 출력 디렉토리로 복사
WASM_SOURCE="target/wasm32-wasip1/release/domain_rust.wasm"
WASM_DEST="$OUTPUT_DIR/domain_rust.wasm"

if [ -f "$WASM_SOURCE" ]; then
    cp "$WASM_SOURCE" "$WASM_DEST"
    echo "✅ WASM file copied to: $WASM_DEST"
    
    # 파일 크기 확인
    WASM_SIZE=$(wc -c < "$WASM_DEST")
    echo "📊 WASM file size: $WASM_SIZE bytes"
    
    # wasmtime으로 유효성 검사 (설치되어 있다면)
    if command -v wasmtime &> /dev/null; then
        echo "🔍 Validating WASM with wasmtime..."
        wasmtime compile "$WASM_DEST" > /dev/null 2>&1 && echo "✅ WASM validation passed" || echo "⚠️  WASM validation failed"
    else
        echo "ℹ️  wasmtime not found, skipping validation"
    fi
    
else
    echo "❌ Build failed: $WASM_SOURCE not found"
    exit 1
fi

echo ""
echo "🎉 Build completed successfully!"
echo "📁 Output: $WASM_DEST"
echo "🚀 Ready to use with wasmtime Python bindings"