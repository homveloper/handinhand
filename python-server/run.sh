#!/bin/bash

# Hand in Hand Python Server 실행 스크립트

set -e

# 프로젝트 루트 디렉토리
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HANDINHAND_ROOT="$(dirname "$PROJECT_ROOT")"

# 기본 설정 파일 경로
DEFAULT_CONFIG="$HANDINHAND_ROOT/shared/config/server-config.json"

# 기본 WASM 파일 경로
DEFAULT_WASM="$HANDINHAND_ROOT/shared/domain-rust/pkg-wasmtime/domain_rust.wasm"

# 도움말 출력
show_help() {
    echo "Hand in Hand Python Server 실행 스크립트"
    echo ""
    echo "사용법:"
    echo "  ./run.sh [옵션]"
    echo ""
    echo "옵션:"
    echo "  -c, --config FILE    설정 파일 경로 (기본값: ../shared/config/server-config.json)"
    echo "  -e, --env ENV        환경별 설정 파일 사용 (development|testing|production)"
    echo "  -w, --wasm FILE      WASM 모듈 파일 경로 (기본값: ../shared/domain-rust/pkg-wasmtime/domain_rust.wasm)"
    echo "  -h, --help           도움말 표시"
    echo ""
    echo "예시:"
    echo "  ./run.sh                                    # 기본 설정으로 실행"
    echo "  ./run.sh -e development                     # 개발 환경 설정으로 실행"
    echo "  ./run.sh -c /path/to/custom-config.json     # 커스텀 설정 파일로 실행"
    echo "  ./run.sh -w /path/to/custom.wasm           # 커스텀 WASM 파일로 실행"
    echo ""
}

# 의존성 확인
check_dependencies() {
    echo "🔍 의존성 확인 중..."
    
    # Python 버전 확인
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3이 설치되어 있지 않습니다."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "✅ Python $PYTHON_VERSION 확인됨"
    
    # 가상환경 활성화 (있는 경우)
    if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
        echo "🐍 가상환경 활성화 중..."
        source "$PROJECT_ROOT/venv/bin/activate"
    elif [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
        echo "🐍 가상환경 활성화 중..."
        source "$PROJECT_ROOT/.venv/bin/activate"
    else
        echo "⚠️  가상환경이 없습니다. 시스템 Python을 사용합니다."
    fi
    
    # 필수 패키지 확인
    echo "📦 필수 패키지 확인 중..."
    python3 -c "import fastapi, redis, uvicorn" 2>/dev/null || {
        echo "❌ 필수 패키지가 설치되어 있지 않습니다."
        echo "다음 명령으로 설치하세요:"
        echo "  pip install fastapi redis uvicorn"
        exit 1
    }
    echo "✅ 필수 패키지 확인됨"
}

# 설정 파일 확인
check_config() {
    local config_file="$1"
    
    if [ ! -f "$config_file" ]; then
        echo "❌ 설정 파일을 찾을 수 없습니다: $config_file"
        echo ""
        echo "사용 가능한 설정 파일:"
        find "$HANDINHAND_ROOT/shared/config" -name "server-config*.json" 2>/dev/null | sed 's/^/  /' || echo "  (설정 파일이 없습니다)"
        exit 1
    fi
    
    # JSON 유효성 검사
    if ! python3 -m json.tool "$config_file" > /dev/null 2>&1; then
        echo "❌ 유효하지 않은 JSON 파일입니다: $config_file"
        exit 1
    fi
    
    echo "✅ 설정 파일 확인됨: $config_file"
}

# Redis 연결 확인
check_redis() {
    local config_file="$1"
    
    echo "🔗 Redis 연결 확인 중..."
    
    # Python으로 설정에서 Redis 정보 추출 및 연결 테스트
    python3 -c "
import json
import redis
import sys

try:
    with open('$config_file', 'r') as f:
        config = json.load(f)
    
    redis_config = config['redis']
    client = redis.Redis(
        host=redis_config['host'],
        port=redis_config['port'],
        db=redis_config['db'],
        password=redis_config.get('password'),
        socket_connect_timeout=3
    )
    
    client.ping()
    print('✅ Redis 연결 성공: {}:{}/{}'.format(
        redis_config['host'], 
        redis_config['port'], 
        redis_config['db']
    ))
except Exception as e:
    print('⚠️  Redis 연결 실패:', str(e))
    print('서버는 실행되지만 Redis 기능은 작동하지 않을 수 있습니다.')
" || echo "⚠️  Redis 연결 확인 중 오류 발생"
}

# 서버 실행
run_server() {
    local config_file="$1"
    local wasm_file="$2"
    
    echo ""
    echo "🚀 Hand in Hand Python Server 시작"
    echo "======================================"
    
    # 현재 디렉토리를 프로젝트 루트로 변경
    cd "$PROJECT_ROOT"
    
    # 서버 실행 명령 구성
    local cmd="python3 cmd/server.py --config \"$config_file\""
    if [ -n "$wasm_file" ]; then
        cmd="$cmd --wasm \"$wasm_file\""
    fi
    
    # 서버 실행
    eval $cmd
}

# 메인 실행 로직
main() {
    local config_file="$DEFAULT_CONFIG"
    local wasm_file="$DEFAULT_WASM"
    
    # 명령행 인자 파싱
    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--config)
                config_file="$2"
                shift 2
                ;;
            -w|--wasm)
                wasm_file="$2"
                shift 2
                ;;
            -e|--env)
                case $2 in
                    development|dev)
                        config_file="$HANDINHAND_ROOT/shared/config/server-config.json"
                        ;;
                    testing|test)
                        config_file="$HANDINHAND_ROOT/shared/config/server-config.testing.json"
                        ;;
                    production|prod)
                        config_file="$HANDINHAND_ROOT/shared/config/server-config.production.json"
                        ;;
                    *)
                        echo "❌ 지원하지 않는 환경: $2"
                        echo "지원 환경: development, testing, production"
                        exit 1
                        ;;
                esac
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo "❌ 알 수 없는 옵션: $1"
                echo "도움말을 보려면 ./run.sh --help를 실행하세요."
                exit 1
                ;;
        esac
    done
    
    # 절대 경로로 변환
    config_file="$(realpath "$config_file")"
    wasm_file="$(realpath "$wasm_file")"
    
    echo "🎯 Hand in Hand Python Server"
    echo "📁 프로젝트 경로: $PROJECT_ROOT"
    echo "⚙️  설정 파일: $config_file"
    echo "🦀 WASM 모듈: $wasm_file"
    echo ""
    
    # 사전 검사
    check_dependencies
    check_config "$config_file"
    check_redis "$config_file"
    
    # 서버 실행
    run_server "$config_file" "$wasm_file"
}

# 스크립트가 직접 실행된 경우에만 main 함수 호출
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi