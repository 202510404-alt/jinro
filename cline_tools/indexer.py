import ast
import json
import hashlib
import os
from pathlib import Path
from typing import Dict, Any, List

class AdvancedIndexerV2:
    """
    [Jjap-Cursor Core Indexer V3.5 - Ultra Universal Engine]
    
    🛠️ 형님의 무제한 범용성 계약 조건 완벽 반영:
      - 특정 폴더 제한 완전 철폐! src/ 내부의 모든 파이썬 파일을 알아서 정밀 센싱합니다.
      - 파일 내부에 'Variables'나 'vars'가 들어간 클래스가 있으면 데이터 프로토콜 장부로 자동 분류.
      - 그 외에 일반적인 엔티티, 플랫폼, 카메라 등의 모든 핵심 클래스는 레지스트리 상수로 100% 자동 징집.
    """
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.symbols: List[Dict[str, Any]] = []
        self.files_context: Dict[str, Any] = {}
        self.definition_map: Dict[str, str] = {}
        
        # 🎯 [보조 지식 장부 변수]
        self.data_protocols: Dict[str, Any] = {}
        self.registry_constants: Dict[str, str] = {}

    def _get_sha256(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _extract_skeleton(self, content: str) -> str:
        try:
            tree = ast.parse(content)
            skeleton_lines = []
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    skeleton_lines.append(f"class {node.name}:")
                    for sub_node in node.body:
                        if isinstance(sub_node, ast.FunctionDef):
                            skeleton_lines.append(f"    def {sub_node.name}(...):")
                            skeleton_lines.append(f"        ...")
                elif isinstance(node, ast.FunctionDef):
                    skeleton_lines.append(f"def {node.name}(...):")
                    skeleton_lines.append(f"    ...")
            return "\n".join(skeleton_lines)
        except Exception:
            return ""

    def parse_protocols_and_registries(self, content: str, rel_path_str: str):
        """[범용성 자동 지능 엔진] 하드코딩 없이 클래스의 성격을 파악하여 장부에 자동 분배"""
        try:
            tree = ast.parse(content)
            for node in tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue

                # 🛡️ 1. 데이터 프로토콜 스캔: 이름에 Variables 또는 vars가 들어가면 데이터 명세서로 징집
                if "Variables" in node.name or "vars" in node.name.lower():
                    fields = {}
                    for sub_node in node.body:
                        if isinstance(sub_node, ast.FunctionDef) and sub_node.name == "__init__":
                            for stmt in sub_node.body:
                                if isinstance(stmt, ast.Assign):
                                    for target in stmt.targets:
                                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                                            val_str = "Unknown"
                                            if isinstance(stmt.value, ast.Constant):
                                                val_str = f"{type(stmt.value.value).__name__} (기본값: {stmt.value.value})"
                                            fields[target.attr] = val_str
                    
                    self.data_protocols[node.name] = {
                        "defined_in": rel_path_str,
                        "fields": fields
                    }
                
                # 🧱 2. 범용 레지스트리 상수 스캔: 폴더 불문! 모든 핵심 구동 클래스(플랫폼, 플레이어, 적 등)를 상수로 맵핑
                else:
                    # 마스터 실행 스위치류나 내장 클래스를 제외한 모든 커스텀 클래스를 상수로 추출
                    if node.name not in ["AppState"]:
                        self.registry_constants[node.name] = f"{rel_path_str}::{node.name}"
                        
        except Exception:
            pass

    def index_file(self, file_path: Path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return

        rel_path = file_path.relative_to(self.project_root)
        rel_path_str = rel_path.as_posix()

        file_hash = self._get_sha256(content)
        skeleton = self._extract_skeleton(content)
        self.files_context[rel_path_str] = {
            "hash": file_hash,
            "mtime": int(file_path.stat().st_mtime),
            "skeleton": skeleton
        }

        # 동적 분배기 기동
        self.parse_protocols_and_registries(content, rel_path_str)

        try:
            tree = ast.parse(content)
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    class_id = f"{rel_path_str}::{node.name}"
                    self.definition_map[node.name] = f"{rel_path_str}:{node.lineno}"
                    end_lineno = getattr(node, "end_lineno", node.lineno)
                    
                    self.symbols.append({
                        "symbol_id": class_id, "full_name": node.name, "name": node.name,
                        "type": "class", "parent": None, "file": rel_path_str,
                        "start_line": node.lineno, "end_line": end_lineno, "range": [node.lineno, end_lineno],
                        "decorators": [ast.dump(d) for d in node.decorator_list], "signature": f"class {node.name}",
                        "calls": [], "used_by": []
                    })
                    
                    for sub in node.body:
                        if isinstance(sub, ast.FunctionDef):
                            method_id = f"{class_id}.{sub.name}"
                            self.definition_map[f"{node.name}.{sub.name}"] = f"{rel_path_str}:{sub.lineno}"
                            sub_end_lineno = getattr(sub, "end_lineno", sub.lineno)
                            
                            calls = []
                            for expr in ast.walk(sub):
                                if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name):
                                    calls.append(expr.func.id)
                                elif isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute):
                                    calls.append(expr.func.attr)

                            self.symbols.append({
                                "symbol_id": method_id, "full_name": f"{node.name}.{sub.name}", "name": sub.name,
                                "type": "method", "parent": node.name, "file": rel_path_str,
                                "start_line": sub.lineno, "end_line": sub_end_lineno, "range": [sub.lineno, sub_end_lineno],
                                "decorators": [ast.dump(d) for d in sub.decorator_list], "signature": f"def {sub.name}(...)",
                                "calls": list(set(calls)), "used_by": []
                            })
                            
                elif isinstance(node, ast.FunctionDef):
                    func_id = f"{rel_path_str}::{node.name}"
                    self.definition_map[node.name] = f"{rel_path_str}:{node.lineno}"
                    func_end_lineno = getattr(node, "end_lineno", node.lineno)
                    
                    self.symbols.append({
                        "symbol_id": func_id, "full_name": node.name, "name": node.name,
                        "type": "function", "parent": None, "file": rel_path_str,
                        "start_line": node.lineno, "end_line": func_end_lineno, "range": [node.lineno, func_end_lineno],
                        "decorators": [ast.dump(d) for d in node.decorator_list], "signature": f"def {node.name}(...)",
                        "calls": [], "used_by": []
                    })
        except Exception:
            pass

    def scan_project(self):
        src_folder = self.project_root / "src"
        if not src_folder.exists():
            print("⚠️ [Indexer] 프로젝트 루트 내에 'src' 폴더를 찾을 수 없어 스캔을 중단합니다.")
            return

        for root, dirs, files in os.walk(src_folder):
            if any(kw in root for kw in [".venv", ".git", "__pycache__", "cline_tools"]):
                continue
            for file in files:
                if file == "start.py":
                    continue
                if file.endswith(".py"):
                    self.index_file(Path(root) / file)

        for s in self.symbols:
            name_to_check = s["name"]
            for target in self.symbols:
                if name_to_check in target.get("calls", []) and s["symbol_id"] != target["symbol_id"]:
                    s["used_by"].append(target["symbol_id"])
            s["used_by"] = sorted(list(set(s["used_by"])))

        # 덮어쓰기 출력 일괄 동기화
        with open(".jjap_context.json", "w", encoding="utf-8") as f:
            json.dump({"files": self.files_context}, f, indent=2, ensure_ascii=False)
        with open(".jjap_symbols.json", "w", encoding="utf-8") as f:
            json.dump({"symbols": self.symbols}, f, indent=2, ensure_ascii=False)
        with open("definition_map.json", "w", encoding="utf-8") as f:
            json.dump(self.definition_map, f, indent=2, ensure_ascii=False)
        with open("data_protocols.json", "w", encoding="utf-8") as f:
            json.dump({"protocols": self.data_protocols}, f, indent=2, ensure_ascii=False)
        with open("registry_constants.json", "w", encoding="utf-8") as f:
            json.dump({"registered_entities": self.registry_constants}, f, indent=2, ensure_ascii=False)

        print("🧬 [Jjap-Indexer Universal] 폴더 제한 해제! 전 구역 자동 분류 및 5대 장부 오버라이트 완료!")

if __name__ == "__main__":
    root = Path(__file__).parent.resolve()
    indexer = AdvancedIndexerV2(root)
    indexer.scan_project()