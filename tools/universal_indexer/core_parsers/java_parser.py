import hashlib
import re
from pathlib import Path

# 🎛️ 디버깅 로그 On/Off 마스터 스위치
DEBUG_LOG = True

def log(message: str):
    if DEBUG_LOG:
        print(f"📡 [Java-Parser Log] {message}")

def _find_matching_curly_brace(lines: list, start_line_idx: int) -> int:
    """
    자바의 중괄호 { } 쌍을 정밀 추적하여 메서드/클래스의 실제 종료 줄 번호(1-based)를 반환합니다.
    """
    brace_count = 0
    opened = False
    
    for idx in range(start_line_idx, len(lines)):
        line = lines[idx]
        # 주석 제거 후 블록 검사
        cleaned_line = re.sub(r'//.*|/\*.*?\*/', '', line)
        
        for char in cleaned_line:
            if char == '{':
                brace_count += 1
                opened = True
            elif char == '}':
                brace_count -= 1
                
        if opened and brace_count <= 0:
            return idx + 1  # 1-based line number
            
    return start_line_idx + 1

def extract_symbols(file_path: Path, project_root: Path):
    """
    ☕ [Java Core Advanced Parser v2.0]
    파이썬과 100% 동일한 5대 장부 규격을 만족하도록 자바 소스를 정밀 해부합니다.
    - 중첩 경로(src/src) 방어선 구축 완료
    - imp: 임포트 패키지 완벽 추출
    - calls: 메서드 내부 호출 분석 엔진 탑재
    - 줄 범위 (시작줄-끝줄) 매칭 완벽 지원
    """
    symbols = []
    file_context = {}
    definition_map = {}
    data_protocols = {}
    registry_constants = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        log(f"❌ 파일 읽기 실패: {file_path} | 에러: {e}")
        return symbols, {}, {}, {}, []

# 🚨 [교정] 독단적인 src/src/ 축약을 제거하고 실제 디스크 상대 경로 규격을 그대로 보존합니다.
    try:
        raw_rel = file_path.relative_to(project_root).as_posix()
    except ValueError:
        raw_rel = file_path.name

    # 별도의 치환 없이 디스크 실제 경로를 단일 진실 공급원(Single Source of Truth) 키값으로 확정
    rel_path_str = raw_rel

    file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    lines = content.splitlines()

    # 1. 🧲 임포트(Imports) 및 패키지 징집
    imports = []
    for line in lines:
        line_strip = line.strip()
        if line_strip.startswith("import ") and line_strip.endswith(";"):
            imp_target = line_strip.replace("import ", "").replace(";", "").strip()
            imports.append(imp_target)
            
    imports_str = f"💡 📦 imp: {', '.join(sorted(list(set(imports))))}" if imports else ""

    # 2. 🩻 클래스 및 메서드 심볼 다차원 스캔
    symbols_info_strings = []
    skeleton_segments = []
    
    current_class = None
    class_start_idx = -1

    # 자바 클래스/인터페이스/메서드 탐색 정규식
    class_patt = re.compile(r'(?:public|protected|private|static|\s)+\s+(?:class|interface|enum)\s+([a-zA-Z0-9_]+)')
    method_patt = re.compile(r'(?:public|protected|private|static|\s)+\s+[\w<>\s?\[\]]+\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*(?:throws\s+[\w\s,]+)?\s*\{?')

    for idx, line in enumerate(lines):
        line_num = idx + 1
        line_stripped = line.strip()
        
        # 주석이나 공백 라인은 스킵
        if line_stripped.startswith("//") or line_stripped.startswith("*") or not line_stripped:
            continue

        # A. 클래스 탐지
        class_match = class_patt.search(line)
        if class_match:
            c_name = class_match.group(1)
            current_class = c_name
            class_start_idx = idx
            end_line = _find_matching_curly_brace(lines, idx)
            
            symbols_info_strings.append(f"🧬 class {c_name} [L{line_num}-{end_line}]")
            skeleton_segments.append(f"class {c_name} {{ // L{line_num}-{end_line}")
            
            symbols.append({
                "symbol_id": f"{rel_path_str}::{c_name}",
                "name": c_name, "full_name": c_name, "type": "class",
                "path": rel_path_str, "start_line": line_num, "end_line": end_line,
                "calls": [], "used_by": []
            })
            definition_map[c_name] = f"{rel_path_str}:{line_num}"
            continue

