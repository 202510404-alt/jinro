import os
import sys
import json
import math
import pygame

# 프로젝트 내부 모듈 참조
from map_system.map_engine import EntityRegistry, TriggerBoxInstance
from map_system.variables import MapVariables
from platform_system.platform_main import Platform

# 🎯 [구조 보존 및 확장] 게임 실행 시점에 DummyEnemy 클래스가 EntityRegistry에 무조건 등록되도록 보장합니다.
try:
    from enemy.enemys.dummy.dummy_main import DummyEnemy
    EntityRegistry.register("dummy", DummyEnemy)
    EntityRegistry.register("DummyEnemy", DummyEnemy)
except ImportError as e:
    print(f"⚠️ [GameMap] DummyEnemy 모듈을 로드할 수 없습니다. 경로를 확인하십시오: {e}")


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
        for entity in self.entities:
            # 1. 엔티티가 dt 기반 업데이트(update_with_dt)를 지원하는지 먼저 확인
            if hasattr(entity, "update_with_dt"):
                try:
                    # 맵 정보(self)와 dt를 같이 전달
                    entity.update_with_dt(player_obj, self.platforms, self, dt)
                except Exception as e:
                    print(f"⚠️ [GameMap] 엔티티 dt 업데이트 중 오류 발생: {e}")
            
            # 2. 지원하지 않고 일반 update만 있다면 기존 규칙대로 self(지형 정보)를 포함하여 호출
            elif hasattr(entity, "update"):
                try:
                    entity.update(player_obj, self.platforms, self)
                except Exception as e:
                    print(f"⚠️ [GameMap] 엔티티 일반 업데이트 중 오류 발생: {e}")
            
            # 2. 전용 메서드가 없고 일반 update만 있다면 이전 규칙대로 self(지형 정보)를 포함하여 호출
            elif hasattr(entity, "update"):
                try:
                    entity.update(player_obj, self.platforms, self)
                except Exception as e:
                    print(f"⚠️ [GameMap] 엔티티 일반 업데이트 중 오류 발생: {e}")
            
            # 2. 전용 메서드가 없고 일반 update만 있다면 이전 규칙대로 self(지형 정보)를 포함하여 호출
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