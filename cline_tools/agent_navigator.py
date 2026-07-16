import json
import sys
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

# =====================================================================
# 🧠 CORE INTELLIGENCE: MULTI-TARGET CODE SLICE LOADER
# =====================================================================
class SemanticNavigator:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.symbols_path = root_dir / ".jjap_symbols.json"
        self.symbols_data = self._load_database()

    def _load_database(self):
        if not self.symbols_path.exists():
            return {"symbols": []}
        try:
            with open(self.symbols_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"symbols": []}

    def extract_multi_slices(self, raw_prompt: str):
        """
        [Multi-Target Protocol Parser]
        형님이 입력한 프롬프트에서 '파일경로:시작줄-끝줄' 또는 '파일경로:줄번호' 규격을 
        정규식으로 전부 추출하여, 요청된 순서대로 코드를 줄줄이 엮어서 반환합니다.
        
        ➕ 플러스 알파 (+α): 사용자가 요청한 구역 내의 심볼을 탐지하고, 
        이를 호출해서 사용하는(used_by) 전역 파일들의 함수부까지 자동으로 연쇄 슬라이싱하여 결합합니다.
        """
        pattern = r"([a-zA-Z0-9_\-\./]+)\s*:\s*(\d+)(?:\s*-\s*(\d+))?"
        matches = re.findall(pattern, raw_prompt)

        if not matches:
            return []

        extracted_slices = []
        req_num = 1

        for match in matches:
            file_rel_path = match[0].strip()
            start_line = int(match[1])
            end_line = int(match[2]) if match[2] else start_line

            # 1. 메인 타겟 파일 슬라이싱 추출
            target_file_path = self.root_dir / file_rel_path
            if not target_file_path.exists():
                continue

            try:
                with open(target_file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                # IndexError 방어망 구축 (줄 범위 안전 보정)
                total_lines = len(lines)
                safe_start = max(1, min(start_line, total_lines))
                safe_end = max(safe_start, min(end_line, total_lines))

                slice_lines = lines[safe_start - 1 : safe_end]
                slice_code = "".join(slice_lines)

                # 메인 슬라이스 저장
                extracted_slices.append({
                    "req_num": f"{req_num}",
                    "file": file_rel_path,
                    "line_range": f"{safe_start}-{safe_end}",
                    "code": slice_code
                })

                # 🔗 플러스 알파 (+α) 의존성 추적 가동
                # 슬라이싱된 텍스트 안에서 정의되거나 사용되는 함수/클래스 명칭 식별하여 used_by 연쇄 징집
                for s in self.symbols_data.get("symbols", []):
                    if s.get("file") == file_rel_path:
                        # 심볼의 라인이 추출 구역 내에 겹치는지 체크
                        s_start = s.get("start_line", 0)
                        s_end = s.get("end_line", 0)
                        if (safe_start <= s_start <= safe_end) or (safe_start <= s_end <= safe_end):
                            # 나를 부르는 곳(used_by) 연쇄 기습 징집
                            for ub_id in s.get("used_by", []):
                                # ub_id 양식 예: "src/map_system/map_engine.py::update"
                                if "::" in ub_id:
                                    ub_file, ub_symbol_name = ub_id.split("::", 1)
                                    # 해당 파일의 심볼 실제 구역 추적
                                    for target_s in self.symbols_data.get("symbols", []):
                                        if target_s.get("file") == ub_file and target_s.get("name") == ub_symbol_name:
                                            ub_file_path = self.root_dir / ub_file
                                            if ub_file_path.exists():
                                                with open(ub_file_path, "r", encoding="utf-8") as ubf:
                                                    ub_lines = ubf.readlines()
                                                ubs_start = target_s.get("start_line", 1)
                                                ubs_end = target_s.get("end_line", len(ub_lines))
                                                
                                                # 안전 보정 및 추출
                                                ubs_start = max(1, min(ubs_start, len(ub_lines)))
                                                ubs_end = max(ubs_start, min(ubs_end, len(ub_lines)))
                                                
                                                ub_slice_code = "".join(ub_lines[ubs_start - 1 : ubs_end])
                                                
                                                # 중복 징집 방지
                                                if not any(x["file"] == ub_file and x["line_range"] == f"{ubs_start}-{ubs_end}" for x in extracted_slices):
                                                    extracted_slices.append({
                                                        "req_num": f"{req_num} 🔗 의존성연동 ({s.get('name')} 호출부 -> {ub_file}의 [{ub_symbol_name}])",
                                                        "file": ub_file,
                                                        "line_range": f"{ubs_start}-{ubs_end}",
                                                        "code": ub_slice_code
                                                    })

            except Exception as e:
                print(f"⚠️ 슬라이싱 추출 실패 ({file_rel_path}): {e}")

            req_num += 1

        return extracted_slices

# =====================================================================
# 🎨 GUI INTERFACE LAYER (UPGRADED VERSION)
# =====================================================================
class JjapCursorNavigatorGUI:
    def __init__(self, root, project_root: Path):
        self.root = root
        self.project_root = project_root
        self.navigator = SemanticNavigator(project_root)
        self.last_markdown_content = "" # 외부 파일 저장용 임시 보관소

        self.root.title("⚡ Jjap-Cursor Agent Navigator v2.0 (Auto-Exporter)")
        self.root.geometry("1000x750")

        # 메인 레이아웃 분할
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 1. 상단 프롬프트 입력창 구역
        input_label = ttk.Label(self.main_container, text="📥 [에이전트 요청 프롬프트 입력 구역]", font=("Malgun Gothic", 11, "bold"))
        input_label.pack(anchor=tk.W, pady=(0, 5))

        self.prompt_input = tk.Text(self.main_container, height=6, font=("Malgun Gothic", 10))
        self.prompt_input.pack(fill=tk.X, pady=(0, 10))
        self.prompt_input.insert(tk.END, "💡 실전 테스트 양식 예시:\nsrc/player/player_main.py:45-75")

        # 2. 중간 제어 버튼 라인
        self.btn_frame = ttk.Frame(self.main_container)
        self.btn_frame.pack(fill=tk.X, pady=(0, 10))

        self.scan_button = ttk.Button(
            self.btn_frame, 
            text="⚡ 소스코드 정밀 슬라이싱 및 컨텍스트 바인딩 가동 ⚡", 
            command=self.execute_slicing_pipeline
        )
        self.scan_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.export_button = ttk.Button(
            self.btn_frame,
            text="💾 마크다운 파일(.md) 개별 내보내기",
            command=self.manual_export_file,
            state=tk.DISABLED # 처음엔 비활성화
        )
        self.export_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 3. 하단 결과창 구역
        output_label = ttk.Label(self.main_container, text="📄 [AI 배송용 최적화 켄텍스트 보따리 (출력 결과)]", font=("Malgun Gothic", 11, "bold"))
        output_label.pack(anchor=tk.W, pady=(0, 5))

        self.code_display = tk.Text(self.main_container, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.code_display.pack(fill=tk.BOTH, expand=True)

        # 4. 최하단 상태 바
        self.status_label = ttk.Label(self.main_container, text="🟢 대기 중... 에이전트 프롬프트를 넣고 가동 버튼을 눌러주십시오.", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(10, 0))

    def execute_slicing_pipeline(self):
        raw_prompt = self.prompt_input.get("1.0", tk.END).strip()
        if not raw_prompt or raw_prompt.startswith("💡"):
            messagebox.showwarning("입력 오류", "형님, 슬라이싱할 대상 파일 경로와 라인을 입력해 주십시오!")
            return

        # 백그라운드 추출 엔진 구동
        extracted_slices = self.navigator.extract_multi_slices(raw_prompt)

        if not extracted_slices:
            self.status_label.config(text="❌ 추출 실패: 프롬프트에서 타겟 패턴('경로:줄번호')을 인식하지 못했습니다.")
            messagebox.showerror("추출 실패", "지정된 경로 문자열 형식을 확인해 주십시오.")
            return

        # 화면 정화 및 마스터 전역 가이드라인 헤더 선언
        self.code_display.delete("1.0", tk.END)
        
        # 마크다운 스트링 빌드 시작
        md_lines = []
        md_lines.append("# ==========================================================================")
        md_lines.append("# 🎯 AI 전역 가이드라인: 무결성과 확장성의 황금 밸런스 규칙")
        md_lines.append("# 소스를 분석, 리팩토링 및 수정 요청할 때 아래 최적화 규칙을 무조건 엄격히 준수하십시오.")
        md_lines.append("#")
        md_lines.append("# 1. 구조 유지: 프로젝트 내 기존 클래스/함수명 명세 및 self.vars 데이터 프로토콜은 엄격히 준수하십시오.")
        md_lines.append("# 2. 환각 방지: 존재하지 않는 가짜 함수 창조 절대 금지! 절대값 연산은 순정 내장 함수 abs()를 쓰십시오.")
        md_lines.append("# 3. 개발 자유: 위 최소 조건 내에서 알고리즘, 물리 수식, 이동 로직은 자유롭고 창의적으로 짜십시오.")
        md_lines.append("# ==========================================================================")

        for slc in extracted_slices:
            md_lines.append(f"# 📄 [요청 {slc['req_num']}] TARGET: {slc['file']} ({slc['line_range']}라인)")
            md_lines.append("# ----------------------------------------------------------")
            md_lines.append("```python")
            md_lines.append(slc["code"].rstrip())
            md_lines.append("```")

        self.last_markdown_content = "".join(md_lines)

        # GUI 창에 렌더링 인쇄
        self.code_display.insert(tk.END, self.last_markdown_content)
        
        # 💾 [플러스 알파] 프로젝트 루트에 extracted_context.md 자동 상시 저장 처리!
        auto_save_path = self.project_root / "extracted_context.md"
        try:
            with open(auto_save_path, "w", encoding="utf-8") as f:
                f.write(self.last_markdown_content)
            status_msg = f"🟢 추출 및 마크다운 자동 저장 완료! -> {auto_save_path.name}"
            self.export_button.config(state=tk.NORMAL)
        except Exception as e:
            status_msg = f"⚠️ 화면 추출 완료했으나 자동 파일 저장 실패: {e}"

        self.status_label.config(text=status_msg)

    def manual_export_file(self):
        """사용자가 원하는 다른 경로에 수동으로 저장할 수 있는 다이얼로그 프로토콜"""
        if not self.last_markdown_content:
            return
        
        file_path = filedialog.asksaveasfilename(
            initialdir=str(self.project_root),
            title="마크다운 컨텍스트 파일 저장",
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.last_markdown_content)
                messagebox.showinfo("내보내기 성공", f"형님, 성공적으로 파일을 내보냈습니다!\n📂 경로: {file_path}")
            except Exception as e:
                messagebox.showerror("내보내기 실패", f"파일 저장 중 에러가 발생했습니다: {e}")

if __name__ == "__main__":
    # 실행 컨텍스트 루트 자동 정렬
    current_dir = Path(__file__).parent.resolve()
    # 만약 cline_tools 폴더 내에 있다면 상위를 루트로 잡고, 아니면 현재 폴더를 루트로 보장
    project_root = current_dir.parent if current_dir.name == "cline_tools" else current_dir

    root_window = tk.Tk()
    app = JjapCursorNavigatorGUI(root_window, project_root)
    root_window.mainloop()