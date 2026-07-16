import os
import ast
import json
from pathlib import Path

# ======================================================================
# 🎯 [경로 방어선 절대 고정]
# 현재 스크립트 파일(create_ai_map.py)의 위치는 무조건 프로젝트루트/cline_tools 입니다.
# 따라서 .parent는 cline_tools가 되고, 그 .parent가 진짜 프로젝트 마스터 루트입니다.
# ======================================================================
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent  # 🔥 상위의 진짜 프로젝트 루트 강제 추적

# 🚨 모든 로드 및 저장 경로를 '진짜 프로젝트 루트' 기준으로 완전 강제 고정
OUTPUT_FILE_PATH = PROJECT_ROOT / "AI_CODEBASE_MAP.md"
REGISTRY_JSON_PATH = PROJECT_ROOT / "registry_constants.json"
PROTOCOL_JSON_PATH = PROJECT_ROOT / "data_protocols.json"

def parse_python_file(file_path: Path):
    """[형님 원본 규격 100% 완벽 보존] 실시간으로 라인 범위, 클래스/함수, 임포트를 징집합니다."""
    compact_symbols_info = []
    imports = []
    global_vars = []
    structural_symbols = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        tree = ast.parse(content)
        
        for node in tree.body:
            # 1. 외부 모듈 임포트 추적
            if isinstance(node, (ast.Import, ast.ImportFrom)) :
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                else:
                    module_name = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module_name}.{alias.name}" if module_name else alias.name)
            
            # 2. 탑레벨 중요 전역 변수/상수 추적
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        global_vars.append(target.id)
                        
            # 3. 클래스 정의 및 내부 메서드 추적 (라인 범위 포함)
            elif isinstance(node, ast.ClassDef):
                class_start = node.lineno
                class_end = getattr(node, "end_lineno", class_start)
                class_info = f"🧬 class {node.name} [L{class_start}-{class_end}]"
                structural_symbols.append(class_info)
                
                # 내부 메서드 순회
                for sub_node in node.body:
                    if isinstance(sub_node, ast.FunctionDef):
                        func_start = sub_node.lineno
                        func_end = getattr(sub_node, "end_lineno", func_start)
                        
                        # 인자값(Arguments) 포착 및 가독성 압축 요약
                        args_list = [a.arg for a in sub_node.args.args]
                        # 가독성을 저해하는 self 제거 및 표현 정돈
                        if "self" in args_list:
                            args_list.remove("self")
                        args_str = ", ".join(args_list)
                        
                        func_info = f"   └─ def {sub_node.name}({args_str}) [L{func_start}-{func_end}]"
                        structural_symbols.append(func_info)
                        
            # 4. 단독 전역 함수 추적 (라인 범위 포함)
            elif isinstance(node, ast.FunctionDef):
                func_start = node.lineno
                func_end = getattr(node, "end_lineno", func_start)
                args_list = [a.arg for a in node.args.args]
                args_str = ", ".join(args_list)
                func_info = f"🎯 def {node.name}({args_str}) [L{func_start}-{func_end}]"
                structural_symbols.append(func_info)
                
        # 토큰 세이브를 위해 핵심만 간결하게 조립 후 송출
        if imports:
            # 중복 제거 및 유효 라이브러리 필터링
            clean_imports = sorted(list(set(imports)))[:6]  
            compact_symbols_info.append(f"💡 📦 imp: {', '.join(clean_imports)}")
        if structural_symbols:
            compact_symbols_info.extend(structural_symbols)
            
    except Exception as e:
        return [f"⚠️ [AST 파싱 실패]: {e}"]
        
    return compact_symbols_info


