#!/bin/bash

# Go WASM 빌드 스크립트 (wasmexport 사용)

echo "Building Go WASM domain module with wasmexport..."

# WASI Preview 1 타겟으로 빌드 (모든 .go 파일 포함)
GOOS=wasip1 GOARCH=wasm go build -o calculator.wasm .

if [ $? -eq 0 ]; then
    echo "✅ WASM build successful!"
    
    # 파일 크기 확인
    ls -lh calculator.wasm
    
    # export된 함수들 확인 (wasm-objdump가 있다면)
    if command -v wasm-objdump &> /dev/null; then
        echo ""
        echo "📋 Exported functions:"
        wasm-objdump -x calculator.wasm | grep "Export" -A 20
    fi
    
    echo ""
    echo "📦 Build complete! File created:"
    echo "  - calculator.wasm"
    echo ""
    echo "Note: This uses WASI Preview 1, not the old js/wasm target"
else
    echo "❌ Build failed!"
    exit 1
fi