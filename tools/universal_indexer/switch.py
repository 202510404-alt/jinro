"""Jjap-Cursor Path Targeting Toggle Controller.

[switch.py]
형님이 프로젝트 소스코드를 수색할 때, 실제 디스크 경로와 1대1로 일치시킬지("ROOT"),
아니면 기존 격리 구조 내부만 스캔할지("EXTRACTION_TARGET_PROJECT") 딸깍 결정하는 영문 마스터 콘솔 스위치입니다.
"""

# 🎛️ 마스터 토글 스위치 
# "ROOT" -> 프로젝트 전체 원본 경로 직접 징집 (경로 불일치 에러 완벽 해결! 실제 경로 유지)
# "EXTRACTION_TARGET_PROJECT"  -> 기존 방식 (오직 extraction_target_project/ 폴더 내부만 검사)
SCAN_MODE = "EXTRACTION_TARGET_PROJECT"

SYSTEM_EXCLUDES = ["system_memory", "system_maps"]