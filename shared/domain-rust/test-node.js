// Node.js에서 Rust WASM 모듈 테스트

import { readFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function loadRustWasm() {
    try {
        // WASM 파일 경로
        const wasmPath = join(__dirname, 'pkg', 'domain_rust_bg.wasm');
        
        // WASM 파일 읽기
        const wasmBuffer = await readFile(wasmPath);
        
        // WASM 모듈 컴파일 및 인스턴스화
        const wasmModule = await WebAssembly.compile(wasmBuffer);
        const wasmInstance = await WebAssembly.instantiate(wasmModule, {
            './domain_rust_bg.js': {
                __wbg_log_1ab7ce1e14dbcdf5: (ptr, len) => {
                    // console.log 구현
                    const memory = wasmInstance.exports.memory;
                    const buffer = new Uint8Array(memory.buffer, ptr, len);
                    const text = new TextDecoder().decode(buffer);
                    console.log(text);
                }
            }
        });
        
        return wasmInstance.exports;
    } catch (error) {
        console.error('❌ Error loading WASM:', error);
        throw error;
    }
}

async function testRustCalculator() {
    try {
        console.log('🦀 Loading Rust WASM module...');
        const rustWasm = await loadRustWasm();
        
        console.log('✅ Rust WASM module loaded successfully!');
        console.log('Available functions:', Object.keys(rustWasm).filter(key => typeof rustWasm[key] === 'function'));
        
        // 메모리 초기화
        if (rustWasm.__wbg_init) {
            rustWasm.__wbg_init();
        }
        
        console.log('\n📊 Testing Rust calculator functions:');
        
        // Add 테스트
        const result1 = rustWasm.add(10, 20);
        console.log(`add(10, 20) = ${result1}`);
        
        const result2 = rustWasm.add(5.5, 4.5);
        console.log(`add(5.5, 4.5) = ${result2}`);
        
        const result3 = rustWasm.add(-1, 1);
        console.log(`add(-1, 1) = ${result3}`);
        
        console.log('\n✅ All Rust WASM tests completed!');
        
    } catch (error) {
        console.error('❌ Error:', error);
    }
}

// 실행
testRustCalculator();