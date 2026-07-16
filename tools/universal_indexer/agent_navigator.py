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
        # 🎛️ [SCAN_MODE 스위치 반영] switch.py의 모드를 동적으로 확인합니다.
        self.raw_root_dir = root_dir
        self.scan_mode = "ROOT"
        
        try:
            # sys.path에 root_dir 및 tools/universal_indexer 경로를 추가하여 switch 모듈 로드 보장
            idx_path = str(root_dir / "tools" / "universal_indexer")
            if idx_path not in sys.path:
                sys.path.insert(0, idx_path)
            
            import switch
            self.scan_mode = getattr(switch, "SCAN_MODE", "ROOT")
            print(f"🎛️ [SWITCH DETECTED] 현재 탐색 스위치 모드: {self.scan_mode}")
        except Exception as e:
            print(f"⚠️ [SWITCH WARNING] switch.py를 로드하지 못해 기본 'ROOT' 모드로 동작합니다. (이유: {e})")

        # 🚀 SRC 모드일 경우 하드디스크 탐색 기준점(self.root_dir)에 'src' 폴더를 강제 결합
        if self.scan_mode == "SRC":
            self.root_dir = root_dir / "src"
            print(f"📁 [MODE: SRC] 탐색 마스터 루트가 복사/격리용 src 폴더로 변경되었습니다: {self.root_dir}")
        else:
            self.root_dir = root_dir
            print(f"📁 [MODE: ROOT] 탐색 마스터 루트가 프로젝트 원본 루트로 설정되었습니다: {self.root_dir}")

        # 🧠 [불러오기 교정] 장부 정보는 언제나 프로젝트의 실제 본체 루트(raw_root_dir) 기준으로 가져옵니다.
        self.symbols_path = self.raw_root_dir / "system_memory" / ".jjap_symbols.json"
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
        [Multi-Target Protocol Parser - 경로 및 클래스명 종속성 완전 격파 버전]
        """
        print("\n" + "="*60)
        print("🚨 [DEBUGGER ON] 내비게이터 멀티 슬라이싱 파이프라인 기동!!!")
        print(f"📥 유저 입력 프롬프트: {repr(raw_prompt)}")
        print(f"⚙️ 현재 매핑 모드: {self.scan_mode} (기준 경로: {self.root_dir})")
        print("="*60)

        pattern = r"([a-zA-Z0-9_\-\./]+)\s*:\s*(\d+)(?:\s*-\s*(\d+))?"
        matches = re.findall(pattern, raw_prompt)

        print(f"🔍 정규식 1차 타겟 스캔 결과: {matches}")
        if not matches:
            print("⚠️ [DEBUG] 매칭되는 파일 경로 및 라인 규격이 없습니다. 빈 배열 리턴.")
            return []

        extracted_slices = []
        req_num = 1

        for match in matches:
            file_rel_path = match[0].strip()
            start_line = int(match[1])
            end_line = int(match[2]) if match[2] else start_line

            print(f"\n🎯 [요청 #{req_num}] 메인 타겟 분석 시작 -> {file_rel_path} ({start_line} ~ {end_line} 라인)")

            # 🛠️ 형님의 설계 의도 전면 반영 구역
            if self.scan_mode == "SRC":
                # AI가 'src/main/java/...' 처럼 가장 바깥 'src/'가 잘린 채로 요청하므로, 
                # 하드디스크의 실제 격리 구조와 맞추기 위해 앞에 'src/'를 추가 빌드합니다.
                # (혹시 이미 src/src/ 형태로 들어온 경우를 대비해 안전장치 추가)
                if not file_rel_path.startswith("src/src/"):
                    target_file_path = self.raw_root_dir / "src" / file_rel_path
                else:
                    target_file_path = self.raw_root_dir / file_rel_path
                
                print(f"   📁 [MODE: SRC] 경로 보정 적용 완료 -> {target_file_path}")
            else:
                # ROOT 모드일 때는 AI가 'src/src/main/java/...' 규격 그대로 던져주므로 
                # 기존과 동일하게 원본 루트 디렉토리에 그대로 결합합니다.
                target_file_path = self.raw_root_dir / file_rel_path
                print(f"   📁 [MODE: ROOT] 원본 경로 유지 -> {target_file_path}")
            
            if not target_file_path.exists():
                # 2차 구제금융: 혹시 모르니 raw_root 기준이나 tools 프리픽스도 함께 스캔
                alt_path = self.raw_root_dir / file_rel_path
                if alt_path.exists():
                    target_file_path = alt_path
                    print(f"   ♻️ [SRC 모드 구제] 프로젝트 전체 원본 경로에서 파일 포착 완료: {target_file_path}")
                else:
                    print(f"   ❌ [ERROR] 해당 파일이 실제 경로에 존재하지 않습니다! 패스합니다.")
                    continue

            try:
                with open(target_file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                total_lines = len(lines)
                safe_start = max(1, min(start_line, total_lines))
                safe_end = max(safe_start, min(end_line, total_lines))
                print(f"   📏 파일 전체 줄 수: {total_lines} | 보정된 안전 범위: {safe_start} ~ {safe_end}")

                slice_lines = lines[safe_start - 1 : safe_end]
                slice_code = "".join(slice_lines)
                print(f"   🟢 1차 메인 슬라이싱 성공 (길이: {len(slice_code)}자)")

                extracted_slices.append({
                    "req_num": f"{req_num}",
                    "file": file_rel_path,
                    "line_range": f"{safe_start}-{safe_end}",
                    "code": slice_code
                })

                # [2단계] 🔗 제이슨 기반 2차 심볼 탐색기 가동
                print(f"   📡 [형님의 2차 사냥기] 잘려 나온 텍스트 내부에서 양방향 심볼 식별 개시...")

                defined_names = re.findall(r"(?:def|class)\s+([a-zA-Z0-9_]+)", slice_code)
                called_names = re.findall(r"(?:[a-zA-Z0-9_]+\.)?([a-zA-Z0-9_]+)\s*\(", slice_code)
                builtin_filters = {"print", "len", "range", "open", "dict", "list", "set", "any", "all", "max", "min", "append", "get", "strip", "split", "exists", "readlines", "join"}
                filtered_called_names = [name for name in called_names if name not in builtin_filters]

                target_symbols = list(set(defined_names + filtered_called_names))
                print(f"   📦 [양방향 통합] 징집 대상 심볼 목록: {target_symbols}")
                
                symbols_list = self.symbols_data.get("symbols", [])
                print(f"   📚 로드된 JSON 장부 총 심볼 개수: {len(symbols_list)}개")

                for target_name in target_symbols:
                    print(f"      🔎 [전역 심볼 대조] 이름: '{target_name}' -> 장부 전체 스캔 중...")
                    match_found = False
                    
                    for s in symbols_list:
                        json_file_path = s.get("file", "")
                        
                        if s.get("name") == target_name:
                            match_found = True
                            t_file = s.get("file", "")
                            s_start = s.get("start_line", 1)
                            s_end = s.get("end_line", 1)

                            if t_file != file_rel_path:
                                print(f"         ➡️ [정방향] 내가 불러온 함수 본체 포착 -> {t_file} ({s_start}~{s_end}라인)")
                                
                                # 🎛️ 형님의 모드별 경로 보정 룰 적용
                                if self.scan_mode == "SRC":
                                    if not t_file.startswith("src/src/"):
                                        callee_file_path = self.raw_root_dir / "src" / t_file
                                    else:
                                        callee_file_path = self.raw_root_dir / t_file
                                else:
                                    # ROOT 모드일 때는 장부 경로 그대로 조립
                                    callee_file_path = self.raw_root_dir / t_file
                                    
                                # [구제금융 버퍼] 혹시 모를 경로 예외 대비
                                if not callee_file_path.exists():
                                    callee_file_path = self.raw_root_dir / t_file
                                if not callee_file_path.exists():
                                    callee_file_path = self.raw_root_dir / "tools" / t_file
                                    
                                if callee_file_path.exists():
                                    with open(callee_file_path, "r", encoding="utf-8") as cf:
                                        cf_lines = cf.readlines()
                                    
                                    s_start = max(1, min(s_start, len(cf_lines)))
                                    s_end = max(s_start, min(s_end, len(cf_lines)))
                                    callee_code = "".join(cf_lines[s_start - 1 : s_end])
                                    
                                    if not any(x["file"] == t_file and x["line_range"] == f"{s_start}-{s_end}" for x in extracted_slices):
                                        extracted_slices.append({
                                            "req_num": f"{req_num} ➡️ 불러온함수 ({target_name} 본체)",
                                            "file": t_file,
                                            "line_range": f"{s_start}-{s_end}",
                                            "code": callee_code
                                        })

                            if (target_name in defined_names) or (s.get("file") == file_rel_path):
                                ub_list = s.get("used_by", [])
                                if ub_list:
                                    print(f"         ⬅️ [역방향] 나를 부르는 전역 호출처 목록(used_by): {ub_list}")
                                    for ub_id in ub_list:
                                        if "::" in ub_id:
                                            ub_file, ub_symbol_name = ub_id.split("::", 1)
                                            if "." in ub_symbol_name:
                                                ub_symbol_name = ub_symbol_name.split(".")[-1]
                                            
                                            sub_match_found = False
                                            for target_s in symbols_list:
                                                sub_t_file = target_s.get("file", "")
                                                s_id = target_s.get("symbol_id", "")
                                                sub_s_name = target_s.get("name", "")
                                                
                                                if (s_id == ub_id) or (ub_id.endswith(s_id)) or (sub_s_name == ub_symbol_name and (sub_t_file == ub_file or ub_file.endswith(sub_t_file) or sub_t_file.endswith(ub_file))):
                                                    sub_match_found = True
                                                    
                                                    # 🎛️ [역방향 탐색 경로 보정] 형님의 모드별 설계 반영
                                                    if self.scan_mode == "SRC":
                                                        # AI가 바깥쪽 'src/'를 생략하고 볼 때를 대비해, 'src/src/' 형태가 아니라면 앞에 'src/'를 강제 결합합니다.
                                                        if not sub_t_file.startswith("src/src/"):
                                                            ub_file_path = self.raw_root_dir / "src" / sub_t_file
                                                        else:
                                                            ub_file_path = self.raw_root_dir / sub_t_file
                                                    else:
                                                        # ROOT 모드일 때는 AI가 전체 경로 규격 그대로 던져주므로 원본대로 조립
                                                        ub_file_path = self.raw_root_dir / sub_t_file
                                                        
                                                    # ♻️ [구제금융 버퍼] 혹시 모를 장부상의 경로 미스매치 예외 방어
                                                    if not ub_file_path.exists():
                                                        ub_file_path = self.raw_root_dir / sub_t_file
                                                    if not ub_file_path.exists():
                                                        ub_file_path = self.raw_root_dir / "tools" / sub_t_file
                                                    if ub_file_path.exists():
                                                        with open(ub_file_path, "r", encoding="utf-8") as ubf:
                                                            ub_lines = ubf.readlines()
                                                        
                                                        ubs_start = max(1, min(target_s.get("start_line", 1), len(ub_lines)))
                                                        ubs_end = max(ubs_start, min(target_s.get("end_line", len(ub_lines)), len(ub_lines)))
                                                        ub_slice_code = "".join(ub_lines[ubs_start - 1 : ubs_end])
                                                        
                                                        if not any(x["file"] == sub_t_file and x["line_range"] == f"{ubs_start}-{ubs_end}" for x in extracted_slices):
                                                            extracted_slices.append({
                                                                "req_num": f"{req_num} 🔗 제이슨연동 ({target_name} 호출처 -> {sub_t_file}의 [{sub_s_name}])",
                                                                "file": sub_t_file,
                                                                "line_range": f"{ubs_start}-{ubs_end}",
                                                                "code": ub_slice_code
                                                            })
                                            if not sub_match_found:
                                                print(f"            ❌ [ERROR] 호출처 구조체 '{ub_id}'를 장부에서 찾지 못했습니다.")
                    
                    if not match_found:
                        print(f"      ❓ [NOT FOUND] 코드엔 찍혀있는데 JSON 장부({file_rel_path})엔 등록 안 된 심볼입니다.")

            except Exception as e:
                import traceback
                print(f"💥 [CRITICAL ERROR] 슬라이싱 중 예외 폭발!!!: {e}")
                traceback.print_exc()

            req_num += 1

        print("\n" + "="*60)
        print(f"🏁 [DEBUG] 최종 반환할 총 슬라이스 묶음 개수: {len(extracted_slices)}개")
        print("="*60 + "\n")
        return extracted_slices

# =====================================================================
# 🎨 GUI INTERFACE LAYER (UPGRADED VERSION)
# =====================================================================
class JjapCursorNavigatorGUI:
    def __init__(self, root, project_root: Path):
        self.root = root
        self.project_root = project_root
        self.navigator = SemanticNavigator(project_root)
        self.last_markdown_content = ""

        # GUI Title에 현재 스캔 모드를 가독성 있게 표기
        self.root.title(f"⚡ Jjap-Cursor Agent Navigator v2.0 (Auto-Exporter) | 모드: {self.navigator.scan_mode}")
        self.root.geometry("1000x750")

        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        input_label = ttk.Label(self.main_container, text=f"📥 [에이전트 요청 프롬프트 입력 구역 - 현재 모드: {self.navigator.scan_mode}]", font=("Malgun Gothic", 11, "bold"))
        input_label.pack(anchor=tk.W, pady=(0, 5))

        self.prompt_input = tk.Text(self.main_container, height=6, font=("Malgun Gothic", 10))
        self.prompt_input.pack(fill=tk.X, pady=(0, 10))
        
        # 안내 문구 최적화
        if self.navigator.scan_mode == "SRC":
            self.prompt_input.insert(tk.END, "💡 실전 테스트 양식 예시 (SRC 모드):\nsrc/src/main/java/com/desertcore/deathevent.java:32-60")
        else:
            self.prompt_input.insert(tk.END, "💡 실전 테스트 양식 예시 (ROOT 모드):\nsrc/main/java/com/desertcore/deathevent.java:32-60")

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
            state=tk.DISABLED
        )
        self.export_button.pack(side=tk.RIGHT, padx=(5, 0))

        output_label = ttk.Label(self.main_container, text="📄 [AI 배송용 최적화 켄텍스트 보따리 (출력 결과)]", font=("Malgun Gothic", 11, "bold"))
        output_label.pack(anchor=tk.W, pady=(0, 5))

        self.code_display = tk.Text(self.main_container, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.code_display.pack(fill=tk.BOTH, expand=True)

        self.status_label = ttk.Label(self.main_container, text=f"🟢 대기 중... [{self.navigator.scan_mode} 모드] 프롬프트를 입력하고 가동 버튼을 누르십시오.", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(10, 0))

    def execute_slicing_pipeline(self):
        raw_prompt = self.prompt_input.get("1.0", tk.END).strip()
        if not raw_prompt or raw_prompt.startswith("💡"):
            messagebox.showwarning("입력 오류", "형님, 슬라이싱할 대상 파일 경로와 라인을 입력해 주십시오!")
            return

        extracted_slices = self.navigator.extract_multi_slices(raw_prompt)

        if not extracted_slices:
            self.status_label.config(text="❌ 추출 실패: 프롬프트에서 타겟 패턴('경로:줄번호')을 인식하지 못했습니다.")
            messagebox.showerror("추출 실패", "지정된 경로 문자열 형식을 확인해 주십시오.")
            return

        self.code_display.delete("1.0", tk.END)
        
        md_lines = []
        md_lines.append("# ==========================================================================")
        md_lines.append("# 🎯 AI GLOBAL GUIDELINES: 코드 무결성 및 디버깅 중심 가이드")
        md_lines.append(f"# [SCAN_MODE] {self.navigator.scan_mode}")
        md_lines.append("# ==========================================================================")

        for slc in extracted_slices:
            md_lines.append(f"# 📄 [요청 {slc['req_num']}] TARGET: {slc['file']} ({slc['line_range']}라인)")
            md_lines.append("# ----------------------------------------------------------")
            md_lines.append("```python")
            md_lines.append(slc["code"].rstrip())
            md_lines.append("```\n")

        self.last_markdown_content = "\n".join(md_lines)
        self.code_display.insert(tk.END, self.last_markdown_content)
        
        # 저장할 때는 언제나 마스터 격리 폴더(system_maps) 내부로 안전 상시 저장
        auto_save_path = self.project_root / "system_maps" / "extracted_context.md"
        try:
            auto_save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(auto_save_path, "w", encoding="utf-8") as f:
                f.write(self.last_markdown_content)
            status_msg = f"🟢 [{self.navigator.scan_mode}] 추출 및 마크다운 자동 저장 완료! -> system_maps/{auto_save_path.name}"
            self.export_button.config(state=tk.NORMAL)
        except Exception as e:
            status_msg = f"⚠️ 화면 추출 완료했으나 자동 파일 저장 실패: {e}"

        self.status_label.config(text=status_msg)
        
    def manual_export_file(self):
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
    current_dir = Path(__file__).parent.resolve()
    
    # 🔄 두 단계 깊이인 tools/universal_indexer/ 구조일 때 마스터 루트 경로 역추적 동기화
    if current_dir.name == "universal_indexer" and current_dir.parent.name == "tools":
        project_root = current_dir.parent.parent
    else:
        project_root = current_dir

    root_window = tk.Tk()
    app = JjapCursorNavigatorGUI(root_window, project_root)
    root_window.mainloop()