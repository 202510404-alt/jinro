import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

# 🎛️ [절대 규칙 2번] 원터치 디버깅 로그 스위치
DEBUG_MODE = True # INFO: True로 두시면 어떤 심볼을 낚아채고 수술하는지 터미널에 100% 자백합니다.

class JjapRetriever:
    """
    Roo Code를 위한 Context Surgeon V2.
    1. Exact Match 우선 탐색 (Disambiguation 해결)
    2. 라인 단위 Truncation (코드 파손 방지)
    3. 엄격한 스키마 계약 (Indexer V2 전제)
    """
    def __init__(self, project_root: Path):
        self.project_root = project_root
        # 🧠 [불러오기 교정] 격리 폴더(system_memory) 안으로 이사 간 인덱싱 장부를 정확하게 바라보도록 관로를 꺾어줍니다.
        self.symbols_file = self.project_root / "system_memory" / ".jjap_symbols.json"
        self.max_context_lines = 300
        self.symbols_db = self._load_symbols()

    def _load_symbols(self) -> List[Dict[str, Any]]:
        if self.symbols_file.exists():
            try:
                with open(self.symbols_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    symbols = data.get("symbols", [])
                    if DEBUG_MODE:
                        print(f"📦 [Retriever 디버그] 인덱싱 장부 로드 완료! (총 {len(symbols)}개 심볼 탑재됨)")
                    return symbols
            except Exception as e:
                print(f"⚠️ [Retriever 에러] 스키마 로드 실패: {e}")
        else:
            if DEBUG_MODE:
                print(f"⚠️ [Retriever 디버그] 장부 파일이 없습니다: {self.symbols_file}")
        return []

    def retrieve_symbol(self, query: str) -> str:
        """심볼 검색 및 정밀 문맥 조립"""
        if DEBUG_MODE:
            print(f"📡 [Retriever 디버그] 수술 쿼리 수신: '{query}'")

        # [지피티 지적 1 해결] 심볼 식별 최적화 (Exact -> Partial -> Fallback)
        target = self._find_best_match(query)
        
        if not target:
            if DEBUG_MODE:
                print(f"❌ [Retriever 디버그] 매칭 실패 -> 장부에서 '{query}'를 찾지 못함")
            return f"❌ '{query}'와 일치하는 심볼을 찾을 수 없습니다. (ID 또는 Name을 확인하세요)"

        file_rel_path = target.get('file')
        file_path = self.project_root / file_rel_path
        
        if DEBUG_MODE:
            print(f"🎯 [Retriever 디버그] 타깃 징집 성공! 심볼ID: {target['symbol_id']} ➡️ 타깃 파일: {file_rel_path}")

        if not file_path.exists():
            return f"❌ 파일을 찾을 수 없습니다: {file_rel_path}"

        with open(file_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()

        # [Surgery 시작]
        context = []
        context.append(f"### [RETRIEVED CONTEXT: {target['symbol_id']}] ###")
        
        # 1. Imports (상단 50줄)
        context.append("\n# --- Imports ---")
        imports = [line.strip() for line in all_lines[:50] if line.strip().startswith(('import ', 'from '))]
        context.extend(imports)
        context.append("    ...")
        if DEBUG_MODE:
            print(f"🧹 [Retriever 디버그] 상단 공통 Import {len(imports)}줄 추출 완료")

        # 2. Parent Context (Class Header)
        if target.get('parent'):
            parent = next((s for s in self.symbols_db if s['name'] == target['parent'] and s['file'] == target['file']), None)
            if parent:
                p_start = parent['range'][0]
                context.append(f"\n# --- Class: {target['parent']} ---")
                context.append(all_lines[p_start-1].rstrip())
                context.append("    \"\"\" (Internal methods hidden) \"\"\"")
                if DEBUG_MODE:
                    print(f"🧱 [Retriever 디버그] 부모 클래스 뼈대 '{target['parent']}' 바느질 바인딩")

        # 3. Target Snippet (Range 준수)
        start, end = target['range']
        context.append(f"\n# --- Target: {target['name']} (Lines {start}-{end}) ---")
        
        # 인덱스 범위 안전하게 가져오기
        snippet = all_lines[max(0, start-1) : min(len(all_lines), end)]
        context.extend([line.rstrip() for line in snippet])
        if DEBUG_MODE:
            print(f"✂️ [Retriever 디버그] 정밀 문맥 수술실(Surgeon) 작동 완료 ({start}~{end} 라인 발췌)")

        # [지피티 지적 2 해결] 라인 단위 안전 절삭
        return self._safe_truncate("\n".join(context))

    def _find_best_match(self, query: str) -> Optional[Dict]:
        """심볼 중복 문제를 해결하기 위한 매칭 로직"""
        # 1. symbol_id 완전 일치 (가장 정확)
        for s in self.symbols_db:
            if s.get('symbol_id') == query: 
                if DEBUG_MODE: print(f"🔍 [Retriever 디버그] 1순위 완전 매칭성공 (Symbol ID): {query}")
                return s
        # 2. name 완전 일치
        for s in self.symbols_db:
            if s.get('name') == query: 
                if DEBUG_MODE: print(f"🔍 [Retriever 디버그] 2순위 명칭 매칭성공 (Name): {query}")
                return s
        # 3. 부분 일치 (Fallback)
        for s in self.symbols_db:
            if query.lower() in s.get('name', '').lower(): 
                if DEBUG_MODE: print(f"🔍 [Retriever 디버그] 3순위 느슨한 부분 매칭성공: {s.get('name')}")
                return s
        return None

    def _safe_truncate(self, text: str) -> str:
        """문자열 단위가 아닌 라인 단위로 끊어서 코드 파손 방지"""
        lines = text.splitlines()
        if len(lines) <= self.max_context_lines:
            return text
        
        if DEBUG_MODE:
            print(f"⚠️ [Retriever 디버그] 경고: 컨텍스트가 한계선({self.max_context_lines}줄)을 초과하여 꼬리 절단단행!")
        truncated = lines[:self.max_context_lines]
        truncated.append("\n... [⚠️ WARNING: Context truncated by line limit to protect token budget] ...")
        return "\n".join(truncated)


def main():
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    if not query:
        print("💡 Usage: python cline_tools/jjap_retriever.py <symbol_id_or_name>")
        return
    
    retriever = JjapRetriever(Path.cwd())
    print(retriever.retrieve_symbol(query))

if __name__ == "__main__":
    main()