def main():
    # 🚨 [경로 교정] 무조건 진짜 프로젝트 마스터 루트 내부의 src 폴더를 정조준합니다.
    src_dir = PROJECT_ROOT / "src"
    
    if not src_dir.exists():
        print(f"❌ [오류] 소스코드 커널 디렉토리가 존재하지 않습니다: {src_dir}")
        return
        
    target_files = sorted(list(src_dir.glob("**/*.py")))
    print(f"🔍 [디버그] 스캔 타깃 파이썬 파일 수집 완료: 총 {len(target_files)}개 탐색됨")
    
    # 레지스트리 및 프로토콜 데이터 연동 사전 로드
    path_to_registry = {}
    if REGISTRY_JSON_PATH.exists():
        try:
            with open(REGISTRY_JSON_PATH, "r", encoding="utf-8") as f:
                reg_data = json.load(f)
                for reg_const, info in reg_data.items():
                    file_rel = info.get("file")
                    if file_rel:
                        # 통일성 유지를 위해 posix 슬래시 형태로 관리
                        posix_path = Path(file_rel).as_posix()
                        if posix_path not in path_to_registry:
                            path_to_registry[posix_path] = []
                        path_to_registry[posix_path].append(reg_const)
        except Exception:
            pass
            
    path_to_protocol = {}
    if PROTOCOL_JSON_PATH.exists():
        try:
            with open(PROTOCOL_JSON_PATH, "r", encoding="utf-8") as f:
                proto_data = json.load(f)
                for proto_name, info in proto_data.items():
                    file_rel = info.get("file")
                    fields = info.get("fields", {})
                    if file_rel:
                        posix_path = Path(file_rel).as_posix()
                        path_to_protocol[posix_path] = (proto_name, fields)
        except Exception:
            pass

    # 🚨 무조건 프로젝트 마스터 루트 최상단에 마스터 장부 생성 강제
    # 🚨 무조건 프로젝트 마스터 루트 최상단에 마스터 장부 생성 강제
    if OUTPUT_FILE_PATH.exists():
        try:
            OUTPUT_FILE_PATH.unlink()
        except Exception:
            pass

    with open(OUTPUT_FILE_PATH, "w", encoding="utf-8", newline="") as f:
        f.write("# 🏗️ AI-OPTIMIZED ULTRA COMPACT CODEBASE MAP (INTELLIGENT SCAN)\n\n")
        f.write("> **[AI 프로토콜 매뉴얼]** 이 문서는 다른 AI 비서들의 경로 오해를 차단하기 위해 파일마다 **실제 하드디스크 상대 경로 `[📂 실제경로]`**를 강제 명시해 둔 특수 지도입니다.\n")
        f.write("> AI 비서는 절대 눈치로 경로를 추측하지 말고, 파일명 뒤에 박혀있는 `[📂 실제경로]` 규격을 그대로 복사하여 agent_navigator를 호출하십시오.\n\n")
        
        f.write("```markdown\n")
        f.write("project_root/\n")
        
        printed_dirs = set()
        
        for file_path in target_files:
            # 🚨 PROJECT_ROOT 기준의 정확한 상대경로 계산
            rel_path = file_path.relative_to(PROJECT_ROOT)
            parts = rel_path.parts
            
            # 파일이 위치한 부모 폴더 트리 선제 렌더링
            for i in range(1, len(parts)):
                current_dir_parts = parts[:i]
                current_dir_path = Path(*current_dir_parts)
                
                if current_dir_path not in printed_dirs:
                    dir_indent = "│   " * (i - 1)
                    f.write(f"{dir_indent}├── {parts[i-1]}/\n")
                    printed_dirs.add(current_dir_path)
            
            indent = "│   " * (len(parts) - 1)
            file_name = parts[-1]
            posix_rel_path = rel_path.as_posix()
            
            symbols_info = parse_python_file(file_path)
            symbols_str = " | ".join(symbols_info) if symbols_info else ""
            
            # 1. 파일 이름 및 원본 심볼 한 줄로 출력
            if symbols_str:
                f.write(f"{indent}├── {file_name} [📂 {posix_rel_path}] -> [{symbols_str}]\n")
            else:
                f.write(f"{indent}├── {file_name} [📂 {posix_rel_path}]\n")
            
            # 2. 하단 서브 트리에 상숫값 레지스트리 명시 정보 결합
            if posix_rel_path in path_to_registry:
                for reg_const in path_to_registry[posix_rel_path]:
                    f.write(f"{indent}│     ├── 🔑 [REGISTRY]: \"{reg_const}\"\n")
                    
            # 3. 하단 서브 트리에 정밀 데이터 변수 프로토콜 스펙 결합
            if posix_rel_path in path_to_protocol:
                proto_name, fields = path_to_protocol[posix_rel_path]
                f.write(f"{indent}│     ├── 📊 [PROTOCOL]: \"{proto_name}\"\n")
                field_items = [f"{k}({v.replace(' (기본값: ', ':').replace(')', '')})" for k, v in fields.items()]
                chunks = [field_items[x:x+4] for x in range(0, len(field_items), 4)]
                for chunk in chunks:
                    f.write(f"{indent}│     │     ├── {', '.join(chunk)}\n")
                    
        f.write("```\n")
        
    print(f"🎯 [마스터 공장] 'AI_CODEBASE_MAP.md'가 {len(target_files)}개의 규격으로 안전하게 프로젝트 루트에 자동 갱신되었습니다 형님!")


# ======================================================================
# 🔗 [파이프라인 결합 방어선] 
# 백그라운드 감시망(jjap_watcher.py)이 호출하는 함수명을 완벽하게 지원하기 위한 브릿지 래퍼 함수
# ======================================================================
def generate_ai_optimized_map():
    """jjap_watcher.py의 실시간 갱신 요청을 수신하여 내부 메인 공장을 가동합니다."""
    main()


if __name__ == "__main__":
    main()