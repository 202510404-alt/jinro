# 🏗️ plan_final.md — ASE-OS Single Source of Truth (v1.1)

> **[전 에이전트 필독 / 최우선순위 문서]**
> 본 문서는 프로젝트 최상위에 위치하는 단 하나의 진실 공급원(SSOT)이다.
> 모든 AI 에이전트(Planner, Manager, Worker, Validator 등)는 코드 수정 전 반드시 본 문서의 §2(스위치 맵), §3(인터페이스 규격), §3.5(디버깅 로그 예측-검증), §3.6(파일 락), §3.7(교차 세션 병합)을 파싱하고 준수해야 한다.
> 경로는 예외 없이 `AI_CODEBASE_MAP.md`의 `[📂 실제경로]` 표기를 그대로 사용한다. 축약·추측·상대경로 임의 변경 금지.

### 📌 v1.1 변경 이력 (v1.0 대비)

* **[신규]** §3.5 디버깅 로그 예측-검증 시스템 — Planner가 로그 삽입 위치·문구·"예측 출력값"까지 사전 확정하여 Task에 포함시키고, Worker는 해당 파일/함수를 **파이프라인 전체가 아닌 단독 실행**으로 돌려 실제 출력을 예측치와 대조 후에만 "설계 완료"로 표시한다.
* **[신규]** §3.6 파일 단위 락(Lock) 안전구조 — Level4 Manager Layer가 파일별 잠금을 관리, 이미 작업 중인 파일에는 다른 Worker를 대기시켜 동시수정 충돌을 원천 차단한다(속도보다 안전 우선).
* **[신규]** §3.7 교차 세션(멀티 터미널) 병합 시스템 — 서로 다른 터미널에서 각각 기획자(Planner) 수준으로 독립 실행 중인 프로젝트를 감지하면, 두 세션이 연결되어 각자의 내부 병합(Level7/8)이 끝난 결과물끼리 최종적으로 한 번 더 병합된다.
* **[변경]** §1.1/§1.2 컴포넌트 현황 표에 위 세 서브시스템 행 추가.
* **[변경]** §2 YAML 스위치 맵에 `debug_log_system`, `file_lock`, `multi_session_merge` 블록 추가.
* **[변경]** §3.4 Reject Rules에 디버깅 로그/락/세션 관련 반려 규칙 추가.
* **[변경]** §4 로드맵에 Phase 11~13 신설(기존 "Phase 11~12 이연" 문구를 구체 Phase로 승격).
* **[변경]** §5 체크리스트에 신규 항목 추가.

---

## ⚠️ 0. 사전 정밀 분석 타겟팅 (병목 선언)

* **정밀 분석 타겟팅**: `cline_tools/indexer.py:97-168` (이유: `index_file()`이 생성하는 심볼 스키마에 `read_set`/`write_set`/`dependency`/`confidence`/`owner` 필드가 없어, Level2(Master Planner)·Level3(Task Graph)가 필요로 하는 계획 단위 메타데이터를 즉시 소비하지 못하고 별도 변환 계층을 요구하는 구조적 병목이 발생함)

부가 리스크 지점(참고용, 우선순위는 위보다 낮음):
* `cline_tools/jjap_retriever.py:39-98` — `retrieve_symbol()`이 단일 심볼 단위로만 동작. Task Graph가 여러 Task의 Read Set을 묶어 배치 조회할 인터페이스가 없어 Level5→Level6 연동 시 N+1 호출 문제 예상.
* `cline_tools/create_ai_map.py:168-236` — `AI_CODEBASE_MAP.md` 생성이 전체 파일 재스캔 방식(Full Rewrite)이라, Task Graph 규모가 커지면 증분(incremental) 갱신 부재로 인한 지연이 예상됨.
* **[v1.1 신규]** 디버깅 로그 예측-검증을 도입하면 Task 수가 늘어날수록 "단독 실행 → 출력 캡처 → 예측치 대조" 사이클의 I/O 비용이 누적된다. Phase 12 착수 전 `agent_core/execution/standalone_runner.py`의 실행 격리(subprocess timeout, 무한루프 방지) 설계를 §3.5.3에 명시해 둔다.

---

## 1. 현황 진단 및 구현율 리포트

### 1.1 물리적 파일 존재 현황 (실 코드 기준)

