import ast
import json
import hashlib
import os
import importlib.util
from pathlib import Path
from typing import Dict, Any, List

# 🎯 영문 switch.py 콘솔 원격 연동
try:
    from switch import SCAN_MODE
except ImportError:
    SCAN_MODE = "ROOT"

# 🎛️ [인덱서 코어 전용] 디버깅 로그 On/Off 마스터 스위치
DEBUG_LOG = True

def log(message: str):
    if DEBUG_LOG:
        print(f"📡 [Indexer-Core Log] {message}")

SCRIPT_DIR = Path(__file__).parent.resolve()
if SCRIPT_DIR.name == "universal_indexer" and SCRIPT_DIR.parent.name == "tools":
    PROJECT_ROOT = SCRIPT_DIR.parent.parent
else:
    PROJECT_ROOT = SCRIPT_DIR

OUTPUT_FILE_PATH = PROJECT_ROOT / "system_maps" / "AI_CODEBASE_MAP.md"
REGISTRY_JSON_PATH = PROJECT_ROOT / "system_memory" / "registry_constants.json"
PROTOCOL_JSON_PATH = PROJECT_ROOT / "system_memory" / "data_protocols.json"

class AdvancedIndexerV2:
    """
    [Jjap-Cursor Core Indexer V3.6 - Ultra Universal Engine]
    동적 플러그인 로딩 및 5대 장부 동기화의 모든 파이프라인에 디버깅 레이더를 도배했습니다.
    """
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.parsers: Dict[str, Any] = {}
        self.symbols: List[Dict[str, Any]] = []
        self.files_context: Dict[str, Any] = {}
        self.definition_map: Dict[str, str] = {}
        self.data_protocols: Dict[str, Any] = {}
        self.registry_constants: List[str] = []
        
        log(f"🏗️ 인덱서 코어 초기화 완료 (마스터 루트 주소: {self.project_root})")
        self._auto_load_parsers()

    def _auto_load_parsers(self):
        """core_parsers 폴더 내부의 파서들을 동적 로드하여 확장자별로 바인딩합니다."""
        parsers_dir = SCRIPT_DIR / "core_parsers"
        log(f"🔌 동적 파서 폴더 탐색 시작 -> 경로: {parsers_dir}")
        
        if not parsers_dir.exists():
            log(f"⚠️ [경고] core_parsers 폴더가 물리적으로 존재하지 않습니다: {parsers_dir}")
            return

        file_list = os.listdir(parsers_dir)
        log(f"📂 폴더 내부 파일 목록 검색 완료 (총 {len(file_list)}개 탐지됨)")

        for file in file_list:
            if file.endswith("_parser.py"):
                ext = f".{file.split('_parser.py')[0]}"
                full_path = parsers_dir / file
                log(f"   ⚙️ 파서 후보 발견: '{file}' -> 매핑 타깃 확장자: '{ext}'")
                
                try:
                    spec = importlib.util.spec_from_file_location(f"parser_{ext}", full_path)
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        if hasattr(mod, "extract_symbols"):
                            self.parsers[ext] = mod.extract_symbols
                            log(f"   └── 🟢 [바인딩 성공] 확장자 [{ext}] 엔진 탑재 완료!")
                        else:
                            log(f"   └── ❌ [인터페이스 불일치] '{file}' 내부에 'extract_symbols' 함수가 없습니다.")
                except Exception as ex:
                    log(f"   └── 💥 [런타임 컴파일 에러] 파서 플러그인 로딩 실패: {file} | 사유: {ex}")

        log(f"📊 파서 동적 마운트 최종 정산: 총 {len(self.parsers)}개의 다국어 컴포넌트 활성화.")

    def scan_project(self):
        """설정된 SCAN_MODE에 따라 프로젝트 내의 모든 등록된 언어 파일을 스캔합니다."""
        # 🛠️ 레거시 "src" 하드코딩을 청산하고, switch.py의 새로운 물리 폴더명("extraction_target_project")과 완벽 매핑
        scan_target = self.project_root if SCAN_MODE == "ROOT" else self.project_root / "extraction_target_project"
        log(f"🚀 [디버깅 레이더 가동] 모드: {SCAN_MODE} | 물리 스캔 범위: {scan_target}")

        EXCLUDE_KEYWORDS = [".venv", ".git", "__pycache__", "system_memory", "system_maps"]
        log(f"🛡️ 고유 스캔 제외 키워드 목록: {EXCLUDE_KEYWORDS}")
        
        if not scan_target.exists():
            log(f"❌ [치명적 오류] 지정된 스캔 타깃 경로가 디스크에 존재하지 않습니다: {scan_target}")
            return

        total_scanned_count = 0
        total_ignored_count = 0

        for root, dirs, files in os.walk(scan_target, followlinks=True):
            normalized_root = root.replace("\\", "/")
            
            # 제외 폴더 조건 검사 및 로깅
            if any(kw in normalized_root for kw in EXCLUDE_KEYWORDS):
                log(f"🚫 [패스] 제외 필터 경로 스킵: {normalized_root}")
                continue

            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()

                # 동적으로 로드된 파서 대상 확장자 범위에 포함되는지 확인
                if ext in self.parsers:
                    log(f"🔍 [타깃 포착] 파일 발견: {file_path.name} (확장자: {ext})")
                    self.index_file(file_path, ext)
                    total_scanned_count += 1
                else:
                    total_ignored_count += 1

        log(f"🏁 스캔 타임라인 종료 -> 분석 통계 [처리 완료: {total_scanned_count}개 | 미지원/패스: {total_ignored_count}개]")

        # 🗂️ 수집 완료 후 디스크 정밀 장부 보관소로 직행 쓰기
        self.save_index_data()

    def index_file(self, file_path: Path, ext: str):
        """개별 파일을 파서를 통해 쪼개어 마스터 장부에 바느질합니다."""
        try:
            rel_path_str = file_path.relative_to(self.project_root).as_posix()
        except ValueError:
            rel_path_str = file_path.resolve().relative_to(self.project_root.resolve()).as_posix()

        log(f"🧵 [장부 바느질 개시] 상대 경로 키: '{rel_path_str}'")
        parser_func = self.parsers[ext]
        
        try:
            log(f"   📡 플러그인 함수 {parser_func.__name__} 원격 연산 제어권 이양 중...")
            res = parser_func(file_path, self.project_root)
            
            if not res or len(res) < 5:
                log(f"   ⚠️ [규격 위반] '{rel_path_str}' 파서의 반환 데이터가 5대 규격을 충족하지 못해 드롭합니다.")
                return

            f_symbols, f_context, f_def_map, f_protocols, f_registry = res

            # 데이터 적재 현황 세부 체크 로그
            log(f"   📥 수집 결과 피드백 받음 -> 심볼: {len(f_symbols)}개, 정의 매핑: {len(f_def_map)}개, 프로토콜: {len(f_protocols)}개, 레지스트리: {len(f_registry)}개")

            # 1. 글로벌 심볼 리스트 누적
            self.symbols.extend(f_symbols)
            
            # 2. 파일 요약 정보 컨텍스트 병합
            self.files_context.update(f_context)
            
            # 3. 정의 맵 및 레지스트리 병합
            self.definition_map.update(f_def_map)
            self.data_protocols.update(f_protocols)
            
            for item in f_registry:
                if item not in self.registry_constants:
                    self.registry_constants.append(item)

            log(f"   📈 [바느질 완료] 마스터 메모리 장부 적재 성공: '{rel_path_str}'")
        except Exception as e:
            log(f"   💥 [인덱싱 내부 크래시] 파일 처리 중 예외 발생: {rel_path_str} | 에러 내용: {e}")

    def save_index_data(self):
        """메모리에 적재된 5대 장부를 디스크에 격리 저장합니다."""
        TARGET_MEMORY_DIR = self.project_root / "system_memory"
        log(f"💾 [디스크 동기화] system_memory 보관소 직인 쓰기 시작 -> 폴더 위치: {TARGET_MEMORY_DIR}")
        
        try:
            os.makedirs(TARGET_MEMORY_DIR, exist_ok=True)

            ctx_path = TARGET_MEMORY_DIR / ".jjap_context.json"
            with open(ctx_path, "w", encoding="utf-8") as f:
                json.dump({"files": self.files_context}, f, indent=2, ensure_ascii=False)
            log(f"   ├── 📄 [.jjap_context.json] 저장 완료 (총 {len(self.files_context)}개 파일 컨텍스트)")

            sym_path = TARGET_MEMORY_DIR / ".jjap_symbols.json"
            with open(sym_path, "w", encoding="utf-8") as f:
                json.dump({"symbols": self.symbols}, f, indent=2, ensure_ascii=False)
            log(f"   ├── 📄 [.jjap_symbols.json] 저장 완료 (총 {len(self.symbols)}개 글로벌 심볼)")

            def_path = TARGET_MEMORY_DIR / "definition_map.json"
            with open(def_path, "w", encoding="utf-8") as f:
                json.dump(self.definition_map, f, indent=2, ensure_ascii=False)
            log(f"   ├── 📄 [definition_map.json] 저장 완료 (총 {len(self.definition_map)}개 빠른 추적 정의 노드)")

            proto_path = TARGET_MEMORY_DIR / "data_protocols.json"
            with open(proto_path, "w", encoding="utf-8") as f:
                json.dump({"protocols": self.data_protocols}, f, indent=2, ensure_ascii=False)
            log(f"   ├── 📄 [data_protocols.json] 저장 완료 (총 {len(self.data_protocols)}개 명세 프로토콜)")

            reg_path = TARGET_MEMORY_DIR / "registry_constants.json"
            with open(reg_path, "w", encoding="utf-8") as f:
                json.dump({"registered_entities": self.registry_constants}, f, indent=2, ensure_ascii=False)
            log(f"   └── 📄 [registry_constants.json] 저장 완료 (총 {len(self.registry_constants)}개 엔티티 레지스트리)")

            print(f"🧬 [Jjap-Indexer Universal] 5대 장부 전체 동기화 성공! 보관된 총 파일 수: {len(self.files_context)}개")
        except Exception as write_err:
            log(f"💥 [디스크 파일 쓰기 치명적 실패] 장부 동동화 중 에러 발생: {write_err}")

if __name__ == "__main__":
    indexer = AdvancedIndexerV2(PROJECT_ROOT)
    indexer.scan_project()