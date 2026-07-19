# 🏗️ 짭커서 프로젝트 CODEBASE MAP

현재 인덱싱된 총 파일 수: **52개**

## 🗂️ [Module Index]
- `extraction_target_project/assets/data/dialogues.json`
- `extraction_target_project/camera.py`
- `extraction_target_project/dialogue_system/dialogue_manager.py`
- `extraction_target_project/enemy/enemys/dummy/__init__.py`
- `extraction_target_project/enemy/enemys/dummy/dummy_main.py`
- `extraction_target_project/enemy/enemys/dummy/variables.py`
- `extraction_target_project/enemy/enemys/test_enemy1/__init__.py`
- `extraction_target_project/enemy/enemys/test_enemy1/test_enemy1_main.py`
- `extraction_target_project/enemy/enemys/test_enemy1/variables.py`
- `extraction_target_project/event_system/actions/move_map.py`
- `extraction_target_project/event_system/actions/play_dialogue.py`
- `extraction_target_project/event_system/actions/spawn_ambush.py`
- `extraction_target_project/event_system/triggers/enemy_clear.py`
- `extraction_target_project/event_system/triggers/npc_interact.py`
- `extraction_target_project/event_system/triggers/zone_enter.py`
- `extraction_target_project/fabric_system/editor_objects.json`
- `extraction_target_project/main.py`
- `extraction_target_project/map_editor_tool/__init__.py`
- `extraction_target_project/map_editor_tool/editor_main.py`
- `extraction_target_project/map_editor_tool/event_discover.py`
- `extraction_target_project/map_editor_tool/input_handler.py`
- `extraction_target_project/map_editor_tool/map_editor.py`
- `extraction_target_project/map_editor_tool/map_selector.py`
- `extraction_target_project/map_editor_tool/object_registry.py`
- `extraction_target_project/map_editor_tool/renderer.py`
- `extraction_target_project/map_editor_tool/selection.py`
- `extraction_target_project/map_editor_tool/serializer.py`
- `extraction_target_project/map_system/__init__.py`
- `extraction_target_project/map_system/map_engine.py`
- `extraction_target_project/map_system/map_main.py`
- `extraction_target_project/map_system/map_settings.py`
- `extraction_target_project/map_system/maps/map_1.json`
- `extraction_target_project/map_system/maps/map_editor_draft.json`
- `extraction_target_project/map_system/maps/map_stage1.json`
- `extraction_target_project/map_system/variables.py`
- `extraction_target_project/platform_system/__init__.py`
- `extraction_target_project/platform_system/platform_main.py`
- `extraction_target_project/platform_system/platform_settings.py`
- `extraction_target_project/platform_system/variables.py`
- `extraction_target_project/player/__init__.py`
- `extraction_target_project/player/asset_loader.py`
- `extraction_target_project/player/combat_processor.py`
- `extraction_target_project/player/input_handler.py`
- `extraction_target_project/player/motions/__init__.py`
- `extraction_target_project/player/motions/air_motions.py`
- `extraction_target_project/player/motions/attack_motions.py`
- `extraction_target_project/player/motions/ground_motions.py`
- `extraction_target_project/player/motions/motion_base.py`
- `extraction_target_project/player/physics_processor.py`
- `extraction_target_project/player/player_main.py`
- `extraction_target_project/player/variables.py`
- `extraction_target_project/settings.py`

## 💀 [Skeleton & Dependency 명세서]
### 📄 extraction_target_project/assets/data/dialogues.json
#### 🧱 Code Skeleton:
```python
📦 [JSON STRUCTURE MAP]
  ├── "stage1_start_chat": List (len: 3)
  ├── "stage1_clear_chat": List (len: 2)
```

--------------------------------------------------

### 📄 extraction_target_project/camera.py
#### 🧱 Code Skeleton:
```python
class ElasticCamera:
    """
    Dynamic Camera Smoothing / Elastic Camera

    - 기본 원리: Camera_Pos += (Target_Pos - Camera_Pos) * lerp_factor
    - dt(초) 기반으로 보정해 FPS가 달라져도 체감이 비슷하게 유지되도록 처리합니다.
    """

    def __init__(
        self,
        viewport_w: int,
        viewport_h: int,
        *,
        smoothing: float = 0.01,
        deadzone_w: int = 30,
        deadzone_h: int = 20,
        max_speed_px_per_sec: float | None = None,
    ):
        # 카메라가 "바라보려는 중심점" (월드 좌표, float 유지)
        self.x = 0.0
        self.y = 0.0

        self.viewport_w = viewport_w
        self.viewport_h = viewport_h

        self.smoothing = float(smoothing)

        self.deadzone_w = int(deadzone_w)
        self.deadzone_h = int(deadzone_h)

        self.max_speed_px_per_sec = max_speed_px_per_sec

    def set_center(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    @staticmethod
    def _frame_lerp(lerp_60fps: float, dt: float) -> float:
        lerp_60fps = max(0.0, min(1.0, float(lerp_60fps)))
        if dt <= 0:
            return 0.0
        return 1.0 - math.pow(1.0 - lerp_60fps, dt * 60.0)

    def update(
        self,
        target_x: float,
        target_y: float,
        dt: float,
        *,
        clamp_y_max: float | None = None,
    ):
        # 1) 순수한 플레이어 중심점을 기반으로 기본 목표점 설정
        desired_x = float(target_x)
        desired_y = float(target_y)

        # 2) 보정되지 않은 원래 목표점과의 차이(거리)를 기반으로 데드존 계산
        dx = desired_x - self.x
        dy = desired_y - self.y

        half_w = self.deadzone_w / 2.0
        half_h = self.deadzone_h / 2.0

        adj_dx = 0.0
        adj_dy = 0.0

        if dx > half_w:
            adj_dx = dx - half_w
        elif dx < -half_w:
            adj_dx = dx + half_w

        if dy > half_h:
            adj_dy = dy - half_h
        elif dy < -half_h:
            adj_dy = dy + half_h

        # [🌟 수정 핵심 1] 상시 보정 조건 검사
        # 현재 카메라 위치가 main에서 준 제한치보다 아래에 도달해 있다면 데드존 내부여도 강제로 움직이게 처리
        is_outside_clamp = (clamp_y_max is not None) and (self.y > float(clamp_y_max))

        if adj_dx == 0.0 and adj_dy == 0.0 and not is_outside_clamp:
            return

        final_target_x = self.x + adj_dx
        final_target_y = self.y + adj_dy

        # [🌟 수정 핵심 2] 데드존을 적용한 최종 목적지 단계에서 clamp_y_max를 걸어줍니다.
        # 이렇게 해야 main.py에서 의도한 땅의 노출 크기(마진)가 화면 하단에 그대로 유지됩니다.
        if clamp_y_max is not None:
            final_target_y = min(final_target_y, float(clamp_y_max))

        # 3) 거리 비례 Lerp 적용 (dt 보정 포함)
        a = self._frame_lerp(self.smoothing, dt)
        new_x = self.x + (final_target_x - self.x) * a
        new_y = self.y + (final_target_y - self.y) * a

        # 4) 속도 상한
        if self.max_speed_px_per_sec is not None and dt > 0:
            max_delta = float(self.max_speed_px_per_sec) * dt
            delta_x = new_x - self.x
            delta_y = new_y - self.y
            dist = math.hypot(delta_x, delta_y)
            if dist > max_delta and dist > 0:
                scale = max_delta / dist
                new_x = self.x + delta_x * scale
                new_y = self.y + delta_y * scale

        # 5) 최종 위치 안전망 클램핑 (시작 지점이 이미 제한선 밖인 경우의 급격한 Snapping 방지)
        if clamp_y_max is not None and self.y <= clamp_y_max:
            new_y = min(new_y, float(clamp_y_max))

        self.x = new_x
        self.y = new_y

    def get_offset(self) -> tuple[float, float]:
        return (self.x - self.viewport_w / 2.0, self.y - self.viewport_h / 2.0)
```

--------------------------------------------------

### 📄 extraction_target_project/dialogue_system/dialogue_manager.py
#### 🧱 Code Skeleton:
```python
class DialogueManager:
    """
    독립형 대사 시스템 엔진 (DialogueManager)
    대사 데이터를 캐싱 및 노드별로 제어하며 월드 정지 상태 제어 인터페이스를 지원합니다.
    """
    def __init__(self):
        self.dialogues = {}
        self.current_sequence = None
        self.current_index = 0
        self.is_active = False

        # 폰트 초기화 (한글 출력을 위해 나눔고딕, 맑은 고딕, 혹은 기본 폰트 바인딩)
        pygame.font.init()
        font_names = ["malgungothic", "nanumgothic", "nanumbrushouter", "notosanskorean", "arial", None]
        self.font_speaker = None
        self.font_text = None
        
        # 순차적으로 사용 가능한 한글 폰트 검색 및 초기화
        for f_name in font_names:
            try:
                self.font_speaker = pygame.font.SysFont(f_name, 32, bold=True)
                self.font_text = pygame.font.SysFont(f_name, 28)
                break
            except Exception:
                continue
        
        # 폴백 설정
        if not self.font_speaker:
            self.font_speaker = pygame.font.Font(None, 36)
            self.font_text = pygame.font.Font(None, 30)

        # 리소스 경로 자동 해결용 base_dir
        self.src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def load_dialogues(self, json_path=None):
        """대사 정보 캐싱"""
        if json_path is None:
            json_path = os.path.join(self.src_dir, "assets", "data", "dialogues.json")
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                self.dialogues = json.load(f)
            print(f"📖 [DialogueManager] {len(self.dialogues)}개의 대사 시퀀스를 성공적으로 로드했습니다.")
        except Exception as e:
            print(f"🚨 [DialogueManager] 대사 파일 로드 에러: {e}")
            self.dialogues = {}

    def start_dialogue(self, dialogue_id):
        """특정 대사 시퀀스 가동"""
        if dialogue_id not in self.dialogues:
            print(f"⚠️ [DialogueManager] 알 수 없는 대사 ID: {dialogue_id}")
            return False

        self.current_sequence = self.dialogues[dialogue_id]
        self.current_index = 0
        self.is_active = True
        print(f"💬 [DialogueManager] 대사 시작 -> ID: '{dialogue_id}' (총 {len(self.current_sequence)}줄)")
        
        # 첫 라인 이벤트/액션 감지 시 즉시 처리
        self._trigger_current_action()
        return True

    def next_line(self):
        """다음 대사로 진행"""
        if not self.is_active or not self.current_sequence:
            return

        self.current_index += 1
        if self.current_index >= len(self.current_sequence):
            self.end_dialogue()
        else:
            self._trigger_current_action()

    def end_dialogue(self):
        """대사 시퀀스 완료 및 비활성화"""
        self.current_sequence = None
        self.current_index = 0
        self.is_active = False
        print("💬 [DialogueManager] 대사 종료 -> 인게임 월드 정상 재개")

    def _trigger_current_action(self):
        """대사 노드에 부여된 특수 연출 액션 실행 구조"""
        if not self.current_sequence or self.current_index >= len(self.current_sequence):
            return
        node = self.current_sequence[self.current_index]
        action = node.get("action")
        if action:
            # Main이나 다른 시스템에서 받아 처리하도록 로그 혹은 이벤트 발행 구조로 설계
            print(f"🎬 [DialogueAction] 연출 트리거: {action}")

    def draw(self, screen):
        """대사창 UI 렌더링"""
        if not self.is_active or not self.current_sequence:
            return

        node = self.current_sequence[self.current_index]
        speaker = node.get("speaker", "???")
        text = node.get("text", "")
        portrait_key = node.get("portrait", "")

        # 1. 반투명 배경 대사 상자 (Virtual 해상도 1600x1200 기준 하단 배치)
        box_rect = pygame.Rect(100, 850, 1400, 300)
        
        # 반투명 효과를 위해 별도 서피스 사용
        box_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        box_surf.fill((20, 20, 30, 230))  # 짙은 남색 반투명
        pygame.draw.rect(box_surf, (150, 180, 220, 255), (0, 0, box_rect.width, box_rect.height), 4) # 하늘색 테두리
        screen.blit(box_surf, (box_rect.x, box_rect.y))

        # 2. 초상화 로드 (AssetManager를 무조건적으로 연동)
        portrait_path = os.path.join(self.src_dir, "assets", "images", "portraits", f"{portrait_key}.png")
        portrait_img = AssetManager.get_image(portrait_path)
        
        # 초상화 200x200으로 스케일링 후 배치
        scaled_portrait = pygame.transform.scale(portrait_img, (200, 200))
        screen.blit(scaled_portrait, (150, 900))

        # 3. 화자 이름 드로우
        speaker_surf = self.font_speaker.render(speaker, True, (255, 230, 150))
        screen.blit(speaker_surf, (380, 890))

        # 4. 말풍선 내 한국어 자동 줄바꿈(Text Wrapping) 및 렌더링
        max_text_w = 1050
        wrapped_lines = self._wrap_text(text, self.font_text, max_text_w)
        
        y_offset = 945
        for line in wrapped_lines:
            line_surf = self.font_text.render(line, True, (240, 240, 250))
            screen.blit(line_surf, (380, y_offset))
            y_offset += 40

        # 5. 다음 대사 지시자 표시 (깜빡이는 연출 생략용 고정 키 가이드)
        prompt_surf = self.font_text.render("[ Space or Enter ]", True, (150, 180, 220))
        screen.blit(prompt_surf, (1300, 1100))

    def _wrap_text(self, text, font, max_width):
        """글자 너비 기반 한국어 글자 단위 자동 줄바꿈 알고리즘"""
        lines = []
        current_line = ""
        for char in text:
            test_line = current_line + char
            width, _ = font.size(test_line)
            if width > max_width:
                lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        return lines
```

--------------------------------------------------

### 📄 extraction_target_project/enemy/enemys/dummy/__init__.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/enemy/enemys/dummy/dummy_main.py
#### 🧱 Code Skeleton:
```python
class DummyEnemy:
    def __init__(self, x=0, y=0, *args, **kwargs):
        # 🎯 [기능 보존 + 호환성 확장] 어떤 데이터 규격(값, dict 등)으로 들어와도 안전하게 x, y 좌표 바인딩
        actual_x = x if x != 0 else kwargs.get("x", 0)
        actual_y = y if y != 0 else kwargs.get("y", 0)
        
        # 맵 시스템 구조에서 혹시나 데이터가 dict 통째로 들어올 경우를 대비한 2중 방어선
        if isinstance(actual_x, dict):
            actual_y = actual_x.get("y", 0)
            actual_x = actual_x.get("x", 0)

        self.vars = DummyVariables(actual_x, actual_y)
        self.load_images()
        
        # 🎯 에디터 기즈모 및 선택 영역에서 충돌 크기(50, 80)를 안전하게 측정할 수 있도록 순정 pygame.Rect 바인딩 보장
        self.rect = pygame.Rect(actual_x, actual_y, 50, 80)

    def load_images(self):
        """🌟 파일 위치와 상관없이, 실행 기준점에서 assets 폴더를 안정적으로 탐색합니다."""
        base_dir = os.path.abspath(".")
        dummy_dir = os.path.join(base_dir, "assets", "images", "enemy", "dummy")
        
        # FileNotFoundError뿐만 아니라 Pygame 자체 로드 에러(convert_alpha 등)까지 한 번에 방어하도록 호환성 개선
        try:
            self.images = {
                "IDLE": pygame.image.load(os.path.join(dummy_dir, "dummy_idle.png")).convert_alpha(),
                "HIT": pygame.image.load(os.path.join(dummy_dir, "dummy_hit.png")).convert_alpha(),
                "DEAD": pygame.image.load(os.path.join(dummy_dir, "dummy_dead.png")).convert_alpha()
            }
            for state in self.images:
                self.images[state] = pygame.transform.scale(self.images[state], (50, 80))
                
        except (FileNotFoundError, pygame.error):
            print("⚠️ 애니메이션 파일이 없거나 경로가 달라 기본 dummy.png 단일 이미지 탐색을 시도합니다.")
            try:
                single_img = pygame.image.load(os.path.join(dummy_dir, "dummy.png")).convert_alpha()
                self.images = {
                    "IDLE": pygame.transform.scale(single_img, (50, 80)),
                    "HIT": pygame.transform.scale(single_img, (50, 80)),
                    "DEAD": pygame.transform.scale(single_img, (50, 80))
                }
            except (FileNotFoundError, pygame.error):
                print("⚠️ 기본 dummy.png 마저 없어 단색 Surface 대체 비상 패치를 적용합니다.")
                # 비디오 디스플레이가 초기화되지 않은 특수 환경(에디터 백그라운드) 크래시 방지
                try:
                    surf = pygame.Surface((50, 80), pygame.SRCALPHA)
                    surf.fill((255, 100, 100))
                    self.images = {"IDLE": surf, "HIT": surf, "DEAD": surf}
                except pygame.error:
                    # Pygame 자체가 미준비 상태인 경우 프로그램이 튕기지 않게 None 처리 후 렌더러에서 우회
                    self.images = {"IDLE": None, "HIT": None, "DEAD": None}

    def check_player_attack(self, player_obj):
        """플레이어의 실시간 공격 히트박스 충돌 감지"""
        # 🎯 [구조 보환] 플레이어가 없거나(에디터 모드), 플레이어가 공격 상태가 아니면 안전하게 패스
        if not player_obj or not hasattr(player_obj, 'vars') or not player_obj.vars.is_attacking or not player_obj.vars.attack_rect:
            return

        dummy_rect = pygame.Rect(self.vars.x, self.vars.y, self.vars.width, self.vars.height)

        if dummy_rect.colliderect(player_obj.vars.attack_rect):
            if not self.vars.is_hit:
                self.vars.is_hit = True
                self.vars.hit_timer = self.vars.hit_duration
                self.vars.hp -= 10
                
                player_obj.vars.has_hit_enemy = True
                print(f"💥 더미 피격 성공! 남은 HP: {self.vars.hp}/100")

    def update(self, player_obj, platforms, game_map=None):
        """인게임 실시간 피격 판정과 함께, 플레이어와 동일한 규칙의 물리 업데이트 처리"""
        if self.vars.hp <= 0:
            return
        
        # 1. 플레이어 피격 체크
        self.check_player_attack(player_obj)

        # 2. 플레이어의 PhysicsProcessor와 완벽히 동일한 메커니즘으로 중력 및 지형 착지 연동
        self.apply_gravity_and_physics(platforms, game_map)

        # 3. 피격 경직 타이머
        if self.vars.is_hit:
            self.vars.hit_timer -= 1
            if self.vars.hit_timer <= 0:
                self.vars.is_hit = False

    def apply_gravity_and_physics(self, platforms, game_map=None):
        """PlayerPhysicsProcessor의 로직을 그대로 이식한 더미 전용 물리 엔진"""
        from settings import GROUND_Y  # 안전망용 기본 바닥 상숫값
        
        # 1. 중력 적용 및 이동 (플레이어 변수명 구조에 맞춰 vy 사용)
        # 플레이어 시펙: vars_obj.vertical_velocity += vars_obj.gravity
        self.vars.vy += 0.8  # 중력가속도 상수값 직접 부여 (필요시 self.vars.gravity 등으로 대체 가능)
        self.vars.y += self.vars.vy

        dummy_rect = pygame.Rect(self.vars.x, self.vars.y, self.vars.width, self.vars.height)
        on_sub_platform = False

        # 2. 플랫폼(발판) 충돌 검사 (플레이어의 platform.vars 구조 완전 매칭)
        if platforms:
            for platform in platforms:
                # 플랫폼의 solid 여부 체크 (플레이어 코드 준수)
                if hasattr(platform, 'vars') and not getattr(platform.vars, 'is_solid', True):
                    continue
                
                # platform.vars.x, y, width, height 추출
                if hasattr(platform, 'vars'):
                    p_x = platform.vars.x
                    p_y = platform.vars.y
                    p_w = platform.vars.width
                    p_h = platform.vars.height
                else:
                    # 혹시나 예외 케이스용 방어선
                    p_x = getattr(platform, 'x', 0)
                    p_y = getattr(platform, 'y', 0)
                    p_w = getattr(platform, 'width', 0)
                    p_h = getattr(platform, 'height', 0)

                plat_rect = pygame.Rect(p_x, p_y, p_w, p_h)
                
                if dummy_rect.colliderect(plat_rect):
                    # 위에서 아래로 떨어지는 중일 때만 착지
                    if self.vars.vy > 0:
                        if (self.vars.y + self.vars.height - self.vars.vy) <= p_y + 10:
                            self.vars.y = p_y - self.vars.height
                            self.vars.vy = 0
                            self.vars.is_grounded = True
                            on_sub_platform = True
                            break

        # 3. 메인 바닥(ground_y) 착지 검사 (플레이어 코드 핵심 이식)
        if not on_sub_platform:
            g_y = game_map.ground_y if (game_map and hasattr(game_map, 'ground_y')) else GROUND_Y
            if self.vars.y + self.vars.height >= g_y:
                self.vars.y = g_y - self.vars.height
                self.vars.vy = 0
                self.vars.is_grounded = True
            else:
                self.vars.is_grounded = False

        # 4. 최종 Rect 동기화
        self.rect.x = self.vars.x
        self.rect.y = self.vars.y

    def draw(self, screen, camera_offset=(0, 0)):
        ox, oy = camera_offset
        if self.vars.hp <= 0 or not screen:
            return 
        
        state = "IDLE"
        if self.vars.is_hit:
            state = "HIT"
            
        current_img = self.images.get(state, self.images.get("IDLE"))
        # 🎯 이미지가 성공적으로 로드된 경우에만 출력하여 크래시 완전 차단
        if current_img:
            screen.blit(current_img, (self.vars.x - ox, self.vars.y - oy))
    
    def draw_debug_overlay(self, screen, camera_offset=(0, 0)):
        """더미 엔티티의 피격 판정(AABB) 상자 및 체력 상태 메타데이터를 화면에 투영합니다."""
        if not DEBUG or self.vars.hp <= 0 or not screen:
            return

        ox, oy = camera_offset
        d_width = getattr(self.vars, 'width', 0)
        d_height = getattr(self.vars, 'height', 0)

        # 1. 🔴 DummyEnemy 피격 판정 상자(AABB) 실선 렌더링
        if d_width > 0 and d_height > 0:
            aabb_rect = pygame.Rect(self.vars.x - ox, self.vars.y - oy, d_width, d_height)
            pygame.draw.rect(screen, (255, 0, 0), aabb_rect, 2)

        # 2. 📊 실시간 체력 및 히트 상태 메타데이터 투영 (Lazy Evaluation 적용)
        try:
            font = pygame.font.SysFont("Consolas", 12)
        except:
            font = pygame.font.Font(None, 12)

        debug_texts = [
            f"HP: {self.vars.hp}/{getattr(self.vars, 'max_hp', '??')}",
            f"HIT: {self.vars.is_hit}",
            f"GND: {self.vars.is_grounded}"
        ]

        for i, text in enumerate(debug_texts):
            text_surf = font.render(text, True, (255, 0, 0))
            screen.blit(text_surf, (self.vars.x - ox, self.vars.y - oy - 15 - (i * 13)))

        # 규격화된 출력 로그 생성
        print(f"[dummy_main.py] draw_debug_overlay() -> Rendered Dummy AABB: HP={self.vars.hp}, HIT={self.vars.is_hit}")

def auto_register_entity():
    """ 전역 공간이 아닌 함수 내부에서 임포트하여 상호 임포트 락(Lock)을 완전히 우회합니다. """
    try:
        from map_system.map_engine import EntityRegistry
        EntityRegistry.register("DummyEnemy", DummyEnemy)
        EntityRegistry.register("dummy_enemy", DummyEnemy)
        EntityRegistry.register("dummy", DummyEnemy)
    except (ImportError, AttributeError):
        # 메인 프로세스 초기화 순서에 의해 아직 모듈이 로드되지 않았다면 예외를 패스하여
        # 이후 맵 매니저 작동 시 정상 참조되도록 우회 유도
        pass
```

--------------------------------------------------

### 📄 extraction_target_project/enemy/enemys/dummy/variables.py
#### 🧱 Code Skeleton:
```python
class DummyVariables:
    def __init__(self, x, y):
        # 📐 위치 및 크기
        self.x = x
        self.y = y
        self.width = 50
        self.height = 70
        
        # 💫 실시간 중력 및 위치 피벗 동적 보정 변수
        self.vy = 0.0
        self.is_grounded = False
        
        # ❤️ 능력치 상태
        self.hp = 100
        self.max_hp = 100
        
        # 💫 피격(Hit) 관련 상태 변수
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 10
        
        # 🎯 맵 에디터 인스펙터 연동 가시성 변수 프로토콜 완벽 주입
        self.is_visible = True
        
        # 🧱 위치/피벗 자동 보정 베이스 라인
        self.initial_y_offset = self.height
```

--------------------------------------------------