| 파일 | 실제 경로 | 상태 | 구현율 |
|---|---|---|---|
| indexer.py | `cline_tools/indexer.py` | ✅ 작동 | 85% |
| create_ai_map.py | `cline_tools/create_ai_map.py` | ✅ 작동 | 80% |
| update_map.py | `cline_tools/update_map.py` | ✅ 작동 | 75% |
| jjap_retriever.py | `cline_tools/jjap_retriever.py` | ✅ 작동 | 70% |
| jjap_lookup.py | `cline_tools/jjap_lookup.py` | ✅ 작동(CLI) | 65% |
| agent_navigator.py | `cline_tools/agent_navigator.py` | ✅ 작동(GUI) | 60% |
| context_builder.py | `cline_tools/context_builder.py` | ⚠️ 부분 구현 | 40% |
| jjap_watcher.py | `cline_tools/jjap_watcher.py` | ✅ 작동 | 75% |
| switch.py | `cline_tools/switch.py` | ✅ 작동(상수) | 100% |
| start.py | `start.py` | ✅ 작동 | 80% |
| Master Planner (Level2) | 미존재 | ❌ 미구현 | 0% |
| Task Graph (Level3) | 미존재 | ❌ 미구현 | 0% |
| Manager Layer (Level4) | 미존재 | ❌ 미구현 | 0% |
| Worker Agents (Level5) | 미존재 | ❌ 미구현 | 0% |
| Live Retriever (Level6) | jjap_retriever.py 일부 재사용 가능 | ⚠️ 부분 기반 존재 | 20% |
| Conflict Manager (Level7) | 미존재 | ❌ 미구현 | 0% |
| Semantic Merge (Level8) | 미존재 | ❌ 미구현 | 0% |
| Validator (Level9) | 미존재 | ❌ 미구현 | 0% |
| Reflection (Level10) | 미존재 | ❌ 미구현 | 0% |
| Evolution Layer (Level11) | 미존재 | ❌ 미구현 | 0% |
| Project Memory (Level1) | `system_memory/*.json` 파일 형태로 부분 존재 | ⚠️ 부분 구현 | 30% |
| **[신규] Debug Log Predictive Verification** | 미존재 | ❌ 미구현 | 0% |
| **[신규] File Lock Manager (Level4 하위)** | 미존재 | ❌ 미구현 | 0% |
| **[신규] Session Registry / Cross-Session Merge** | 미존재 | ❌ 미구현 | 0% |

### 1.2 레이어별 종합 진단

```
Level 0  Knowledge Layer      ████████░░  80%  (Indexer/Map/Retriever 프로토타입 완성)
Level 1  Project Memory       ███░░░░░░░  30%  (JSON 장부는 있으나 실패이력/빌드이력 스키마 부재)
Level 2  Master Planner       ░░░░░░░░░░   0%  (미착수 — v1.1부터 debug_log_plan/예측출력 생성 책임 추가)
Level 3  Task Graph           ░░░░░░░░░░   0%  (미착수)
Level 4  Manager Layer        ░░░░░░░░░░   0%  (미착수 — v1.1부터 File Lock 관리 책임 추가)
Level 5  Worker Agents        ░░░░░░░░░░   0%  (미착수, gemini_client.py 등은 스텁 수준)
Level 6  Live Retriever       ██░░░░░░░░  20%  (jjap_retriever 단일조회만 가능)
Level 7  Conflict Manager     ░░░░░░░░░░   0%  (미착수)
Level 8  Semantic Merge       ░░░░░░░░░░   0%  (미착수)
Level 9  Validator            ░░░░░░░░░░   0%  (agent_core/validation/ 폴더만 존재, 빈 __init__)
Level 10 Reflection           ░░░░░░░░░░   0%  (미착수)
Level 11 Evolution Layer      ░░░░░░░░░░   0%  (미착수)
[신규] Debug Log Predictive   ░░░░░░░░░░   0%  (미착수, Phase 12 목표)
[신규] File Lock (L4 하위)     ░░░░░░░░░░   0%  (미착수, Phase 11 목표)
[신규] Cross-Session Merge    ░░░░░░░░░░   0%  (미착수, Phase 13 목표)
```

### 1.3 핵심 구조적 결함 (치명도 순)

1. **스키마 불일치**: `indexer.py`의 symbol 스키마(`symbol_id`, `range`, `calls`, `used_by`)는 Task Graph가 요구하는 `Read Set / Write Set / Dependency / Confidence / Owner`를 포함하지 않음. → §0 병목과 동일 지점.
2. **경로 이중 기준**: `SCAN_MODE`(switch.py)가 "ROOT"/"SRC" 두 가지 기준을 가지며, `indexer.py`는 `PROJECT_ROOT = SCRIPT_DIR.parent`로 고정 계산하는 반면 `create_ai_map.py`는 `SCRIPT_DIR.name == "cline_tools"` 조건부 계산을 사용함. 두 파일의 루트 계산 로직이 미묘하게 다르므로 향후 Task Graph가 두 로직 중 무엇을 신뢰할지 충돌 가능.
3. **agent_core/ 스텁 상태**: `agent_core/plan/`, `agent_core/validation/`, `agent_core/execution/`, `agent_core/memory/` 폴더가 이미 존재하지만 `__init__.py`만 있고 실질 코드 없음 → Level2/Level9의 물리적 착지 위치는 이미 확보되어 있음(디렉토리 재사용 가능).
4. **[v1.1 신규] "완료" 판정 기준의 모호성**: 기존 설계는 Validator(Level9)가 import/build/test 통과 여부만으로 Task를 DONE 처리한다. 그러나 이는 "코드가 실행은 되지만 의도한 로직대로 동작하는지"를 보증하지 않는다 → §3.5에서 Planner가 사전 예측한 출력값과 실제 단독실행 출력값을 대조하는 절차를 DONE 판정의 필수 조건으로 승격한다.
5. **[v1.1 신규] 동시성 안전장치 부재**: 현재 설계에는 Worker 2개 이상이 동일 파일을 동시에 수정할 가능성을 막는 장치가 없다. → §3.6 File Lock으로 해소.
6. **[v1.1 신규] 세션 간 고립**: 동일 인간이 여러 터미널에서 별도 프로젝트(혹은 같은 프로젝트의 다른 브랜치)를 동시에 돌릴 경우, 두 세션은 서로의 존재를 모른 채 각자 완료된다. 병합 시점에 사람이 수동 개입해야 함 → §3.7 Session Registry로 해소.

