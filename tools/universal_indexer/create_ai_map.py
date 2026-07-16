import os
import ast
import json
from pathlib import Path

try:
    from tools.universal_indexer.switch import SCAN_MODE
except ImportError:
    SCAN_MODE = "ROOT"
# ======================================================================
# 🎯 [경로 방어선 절대 고정]
# 현재 스크립트 파일 위치를 기준으로 진짜 프로젝트 마스터 루트를 추적합니다.
# 폴더 구조가 tools/universal_indexer/ 로 1단계 더 깊어졌으므로,
# "universal_indexer" 폴더 안에 있고 그 상위 폴더가 "tools"일 때만
# 두 단계 위(.parent.parent)를 진짜 루트로 판정합니다.
# 그 외의 경우(예: 단독 실행, 다른 위치로 복사됨 등)는 현재 폴더를 루트로 안전하게 폴백합니다.
# ======================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
# 🔄 폴더 물리 명칭이 변경되었으므로 검사 타깃 문자열을 똑같이 싱크해 줍니다.
if SCRIPT_DIR.name == "universal_indexer" and SCRIPT_DIR.parent.name == "tools":
    PROJECT_ROOT = SCRIPT_DIR.parent.parent
else:
    PROJECT_ROOT = SCRIPT_DIR

# 🚨 [경로 교정 핵심] indexer.py가 "실제로" 파일을 쓰는 위치와 100% 일치시킴
#    - 인덱서 장부(registry/protocol)는 system_memory/ 에 있음
#    - 결과물 지도는 update_map.py와 동일하게 system_maps/ 에 저장
OUTPUT_DIR = PROJECT_ROOT / "system_maps"
OUTPUT_FILE_PATH = OUTPUT_DIR / "AI_CODEBASE_MAP.md"
REGISTRY_JSON_PATH = PROJECT_ROOT / "system_memory" / "registry_constants.json"
PROTOCOL_JSON_PATH = PROJECT_ROOT / "system_memory" / "data_protocols.json"

# 🛡️ indexer.py의 scan_project()와 동일한 제외 규칙
EXCLUDE_KEYWORDS = [".venv", ".git", "__pycache__", "system_memory", "system_maps"]