### 📄 extraction_target_project/enemy/enemys/test_enemy1/__init__.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/enemy/enemys/test_enemy1/test_enemy1_main.py
#### 🧱 Code Skeleton:
```python
class TestEnemy1:
    def __init__(self, x, y):
        # 1. variables.py에 명시된 모든 변수를 실시간 데이터로 장착!
        self.vars = TestEnemy1Variables()
        self.vars.x = x
        self.vars.y = y
        
        # 2. 실시간 AI 상태 제어 변수
        self.state = "PATROL" # PATROL, CHASE, LOST, ATTACK
        
        # 물리 연산용 접지 플래그 (점프 판단 및 낙하 판정용)
        self.on_ground = False

    def take_damage(self, amount, knockback_dir=0):
        """플레이어의 공격을 받았을 때 데미지를 받고 넉백되는 피격 로직"""
        if self.vars.is_dead:
            return
            
        self.vars.hp = max(0, self.vars.hp - amount)
        self.vars.is_hit = True
        self.vars.hit_timer = 20  # 약 0.3초간 완벽 경직 및 넉백
        
        # 타격을 받으면 즉시 뒤로 튕겨 나감 (넉백 가속도 주입)
        if knockback_dir != 0:
            self.vars.vx = knockback_dir * 350.0  # 넉백 강도 설정
        
        # 맞자마자 플레이어를 향해 상태를 '추적(CHASE)' 모드로 강제 강제 전환
        self.state = "CHASE"
        
        print(f"💥 [TestEnemy1] 피격! 체력: {self.vars.hp}/{self.vars.max_hp}")
        
        if self.vars.hp <= 0:
            self.vars.is_dead = True
            self.vars.vx = 0
            print("💀 [TestEnemy1] 사망함.")

    def check_line_of_sight(self, player_obj, platforms):
        """적과 플레이어 사이에 벽(플랫폼)이 가로막고 있는지 선형 보간(LERP) 검사"""
        if not hasattr(player_obj, 'vars'):
            return False
            
        px, py = player_obj.vars.x, player_obj.vars.y
        ex, ey = self.vars.x, self.vars.y
        
        # 거리가 감지 범위보다 멀면 즉시 감지 실패
        distance = math.hypot(px - ex, py - ey)
        if distance > self.vars.detection_range:
            return False
            
        steps = int(distance / 10) + 1
        for i in range(steps):
            t = i / steps
            lx = ex + (px - ex) * t
            ly = ey + (py - ey) * t
            
            for plat in platforms:
                plat_x = getattr(plat, 'x', 0)
                plat_y = getattr(plat, 'y', 0)
                plat_w = getattr(plat, 'width', 0) or getattr(plat, 'w', 40)
                plat_h = getattr(plat, 'height', 0) or getattr(plat, 'h', 40)
                
                plat_rect = pygame.Rect(plat_x, plat_y, plat_w, plat_h)
                if plat_rect.collidepoint(lx, ly):
                    return False
                    
        return True

    def update_with_dt(self, player_obj, platforms, game_map, dt):
        """
        인게임 루프에서 매 프레임 호출하는 핵심 업데이트 메서드.
        피격 경직 중일 때는 AI 행동 패턴을 일시정지하고 물리 넉백 슬라이딩 감속만 처리합니다.
        """
        # dt 가드 설정
        dt = min(dt, 0.1)

        # ----------------- [1. 피격 경직(Hit State) 및 넉백 감쇠 연산] -----------------
        if self.vars.is_hit:
            self.vars.hit_timer -= 1
            if self.vars.hit_timer <= 0:
                self.vars.is_hit = False
                
            # 바닥 마찰력으로 넉백에 의한 속도를 서서히 미끄러지며 줄임
            self.vars.vx *= 0.85
            
            # 경직 상태에서도 벽 충돌 및 중력 처리는 유지
            self._apply_gravity_and_collisions(platforms, game_map, dt)
            return

        if self.vars.is_dead:
            self.vars.vx = 0
            self._apply_gravity_and_collisions(platforms, game_map, dt)
            return

        # ----------------- [2. AI 상태 머신 연산 및 속도(vx) 설정] -----------------
        can_see_player = self.check_line_of_sight(player_obj, platforms)
        dx = player_obj.vars.x - self.vars.x if hasattr(player_obj, 'vars') else 0
        distance_to_player = abs(dx)

        if self.state == "PATROL":
            self.vars.vx = self.vars.direction * self.vars.patrol_speed
            if can_see_player:
                self.state = "CHASE"

        elif self.state == "CHASE":
            if dx > 0:
                self.vars.direction = 1
            elif dx < 0:
                self.vars.direction = -1
            self.vars.vx = self.vars.direction * self.vars.chase_speed
            
            if distance_to_player <= self.vars.attack_range:
                self.state = "ATTACK"
                self.vars.attack_cooldown = 40
            elif not can_see_player:
                self.state = "LOST"
                self.vars.lost_timer = self.vars.lost_delay

        elif self.state == "LOST":
            self.vars.lost_timer -= 1
            if can_see_player:
                self.state = "CHASE"
                self.vars.lost_timer = 0
            elif self.vars.lost_timer <= 0:
                self.state = "PATROL"

        elif self.state == "ATTACK":
            self.vars.vx = 0
            self.vars.attack_cooldown -= 1
            if self.vars.attack_cooldown <= 0:
                if distance_to_player > self.vars.attack_range:
                    self.state = "CHASE"
                else:
                    self.vars.attack_cooldown = 40

        # AI 연산 후 최종 물리 및 플랫폼 충돌 적용
        self._apply_gravity_and_collisions(platforms, game_map, dt)

    def _apply_gravity_and_collisions(self, platforms, game_map, dt):
        """순수 중력 및 플랫폼 충돌 로직"""
        # 중력 적용
        GRAVITY = 980.0 * dt
        self.vars.vy += GRAVITY
        if self.vars.vy > 900.0:
            self.vars.vy = 900.0

        # X축 이동 및 충돌
        self.vars.x += self.vars.vx * dt * 60.0
        self_rect = pygame.Rect(self.vars.x, self.vars.y, self.vars.width, self.vars.height)

        for plat in platforms:
            p_vars = getattr(plat, 'vars', None)
            plat_x = getattr(p_vars if p_vars else plat, 'x', 0)
            plat_y = getattr(p_vars if p_vars else plat, 'y', 0)
            plat_w = getattr(p_vars if p_vars else plat, 'width', 0) or getattr(plat, 'w', 40)
            plat_h = getattr(p_vars if p_vars else plat, 'height', 0) or getattr(plat, 'h', 40)
            plat_rect = pygame.Rect(plat_x, plat_y, plat_w, plat_h)
            
            if self_rect.colliderect(plat_rect):
                if self.vars.y + self.vars.height > plat_rect.top + 4 and self.vars.y < plat_rect.bottom - 4:
                    if self.vars.vx > 0:
                        self.vars.x = plat_rect.left - self.vars.width
                        self.vars.direction = -1
                    elif self.vars.vx < 0:
                        self.vars.x = plat_rect.right
                        self.vars.direction = 1
                    break

        # Y축 이동 및 충돌
        old_bottom = self.vars.y + self.vars.height
        self.vars.y += self.vars.vy * dt
        self_rect = pygame.Rect(self.vars.x, self.vars.y, self.vars.width, self.vars.height)
        self.on_ground = False

        for plat in platforms:
            p_vars = getattr(plat, 'vars', None)
            plat_x = getattr(p_vars if p_vars else plat, 'x', 0)
            plat_y = getattr(p_vars if p_vars else plat, 'y', 0)
            plat_w = getattr(p_vars if p_vars else plat, 'width', 0) or getattr(plat, 'w', 40)
            plat_h = getattr(p_vars if p_vars else plat, 'height', 0) or getattr(plat, 'h', 40)
            plat_rect = pygame.Rect(plat_x, plat_y, plat_w, plat_h)
            
            if self_rect.colliderect(plat_rect):
                if self.vars.vy >= 0 and old_bottom <= plat_rect.top + 12:
                    self.vars.y = plat_rect.top - self.vars.height
                    self.vars.vy = 0
                    self.on_ground = True
                    break

    def draw(self, screen, camera_offset=(0, 0)):
        if self.vars.is_dead:
            return # 죽었으면 렌더링 스킵 (추후 사망 시체 애니메이션 추가 공간)
            
        render_x = self.vars.x - camera_offset[0]
        render_y = self.vars.y - camera_offset[1]
        
        # 🎨 피격(is_hit) 시 빨간색 상자, 평소에는 주황색 상자로 렌더링하여 피격 피드백 제공!
        body_color = (231, 76, 60) if self.vars.is_hit else (241, 196, 15)
        
        rect = pygame.Rect(render_x, render_y, self.vars.width, self.vars.height)
        pygame.draw.rect(screen, body_color, rect)
        pygame.draw.rect(screen, (44, 62, 80), rect, 2)
        
        # 눈 렌더링
        eye_x = render_x + (self.vars.width - 12 if self.vars.direction == 1 else 6)
        pygame.draw.rect(screen, (0, 0, 0), (eye_x, render_y + 15, 6, 6))

    def draw_debug_overlay(self, screen, camera_offset=(0, 0)):
        """인공지능 적(TestEnemy1)의 AABB 경계상자 및 상태 머신 메타데이터를 화면에 투영합니다."""
        if not DEBUG or getattr(self.vars, 'is_dead', False) or not screen:
            return

        ox, oy = camera_offset
        e_width = getattr(self.vars, 'width', 0)
        e_height = getattr(self.vars, 'height', 0)

        # 1. 🔴 TestEnemy1 피격 판정 상자(AABB) 실선 렌더링
        if e_width > 0 and e_height > 0:
            aabb_rect = pygame.Rect(self.vars.x - ox, self.vars.y - oy, e_width, e_height)
            pygame.draw.rect(screen, (255, 0, 0), aabb_rect, 2)

        # 2. 📊 AI 상태 구조 및 물리 데이터 추적 (Lazy Evaluation)
        try:
            font = pygame.font.SysFont("Consolas", 12)
        except:
            font = pygame.font.Font(None, 12)

        debug_texts = [
            f"HP: {self.vars.hp}/{getattr(self.vars, 'max_hp', '??')}",
            f"STATE: {getattr(self, 'state', 'NONE')}",            # self 직속 속성 추적으로 변경
            f"VEL: ({getattr(self.vars, 'vx', 0):.1f}, {getattr(self.vars, 'vy', 0):.1f})",
            f"GND: {getattr(self, 'on_ground', False)}"             # 누락된 실시간 접지 데이터 바인딩
        ]

        for i, text in enumerate(debug_texts):
            text_surf = font.render(text, True, (255, 0, 0))
            screen.blit(text_surf, (self.vars.x - ox, self.vars.y - oy - 15 - (i * 13)))

        if DEBUG:
            print(f"[test_enemy1_main.py] draw_debug_overlay() -> Rendered AI Enemy AABB: HP={self.vars.hp}, STATE={getattr(self.vars, 'state', 'NONE')}")
```

--------------------------------------------------

### 📄 extraction_target_project/enemy/enemys/test_enemy1/variables.py
#### 🧱 Code Skeleton:
```python
class TestEnemy1Variables:
    def __init__(self):
        # 1. 기본 식별 및 플래그
        self.is_enemy = True          # 💡 이전 단계에서 만든 하이브리드 최적화 가드를 위한 핵심 적 태그!
        self.hp = 100                 # 체력
        self.max_hp = 100             # 최대 체력
        self.is_dead = False          # 사망 여부
        self.is_hit = False           # 피격 경직 상태 여부
        self.hit_timer = 0            # 피격 경직 타이머
        
        # 2. 물리 및 기본 위치 데이터 (main에서 실시간으로 대입/업데이트되는 변수들)
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.width = 40
        self.height = 60
        
        # 3. AI 이동 및 속도 제어
        self.patrol_speed = 1.5       # 평소 순찰할 때 걷는 속도
        self.chase_speed = 3.2        # 플레이어를 발견하고 쫓아갈 때 뛰는 속도
        self.direction = 1            # 바라보는 방향 (1: 오른쪽, -1: 왼쪽)
        
        # 4. AI 인지 범위 및 추적 시스템 (픽셀 단위)
        self.detection_range = 350    # 플레이어를 감지하는 시야 범위
        self.attack_range = 45        # 근접 공격을 시작하는 무기 사정거리
        
        # 5. 어그로 시간(초/프레임) 관리
        self.lost_timer = 0           # 실시간 시야 상실 타이머
        self.lost_delay = 180         # 시야에서 벗어나도 3초(180프레임) 동안 추적을 유지
        
        # 6. 공격 동작 관리
        self.attack_cooldown = 0      # 다음 공격까지 남은 쿨타임
        self.attack_ready_time = 30   # 공격 모션 전 선딜레이 시간 (0.5초 = 30프레임)
        self.attack_total_cooldown = 60 # 공격 완료 후 재사용 대기 시간 (1초 = 60프레임)
```

--------------------------------------------------

### 📄 extraction_target_project/event_system/actions/move_map.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/event_system/actions/play_dialogue.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/event_system/actions/spawn_ambush.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/event_system/triggers/enemy_clear.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/event_system/triggers/npc_interact.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/event_system/triggers/zone_enter.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/fabric_system/editor_objects.json
#### 🧱 Code Skeleton:
```python
📦 [JSON STRUCTURE MAP]
  ├── "objects": List (len: 2)
```

--------------------------------------------------

### 📄 extraction_target_project/main.py
#### 🧱 Code Skeleton:
```python
class AppState:
    MAIN_MENU = "MAIN_MENU"
    GAME_PLAY = "GAME_PLAY"
    MAP_EDITOR = "MAP_EDITOR"

def draw_player_hp_hud(surface, player_obj):
    """
    플레이어 HP HUD 표시 (순정 사양 준수 및 비주얼 게이지 적용)
    """
    if hasattr(player_obj, 'vars') and hasattr(player_obj.vars, 'hp'):
        # 1. 기존 데이터 프로토콜 안전하게 참조
        hp = player_obj.vars.hp
        max_hp = getattr(player_obj.vars, 'max_hp', 100) # 안전장치: 없을 경우 100 기본값
        
        # 2. HP 비율 계산 (0.0 ~ 1.0 제한)
        hp_ratio = max(0.0, min(1.0, float(hp) / float(max_hp)))
        
        # 3. HUD 위치 및 크기 정의 (왼쪽 위 배치)
        hud_x, hud_y = 20, 20
        bar_width, bar_height = 200, 20
        border_thickness = 2
        
        # 4. 체력바 배경 (어두운 회색/검은색 테두리 배경)
        bg_rect = pygame.Rect(hud_x, hud_y, bar_width, bar_height)
        pygame.draw.rect(surface, (30, 41, 59), bg_rect)  # Slate 800 배경색
        
        # 5. 체력바 채우기 (현재 체력 비율 적용)
        # 체력이 낮아질수록 초록색(안전) -> 노란색(경고) -> 빨간색(위험)으로 보간 연산
        if hp_ratio > 0.5:
            bar_color = (34, 197, 94)  # 초록색 (Green 500)
        elif hp_ratio > 0.2:
            bar_color = (234, 179, 8)  # 노란색 (Yellow 500)
        else:
            bar_color = (239, 68, 68)  # 빨간색 (Red 500)
            
        fill_width = int(bar_width * hp_ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(hud_x, hud_y, fill_width, bar_height)
            pygame.draw.rect(surface, bar_color, fill_rect)
            
        # 6. 체력바 외곽 테두리선 그리기
        border_rect = pygame.Rect(hud_x, hud_y, bar_width, bar_height)
        pygame.draw.rect(surface, (255, 255, 255), border_rect, border_thickness, border_radius=3)
        
        # 7. 수치 텍스트 오버레이 (바 중앙 혹은 오른쪽에 가독성 높게 출력)
        try:
            font = pygame.font.SysFont("malgungothic", 14, bold=True)
        except Exception:
            font = pygame.font.SysFont(None, 18, bold=True)
            
        text_surf = font.render(f"{hp} / {max_hp}", True, (255, 255, 255))
        # 검은색 텍스트 테두리(그림자) 효과로 시인성 극대화
        shadow_surf = font.render(f"{hp} / {max_hp}", True, (0, 0, 0))
        
        text_x = hud_x + bar_width + 10
        text_y = hud_y + (bar_height - text_surf.get_height()) // 2
        
        surface.blit(shadow_surf, (text_x + 1, text_y + 1))
        surface.blit(text_surf, (text_x, text_y))

def run_game(window_screen, virtual_screen, clock):
     """실제 인게임 액션 플레이 모드 루프 (AI 오염 제거 및 멀티맵 동적 락 장착)"""
     global DEBUG_SHOW_HITBOX
     # 1. 객체 초기화 (기존 데이터 프로토콜 엄격 준수)
     player = Player(100, GROUND_Y - 60)
     game_map = GameMap(map_id=1)
     
     dialogue_manager = DialogueManager()
     dialogue_manager.load_dialogues()
     
     def start_dialogue_handler(action):
         dialogue_id = action.get("dialogue_id")
         dialogue_manager.start_dialogue(dialogue_id)
         
     game_map.register_action_handler("start_dialogue", start_dialogue_handler)
     dialogue_manager.start_dialogue("stage1_start_chat")
     
     # 2. 순정 카메라 엔진 셋업
     camera = ElasticCamera(
         VIRTUAL_WIDTH, VIRTUAL_HEIGHT,
         smoothing=CAMERA_SMOOTHING,
         deadzone_w=CAMERA_DEADZONE_W,
         deadzone_h=CAMERA_DEADZONE_H,
         max_speed_px_per_sec=None,
     )
     camera.set_center(player.vars.x + player.vars.width / 2.0, player.vars.y + player.vars.height / 2.0)
     
# 3. 게임 메인 루프
     while True:
         dt = clock.tick(FPS) / 1000.0
         
         for event in pygame.event.get():
             if event.type == pygame.QUIT:
                 return None
             elif event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_ESCAPE:
                     return AppState.MAIN_MENU
                 # F3 키 입력을 인터셉트하여 히트박스 디버그 플래그 실시간 토글
                 elif event.key == pygame.K_F3:
                     before_state = DEBUG_SHOW_HITBOX
                     DEBUG_SHOW_HITBOX = not DEBUG_SHOW_HITBOX
                     if DEBUG:
                         print(f"[main.py] run_game() -> Debug Toggle Changed: DEBUG_SHOW_HITBOX ({before_state} -> {DEBUG_SHOW_HITBOX})")
                 if dialogue_manager.is_active and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    dialogue_manager.next_line()
                    
        # 대화창이 꺼져있을 때만 물리 및 업데이트 작동
         if not dialogue_manager.is_active:
            # 델타 타임(dt)과 적 목록(game_map.entities)을 함께 넘겨주어 정밀 물리와 타격을 작동시킵니다.
# 만약 main.py 내부의 루프에 dt 변수명이 다르게 되어있다면(예: deltatime 등) 해당 변수명으로 넣어주세요.
            dt = clock.get_time() / 1000.0  # 혹시 루프 내에 dt 정의가 없다면 이 줄을 위에 추가하세요.
            player.update_with_dt(game_map.platforms, game_map, dt, entities=game_map.entities)
            game_map.update(dt, player_obj=player)
            
            # 카메라 타겟 중심점 계산
            target_cx = float(player.vars.x + player.vars.width / 2.0)
            target_cy = float(player.vars.y + player.vars.height / 2.0)
            
            # [💡 형님의 매서운 지적 완벽 반영: JSON 멀티맵 동적 바닥 연동]
            # 하드코딩 600을 완전히 제거하고, JSON에서 파싱해온 맵의 바닥 높이를 실시간 추적합니다.
            dynamic_ground_y = float(game_map.ground_y) if hasattr(game_map, 'ground_y') else float(GROUND_Y)
            
            # 카메라가 화면 하단 한계선을 넘어 맵 바깥(땅 에셋 밑바닥 허공)을 보지 못하게 완벽 락(Lock)
            clamp_cam_y_max = float(game_map.ground_y) - (float(VIRTUAL_HEIGHT) / 2.0) + 30.0
            
            # 카메라 동적 업데이트 실행
            camera.update(target_cx, target_cy, dt, clamp_y_max=clamp_cam_y_max)
            
        # 4. 렌더링 파이프라인 (카메라 오프셋 적용)
         camera_offset = camera.get_offset()
         virtual_screen.fill((0, 0, 0))
        
        # 맵, 플레이어, HUD 그리기
         game_map.draw(virtual_screen, camera_offset=camera_offset)
         player.draw(virtual_screen, camera_offset=camera_offset)
         draw_player_hp_hud(virtual_screen, player)
        
         if dialogue_manager.is_active:
            dialogue_manager.draw(virtual_screen)
            
        # 가상 화면을 실제 윈도우 스크린 크기에 맞게 업스케일링 블릿
         scaled_surf = pygame.transform.scale(virtual_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
         window_screen.blit(scaled_surf, (0, 0))
         pygame.display.flip()

def run_main_menu(window_screen, virtual_screen, clock):
    """메인 메뉴 루프 (순정 사양 복구 및 수려한 디자인 제공)"""
    pygame.display.set_caption("Game Engine - Main Menu")
    
    # 폰트 로딩 (한글 및 영문 텍스트 지원)
    try:
        title_font = pygame.font.SysFont("malgungothic", 72, bold=True)
        menu_font = pygame.font.SysFont("malgungothic", 36)
        info_font = pygame.font.SysFont("malgungothic", 24)
    except Exception:
        title_font = pygame.font.SysFont(None, 72, bold=True)
        menu_font = pygame.font.SysFont(None, 36)
        info_font = pygame.font.SysFont(None, 24)
        
    import math
    time_elapsed = 0.0
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        time_elapsed += dt
        
        # 키보드 이벤트 처리 및 락 해제
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    return AppState.GAME_PLAY
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    return AppState.MAP_EDITOR
                elif event.key == pygame.K_ESCAPE:
                    return None
                    
        # 가상 화면 렌더링 시작 (풍부하고 고급스러운 테마)
        virtual_screen.fill((15, 23, 42))  # Slate 900
        
        # 그리드 패턴 렌더링 (미학적 디테일)
        grid_size = 80
        grid_color = (30, 41, 59)
        for x in range(0, VIRTUAL_WIDTH, grid_size):
            pygame.draw.line(virtual_screen, grid_color, (x, 0), (x, VIRTUAL_HEIGHT))
        for y in range(0, VIRTUAL_HEIGHT, grid_size):
            pygame.draw.line(virtual_screen, grid_color, (0, y), (VIRTUAL_WIDTH, y))
            
        # 타이틀 텍스트 애니메이션 (사인파를 활용한 맥동)
        pulse_val = math.sin(time_elapsed * 3.0) * 8.0
        
        # 타이틀 글로우/그림자 효과
        shadow_surf = title_font.render("Game Engine", True, (56, 189, 248))  # Sky 400
        shadow_rect = shadow_surf.get_rect(center=(VIRTUAL_WIDTH // 2 - 4, 300 + int(pulse_val) - 4))
        virtual_screen.blit(shadow_surf, shadow_rect)
        
        title_surf = title_font.render("wwwGame Engine", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(VIRTUAL_WIDTH // 2, 300 + int(pulse_val)))
        virtual_screen.blit(title_surf, title_rect)
        
        # 메뉴 박스 디자인
        btn_w, btn_h = 560, 90
        btn_x = (VIRTUAL_WIDTH - btn_w) // 2
        
        # 1: START GAME 버튼
        rect1 = pygame.Rect(btn_x, 520, btn_w, btn_h)
        pygame.draw.rect(virtual_screen, (30, 41, 59), rect1, border_radius=12)
        pygame.draw.rect(virtual_screen, (129, 140, 248), rect1, 3, border_radius=12)  # Indigo 400 Border
        text1 = menu_font.render("1: START GAME", True, (243, 244, 246))
        text1_rect = text1.get_rect(center=rect1.center)
        virtual_screen.blit(text1, text1_rect)
        
        # 2: MAP EDITOR 버튼
        rect2 = pygame.Rect(btn_x, 650, btn_w, btn_h)
        pygame.draw.rect(virtual_screen, (30, 41, 59), rect2, border_radius=12)
        pygame.draw.rect(virtual_screen, (16, 185, 129), rect2, 3, border_radius=12)  # Emerald 500 Border
        text2 = menu_font.render("2: MAP EDITOR", True, (243, 244, 246))
        text2_rect = text2.get_rect(center=rect2.center)
        virtual_screen.blit(text2, text2_rect)
        
        # 조작 가이드 메시지
        info_text = info_font.render("Press KEY 1 or 2 to select option, ESC to Quit", True, (148, 163, 184))
        info_rect = info_text.get_rect(center=(VIRTUAL_WIDTH // 2, 820))
        virtual_screen.blit(info_text, info_rect)
        
        # 가상 화면 스케일 업 블릿
        scaled_surf = pygame.transform.scale(virtual_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
        window_screen.blit(scaled_surf, (0, 0))
        pygame.display.flip()

def draw(self, screen, camera_offset=(0, 0)):
        """플레이어 본체 이미지와 공격 시 쇠파이프 콤보 이펙트를 화면에 렌더링하고 디버그 오버레이를 최종적으로 상위 투영합니다."""
        ox, oy = camera_offset
        # 🎬 1. 캐릭터 본체 스프라이트 시퀀스 추출 및 출력 (기존 순정 로직 완벽 보존)
        anim_list = self.assets.images.get(self.vars.current_state, [])
        if not anim_list:
            return
            
        # 혹시 모를 인덱스 바운드 에러를 막기 위한 최종 안전 필터링
        idx = min(self.vars.current_frame_idx, len(anim_list) - 1)
        player_image = anim_list[idx]
        
        # 왼쪽을 바라보고 있다면 이미지 좌우 반전
        if not self.vars.facing_right:
            player_image = pygame.transform.flip(player_image, True, False)
            
        screen.blit(player_image, (self.vars.x - ox, self.vars.y - oy))
        
        # ─────────────────────────────────────────────────────────────
        # 🎯 [새로운 시스템 추가] 쇠파이프 타격 범위(이펙트) 가시화 및 콤보별 연출
        # ─────────────────────────────────────────────────────────────
        if getattr(self.vars, 'is_attacking', False) and getattr(self.vars, 'attack_rect', None):
            # 카메라 좌표계가 반영된 실시간 이펙트 렌더링 사각형 변환
            eff_rect = pygame.Rect(
                self.vars.attack_rect.x - ox,
                self.vars.attack_rect.y - oy,
                self.vars.attack_rect.width,
                self.vars.attack_rect.height
            )
            
            # 투명도(Alpha) 표현이 가능한 이펙트 전용 특수 표면(Surface) 생성 (최적화 결합)
            effect_surf = pygame.Surface((eff_rect.width, eff_rect.height), pygame.SRCALPHA)
            
            # 현재 콤보 단수(1타, 2타, 3타막타)에 맞춰 시각 효과 가변 분기
            combo = getattr(self.vars, 'combo_step', 1)
            if combo == 1:
                # 1타: 신속하게 파고드는 블루 화이트 타격 잔상 (반투명)
                color = (52, 152, 219, 140) 
                pygame.draw.ellipse(effect_surf, color, (0, 0, eff_rect.width, eff_rect.height))
            elif combo == 2:
                # 2타: 좌우 반전 궤적으로 휘두르는 날카로운 옐로우 타격 잔상
                color = (241, 196, 15, 140)
                pygame.draw.ellipse(effect_surf, color, (0, 0, eff_rect.width, eff_rect.height))
            elif combo == 3:
                # 3타: 제자리 고정 묵직한 오렌지-레드 대형 광역 내려찍기 충격파 연출
                color = (231, 76, 60, 180)
                # 바닥 충격파 영역 생성
                pygame.draw.rect(effect_surf, color, (0, 0, eff_rect.width, eff_rect.height), border_radius=8)
                # 크래시 방지 및 시인성을 위한 내부 화이트 하이라이트 테두리 선 추가
                pygame.draw.rect(effect_surf, (255, 255, 255, 220), (0, 0, eff_rect.width, eff_rect.height), 3, border_radius=8)
                
            # 최종 연산 완료된 이펙트를 게임 화면에 블릿(Blit) 출력
            screen.blit(effect_surf, (eff_rect.x, eff_rect.y))

        # ─────────────────────────────────────────────────────────────
        # 📊 [F3 실시간 메타데이터 스택 레이어 주입] 마인크래프트 스타일 오버레이
        # ─────────────────────────────────────────────────────────────
        if getattr(settings, 'DEBUG_SHOW_HITBOX', False):
            try:
                font = pygame.font.SysFont("Consolas", 14)
            except:
                font = pygame.font.Font(None, 14)
            
            meta_data = [
                "--- SYSTEM INFO (F3 MODE) ---",
                f"PLAYER WORLD POS: ({self.vars.x:.2f}, {self.vars.y:.2f})",
                f"PLAYER STATE: {self.vars.current_state} (FRAME: {self.vars.current_frame_idx})",
                f"CAMERA OFFSET: ox={ox}, oy={oy}",
                f"ATTACK ACTIVE: {getattr(self.vars, 'is_attacking', False)} (MODE: {getattr(self.vars, 'attack_mode', 'NORMAL')})"
            ]
            
            # 좌측 상단에 흑색 반투명 가독성 패널 및 화이트 텍스트 스택 블릿
            for idx, text in enumerate(meta_data):
                txt_surf = font.render(text, True, (255, 255, 255))
                bg_surf = pygame.Surface((txt_surf.get_width() + 6, txt_surf.get_height() + 4), pygame.SRCALPHA)
                bg_surf.fill((0, 0, 0, 150))
                screen.blit(bg_surf, (10, 60 + (idx * 20)))
                screen.blit(txt_surf, (13, 62 + (idx * 20)))

def main():
    """게임 진입점"""
    pygame.init()
    pygame.display.set_caption("Jjap Cursor Game Engine")
    
    window_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    clock = pygame.time.Clock()
    
    current_state = AppState.MAIN_MENU
    
    while current_state is not None:
        if current_state == AppState.MAIN_MENU:
            current_state = run_main_menu(window_screen, virtual_screen, clock)
        elif current_state == AppState.GAME_PLAY:
            current_state = run_game(window_screen, virtual_screen, clock)
        elif current_state == AppState.MAP_EDITOR:
            from map_editor_tool.map_editor import MapEditor
            editor = MapEditor()
            current_state = editor.run(window_screen, virtual_screen, clock)
        else:
            break
            
    pygame.quit()
    sys.exit()
```

