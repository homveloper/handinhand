#!/bin/bash
# Hand in Hand Python Server - uv 간편 실행

set -e

# 기본 설정 파일
CONFIG="${1:-../shared/config/server-config.json}"

# uv로 의존성 설치 및 서버 실행
uv run python cmd/server.py --config "$CONFIG"