---

## 2. 실험용 글로벌 스위치 맵 (YAML)

```yaml
# ase_os_config.yaml
# [📂 실제경로] project_root/ase_os_config.yaml (신규 생성 필요)

ase_os:
  version: "1.1"

  layers:
    level0_knowledge:
      enabled: true              # 항상 true 권장 (다른 모든 레이어의 기반)
      fallback: "n/a"            # 끌 수 없음 — 끄면 시스템 전체 정지

    level1_project_memory:
      enabled: false
      fallback: "in_memory_dict"     # OFF 시: 프로세스 휘발성 dict로 대체, 재시작 시 기억 소실

    level2_master_planner:
      enabled: false
      fallback: "manual_task_input"  # OFF 시: 사용자가 Task Graph를 JSON으로 직접 입력
      require_debug_log_plan: true   # [v1.1] Planner가 Task마다 debug_log_plan 미생성 시 Task 반려

    level3_task_graph:
      enabled: false
      fallback: "single_task_mode"   # OFF 시: 그래프 없이 Task 1개만 순차 처리(기존 파이프라인과 동일)

    level4_manager_layer:
      enabled: false
      fallback: "direct_worker_dispatch"  # OFF 시: Task Graph가 Worker를 직접 호출
      file_lock:                          # [v1.1 신규]
        enabled: true                     # 끄면 동시성 위험 감수, 속도만 우선할 때 사용
        wait_strategy: "block_until_free"  # "block_until_free" | "queue_and_reorder" | "fail_fast"
        max_wait_sec: 900                  # 초과 시 Manager가 해당 Task를 BLOCKED 처리하고 Planner에 재계획 요청
        lock_store: "system_memory/locks/"

    level5_worker_agents:
      enabled: true
      fallback: "n/a"             # 최소 1개 Worker 없이는 Patch 생성 불가 (끌 수 없음)

    level6_live_retriever:
      enabled: true
      fallback: "static_context_builder"  # OFF 시: context_builder.py의 정적 전체 파일 첨부로 대체(비용 증가 감수)

    level7_conflict_manager:
      enabled: false
      fallback: "post_hoc_git_merge"  # OFF 시: 사전예측 없이 기존 Git merge 방식으로 사후 충돌 해결

    level8_semantic_merge:
      enabled: false
      fallback: "raw_git_merge"       # OFF 시: 의도 분석 없이 텍스트 기반 Git merge

    level9_validator:
      enabled: true
      fallback: "import_check_only"   # OFF 상당: 전체 검증 스킵, import 여부만 최소 체크
      require_predicted_output_match: true  # [v1.1] true면 §3.5 예측-검증 통과 없이는 DONE 불가

    level10_reflection:
      enabled: false
      fallback: "raw_error_passthrough"  # OFF 시: 구조화 리포트 없이 원본 stacktrace만 Planner에 전달

    level11_evolution:
      enabled: false
      fallback: "static_ruleset"      # OFF 시: Conflict Rule/Prompt 고정, 자가개선 없음

  # [v1.1 신규] 디버깅 로그 전역 온오프 — 최종 합본 코드에도 그대로 남아
  # 사람이 나중에 켜고 끌 수 있는 상시 스위치. Task 단위 스위치와는 별개다.
  debug_log_system:
    enabled: true
    global_toggle_env: "ASE_DEBUG"        # 최종 코드에서 `if os.getenv("ASE_DEBUG") == "1":` 형태로 사용
    per_task_toggle: true                  # Task별 세부 on/off도 허용 (ASE_DEBUG_<task_id>)
    standalone_execution:
      enabled: true                        # Worker가 파일 단독실행으로 예측 검증 수행
      timeout_sec: 30                      # 무한루프/행 방지
      isolate_env: true                    # 별도 subprocess, 부작용 있는 I/O(DB write 등)는 mock 강제

  # [v1.1 신규] 멀티 터미널 교차 세션 병합
  multi_session_merge:
    enabled: false                          # 기본 OFF — 단일 터미널 사용자는 굳이 켤 필요 없음
    fallback: "manual_cross_merge"          # OFF 시: 사람이 두 세션 결과물을 수동 git merge
    session_registry_path: "system_memory/sessions.json"
    heartbeat_interval_sec: 20
    overlap_detection: "write_set_path_prefix"  # 두 세션의 write_set 파일경로가 겹치면 연결 후보로 판단

  measurement:
    track_success_rate: true
    track_token_usage: true
    track_api_calls: true
    track_execution_time: true
    track_import_errors: true
    track_runtime_errors: true
    track_predicted_vs_actual_output_diff: true   # [v1.1]
    track_lock_wait_time: true                     # [v1.1]
    track_cross_session_merge_count: true          # [v1.1]
```

**규칙**: 각 레이어는 상위 레이어가 OFF일 때 자신의 입력을 fallback 경로에서 받도록 구현해야 하며, 레이어 간 직접 import는 금지하고 반드시 §3의 인터페이스(ABC)를 경유한다.

---

## 3. 인터페이스 규격화 (환각 방지 백본)

### 3.1 공통 계약 원칙