--------------------------------------------------

### 📄 extraction_target_project/map_editor_tool/__init__.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/map_editor_tool/editor_main.py
#### 🧱 Code Skeleton:
```python
class MapEditor:
    SIDEBAR_W = 330
    GRID_SIZE = 40
    PANEL_PAD = 24
    SAVE_BUTTON_RECT = pygame.Rect(settings.VIRTUAL_WIDTH - SIDEBAR_W + PANEL_PAD, 168, SIDEBAR_W - PANEL_PAD * 2, 48)

    def __init__(self, map_name=None, save_name=None):
        EditorObjectRegistry.ensure_defaults()
        EditorObjectRegistry.discover_fabric_definitions()
        self.maps_dir = self._ensure_maps_dir()
        self.map_files = map_selector.scan_map_files(self)
        self.map_name = map_name
        self.save_name = save_name or map_name
        self.selected_map_file = self._map_name_to_file(map_name) if map_name else None
        self.map_manager = None
        self.palette = EditorObjectRegistry.definitions()
        self.palette_index = 0
        self.tool = "place"
        self.mode = "select" if map_name is None else "edit"
        self.camera = pygame.Vector2(0, 0)
        self.selected_platform = None
        self.dragging = False
        self.drag_offset = pygame.Vector2(0, 0)
        self.status_message = "Select a map to edit"
        self.selected_trigger_idx = -1
        self.font = pygame.font.SysFont("malgungothic", 24)
        self.small_font = pygame.font.SysFont("malgungothic", 18)
        self.header_font = pygame.font.SysFont("malgungothic", 30, bold=True)
        self._build_map_selection_buttons()
        if map_name is not None:
            self.load_map(map_name, self.selected_map_file)

    def _ensure_maps_dir(self):
        maps_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "map_system", "maps")
        os.makedirs(maps_dir, exist_ok=True)
        return maps_dir

    def _build_map_selection_buttons(self):
        map_selector.build_map_selection_buttons(self)

    def get_object_visibility(self, obj):
        return selection.get_object_visibility(self, obj)

    def calculate_placement_pos(self, mouse_world_x, mouse_world_y, current_definition):
        return input_handler.calculate_placement_pos(self, mouse_world_x, mouse_world_y, current_definition)

    def load_map(self, map_name, file_name=None):
        self.map_name = map_name
        self.save_name = map_name
        self.selected_map_file = file_name or self._map_name_to_file(map_name)

        from map_system.map_main import GameMap
        self.map_manager = GameMap(map_id=map_name)

        if not hasattr(self.map_manager, "structures"):
            self.map_manager.structures = []

        self.mode = "edit"
        self.camera.x = 0
        self.camera.y = 0
        self.selected_platform = None
        self.dragging = False
        self.status_message = f"Editing {self.selected_map_file}"

    def _file_to_map_name(self, file_name):
        return map_selector.file_to_map_name(file_name)

    def _map_name_to_file(self, map_name):
        return map_selector.map_name_to_file(map_name)

    def _next_new_map_file(self):
        return map_selector.next_new_map_file(self)

    def run(self, window_screen, virtual_screen, clock):
        pygame.display.set_caption("Jin Ro Project - Map Editor")
        while True:
            dt = clock.tick(settings.FPS) / 1000.0
            mouse_virtual = self._window_to_virtual(pygame.mouse.get_pos())

            for event in pygame.event.get():
                result = self._handle_event(event, mouse_virtual)
                if result is not None:
                    return result

            if self.mode == "edit":
                self._update_camera(dt)
                self._draw(virtual_screen)
            else:
                self._draw_map_select(virtual_screen, mouse_virtual)
            scaled_surface = pygame.transform.smoothscale(
                virtual_screen,
                (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
            )
            window_screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()

    def _handle_event(self, event, mouse_virtual):
        return input_handler.handle_event(self, event, mouse_virtual)

    def _handle_select_event(self, event, mouse_virtual):
        return map_selector.handle_select_event(self, event, mouse_virtual)

    def _handle_keydown(self, event):
        return input_handler.handle_keydown(self, event)

    def _handle_selected_shortcuts(self, event):
        return input_handler.handle_selected_shortcuts(self, event)

    def _handle_mouse_down(self, event, mouse_virtual):
        return input_handler.handle_mouse_down(self, event, mouse_virtual)

    def _handle_sidebar_click(self, mouse_virtual):
        return input_handler.handle_sidebar_click(self, mouse_virtual)

    def _update_camera(self, dt):
        return input_handler.update_camera(self, dt)

    def place_selected(self, world):
        return selection.place_selected(self, world)

    def find_platform_at(self, world):
        return selection.find_platform_at(self, world)

    def delete_selected(self):
        return selection.delete_selected(self)

    def save_map(self):
        return serializer.save_map(self)

    def load_saved_or_source(self):
        return serializer.load_saved_or_source(self)

    def serialize_map(self):
        return serializer.serialize_map(self)

    def _serialize_platform(self, platform):
        return serializer._serialize_platform(self, platform)

    def _serialize_structure(self, struct):
        return serializer._serialize_structure(self, struct)

    def _serialize_entity(self, entity):
        return serializer._serialize_entity(self, entity)

    def _serialize_trigger(self, trigger):
        return serializer._serialize_trigger(self, trigger)

    def _infer_entity_type(self, entity):
        return serializer._infer_entity_type(self, entity)

    def _draw(self, surface):
        return renderer.draw(self, surface)

    def _draw_map_select(self, surface, mouse_virtual):
        return renderer.draw_map_select(self, surface, mouse_virtual)

    def _draw_button(self, surface, rect, label, is_hovered=False):
        return renderer.draw_button(self, surface, rect, label, is_hovered)

    def _draw_grid(self, surface):
        return renderer.draw_grid(self, surface)

    def _draw_selection(self, surface):
        return renderer.draw_selection(self, surface)

    def _draw_sidebar(self, surface):
        return renderer.draw_sidebar(self, surface)

    def _draw_tool_button(self, surface, tool, x, y):
        return renderer.draw_tool_button(self, surface, tool, x, y)

    def _draw_inspector(self, surface, panel_x):
        return renderer.draw_inspector(self, surface, panel_x)

    def _draw_help(self, surface, panel_x):
        return renderer.draw_help(self, surface, panel_x)

    def _draw_status(self, surface):
        return renderer.draw_status(self, surface)

    def _text(self, surface, text, x, y, font, color=(238, 242, 245)):
        return renderer.text(self, surface, text, x, y, font, color)

    def _window_to_virtual(self, pos):
        return input_handler.window_to_virtual(self, pos)

    def _screen_to_world(self, pos):
        return input_handler.screen_to_world(self, pos)

    def _snap(self, value):
        return input_handler.snap(self, value)

    def _app_state(self, name):
        if name == "MENU":
            return "MAIN_MENU"
        if name == "QUIT":
            return None
        return name

    def scan_map_files(self):
        return map_selector.scan_map_files(self)
```

--------------------------------------------------

### 📄 extraction_target_project/map_editor_tool/event_discover.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/map_editor_tool/input_handler.py
#### 🧱 Code Skeleton:
```python
def calculate_placement_pos(editor, mouse_world_x, mouse_world_y, current_definition):
    """설치 Y값 자유화: 카테고리가 enemy일 경우 타일 스냅을 풀고 마우스 좌표를 그대로 반환"""
    if current_definition.category == "enemy":
        return mouse_world_x, mouse_world_y

    # 일반 플랫폼은 기존 격자(스냅) 시스템 유지
    snap_x = (mouse_world_x // editor.GRID_SIZE) * editor.GRID_SIZE
    snap_y = (mouse_world_y // editor.GRID_SIZE) * editor.GRID_SIZE
    return snap_x, snap_y

def handle_event(editor, event, mouse_virtual):
    if event.type == pygame.QUIT:
        return editor._app_state("QUIT")
    if editor.mode == "select":
        from map_editor_tool import map_selector
        return map_selector.handle_select_event(editor, event, mouse_virtual)
        
    # 🎯 최소한의 안전한 단축키만 가볍게 복구하고 싶을 때 추가하는 영역
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return editor._app_state("MENU") # ESC 누르면 안전하게 메뉴로 퇴장
        elif event.key == pygame.K_1:
            editor.tool = "place"
        elif event.key == pygame.K_2:
            editor.tool = "select"
        elif event.key == pygame.K_3:
            editor.tool = "erase"
            
    if event.type == pygame.MOUSEBUTTONDOWN:
        return handle_mouse_down(editor, event, mouse_virtual)
    if event.type == pygame.MOUSEMOTION and editor.dragging and editor.selected_platform:
        world = screen_to_world(editor, mouse_virtual)
        vars_obj = editor.selected_platform.vars
        vars_obj.x = snap(editor, world.x - editor.drag_offset.x)
        vars_obj.y = snap(editor, world.y - editor.drag_offset.y)
    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        editor.dragging = False
    return None

def handle_keydown(editor, event):
    if event.key == pygame.K_ESCAPE:
        return editor._app_state("MENU")
    if event.key == pygame.K_1:
        editor.tool = "place"
    elif event.key == pygame.K_2:
        editor.tool = "select"
    elif event.key == pygame.K_3:
        editor.tool = "erase"
    elif event.key == pygame.K_TAB and editor.palette:
        editor.palette_index = (editor.palette_index + 1) % len(editor.palette)
    elif event.key == pygame.K_s:
        if editor.save_map():
            return editor._app_state("MENU")
    elif event.key == pygame.K_l:
        editor.load_saved_or_source()
    elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
        selection.delete_selected(editor)
    elif editor.selected_platform:
        handle_selected_shortcuts(editor, event)
    return None

def handle_sidebar_click(editor, click_pos):
    """
    사이드바 영역 클릭 시 세부 처리부.
    인스펙터 UI 내부의 버튼 충돌을 계산하여 즉시 속성 및 리사이징을 수행합니다.
    """
    panel_x = settings.VIRTUAL_WIDTH - editor.SIDEBAR_W
    if click_pos.x < panel_x:
        return False

    # 1. 저장 버튼 클릭 처리
    if editor.SAVE_BUTTON_RECT.collidepoint(click_pos):
        from map_editor_tool import serializer
        serializer.save_map(editor)
        return True

    # 2. 툴 버튼 클릭 처리
    for tool_name, rect_x in [("place", panel_x + 24), ("select", panel_x + 116), ("erase", panel_x + 208)]:
        tool_rect = pygame.Rect(rect_x, 246, 82, 42)
        if tool_rect.collidepoint(click_pos):
            editor.tool = tool_name
            return True

    # 3. 팔레트 오브젝트 선택 처리
    for idx, definition in enumerate(editor.palette):
        rect = pygame.Rect(panel_x + 24, 348 + idx * 54, editor.SIDEBAR_W - 48, 42)
        if rect.collidepoint(click_pos):
            editor.palette_index = idx
            return True

    # 4. 플랫폼 인스펙터 버튼 인터랙션 처리 (플랫폼이 선택되어 있을 때만 동작)
    if editor.selected_platform:
        vars_obj = editor.selected_platform.vars

        # ── 가로 길이(Width) 수정 버튼 ──
        if hasattr(editor, "BTN_W_DEC") and editor.BTN_W_DEC.collidepoint(click_pos):
            vars_obj.width = max(editor.GRID_SIZE, vars_obj.width - editor.GRID_SIZE)
            editor.selected_platform.load_image() # 실시간 텍스처 리사이징
            return True
        elif hasattr(editor, "BTN_W_INC") and editor.BTN_W_INC.collidepoint(click_pos):
            vars_obj.width += editor.GRID_SIZE
            editor.selected_platform.load_image()
            return True

        # ── 세로 길이(Height) 수정 버튼 ──
        elif hasattr(editor, "BTN_H_DEC") and editor.BTN_H_DEC.collidepoint(click_pos):
            vars_obj.height = max(10, vars_obj.height - 10)
            editor.selected_platform.load_image()
            return True
        elif hasattr(editor, "BTN_H_INC") and editor.BTN_H_INC.collidepoint(click_pos):
            vars_obj.height += 10
            editor.selected_platform.load_image()
            return True

        # ── 충돌 타입 3종 변경 버튼 ──
        elif hasattr(editor, "BTN_SOLID") and editor.BTN_SOLID.collidepoint(click_pos):
            vars_obj.platform_type = "SOLID"
            vars_obj.is_solid = True
            vars_obj.passable_from_bottom = False
            return True
        elif hasattr(editor, "BTN_ONE_WAY") and editor.BTN_ONE_WAY.collidepoint(click_pos):
            vars_obj.platform_type = "ONE_WAY"
            vars_obj.is_solid = True
            vars_obj.passable_from_bottom = True
            return True
        elif hasattr(editor, "BTN_GHOST") and editor.BTN_GHOST.collidepoint(click_pos):
            vars_obj.platform_type = "GHOST"
            vars_obj.is_solid = False
            vars_obj.passable_from_bottom = True
            return True

    return False

def handle_mouse_down(editor, event, mouse_virtual):
    # 어떤 타입의 좌표가 들어와도 pygame.Vector2로 강제 통합하여 무결성 유지
    pos_vector = pygame.Vector2(mouse_virtual[0], mouse_virtual[1])

    if event.button == 1:
        # 사이드바 충돌 판정 (Vector2 속성인 .x 활용)
        if pos_vector.x >= settings.VIRTUAL_WIDTH - editor.SIDEBAR_W:
            return handle_sidebar_click(editor, pos_vector)

        world = screen_to_world(editor, pos_vector)
        if editor.tool == "place":
            selection.place_selected(editor, world)
        elif editor.tool == "erase":
            target_obj = selection.find_platform_at(editor, world)
            if target_obj:
                if target_obj in editor.map_manager.platforms:
                    editor.map_manager.platforms.remove(target_obj)
                    if hasattr(editor.map_manager, "structures") and target_obj in editor.map_manager.structures:
                        editor.map_manager.structures.remove(target_obj)
                elif target_obj in editor.map_manager.entities:
                    editor.map_manager.entities.remove(target_obj)

                if editor.selected_platform is target_obj:
                    editor.selected_platform = None
        else:
            editor.selected_platform = selection.find_platform_at(editor, world)
            if editor.selected_platform:
                vars_obj = editor.selected_platform.vars
                editor.dragging = True
                editor.drag_offset = pygame.Vector2(world.x - vars_obj.x, world.y - vars_obj.y)
                
    elif event.button == 3:
        editor.tool = "select"
        editor.selected_platform = selection.find_platform_at(editor, screen_to_world(editor, pos_vector))
        
    elif event.button == 4:
        editor.camera.y = max(0, editor.camera.y - editor.GRID_SIZE)
    elif event.button == 5:
        editor.camera.y += editor.GRID_SIZE
        
    return None

def handle_sidebar_click(editor, mouse_virtual):
    # 어떤 형태의 마우스 좌표가 넘어오든 안전하게 언패킹
    x, y = mouse_virtual[0], mouse_virtual[1]
    panel_x = settings.VIRTUAL_WIDTH - editor.SIDEBAR_W

    # 1. 원래의 [저장] 버튼 처리 (기존 구조 완벽 유지)
    if editor.SAVE_BUTTON_RECT.collidepoint(x, y):
        if editor.save_map():
            return editor._app_state("MENU")
        return None

    # 2. 원래의 [툴 선택] 버튼 처리 (기존 구조 완벽 유지)
    tool_buttons = [
        ("place", pygame.Rect(panel_x + 24, 246, 82, 42)),
        ("select", pygame.Rect(panel_x + 116, 246, 82, 42)),
        ("erase", pygame.Rect(panel_x + 208, 246, 82, 42)),
    ]
    for tool, rect in tool_buttons:
        if rect.collidepoint(x, y):
            editor.tool = tool
            return None

    # 3. 원래의 [팔레트 아이템 선택] 처리 (기존 구조 완벽 유지)
    item_y = 348
    for idx, _definition in enumerate(editor.palette):
        rect = pygame.Rect(panel_x + 24, item_y + idx * 54, editor.SIDEBAR_W - 48, 42)
        if rect.collidepoint(x, y):
            editor.palette_index = idx
            editor.tool = "place"
            return None

    # 4. 🎯 추가된 [인스펙터 플랫폼 수정] 처리 (선택된 플랫폼이 있을 때만 안전하게 검사)
    # map_editor_tool/input_handler.py의 handle_sidebar_click 내 인스펙터 수정부
    if editor.selected_platform:
        vars_obj = editor.selected_platform.vars

        # ── 가로 길이(W) 수정 ──
        if hasattr(editor, "BTN_W_DEC") and editor.BTN_W_DEC.collidepoint(x, y):
            vars_obj.width = max(editor.GRID_SIZE, vars_obj.width - editor.GRID_SIZE)
            editor.selected_platform.load_image()
            return None
        elif hasattr(editor, "BTN_W_INC") and editor.BTN_W_INC.collidepoint(x, y):
            vars_obj.width += editor.GRID_SIZE
            editor.selected_platform.load_image()
            return None

        # ── 세로 길이(H) 수정 ──
        elif hasattr(editor, "BTN_H_DEC") and editor.BTN_H_DEC.collidepoint(x, y):
            vars_obj.height = max(10, vars_obj.height - 10)
            editor.selected_platform.load_image()
            return None
        elif hasattr(editor, "BTN_H_INC") and editor.BTN_H_INC.collidepoint(x, y):
            vars_obj.height += 10
            editor.selected_platform.load_image()
            return None

        # ── 충돌 타입 3종 변경 및 내부 물리 플래그 강제 정렬 ──
        elif hasattr(editor, "BTN_SOLID") and editor.BTN_SOLID.collidepoint(x, y):
            vars_obj.platform_type = "SOLID"
            vars_obj.is_solid = True
            vars_obj.passable_from_bottom = False
            return None
        elif hasattr(editor, "BTN_ONE_WAY") and editor.BTN_ONE_WAY.collidepoint(x, y):
            vars_obj.platform_type = "ONE_WAY"
            vars_obj.is_solid = True
            vars_obj.passable_from_bottom = True
            return None
        elif hasattr(editor, "BTN_GHOST") and editor.BTN_GHOST.collidepoint(x, y):
            vars_obj.platform_type = "GHOST"
            vars_obj.is_solid = False
            vars_obj.passable_from_bottom = True
            return None

    return None

def update_camera(editor, dt):
    keys = pygame.key.get_pressed()
    speed = 720 * dt
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        editor.camera.x = max(0, editor.camera.x - speed)
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        max_x = max(0, editor.map_manager.width - (settings.VIRTUAL_WIDTH - editor.SIDEBAR_W))
        editor.camera.x = min(max_x, editor.camera.x + speed)
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        editor.camera.y = max(0, editor.camera.y - speed)
    if keys[pygame.K_s] and not (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
        max_y = max(0, editor.map_manager.height - settings.VIRTUAL_HEIGHT)
        editor.camera.y = min(max_y, editor.camera.y + speed)
    if keys[pygame.K_DOWN]:
        max_y = max(0, editor.map_manager.height - settings.VIRTUAL_HEIGHT)
        editor.camera.y = min(max_y, editor.camera.y + speed)

def window_to_virtual(editor, pos):
    x, y = pos
    return int(x * settings.VIRTUAL_WIDTH / settings.SCREEN_WIDTH), int(y * settings.VIRTUAL_HEIGHT / settings.SCREEN_HEIGHT)

def screen_to_world(editor, pos):
    x, y = pos
    return pygame.Vector2(x + editor.camera.x, y + editor.camera.y)

def snap(editor, value):
    return int(round(float(value) / editor.GRID_SIZE) * editor.GRID_SIZE)
```

--------------------------------------------------

### 📄 extraction_target_project/map_editor_tool/map_editor.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/map_editor_tool/map_selector.py
#### 🧱 Code Skeleton:
```python
def scan_map_files(editor):
    return sorted(
        file_name
        for file_name in os.listdir(editor.maps_dir)
        if file_name.lower().endswith(".json") and os.path.isfile(os.path.join(editor.maps_dir, file_name))
    )

def build_map_selection_buttons(editor):
    editor.map_select_buttons = []
    button_w = 560
    button_h = 54
    start_x = (settings.VIRTUAL_WIDTH - button_w) // 2
    start_y = 310

    # 1. 기존 존재하는 맵 파일 리스트 버튼 생성
    for idx, file_name in enumerate(editor.map_files):
        rect = pygame.Rect(start_x, start_y + idx * 68, button_w, button_h)
        editor.map_select_buttons.append((file_name, rect))

    # 2. 리스트 아래에 유연하게 이어 붙을 Y축 시작점 계산
    new_y = start_y + max(len(editor.map_files), 1) * 68 + 10

    # 🎯 [오류 원인 해결] 누락되었던 새 맵 생성 버튼과 메인메뉴 복귀 버튼 할당
    editor.new_map_button = pygame.Rect(start_x, new_y, button_w, button_h)
    editor.back_button = pygame.Rect(start_x, new_y + 68, button_w, button_h)

def handle_select_event(editor, event, mouse_virtual):
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return editor._app_state("MENU")
    if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
        return None

    for file_name, rect in editor.map_select_buttons:
        if rect.collidepoint(mouse_virtual):
            editor.load_map(file_to_map_name(file_name), file_name)
            return None

    if editor.new_map_button.collidepoint(mouse_virtual):
        file_name = next_new_map_file(editor)
        editor.load_map(file_to_map_name(file_name), file_name)
        return None

    if editor.back_button.collidepoint(mouse_virtual):
        return editor._app_state("MENU")
    return None

def file_to_map_name(file_name):
    stem = os.path.splitext(file_name)[0]
    if stem.startswith("map_"):
        return stem[4:]
    if stem.startswith("map") and stem[3:].isdigit():
        return stem[3:]
    return stem

def map_name_to_file(map_name):
    if map_name is None:
        return None
    name = str(map_name)
    if name.startswith("map") and name.endswith(".json"):
        return name
    if name.isdigit():
        return f"map{name}.json"
    return f"map_{name}.json"

def next_new_map_file(editor):
    base = "map_new.json"
    if base not in editor.map_files and not os.path.exists(os.path.join(editor.maps_dir, base)):
        return base
    idx = 1
    while True:
        file_name = f"map_new_{idx}.json"
        if file_name not in editor.map_files and not os.path.exists(os.path.join(editor.maps_dir, file_name)):
            return file_name
        idx += 1
```

--------------------------------------------------

