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
