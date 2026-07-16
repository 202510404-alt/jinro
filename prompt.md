# TASK: Project Architecture Refactoring (Multi-Language Tools Expansion)

## 📌 0. CURRENT RUNTIME ENVIRONMENT (CRITICAL)
* **Executing Directory (Project Root)**: `C:\Users\COMLAB\Desktop\AI_agent\`
* **Current State**: `cline_tools/` directory, `start.py`, and `agent_core/` exist directly under this root.
* **Refactoring Shell**: All file system operations (mkdir, mv, rm) must be relative to this `AI_agent` path.

---

## 🎯 1. 최종 목표 및 배경
현재 프로젝트 루트에 존재하는 `cline_tools/` 디렉토리는 단순 요약기 툴파일 모음집으로 작동하고 있습니다. 향후 Python뿐만 아니라 TypeScript, Go 등 다양한 언어/플랫폼의 에이전트 툴을 유연하게 수용할 수 있도록 다중 계층 디렉토리 구조로 리팩토링을 수행합니다.

* **기존 물리 경로**: `C:\Users\COMLAB\Desktop\AI_agent\cline_tools\`
* **신규 변경 경로**: `C:\Users\COMLAB\Desktop\AI_agent\tools\python_agent_tools\`

---

## 🛠️ 2. 리팩토링 대상 파일 스코프
* **SSOT 문서**: `plan_final.md`, `AI_CODEBASE_MAP.md`
* **소스 코드**: `start.py` 및 기존 `cline_tools/` 내에 존재하던 모든 `.py` 파일 전체

---

## 📋 3. 단계별 실행 프로토콜 (Execution Pipeline)

안티그래비티는 아래 단계를 원자적(Atomic)으로 수행하며, 한 단계가 성공할 때만 다음 단계로 이행합니다.

### Phase 1: 파일 내부 텍스트 및 주석 정밀 리팩토링
* 물리적 폴더를 이동하기 전, 컨텍스트 소실을 막기 위해 파일 내부 코드부터 수정합니다.
* `plan_final.md`, `AI_CODEBASE_MAP.md`, `start.py`, 그리고 기존 `cline_tools/` 내부의 모든 소스 코드 안에서 발생하는 아래 패턴을 매칭하여 수정하십시오.
    * **텍스트/경로 문자열 매칭**: `cline_tools` ➡️ `tools/python_agent_tools`
    * **헤더 주석 규격 매칭**: `[📂 cline_tools/...]` ➡️ `[📂 tools/python_agent_tools/...]`
* **주의**: `create_ai_map.py` 내부에 존재하는 `SCRIPT_DIR.name == "cline_tools"`와 같은 조건부 로직이나 루트 계산 로직(`PROJECT_ROOT`)이 있다면, 바뀐 폴더명(`python_agent_tools`) 및 계층 깊이(Depth가 하나 더 깊어짐)에 맞게 정밀하게 동기화 가공해야 합니다.

### Phase 2: 신규 다중 레이어 디렉토리 구조 생성
* 터미널 명령 또는 파일 시스템 툴을 이용하여 `C:\Users\COMLAB\Desktop\AI_agent\` 하위에 신규 구조를 신설합니다.
* 생성할 경로: `tools/python_agent_tools/`
* (향후 `tools/ts_agent_tools/` 등이 들어올 수 있는 확장 베이스라인 구축 목적)

### Phase 3: 파일 이동 및 이전 흔적 삭제
* 기존 `cline_tools/` 내부에 있던 모든 파이썬 파일들을 새롭게 생성된 `tools/python_agent_tools/` 내부로 온전하게 이동(Move)시킵니다.
* 이동이 완료되면 비어있는 기존 `cline_tools/` 디렉토리를 완전히 삭제(Clean)합니다.

### Phase 4: 시스템 구동 및 참조 무결성 검증 (Sanity Check)
* 리팩토링 완료 후, 안티그래비티 런타임 툴을 사용하여 시스템을 구동해 봅니다.
* `python tools/python_agent_tools/indexer.py` 또는 `python start.py`를 실행하여 `ImportError` 및 경로 계산 에러가 터지지 않는지 최종 확인하십시오.
* 만약 에러가 발생한다면, 에러 로그를 분석하여 미처 변경되지 못한 잔여 경로 의존성을 끝까지 추적해서 수정하십시오.

---

## ⚠️ 4. 에이전트 절대 제약 사항 (Reject Rules)
1.  **스텁 코드 생성 금지**: 코드 이동 및 수정 과정에서 절대 `# TODO`, `pass`, `...` 등으로 기존 로직을 생략하거나 유실시키지 마십시오.
2.  **경로 추측 금지**: 모든 파일의 경로는 오직 신설된 `[📂 tools/python_agent_tools/...]` 기준의 상대 경로 무결성을 엄격하게 유지해야 합니다.