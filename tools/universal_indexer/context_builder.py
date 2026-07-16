"""Context Builder module for Cline Tools.

[AI 배송용 컨텍스트 최적화 비서]
이 파일은 형님이 저(Gemini)에게 소스코드를 긁어서 보내기 직전에, 
메모리 상에서 코드를 한 줄씩 검열하여 토큰(비용)을 절약하고 
과거 오류 수정 내역만 핀포인트로 전달하는 '필터링 및 압축' 실무 도구입니다.
"""

import os
from pathlib import Path


class ContextBuilder:
    """날것의 소스코드를 정화하여 AI가 가장 좋아하는 영양가 있는 형태로 가공하는 비서 클래스입니다."""

    def __init__(self, project_root: str) -> None:
        """비서관을 초기화하며 기준이 되는 프로젝트 루트 경로를 지정합니다."""
        self.project_root = Path(project_root)

    def read_and_clean_file(self, relative_path: str) -> str:
        """파일을 읽어서 사람용 주석(# INFO:) 내용은 완전히 비우되,
        줄바꿈과 콤팩트한 줄 번호 태그만 강제로 남겨서 토큰을 최소화하고
        AI와 인간의 라인 인덱스를 100% 동기화하는 개조 함수입니다.
        """
        file_path = self.project_root / relative_path
        
        if not file_path.exists():
            raise FileNotFoundError(f"요청하신 경로에 파일이 존재하지 않습니다: {relative_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        cleaned_lines = []
        in_multiline_comment = False

        # enumerate를 사용해 파일 원본의 물리적인 줄 번호(1부터 시작)를 정확히 추적합니다.
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()

            # 1. 다중행 주석(""") 처리 블록
            if stripped.startswith('"""') or stripped.endswith('"""'):
                if '"""' in stripped and len(stripped) > 3:
                    pass 
                else:
                    in_multiline_comment = not in_multiline_comment
                    # 토큰 최소화: 라벨과 원본 줄바꿈만 남김
                    cleaned_lines.append(f"[{idx:03d}]\n")
                    continue

            if in_multiline_comment:
                # 다중행 주석 내부도 토큰 절약을 위해 내용을 비우고 줄만 유지
                cleaned_lines.append(f"[{idx:03d}]\n")
                continue

            # ⭐ 형님의 핵심 지시사항: 주석 부분은 내용을 비운 채 억지로 줄 표시를 유지!
            # 2. # INFO: 로 시작하는 주석행 처리
            if stripped.startswith("# INFO:"):
                # 💡 핵심: 긴 주석 텍스트를 다 날려버리고 오직 줄 번호 태그와 개행만 주입 (토큰 최소화!)
                cleaned_lines.append(f"[{idx:03d}]\n")
                continue

            # 3. 코드 옆에 붙은 꼬리표 주석 예외 처리 (`x = 1  # INFO: ...`)
            if " # INFO:" in line:
                # 주석 내용만 잘라내고, 코드 앞단에 줄 번호를 붙여서 재조립
                pure_code = line.split(" # INFO:")[0]
                cleaned_lines.append(f"[{idx:03d}]{pure_code}\n")
                continue

            # 4. 일반 빈 줄 처리
            if not stripped:
                cleaned_lines.append(f"[{idx:03d}]\n")
                continue

            # 5. 그 외의 순수 실행 코드 및 보존 주석 (# HISTORY:, # FIX:)
            # AI가 토큰을 해석할 때 밀리지 않도록 고정형 태그를 맨 앞에 강제 주입합니다.
            cleaned_lines.append(f"[{idx:03d}]{line}")

        return "".join(cleaned_lines)

    def assemble_ai_prompt(self, user_query: str, affected_files: list[str]) -> str:
        """검열된 파일 소스코드들과 형님의 최종 질문을 엮어서 저(Gemini)에게 배송할 최종 프롬프트 보따리를 조립합니다.
        
        🛠️ 내가 내부에서 부려먹는 함수:
          - `self.read_and_clean_file()`: 각 파일들을 돌면서 `# INFO:` 주석을 청소하라고 지시함.
        """
        prompt_parts = []
        prompt_parts.append(f"=== USER REQUEST ===\n{user_query}\n\n")
        prompt_parts.append("=== CLEANED CONTEXT CODEBASE ===\n")
        prompt_parts.append("아래 소스코드들은 토큰 절약을 위해 불필요한 설명 주석(# INFO:)이 제거되고, ")
        prompt_parts.append("과거 오류 수정 내역(# HISTORY:)만 온전히 보존된 청정 코드입니다.\n\n")

        for rel_path in affected_files:
            # 🛡️ [격리 방어선] 장부 보관소(system_memory) 및 마스터 지도(system_maps) 내부 파일은 컨텍스트 수집 대상에서 완전 무시
            if "system_memory" in str(rel_path) or "system_maps" in str(rel_path):
                continue

            prompt_parts.append(f"--- FILE: {rel_path} ---")
            try:
                # 위에 만들어 둔 청소 함수를 실행시켜 알짜배기 코드만 받아옵니다.
                purified_code = self.read_and_clean_file(rel_path)
                prompt_parts.append(purified_code)
            except Exception as e:
                prompt_parts.append(f"파일을 읽는 중 오류 발생: {str(e)}")
            prompt_parts.append("\n")

        # 최종적으로 저(Gemini)의 뇌세포로 들어올 텍스트 보따리가 완성되는 순간입니다.
        return "\n".join(prompt_parts)