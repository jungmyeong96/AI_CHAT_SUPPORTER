#!/bin/bash
# run_pipeline.sh

echo "🚀 [5시간 해커톤] AI 에이전트 파이프라인 초기화를 시작합니다..."

# 1. 아키텍처 명세에 따른 물리 볼륨 공유 경로 선제 생성
mkdir -p backend/backend_data qdrant_storage ollama_storage[cite: 3]

# 2. 에이전트 규칙 파일 배치 여부 검증
if [ ! -f "config/agent_1_architect.md" ]; then
    echo "❌ 에러: config/ 폴더 내에 에이전트 프롬프트 파일이 존재하지 않습니다."
    exit 1
fi

echo "✅ 모든 전처리 및 인프라 룰 설정이 완료되었습니다."
echo "💡 이제 Cursor Composer를 열고 아래 명령어로 해커톤을 시작하십시오:"
echo "👉 '@config/agent_1_architect.md 시스템 설계를 시작하고 스키마와 계약서를 빌드해줘.'"