### 📄 extraction_target_project/map_editor_tool/object_registry.py
#### 🧱 Code Skeleton:
```python
class EditorObjectDefinition:
    type_id: str
    label: str
    category: str
    factory_type: str
    defaults: dict = field(default_factory=dict)
    serializer: Callable | None = None

class EditorObjectRegistry:
    _definitions: dict[str, EditorObjectDefinition] = {}

    @classmethod
    def register(cls, definition: EditorObjectDefinition):
        cls._definitions[definition.type_id] = definition

    @classmethod
    def definitions(cls):
        return list(cls._definitions.values())

    @classmethod
    def get(cls, type_id):
        return cls._definitions.get(type_id)

    # [📂 map_editor_tool/object_registry.py] 수정안

    @classmethod
    def ensure_defaults(cls):
        # 1. 지형 플랫폼 등 기본 오브젝트는 먼저 등록해둡니다.
        if "platform.basic" not in cls._definitions:
            cls.register(
                EditorObjectDefinition(
                    type_id="platform.basic",
                    label="Platform",
                    category="platform",
                    factory_type="platform",
                    defaults={"width": 240, "height": 40, "z_index": 2}
                )
            )

        # 2. 🪐 [폴더 동적 스캔 프로토콜] enemy/enemys 폴더 내부를 실시간 탐색합니다.
        # 프로젝트 루트 기준으로 경로를 유연하게 탐색하기 위한 베이스 설정
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 실제 적 폴더들이 위치한 물리 경로 계산
        enemys_dir = os.path.join(current_dir, "enemy", "enemys")

        if os.path.exists(enemys_dir):
            try:
                # 폴더 내부를 뒤져서 하위 폴더(디렉토리) 목록만 추출합니다.
                for folder_name in os.listdir(enemys_dir):
                    sub_path = os.path.join(enemys_dir, folder_name)
                    if os.path.isdir(sub_path) and not folder_name.startswith("__"):
                        
                        # 예: folder_name이 "test_enemy1" 이라면
                        type_id = f"enemy.{folder_name}"      # "enemy.test_enemy1"
                        # 에디터 UI에 보여줄 레이블 이름 자동 변환 ("test_enemy1" -> "Test Enemy1")
                        label = folder_name.replace("_", " ").title() 
                        
                        if type_id not in cls._definitions:
                            cls.register(
                                EditorObjectDefinition(
                                    type_id=type_id,
                                    label=label,
                                    category="enemy",
                                    factory_type=folder_name, # "test_enemy1" (serializer 및 factory 연동 이름)
                                    defaults={"z_index": 3}
                                )
                            )
                            print(f"🤖 [EditorRegistry] 동적 적 버튼 등록 성공: {label} ({type_id})")
            except Exception as e:
                print(f"⚠️ [EditorRegistry] 적 폴더 스캔 중 오류 발생: {e}")
        else:
            # 폴더를 찾을 수 없는 경우를 대비한 비상 안전 폴백 (더미 기본 등록)
            if "enemy.dummy" not in cls._definitions:
                cls.register(
                    EditorObjectDefinition(
                        type_id="enemy.dummy",
                        label="Dummy Enemy (Fallback)",
                        category="enemy",
                        factory_type="dummy",
                        defaults={"z_index": 3}
                    )
                )
    
    def discover_fabric_definitions(cls):
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates = [
            os.path.join(src_dir, "fabric_system", "editor_objects.json"),
            os.path.join(src_dir, "fabric", "editor_objects.json"),
        ]
        for path in candidates:
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                for item in payload.get("objects", []):
                    cls.register(
                        EditorObjectDefinition(
                            type_id=item["type_id"],
                            label=item.get("label", item["type_id"]),
                            category=item.get("category", "fabric"),
                            factory_type=item.get("factory_type", item["type_id"]),
                            defaults=item.get("defaults", {}),
                        )
                    )
            except (KeyError, TypeError, json.JSONDecodeError) as exc:
                print(f"[MapEditor] fabric palette load skipped: {path} ({exc})")

    @classmethod
    def discover_fabric_definitions(cls):
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates = [
            os.path.join(src_dir, "fabric_system", "editor_objects.json"),
            os.path.join(src_dir, "fabric", "editor_objects.json"),
        ]
        for path in candidates:
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                for item in payload.get("objects", []):
                    cls.register(
                        EditorObjectDefinition(
                            type_id=item["type_id"],
                            label=item.get("label", item["type_id"]),
                            category=item.get("category", "fabric"),
                            factory_type=item.get("factory_type", item["type_id"]),
                            defaults=item.get("defaults", {}),
                        )
                    )
            except (KeyError, TypeError, json.JSONDecodeError) as exc:
                print(f"[MapEditor] fabric palette load skipped: {path} ({exc})")
```

--------------------------------------------------

### 📄 extraction_target_project/map_editor_tool/renderer.py
#### 🧱 Code Skeleton:
```python
def draw(editor, surface):
    surface.fill((10, 15, 20))
    editor.map_manager.draw(surface, camera_offset=(editor.camera.x, editor.camera.y))
    draw_grid(editor, surface)
    draw_selection(editor, surface)
    draw_sidebar(editor, surface)
    draw_status(editor, surface)

def draw_map_select(editor, surface, mouse_virtual):
    surface.fill((18, 24, 30))
    title = editor.header_font.render("Select Map", True, (238, 242, 245))
    surface.blit(title, title.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 150)))

    subtitle_text = f"{len(editor.map_files)} map file(s) in src/map_system/maps"
    subtitle = editor.small_font.render(subtitle_text, True, (180, 198, 214))
    surface.blit(subtitle, subtitle.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 202)))

    if not editor.map_select_buttons:
        empty = editor.font.render("No existing maps found.", True, (220, 229, 237))
        surface.blit(empty, empty.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 310)))

    for file_name, rect in editor.map_select_buttons:
        draw_button(editor, surface, rect, file_name, rect.collidepoint(mouse_virtual))

    draw_button(editor, surface, editor.new_map_button, "Create New Map", editor.new_map_button.collidepoint(mouse_virtual))
    draw_button(editor, surface, editor.back_button, "Back to Main Menu", editor.back_button.collidepoint(mouse_virtual))

    help_text = editor.small_font.render("Click a file to open it. Esc returns to the main menu.", True, (150, 170, 188))
    surface.blit(help_text, help_text.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT - 120)))

def draw_button(editor, surface, rect, label, is_hovered=False):
    fill = (58, 78, 96) if is_hovered else (38, 49, 59)
    border = (152, 177, 199) if is_hovered else (74, 91, 106)
    pygame.draw.rect(surface, fill, rect, border_radius=6)
    pygame.draw.rect(surface, border, rect, 2, border_radius=6)
    label_surface = editor.font.render(label, True, (238, 242, 245))
    surface.blit(label_surface, label_surface.get_rect(center=rect.center))

def draw_grid(editor, surface):
    world_left = int(editor.camera.x)
    world_top = int(editor.camera.y)
    view_w = settings.VIRTUAL_WIDTH - editor.SIDEBAR_W
    view_h = settings.VIRTUAL_HEIGHT
    color = (255, 255, 255, 34)

    grid_overlay = pygame.Surface((view_w, view_h), pygame.SRCALPHA)
    start_x = -(world_left % editor.GRID_SIZE)
    start_y = -(world_top % editor.GRID_SIZE)
    for x in range(start_x, view_w, editor.GRID_SIZE):
        pygame.draw.line(grid_overlay, color, (x, 0), (x, view_h))
    for y in range(start_y, view_h, editor.GRID_SIZE):
        pygame.draw.line(grid_overlay, color, (0, y), (view_w, y))
    surface.blit(grid_overlay, (0, 0))

def draw_selection(editor, surface):
    if not editor.selected_platform:
        return
    vars_obj = editor.selected_platform.vars
    rect = pygame.Rect(
        vars_obj.x - editor.camera.x,
        vars_obj.y - editor.camera.y,
        vars_obj.width,
        vars_obj.height,
    )
    pygame.draw.rect(surface, (255, 229, 122), rect, 4)

def draw_sidebar(editor, surface):
    panel_x = settings.VIRTUAL_WIDTH - editor.SIDEBAR_W
    pygame.draw.rect(surface, (26, 34, 42), (panel_x, 0, editor.SIDEBAR_W, settings.VIRTUAL_HEIGHT))
    pygame.draw.line(surface, (88, 106, 124), (panel_x, 0), (panel_x, settings.VIRTUAL_HEIGHT), 3)

    text(editor, surface, "Map Editor", panel_x + 24, 34, editor.header_font)
    text(editor, surface, f"Editing: {editor.selected_map_file}", panel_x + 24, 78, editor.small_font, (180, 198, 214))
    text(editor, surface, "Save writes this file and exits.", panel_x + 24, 104, editor.small_font, (180, 198, 214))

    from map_editor_tool import input_handler
    hovered = editor.SAVE_BUTTON_RECT.collidepoint(input_handler.window_to_virtual(editor, pygame.mouse.get_pos()))
    draw_button(editor, surface, editor.SAVE_BUTTON_RECT, "Save", hovered)

    text(editor, surface, "Tools", panel_x + 24, 214, editor.font)
    draw_tool_button(editor, surface, "place", panel_x + 24, 246)
    draw_tool_button(editor, surface, "select", panel_x + 116, 246)
    draw_tool_button(editor, surface, "erase", panel_x + 208, 246)

    text(editor, surface, "Palette", panel_x + 24, 310, editor.font)
    for idx, definition in enumerate(editor.palette):
        rect = pygame.Rect(panel_x + 24, 348 + idx * 54, editor.SIDEBAR_W - 48, 42)
        active = idx == editor.palette_index
        pygame.draw.rect(surface, (67, 92, 111) if active else (38, 49, 59), rect, border_radius=5)
        pygame.draw.rect(surface, (145, 170, 190) if active else (74, 91, 106), rect, 1, border_radius=5)
        text(editor, surface, definition.label, rect.x + 12, rect.y + 10, editor.small_font)

    draw_inspector(editor, surface, panel_x)
    draw_help(editor, surface, panel_x)

def draw_tool_button(editor, surface, tool, x, y):
    rect = pygame.Rect(x, y, 82, 42)
    active = editor.tool == tool
    pygame.draw.rect(surface, (72, 101, 82) if active else (38, 49, 59), rect, border_radius=5)
    pygame.draw.rect(surface, (142, 188, 155) if active else (74, 91, 106), rect, 1, border_radius=5)
    text(editor, surface, tool, x + 10, y + 11, editor.small_font)

def draw_inspector(editor, surface, panel_x):
    y = 520
    text(editor, surface, "Inspector", panel_x + 24, y, editor.header_font)
    if not editor.selected_platform:
        text(editor, surface, "No selection", panel_x + 24, y + 40, editor.small_font, (180, 198, 214))
        return
        
    vars_obj = editor.selected_platform.vars
    
    # 기본 좌표 및 크기 출력
    text(editor, surface, f"Pos: ({int(vars_obj.x)}, {int(vars_obj.y)})", panel_x + 24, y + 36, editor.small_font)
    text(editor, surface, f"Size: {int(vars_obj.width)} x {int(vars_obj.height)}", panel_x + 24, y + 60, editor.small_font)

    # --- [가로/세로 조절 UI 영역] ---
    # 가로(W) 조절 버튼 레이아웃 (W: [ - ] 100 [ + ])
    text(editor, surface, "W:", panel_x + 24, y + 90, editor.small_font)
    editor.BTN_W_DEC = pygame.Rect(panel_x + 50, y + 84, 28, 24)
    editor.BTN_W_INC = pygame.Rect(panel_x + 130, y + 84, 28, 24)
    
    # 세로(H) 조절 버튼 레이아웃 (H: [ - ] 40 [ + ])
    text(editor, surface, "H:", panel_x + 175, y + 90, editor.small_font)
    editor.BTN_H_DEC = pygame.Rect(panel_x + 195, y + 84, 28, 24)
    editor.BTN_H_INC = pygame.Rect(panel_x + 275, y + 84, 28, 24)

    # W 버튼 렌더링
    pygame.draw.rect(surface, (50, 65, 80), editor.BTN_W_DEC, border_radius=3)
    pygame.draw.rect(surface, (50, 65, 80), editor.BTN_W_INC, border_radius=3)
    text(editor, surface, "-", panel_x + 60, y + 88, editor.small_font)
    text(editor, surface, "+", panel_x + 140, y + 88, editor.small_font)
    text(editor, surface, f"{int(vars_obj.width)}", panel_x + 88, y + 90, editor.small_font, (255, 230, 150))

    # H 버튼 렌더링
    pygame.draw.rect(surface, (50, 65, 80), editor.BTN_H_DEC, border_radius=3)
    pygame.draw.rect(surface, (50, 65, 80), editor.BTN_H_INC, border_radius=3)
    text(editor, surface, "-", panel_x + 205, y + 88, editor.small_font)
    text(editor, surface, "+", panel_x + 285, y + 88, editor.small_font)
    text(editor, surface, f"{int(vars_obj.height)}", panel_x + 233, y + 90, editor.small_font, (255, 230, 150))

    # --- [플랫폼 충돌 타입 UI 버튼 영역] ---
    text(editor, surface, "Collision Type:", panel_x + 24, y + 130, editor.small_font)
    
    # 3종류 버튼의 Rect 생성 및 할당
    editor.BTN_SOLID = pygame.Rect(panel_x + 24, y + 155, 80, 28)
    editor.BTN_ONE_WAY = pygame.Rect(panel_x + 114, y + 155, 90, 28)
    editor.BTN_GHOST = pygame.Rect(panel_x + 214, y + 155, 80, 28)

    current_type = getattr(vars_obj, "platform_type", "SOLID")

    # 버튼 내부 그리기 함수
    def draw_type_btn(rect, label, target_type):
        is_active = (current_type == target_type)
        bg_color = (72, 101, 82) if is_active else (38, 49, 59)
        border_color = (142, 188, 155) if is_active else (74, 91, 106)
        pygame.draw.rect(surface, bg_color, rect, border_radius=4)
        pygame.draw.rect(surface, border_color, rect, 1, border_radius=4)
        text(editor, surface, label, rect.x + 8, rect.y + 6, editor.small_font, (255, 255, 255) if is_active else (180, 198, 214))

    draw_type_btn(editor.BTN_SOLID, "SOLID", "SOLID")
    draw_type_btn(editor.BTN_ONE_WAY, "ONE-WAY", "ONE_WAY")
    draw_type_btn(editor.BTN_GHOST, "GHOST", "GHOST")

def draw_help(editor, surface, panel_x):
    y = settings.VIRTUAL_HEIGHT - 210
    lines = [
        "1 place  2 select  3 erase",
        "WASD/arrows pan camera",
        "S save  L reload  Esc menu",
        "[ ] width  ; ' height",
        "V visibility  P pass-through",
    ]
    for idx, line in enumerate(lines):
        text(editor, surface, line, panel_x + 24, y + idx * 30, editor.small_font, (180, 198, 214))

def draw_status(editor, surface):
    pygame.draw.rect(surface, (18, 24, 30), (0, settings.VIRTUAL_HEIGHT - 36, settings.VIRTUAL_WIDTH - editor.SIDEBAR_W, 36))
    text(editor, surface, editor.status_message, 18, settings.VIRTUAL_HEIGHT - 28, editor.small_font, (220, 229, 237))

def text(editor, surface, text_str, x, y, font, color=(238, 242, 245)):
    surface.blit(font.render(str(text_str), True, color), (x, y))
```

--------------------------------------------------

### 📄 extraction_target_project/map_editor_tool/selection.py
#### 🧱 Code Skeleton:
```python
def get_object_visibility(editor, obj):
    """인스펙터 팅김 해결: 객체 유형 불일치로 인한 속성 부재를 해결하는 안전 조회 함수"""
    if hasattr(obj, "vars"):
        return getattr(obj.vars, "is_visible", True)
    return getattr(obj, "is_visible", True)

def find_platform_at(editor, world):
    # 1. 먼저 플랫폼 지형 레이어 탐색
    for platform in reversed(editor.map_manager.platforms):
        vars_obj = platform.vars
        rect = pygame.Rect(vars_obj.x, vars_obj.y, vars_obj.width, vars_obj.height)
        if rect.collidepoint(world.x, world.y):
            return platform

    # 2. 없으면 엔티티(적/NPC) 레이어 탐색 (find_entity_at 통합 연동)
    if hasattr(editor.map_manager, "entities") and editor.map_manager.entities:
        for entity in reversed(editor.map_manager.entities):
            vars_obj = getattr(entity, "vars", None)
            if vars_obj:
                ent_x = getattr(vars_obj, "x", 0)
                ent_y = getattr(vars_obj, "y", 0)
                ent_w = getattr(vars_obj, "width", 50)  # dummy_main 명세 가이드 기준
                ent_h = getattr(vars_obj, "height", 80)
                rect = pygame.Rect(ent_x, ent_y, ent_w, ent_h)
                if rect.collidepoint(world.x, world.y):
                    return entity
    return None

def delete_selected(editor):
    if not editor.selected_platform:
        return

    # 1. 플랫폼 컨테이너에서 제거 시도
    if editor.selected_platform in editor.map_manager.platforms:
        editor.map_manager.platforms.remove(editor.selected_platform)
        if hasattr(editor.map_manager, "structures") and editor.selected_platform in editor.map_manager.structures:
            editor.map_manager.structures.remove(editor.selected_platform)
        editor.selected_platform = None
        editor.status_message = "Deleted selected platform"

    # 2. 엔티티 컨테이너에서 제거 시도
    elif hasattr(editor.map_manager, "entities") and editor.selected_platform in editor.map_manager.entities:
        editor.map_manager.entities.remove(editor.selected_platform)
        editor.selected_platform = None
        editor.status_message = "Deleted selected entity unit"

def place_selected(editor, world):
    if not editor.palette:
        return
    definition = editor.palette[editor.palette_index]
    data = dict(definition.defaults)

    # 🧱 [분기 1] 순정 지형 플랫폼 생성 로직 (인자 규격 유지)
    if definition.category == "platform":
        data.setdefault("width", 240)
        data.setdefault("height", 40)
        platform = EntityRegistry.create(
            definition.factory_type,
            x=editor._snap(world.x),
            y=editor._snap(world.y),
            width=data["width"],
            height=data["height"],
            is_visible=data.get("is_visible", True),
            can_pass_through=data.get("can_pass_through", False),
        )
        if not platform and definition.factory_type == "platform":
            from platform_system.platform_main import Platform
            platform = Platform(
                x=editor._snap(world.x),
                y=editor._snap(world.y),
                width=data["width"],
                height=data["height"],
                is_visible=data.get("is_visible", True),
                can_pass_through=data.get("can_pass_through", False),
            )
        if platform:
            platform.type = definition.factory_type
            platform.z_index = data.get("z_index", 2)
            editor.map_manager.platforms.append(platform)
            if not hasattr(editor.map_manager, "structures"):
                editor.map_manager.structures = []
            editor.map_manager.structures.append(platform)
            editor.selected_platform = platform
            editor.status_message = f"Placed {definition.label}"

    # 🪐 [분기 2] 적(Enemy) 및 NPC 엔티티 생성 로직 (공중 배치 자유도 보장)
    elif definition.category in ["enemy", "npc"]:
         entity = EntityRegistry.create(
             definition.factory_type,
             x=editor._snap(world.x),
             y=editor._snap(world.y)
         )

         # 🎯 [안전장치] EntityRegistry가 동적으로 "dummy"를 생성하지 못했을 때를 위한 직접 복구 분기
         if not entity and definition.factory_type == "dummy":
             from enemy.enemys.dummy.dummy_main import DummyEnemy
             entity = DummyEnemy(
                 x=editor._snap(world.x),
                 y=editor._snap(world.y)
             )

         if entity:
             # 순정 지형 매커니즘과 충돌하지 않도록 하위 변수 타입 보존
             entity.type = definition.factory_type
             entity.z_index = data.get("z_index", 3)

             if not hasattr(editor.map_manager, "entities"):
                 editor.map_manager.entities = []
             editor.map_manager.entities.append(entity)

             # 에디터 선택 시스템 호환성 바인딩
             editor.selected_platform = entity
             editor.status_message = f"Placed Entity: {definition.label}"
```

--------------------------------------------------

### 📄 extraction_target_project/map_editor_tool/serializer.py
#### 🧱 Code Skeleton:
```python
def save_map(editor):
    data = serialize_map(editor)
    file_name = editor.selected_map_file or editor._map_name_to_file(editor.save_name or editor.map_name or "new")
    save_path = os.path.join(editor.maps_dir, file_name)
    temp_path = f"{save_path}.tmp"
    try:
        os.makedirs(editor.maps_dir, exist_ok=True)
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(temp_path, save_path)
        editor.status_message = f"Saved {file_name}"
        return True
    except OSError as exc:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        editor.status_message = f"Save failed: {exc}"
        return False

def load_saved_or_source(editor):
    from map_system.map_main import GameMap
    editor.map_manager = GameMap(map_id=editor.map_name)
    if not hasattr(editor.map_manager, "structures"):
        editor.map_manager.structures = []
    editor.selected_platform = None
    editor.dragging = False
    editor.status_message = f"Reloaded {editor.selected_map_file}"

def serialize_map(editor):
    if not hasattr(editor.map_manager, "structures"):
        editor.map_manager.structures = []

    return {
        "schema_version": 2,
        "map_id": editor.map_manager.map_id,
        "map_width": editor.map_manager.width,
        "map_height": editor.map_manager.height,
        "background_type": editor.map_manager.background_type,
        "ground_type": editor.map_manager.ground_type,
        "ground_y": editor.map_manager.ground_y,
        "platforms": [
            _serialize_platform(editor, platform)
            for platform in editor.map_manager.platforms
            if platform not in editor.map_manager.structures and not getattr(platform, "is_ground", False)
        ],
        "structures": [_serialize_structure(editor, struct) for struct in editor.map_manager.structures],
        "entities": [_serialize_entity(editor, entity) for entity in editor.map_manager.entities],
        "triggers": [_serialize_trigger(editor, trigger) for trigger in editor.map_manager.triggers],
        "editor_metadata": {
            "source_map": editor.map_name,
            "file_name": editor.selected_map_file,
            "object_registry": [
                {
                    "type_id": definition.type_id,
                    "category": definition.category,
                    "factory_type": definition.factory_type,
                }
                for definition in editor.palette
            ],
            "future_layers": {
                "fabric": [],
            },
        },
    }

def _serialize_platform(editor, platform):
    vars_obj = platform.vars
    
    # platform_type 속성이 존재하지 않는 구버전 대비 예외 처리
    p_type = getattr(vars_obj, "platform_type", "SOLID")

    return {
        "type": getattr(platform, "type", "platform"),
        "x": int(vars_obj.x),
        "y": int(vars_obj.y),
        "width": int(vars_obj.width),
        "height": int(vars_obj.height),
        "is_visible": bool(vars_obj.is_visible),
        "is_solid": bool(vars_obj.is_solid),
        "platform_type": p_type,  # 🎯 JSON 저장 스펙에 반드시 플랫폼 유형 추가 보장!
        "can_pass_through": bool(getattr(vars_obj, "passable_from_bottom", False) or getattr(vars_obj, "can_pass_through", False)),
        "z_index": int(getattr(platform, "z_index", 2)),
    }

def _serialize_structure(editor, struct):
    vars_obj = struct.vars
    
    # 🎯 데이터 주도형 아키텍처 상태 추출 무결성 확보
    # struct.type 또는 vars_obj에 내장된 platform_type 프로토콜을 안전하게 탐색
    p_type = getattr(struct, "type", "SOLID")
    if hasattr(vars_obj, "platform_type"):
        p_type = vars_obj.platform_type
    elif hasattr(struct, "platform_type"):
        p_type = struct.platform_type

    return {
        "type": str(p_type), # 인게임 및 하위 호환성을 위한 분기 매핑 보존
        "platform_type": str(p_type), # 맵 시스템 파싱 동기화를 위한 핵심 필드 추가
        "x": int(vars_obj.x),
        "y": int(vars_obj.y),
        "width": int(vars_obj.width),
        "height": int(vars_obj.height),
        "is_visible": bool(vars_obj.is_visible),
        "can_pass_through": bool(getattr(vars_obj, "passable_from_bottom", False) or getattr(vars_obj, "can_pass_through", False)),
        "z_index": int(getattr(struct, "z_index", 2)),
    }

def _serialize_entity(editor, entity):
    vars_obj = getattr(entity, "vars", None)

    # 타입 추론의 무결성을 확보하기 위한 폴백 처리
    entity_type = _infer_entity_type(editor, entity)
    if not entity_type and entity.__class__.__name__ == "DummyEnemy":
        entity_type = "dummy_enemy"

    return {
        "type": entity_type,
        "x": int(getattr(vars_obj, "x", 0)),
        "y": int(getattr(vars_obj, "y", 0)),
        "z_index": int(getattr(entity, "z_index", 3)),
    }

def _serialize_trigger(editor, trigger):
     bounds = trigger.get("bounds", pygame.Rect(0, 0, 0, 0))
     return {
         "type": trigger.get("type", "enter_area"),
         "bounds": {
             "x": bounds.x,
             "y": bounds.y,
             "width": bounds.width,
             "height": bounds.height,
         },
         "action": trigger.get("action", {}),
         "triggered": bool(trigger.get("triggered", False)),
     }

def _infer_entity_type(editor, entity):
    """엔티티 객체로부터 JSON에 저장할 type_id를 안전하게 매핑 및 역추론"""
    if hasattr(entity, "type"):
        return entity.type

    # 클래스 이름을 기반으로 타입 자동 파싱 (예: TestEnemy1 -> test_enemy1)
    class_name = entity.__class__.__name__
    
    # "Enemy" 접미사가 붙어있다면 제거 (예: DummyEnemy -> Dummy -> dummy)
    if class_name.endswith("Enemy") and class_name != "Enemy":
        class_name = class_name[:-5]
        
    # PascalCase -> snake_case 정규식 변환
    import re
    snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
    return snake_name
```

