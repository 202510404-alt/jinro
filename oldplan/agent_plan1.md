# 🏗️ plan_final.md — ASE-OS Single Source of Truth (v1.0)

> **[전 에이전트 필독 / 최우선순위 문서]**
> 본 문서는 프로젝트 최상위에 위치하는 단 하나의 진실 공급원(SSOT)이다.
> 모든 AI 에이전트(Planner, Worker, Manager, Validator 등)는 코드 수정 전 반드시 본 문서의 §2(스위치 맵), §3(인터페이스 규격)을 파싱하고 준수해야 한다.
> 경로는 예외 없이 `AI_CODEBASE_MAP.md`의 `[📂 실제경로]` 표기를 그대로 사용한다. 축약·추측·상대경로 임의 변경 금지.

---

## ⚠️ 0. 사전 정밀 분석 타겟팅 (병목 선언)

* **정밀 분석 타겟팅**: `cline_tools/indexer.py:97-168` (이유: `index_file()`이 생성하는 심볼 스키마에 `read_set`/`write_set`/`dependency`/`confidence`/`owner` 필드가 없어, Level2(Master Planner)·Level3(Task Graph)가 필요로 하는 계획 단위 메타데이터를 즉시 소비하지 못하고 별도 변환 계층을 요구하는 구조적 병목이 발생함)

부가 리스크 지점(참고용, 우선순위는 위보다 낮음):
* `cline_tools/jjap_retriever.py:39-98` — `retrieve_symbol()`이 단일 심볼 단위로만 동작. Task Graph가 여러 Task의 Read Set을 묶어 배치 조회할 인터페이스가 없어 Level5→Level6 연동 시 N+1 호출 문제 예상.
* `cline_tools/create_ai_map.py:168-236` — `AI_CODEBASE_MAP.md` 생성이 전체 파일 재스캔 방식(Full Rewrite)이라, Task Graph 규모가 커지면 증분(incremental) 갱신 부재로 인한 지연이 예상됨.

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

### 1.2 레이어별 종합 진단

```
Level 0  Knowledge Layer      ████████░░  80%  (Indexer/Map/Retriever 프로토타입 완성)
Level 1  Project Memory       ███░░░░░░░  30%  (JSON 장부는 있으나 실패이력/빌드이력 스키마 부재)
Level 2  Master Planner       ░░░░░░░░░░   0%  (미착수)
Level 3  Task Graph           ░░░░░░░░░░   0%  (미착수)
Level 4  Manager Layer        ░░░░░░░░░░   0%  (미착수)
Level 5  Worker Agents        ░░░░░░░░░░   0%  (미착수, gemini_client.py 등은 스텁 수준)
Level 6  Live Retriever       ██░░░░░░░░  20%  (jjap_retriever 단일조회만 가능)
Level 7  Conflict Manager     ░░░░░░░░░░   0%  (미착수)
Level 8  Semantic Merge       ░░░░░░░░░░   0%  (미착수)
Level 9  Validator            ░░░░░░░░░░   0%  (agent_core/validation/ 폴더만 존재, 빈 __init__)
Level 10 Reflection           ░░░░░░░░░░   0%  (미착수)
Level 11 Evolution Layer      ░░░░░░░░░░   0%  (미착수)
```

### 1.3 핵심 구조적 결함 (치명도 순)

1. **스키마 불일치**: `indexer.py`의 symbol 스키마(`symbol_id`, `range`, `calls`, `used_by`)는 Task Graph가 요구하는 `Read Set / Write Set / Dependency / Confidence / Owner`를 포함하지 않음. → §0 병목과 동일 지점.
2. **경로 이중 기준**: `SCAN_MODE`(switch.py)가 "ROOT"/"SRC" 두 가지 기준을 가지며, `indexer.py`는 `PROJECT_ROOT = SCRIPT_DIR.parent`로 고정 계산하는 반면 `create_ai_map.py`는 `SCRIPT_DIR.name == "cline_tools"` 조건부 계산을 사용함. 두 파일의 루트 계산 로직이 미묘하게 다르므로 향후 Task Graph가 두 로직 중 무엇을 신뢰할지 충돌 가능.
3. **agent_core/ 스텁 상태**: `agent_core/plan/`, `agent_core/validation/`, `agent_core/execution/`, `agent_core/memory/` 폴더가 이미 존재하지만 `__init__.py`만 있고 실질 코드 없음 → Level2/Level9의 물리적 착지 위치는 이미 확보되어 있음(디렉토리 재사용 가능).