* 모든 핵심 클래스는 `abc.ABC`를 상속하고 `@abstractmethod`로 계약을 강제한다.
* 모든 공개 메서드는 `typing`으로 완전한 타입 힌팅을 명시한다 (인자·반환값 모두).
* **주석으로 로직을 대체하는 것을 금지**한다 — `# TODO: implement later`, `pass  # 구현 예정` 같은 스텁은 CI에서 정적 검사로 차단한다 (§3.4 참조).
* 모든 구현체는 파일 상단에 `# [📂 실제경로]` 주석을 명시해 자기 위치를 스스로 증명해야 한다 (경로 왜곡 방지).
* **[v1.1 신규]** Task가 `write_set`에 포함된 함수/파일을 수정하는 모든 Patch는 반드시 `debug_log_plan`에 명시된 로그 삽입을 포함해야 하며, 해당 로그는 §2 `debug_log_system.global_toggle_env`로 온오프 가능한 형태로 작성되어야 한다 (하드코딩된 `print()` 단독 사용 금지).

### 3.2 데이터 모델 (Task Graph 병목 해소용 신규 스키마)

```python
# [📂 실제경로] agent_core/plan/schemas.py

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"          # [v1.1] File Lock 대기 또는 재계획 대기 상태 포함
    AWAITING_MERGE = "awaiting_merge"  # [v1.1] 로컬 완료, 교차 세션 병합 대기
    DONE = "done"
    FAILED = "failed"


@dataclass(frozen=True)
class SymbolRef:
    """indexer.py의 symbol_id 를 그대로 참조하는 불변 포인터.
    실제 코드 내용은 담지 않고, Level6 Retriever 호출용 키만 보관한다."""
    symbol_id: str          # 예: "cline_tools/indexer.py::AdvancedIndexerV2.index_file"
    file: str                # [📂 실제경로] 규격 그대로
    start_line: int
    end_line: int


@dataclass(frozen=True)
class DebugLogSpec:
    """[v1.1 신규] Master Planner가 Task 생성 시점에 미리 확정하는 디버깅 로그 명세.
    '어디에 무엇을 심고, 어떤 출력이 나와야 하는가'를 Worker에게 통째로 떠먹여준다."""
    log_id: str                      # 예: "T014-L1" (Task 14, 로그 1번)
    file: str                        # [📂 실제경로] 규격
    insert_after_line: int           # 삽입 기준 라인 (Worker 임의 위치 삽입 금지)
    log_statement_template: str      # 예: 'logger.debug(f"[T014-L1] result={result!r}")'
    toggle_key: str                  # 예: "ASE_DEBUG_T014" — 전역 스위치와 별개로 개별 온오프
    predicted_output_pattern: str    # 정규식. 실제 stdout/log에서 이 패턴이 검출되어야 통과
    rationale: str                   # 이 로그가 왜 필요한지(어떤 가설을 검증하는지) 1문장


@dataclass
class Task:
    """Level3 Task Graph의 최소 단위. plan1.md Level3 명세를 코드로 고정."""
    task_id: str
    goal: str
    priority: int                       # 1(최고) ~ 5(최저)
    read_set: list[SymbolRef] = field(default_factory=list)
    write_set: list[SymbolRef] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)   # 선행 task_id 목록
    confidence: float = 0.5             # Master Planner가 산정한 성공 확신도 0.0~1.0
    owner: Optional[str] = None         # 배정된 Manager/Worker 식별자
    estimated_symbols: int = 0          # 예상 변경 심볼 개수 (부하 산정용)
    status: TaskStatus = TaskStatus.PENDING

    # --- [v1.1 신규 필드] ---
    debug_log_plan: list[DebugLogSpec] = field(default_factory=list)
    """Planner가 이 Task 수행 시 삽입되어야 할 디버깅 로그를 전부 사전 확정.
    비어 있으면 Level9 Validator가 즉시 반려(§3.4 규칙 6)."""

    standalone_entrypoint: Optional[str] = None
    """§3.5 단독실행 검증용 진입점. 예: 'python -m cline_tools.indexer --self-test'
    전체 파이프라인을 띄우지 않고 이 Task가 건드린 파일/함수만 격리 실행하기 위한 커맨드."""

    predicted_summary: Optional[str] = None
    """Planner가 이 Task 완료 시 나타날 것으로 예상하는 전체 동작 요약(자연어 1~2문장).
    Reflection(Level10)이 실패 시 '예측과 무엇이 달랐는지' 비교 기준으로 사용."""

    session_id: Optional[str] = None
    """[v1.1] 이 Task를 생성한 터미널 세션 식별자. §3.7 교차 세션 병합 시 출처 추적용."""


@dataclass
class ExecutionResult:
    """[v1.1 신규] §3.5 단독실행 결과를 표준화한 값 객체."""
    task_id: str
    stdout: str
    stderr: str
    exit_code: int
    matched_log_ids: list[str] = field(default_factory=list)     # predicted_output_pattern 매칭 성공한 log_id
    unmatched_log_ids: list[str] = field(default_factory=list)   # 매칭 실패 → Task는 DONE 불가
    duration_sec: float = 0.0
```

> **병목 해소 지침**: `indexer.py:97-168`의 `index_file()`이 반환하는 raw symbol dict는 그대로 두되, Level2/3 진입 직전 어댑터 함수 `to_symbol_ref(raw: dict) -> SymbolRef`를 `agent_core/plan/` 내부에 신설하여 스키마 변환을 명시적 단일 지점으로 고정한다. Task Graph는 절대 raw indexer dict를 직접 참조하지 않는다.

