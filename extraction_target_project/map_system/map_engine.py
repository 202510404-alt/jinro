# src/map_system/map_engine.py
import pygame
import os
import sys
import math
import json
import settings
import importlib
import re

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

