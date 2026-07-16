import json
import hashlib
from pathlib import Path

def extract_symbols(file_path: Path, project_root: Path):
    """
    📦 [JSON Core Parser v1.0]
    새로운 자동화 임포터 인터페이스 계약(5대 장부 리턴 구조)을 100% 준수합니다.
    JSON 파일 내부의 주요 루트 키(Root Keys) 및 스키마 구조를 탐지하여 스켈레톤과 심볼로 등록합니다.
    """
    # 🤝 새로운 사령탑이 한 번에 흡수할 5대 데이터 규격 초기화
    symbols = []
    file_context = {}
    definition_map = {}
    data_protocols = {}
    registry_constants = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        # 파일 읽기 실패 시 안전 패스 프로토콜
        return symbols, {}, {}, {}, []

    rel_path_str = file_path.relative_to(project_root).as_posix()
    file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    # 1. JSON 문법 유효성 검사 및 파싱
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # 깨진 JSON 파일 방어선
        return symbols, {}, {}, {}, []

    # 2. 🧱 스켈레톤(뼈대) 및 요약 텍스트 생성
    # AI 비서들이 JSON의 전체 덩어리를 다 먹어서 컨텍스트가 터지는 것을 막기 위해,
    # 최상위 키 레이아웃과 데이터 타입만 예쁘게 요약 요리합니다.
    skeleton_lines = ["📦 [JSON STRUCTURE MAP]"]
    symbols_info_strings = []

    if isinstance(data, dict):
        for key, value in data.items():
            val_type = type(value).__name__
            # 요소 개수나 문자열 길이 힌트 제공
            if isinstance(value, list):
                hint = f"List (len: {len(value)})"
            elif isinstance(value, dict):
                hint = f"Dict (keys: {list(value.keys())[:3]}...)"
            else:
                hint = f"{val_type} (val: {str(value)[:20]})"

            skeleton_lines.append(f"  ├── \"{key}\": {hint}")
            
            # 심볼 장부 등록용 문자열 적립
            symbols_info_strings.append(f"🔑 \"{key}\" [{val_type}]")
            
            # 5대 장부 중 1번 'symbols'에 개별 키를 심볼 ID로 정밀 바느질
            s_id = f"{rel_path_str}::{key}"
            symbols.append({
                "symbol_id": s_id, "name": key, "full_name": f"json.{key}", "type": "json_key",
                "path": rel_path_str, "start_line": 1, "end_line": 1,
                "calls": [], "used_by": []
            })
            # 정의 맵 매핑 등록
            definition_map[key] = f"{rel_path_str}:1"

    elif isinstance(data, list):
        skeleton_lines.append(f"  └── Root Array: List (len: {len(data)})")
        symbols_info_strings.append(f"📦 Root_Array [len: {len(data)}]")

    skeleton_text = "\n".join(skeleton_lines)

    # 3. 파일 한줄 요약 및 컨텍스트 바느질
    summary_parts = [f"💡 📦 json_keys: {len(symbols_info_strings)}개 포착"]
    summary_parts.extend(symbols_info_strings[:5]) # 너무 길어지면 끊기 (가독성 유지)
    if len(symbols_info_strings) > 5:
        summary_parts.append(f"...외 {len(symbols_info_strings)-5}개")
        
    symbols_summary_str = " | ".join(summary_parts)

    file_context[rel_path_str] = {
        "hash": file_hash,
        "symbols_summary": symbols_summary_str,
        "skeleton": skeleton_text
    }

    # 4. JSON 파일의 특정 네이밍이 들어올 때 데이터 프로토콜이나 레지스트리로 귀속해주는 유연성 필터
    file_name_lower = file_path.name.lower()
    if "protocol" in file_name_lower or "schema" in file_name_lower:
        # JSON 구조 자체를 데이터 프로토콜 레이아웃으로 복사 탑재
        if isinstance(data, dict):
            data_protocols[file_path.stem] = {k: type(v).__name__ for k, v in data.items()}
    elif "constant" in file_name_lower or "registry" in file_name_lower:
        registry_constants.append(f"JSON_CONFIG::{file_path.stem.upper()}")

    # 🤝 최종 5대 규격 튜플 리턴
    return symbols, file_context, definition_map, data_protocols, registry_constants