--------------------------------------------------

### 📄 extraction_target_project/map_system/__init__.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/map_system/map_engine.py
#### 🧱 Code Skeleton:
```python
class AssetManager:
    """
    중앙 집중식 자원 관리자 (AssetManager)
    이미지를 캐싱하여 메모리에 동일 리소스가 중복 로드되는 것을 물리적으로 방지합니다.
    """
    _image_cache = {}

    @classmethod
    def get_image(cls, path, use_alpha=True):
        normalized_path = os.path.abspath(path)
        if normalized_path not in cls._image_cache:
            try:
                if use_alpha:
                    image = pygame.image.load(normalized_path).convert_alpha()
                else:
                    image = pygame.image.load(normalized_path).convert()
                cls._image_cache[normalized_path] = image
            except Exception as e:
                print(f"🚨 [AssetManager] 리소스 로드 실패: {path} ({e})")
                # 폴백용 임시 서피스 생성
                fallback = pygame.Surface((32, 32), pygame.SRCALPHA)
                fallback.fill((255, 0, 128))  # 핫핑크색 경고용 박스
                cls._image_cache[normalized_path] = fallback
        return cls._image_cache[normalized_path]

class EntityRegistry:
    """
    클래스 참조 격리를 위한 중앙 집중식 Registry 시스템
    """
    _registry = {}

    @classmethod
    def register(cls, type_name, class_obj):
        cls._registry[type_name] = class_obj

    @classmethod
    def create(cls, type_name, x, y, **kwargs):
        # 1. 기존에 이미 캐싱/등록된 엔티티가 있다면 전달된 kwargs를 포함해 인스턴스 생성
        if type_name in cls._registry:
            return cls._registry[type_name](x, y, **kwargs)
        
        # 2. 🚀 [자동 동적 탐색] 등록되지 않은 타입인 경우, 폴더 규칙을 기반으로 실시간 임포트 시도
        try:
            # 예: "test_enemy1" -> enemy.enemys.test_enemy1.test_enemy1_main
            # "dummy" -> enemy.enemys.dummy.dummy_main
            module_path = f"enemy.enemys.{type_name}.{type_name}_main"
            module = importlib.import_module(module_path)

            # 스네이크 케이스를 PascalCase로 변환 (예: test_enemy1 -> TestEnemy1)
            pascal_name = "".join([w.capitalize() for w in type_name.split("_")])
            
            class_obj = None
            # 클래스 이름 매칭 유연성 보장 (TestEnemy1, TestEnemy1Enemy, DummyEnemy 등 탐색)
            for candidate_name in [pascal_name, f"{pascal_name}Enemy", f"{pascal_name}Main"]:
                if hasattr(module, candidate_name):
                    class_obj = getattr(module, candidate_name)
                    break
            
            if class_obj:
                # 성능을 위해 다음 호출부터는 캐싱되도록 등록
                cls.register(type_name, class_obj)
                cls.register(class_obj.__name__, class_obj)
                # 새로 임포트한 클래스를 인스턴스화할 때도 **kwargs를 안전하게 넘겨줌
                return class_obj(x, y, **kwargs)
                
        except Exception as e:
            print(f"⚠️ [EntityRegistry] '{type_name}' 동적 생성 실패: {e}")

        return None

class TriggerBoxInstance:
    def __init__(self, x, y, width, height, trigger_module, action_module):
        self.rect = pygame.Rect(x, y, width, height)
        self.trigger_module_name = trigger_module
        self.action_module_name = action_module
        self.is_triggered = False  # 단발성 실행 제어용 플래그

    def to_dict(self):
        return {
            "x": self.rect.x,
            "y": self.rect.y,
            "width": self.rect.width,
            "height": self.rect.height,
            "trigger_module": self.trigger_module_name,
            "action_module": self.action_module_name
        }

class MapManager:
    """
    데이터 지향 설계 기반 범용 MapManager 시스템
    JSON 데이터를 분석하여 지형 정보, 인게임 엔티티, 트리거/이벤트 라이프사이클을 총괄 제어합니다.
    """
    # 🔴 인게임(map_name_or_id)과 에디터(인자 없음) 양쪽 호출 규격을 모두 수용하는 가변 인자 혹은 초깃값 지정
    def __init__(self, map_name_or_id="stage1"):
        self.map_name_or_id = map_name_or_id
        
        self.map_id = 1
        self.width = settings.VIRTUAL_WIDTH
        self.height = settings.VIRTUAL_HEIGHT
        
        self.background_type = "bg_sky"
        self.ground_type = "ground_dirt"
        self.ground_y = settings.GROUND_Y
        
        self.platforms = []
        self.structures = []  # 🎯 구조물 리스트 선언
        self.entities = []
        self.triggers = []
        self.trigger_boxes = []
        self.action_handlers = {}
        
        # 🌄 백드롭 무한 시차 배경용 파라미터 (안전 마진 및 시차 배율 변수화)
        self.safe_margin = 400
        self.backdrop_parallax_factor_x = 0.05
        self.backdrop_parallax_factor_y = 0.05
        
        # 🌟 맵 데이터 로드 및 에셋 초기화
        self.load_map_data()
        self.load_assets()

    # 🟢 [인터페이스 추가] 에디터에서 마우스 브러시로 트리거를 심을 때 에러 없이 받아주는 팩토리
    def add_trigger_box(self, x, y, width, height, trigger_module, action_module):
        for box in self.trigger_boxes:
            if box.rect.x == x and box.rect.y == y:
                return False
        new_box = TriggerBoxInstance(x, y, width, height, trigger_module, action_module)
        self.trigger_boxes.append(new_box)
        return True

    # 🟢 [인터페이스 추가] 에디터 지우개 모드 시 트리거 박스까지 감지하여 제거하는 확장 지우개
    def remove_at_position(self, x, y):
        if hasattr(self, "platforms") and self.platforms:
            self.platforms = [p for p in self.platforms if not (p.x == x and p.y == y)]
        self.trigger_boxes = [box for box in self.trigger_boxes if not box.rect.collidepoint(x, y)]

    def load_map_data(self):
        """JSON 데이터 분석 및 예외 처리 바인딩"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 문자열(예: 'stage1') 또는 정수(예: 1) 형태 모두 호환
        # map_1.json이 있으므로 map1.json 뿐만 아니라 map_1.json도 검사
        if isinstance(self.map_name_or_id, int) or (isinstance(self.map_name_or_id, str) and self.map_name_or_id.isdigit()):
            file_name_1 = f"map_{self.map_name_or_id}.json"
            file_name_2 = f"map{self.map_name_or_id}.json"
            json_path = os.path.join(current_dir, "maps", file_name_1)
            if not os.path.exists(json_path):
                json_path = os.path.join(current_dir, "maps", file_name_2)
        else:
            file_name = f"map_{self.map_name_or_id}.json"
            json_path = os.path.join(current_dir, "maps", file_name)
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # 복합 스키마 지원 (nested map_data vs flat 구조)
            if "map_data" in data:
                map_inner_data = data["map_data"]
                settings_data = map_inner_data.get("settings", {})
            else:
                map_inner_data = data
                settings_data = {
                    "width": data.get("map_width"),
                    "height": data.get("map_height"),
                    "background_type": data.get("background_type"),
                    "ground_type": data.get("ground_type"),
                    "ground_y": data.get("ground_y"),
                }
                
            self.map_id = data.get("map_id", 1)
            self.width = settings_data.get("width") or settings_data.get("map_width") or settings.VIRTUAL_WIDTH
            self.height = settings_data.get("height") or settings_data.get("map_height") or settings.VIRTUAL_HEIGHT
            self.background_type = settings_data.get("background_type") or "bg_sky"
            self.ground_type = settings_data.get("ground_type") or "ground_dirt"
            self.ground_y = settings_data.get("ground_y") or settings.GROUND_Y
            
            # 리스트 리셋
            self.platforms = []
            self.structures = []
            self.entities = []
            self.triggers = []
            self.trigger_boxes = []
            
            # 🧱 플랫폼 데이터 등록 생성 (EntityRegistry 연동)
            for p_data in map_inner_data.get("platforms", []):
                p_type = p_data.get("type", "platform")
                platform_obj = EntityRegistry.create(
                    p_type,
                    x=p_data["x"],
                    y=p_data["y"],
                    width=p_data["width"],
                    height=p_data["height"],
                    is_visible=p_data.get("is_visible", True),
                    can_pass_through=p_data.get("can_pass_through", False) or p_data.get("passable_from_bottom", False)
                )
                if platform_obj:
                    platform_obj.z_index = p_data.get("z_index", 2)
                    self.platforms.append(platform_obj)
            
            # 🧱 structures 또는 objects 리스트 데이터 로드 무결성 확보
            raw_structs = []
            if "structures" in map_inner_data:
                raw_structs.extend(map_inner_data.get("structures", []))
            if "objects" in map_inner_data:
                raw_structs.extend(map_inner_data.get("objects", []))

            for s_data in raw_structs:
                try:
                    if not isinstance(s_data, dict):
                        continue
                    x = float(s_data.get("x", 0.0))
                    y = float(s_data.get("y", 0.0))
                    width = float(s_data.get("width", 240.0))
                    height = float(s_data.get("height", 40.0))
                    type_val = str(s_data.get("type", "platform"))

                    platform_obj = EntityRegistry.create(
                        "platform",
                        x=x,
                        y=y,
                        width=int(width),
                        height=int(height),
                        is_visible=s_data.get("is_visible", True),
                        can_pass_through=s_data.get("can_pass_through", False) or s_data.get("passable_from_bottom", False)
                    )
                    if platform_obj:
                        platform_obj.type = type_val
                        platform_obj.z_index = int(s_data.get("z_index", 2))
                        self.structures.append(platform_obj)
                        self.platforms.append(platform_obj)
                except Exception as e:
                    print(f"⚠️ [MapManager] 구조물 개별 파싱 실패: {e}")
                    
            # 🎯 엔티티(적, NPC 등) 동적 생성 (EntityRegistry 연동)
            entity_data = map_inner_data.get("entities", [])
            enemy_data = map_inner_data.get("enemies", [])
            if enemy_data:
                entity_data = [item for item in entity_data if item.get("type") != "dummy"]

            for e_data in entity_data:
                self._create_entity_from_data(e_data)

            for e_data in enemy_data:
                self._create_entity_from_data(e_data)
                    
            # 🔔 트리거 영역 파싱 및 예외 처리
            for t_data in map_inner_data.get("triggers", []):
                bounds = t_data.get("bounds", {})
                action = t_data.get("action", {})
                if bounds and action:
                    self.triggers.append({
                        "type": t_data.get("type", "enter_area"),
                        "bounds": pygame.Rect(bounds.get("x", 0), bounds.get("y", 0), bounds.get("width", 50), bounds.get("height", 50)),
                        "action": action,
                        "triggered": t_data.get("triggered", False)
                    })
                    
            # 🟢 [기능 확장] JSON에서 trigger_boxes 안전하게 파싱 및 바인딩
            if "trigger_boxes" in map_inner_data:
                for tb_data in map_inner_data["trigger_boxes"]:
                    box = TriggerBoxInstance(
                        x=tb_data["x"], y=tb_data["y"],
                        width=tb_data["width"], height=tb_data["height"],
                        trigger_module=tb_data["trigger_module"],
                        action_module=tb_data["action_module"]
                    )
                    self.trigger_boxes.append(box)
                    
        except FileNotFoundError:
            print(f"🚨 [MapManager] 맵 구성 파일({json_path})이 없어 기본값으로 초기화합니다.")
            self.fallback_default_map()
        except json.JSONDecodeError:
            print(f"🚨 [MapManager] {json_path} JSON 문법 파싱 오류가 있어 기본값으로 초기화합니다.")
            self.fallback_default_map()
        except Exception as e:
            print(f"🚨 [MapManager] 맵 데이터 로드 오류: {e}")
            import traceback
            traceback.print_exc()
            self.fallback_default_map()

    def _create_entity_from_data(self, e_data):
        e_type = e_data.get("type")
        if not e_type:
            return

        # x, y 값을 확실하게 선점
        spawn_x = e_data.get("x", 0)
        spawn_y = e_data.get("y", 0)

        # 🎯 [구조 보강] 생성자가 위치 인자(x, y) 혹은 키워드 인자(x=x, y=y)를 유연하게 수용할 수 있도록 safe 파라미터 전달
        entity_obj = EntityRegistry.create(
            e_type,
            spawn_x,
            spawn_y,
            x=spawn_x,
            y=spawn_y
        )
        
        if entity_obj:
            # 1. 내부 변수 프로토콜(self.vars) 데이터 동기화
            vars_obj = getattr(entity_obj, "vars", None)
            if vars_obj:
                vars_obj.x = spawn_x
                vars_obj.y = spawn_y
            
            # 2. 렌더링 및 충돌용 순정 pygame.Rect 좌표 동기화 (화면 누락 완전 차단)
            if hasattr(entity_obj, "rect") and entity_obj.rect is not None:
                entity_obj.rect.x = spawn_x
                entity_obj.rect.y = spawn_y
                
            entity_obj.z_index = e_data.get("z_index", 3)
            self.entities.append(entity_obj)

    def fallback_default_map(self):
        """안전장치: 예외 발생 시 게임 크래시를 방지하기 위한 디폴트 세팅"""
        self.width = settings.VIRTUAL_WIDTH
        self.height = settings.VIRTUAL_HEIGHT
        self.background_type = "bg_sky"
        self.ground_type = "ground_dirt"
        self.ground_y = settings.GROUND_Y
        self.platforms = []
        self.structures = []
        self.entities = []
        self.triggers = []

    def load_assets(self):
        """AssetManager 연동을 통해 중복 이미지 로드를 배제"""
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bg_dir = os.path.join(src_dir, "assets", "images", "map", "background")
        ground_dir = os.path.join(src_dir, "assets", "images", "map", "ground")
        test_bg_dir = os.path.join(bg_dir, "test_map")

        self.bg_image = AssetManager.get_image(os.path.join(bg_dir, f"{self.background_type}.png"))
        self.ground_image = AssetManager.get_image(os.path.join(ground_dir, f"{self.ground_type}.png"))

        # 백드롭 로드 및 2D 스크롤용 스케일 마진 적용
        loaded_backdrop = AssetManager.get_image(os.path.join(test_bg_dir, "backdrop.jpg"), use_alpha=False)
        target_h = settings.VIRTUAL_HEIGHT + self.safe_margin
        orig_w = loaded_backdrop.get_width()
        orig_h = loaded_backdrop.get_height()
        if orig_h > 0:
            target_w = int(orig_w * (target_h / orig_h))
            self.backdrop = pygame.transform.scale(loaded_backdrop, (target_w, target_h))
        else:
            self.backdrop = loaded_backdrop

        self.background = AssetManager.get_image(os.path.join(test_bg_dir, "background.jpg"), use_alpha=False)

    def register_action_handler(self, action_type, handler_callback):
        """외부에서 트리거 액션(대사 등) 발생 시 실행할 핸들러 등록 (느슨한 결합 구조)"""
        self.action_handlers[action_type] = handler_callback

    def execute_trigger_action(self, action):
        """추상화된 트리거 이벤트 처리기"""
        action_type = action.get("type")
        
        # 1. 외부 핸들러가 등록되어 있는 경우 우선 처리 (느슨한 결합 구조 연동)
        if action_type in self.action_handlers:
            self.action_handlers[action_type](action)
            return

        # 2. 기본 엔진 내장 액션
        if action_type == "spawn_enemy":
            e_type = action.get("entity_type")
            sx = action.get("spawn_x", 0)
            sy = action.get("spawn_y", 0)
            entity_obj = EntityRegistry.create(e_type, x=sx, y=sy)
            if entity_obj:
                entity_obj.z_index = action.get("z_index", 3)
                self.entities.append(entity_obj)
                print(f"🔊 [MapManager] 트리거 액션 실행: '{e_type}' 소환 성공! 좌표: ({sx}, {sy})")

    def update(self, dt, player_obj=None):
        """인게임 오브젝트 라이프사이클 및 트리거 관리 루틴"""
        # 1. 플랫폼 상태 업데이트 (필요한 경우)
        for platform in self.platforms:
            if hasattr(platform, "update"):
                platform.update()

        # 2. 엔티티 상태 업데이트 및 라이프사이클 갱신 (파괴된 객체 안전 메모리 해제)
        active_entities = []
        for entity in self.entities:
            # 상태 갱신 수행
            if hasattr(entity, "update"):
                try:
                    # Player 연동이 우선적으로 필요한 경우
                    entity.update(player_obj)
                except TypeError:
                    try:
                        # dt(delta_time)만 받는 기본 update
                        entity.update(dt)
                    except TypeError:
                        # 인자가 없는 update
                        entity.update()

            # 파괴 판정 (HP가 0 이하이거나 파괴 플래그가 선언된 경우)
            is_dead = False
            if hasattr(entity, "vars") and hasattr(entity.vars, "hp") and entity.vars.hp <= 0:
                is_dead = True
            elif getattr(entity, "is_destroyed", False):
                is_dead = True

            if is_dead:
                # 소멸 콜백 호출
                if hasattr(entity, "destroy"):
                    entity.destroy()
                elif hasattr(entity, "on_remove"):
                    entity.on_remove()
                print(f"🗑️ [MapManager] 엔티티 파괴 해제: {entity.__class__.__name__}")
            else:
                active_entities.append(entity)

        self.entities = active_entities

        # 3. 트리거 센서 영역 체크 (플레이어 위치 기반)
        if player_obj:
            player_rect = pygame.Rect(player_obj.vars.x, player_obj.vars.y, player_obj.vars.width, player_obj.vars.height)
            for trigger in self.triggers:
                if not trigger["triggered"]:
                    if player_rect.colliderect(trigger["bounds"]):
                        trigger["triggered"] = True
                        self.execute_trigger_action(trigger["action"])
            
            # 🟢 [기능 확장] 트리거 박스 실시간 감시 엔진 구동
            self.update_trigger_system(player_obj)

    def update_trigger_system(self, player_obj):
        """🎯 트리거 박스를 순회하며 조건 충족 시 액션을 동적 실행하는 코어 루프"""
        import importlib
        
        for box in self.trigger_boxes:
            # 이미 실행 완료된 단발성 트리거는 연산 스킵
            if getattr(box, "is_triggered", False):
                continue
                
            try:
                # 🔴 1. 트리거 조건 파일 동적 로드 및 검사 (예: src/event_system/triggers/enemy_clear.py)
                trigger_mod = importlib.import_module(f"event_system.triggers.{box.trigger_module_name}")
                
                # 조건식에 플레이어 정보와 맵 안의 전체 엔티티 리스트를 넘겨 유연성 확보
                if hasattr(trigger_mod, "condition_check") and trigger_mod.condition_check(box.rect, player_obj, self.entities):
                    
                    # 🔵 2. 조건이 True라면 매핑된 액션 파일 동적 로드 및 즉시 실행 (예: src/event_system/actions/play_dialogue.py)
                    action_mod = importlib.import_module(f"event_system.actions.{box.action_module_name}")
                    if hasattr(action_mod, "execute"):
                        action_mod.execute(player_obj, self.entities)
                    
                    # 🔒 3. 단발성 잠금 장치 활성화 (다시 실행되지 않도록)
                    box.is_triggered = True
                    
            except ModuleNotFoundError as e:
                print(f"⚠️ [TriggerSystem] 모듈 로드 실패: {e}")
            except Exception as e:
                print(f"⚠️ [TriggerSystem] 트리거 처리 중 예외 발생: {e}")

    def draw(self, screen, camera_offset=(0, 0)):
        """Z-Index Layer System 기반 계층형 렌더링"""
        cam_x, cam_y = camera_offset
        viewport_w = screen.get_width()
        viewport_h = screen.get_height()

        # Layer 0: 🌌 backdrop (2D 무한 시차 원경)
        backdrop_scroll_x = cam_x * self.backdrop_parallax_factor_x
        backdrop_scroll_y = cam_y * self.backdrop_parallax_factor_y
        self._draw_2d_tiled(screen, self.backdrop, backdrop_scroll_x, backdrop_scroll_y, viewport_w, viewport_h)

        # Layer 1: 🌿 background (지면 밀착 X축 패럴랙스 근경)
        ground_y = float(self.ground_y)
        bg_h = float(self.background.get_height())
        bg_screen_y = ground_y - bg_h - cam_y
        bg_scroll_x = cam_x * settings.BACKGROUND_X_RATIO
        self._draw_x_tiled(screen, self.background, bg_scroll_x, bg_screen_y, viewport_w)

        # Ground Tiles (기본 지형 레이어)
        ground_w = self.ground_image.get_width()
        pad_x = float(getattr(settings, "MAP_PADDING_X", 800.0))
        min_x = -pad_x
        max_x = self.width + pad_x
        start_x = int(math.floor(min_x / ground_w) * ground_w)
        end_x = int(math.ceil(max_x / ground_w) * ground_w)
        for x_pos in range(start_x, end_x, ground_w):
            screen.blit(self.ground_image, (x_pos - cam_x, ground_y - cam_y))

        # Layer 2 & 3: Z-Index 정렬을 통한 발판 플랫폼 및 엔티티 일괄 렌더링
        drawables = []
        for platform in self.platforms:
            if hasattr(platform, "draw"):
                z = getattr(platform, "z_index", 2)
                drawables.append((z, platform))

        for entity in self.entities:
            if hasattr(entity, "draw"):
                z = getattr(entity, "z_index", 3)
                drawables.append((z, entity))

        # Z-Index 순차 정렬
        drawables.sort(key=lambda x: x[0])
        for z, obj in drawables:
            obj.draw(screen, camera_offset=camera_offset)

    def _draw_x_tiled(self, screen, surface, scroll_x, screen_y, viewport_w):
        img_w = surface.get_width()
        if img_w <= 0:
            return
        tile_offset_x = scroll_x % img_w
        start_x = -tile_offset_x
        tiles_needed = math.ceil((viewport_w + tile_offset_x) / img_w) + 1
        for i in range(tiles_needed):
            screen.blit(surface, (start_x + i * img_w, screen_y))

    def _draw_2d_tiled(self, screen, surface, scroll_x, scroll_y, viewport_w, viewport_h):
        img_w = surface.get_width()
        img_h = surface.get_height()
        if img_w <= 0 or img_h <= 0:
            return
        tile_offset_x = float(scroll_x) % img_w
        tile_offset_y = float(scroll_y) % img_h
        start_x = -tile_offset_x
        start_y = -tile_offset_y
        tiles_needed_x = math.ceil((viewport_w + tile_offset_x) / img_w) + 1
        tiles_needed_y = math.ceil((viewport_h + tile_offset_y) / img_h) + 1
        for i in range(tiles_needed_x):
            for j in range(tiles_needed_y):
                screen.blit(surface, (start_x + i * img_w, start_y + j * img_h))
```

--------------------------------------------------

