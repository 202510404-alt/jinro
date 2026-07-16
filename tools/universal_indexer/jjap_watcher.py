"""Jjap-Cursor Codebase Real-time Auto Watcher.

[백그라운드 자동화 감시 사령탑 - 절대 경로 물리 로드 버전]
# INFO: 파이썬의 import 검색 알고리즘을 우회하고, 하드디스크의 해당 파일을 핀포인트 타격 로드합니다.
"""

import os
import sys
import time
from pathlib import Path
import importlib.util

# 🎛️ [절대 규칙 2번] 원터치 디버깅 로그 스위치
DEBUG_MODE = True

# 🔄 물리적 경로 계산 (신규 universal_indexer 2단계 깊이 뼈대에 맞춤 수정)
CURRENT_DIR = Path(__file__).parent.resolve()

# 폴더명이 universal_indexer 이고 부모가 tools 일 때만 진짜 마스터 루트(2단계 위)를 낚아챕니다.
if CURRENT_DIR.name == "universal_indexer" and CURRENT_DIR.parent.name == "tools":
    PROJECT_ROOT = CURRENT_DIR.parent.parent
else:
    PROJECT_ROOT = CURRENT_DIR

def import_file_directly(module_name: str, file_path: Path):
    """파이썬 모듈 캐시를 우회하고 하드디스크의 파일을 날것 그대로 강제 로드합니다."""
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"❌ '{file_path}' 경로에서 spec을 추출할 수 없습니다.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def run_pipeline():
    """소스코드 변경 포착 시 인덱싱 공장과 지도 제작소를 연쇄 가동하는 마스터 파이프라인"""
    print("\n🔄 [파이프라인 트리거] 소스코드 변동 정밀 포착! 정렬 재인덱싱 작전 개시...")
    
    try:
        # [Step 3-1] 메모리 찌꺼기 청소 (캐시 크래시 원천 방지)
        for key in ["indexer", "update_map", "create_ai_map"]:
            if key in sys.modules:
                del sys.modules[key]

        # 🎯 1단계: 인덱서 강제 가동 (AdvancedIndexerV2)
        indexer_path = CURRENT_DIR / "indexer.py"
        indexer_module = import_file_directly("indexer", indexer_path)
        print("  ➡️ 1/3 단계: 신형 인덱서 V2 스캔 엔진 가동 중...")
        
        indexer_obj = indexer_module.AdvancedIndexerV2(PROJECT_ROOT)
        indexer_obj.scan_project()
        
        # 디버그 모드일 때만 심볼 정밀 스캔 내역 도배
        if DEBUG_MODE:
            classes = [s["name"] for s in indexer_obj.symbols if s.get("type") == "class"]
            methods = [s["name"] for s in indexer_obj.symbols if s.get("type") in ["function", "method"]]
            print(f"    🧬 [디버그] 클래스 목록 추출: {classes}")
            print(f"    🎯 [디버그] 함수/메서드 목록 추출: {methods}")
            
        # 🎯 2단계: 기존 인간용 백과사전 지도 제작 (update_map.py)
        update_map_path = CURRENT_DIR / "update_map.py"
        update_map_module = import_file_directly("update_map", update_map_path)
        print("  ➡️ 2/3 단계: 인간용 CODEBASE_MAP.md 장부 최신화 중...")
        update_map_module.update_map()        
        
        # 🎯 3단계: 형님의 특명! AI 전용 초경량 극한 요약 지도 실시간 동기화 (신설 🔥)
        create_ai_map_path = CURRENT_DIR / "create_ai_map.py"
        create_ai_map_module = import_file_directly("create_ai_map", create_ai_map_path)
        print("  ➡️ 3/3 단계: AI용 AI_CODEBASE_MAP.md 초경량 압축 시그니처 지도 생산 중...")
        create_ai_map_module.generate_ai_optimized_map()
        
        print("✅ [동기화 완료] 모든 장부와 AI 가성비 지도가 최신 상태로 바느질되었습니다!\n")
        
    except Exception as e:
        print(f"❌ [에러 발생] 파이프라인 구동 중 사고 발생: {e}")
        import traceback
        if DEBUG_MODE:
            traceback.print_exc()

# 💡 Watchdog 핸들러 및 Observer 설정부 (기존 로직 유지)
class CodeChangeHandler:
    def __init__(self):
        self.last_trigger_time = 0
        self.debounce_duration = 0.5  # 디바운스 초단위 설정
        
    def dispatch(self, event):
        if event.is_directory:
            return
            
        src_path = Path(event.src_path)
        
        # 검열 검문소: 백그라운드 찌꺼기나 결과물 파일은 가볍게 무시
        # 🛡️ [격리 방어선] 무한 루프 폭파 방지용 system_memory 및 system_maps 폴더 무시 키워드 추가 주입!
        EXCLUDE_KEYWORDS = [".venv", ".git", "__pycache__", "cline_tools", ".json", ".md", "system_memory", "system_maps"]
        if any(kw in src_path.as_posix() for kw in EXCLUDE_KEYWORDS):
            return
            
        if src_path.suffix == ".py":
            current_time = time.time()
            if current_time - self.last_trigger_time > self.debounce_duration:
                self.last_trigger_time = current_time
                if DEBUG_MODE:
                    print(f"🔔 [감시망 포착] 파일 변경 감지됨: {src_path.name}")
                run_pipeline()

def main():
    print("=" * 70)
    print("🚀 [Jjap-Cursor Watcher] 실시간 백그라운드 감시망 기동!")
    print(f"📂 감시 대상 진짜 루트 절대 경로: {PROJECT_ROOT}")
    print(f"⚙️  초정밀 디버깅 모드 상태: {'🔴 ON' if DEBUG_MODE else '⚪ OFF'}")
    print("💡 소스코드를 수정하고 저장(Ctrl+S)하면 AI 초경량 지도가 무한 자동 갱신됩니다.")
    print("=" * 70)
    
    # 초도 기동 시 장부가 없을 수 있으므로 파이프라인 1회 선제 타격 가동
    run_pipeline()
    
    try:
        from watchdog.observers.polling import PollingObserver as Observer
    except ImportError:
        from watchdog.observers import Observer

    event_handler = CodeChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=str(PROJECT_ROOT), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()