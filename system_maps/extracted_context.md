# ==========================================================================
# 🎯 AI GLOBAL GUIDELINES: 코드 무결성 및 디버깅 중심 가이드
# [SCAN_MODE] EXTRACTION_TARGET_PROJECT
# ==========================================================================
# 📄 [요청 1] TARGET: extraction_target_project/map_editor_tool/selection.py (1-121라인)
# ----------------------------------------------------------
```python
import pygame

from map_system.map_engine import EntityRegistry


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

# 📄 [요청 2] TARGET: extraction_target_project/map_editor_tool/serializer.py (1-172라인)
# ----------------------------------------------------------
```python
import json
import os

import pygame


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


# map_editor_tool/serializer.py:78-90 범위 수정

# map_editor_tool/serializer.py 수정 (L88-103 부근)
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


# [📂 map_editor_tool/serializer.py]의 _infer_entity_type 함수 수정본

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