### 📄 extraction_target_project/map_system/map_main.py
#### 🧱 Code Skeleton:
```python
class GameMap:
    def __init__(self, map_id):
        self.map_id = map_id
        self.trigger_boxes = []
        self.entities = []            # 엔티티 컨테이너 보장
        self.platforms = []
        self.structures = []
        self.objects = []
        
        # 🎯 [누락 복구] 액션 핸들러 및 패럴랙스 렌더링 스펙 프로토콜 무결성 선행 선언
        self.action_handlers = {}
        self.safe_margin = 200        # 화면 경계 노출 차단용 safe_margin 기본값 셋업
        
        # 패럴랙스 스크롤 계수 안전망 초기화 보장
        self.backdrop_parallax_factor_x = 0.2
        self.backdrop_parallax_factor_y = 0.1
        self.background_parallax_factor_x = 0.5
        self.background_parallax_factor_y = 0.3
        
        # 맵 데이터 파싱 및 빌드 진행
        self.load_map_from_json()
        
        # 에셋 및 배경 이미지 레이어 가동
        self.load_map_assets()
        self.build_map()

    def load_map_from_json(self):
        """🌟 maps 폴더 안의 json 파일을 읽어 맵 데이터를 세팅합니다."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        if isinstance(self.map_id, int) or (isinstance(self.map_id, str) and self.map_id.isdigit()):
            file_name = f"map_{self.map_id}.json"
        else:
            file_name = f"map_{self.map_id}.json" if not str(self.map_id).startswith("map_") else f"{self.map_id}.json"
            
        json_path = os.path.normpath(os.path.join(current_dir, "maps", file_name))
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if "map_data" in data:
                map_inner_data = data["map_data"]
                settings_data = map_inner_data.get("settings", {})
            else:
                map_inner_data = data
                settings_data = {
                    "width": data.get("map_width"),
                    "height": data.get("map_height"),
                    "background_type": data.get("background_type"),
                    "ground_type": data.get("ground_type"),
                    "ground_y": data.get("ground_y"),
                }
            
            settings_data["map_id"] = data.get("map_id", self.map_id)
            
            self.vars = MapVariables(settings_data)
            self.width = self.vars.width
            self.height = self.vars.height
            
            height_val = settings_data.get("height") or settings_data.get("map_height")
            self.ground_y = float(height_val) if height_val is not None else 600.0
            self.vars.ground_y = self.ground_y
            
            self.background_type = self.vars.background_type
            self.ground_type = self.vars.ground_type
            self.raw_platforms = map_inner_data.get("platforms", [])
            self.raw_structures = map_inner_data.get("structures", [])
            self.raw_objects = map_inner_data.get("objects", [])
            self.raw_entities = map_inner_data.get("entities", [])
            self.raw_triggers = map_inner_data.get("triggers", [])
            
            if "trigger_boxes" in map_inner_data:
                for tb_data in map_inner_data["trigger_boxes"]:
                     box = TriggerBoxInstance(
                         x=tb_data["x"], y=tb_data["y"],
                         width=tb_data["width"], height=tb_data["height"],
                         trigger_module=tb_data["trigger_module"],
                         action_module=tb_data["action_module"]
                     )
                     self.trigger_boxes.append(box)

            # JSON 데이터 기반 실체화 파이프라인
            if isinstance(self.entities, list):
                for e_data in self.raw_entities:
                    e_type = e_data.get("type") or e_data.get("entity_type")
                    e_x = e_data.get("x", 0)
                    e_y = e_data.get("y", 0)
                    if e_type:
                        obj = EntityRegistry.create(e_type, x=e_x, y=e_y)
                        if obj:
                            self.entities.append(obj)
            
        except FileNotFoundError:
            print(f"⚠️ [GameMap] 맵 구성 파일({json_path})이 없어 기본값으로 초기화합니다.")
            self.fallback_default_map()
        except Exception as e:
            print(f"\n❌ 에러: 맵 데이터 파일({json_path}) 로드 중 에러 발생: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def register_action_handler(self, action_type, handler_callback):
        """이벤트 액션을 처리할 핸들러를 등록합니다."""
        self.action_handlers[action_type] = handler_callback

    def load_map_assets(self):
        """맵에 필요한 이미지 에셋을 로드합니다. (지형 타일, backdrop, background)"""
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bg_dir   = os.path.join(src_dir, "assets", "images", "map", "background")
        ground_dir = os.path.join(src_dir, "assets", "images", "map", "ground")
        test_bg_dir = os.path.join(bg_dir, "test_map")

        try:
            self.bg_image = pygame.image.load(
                os.path.join(bg_dir, f"{self.vars.background_type}.png")
            ).convert_alpha()
            self.ground_image = pygame.image.load(
                os.path.join(ground_dir, f"{self.vars.ground_type}.png")
            ).convert_alpha()
        except Exception as e:
            print(f"⚠️ [경고] 기본 타일 로드 실패 → 단색 대체 패치 가동 ({e})")
            self.bg_image = pygame.Surface((40, 40))
            self.bg_image.fill((30, 30, 40))
            self.ground_image = pygame.Surface((40, 40))
            self.ground_image.fill((80, 120, 60))

        import settings
        try:
            loaded_backdrop = pygame.image.load(os.path.join(test_bg_dir, "backdrop.jpg")).convert()
        except Exception as e:
            loaded_backdrop = pygame.Surface((1600, 1200))
            loaded_backdrop.fill((100, 160, 220))

        target_h = settings.VIRTUAL_HEIGHT + self.safe_margin
        orig_w = loaded_backdrop.get_width()
        orig_h = loaded_backdrop.get_height()
        
        scale_ratio = target_h / float(orig_h)
        target_w = int(orig_w * scale_ratio)
        self.backdrop = pygame.transform.scale(loaded_backdrop, (target_w, target_h))

        try:
            self.background = pygame.image.load(os.path.join(test_bg_dir, "background.jpg")).convert()
        except Exception as e:
            self.background = pygame.Surface((1600, 600))
            self.background.fill((80, 140, 200))

    def build_map(self):
        """로드된 파싱 데이터를 바탕으로 실제 물리 플랫폼 객체들을 인스턴스화합니다."""
        self.platforms = []
        self.structures = []
        
        import settings
        total_floor_width = float(self.width) + float(settings.VIRTUAL_WIDTH) + float(self.safe_margin)
        tile_w = self.ground_image.get_width()
        tile_h = self.ground_image.get_height()
        
        tiles_needed = int(math.ceil(total_floor_width / tile_w))
        for i in range(tiles_needed):
            x = i * tile_w
            pf = Platform(x, self.ground_y, tile_w, tile_h)
            pf.is_ground = True  
            self.platforms.append(pf)
            
        # 1. 일반 플랫폼 복원 파트 수정
        for p_data in self.raw_platforms:
            pf = Platform(
                x=p_data.get("x"),
                y=p_data.get("y"),
                width=p_data.get("width"),
                height=p_data.get("height"),
                is_visible=bool(p_data.get("is_visible", True)),
                platform_type=str(p_data.get("platform_type", "SOLID"))  # 정적 파라미터 매핑 확보
            )
            self.platforms.append(pf)

        # 🧱 structures/objects 리스트 데이터 로드 무결성 확보
        raw_structs = []
        if hasattr(self, "raw_structures") and self.raw_structures:
            raw_structs.extend(self.raw_structures)
        if hasattr(self, "raw_objects") and self.raw_objects:
            raw_structs.extend(self.raw_objects)

        for s_data in raw_structs:
            try:
                if not isinstance(s_data, dict):
                    continue
                x = float(s_data.get("x", 0.0))
                y = float(s_data.get("y", 0.0))
                width = float(s_data.get("width", 240.0))
                height = float(s_data.get("height", 40.0))
                
                # 구조물 내 platform_type 키 매핑 (하위 호환을 위해 "type" 스펙도 フォールバック 처리)
                p_type = s_data.get("platform_type", s_data.get("type", "SOLID"))
                if p_type == "platform":  # 레거시 명칭 예외 처리
                    p_type = "SOLID"

                pf = Platform(
                    x=x,
                    y=y,
                    width=int(width),
                    height=int(height),
                    is_visible=bool(s_data.get("is_visible", True)),
                    platform_type=str(p_type)  # 초기화 단계에서 확실히 전달
                )
                
                # 추가 데이터 프로토콜 무결성 보존
                pf.type = p_type
                pf.z_index = int(s_data.get("z_index", 2))
                
                self.structures.append(pf)
                self.platforms.append(pf)
            # (앞부분 생략: structures 및 platforms 처리 코드...)
            except Exception as e:
                print(f"⚠️ [GameMap] 구조물 개별 파싱 실패: {e}")

        # 🎯 [수정] 덮어쓰기 버그 제거: load_map_from_json에서 이미 self.entities가 생성되었으므로 재초기화하지 않습니다.
        # 기존의 self.entities = [] 및 raw_entities 순회 루프를 통째로 삭제합니다.

        self.triggers = []
        for t_data in self.raw_triggers:
            bounds = t_data.get("bounds", {})
            action = t_data.get("action", {})
            if bounds and action:
                self.triggers.append({
                    "type": t_data.get("type", "enter_area"),
                    "bounds": pygame.Rect(bounds.get("x", 0), bounds.get("y", 0), bounds.get("width", 50), bounds.get("height", 50)),
                    "action": action,
                    "triggered": t_data.get("triggered", False)
                })

    def register_action_handler(self, action_type, handler_callback):
        self.action_handlers[action_type] = handler_callback

    def execute_trigger_action(self, action):
        action_type = action.get("type")
        if action_type in self.action_handlers:
            self.action_handlers[action_type](action)
            return
        if action_type == "spawn_enemy":
            e_type = action.get("entity_type")
            sx = action.get("spawn_x", 0)
            sy = action.get("spawn_y", 0)
            entity_obj = EntityRegistry.create(e_type, x=sx, y=sy)
            if entity_obj:
                entity_obj.z_index = action.get("z_index", 3)
                self.entities.append(entity_obj)

    def update(self, dt, player_obj):
        """main.py의 호출 규격(dt, player_obj)에 맞춘 맵 전체 요소 실시간 업데이트 프로토콜"""
        
        # 💡 [해결 방안] 파이썬 인터프리터에게 이 함수 내의 pygame은 
        # 로컬 변수가 아니라 모듈 전역(global)에 정의된 pygame임을 명시적으로 알려줍니다.
        global pygame
        import pygame
        
        # 💡 [유동적 해상도 반영] 현재 화면 크기의 1.5배 영역을 활성화 반경으로 실시간 계산
        try:
            import settings
            limit_x = settings.VIRTUAL_WIDTH * 1.5
            limit_y = settings.VIRTUAL_HEIGHT * 1.5
        except Exception:
            # settings 호출이 안 될 경우, 현재 실행 중인 pygame 창 크기 기준으로 자동 우회
            current_surface = pygame.display.get_surface()
            if current_surface:
                screen_w, screen_h = current_surface.get_size()
                limit_x = screen_w * 1.5
                limit_y = screen_h * 1.5
            else:
                limit_x = 1200
                limit_y = 900

        for entity in self.entities:
            # 💡 [최적화 가드] 플레이어 활성화 범위(Activation Box) 내부의 적들만 실시간 업데이트 적용
            if hasattr(player_obj, 'vars') and hasattr(player_obj.vars, 'x'):
                
                # 1단계: 개발자가 지정한 명시적인 적 태그(is_enemy)가 있는지 먼저 확인
                is_enemy = getattr(entity, "is_enemy", None)
                
                # 2단계: 태그가 명시되어 있지 않다면(None), 폴더 경로 및 클래스명으로 자동 판별 (안전망)
                if is_enemy is None:
                    is_enemy = "enemy" in entity.__class__.__module__.lower() or "enemy" in entity.__class__.__name__.lower()
                
                # 최종적으로 적(is_enemy가 True)인 경우에만 거리 계산 및 잠재우기(Skip) 적용
                if is_enemy and hasattr(entity, 'vars') and hasattr(entity.vars, 'x'):
                    px, py = player_obj.vars.x, player_obj.vars.y
                    ex, ey = entity.vars.x, entity.vars.y
                    
                    # 활성화 범위를 벗어난 먼 거리의 적들은 연산을 완전히 스킵(최적화)
                    if abs(ex - px) > limit_x or abs(ey - py) > limit_y:
                        continue

            # ----------------------------------------------------
            # 3. 활성화 범위 내에 있는 적들과 일반 오브젝트들은 즉시 업데이트
            # ----------------------------------------------------
            if hasattr(entity, "update_with_dt"):
                try:
                    entity.update_with_dt(player_obj, self.platforms, self, dt)
                except Exception as e:
                    print(f"⚠️ [GameMap] 엔티티 dt 업데이트 중 오류 발생: {e}")
            
            elif hasattr(entity, "update"):
                try:
                    entity.update(player_obj, self.platforms, self)
                except Exception as e:
                    print(f"⚠️ [GameMap] 엔티티 일반 업데이트 중 오류 발생: {e}")
                    
        # 트리거 박스 인스턴스 실시간 업데이트 보장 
        for box in self.trigger_boxes:
            if hasattr(box, "update"):
                try:
                    box.update(dt)
                except Exception as e:
                    print(f"⚠️ [GameMap] 트리거 박스 업데이트 실패: {e}")

        # 실시간 영역 진입형 트리거(Triggers) 검사 로직 무결성 전개
        if hasattr(player_obj, 'vars') and hasattr(player_obj.vars, 'x'):
            p_rect = pygame.Rect(player_obj.vars.x, player_obj.vars.y, 
                                 getattr(player_obj.vars, 'width', 40), 
                                 getattr(player_obj.vars, 'height', 60))
            
            for trigger in self.triggers:
                if not trigger.get("triggered", False):
                    bounds = trigger.get("bounds")
                    if bounds and p_rect.colliderect(bounds):
                        trigger["triggered"] = True
                        action = trigger.get("action", {})
                        a_type = action.get("type")
                        
                        print(f"🎬 [GameMap] 트리거 발동 -> 타입: '{a_type}'")
                        
                        # 대사 트리거 연동 프로토콜
                        if a_type == "start_dialogue":
                            d_id = action.get("dialogue_id")
                            from dialogue_system.dialogue_manager import DialogueManager
                            DialogueManager.get_instance().start_dialogue(d_id)
                        
                        # 핸들러 확장성 대응
                        if a_type in self.action_handlers:
                            try:
                                self.action_handlers[a_type](action)
                            except Exception as e:
                                print(f"⚠️ [GameMap] 액션 핸들러 실행 실패: {e}")

    def draw(self, screen, camera_offset=(0, 0)):
        """배경, 바닥 지형, 공중 플랫폼 지형들을 순서대로 화면에 렌더링합니다."""
        # camera_offset = (카메라 좌측 상단의 월드 X, 월드 Y)
        cam_x, cam_y = camera_offset
        import settings

        # 동적 지면 좌표 self.ground_y 적용
        self.vars.ground_y = self.ground_y

        viewport_w = screen.get_width()    # 가상 스크린 너비
        viewport_h = screen.get_height()   # 가상 스크린 높이

        # ================================================================
        # 🛠️ 내부 헬퍼: X축 전용 Modulo 무한 타일링
        # ----------------------------------------------------------------
        # 설계 원칙
        #   - while 문 / 조건 기반 무한루프 완전 금지
        #   - Y축 타일링 없음 — Y 좌표는 호출자가 확정된 screen_y를 전달
        #
        # [X축 Modulo 스크롤 공식]
        #   ① tile_offset_x = scroll_x % img_w
        #        scroll_x  : 카메라 X 오프셋 × 패럴랙스 비율
        #        결과 범위  : [0, img_w)  ← Python %는 음수 입력에도 항상 양수 반환
        #        의미       : 이번 프레임에서 왼쪽 끝 타일을 화면 좌측 밖으로
        #                     몇 픽셀만큼 밀어낼지
        #
        #   ② start_x = -tile_offset_x
        #        첫 타일의 화면 X 좌표. 항상 화면 왼쪽 바깥(-img_w+1 ~ 0)에서 시작.
        #
        #   ③ tiles_needed = ceil((viewport_w + tile_offset_x) / img_w) + 1
        #        왼쪽으로 최대 img_w-1 픽셀 튀어나온 타일까지 포함해
        #        화면 오른쪽 끝을 빈틈없이 덮을 최소 타일 수 + 여유 1장
        # ================================================================
        def _draw_x_tiled(surface, scroll_x, screen_y):
            """
            surface를 X축으로만 무한 타일링하여 screen에 그립니다.
            """
            img_w = surface.get_width()
            if img_w <= 0:
                return

            tile_offset_x = scroll_x % img_w
            start_x = -tile_offset_x
            tiles_needed = math.ceil((viewport_w + tile_offset_x) / img_w) + 1

            for i in range(tiles_needed):
                screen.blit(surface, (start_x + i * img_w, screen_y))

        def _draw_2d_tiled(surface, scroll_x, scroll_y):
            """
            surface를 X축 및 Y축으로 2차원 무한 타일링하여 screen에 그립니다.
            """
            img_w = surface.get_width()
            img_h = surface.get_height()
            if img_w <= 0 or img_h <= 0:
                return

            # 부호 예외 처리를 포함한 Modulo 연산
            tile_offset_x = float(scroll_x) % img_w
            tile_offset_y = float(scroll_y) % img_h

            # 첫 타일 화면 좌표 (화면 바깥 상단/좌단)
            start_x = -tile_offset_x
            start_y = -tile_offset_y

            # 필요한 타일 수 계산
            tiles_needed_x = math.ceil((viewport_w + tile_offset_x) / img_w) + 1
            tiles_needed_y = math.ceil((viewport_h + tile_offset_y) / img_h) + 1

            for i in range(tiles_needed_x):
                for j in range(tiles_needed_y):
                    screen.blit(surface, (start_x + i * img_w, start_y + j * img_h))

        # ================================================================
        # 🌌 LAYER 1 — backdrop (전역 원경 / 하늘 바탕화면)
        # ================================================================
        # ┌─ Y 좌표 법칙 ────────────────────────────────────────────────┐
        # │  기존 backdrop은 화면 최상단(y = 0)에 고정되었으나,          │
        # │  이제 Y축 무한 시차 스크롤 및 타일링을 완벽하게 수행합니다.  │
        # │  backdrop_scroll_y = cam_y * self.backdrop_parallax_factor_y  │
        # └──────────────────────────────────────────────────────────────┘
        # ┌─ X 좌표 법칙 ────────────────────────────────────────────────┐
        # │  backdrop_scroll_x = cam_x * self.backdrop_parallax_factor_x  │
        # └──────────────────────────────────────────────────────────────┘
        backdrop_scroll_x = cam_x * self.backdrop_parallax_factor_x
        backdrop_scroll_y = cam_y * self.backdrop_parallax_factor_y
        _draw_2d_tiled(self.backdrop, scroll_x=backdrop_scroll_x, scroll_y=backdrop_scroll_y)

        # ================================================================
        # 🌿 LAYER 2 — background (지상 배경 / 도시·빌딩숲)
        # ================================================================
        # ┌─ Y 좌표 법칙 ────────────────────────────────────────────────┐
        # │  이미지의 바닥(Bottom)이 항상 월드의 ground_y에 밀착한다.    │
        # │                                                               │
        # │  [월드 좌표 → 화면 좌표 변환 공식]                           │
        # │   이미지 top의 월드 Y = ground_y - background.get_height()   │
        # │   화면 Y             = 월드 Y - cam_y                        │
        # │                                                               │
        # │   ∴ screen_y = ground_y - background.get_height() - cam_y   │
        # │                                                               │
        # │  backdrop의 screen_y=0 공식과 완전히 독립적.                 │
        # │  backdrop 높이, 다른 이미지 크기 일절 참조하지 않는다.       │
        # └──────────────────────────────────────────────────────────────┘
        # ┌─ X 좌표 법칙 ────────────────────────────────────────────────┐
        # │  scroll_x = cam_x * BACKGROUND_X_RATIO                      │
        # │  → backdrop보다 빠르게 X 타일링하여 원근감 연출.             │
        # └──────────────────────────────────────────────────────────────┘
        ground_y      = float(self.vars.ground_y)
        bg_h          = float(self.background.get_height())
        bg_screen_y   = ground_y - bg_h - cam_y   # 지면 밀착 공식
        bg_scroll_x   = cam_x * settings.BACKGROUND_X_RATIO
        _draw_x_tiled(self.background, scroll_x=bg_scroll_x, screen_y=bg_screen_y)

        # ================================================================
        # 🧱 LAYER 3 — Z-Index 정렬을 통한 플랫폼 및 엔티티 일괄 렌더링
        # ================================================================
        drawables = []
        for platform in self.platforms:
            if hasattr(platform, "draw"):
                z = getattr(platform, "z_index", 2)
                drawables.append((z, platform))
        for entity in self.entities:
            if hasattr(entity, "draw"):
                z = getattr(entity, "z_index", 3)
                drawables.append((z, entity))
        drawables.sort(key=lambda x: x[0])
        for z, obj in drawables:
            obj.draw(screen, camera_offset=camera_offset)

            # 전역 히트박스 디버그 활성화 시 각 엔티티의 디버그 오버레이 순차 커플링 출력
            if getattr(settings, "DEBUG_SHOW_HITBOX", False) and hasattr(obj, "draw_debug_overlay"):
                obj.draw_debug_overlay(screen, camera_offset=camera_offset)

        # ================================================================
        # 🪨 LAYER 4 — 흙바닥 지형 타일
        # ================================================================
        ground_w = self.ground_image.get_width()

        # 카메라 잘림 방지 패딩을 포함한 X 렌더링 범위 계산
        pad_x   = float(getattr(self.vars, "ground_draw_padding_x", settings.MAP_PADDING_X))
        min_x   = -pad_x
        max_x   = self.vars.width + pad_x

        # 타일 크기 단위로 맞아떨어지는 시작/끝 산출
        start_x = int(math.floor(min_x / ground_w) * ground_w)
        end_x   = int(math.ceil(max_x  / ground_w) * ground_w)

        for x_pos in range(start_x, end_x, ground_w):
            screen.blit(self.ground_image, (x_pos - cam_x, ground_y - cam_y))

    def update_trigger_system(self, player_obj):
        """🎯 트리거 박스를 순회하며 조건 충족 시 액션을 동적 실행하는 코어 루프"""
        import importlib
        
        for box in self.trigger_boxes:
            if getattr(box, "is_triggered", False):
                continue
                
            try:
                trigger_mod = importlib.import_module(f"event_system.triggers.{box.trigger_module_name}")
                if hasattr(trigger_mod, "condition_check") and trigger_mod.condition_check(box.rect, player_obj, self.entities):
                    action_mod = importlib.import_module(f"event_system.actions.{box.action_module_name}")
                    if hasattr(action_mod, "execute"):
                        action_mod.execute(player_obj, self.entities)
                    box.is_triggered = True
            except ModuleNotFoundError as e:
                print(f"⚠️ [TriggerSystem] 모듈 로드 실패: {e}")
            except Exception as e:
                print(f"⚠️ [TriggerSystem] 트리거 처리 중 예외 발생: {e}")

    def fallback_default_map(self):
        """안전장치: 예외 발생 시 게임 크래시를 방지하기 위한 디폴트 세팅"""
        import settings
        self.width = settings.VIRTUAL_WIDTH
        self.height = settings.VIRTUAL_HEIGHT
        self.background_type = "bg_sky"
        self.ground_type = "ground_dirt"
        self.ground_y = settings.GROUND_Y
        
        settings_data = {
            "width": self.width,
            "height": self.height,
            "background_type": self.background_type,
            "ground_type": self.ground_type,
            "ground_y": self.ground_y,
            "map_id": self.map_id
        }
        self.vars = MapVariables(settings_data)
        self.raw_platforms = []
        self.raw_structures = []
        self.raw_objects = []
        self.raw_entities = []
        self.raw_triggers = []

    def add_platform(self, x, y, width, height, is_visible=True, can_pass_through=False, platform_type="SOLID"):
        """플랫폼 추가 인터페이스 (3종 분기 및 동적 크기 완벽 수용 조치)"""
        from map_system.map_engine import EntityRegistry
        
        # 1차 분기: 동적 레지스트리 팩토리 호출 시 platform_type 인자 주입
        platform_obj = EntityRegistry.create(
            "platform",
            x=x,
            y=y,
            width=width,
            height=height,
            is_visible=is_visible,
            can_pass_through=can_pass_through,
            platform_type=platform_type
        )
        
        # 2차 분기: Fallback 기본 클래스 생성 처리
        if not platform_obj:
            from platform_system.platform_main import Platform
            platform_obj = Platform(
                x=x,
                y=y,
                width=width,
                height=height,
                is_visible=is_visible,
                can_pass_through=can_pass_through,
                platform_type=platform_type
            )
            
        if platform_obj:
            platform_obj.type = "platform"
            platform_obj.z_index = 2
            
            # 동적 크기에 따른 Pygame Rect 갱신 무결성 확보 확인
            if hasattr(platform_obj, 'image') and platform_obj.image:
                # 텍스처 리사이징이 필요한 아키텍처일 경우 스케일 자동 매칭
                platform_obj.image = pygame.transform.scale(platform_obj.image, (width, height))
            
            self.platforms.append(platform_obj)
            if not hasattr(self, "structures"):
                self.structures = []
            self.structures.append(platform_obj)
            return platform_obj
        return None

    def add_trigger_box(self, x, y, width, height, trigger_module, action_module):
        """트리거 박스 추가 인터페이스 (에디터 연동 대응)"""
        if not hasattr(self, "trigger_boxes"):
            self.trigger_boxes = []
        for box in self.trigger_boxes:
            if box.rect.x == x and box.rect.y == y:
                return False
        from map_system.map_engine import TriggerBoxInstance
        new_box = TriggerBoxInstance(x, y, width, height, trigger_module, action_module)
        self.trigger_boxes.append(new_box)
        return True

    def remove_at_position(self, x, y):
        """오브젝트 제거 인터페이스 (에디터 연동 대응)"""
        self.platforms = [p for p in self.platforms if not (hasattr(p, "vars") and p.vars.x == x and p.vars.y == y)]
        if hasattr(self, "structures"):
            self.structures = [s for s in self.structures if not (hasattr(s, "vars") and s.vars.x == x and s.vars.y == y)]
        if hasattr(self, "trigger_boxes"):
            self.trigger_boxes = [box for box in self.trigger_boxes if not box.rect.collidepoint(x, y)]

    def _infer_entity_type(self, entity):
        if entity.__class__.__name__ == "DummyEnemy":
            return "dummy"
        return entity.__class__.__name__.lower()

    def save_map(self, map_name):
        """맵 데이터를 JSON 포맷으로 세이브하는 직렬화 메소드"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        maps_dir = os.path.join(current_dir, "maps")
        os.makedirs(maps_dir, exist_ok=True)
        
        if isinstance(map_name, int) or (isinstance(map_name, str) and map_name.isdigit()):
            file_name = f"map_{map_name}.json"
        else:
            file_name = f"map_{map_name}.json" if not str(map_name).startswith("map_") else f"{map_name}.json"
            
        save_path = os.path.join(maps_dir, file_name)
        temp_path = f"{save_path}.tmp"
        
        if not hasattr(self, "structures"):
            self.structures = []
        if not hasattr(self, "trigger_boxes"):
            self.trigger_boxes = []
            
        data = {
            "schema_version": 2,
            "map_id": self.map_id,
            "map_width": self.width,
            "map_height": self.height,
            "background_type": self.background_type,
            "ground_type": self.ground_type,
            "ground_y": self.ground_y,
            "platforms": [
                {
                    "type": getattr(p, "type", "platform"),
                    "x": int(p.vars.x),
                    "y": int(p.vars.y),
                    "width": int(p.vars.width),
                    "height": int(p.vars.height),
                    "is_visible": bool(p.vars.is_visible),
                    "can_pass_through": bool(getattr(p.vars, "passable_from_bottom", False) or getattr(p.vars, "can_pass_through", False)),
                    "z_index": int(getattr(p, "z_index", 2)),
                }
                for p in self.platforms if p not in self.structures and not getattr(p, "is_ground", False)
            ],
            "structures": [
                {
                    "type": getattr(s, "type", "platform"),
                    "x": int(s.vars.x),
                    "y": int(s.vars.y),
                    "width": int(s.vars.width),
                    "height": int(s.vars.height),
                    "is_visible": bool(s.vars.is_visible),
                    "can_pass_through": bool(getattr(s.vars, "passable_from_bottom", False) or getattr(s.vars, "can_pass_through", False)),
                    "z_index": int(getattr(s, "z_index", 2)),
                }
                for s in self.structures
            ],
            "entities": [
                {
                    "type": self._infer_entity_type(e),
                    "x": int(getattr(e.vars, "x", 0)),
                    "y": int(getattr(e.vars, "y", 0)),
                    "z_index": int(getattr(e, "z_index", 3)),
                }
                for e in self.entities
            ],
            "triggers": [
                {
                    "type": t.get("type", "enter_area"),
                    "bounds": {
                        "x": t.get("bounds").x,
                        "y": t.get("bounds").y,
                        "width": t.get("bounds").width,
                        "height": t.get("bounds").height,
                    },
                    "action": t.get("action", {}),
                    "triggered": bool(t.get("triggered", False)),
                }
                for t in self.triggers
            ],
            "trigger_boxes": [
                {
                    "x": int(box.rect.x),
                    "y": int(box.rect.y),
                    "width": int(box.rect.width),
                    "height": int(box.rect.height),
                    "trigger_module": box.trigger_module_name,
                    "action_module": box.action_module_name
                }
                for box in self.trigger_boxes
            ]
        }
        
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
            os.replace(temp_path, save_path)
            return True
        except OSError:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            return False

    def load_map(self, map_name):
        """맵 데이터를 파일에서 재로드하여 연동"""
        self.map_id = map_name
        self.load_map_from_json()
        self.build_map()
```