# =====================================================================
# 🛠️ [수정] 자체 파이썬 AST 파싱 함수를 제거하고, 
# 인덱서가 이미 만들어둔 .jjap_context.json 통합 장부를 로드하는 함수로 대체합니다.
# =====================================================================
def load_jjap_context():
    """
    Indexer가 모든 언어(Python, Java, JSON)를 스캔해서 만들어둔 
    통합 .jjap_context.json 장부를 읽어옵니다. (단일 진실 공급원)
    """
    context_path = PROJECT_ROOT / "system_memory" / ".jjap_context.json"
    if not context_path.exists():
        # 만약 해당 위치에 없으면 프로젝트 루트 폴더도 확인 (폴백 방어선)
        context_path = PROJECT_ROOT / ".jjap_context.json"
        
    if context_path.exists():
        try:
            with open(context_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("files", {})
        except Exception as e:
            print(f"⚠️ [.jjap_context.json] 로드 중 오류 발생: {e}")
    else:
        print("⚠️ [.jjap_context.json] 통합 장부 파일을 찾을 수 없습니다. 인덱서를 먼저 실행해 주세요.")
    return {}


def collect_target_files():
    """[수정] .py 제한을 해제하고, 제외 키워드가 없는 프로젝트 내의 '모든 파일'을 수집합니다."""
    print("=" * 80)
    print("[DEBUG] collect_target_files() 시작")
    print(f"[DEBUG] PROJECT_ROOT = {PROJECT_ROOT}")
    print(f"[DEBUG] SCAN_MODE    = {SCAN_MODE}")
    print("=" * 80)
    if SCAN_MODE == "ROOT":
        scan_target = PROJECT_ROOT
        print("🎯 [create_ai_map] Mode: ROOT (프로젝트 전체 경로를 직접 스캔합니다)")
    else:
        # 레거시 src 지칭을 완전히 청산하고, 새로운 타깃 폴더명으로 단일화
        scan_target = PROJECT_ROOT / "extraction_target_project"
        print("🎯 [create_ai_map] Mode: EXTRACTION_TARGET_PROJECT (extraction_target_project/ 폴더 내부만 정밀 스캔합니다)")

    if not scan_target.exists():
        print(f"❌ [오류] 스캔 대상 경로가 존재하지 않습니다: {scan_target}")
        return []

    print(f"[DEBUG] SCAN_TARGET  = {scan_target}")

    target_files = []
    for root, dirs, files in os.walk(scan_target, followlinks=True):
        normalized_root = root.replace("\\", "/")

        print("\n------------------------------------------------------")
        print(f"[DEBUG] WALK ROOT : {root}")
        print(f"[DEBUG] DIR COUNT : {len(dirs)}")
        print(f"[DEBUG] FILE COUNT: {len(files)}")

        if "src/project_root/src" in normalized_root:
            print(f"[SKIP] duplicated path : {normalized_root}")
            continue
        if any(kw in normalized_root for kw in EXCLUDE_KEYWORDS):
            print(f"[SKIP] excluded keyword : {normalized_root}")
            continue

        print("[DIRS]")
        for d in dirs:
            print("   ", d)

        print("[FILES]")
        for file in files:
            print("   ", file)

        for file in files:
            if file == "start.py" and SCAN_MODE == "SRC":
                continue
            
            # 💡 [교정] 특정 확장자 차단 해제 -> 모든 파일을 수집 대상으로 포함
            full_path = Path(root) / file
            print(f"[ADD] {full_path}")
            target_files.append(full_path)

    print("=" * 80)
    print("[DEBUG] collect_target_files END")
    print(f"[DEBUG] TOTAL FILES = {len(target_files)}")
    print("=" * 80)

    return sorted(target_files)


def load_registry():
    """
    🔑 [Universal Registry Loader]
    신형 인덱서가 내뱉는 어떠한 형태의 데이터 구조도 유연하게 수용합니다.
    자바스크립트, C# 등 미래의 노동자 파서가 합류하여 형식이 변해도 절대 크래시가 나지 않습니다.
    """
    if not REGISTRY_JSON_PATH.exists():
        return set()
    try:
        with open(REGISTRY_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Case A: {"registered_entities": [...]} 로 감싸진 완벽한 신형 포맷
            if isinstance(data, dict) and "registered_entities" in data:
                entities = data["registered_entities"]
                if isinstance(entities, list):
                    return set(entities)
                elif isinstance(entities, dict):
                    return set(entities.keys())

            # Case B: 파일 경로별 딕셔너리 구조 { "path": [...] } 로 유입될 경우 호환
            if isinstance(data, dict):
                extracted = set()
                for k, v in data.items():
                    if isinstance(v, list):
                        for item in v: extracted.add(str(item))
                    else:
                        extracted.add(str(k))
                return extracted

            # Case C: 단순 순정 리스트 구조로 유입될 경우
            if isinstance(data, list):
                return set(str(x) for x in data)

            return set()
    except Exception as e:
        print(f"⚠️ [맵메이커 방어선] 레지스트리 로드 실패 우회: {e}")
        return set()


def load_protocols():
    """
    📊 [Universal Protocol Loader]
    신형 인덱서의 {"protocols": {...}} 마스터 구조를 안전하게 분해 및 흡수합니다.
    """
    if not PROTOCOL_JSON_PATH.exists():
        return {}
    try:
        with open(PROTOCOL_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Case A: {"protocols": {...}} 신형 포맷 대응
            if isinstance(data, dict) and "protocols" in data:
                return data["protocols"]
                
            # Case B: 평평한 순정 딕셔너리 구조
            if isinstance(data, dict):
                return data
                
            return {}
    except Exception as e:
        print(f"⚠️ [맵메이커 방어선] 프로토콜 로드 실패 우회: {e}")
        return {}


# =====================================================================
# 🛠️ [수정] .jjap_context.json에 존재하지 않는 "classes" 키를 조회하던 버그를 잡고,
# .jjap_symbols.json 장부의 'type' == 'class' 데이터를 기반으로 정밀 매칭합니다.
# =====================================================================
def parse_protocols_and_registries():
    """
    통합 심볼 장부를 기반으로 어떤 파일에 어떤 클래스(Registry, Protocol)가 
    정의되어 있는지 역추적하여 최종 매칭 테이블을 완성합니다 형님!
    """
    path_to_registry = {}
    path_to_protocol = {}

    # 1. 원본 장부 로드 (레지스트리 상수 및 프로토콜 명세 리스트)
    registry_data = load_registry()      # 기존의 load_registry 활용
    protocol_data = load_protocols()    # 기존의 load_protocols 활용

    # 2. 글로벌 심볼 장부(.jjap_symbols.json)에서 class 타입 추출
    symbols_path = PROJECT_ROOT / "system_memory" / ".jjap_symbols.json"
    if not symbols_path.exists():
        symbols_path = PROJECT_ROOT / ".jjap_symbols.json"

    all_symbols = []
    if symbols_path.exists():
        try:
            with open(symbols_path, "r", encoding="utf-8") as f:
                all_symbols = json.load(f).get("symbols", [])
        except Exception as e:
            print(f"⚠️ [.jjap_symbols.json] 읽기 실패: {e}")

    # 3. 심볼 장부를 순회하며 클래스 단위로 레지스트리/프로토콜 싱크 매칭
    for sym in all_symbols:
        if sym.get("type") != "class":
            continue
            
        cls_name = sym.get("name")
        rel_path = sym.get("path") # 예: "src/src/main/java/com/desertcore/lobbycmd.java"
        
        if not cls_name or not rel_path:
            continue

        # Posix 표준 경로 문자열로 정규화
        posix_rel_path = Path(rel_path).as_posix()

        # [A] 레지스트리 매칭 검사
        if cls_name in registry_data:
            if posix_rel_path not in path_to_registry:
                path_to_registry[posix_rel_path] = set()
            path_to_registry[posix_rel_path].add(cls_name)

        # [B] 프로토콜 명세 매칭 검사
        if cls_name in protocol_data:
            if posix_rel_path not in path_to_protocol:
                path_to_protocol[posix_rel_path] = []
            # 중복 추가 방어
            if (cls_name, protocol_data[cls_name]) not in path_to_protocol[posix_rel_path]:
                path_to_protocol[posix_rel_path].append((cls_name, protocol_data[cls_name]))

    return path_to_registry, path_to_protocol


def main():
    target_files = collect_target_files()
    
    # 1. 🛠️ [통합 개조] 인덱서가 작성한 모든 언어의 통합 컨텍스트 장부 미리 로드
    jjap_context = load_jjap_context()

    # 2. 🛠️ [통합 개조] 리팩터링된 글로벌 심볼 기반 레지스트리/프로토콜 역추적 매칭 데이터 획득
    path_to_registry, path_to_protocol = parse_protocols_and_registries()

    # 출력 타깃 폴더(system_maps/) 자동 확보 안전망
    OUTPUT_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
        # 🎯 [메모리 오염 방어] 바깥에 있던 printed_dirs를 이 안쪽으로 이사시켰습니다 형님!
        # 파일이 새로 열려 쓰여질 때마다 기존 장부를 깨끗하게 초기화하여 모드 전환 시 뒤엉킴을 막습니다.
        printed_dirs = set()

        # 마스터 헤더 사양 작성 (순정 코드 100% 유지)
        f.write("# 🏗️ AI-OPTIMIZED ULTRA COMPACT CODEBASE MAP (INTELLIGENT SCAN)\n\n")
        f.write("> **[AI 프로토콜 매뉴얼]** 이 문서는 다른 AI 비서들의 경로 오해를 차단하기 위해 파일마다 **실제 하드디스크 상대 경로 `[📂 실제경로]`**를 강제 명시해 둔 특수 지도입니다.\n")
        f.write("> AI 비서는 절대 눈치로 경로를 추측하지 말고, 파일명 뒤에 박혀있는 `[📂 실제경로]` 규격을 그대로 복사하여 agent_navigator를 호출하십시오.\n\n")
        f.write("```markdown\nproject_root/\n")
        
        # 파일 스캔 및 맵 생성 순회 루프
        for file_path in target_files:
            rel_path = file_path.relative_to(PROJECT_ROOT)
            posix_rel_path = rel_path.as_posix()
            file_name = file_path.name

            # 🎯 [형님 제안 반영] EXTRACTION_TARGET_PROJECT 모드일 때만 가장 바깥의 'extraction_target_project/' 문자열 제거 (출력용 display_path 생성)
            if SCAN_MODE == "EXTRACTION_TARGET_PROJECT" and posix_rel_path.startswith("extraction_target_project/"):
                display_path = posix_rel_path[26:]  # "extraction_target_project/" 26글자 컷
            else:
                display_path = posix_rel_path

            # 🌲 트리 계층 디렉토리 라인 생성 및 중복 출력 방지 (display_path 기준 트리 생성)
            parts = Path(display_path).parts
            for i in range(len(parts) - 1):
                current_dir_path = Path(*parts[:i + 1]).as_posix()
                if current_dir_path not in printed_dirs:
                    printed_dirs.add(current_dir_path)
                    indent = "│   " * i
                    f.write(f"{indent}├── {parts[i]}/\n")

            indent = "│   " * (len(parts) - 1)

            # 🛠️ [기존 순정 장부 조회 유지] 데이터 대조용 장부 조회는 원래 수집 경로(posix_rel_path)로 수행하여 누락 방지
            file_meta = jjap_context.get(posix_rel_path, {})
            symbols_info = file_meta.get("symbols_summary", "")

            # 🛠️ 레거시 src 대신 실제 물리 폴더명인 "extraction_target_project" 기준으로 중복 경로 폴백 방어선 구축
            if not symbols_info and posix_rel_path.startswith("extraction_target_project/extraction_target_project/"):
                shorter_path = posix_rel_path.replace("extraction_target_project/extraction_target_project/", "extraction_target_project/", 1)
                symbols_info = jjap_context.get(shorter_path, {}).get("symbols_summary", "")

            # 코드맵에 최종 파일 사양 한 줄 출력 (출력값만 display_path 적용)
            if symbols_info:
                f.write(f"{indent}├── {file_name} [📂 {display_path}] -> [{symbols_info}]\n")
            else:
                f.write(f"{indent}├── {file_name} [📂 {display_path}]\n")

            # 🔑 하위 레지스트리 매칭 블록 출력 (순정 원래 키값 유지)
            if posix_rel_path in path_to_registry:
                for reg_const in path_to_registry[posix_rel_path]:
                    f.write(f"{indent}│     ├── 🔑 [REGISTRY]: \"{reg_const}\"\n")

            # 📊 하위 프로토콜 청크 매칭 블록 출력 (순정 원래 키값 유지)
            if posix_rel_path in path_to_protocol:
                for proto_name, fields in path_to_protocol[posix_rel_path]:
                    f.write(f"{indent}│     ├── 📊 [PROTOCOL]: \"{proto_name}\"\n")
                    field_items = [
                        f"{k}({v.replace(' (기본값: ', ':').replace(')', '')})"
                        for k, v in fields.items()
                    ]
                    chunks = [field_items[x:x + 4] for x in range(0, len(field_items), 4)]
                    for chunk in chunks:
                        f.write(f"{indent}│     │     ├── {', '.join(chunk)}\n")
    
    # 하단 디버그 로그 및 요약 보고서 파일 쓰기 (순정 유지)
    print("=" * 80)
    print("[SUMMARY]")
    print(f"Directories Printed : {len(printed_dirs)}")
    print(f"Files Written       : {len(target_files)}")
    print("=" * 80)

    with open("scan_debug.txt", "w", encoding="utf-8") as dbg:
        dbg.write("==== ALL FILES ====\n")
        for p in target_files:
            dbg.write(str(p) + "\n")

    print(f"🎯 [마스터 공장] 'system_maps/AI_CODEBASE_MAP.md'가 모든 파일 구조를 포함하여 안전하게 자동 갱신되었습니다 형님!")

# ======================================================================
# 🔗 [파이프라인 결합 방어선]
# jjap_watcher.py가 호출하는 함수명을 완벽하게 지원하기 위한 브릿지 래퍼 함수
# ======================================================================
def generate_ai_optimized_map():
    """jjap_watcher.py의 실시간 갱신 요청을 수신하여 내부 메인 공장을 가동합니다."""
    main()


if __name__ == "__main__":
    main()
