# [SYSTEM PROTOCOL: PLAYER SUBSYSTEM INTEGRATION & REFRACTORING]
당신은 게임 엔진 프레임워크 내에서 플레이어 컴포넌트(입력, 물리, 전투, 데이터 모델, 메인 관제) 간의 파괴된 데이터 흐름을 동기화하고, 시스템을 델타 타임(Delta Time) 기반 가변 프레임 독립 구조로 완전히 개편하는 소프트웨어 아키텍트 에이전트입니다.

## 🚨 현재 시스템의 치명적인 문제점 (작업 목적)
현재 플레이어 모듈들은 단독으로는 정상처럼 보이나, 상호 호출 구조가 완전히 어긋나 있습니다:
1. `player_main.py`가 `combat_processor.py`를 호출할 때 필수 인자(dt, entities)를 누락하여 TypeError 크래시가 납니다.
2. `input_handler.py`가 외부 `keys` 매개변수를 무력화하고 `vars_obj.x` 좌표를 직접 조작하여, 중앙 물리 엔진의 무결성을 파괴하고 주사율 불일치 버그를 유발합니다.
3. `variables.py`에 물리 연산용 속도(`vx`, `vy`)와 가변 애니메이션 딜레이 맵이 누락되어 다른 모듈 참조 시 AttributeError 크래시가 터집니다.

이 상호 참조 모순 체계를 단 한 번의 수정으로 완벽히 결합하고 컴포넌트 간 단일 책임 원칙(SRP)을 정렬하십시오.

---

## 🛠️ 모듈별 상세 수정 및 추가 명세

### 1. [📂 src/player/variables.py] - 데이터 모델 재정비
- **물리 가속도 변수 보충**: 관성 마찰력 및 델타 타임 연산의 중심축이 될 `self.vx = 0.0` 및 `self.vy = 0.0` 변수를 필수적으로 선언하십시오.
- **전투 확장성 확보**: `combat_processor.py` v1.3이 가변 데미지 연산을 수행할 수 있도록 기본 데미지 변수 `self.attack_damage = 15`를 명시적으로 추가하십시오.
- **콤보 애니메이션 제어 확장**: 단일 'ATTACK' 연출 외에도 콤보 단계별(1타, 2타, 3타) 프레임 재생 속도를 정밀하게 개별 통제할 수 있도록 `self.state_delays` 딕셔너리에 `"ATTACK_1": 5, "ATTACK_2": 5, "ATTACK_3": 5` 쌍을 사전 대비용으로 확장해 두십시오.

### 2. [📂 player/input_handler.py] - 입력 의도 캡슐화 및 하드코딩 제거
- **캡슐화 복구**: 함수 내부에서 `keys = pygame.key.get_pressed()`로 로컬 키보드를 재조회하여 외부 매개변수를 덮어쓰던 치명적인 오류 코드를 완전히 제거하십시오. 오직 인자로 전달된 `keys` 객체만 신뢰해야 합니다.
- **단일 책임 원칙(SRP) 적용**: `vars_obj.x -= current_speed` 등 플레이어의 물리 좌표를 직접 변조(순간이동)하던 코드를 완벽히 삭제하십시오. 입력 핸들러는 사용자가 움직이려고 한다는 의사 플래그(`vars_obj.is_moving = True`)와 바라보는 방향(`facing_right`) 상태 전환만 제어해야 합니다.
- **콤보 타이머 안전망**: `trigger_attack` 메서드 내부에서 콤보 유효 시간이 소진되었을 때(`vars_obj.combo_timer <= 0`) 콤보 단계를 1타로 안전하게 리셋해주는 예외 분기 로직과 `combo_timer` 공급 로직을 누락 없이 보완하십시오.

### 3. [📂 src/player/player_main.py] - 중앙 제어 링킹 및 dt 보정 통합
- **메서드 인터페이스 갱신**: 메인 루프와의 델타 타임 동기화를 위해 `update` 메서드가 가변 프레임 스케일러인 `dt`와 주변 적 목록인 `entities`를 접수할 수 있도록 시그니처를 `def update(self, platforms, entities=None, game_map=None, dt=1.0/60.0):`로 개편하십시오.
- **관성 물리 메커니즘 통합**: 입력 핸들러가 넘겨준 `is_moving` 플래그를 바탕으로 `fps_scale = dt * 60.0` 가중치를 산출한 뒤, 플레이어의 속도(`vx`)를 가속하거나 입력이 끊겼을 때 부드럽게 감속하는 관성 마찰력(`self.vars.vx *= max(0.0, 1.0 - (0.35 * fps_scale))`) 로직을 여기서 중앙 집권화하고, 최종적으로 `self.vars.x += self.vars.vx * fps_scale` 연산을 수행하십시오.
- **인터페이스 충돌 해결**: 서브 엔진들을 구동할 때 타 모듈의 요구 사양에 완벽히 맞추어 `self.physics_engine.process(self.vars, platforms, game_map=game_map, dt=dt)` 및 `self.combat_engine.process(self.vars, entities=entities, dt=dt)` 형태로 파라미터를 누락 없이 완벽 매핑하여 호출하십시오.
- **콤보 타이머 실시간 감산**: 매 프레임 `self.vars.combo_timer -= fps_scale` 연산을 수행하여 시간이 지남에 따라 공격 콤보 연계가 정상적으로 만료 및 초기화되도록 동기화 루프를 완성하십시오.
- **애니메이션 스케일러 적용**: 프레임 누적 변수인 `self.vars.anim_timer`에 고정치 `1`이 아닌 프레임 가중치 `fps_scale`을 누적하여, 고주사율 모니터에서도 애니메이션이 비정상적으로 빨라지지 않고 일정한 틱 속도를 유지하도록 보정하십시오.

---

## 📋 OUTPUT FORMAT & CONSTRAINTS
- 위 가이드를 만족하도록 `variables.py`, `input_handler.py`, `player_main.py` 세 파일의 최종 수정본 전체 코드를 생략(Snippet) 없이 완전하게 한 번에 작성해 주세요.
- 모든 연산은 `dt` 기반의 가변 프레임 독립성(Frame Independence) 규칙을 완벽하게 준수해야 합니다.
- 기존의 안정화 버전 컴포넌트들(`physics_processor.py`, `combat_processor.py`)이 요구하는 파라미터 규격을 단 하나도 빠뜨리지 말고 완벽히 공급하십시오.