--------------------------------------------------

### 📄 extraction_target_project/map_system/map_settings.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/map_system/maps/map_1.json
#### 🧱 Code Skeleton:
```python
📦 [JSON STRUCTURE MAP]
  ├── "schema_version": int (val: 2)
  ├── "map_id": str (val: 1)
  ├── "map_width": int (val: 3200)
  ├── "map_height": int (val: 1800)
  ├── "background_type": str (val: bg_sky)
  ├── "ground_type": str (val: ground_dirt)
  ├── "ground_y": float (val: 1800.0)
  ├── "platforms": List (len: 0)
  ├── "structures": List (len: 4)
  ├── "entities": List (len: 10)
  ├── "triggers": List (len: 0)
  ├── "editor_metadata": Dict (keys: ['source_map', 'file_name', 'object_registry']...)
```

--------------------------------------------------

### 📄 extraction_target_project/map_system/maps/map_editor_draft.json
#### 🧱 Code Skeleton:
```python
📦 [JSON STRUCTURE MAP]
  ├── "schema_version": int (val: 2)
  ├── "map_id": str (val: editor_draft)
  ├── "map_width": int (val: 2400)
  ├── "map_height": int (val: 1200)
  ├── "background_type": str (val: bg_sky)
  ├── "ground_type": str (val: ground_dirt)
  ├── "ground_y": float (val: 1200.0)
  ├── "platforms": List (len: 0)
  ├── "structures": List (len: 8)
  ├── "entities": List (len: 2)
  ├── "triggers": List (len: 1)
  ├── "editor_metadata": Dict (keys: ['source_map', 'file_name', 'object_registry']...)
```

--------------------------------------------------

### 📄 extraction_target_project/map_system/maps/map_stage1.json
#### 🧱 Code Skeleton:
```python
📦 [JSON STRUCTURE MAP]
  ├── "schema_version": int (val: 2)
  ├── "map_id": str (val: stage1)
  ├── "map_width": int (val: 2400)
  ├── "map_height": int (val: 1200)
  ├── "background_type": str (val: bg_sky)
  ├── "ground_type": str (val: ground_dirt)
  ├── "ground_y": float (val: 1200.0)
  ├── "platforms": List (len: 0)
  ├── "structures": List (len: 0)
  ├── "entities": List (len: 0)
  ├── "triggers": List (len: 1)
  ├── "editor_metadata": Dict (keys: ['source_map', 'file_name', 'object_registry']...)
```

--------------------------------------------------

### 📄 extraction_target_project/map_system/variables.py
#### 🧱 Code Skeleton:
```python
class MapVariables:
    def __init__(self, map_id=1, width=None, height=None):
        """
        맵 전체 크기에 맞춰 배경과 바닥 이미지를 
        몇 개나 이어 붙여야 하는지 계산하고 저장하는 설계도
        """
        if isinstance(map_id, dict):
            settings_dict = map_id
            self.map_id = settings_dict.get("map_id", 1)
            self.width = settings_dict.get("width") or settings_dict.get("map_width") or DEFAULT_MAP_WIDTH
            self.height = settings_dict.get("height") or settings_dict.get("map_height") or DEFAULT_MAP_HEIGHT
            self.background_type = settings_dict.get("background_type") or DEFAULT_BACKGROUND_TYPE
            self.ground_type = settings_dict.get("ground_type") or DEFAULT_GROUND_TYPE
            self.ground_y = settings_dict.get("ground_y") or DEFAULT_GROUND_Y
        else:
            self.map_id = map_id
            self.width = width if width is not None else DEFAULT_MAP_WIDTH
            self.height = height if height is not None else DEFAULT_MAP_HEIGHT
            self.background_type = DEFAULT_BACKGROUND_TYPE
            self.ground_type = DEFAULT_GROUND_TYPE
            self.ground_y = DEFAULT_GROUND_Y

        # 1. 🖼️ 배경 데이터 및 이어 붙일 개수 계산
        self.bg_width = DEFAULT_BG_WIDTH
        self.bg_height = DEFAULT_BG_HEIGHT
        # 맵 전체를 채우기 위해 가로로 몇 장을 이어 붙여야 하는지 계산 (올림 처리)
        self.bg_repeat_count = math.ceil(self.width / self.bg_width) # 1600 / 800 = 2장
        
        # 2. 🪵 바닥 데이터 및 이어 붙일 개수 계산
        self.ground_tile_width = DEFAULT_GROUND_TILE_WIDTH
        self.ground_tile_height = DEFAULT_GROUND_TILE_HEIGHT

        # ============================================================
        # 🗺️ 카메라 잘림 방지를 위한 좌우 패딩값(월드 좌표 기준)
        # - 카메라가 맵 끝으로 이동할 때 화면의 양쪽이 비지 않도록
        #   바닥 타일을 더 넓게 그립니다.
        # - 값은 settings.py에서 관리합니다(하드코딩 금지).
        self.ground_draw_padding_x = float(getattr(settings, "MAP_PADDING_X", 0.0))
        # 맵 끝까지 바닥 타일을 몇 개나 도장 찍어야 하는지 계산
        self.ground_repeat_count = math.ceil(self.width / self.ground_tile_width) # 1600 / 64 = 25개
        
        # 3. 🧱 구조물 리스트 (기존 유지)
        self.platform_data_list = []
        self.trap_data_list = []
```

--------------------------------------------------

### 📄 extraction_target_project/platform_system/__init__.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/platform_system/platform_main.py
#### 🧱 Code Skeleton:
```python
class Platform:
    def __init__(self, x, y, width=200, height=30, **kwargs):
        self.vars = PlatformVariables(x, y, width, height, **kwargs)
        self.load_image()

    def load_image(self):
        # 🌟 현재 파일(src/platform_system/platform_main.py) 위치 기준 상위 src/ 폴더 추적
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        img_dir = os.path.join(src_dir, "assets", "images", "platform")
        
        try:
            self.image = pygame.image.load(os.path.join(img_dir, "platform_brick.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.vars.width, self.vars.height))
        except pygame.error as e:
            print(f"\n❌ 에러: 플랫폼 이미지를 로드할 수 없습니다. ({e})")
            print(f"참조 실패한 디렉터리: {img_dir}")
            pygame.quit()
            sys.exit()

    def update(self):
        pass

    def draw(self, screen, camera_offset=(0, 0)):
        """🌟 플랫폼이 보임 처리되어 있다면 화면에 그립니다."""
        if self.vars.is_visible:
            ox, oy = camera_offset
            screen.blit(self.image, (self.vars.x - ox, self.vars.y - oy))
```

--------------------------------------------------

### 📄 extraction_target_project/platform_system/platform_settings.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/platform_system/variables.py
#### 🧱 Code Skeleton:
```python
class PlatformVariables:
    def __init__(self, x, y, 
                 width=DEFAULT_PLATFORM_WIDTH, 
                 height=DEFAULT_PLATFORM_HEIGHT, 
                 is_solid=DEFAULT_IS_SOLID, 
                 is_visible=DEFAULT_IS_VISIBLE, 
                 passable_from_bottom=DEFAULT_PASSABLE_FROM_BOTTOM, 
                 platform_type="SOLID",  # SOLID, ONE_WAY, GHOST 기본값 세팅
                 **kwargs):
        """
        플랫폼의 속성들을 관리하는 데이터 클래스 (무결성 및 확장 규칙 준수)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_visible = is_visible                 
        
        # 가변 인자 매핑 유연성 확보
        if "platform_type" in kwargs:
            self.platform_type = kwargs["platform_type"]
        else:
            self.platform_type = platform_type

        # 플랫폼 타입 기반 판정 규칙 바인딩
        if self.platform_type == "SOLID":
            self.is_solid = True
            self.passable_from_bottom = False
        elif self.platform_type == "ONE_WAY":
            self.is_solid = True
            self.passable_from_bottom = True  # 하단 및 측면 통과 판정 활성화
        elif self.platform_type == "GHOST":
            self.is_solid = False
            self.passable_from_bottom = True  # 완전 전방향 통과 판정
            
        self.velocity_x = DEFAULT_PLATFORM_SPEED_X
        self.velocity_y = DEFAULT_PLATFORM_SPEED_Y
```

--------------------------------------------------

### 📄 extraction_target_project/player/__init__.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/player/asset_loader.py
#### 🧱 Code Skeleton:
```python
class PlayerAssetLoader:
    def __init__(self, vars_obj):
        self.images = {}
        self.effect_images = {}
        self.load_all_assets(vars_obj)

    def load_all_assets(self, vars_obj):
        # 🌟 현재 파일(src/player/asset_loader.py) 위치 기준 상위의 src/ 폴더 절대 경로 추출
        src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 정확히 src/assets/images/player 경로 조립
        base_dir = os.path.join(src_dir, "assets", "images", "player")
        move_dir = os.path.join(base_dir, "player_move")
        effect_dir = os.path.join(base_dir, "attack_effect")
        
        try:
            # 🎬 1. 캐릭터 모션 이미지 로드 (여러 장의 프레임을 리스트로 바인딩)
            self.images = {
                # 대기: 1 -> 2 -> 3
                "IDLE": self._load_series(move_dir, ["player_stand1.png", "player_stand2.png", "player_stand3.png"], vars_obj.width, vars_obj.height),
                
                # 이동/달리기: 1 -> 2 -> 3 (동일한 3장 애니메이션 시퀀스 공유)
                "WALK": self._load_series(move_dir, ["player_run1.png", "player_run2.png", "player_run3.png"], vars_obj.width, vars_obj.height),
                "RUN": self._load_series(move_dir, ["player_run1.png", "player_run2.png", "player_run3.png"], vars_obj.width, vars_obj.height),
                
                # 점프 시작 찰나 (W 누른 순간)
                "READY_JUMP": self._load_series(move_dir, ["player_readyjump.png"], vars_obj.width, vars_obj.height),
                
                # 공중 체공 전체 (상승/하강 전체 루프): 1 -> 2 -> 3
                "JUMP_UP": self._load_series(move_dir, ["player_jump1.png", "player_jump2.png", "player_jump3.png"], vars_obj.width, vars_obj.height),
                "FALL": self._load_series(move_dir, ["player_jump1.png", "player_jump2.png", "player_jump3.png"], vars_obj.width, vars_obj.height),
                
                # ⚔️ 기존 공격 모션 (애니메이션 연동 전까지 첫 번째 프레임으로 안전 유지)
                "ATTACK_1": self._load_series(move_dir, ["player_stand1.png"], vars_obj.width, vars_obj.height),
                "ATTACK_2": self._load_series(move_dir, ["player_stand1.png"], vars_obj.width, vars_obj.height),
                "ATTACK_3": self._load_series(move_dir, ["player_stand1.png"], vars_obj.width, vars_obj.height)
            }

            # 🧱 2. 공격 콤보 이펙트 이미지 로드
            self.effect_images = {
                1: pygame.image.load(os.path.join(effect_dir, "effect_hit1.png")).convert_alpha(),
                2: pygame.image.load(os.path.join(effect_dir, "effect_hit2.png")).convert_alpha(),
                3: pygame.image.load(os.path.join(effect_dir, "effect_hit3.png")).convert_alpha()
            }
            # 원본과 완벽히 동일하게 이펙트 규격 자동화 (플레이어 너비의 2배 스케일링)
            for step in self.effect_images:
                self.effect_images[step] = pygame.transform.scale(
                    self.effect_images[step], (vars_obj.width * 2, vars_obj.height)
                )

        except pygame.error as e:
            print(f"\n❌ 에러: 플레이어 또는 이펙트 에셋 로드 실패! ({e})")
            print(f"참조 실패한 디렉터리: {base_dir}")
            pygame.quit()
            sys.exit()

    def _load_series(self, directory, file_list, target_w, target_h):
        """지정된 디렉토리의 파일들을 순서대로 읽어와 크기를 가공한 뒤 리스트로 반환합니다."""
        series = []
        for file_name in file_list:
            full_path = os.path.join(directory, file_name)
            img = pygame.image.load(full_path).convert_alpha()
            img = pygame.transform.scale(img, (target_w, target_h))
            series.append(img)
        return series
```

--------------------------------------------------

### 📄 extraction_target_project/player/combat_processor.py
#### 🧱 Code Skeleton:
```python
def _obb_vs_aabb_collide(cx, cy, half_len, half_wid, dir_x, dir_y, ax, ay, aw, ah):
    """
    돌진 궤적 기반 OBB(중심 cx,cy / 장축 half_len / 단축 half_wid / 방향 dir_x,dir_y)와
    적 히트박스 AABB(ax,ay,aw,ah) 간의 SAT(분리축 정리) 충돌 판정.
    """
    a_half_w = aw * 0.5
    a_half_h = ah * 0.5
    a_cx = ax + a_half_w
    a_cy = ay + a_half_h

    tx = a_cx - cx
    ty = a_cy - cy

    perp_x = -dir_y
    perp_y = dir_x

    # [축 1] OBB 장축
    proj_len = tx * dir_x + ty * dir_y
    r_aabb_on_dir = a_half_w * abs(dir_x) + a_half_h * abs(dir_y)
    if abs(proj_len) > half_len + r_aabb_on_dir:
        return False

    # [축 2] OBB 단축
    proj_wid = tx * perp_x + ty * perp_y
    r_aabb_on_perp = a_half_w * abs(perp_x) + a_half_h * abs(perp_y)
    if abs(proj_wid) > half_wid + r_aabb_on_perp:
        return False

    # [축 3] 월드 X축
    r_obb_on_x = half_len * abs(dir_x) + half_wid * abs(perp_x)
    if abs(tx) > a_half_w + r_obb_on_x:
        return False

    # [축 4] 월드 Y축
    r_obb_on_y = half_len * abs(dir_y) + half_wid * abs(perp_y)
    if abs(ty) > a_half_h + r_obb_on_y:
        return False

    return True

class PlayerCombatProcessor:
    def __init__(self):
        pass

    def process(self, vars_obj, entities=None, dt=0.0):
        # 가변 프레임 환경에 대응하기 위한 프레임 스케일러 보정값 계산
        fps_scale = dt * 60.0

        # 안전장치: 변수 객체에 쿨타임 필드가 없을 경우 동적 확보
        if not hasattr(vars_obj, 'attack_cooldown_timer'):
            vars_obj.attack_cooldown_timer = 0.0

        # 1. 공격 불가(쿨타임) 실시간 감쇄 연산
        if vars_obj.attack_cooldown_timer > 0.0:
            vars_obj.attack_cooldown_timer -= dt
            if vars_obj.attack_cooldown_timer < 0.0:
                vars_obj.attack_cooldown_timer = 0.0

# 2. 새로운 공격 모션 프레임 개시 시점 (트리거)
        if vars_obj.is_attacking and getattr(vars_obj, 'attack_timer', 0) == 0:
            if not hasattr(vars_obj, 'attack_mode'):
                vars_obj.attack_mode = "NORMAL"

            # 디버그용 Before 상태 백업
            if DEBUG:
                before_mode = vars_obj.attack_mode
                before_x = getattr(vars_obj, 'x', 0)
                before_y = getattr(vars_obj, 'y', 0)

            # 📐 [OBB 축 A점] 돌진/공격 개시 원점 박제
            vars_obj.attack_start_x = vars_obj.x
            vars_obj.attack_start_y = vars_obj.y
            vars_obj.has_hit_enemy = False

            # 타겟팅 공통 변수 상위 스코프 초기화
            target_enemy = None
            max_target_distance = vars_obj.attack_range_width * 2.0
            min_dist_sq = max_target_distance * max_target_distance

            # -------------------------------------------------------------
            # [A 트랙] 좌클릭 일반 제자리 콤보 공격 초기화
            # -------------------------------------------------------------
            if vars_obj.attack_mode == "NORMAL":
                if not hasattr(vars_obj, 'combo_step') or vars_obj.combo_step == 0:
                    vars_obj.combo_step = 1
                
                # 타수별 프레임 차등 제어
                vars_obj.attack_timer = 12 if vars_obj.combo_step in [1, 2] else 18
                vars_obj.target_enemy = None

            # -------------------------------------------------------------
            # [B 트랙] 우클릭 신규 대쉬 공격 초기화
            # -------------------------------------------------------------
            elif vars_obj.attack_mode == "DASH":
                vars_obj.attack_timer = 12
                dash_speed = 20.0

                # 🎯 대쉬 트랙 내 독립 레이더 가동 (공격 범위 2배 탐색)
                target_enemy = None
                max_target_distance = vars_obj.attack_range_width * 2.0
                min_dist_sq = max_target_distance * max_target_distance

                if entities:
                    for entity in entities:
                        if entity is self or getattr(entity, 'vars', None) is vars_obj:
                            continue
                        e_vars = getattr(entity, 'vars', None)
                        if not e_vars or getattr(e_vars, 'is_dead', False):
                            continue

                        dx = e_vars.x - vars_obj.x
                        dy = e_vars.y - vars_obj.y
                        dist_sq = dx * dx + dy * dy

                        if dist_sq <= min_dist_sq:
                            min_dist_sq = dist_sq
                            target_enemy = entity

                vars_obj.target_enemy = target_enemy

                # 대쉬 물리 구동 벡터 계산
                if target_enemy:
                    te_vars = target_enemy.vars
                    dx = te_vars.x - vars_obj.x
                    dy = te_vars.y - vars_obj.y
                    dist_sq = dx * dx + dy * dy
                    dist = math.sqrt(dist_sq) if dist_sq > 0 else 1.0

                    vars_obj.facing_right = (dx > 0)
                    y_margin = 25

                    if abs(dy) > y_margin:
                        vars_obj.vx = (dx / dist) * dash_speed
                        vars_obj.vy = (dy / dist) * dash_speed
                    else:
                        vars_obj.vx = dash_speed if vars_obj.facing_right else -dash_speed
                        vars_obj.vy = 0.0
                else:
                    vars_obj.vx = dash_speed if vars_obj.facing_right else -dash_speed
                    vars_obj.vy = 0.0

            # 규격화된 Before-After 디버그 로그 출력 (Lazy Evaluation)
            if DEBUG:
                print(f"[combat_processor.py] process() -> Attack Initialization Changed: Mode={before_mode} -> {vars_obj.attack_mode}, Origin=({before_x}, {before_y}) -> ({vars_obj.attack_start_x}, {vars_obj.attack_start_y}), Timer={vars_obj.attack_timer}")
                print(f"[combat_processor.py] process() -> Attack Initialized: mode={vars_obj.attack_mode}, step={getattr(vars_obj, 'combo_step', 0)}, target={vars_obj.target_enemy}")
        # -------------------------------------------------------------
        # 3. 공격 액션 진행 및 실시간 히트박스 / 피격 판정 루프 (완벽 복원)
        # -------------------------------------------------------------
        if vars_obj.is_attacking:
            # 원본 정수형 타이머 시스템에 맞추어 1프레임씩 감쇄 일관성 유지
            vars_obj.attack_timer -= 1

            # 🛠️ [멈춤 현상 완전 해결 핵심 핵심 영역] 
            # 공격 판정 프레임 후반부(마지막 4프레임) 혹은 후딜레이 진입 직전 상태인 경우,
            # 애니메이션 컨텍스트 유지를 위해 `is_attacking = True` 상태는 그대로 가두어 두되,
            # 사용자의 이동 키 입력 여부에 맞춰 물리 속도 벡터(`vx`)를 사전 개방하여 경직을 파쇄합니다.
            if vars_obj.attack_mode == "NORMAL" and vars_obj.attack_timer <= 4:
                if getattr(vars_obj, 'is_moving', False):
                    target_speed = vars_obj.run_speed if vars_obj.move_state == "RUN" else vars_obj.walk_speed
                    direction = 1 if vars_obj.facing_right else -1
                    vars_obj.vx = target_speed * direction

            # 3-1. 공격 모드 및 콤보 스텝별 히트박스 갱신 생성
            if vars_obj.attack_mode == "DASH":
                # 대쉬 공격은 무조건 이동 궤적 기반 OBB 판정 영역 사용
                start_x = getattr(vars_obj, 'attack_start_x', vars_obj.x)
                start_y = getattr(vars_obj, 'attack_start_y', vars_obj.y)

                start_cx = start_x + vars_obj.width * 0.5
                start_cy = start_y + vars_obj.height * 0.5
                cur_cx = vars_obj.x + vars_obj.width * 0.5
                cur_cy = vars_obj.y + vars_obj.height * 0.5

                seg_dx = cur_cx - start_cx
                seg_dy = cur_cy - start_cy
                seg_len = math.sqrt(seg_dx * seg_dx + seg_dy * seg_dy)

                if seg_len > 0.0001:
                    dir_x = seg_dx / seg_len
                    dir_y = seg_dy / seg_len
                else:
                    dir_x = 1.0 if vars_obj.facing_right else -1.0
                    dir_y = 0.0

                half_len = (seg_len * 0.5) + (vars_obj.attack_range_width * 0.5) + 80
                half_wid = (vars_obj.attack_range_height * 0.5) * 1.5
                obb_cx = (start_cx + cur_cx) * 0.5
                obb_cy = (start_cy + cur_cy) * 0.5

                vars_obj.attack_obb = (obb_cx, obb_cy, half_len, half_wid, dir_x, dir_y)
                vars_obj.attack_rect = pygame.Rect(
                    int(obb_cx - half_len), int(obb_cy - half_wid),
                    int(half_len * 2), int(half_wid * 2)
                )

            elif vars_obj.attack_mode == "NORMAL":
                if vars_obj.combo_step in [1, 2]:
                    # 제자리 일반 공격 1, 2타: 플레이어 중심 기준 전방 지향 OBB 정적 구성
                    dir_x = 1.0 if vars_obj.facing_right else -1.0
                    dir_y = 0.0
                    half_len = vars_obj.attack_range_width * 0.5
                    half_wid = vars_obj.attack_range_height * 0.5
                    
                    # 시선 방향으로 판정 중심 약간 오프셋
                    obb_cx = (vars_obj.x + vars_obj.width * 0.5) + (dir_x * half_len * 0.5)
                    obb_cy = vars_obj.y + vars_obj.height * 0.5

                    vars_obj.attack_obb = (obb_cx, obb_cy, half_len, half_wid, dir_x, dir_y)
                    vars_obj.attack_rect = pygame.Rect(
                        int(obb_cx - half_len), int(obb_cy - half_wid),
                        int(half_len * 2), int(half_wid * 2)
                    )
                else:
                    # 제자리 일반 공격 3타: 몸 중심 기준 확장 사양 고정 AABB 범위 공격
                    attack_w = vars_obj.attack_range_width * 1.6
                    attack_h = vars_obj.attack_range_height * 1.6
                    ax = vars_obj.x - (attack_w - vars_obj.width) * 0.5
                    ay = vars_obj.y - (attack_h - vars_obj.height) * 0.5

                    vars_obj.attack_obb = None
                    vars_obj.attack_rect = pygame.Rect(int(ax), int(ay), int(attack_w), int(attack_h))

            # 3-2. 실시간 피격 감지 및 대미지 인가 세션
            if entities and not vars_obj.has_hit_enemy:
                for entity in entities:
                    if entity is self or getattr(entity, 'vars', None) is vars_obj:
                        continue
                    e_vars = getattr(entity, 'vars', None)
                    if not e_vars or getattr(e_vars, 'is_dead', False) or getattr(e_vars, 'is_hit', False):
                        continue

                    # 충돌 기하 연산 분기
                    if vars_obj.attack_obb is not None:
                        obb_cx, obb_cy, half_len, half_wid, dir_x, dir_y = vars_obj.attack_obb
                        hit = _obb_vs_aabb_collide(
                            obb_cx, obb_cy, half_len, half_wid, dir_x, dir_y,
                            e_vars.x, e_vars.y, e_vars.width, e_vars.height
                        )
                    else:
                        enemy_rect = pygame.Rect(e_vars.x, e_vars.y, e_vars.width, e_vars.height)
                        hit = vars_obj.attack_rect.colliderect(enemy_rect)

                    if hit:
                        vars_obj.has_hit_enemy = True
                        damage = getattr(vars_obj, 'attack_damage', 15)
                        attack_dir = 1 if vars_obj.facing_right else -1

                        # 대미지 및 넉백 계수 판정 처리
                        if vars_obj.attack_mode == "NORMAL" and vars_obj.combo_step == 3:
                            damage = int(damage * 1.5)
                            if hasattr(entity, 'take_damage'):
                                entity.take_damage(damage, knockback_dir=attack_dir * 0.0)
                        else:
                            if hasattr(entity, 'take_damage'):
                                entity.take_damage(damage, knockback_dir=attack_dir * 0.0)

                        if DEBUG:
                            print(f"[combat_processor.py] process() -> Hit Registered: Target={entity}, Damage={damage}")
                        break

            # 3-3. 공격 모션 시간 종료 시 상태 자원 정산 및 데이터 동기화
            if vars_obj.attack_timer <= 0:
                vars_obj.attack_timer = 0
                vars_obj.is_attacking = False
                vars_obj.attack_rect = None
                vars_obj.attack_obb = None

                # 트랙별 재사용 대기시간 독립 주입
                if vars_obj.attack_mode == "NORMAL":
                    if vars_obj.combo_step in [1, 2]:
                        vars_obj.attack_cooldown_timer = 0.15
                    elif vars_obj.combo_step == 3:
                        vars_obj.attack_cooldown_timer = 0.25

                    # 일반 공격 후속 연계 판정 정산 (적을 맞추지 못했거나 마지막 타수인 경우 콤보 리셋)
                    if vars_obj.combo_step == 3 or not vars_obj.has_hit_enemy:
                        vars_obj.combo_step = 0
                        vars_obj.combo_timer = 0
                else:
                    # DASH 모드는 고정 후딜레이 부여 후 연계 콤보 스텝 초기화 가드
                    vars_obj.attack_cooldown_timer = 0.2
                    vars_obj.combo_step = 0
                    vars_obj.combo_timer = 0
        else:
            vars_obj.attack_rect = None
            vars_obj.attack_obb = None
```