### 3.3 핵심 인터페이스 (ABC)

```python
# [📂 실제경로] agent_core/plan/planner.py

from abc import ABC, abstractmethod
from agent_core.plan.schemas import Task


class MasterPlanner(ABC):
    @abstractmethod
    def decompose(self, user_request: str, codebase_map_path: str) -> list[Task]:
        """AI_CODEBASE_MAP.md와 Project Memory만 참조하여 Task 목록을 생성한다.
        원본 소스 코드 파일을 직접 읽지 않는다 (Level2 제약).
        [v1.1] 각 Task는 debug_log_plan / standalone_entrypoint / predicted_summary가
        전부 채워진 상태로 반환되어야 한다 — 하위 Worker에게 '무엇을 왜 얼마나' 수정할지
        전부 미리 떠먹여주는 것이 Level2의 핵심 책무다."""
        raise NotImplementedError
```

```python
# [📂 실제경로] agent_core/plan/task_graph.py  (신규 파일)

from abc import ABC, abstractmethod
from agent_core.plan.schemas import Task


class TaskGraph(ABC):
    @abstractmethod
    def add_task(self, task: Task) -> None: ...

    @abstractmethod
    def get_ready_tasks(self) -> list[Task]:
        """dependencies가 모두 DONE인 Task만 반환."""
        raise NotImplementedError

    @abstractmethod
    def mark_status(self, task_id: str, status: str) -> None: ...
```

```python
# [📂 실제경로] agent_core/execution/conflict_manager.py  (신규 파일)

from abc import ABC, abstractmethod
from agent_core.plan.schemas import Task


class ConflictManager(ABC):
    @abstractmethod
    def predict_conflicts(self, tasks: list[Task]) -> dict[str, list[str]]:
        """Read/Write Set 교집합만으로 충돌을 예측한다.
        반환값: {task_id: [충돌하는 다른 task_id 목록]}
        코드 본문은 참조하지 않는다 (Level7 제약, plan1.md 명세 반영)."""
        raise NotImplementedError

    @abstractmethod
    def replan(self, tasks: list[Task], conflicts: dict[str, list[str]]) -> list[Task]:
        """충돌이 예측된 Task들의 우선순위/의존성을 재배치한다."""
        raise NotImplementedError
```

```python
# [📂 실제경로] agent_core/validation/validator.py  (신규 파일)

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ValidationReport:
    passed: bool
    stage: str                 # "import" | "build" | "static" | "type" | "unit_test" | "runtime" | "predicted_output"
    errors: list[str]
    recommendation: str        # Reflection(Level10)에 바로 전달될 요약


class Validator(ABC):
    @abstractmethod
    def run_all(self, patch_path: str) -> list[ValidationReport]:
        """[v1.1] ase_os_config.yaml의 level9_validator.require_predicted_output_match가
        true인 경우, 마지막 stage로 §3.5 StandaloneExecutionValidator 결과를 반드시 포함한다.
        해당 stage가 실패하면 다른 stage가 전부 통과해도 Task는 DONE으로 전이할 수 없다."""
        raise NotImplementedError
```

### 3.5 디버깅 로그 예측-검증 시스템 (Predictive Debug-Log Verification)

**설계 의도**: "코드가 돌아간다"와 "의도대로 동작한다"는 다르다. 이를 자동으로 구분하기 위해, 계획(Plan) 단계에서부터 Planner가 "이 지점에 이 로그를 심고, 그러면 이런 출력이 나와야 정상이다"까지 전부 예측해서 Task에 못 박아 넣는다. Worker는 그 명세대로 로그를 심고, 전체 앱을 띄우는 대신 **해당 파일/함수만 단독실행**해서 출력을 뽑아내고, Planner의 예측치와 대조한다. 일치해야만 그 Task는 "설계 완료"로 인정된다.

이 구조의 부가 효과: 나중에 여러 Task 결과물이 합쳐질 때, 병합 담당(Level7/8/9)은 각 Task 계획서에 적힌 `predicted_output_pattern`을 그대로 다시 돌려보는 것만으로 "이 조각이 여전히 의도대로 동작하는지"를 빠르게 재확인할 수 있다. 또한 AI가 완벽하게 작업하지 못했더라도, 최종 코드에 남는 디버깅 로그 자체가 사람이 직접 디버깅할 때 유용한 흔적으로 남는다.

```python
# [📂 실제경로] agent_core/execution/standalone_runner.py  (신규 파일)

from abc import ABC, abstractmethod
from agent_core.plan.schemas import Task, ExecutionResult


class StandaloneExecutionValidator(ABC):
    @abstractmethod
    def run_standalone(self, task: Task, patch_path: str) -> ExecutionResult:
        """task.standalone_entrypoint 로 지정된 커맨드를 격리된 subprocess에서 실행한다.
        - 전체 파이프라인(start.py 등)을 기동하지 않는다.
        - ase_os_config.yaml: debug_log_system.standalone_execution.timeout_sec 초과 시 강제 종료.
        - 부작용 있는 I/O(외부 API 호출, DB write 등)는 반드시 mock으로 대체되어 있어야 하며,
          mock이 없는 상태로 실행되는 것을 감지하면 즉시 FAILED 처리한다."""
        raise NotImplementedError

    @abstractmethod
    def match_predicted_output(
        self, result: ExecutionResult, task: Task
    ) -> tuple[bool, list[str]]:
        """task.debug_log_plan의 각 DebugLogSpec.predicted_output_pattern을
        result.stdout/stderr에서 정규식 매칭한다.
        반환: (전부 매칭되었는가, 매칭 실패한 log_id 목록)"""
        raise NotImplementedError
```