---

## 2. 실험용 글로벌 스위치 맵 (YAML)

```yaml
# ase_os_config.yaml
# [📂 실제경로] project_root/ase_os_config.yaml (신규 생성 필요)

ase_os:
  version: "1.0"

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

    level3_task_graph:
      enabled: false
      fallback: "single_task_mode"   # OFF 시: 그래프 없이 Task 1개만 순차 처리(기존 파이프라인과 동일)

    level4_manager_layer:
      enabled: false
      fallback: "direct_worker_dispatch"  # OFF 시: Task Graph가 Worker를 직접 호출

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

    level10_reflection:
      enabled: false
      fallback: "raw_error_passthrough"  # OFF 시: 구조화 리포트 없이 원본 stacktrace만 Planner에 전달

    level11_evolution:
      enabled: false
      fallback: "static_ruleset"      # OFF 시: Conflict Rule/Prompt 고정, 자가개선 없음

  measurement:
    track_success_rate: true
    track_token_usage: true
    track_api_calls: true
    track_execution_time: true
    track_import_errors: true
    track_runtime_errors: true
```

**규칙**: 각 레이어는 상위 레이어가 OFF일 때 자신의 입력을 fallback 경로에서 받도록 구현해야 하며, 레이어 간 직접 import는 금지하고 반드시 §3의 인터페이스(ABC)를 경유한다.

---

## 3. 인터페이스 규격화 (환각 방지 백본)

### 3.1 공통 계약 원칙

* 모든 핵심 클래스는 `abc.ABC`를 상속하고 `@abstractmethod`로 계약을 강제한다.
* 모든 공개 메서드는 `typing`으로 완전한 타입 힌팅을 명시한다 (인자·반환값 모두).
* **주석으로 로직을 대체하는 것을 금지**한다 — `# TODO: implement later`, `pass  # 구현 예정` 같은 스텁은 CI에서 정적 검사로 차단한다 (§3.4 참조).
* 모든 구현체는 파일 상단에 `# [📂 실제경로]` 주석을 명시해 자기 위치를 스스로 증명해야 한다 (경로 왜곡 방지).

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
    BLOCKED = "blocked"
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
        원본 소스 코드 파일을 직접 읽지 않는다 (Level2 제약)."""
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
    stage: str                 # "import" | "build" | "static" | "type" | "unit_test" | "runtime"
    errors: list[str]
    recommendation: str        # Reflection(Level10)에 바로 전달될 요약


class Validator(ABC):
    @abstractmethod
    def run_all(self, patch_path: str) -> list[ValidationReport]:
        raise NotImplementedError
```

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
```

---

## 4. 점진적 부하 분산 로드맵 (10 Phase / 마이크로 리팩토링)

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

> Manager Layer(Level4)와 Evolution Layer(Level11)는 Phase 1~10 완료 후 별도 Phase 11~12로 이연한다 (plan1.md의 로드맵 우선순위 유지, 조기 확장으로 인한 결합도 증가 방지).

---

## 5. 부록 — 경로 참조 무결성 체크리스트

에이전트는 코드 수정 제안 전 아래를 자가 검증한다.

- [ ] 참조한 모든 파일 경로가 `AI_CODEBASE_MAP.md`의 `[📂 실제경로]`와 문자 단위로 일치하는가?
- [ ] `SCAN_MODE`(switch.py) 값에 따라 `PROJECT_ROOT` 계산 로직이 indexer.py / create_ai_map.py 간에 상이할 수 있음을 인지했는가?
- [ ] 수정 대상 심볼이 Task의 `write_set`에 정확히 등록되어 있는가?
- [ ] 신규 파일 생성 시 `agent_core/{plan,execution,memory,validation}/` 기존 디렉토리 구조를 재사용했는가 (불필요한 신규 폴더 생성 금지)?