--------------------------------------------------

### 📄 extraction_target_project/player/input_handler.py
#### 🧱 Code Skeleton:
```python
class PlayerInputHandler:
    def __init__(self):
        self.mouse_left_was_pressed = False
        self.mouse_right_was_pressed = False

    def update(self, vars_obj, keys, dt=0.0):
        mouse_state = pygame.mouse.get_pressed()

        # ⚔️ 1-A. 좌클릭: 제자리 일반 공격 콤보 트랙 (NORMAL)
        if mouse_state[0]:
            if not self.mouse_left_was_pressed:
                cooldown = getattr(vars_obj, 'attack_cooldown_timer', 0.0)
                if cooldown <= 0.0:
                    self.trigger_attack(vars_obj, attack_mode="NORMAL")
            self.mouse_left_was_pressed = True
        else:
            self.mouse_left_was_pressed = False

        # ⚔️ 1-B. 우클릭: 독립된 단발성 돌진 공격 트랙 (DASH)
        if mouse_state[2]:
            if not self.mouse_right_was_pressed:
                cooldown = getattr(vars_obj, 'attack_cooldown_timer', 0.0)
                if cooldown <= 0.0:
                    self.trigger_attack(vars_obj, attack_mode="DASH")
            self.mouse_right_was_pressed = True
        else:
            self.mouse_right_was_pressed = False

        # 🏃 2. 키보드 이동 입력 상태 플래그 초기화
        vars_obj.is_moving = False

        # [무결성 수정] 시프트 키 분기
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            vars_obj.move_state = "RUN"
        else:
            vars_obj.move_state = "WALK"

        # 🎯 [무결성 수정] A/D 동시 입력 방지 (if-elif 구조 적용)
        # 이펙트 출력 및 공격 도중에도 사용자의 즉각적인 이동 전환 역동성을 보장하기 위해
        # 이동 입력 플래그(is_moving)와 시선 방향(facing_right) 전환 가드를 전면 개방합니다.
        if keys[pygame.K_a]:
            vars_obj.is_moving = True
            vars_obj.facing_right = False

        elif keys[pygame.K_d]:
            vars_obj.is_moving = True
            vars_obj.facing_right = True

        # 🚀 3. 점프 입력 제어 (공격 중 대각선 돌진 중일 때 점프가 입력되어 궤적이 깨지는 것을 안전 방지)
        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and not vars_obj.is_jumping:
            # 돌진 공격 중에 강제 점프로 속도 벡터가 상충되지 않도록 가드
            if not vars_obj.is_attacking:
                vars_obj.vertical_velocity = -vars_obj.jump_power
                vars_obj.is_jumping = True

    def trigger_attack(self, vars_obj, attack_mode):
        # 공격 중인 애니메이션 세션이 도는 동안에는 중복 입력 방지
        if vars_obj.is_attacking:
            return

        vars_obj.is_attacking = True
        vars_obj.attack_mode = attack_mode

        if attack_mode == "NORMAL":
            # ⚔️ [OnHit 전용 콤보 전환] - 일반 공격 트랙 전용으로 완전 격리
            if getattr(vars_obj, 'combo_timer', 0) <= 0 or getattr(vars_obj, 'combo_step', 0) == 0:
                vars_obj.combo_step = 1
            else:
                if vars_obj.combo_step == 1:
                    vars_obj.combo_step = 2
                elif vars_obj.combo_step == 2:
                    vars_obj.combo_step = 3
                else:
                    vars_obj.combo_step = 1
            vars_obj.combo_timer = vars_obj.combo_expire_time
        else:
            # DASH 모드는 콤보 단계와 연동하지 않으며 단발성으로 작동
            vars_obj.combo_step = 0
```

--------------------------------------------------

### 📄 extraction_target_project/player/motions/__init__.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

### 📄 extraction_target_project/player/motions/air_motions.py
#### 🧱 Code Skeleton:
```python
class AirMotions(MotionBase):
    def handle_state(self, vars_obj):
        # 공중에 떠 있을 때만 판정
        if vars_obj.is_jumping:
            if vars_obj.vertical_velocity < 0:
                return "JUMP_UP"
            else:
                return "FALL"
        return None
```

--------------------------------------------------

### 📄 extraction_target_project/player/motions/attack_motions.py
#### 🧱 Code Skeleton:
```python
class AttackMotions(MotionBase):
    def handle_state(self, vars_obj):
        # 플레이어가 공격 중일 때만 작동
        if vars_obj.is_attacking:
            if vars_obj.combo_step == 1:
                return "ATTACK_1"
            elif vars_obj.combo_step == 2:
                return "ATTACK_2"
            elif vars_obj.combo_step == 3:
                return "ATTACK_3"
        return None
```

--------------------------------------------------

### 📄 extraction_target_project/player/motions/ground_motions.py
#### 🧱 Code Skeleton:
```python
class GroundMotions(MotionBase):
    def handle_state(self, vars_obj):
        # 공중에 떠 있다면 지상 모션 판정을 하지 않음
        if vars_obj.is_jumping:
            return None
            
        if vars_obj.is_moving:
            return vars_obj.move_state  # "WALK" 또는 "RUN" 반환
        else:
            return "IDLE"
```

--------------------------------------------------

### 📄 extraction_target_project/player/motions/motion_base.py
#### 🧱 Code Skeleton:
```python
class MotionBase:
    def __init__(self):
        pass
    
    def handle_state(self, vars_obj):
        """각 모션 클래스에서 플레이어 변수를 보고 상태를 판정할 메서드 (오버라이딩용)"""
        pass
```

--------------------------------------------------

### 📄 extraction_target_project/player/physics_processor.py
#### 🧱 Code Skeleton:
```python
class PlayerPhysicsProcessor:
    def __init__(self):
        pass

    def process(self, vars_obj, platforms, game_map=None, dt=1.0/60.0):
        # 1. Y축 좌표를 업데이트하기 전에 '이전 발끝 위치'를 먼저 기록
        old_bottom = vars_obj.y + vars_obj.height

        # 가변 프레임 환경(dt)에 맞춘 가속 스케일러 연산
        fps_scale = dt * 60.0

        # 중력 적용 및 Y축 좌표 실제 이동
        vars_obj.vertical_velocity += vars_obj.gravity * fps_scale
        vars_obj.y += vars_obj.vertical_velocity * fps_scale

        player_rect = pygame.Rect(vars_obj.x, vars_obj.y, vars_obj.width, vars_obj.height)
        on_sub_platform = False

        # 플랫폼 충돌 정밀 검사
        for platform in platforms:
            # [GHOST 분기] 통과형 플랫폼은 연산에서 제외
            if not platform.vars.is_solid:
                continue
                
            plat_rect = pygame.Rect(platform.vars.x, platform.vars.y, platform.vars.width, platform.vars.height)
            
            if player_rect.colliderect(plat_rect):
                # ─── A. 하강/낙하 중일 때 (착지 처리: SOLID & ONE_WAY 공통) ───
                if vars_obj.vertical_velocity > 0:
                    # [하드코딩 제거] 매직 넘버 12 대신 낙하 속도와 프레임 보정치를 연동한 동적 착지 임계값 산출
                    dynamic_threshold = max(12.0, vars_obj.vertical_velocity * fps_scale + 2.0)
                    
                    if old_bottom <= platform.vars.y + dynamic_threshold:
                        vars_obj.y = platform.vars.y - vars_obj.height
                        vars_obj.vertical_velocity = 0
                        vars_obj.is_jumping = False
                        on_sub_platform = True
                        
                        # 💡 [차후 기능 확장 가드] 플랫폼 객체에 특수 밟기 기믹(무너짐 등) 기능이 있다면 동적 호출
                        if hasattr(platform, "on_stepped"):
                            platform.on_stepped(vars_obj, dt)
                        break
                
                # ─── B. 점프 상승 중일 때 (천장 충돌 처리: ONLY SOLID) ───
                elif vars_obj.vertical_velocity < 0:
                    # 아래에서 위로 통과할 수 없는 플랫폼 유형인 경우에만 정수리를 막음
                    if not platform.vars.passable_from_bottom:
                        # 이전 프레임의 머리 꼭대기 위치를 가변 dt 스케일에 맞춰 정확하게 역산
                        old_top = vars_obj.y - (vars_obj.vertical_velocity * fps_scale)
                        if old_top >= platform.vars.y + platform.vars.height:
                            vars_obj.y = platform.vars.y + platform.vars.height
                            vars_obj.vertical_velocity = 0 
                            
                            # 💡 [차후 기능 확장 가드] 천장 충돌 시 플랫폼 특수 기믹(스위치 작동 등) 확장 인터페이스
                            if hasattr(platform, "on_head_bump"):
                                platform.on_head_bump(vars_obj, dt)

        # 맵 시스템의 메인 바닥 착지 처리
        if not on_sub_platform:
            g_y = game_map.ground_y if (game_map and hasattr(game_map, 'ground_y')) else GROUND_Y
            if vars_obj.y + vars_obj.height >= g_y:
                vars_obj.y = g_y - vars_obj.height
                vars_obj.vertical_velocity = 0
                vars_obj.is_jumping = False

        # 좌측 화면 경계 밖 이탈 제어
        if vars_obj.x < 0:
            vars_obj.x = 0

        # 우측 화면/월드 경계 밖 이탈 제어 (유동적 가변 맵 대응 너비 반영)
        max_width = game_map.width if game_map else SCREEN_WIDTH
        if vars_obj.x > max_width - vars_obj.width:
            vars_obj.x = max_width - vars_obj.width
```

--------------------------------------------------

### 📄 extraction_target_project/player/player_main.py
#### 🧱 Code Skeleton:
```python
class Player:
    def __init__(self, x, y):
        # 데이터 및 입력 핸들러 초기화
        self.vars = PlayerVariables(x, y)
        self.vars_obj = self.vars  # 하위 호환성 및 외부 접근 편의를 위해 vars_obj 연결
        self.input_handler = PlayerInputHandler()
        
        # 🌟 분리된 컴포넌트 조립 (경로 수정이 완료된 에셋 로더 가동)
        self.assets = PlayerAssetLoader(self.vars)
        self.physics_engine = PlayerPhysicsProcessor()
        self.combat_engine = PlayerCombatProcessor()
        
        # 애니메이션 모션 판독기들 조립
        self.ground_motion_processor = GroundMotions()
        self.air_motion_processor = AirMotions()
        self.attack_motion_processor = AttackMotions()

    def update_animation_state(self):
        """현재 플레이어 변수를 분석해 상태 문자열(애니메이션 키)을 결정합니다."""
        state = None
        if self.vars.is_attacking:
            state = self.attack_motion_processor.handle_state(self.vars)
        elif self.vars.is_jumping or self.vars.vertical_velocity != 0:
            state = self.air_motion_processor.handle_state(self.vars)
        else:
            state = self.ground_motion_processor.handle_state(self.vars)
            
        if state is not None:
            self.vars.current_state = state

    def update(self, platforms, entities=None, game_map=None, dt=1.0/60.0):
        """플레이어의 모든 입력, 이동, 충돌, 애니메이션 프레임을 실시간 업데이트합니다."""

        # 가변 프레임 환경에 대응하기 위한 프레임 스케일러 보정값 계산
        fps_scale = dt * 60.0

        # ⏱️ [누락 해결] 콤보 유효 타이머 감소 연산 (시간 경과 시 콤보 리셋 보장)
        if getattr(self.vars, 'combo_timer', 0) > 0:
            self.vars.combo_timer -= fps_scale
            if self.vars.combo_timer < 0:
                self.vars.combo_timer = 0

        # 💀 사망 상태(is_dead == True) 예외 처리 및 기초 동작 제한
        if self.vars.is_dead:
            self.vars.is_moving = False
            self.vars.is_attacking = False
            self.vars.attack_rect = None
            self.vars.attack_obb = None

            # 최소한의 물리 엔진(중력, 충돌 판정)만 처리하여 바닥에 떨어질 수 있게 함 (dt 반영)
            self.physics_engine.process(self.vars, platforms, game_map=game_map, dt=dt)

            # 사망 애니메이션 상태 적용 (DEAD 에셋이 없는 경우 기본 IDLE 대기 상태 유지)
            if "DEAD" in self.assets.images:
                self.vars.current_state = "DEAD"
            else:
                self.vars.current_state = "IDLE"

            # 애니메이션 프레임 업데이트 (fps_scale 반영)
            anim_list = self.assets.images.get(self.vars.current_state, [])
            if anim_list:
                self.vars.anim_timer += fps_scale
                delay = getattr(self.vars, 'state_delays', {}).get(self.vars.current_state, self.vars.anim_speed)
                if self.vars.anim_timer >= delay:
                    self.vars.anim_timer = 0
                    self.vars.current_frame_idx = (self.vars.current_frame_idx + 1) % len(anim_list)
            return

        # 1. ⌨️ 사용자 키보드 입력 분석 (인자 전달 구조 유지)
        keys = pygame.key.get_pressed()
        self.input_handler.update(self.vars, keys)

  # 🪐 [관성 물리 메커니즘 통합]
        if self.vars.is_attacking:
            if getattr(self.vars, 'attack_mode', 'NORMAL') == 'NORMAL':
                if self.vars.is_moving:
                    # 현재 move_state("RUN" 또는 "WALK")에 맞는 속도를 가져옵니다.
                    target_speed = self.vars.run_speed if self.vars.move_state == "RUN" else self.vars.walk_speed
                    direction = 1 if self.vars.facing_right else -1
                    
                    # 💡 감속 비율을 0.4에서 0.7~0.8 정도로 올려주거나, 
                    # 아예 1.0으로 만들면 공격 중에도 대시 속도가 시원하게 유지됩니다!
                    vars_target_modifier = 0.75  # 75% 속도 유지 (원하는 대로 조절 가능)
                    target_vx = target_speed * direction * vars_target_modifier
                    
                    self.vars.vx += (target_vx - self.vars.vx) * min(1.0, 0.25 * fps_scale)
                else:
                    self.vars.vx *= max(0.0, 1.0 - (0.35 * fps_scale))
            else:
                # DASH 모드는 전투 프로세서 내부의 고유 가속도 프로파일 유지를 위해 관성 보존 패스 처리합니다.
                pass
        else:
            if self.vars.is_moving:
                # 가속
                target_speed = self.vars.run_speed if self.vars.move_state == "RUN" else self.vars.walk_speed
                direction = 1 if self.vars.facing_right else -1
                target_vx = target_speed * direction
                # 가속률 적용하여 target_vx에 도달
                self.vars.vx += (target_vx - self.vars.vx) * min(1.0, 0.25 * fps_scale)
            else:
                # 감속
                self.vars.vx *= max(0.0, 1.0 - (0.35 * fps_scale))

            # 공격 중이 아닐 때는 vy도 자연스럽게 감속
            self.vars.vy *= max(0.0, 1.0 - (0.35 * fps_scale))

        # 최종 물리 좌표(x, y) 업데이트
        self.vars.x += self.vars.vx * fps_scale
        self.vars.y += self.vars.vy * fps_scale

        # 2. 🪐 [오류 수정] 분리된 엔진 컴포넌트 가동 (물리 및 전투 엔진 인터페이스 및 dt 결합 완벽 갱신)
        self.physics_engine.process(self.vars, platforms, game_map=game_map, dt=dt)
        self.combat_engine.process(self.vars, entities=entities, dt=dt)

        # 3. 🎬 상태 기반 애니메이션 프레임 제어
        self.update_animation_state()

        anim_list = self.assets.images.get(self.vars.current_state, [])
        if anim_list:
            # [가변 보정] 델타 프레임 가중치를 더해 어떤 프레임에서도 일정한 속도로 애니메이션 재생
            self.vars.anim_timer += fps_scale
            # 각 상태(State)별로 지정된 프레임 딜레이 적용 (없으면 기본 anim_speed인 8 적용)
            delay = getattr(self.vars, 'state_delays', {}).get(self.vars.current_state, self.vars.anim_speed)
            if self.vars.anim_timer >= delay:
                self.vars.anim_timer = 0
                self.vars.current_frame_idx = (self.vars.current_frame_idx + 1) % len(anim_list)

    def update_with_dt(self, platforms, game_map, dt, entities=None):
        """main.py의 호출 인터페이스를 지원하기 위한 update 래퍼 메서드"""
        self.update(platforms, entities=entities, game_map=game_map, dt=dt)

    def draw(self, screen, camera_offset=(0, 0)):
        """플레이어 본체 이미지와 공격 시 콤보 이펙트 및 임시 돌진 범위 시각화를 화면에 렌더링합니다."""
# 파일 상단의 로컬 DEBUG 기본값과 전역 settings 스위치를 상호 결합하여 동기화
        global DEBUG
        current_debug_state = DEBUG or getattr(settings, 'DEBUG_SHOW_HITBOX', False)
        ox, oy = camera_offset
        # 🎬 1. 캐릭터 본체 스프라이트 시퀀스 추출 및 출력
        anim_list = self.assets.images.get(self.vars.current_state, [])
        if not anim_list:
            return
            
        # 혹시 모를 인덱스 바운드 에러를 막기 위한 최종 안전 필터링
        idx = min(self.vars.current_frame_idx, len(anim_list) - 1)
        player_image = anim_list[idx]
        
        # 왼쪽을 바라보고 있다면 이미지 좌우 반전
        if not self.vars.facing_right:
            player_image = pygame.transform.flip(player_image, True, False)
            
        screen.blit(player_image, (self.vars.x - ox, self.vars.y - oy))
        
        # 2. ⚔️ 공격 애니메이션 중일 때 콤보 검기 이펙트 출력 (원본 로직 완벽 보존)
        if self.vars.is_attacking and self.vars.combo_step in self.assets.effect_images:
            effect_img = self.assets.effect_images[self.vars.combo_step]
            
            # 플레이어가 바라보는 방향에 맞춰 이펙트도 반전 및 위치 정렬
            if not self.vars.facing_right:
                effect_img = pygame.transform.flip(effect_img, True, False)
                screen.blit(effect_img, (self.vars.x - ox - 60, self.vars.y - oy))
            else:
                screen.blit(effect_img, (self.vars.x - ox + 30, self.vars.y - oy))

        # 3. 🔴 [임시 이펙트] 돌진 공격(DASH) 범위 실시간 빨간색 렌더링
        if self.vars.is_attacking and getattr(self.vars, 'attack_mode', 'NORMAL') == 'DASH':
            attack_obb = getattr(self.vars, 'attack_obb', None)
            if attack_obb is not None:
                obb_cx, obb_cy, half_len, half_wid, dir_x, dir_y = attack_obb
                
                # 수직 방향 벡터 계산
                perp_x = -dir_y
                perp_y = dir_x

                # 카메라도 함께 움직이므로 오프셋(ox, oy)을 빼서 실제 화면 좌표를 도출합니다.
                corners = [
                    (obb_cx + dir_x * half_len + perp_x * half_wid - ox, obb_cy + dir_y * half_len + perp_y * half_wid - oy),
                    (obb_cx - dir_x * half_len + perp_x * half_wid - ox, obb_cy - dir_y * half_len + perp_y * half_wid - oy),
                    (obb_cx - dir_x * half_len - perp_x * half_wid - ox, obb_cy - dir_y * half_len - perp_y * half_wid - oy),
                    (obb_cx + dir_x * half_len - perp_x * half_wid - ox, obb_cy + dir_y * half_len - perp_y * half_wid - oy)
                ]

                # 알파 채우기를 위한 독립 서피스 생성 및 알파 채널 블릿 연산
                overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                pygame.draw.polygon(overlay, (255, 0, 0, 75), corners)  # 내부 반투명 레드 가이드라인
                screen.blit(overlay, (0, 0))

                # 경계선 실선 그리기
                pygame.draw.polygon(screen, (255, 0, 0), corners, 2)  # 외곽 붉은색 경계선

                if DEBUG:
                    print(f"[player_main.py] draw() -> Rendered DASH OBB Area: center=({obb_cx}, {obb_cy}), len={half_len}, wid={half_wid}")

        # 4. 🟢 [디버그 오버레이] 플레이어 피격 판정 상자(AABB) 실시간 녹색 렌더링
        if DEBUG:
            # 플레이어의 width와 height 속성이 설정되어 있는지 안전 필터링 거침
            p_width = getattr(self.vars, 'width', 0)
            p_height = getattr(self.vars, 'height', 0)
            if p_width > 0 and p_height > 0:
                aabb_rect = pygame.Rect(self.vars.x - ox, self.vars.y - oy, p_width, p_height)
                pygame.draw.rect(screen, (0, 255, 0), aabb_rect, 2)
                
                # 런타임 성능 저하 방지를 위해 디버그 스위치 기반 정밀 로깅 수행
                print(f"[player_main.py] draw() -> Rendered Player AABB: rect=({aabb_rect.x}, {aabb_rect.y}, {aabb_rect.width}, {aabb_rect.height})")
```

--------------------------------------------------

### 📄 extraction_target_project/player/variables.py
#### 🧱 Code Skeleton:
```python
class PlayerVariables:
    def __init__(self, x, y):
        # 🧍 기본 물리 변수
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.walk_speed = 4
        self.run_speed = 8
        self.jump_power = 16
        self.gravity = 0.8
        self.vertical_velocity = 0
        self.is_jumping = False
        self.current_state = "IDLE"
        self.facing_right = True
        self.is_moving = False
        self.move_state = "WALK"

        # 🧍 물리 가속도 변수 보충 (가변 프레임 및 관성 마찰 연산의 축)
        self.vx = 0.0
        self.vy = 0.0

        # ⚔️ 공격 및 콤보 관련 변수
        self.is_attacking = False       # 현재 공격 애니메이션/모션이 재생 중인가?
        self.combo_step = 0             # 0: 공격안함, 1: 1타, 2: 2타, 3: 3타
        self.attack_timer = 0           # 공격 모션이 유지되는 프레임 수
        self.attack_duration = 15       # 공격 모션 1회당 유지 시간
        self.has_hit_enemy = False      # 이번 공격 타수에서 적을 맞췄는가?

        # ⚔️ 전투 확장성 확보 (v1.3 연동용 기본 공격력)
        self.attack_damage = 15

        # ⏱️ 콤보 유효 타이머 (1.5초 = 90프레임)
        self.combo_expire_time = 90
        self.combo_timer = 0

        # 📐 공격 범위(히트박스) 크기 설정
        self.attack_range_width = 80
        self.attack_range_height = 50
        self.attack_rect = None

        # player/variables.py 내부 __init__ 하단에 추가할 변수 프로토콜
        self.attack_cooldown_timer = 0.0  # 공격 입력 및 콤보 조작 제한 타이머 (초 단위)
        self.target_enemy = None          # 현재 콤보 사이클 내에서 정밀 조준 중인 적 객체 참조

        # 📐 [OBB 돌진 판정용 신규 변수]
        self.attack_start_x = x           # 현재 타수의 돌진이 시작된 X좌표 (OBB 축의 A점)
        self.attack_start_y = y           # 현재 타수의 돌진이 시작된 Y좌표 (OBB 축의 A점)
        self.attack_obb = None            # (중심x, 중심y, 장축절반, 단축절반, 방향x, 방향y) 튜플
        self.is_targeting = False         # True: 좌클릭발 자동 타겟팅, False: 우클릭발 비타겟팅 고정

        # 🎬 [애니메이션 핵심 제어 변수]
        self.anim_timer = 0             # 프레임 카운터
        self.anim_speed = 8             # 숫자가 낮을수록 애니메이션이 빨라짐 (8프레임마다 다음 장)
        self.current_frame_idx = 0      # 리스트에서 현재 몇 번째 이미지를 그릴지 인덱스

        # 🎬 콤보 애니메이션 제어 확장 (콤보 타수별 프레임 재생 딜레이 개별 설정)
        self.state_delays = {
            "IDLE": 8,
            "WALK": 6,
            "RUN": 4,
            "ATTACK": 5,
            "ATTACK_1": 5,
            "ATTACK_2": 5,
            "ATTACK_3": 5
        }

        # 🚀 점프 선딜레이 타이머 (W 누른 순간 5프레임 동안만 READY_JUMP 유지)
        self.ready_jump_timer = 0

        # ❤️ HP 및 생존 관련 변수
        self.max_hp = 100
        self.hp = 100
        self.is_dead = False

    def take_damage(self, amount):
        """데미지를 입어 hp를 감소시키고, 0 이하가 되면 사망 처리합니다."""
        if self.is_dead or amount <= 0:
            return
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.is_dead = True

    def heal(self, amount):
        """체력을 회복시키되, 최대 체력을초과하지 않도록 합니다."""
        if self.is_dead or amount <= 0:
            return
        self.hp = min(self.max_hp, self.hp + amount)
```

--------------------------------------------------

### 📄 extraction_target_project/settings.py
*선언된 클래스나 함수가 없는 파일이거나 모듈입니다.*

--------------------------------------------------