**동작 절차 (요약)**

1. Level2 Master Planner가 Task 생성 시, 해당 Task가 건드릴 파일마다 `DebugLogSpec`(위치·로그문·예측 출력 패턴)을 확정해 `debug_log_plan`에 채운다.
2. Level5 Worker는 Patch를 만들 때 `debug_log_plan`에 적힌 로그를 **정확히 지정된 위치에, 지정된 토글 키로** 삽입한다. 임의 위치·임의 문구 삽입은 §3.4 규칙 6에 의해 반려된다.
3. Level9 Validator가 기존 import/build/test 단계를 통과시킨 뒤, 마지막으로 `StandaloneExecutionValidator.run_standalone()`을 호출해 해당 파일/함수만 단독 실행한다.
4. `match_predicted_output()`으로 실제 출력과 Planner의 예측 패턴을 대조한다. 전부 일치해야 Task가 `DONE`으로 전이한다. 하나라도 불일치하면 `FAILED` 처리 후 Level10 Reflection에 "예측 대비 실제 출력 차이"를 그대로 넘긴다(§3.2 `predicted_summary` 활용).
5. 로그 자체는 삭제하지 않고 최종 합본 코드에 남긴다. `debug_log_system.global_toggle_env`(예: `ASE_DEBUG`) 하나로 전체를 켜고 끌 수 있으며, Task별 개별 토글(`toggle_key`)로 세분화된 on/off도 가능하다.

### 3.6 파일 단위 락(Lock) 안전구조 (Level4 Manager Layer 확장)

**설계 의도**: 여러 Worker(또는 여러 터미널)가 동시에 도는 것 자체는 허용하되, **동일 파일**에 대한 동시 쓰기만은 절대 허용하지 않는다. 속도보다 안전을 우선하는 구조이며, 이미 다른 에이전트가 작업 중인 파일에 대한 Task는 그 파일이 풀릴 때까지 대기한다.

```python
# [📂 실제경로] agent_core/execution/file_lock.py  (신규 파일)

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LockInfo:
    file_path: str          # [📂 실제경로] 규격
    owner_task_id: str
    owner_session_id: str   # [v1.1] 어느 터미널 세션이 잡았는지 (§3.7과 연동)
    acquired_at: float       # UNIX timestamp


class FileLockManager(ABC):
    @abstractmethod
    def acquire(self, file_path: str, task_id: str, session_id: str) -> bool:
        """락 획득 시도. 이미 잠겨 있으면 False를 즉시 반환한다(블로킹하지 않음 —
        대기/재시도 정책은 Manager Layer의 호출부가 wait_strategy에 따라 결정)."""
        raise NotImplementedError

    @abstractmethod
    def release(self, file_path: str, task_id: str) -> None: ...

    @abstractmethod
    def get_lock(self, file_path: str) -> Optional[LockInfo]: ...

    @abstractmethod
    def sweep_stale_locks(self, max_age_sec: int) -> list[str]:
        """비정상 종료로 반환되지 않은 락을 정리한다. 반환값: 정리된 file_path 목록."""
        raise NotImplementedError
```

**Manager Layer 동작 규칙**

* Task가 `get_ready_tasks()`로 올라오면, Manager는 해당 Task의 `write_set` 파일 전부에 대해 `acquire()`를 시도한다.
* 하나라도 실패하면 `ase_os_config.yaml: level4_manager_layer.file_lock.wait_strategy`에 따라:
  * `block_until_free`: Task를 `BLOCKED` 상태로 두고 폴링 대기 (기본값)
  * `queue_and_reorder`: Task Graph에 우선순위를 낮춰 재삽입, 다른 Ready Task를 먼저 처리
  * `fail_fast`: 즉시 Planner에 재계획(replan) 요청
* `max_wait_sec` 초과 시 무조건 `BLOCKED` → Planner 재계획 요청으로 승격(무한 대기 방지).
* Task 완료(DONE/FAILED 확정) 즉시 `release()` 호출은 필수이며, 이를 누락한 Worker 구현은 §3.4 규칙 7로 반려한다.
* 락 정보는 `system_memory/locks/*.lock` (JSON)에 영속화되어, 프로세스 재시작 후에도 잔류 락을 `sweep_stale_locks()`로 복구 가능해야 한다.

### 3.7 교차 세션(멀티 터미널) 병합 시스템

**설계 의도**: 한 사람이 여러 터미널에서 각각 독립적으로 Planner를 돌려 서로 다른(혹은 겹치는) 작업을 동시에 진행할 수 있다. 각 세션은 자기 안에서 Level7(Conflict)/Level8(Semantic Merge)까지 끝내 "로컬 완료" 상태가 되고, 이후 다른 세션의 존재가 감지되면 두 세션의 로컬 완료 결과물끼리 한 단계 더 높은 수준에서 병합된다. 즉, Level7/8을 Task 단위가 아니라 **세션 단위**로 한 번 더 재적용하는 구조다.

