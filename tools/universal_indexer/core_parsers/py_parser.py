import ast
import hashlib
from pathlib import Path

def extract_symbols(file_path: Path, project_root: Path):
    """
    🐍 [Python Core Parser v1.0]
    기존 indexer.py 내부의 순정 파이썬 AST 스캔, 스켈레톤 추출, 레지스트리/프로토콜 징집 로직을
    단 하나의 약속된 마스터 함수 구조로 완벽 격리 이사 완료했습니다 형님!
    
    리턴값: (symbols_list, file_context_dict, definition_map_dict, data_protocols_dict, registry_constants_dict)
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
        # 파일 읽기 실패 시 빈 규격 레이아웃으로 안전 패스
        return symbols, {}, {}, {}, []

    rel_path_str = file_path.relative_to(project_root).as_posix()
    file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    try:
        root = ast.parse(content)
    except SyntaxError:
        # 문법 에러 파일 방어선
        return symbols, {}, {}, {}, []

    # 1. 🧱 스켈레톤(뼈대) 소스 정밀 요약
    lines = content.splitlines()
    skeleton_lines = []
    for node in root.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            start_idx = node.lineno - 1
            end_idx = min(node.end_lineno, len(lines)) if getattr(node, "end_lineno", None) else start_idx + 1
            skeleton_lines.extend(lines[start_idx:end_idx])
            skeleton_lines.append("")
    skeleton_text = "\n".join(skeleton_lines)

    # 2. 🧬 내부 상호 호출 관계 자백용 1차 지도 빌드
    func_lines = {}
    for node in ast.walk(root):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_lines[node.name] = (node.lineno, node.end_lineno)
        elif isinstance(node, ast.ClassDef):
            func_lines[node.name] = (node.lineno, node.end_lineno)

    # 3. 🔑 레지스트리 & 프로토콜 징집 레이더 가동
    for node in root.body:
        if isinstance(node, ast.ClassDef):
            has_vars = False
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and (target.id == "vars" or "variables" in target.id.lower()):
                            has_vars = True
            
            if has_vars:
                # 데이터 프로토콜 장부 등록
                fields = {}
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id != "vars":
                                if isinstance(item.value, ast.Constant):
                                    fields[target.id] = f"{type(item.value.value).__name__} (기본값: {item.value.value})"
                                else:
                                    fields[target.id] = "Any"
                data_protocols[node.name] = fields
            else:
                # 일반 핵심 클래스는 레지스트리 상수로 귀속
                KEYWORDS = ["entity", "platform", "camera", "sensor", "agent", "navigator", "indexer", "retriever", "handler"]
                if any(kw in node.name.lower() for kw in KEYWORDS):
                    registry_constants.append(node.name)

    # 4. 🎯 클래스/메서드/함수 트리 구조 정밀 추적 및 심볼 바느질
    symbols_info_strings = []
    
    # 탑레벨 함수/클래스 1차 등록
    for node in root.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            s_name = node.name
            s_id = f"{rel_path_str}::{s_name}"
            symbols_info_strings.append(f"🎯 def {s_name}() [L{node.lineno}-{node.end_lineno}]")
            
            calls = []
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                    if child.func.id in func_lines and child.func.id != s_name:
                        calls.append(child.func.id)
            
            symbols.append({
                "symbol_id": s_id, "name": s_name, "full_name": s_name, "type": "function",
                "path": rel_path_str, "start_line": node.lineno, "end_line": node.end_lineno,
                "calls": list(set(calls)), "used_by": []
            })
            definition_map[s_name] = f"{rel_path_str}:{node.lineno}"

        elif isinstance(node, ast.ClassDef):
            c_name = node.name
            c_id = f"{rel_path_str}::{c_name}"
            symbols_info_strings.append(f"🧬 class {c_name} [L{node.lineno}-{node.end_lineno}]")
            
            symbols.append({
                "symbol_id": c_id, "name": c_name, "full_name": c_name, "type": "class",
                "path": rel_path_str, "start_line": node.lineno, "end_line": node.end_lineno,
                "calls": [], "used_by": []
            })
            definition_map[c_name] = f"{rel_path_str}:{node.lineno}"

            # 클래스 내부 메서드 슬라이싱
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    m_name = sub.name
                    m_id = f"{rel_path_str}::{c_name}.{m_name}"
                    symbols_info_strings.append(f"    └─ def {m_name}() [L{sub.lineno}-{sub.end_lineno}]")
                    
                    sub_calls = []
                    for child in ast.walk(sub):
                        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                            if child.func.id in func_lines and child.func.id != m_name:
                                sub_calls.append(child.func.id)
                    
                    symbols.append({
                        "symbol_id": m_id, "name": m_name, "full_name": f"{c_name}.{m_name}", "type": "method",
                        "path": rel_path_str, "start_line": sub.lineno, "end_line": sub.end_lineno,
                        "calls": list(set(sub_calls)), "used_by": []
                    })
                    definition_map[f"{c_name}.{m_name}"] = f"{rel_path_str}:{sub.lineno}"

    # 임포트 내역 파싱
    imports = []
    for node in ast.walk(root):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    imports_str = f"💡 📦 imp: {', '.join(sorted(list(set(imports))))}" if imports else ""

    # 최종 한줄 요약 문자열 조립
    summary_parts = [imports_str] if imports_str else []
    summary_parts.extend(symbols_info_strings)
    symbols_summary_str = " | ".join(summary_parts)

    file_context[rel_path_str] = {
        "hash": file_hash,
        "symbols_summary": symbols_summary_str,
        "skeleton": skeleton_text
    }

    return symbols, file_context, definition_map, data_protocols, registry_constants