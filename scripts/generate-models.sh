#!/bin/bash

# JSON Schema에서 각 언어별 모델 코드 생성 스크립트
# Hand in Hand 프로젝트용

set -e

# 프로젝트 루트 디렉토리
PROJECT_ROOT="/Users/danghamo/Documents/gituhb/handinhand"
SCHEMAS_DIR="$PROJECT_ROOT/shared/schemas"

echo "🚀 Hand in Hand - JSON Schema 기반 모델 코드 생성 시작"
echo "======================================================="

# 각 언어별 출력 디렉토리 생성
mkdir -p "$PROJECT_ROOT/python-server/src/domain/user/entities"
mkdir -p "$PROJECT_ROOT/python-server/src/config"
mkdir -p "$PROJECT_ROOT/nodejs-server/src/domain/user/entities"
mkdir -p "$PROJECT_ROOT/nodejs-server/src/config"
mkdir -p "$PROJECT_ROOT/golang-server/src/domain/user/entities"
mkdir -p "$PROJECT_ROOT/golang-server/src/config"
mkdir -p "$PROJECT_ROOT/csharp-server/src/Domain/User/Entities"
mkdir -p "$PROJECT_ROOT/csharp-server/src/Config"
mkdir -p "$PROJECT_ROOT/shared/domain-rust/src/schemas"

echo "📁 출력 디렉토리 생성 완료"

# Python 모델 생성 (Schema 접미사)
echo "🐍 Python 모델 생성 중..."
quicktype --src-lang schema --lang py \
  -o "$PROJECT_ROOT/python-server/src/domain/user/aggregates/user_aggregates_schema.py" \
  --python-version 3.7 --nice-property-names \
  "$SCHEMAS_DIR/UserAggregates.json"

quicktype --src-lang schema --lang py \
  -o "$PROJECT_ROOT/python-server/src/domain/user/aggregates/profile_entity_schema.py" \
  --python-version 3.7 --nice-property-names \
  "$SCHEMAS_DIR/ProfileEntity.json"

quicktype --src-lang schema --lang py \
  -o "$PROJECT_ROOT/python-server/src/domain/user/aggregates/inventory_entity_schema.py" \
  --python-version 3.7 --nice-property-names \
  "$SCHEMAS_DIR/InventoryEntity.json"

quicktype --src-lang schema --lang py \
  -o "$PROJECT_ROOT/python-server/src/config/server_config_schema.py" \
  --python-version 3.7 --nice-property-names \
  "$SCHEMAS_DIR/ServerConfig.json"

echo "✅ Python 모델 생성 완료"

# Node.js 모델 생성 (Schema 접미사)
echo "🟨 Node.js TypeScript 모델 생성 중..."
quicktype --src-lang schema --lang ts \
  -o "$PROJECT_ROOT/nodejs-server/src/domain/user/aggregates/UserAggregatesSchema.ts" \
  --nice-property-names \
  "$SCHEMAS_DIR/UserAggregates.json"

quicktype --src-lang schema --lang ts \
  -o "$PROJECT_ROOT/nodejs-server/src/domain/user/aggregates/ProfileEntitySchema.ts" \
  --nice-property-names \
  "$SCHEMAS_DIR/ProfileEntity.json"

quicktype --src-lang schema --lang ts \
  -o "$PROJECT_ROOT/nodejs-server/src/domain/user/aggregates/InventoryEntitySchema.ts" \
  --nice-property-names \
  "$SCHEMAS_DIR/InventoryEntity.json"

quicktype --src-lang schema --lang ts \
  -o "$PROJECT_ROOT/nodejs-server/src/config/ServerConfigSchema.ts" \
  --nice-property-names \
  "$SCHEMAS_DIR/ServerConfig.json"

echo "✅ Node.js TypeScript 모델 생성 완료"

# Go 모델 생성 (Schema 접미사)
echo "🔵 Go 모델 생성 중..."
quicktype --src-lang schema --lang go \
  -o "$PROJECT_ROOT/golang-server/src/domain/user/aggregates/user_aggregates_schema.go" \
  --package entities \
  "$SCHEMAS_DIR/UserAggregates.json"

