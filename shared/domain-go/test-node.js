// Node.js에서 Go wasmexport 함수 사용하기
// Node.js 20+ 필요 (WASI 지원)

const { readFile } = require('fs/promises');
const { WASI } = require('wasi');
const { argv, env } = require('process');

async function loadWasmModule() {
    // WASI 인스턴스 생성
    const wasi = new WASI({
        args: argv,
        env,
        preopens: {
            '/': '/'
        }
    });

    // WASM 파일 읽기
    const wasm = await readFile('./calculator.wasm');
    
    // WASM 모듈 컴파일
    const module = await WebAssembly.compile(wasm);
    
    // WASM 인스턴스 생성
    const instance = await WebAssembly.instantiate(module, {
        wasi_snapshot_preview1: wasi.wasiImport
    });
    
    // WASI 초기화
    wasi.start(instance);
    
    return instance.exports;
}

async function testCalculator() {
    try {
        console.log('Loading WASM module...');
        const calculator = await loadWasmModule();
        
        console.log('\n✅ WASM module loaded successfully!');
        console.log('Available functions:', Object.keys(calculator));
        
        // 함수 테스트
        console.log('\n📊 Testing calculator functions:');
        
        // Add 테스트
        const sum = calculator.Add(10, 20);
        console.log(`Add(10, 20) = ${sum}`);
        
        // Multiply 테스트
        const product = calculator.Multiply(5, 6);
        console.log(`Multiply(5, 6) = ${product}`);
        
        // CalculateTax 테스트
        const total = calculator.CalculateTax(100, 10);
        console.log(`CalculateTax(100, 10) = ${total}`);
        
        // AddInt32 테스트
        const intSum = calculator.AddInt32(15, 25);
        console.log(`AddInt32(15, 25) = ${intSum}`);
        
        // IsPositive 테스트
        const positive1 = calculator.IsPositive(5);
        const positive2 = calculator.IsPositive(-5);
        console.log(`IsPositive(5) = ${positive1 === 1 ? 'true' : 'false'}`);
        console.log(`IsPositive(-5) = ${positive2 === 1 ? 'true' : 'false'}`);
        
        // Power 테스트
        const powerResult = calculator.Power(2, 8);
        console.log(`Power(2, 8) = ${powerResult}`);
        
        // CalculateDiscount 테스트
        const discounted = calculator.CalculateDiscount(100, 20);
        console.log(`CalculateDiscount(100, 20) = ${discounted}`);
        
        console.log('\n✅ All tests completed!');
        
    } catch (error) {
        console.error('❌ Error:', error);
    }
}

// 실행
testCalculator();