"""
WASM Instance 생성 및 관리
wasmer-python을 사용하여 Rust WASM 모듈 로드
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

try:
    from wasmtime import Store, Module, Instance, Engine, Linker, WasiConfig
    WASMTIME_AVAILABLE = True
except ImportError:
    WASMTIME_AVAILABLE = False
    Instance = None  # ImportError 시 Instance 타입 정의

logger = logging.getLogger(__name__)


def CreateWasmInstance(wasm_file_path: str) -> Tuple[Optional['Instance'], Optional[str]]:
    """
    WASM 인스턴스 생성 (Go-style naming, 명시적 에러 처리)
    
    Args:
        wasm_file_path: WASM 파일 경로
        
    Returns:
        Tuple[Optional[Instance], Optional[str]]: (인스턴스, 에러메시지)
    """
    if not WASMTIME_AVAILABLE:
        error_msg = "500: wasmtime-python is not installed. Install with: uv add wasmtime"
        logger.error(error_msg)
        return None, error_msg
    
    wasm_path = Path(wasm_file_path)
    if not wasm_path.exists():
        error_msg = f"404: WASM file not found: {wasm_path}"
        logger.error(error_msg)
        return None, error_msg
    
    logger.info(f"Loading WASM module from: {wasm_path}")
    
    # Store 생성
    try:
        store = Store()
    except Exception as e:
        error_msg = f"500: Failed to create WASM store: {str(e)}"
        logger.error(error_msg)
        return None, error_msg
    
    # Module 컴파일 (파일에서 직접)
    try:
        module = Module.from_file(store.engine, str(wasm_path))
    except Exception as e:
        error_msg = f"500: Failed to compile WASM module: {str(e)}"
        logger.error(error_msg)
        return None, error_msg
    
    # WASI Linker를 사용하여 Instance 생성
    try:
        linker = Linker(store.engine)
        linker.define_wasi()
        instance = linker.instantiate(store, module)
    except Exception as e:
        error_msg = f"500: Failed to create WASM instance: {str(e)}"
        logger.error(error_msg)
        return None, error_msg
    
    # 사용 가능한 exports 확인
    try:
        available_exports = list(instance.exports(store).keys())
        logger.info(f"✅ WASM instance created successfully")
        logger.info(f"Available exports: {available_exports}")
        
        # Store를 instance에 저장 (나중에 함수 호출시 필요)
        instance.store = store
        
        return instance, None
        
    except Exception as e:
        error_msg = f"500: Failed to inspect WASM exports: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