```python
# [📂 실제경로] agent_core/plan/session_registry.py  (신규 파일)

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SessionInfo:
    session_id: str
    project_root: str
    terminal_label: str          # 사람이 구분하기 위한 표시명 (예: "터미널-A")
    write_set_paths: list[str] = field(default_factory=list)  # 이 세션이 건드리는 파일 전체 경로
    status: str = "active"       # "active" | "local_merge_done" | "cross_merged" | "closed"
    last_heartbeat: float = 0.0


class SessionRegistry(ABC):
    @abstractmethod
    def register_session(self, session: SessionInfo) -> None: ...

    @abstractmethod
    def heartbeat(self, session_id: str) -> None:
        """ase_os_config.yaml: multi_session_merge.heartbeat_interval_sec 주기로 호출.
        일정 시간 heartbeat가 없으면 죽은 세션으로 간주하고 목록에서 제외."""
        raise NotImplementedError

    @abstractmethod
    def list_active_sessions(self, exclude_session_id: str) -> list[SessionInfo]: ...

    @abstractmethod
    def detect_overlap(self, session_id: str) -> list[SessionInfo]:
        """multi_session_merge.overlap_detection 전략(기본: write_set_path_prefix)에 따라
        write_set 경로가 겹치는 다른 활성 세션을 찾아 반환한다."""
        raise NotImplementedError


class CrossSessionMergeCoordinator(ABC):
    @abstractmethod
    def wait_for_local_merge(self, session_id: str) -> bool:
        """자신의 세션이 Level7/8 로컬 병합을 끝냈는지 확인."""
        raise NotImplementedError

    @abstractmethod
    def merge_sessions(self, session_a: SessionInfo, session_b: SessionInfo) -> str:
        """두 세션이 모두 local_merge_done 상태일 때만 호출 가능.
        각 세션의 결과물을 별도 git 브랜치로 간주하고, ConflictManager/SemanticMerge를
        '파일 단위'가 아닌 '세션 산출물 단위'로 재적용해 최종 병합 브랜치를 만든다.
        반환값: 병합된 브랜치/커밋 참조."""
        raise NotImplementedError
```

**동작 절차 (요약)**

1. 터미널에서 Master Planner가 기동될 때마다 `SessionRegistry.register_session()`으로 자신을 등록하고, 주기적으로 `heartbeat()`를 보낸다.
2. 각 세션은 자신의 Task Graph가 전부 `DONE` + 로컬 Level7/8 병합까지 끝나면 상태를 `local_merge_done`으로 바꾸고 `AWAITING_MERGE` 상태로 대기한다.
3. `detect_overlap()`이 write_set 경로가 겹치는 다른 활성/완료 세션을 발견하면, 두 세션 모두 `local_merge_done`이 될 때까지 기다린 뒤 `merge_sessions()`가 호출되어 최종 통합 브랜치를 만든다.
4. 겹치는 세션이 끝내 발견되지 않으면(서로 다른 프로젝트였거나 write_set이 겹치지 않음) 각 세션은 독립적으로 최종 완료 처리된다 — 강제로 병합을 기다리게 하지 않는다.
5. 기본값은 `multi_session_merge.enabled: false`다. 단일 터미널만 쓰는 사용자에게는 불필요한 오버헤드이므로, 여러 터미널을 동시에 굴릴 계획이 있을 때만 켠다.

### 3.4 코드 생략 방지 템플릿 제약

에이전트가 Patch를 생성할 때 아래 조건을 위반하면 Validator(Level9) 이전 단계에서 즉시 반려한다.

```
[REJECT RULES]
1. 정규식 `#\s*(TODO|FIXME|구현\s*예정|생략)` 매칭 시 즉시 반려.
2. 함수 본문이 `pass`, `...`, `raise NotImplementedError` 단독으로만 구성되어 있고
   해당 함수가 Task의 write_set에 포함된 경우 즉시 반려.
3. Task의 write_set에 명시된 심볼(symbol_id) 외 파일을 수정한 Patch는 즉시 반려
   (Read Set 외부 파일은 참조만 허용, 수정 불허).
4. `[📂 실제경로]` 헤더 주석이 없는 신규 파일은 즉시 반려.
5. 한 Patch는 20줄(라인 diff 기준) 이내로 제한 — 초과 시 Task를 자동 분할 요청.
6. [v1.1] Task의 write_set을 수정하는 Patch인데 `debug_log_plan`이 비어 있거나,
   Patch에 debug_log_plan에 명시된 로그 삽입이 하나라도 누락된 경우 즉시 반려.
7. [v1.1] Task가 DONE/FAILED로 전이하는 시점에 자신이 획득한 File Lock을
   release()하지 않는 Worker/Manager 구현은 즉시 반려(락 잔류로 인한 시스템 정지 방지).
8. [v1.1] standalone_entrypoint 없이 write_set을 3개 이상 포함하는 Task는 즉시 반려
   — 단독실행 검증이 불가능할 정도로 Task가 크다는 신호이므로 자동 분할 요청.
