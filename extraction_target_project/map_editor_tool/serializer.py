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