quicktype --src-lang schema --lang go \
  -o "$PROJECT_ROOT/golang-server/src/domain/user/aggregates/profile_entity_schema.go" \
  --package entities \
  "$SCHEMAS_DIR/ProfileEntity.json"

quicktype --src-lang schema --lang go \
  -o "$PROJECT_ROOT/golang-server/src/domain/user/aggregates/inventory_entity_schema.go" \
  --package entities \
  "$SCHEMAS_DIR/InventoryEntity.json"

quicktype --src-lang schema --lang go \
  -o "$PROJECT_ROOT/golang-server/src/config/server_config_schema.go" \
  --package config \
  "$SCHEMAS_DIR/ServerConfig.json"

echo "✅ Go 모델 생성 완료"

# C# 모델 생성 (Schema 접미사)
echo "🟣 C# 모델 생성 중..."
quicktype --src-lang schema --lang cs \
  -o "$PROJECT_ROOT/csharp-server/src/Domain/user/aggregates/UserAggregatesSchema.cs" \
  --namespace HandInHand.Domain.User.Entities \
  "$SCHEMAS_DIR/UserAggregates.json"

quicktype --src-lang schema --lang cs \
  -o "$PROJECT_ROOT/csharp-server/src/Domain/user/aggregates/ProfileEntitySchema.cs" \
  --namespace HandInHand.Domain.User.Entities \
  "$SCHEMAS_DIR/ProfileEntity.json"

quicktype --src-lang schema --lang cs \
  -o "$PROJECT_ROOT/csharp-server/src/Domain/user/aggregates/InventoryEntitySchema.cs" \
  --namespace HandInHand.Domain.User.Entities \
  "$SCHEMAS_DIR/InventoryEntity.json"

quicktype --src-lang schema --lang cs \
  -o "$PROJECT_ROOT/csharp-server/src/Config/ServerConfigSchema.cs" \
  --namespace HandInHand.Config \
  "$SCHEMAS_DIR/ServerConfig.json"

echo "✅ C# 모델 생성 완료"

# Rust 모델 생성 (Schema 접미사)
echo "🦀 Rust 모델 생성 중..."
quicktype --src-lang schema --lang rust \
  -o "$PROJECT_ROOT/shared/domain-rust/src/schemas/user_aggregates_schema.rs" \
  "$SCHEMAS_DIR/UserAggregates.json"

quicktype --src-lang schema --lang rust \
  -o "$PROJECT_ROOT/shared/domain-rust/src/schemas/profile_entity_schema.rs" \
  "$SCHEMAS_DIR/ProfileEntity.json"

quicktype --src-lang schema --lang rust \
  -o "$PROJECT_ROOT/shared/domain-rust/src/schemas/inventory_entity_schema.rs" \
  "$SCHEMAS_DIR/InventoryEntity.json"

quicktype --src-lang schema --lang rust \
  -o "$PROJECT_ROOT/shared/domain-rust/src/schemas/server_config_schema.rs" \
  "$SCHEMAS_DIR/ServerConfig.json"

echo "✅ Rust 모델 생성 완료"

echo ""
echo "🎉 모든 언어별 모델 코드 생성 완료!"
echo "======================================="
echo "💡 파일 구조 안내:"
echo "   - *_schema.* : JSON Schema에서 자동 생성 (수정 금지)"
echo "   - *.* : 실제 비즈니스 로직 구현 (자유롭게 수정 가능)"
echo "   - 예: user_aggregates_schema.py (자동생성) → user_aggregates.py (비즈니스 로직)"
echo "📂 생성된 파일 위치:"
echo "   🐍 Python: python-server/src/domain/user/aggregates/"
echo "   🟨 Node.js: nodejs-server/src/domain/user/aggregates/"
echo "   🔵 Go: golang-server/src/domain/user/aggregates/"
echo "   🟣 C#: csharp-server/src/Domain/user/aggregates/"
echo "   🦀 Rust: shared/domain-rust/src/schemas/"
echo ""
echo "📋 다음 단계:"
echo "   1. 각 언어별 프로젝트에서 모델 임포트 확인"
echo "   2. 직렬화/역직렬화 테스트"
echo "   3. 각 언어별 Repository 패턴 구현"