```

---

## 4. 점진적 부하 분산 로드맵 (13 Phase / 마이크로 리팩토링)

각 Phase는 diff 20줄 이내 단위로 쪼개 진행하며, Phase 완료 조건은 "빌드 성공 + 최소 1개 테스트 통과"로 고정한다.

| Phase | 목표 | 물리적 변경 파일 | 완료 조건 |
|---|---|---|---|
| 1 | §0 병목 해소: `SymbolRef`/`Task` dataclass 신설 | `agent_core/plan/schemas.py` (신규) | import 성공, 단위 테스트 1건 |
| 2 | 어댑터 함수 `to_symbol_ref()` 작성 (raw indexer dict → SymbolRef) | `agent_core/plan/schemas.py` 확장 | indexer 출력 100건 샘플 변환 성공 |
| 3 | `MasterPlanner` ABC + `use_planner: false`일 때 수동 JSON 입력 폴백 구현 | `agent_core/plan/planner.py` | ase_os_config.yaml 스위치 온오프 동작 확인 |
| 4 | `TaskGraph` ABC + 최소 DAG (add/get_ready/mark_status) | `agent_core/plan/task_graph.py` (신규) | 3개 Task 의존성 그래프 순회 테스트 통과 |
| 5 | Worker 2개 병렬 실행 (기존 gemini_client.py 스텁 실체화) | `agent_core/plan/gemini_client.py` | 동시 2 Patch 생성, 파일 충돌 없음 |
| 6 | `ConflictManager.predict_conflicts()` — write_set 교집합 검사만 구현 | `agent_core/execution/conflict_manager.py` (신규) | 인위적 충돌 시나리오 2건 탐지 성공 |
| 7 | Semantic Merge 최소 버전 (Intent 태그 기반 단순 병합) | `agent_core/execution/semantic_merge.py` (신규) | Patch A/B 병합 후 import 성공 |
| 8 | `Validator.run_all()` — import + build 2단계만 우선 구현 | `agent_core/validation/validator.py` (신규) | 고의 ImportError 케이스 탐지 |
| 9 | Reflection 최소 버전 — ValidationReport → 1문장 recommendation 생성 | `agent_core/execution/reflection.py` (신규) | 동일 ImportError 재발생률 감소 확인 |
| 10 | Project Memory 영속화 — 실패이력/빌드이력 JSON 스키마 확정 | `system_memory/task_history.json` (신규 스키마) | 재시작 후 이전 실패 이력 조회 성공 |
| **11** | **[v1.1]** File Lock Manager 구현 — Manager Layer가 write_set 파일에 락 획득/대기/해제 | `agent_core/execution/file_lock.py` (신규) | Worker 2개가 동일 파일 write_set을 가진 Task 동시 투입 시, 한쪽이 정상 대기 후 순차 처리됨을 확인 |
| **12** | **[v1.1]** 디버깅 로그 예측-검증 파이프라인 — `DebugLogSpec`/`StandaloneExecutionValidator` 구현, Level9에 통합 | `agent_core/execution/standalone_runner.py` (신규), `agent_core/validation/validator.py` 확장 | Planner가 예측한 출력 패턴과 실제 단독실행 출력이 3개 샘플 Task에서 100% 매칭 |
| **13** | **[v1.1]** Session Registry + Cross-Session Merge Coordinator — 2개 터미널 시뮬레이션으로 검증 | `agent_core/plan/session_registry.py` (신규) | 서로 다른 두 프로세스가 겹치는 write_set을 가진 Task를 각각 완료 후, 자동으로 병합 브랜치 1개 생성 확인 |

> Evolution Layer(Level11)는 Phase 1~13 완료 후 별도 Phase 14로 이연한다 (plan1.md의 로드맵 우선순위 유지, 조기 확장으로 인한 결합도 증가 방지). Manager Layer(Level4) 기본 골격은 Phase 11에서 File Lock과 함께 최초 구현되며, 순수 디스패치 로직 고도화는 이후 별도 이슈로 분리한다.

---

## 5. 부록 — 경로 참조 무결성 체크리스트

에이전트는 코드 수정 제안 전 아래를 자가 검증한다.

- [ ] 참조한 모든 파일 경로가 `AI_CODEBASE_MAP.md`의 `[📂 실제경로]`와 문자 단위로 일치하는가?
- [ ] `SCAN_MODE`(switch.py) 값에 따라 `PROJECT_ROOT` 계산 로직이 indexer.py / create_ai_map.py 간에 상이할 수 있음을 인지했는가?
- [ ] 수정 대상 심볼이 Task의 `write_set`에 정확히 등록되어 있는가?
- [ ] 신규 파일 생성 시 `agent_core/{plan,execution,memory,validation}/` 기존 디렉토리 구조를 재사용했는가 (불필요한 신규 폴더 생성 금지)?
- [ ] **[v1.1]** 이 Task의 `debug_log_plan`이 채워져 있고, Patch가 그 명세(위치·문구·토글키)를 정확히 반영했는가?
- [ ] **[v1.1]** `standalone_entrypoint`로 지정된 커맨드가 실제로 전체 파이프라인 없이 단독 실행 가능한가 (외부 I/O는 mock 처리되었는가)?
- [ ] **[v1.1]** Task 완료/실패 확정 직전, 이 Task가 획득했던 File Lock을 전부 `release()` 했는가?
- [ ] **[v1.1]** `multi_session_merge.enabled: true`인 환경이라면, 이 세션의 `write_set_paths`가 `SessionRegistry`에 최신 상태로 등록되어 있는가?