# B. 메서드 탐지 및 인자(파라미터) 정밀 추출로 변경
        method_match = method_patt.search(line)
        if method_match and ("(" in line_stripped and "import " not in line_stripped):
            m_name = method_match.group(1)
            
            if m_name in ["if", "for", "while", "switch", "catch", "return"]:
                continue
                
            # 💡 [추가] 메서드 선언 전체 라인에서 괄호 ( ) 내부의 인자 정보만 파싱
            param_match = re.search(r'\((.*?)\)', line_stripped)
            params_str = ""
            if param_match:
                # 예: "String player, int score" -> "String, int" 형태로 타입만 콤팩트하게 정렬
                raw_params = param_match.group(1).strip()
                if raw_params:
                    # 공백 기준으로 나눠서 변수명은 버리고 타입명만 수집
                    param_types = [p.strip().split()[0] for p in raw_params.split(",") if p.strip()]
                    params_str = ", ".join(param_types)

            end_line = _find_matching_curly_brace(lines, idx)
            
            
            # 메서드 바디 본문 추출 (내부 호출 함수 파싱용)
            body_lines = lines[idx:end_line]
            body_text = "\n".join(body_lines)
            
            # 내부 호출 추적 (간이 자바 식별자 파서: 다른 함수명 호출부 스캔)
            possible_calls = re.findall(r'([a-zA-Z0-9_]+)\s*\(', body_text)
            detected_calls = [
                name for name in possible_calls 
                if name not in ["if", "for", "while", "switch", "catch", "synchronized", "super", "this", m_name]
            ]
            detected_calls = list(set(detected_calls))

            # =================================================================
            # 🎯 [수정 완료] 파이썬 규격과 완벽 동기화하여 줄 범위 [L시작-끝] 복원
            # =================================================================
            if current_class:
                m_id = f"{rel_path_str}::{current_class}.{m_name}"
                full_name = f"{current_class}.{m_name}"
                # ✅ [교정] 클래스 내부의 메서드 정보와 줄 범위를 정확하게 매핑합니다.
                symbols_info_strings.append(f"🎯 def {m_name}({params_str}) [L{line_num}-{end_line}]")
                skeleton_segments.append(f"    {line_stripped} // L{line_num}-{end_line}")
                def_key = full_name
            else:
                m_id = f"{rel_path_str}::{m_name}"
                full_name = m_name
                # ✅ [교정] 단독 메서드 정보와 줄 범위를 정확하게 매핑합니다.
                symbols_info_strings.append(f"🎯 def {m_name}({params_str}) [L{line_num}-{end_line}]")
                skeleton_segments.append(f"{line_stripped} // L{line_num}-{end_line}")
                def_key = m_name

            symbols.append({
                "symbol_id": m_id, "name": m_name, "full_name": full_name, "type": "method",
                "path": rel_path_str, "start_line": line_num, "end_line": end_line,
                "calls": detected_calls, "used_by": []
            })
            definition_map[def_key] = f"{rel_path_str}:{line_num}"

    # 3. 🧱 소스 스켈레톤 마감 처리
    skeleton_text = "\n".join(skeleton_segments)

    # 4. 🎚️ 파이썬 마스터 규격 한줄 요약 문자열 조립 완료
    summary_parts = [imports_str] if imports_str else []
    summary_parts.extend(symbols_info_strings)
    symbols_summary_str = " | ".join(summary_parts)

    file_context[rel_path_str] = {
        "hash": file_hash,
        "symbols_summary": symbols_summary_str,
        "skeleton": skeleton_text
    }

    log(f"✅ 자바 소스 스캔 완료 -> 경로: {rel_path_str} | 심볼: {len(symbols)}개 포착")
    return symbols, file_context, definition_map, data_protocols, registry_constants